from clang.cindex import Index, CursorKind, AccessSpecifier, TypeKind
from bs4 import BeautifulSoup
import openai

access_specifier_map = {
    AccessSpecifier.INVALID: 'INVALID',
    AccessSpecifier.PUBLIC: 'public:',
    AccessSpecifier.PROTECTED: 'protected:',
    AccessSpecifier.PRIVATE: 'private:'
}


designPatterns = """
                //Pattern 1

/* This is the cold code isolation pattern: Assume we have  a function that hot code and cold code  */

int foo(std::vector<int>& vec){
	int sum = 0; 
	for (int i = 0;  i < vec.size(); i++){
		int e =  vec[i];
		if (/*some rare condition*/ ) {
			/*execute some large code block*/
		}
		
		else sum += e; 
	}
	return sum; 
}


/*Now isolate the cold code by putting it into a separate function so that foo only contains hot code*/

void edgeCaseHandler(){/*large code block*/}

int foo(std::vector<int>& vec){
	int sum = 0; 
	for (int i = 0;  i < vec.size(); i++){
		int e =  vec[i];
		if (/*some rare condition*/ ) edgeCaseHandle();
		else sum += e; 
	}
	return sum; 
}


//Another Example: 

// hot code before ...
if (checkForErrorA()) // cold code starts
    //medium-sized code block
else if (checkForErrorB())
    //medium-sized code block
else if (checkForErrorC())
    //medium-sized code block
else
    sendOrderToExchange(); // hot code again
    
//make the code more i-cache friendly by refactoring it such that the cold code is removed

int errorFlags;
//...
if (!errorFlags)//hot code continous until here
    sendOrderToExchange(); 
else 
    HandleError(errorFlags);
    
    

    
    
 //Pattern 2: Template Based Branch eliminiation pattern
//non-templated version with Branches
float foo_slow(std::vector<int>& vec, bool include_negatives) {
    int len = vec.size();
    int average = 0;
    int count = 0;
    for (int i = 0; i < len; i++)
    {
        if (include_negatives) {
            average += vec[i];
        }
        else
        {
            int e = abs(vec[i]);
            average += e;
            count++;
        }

    }

    if (include_negatives)
        return average / len;
    else
        return average / count;
}


//now since the value of include_negatives is known at compile time, 
//we can eliminate the branches using templates, i.e. apply the Template Based Branch Elimination Pattern: 
//TB Version without branches
template <bool include_negatives>
float foo_fast(std::vector<int>& vec) {
    int len = vec.size();
    int average = 0;
    int count = 0;
    for (int i = 0; i < len; i++) {
        if (include_negatives)
        {
            average += vec[i];
        }
        else
        {
            int e = abs(vec[i]);
            average += e;
            count++;
        }
    }

    if (include_negatives)
        return average / len;

    else
        return average / count;
}
    
    
//Pattern 3: The CRTP 
//instead of using virtual functions:     
    //regular OOP-Variant
class Base {
protected:
    int counter;
public:
    Base(): counter(0) {};
    virtual void inc(){counter += 1;}
    int getCounter(){return counter;}
};

class Special: public Base {
public:
    void inc() override {counter += 2;}
};

//would result in dynamic function dispatch
Special* spec = new Special; 
spec->inc();


// we employ the CRTP
//CRTP ---------
template <typename Derived>
class CRTPTemplate {
protected:
    int counter;
public:
    CRTPTemplate() : counter(0) {}
    void inc(){static_cast<Derived*>(this)->inc();}
    int getCounter(){return counter;}
};

class SpecialCRTP: public CRTPTemplate<SpecialCRTP> {
public:
    void inc() { counter = counter + 2;}
};

//would result in static function dispatch
Special* specCRTP = new SpecialCRTP(); 
specCRTP->inc();

                 """






class Refactor:
    def __init__(self, apiKey):
        self.apiKey = "X"

    def generateCppFile(self, cpp_file, h_file, output_file):
        index = Index.create()

        # Parse the two files
        tu_cpp = index.parse(cpp_file)
        tu_h = index.parse(h_file, args=['-x', 'c++'])

        # Mapping from method names to their definitions
        definitions = {}
        for cursor in tu_cpp.cursor.walk_preorder():
            if cursor.location.file is None or cursor.location.file.name != cpp_file:
                continue
            if (cursor.kind == CursorKind.CXX_METHOD or cursor.kind == CursorKind.CONSTRUCTOR) and cursor.is_definition():
                class_name = cursor.semantic_parent.spelling
                method_name = cursor.spelling
                code = self._get_code(cursor).replace("\n", "\n\t")
                definitions[(class_name, method_name)] = code

        # Write the class declaration to the output file
        class_name = None
        base_class_name = None
        bracket_open = False

        with open(output_file, 'w') as f:
            # Copy include statements from the header file
            with open(h_file, 'r') as h_f:
                for line in h_f:
                    if line.startswith('#include'):
                        print(line.strip(), file=f)
            for cursor in tu_h.cursor.walk_preorder():
                if cursor.location.file is None or cursor.location.file.name != h_file:
                    continue
                if cursor.kind == CursorKind.CLASS_DECL:
                    if bracket_open:
                        print("\n};", file=f)
                    class_name = cursor.spelling
                    print(f"\nclass {class_name}", end='', file=f)
                    for c in cursor.get_children():
                        if c.kind == CursorKind.CXX_BASE_SPECIFIER:
                            base_class_name = c.type.spelling
                            access_specifier = access_specifier_map[c.access_specifier].replace(':', '')
                            print(f" : {access_specifier} {base_class_name}", end='', file=f)
                    print(" {", file=f)
                    bracket_open = True
                elif cursor.kind == CursorKind.CXX_ACCESS_SPEC_DECL:
                    print(access_specifier_map[cursor.access_specifier], file=f)
                elif cursor.kind == CursorKind.FIELD_DECL:
                    print("\t" + cursor.type.spelling + " " + cursor.spelling + ';', file=f)
                elif cursor.kind == CursorKind.CXX_METHOD or cursor.kind == CursorKind.CONSTRUCTOR:
                    space = "\t"
                    if cursor.is_virtual_method():
                        print("\t virtual", end = ' ', file=f)
                        space = ""
                    print(space + definitions[(class_name, cursor.spelling)].replace(class_name + "::", ""), file=f)
            
            if bracket_open:
                print("\n};", file=f)

    def _get_code(self, cursor):
        extent = cursor.extent
        with open(cursor.location.file.name, 'r') as f:
            lines = f.readlines()
            start = extent.start.line - 1 
            end = extent.end.line
            return ''.join(lines[start:end])

    def _convertHTMLtoCPP(self, htmlFile, outfilename):
        # Read the HTML file
        with open(htmlFile, 'r') as file:
            html_content = file.read()

        # Parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find <pre> or <code> tags in the HTML
        code_blocks = soup.find_all(['pre', 'code'])

        # Extract and concatenate the C++ code
        cpp_code = ""
        for code_block in code_blocks:
            cpp_code += code_block.get_text()

        with open(outfilename, "w") as f:
            f.write(cpp_code)

    def send_prompt_to_cgpt(self, cppFile):
        
        openai.api_key = self.apiKey
        
        cppCode = ""
        with open("DummyCode/final.cpp", "r") as f:
            for line in f.readlines():
                cppCode += line

        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a code refactoring assistant. Given some C++ code with certain comments, \
                    your task is refactor the code by implementing the design pattern suggestions written in the comments of the C++ code. \
                    Your response should only consist of the C++ code and nothing else."},
                {"role": "user", "content": cppCode},
            ]
        )

        return response.choices[0].message['content']