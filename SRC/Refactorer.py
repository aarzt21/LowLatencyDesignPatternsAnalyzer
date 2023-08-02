from clang.cindex import Index, CursorKind, AccessSpecifier, TypeKind
from bs4 import BeautifulSoup
import openai
import re


access_specifier_map = {
    AccessSpecifier.INVALID: 'INVALID',
    AccessSpecifier.PUBLIC: 'public:',
    AccessSpecifier.PROTECTED: 'protected:',
    AccessSpecifier.PRIVATE: 'private:'
}


designPatterns = """
//Pattern 1: Cold Code isolation pattern ----------------------------------
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

 //Pattern 2: Template Based Branch eliminiation pattern ----------------------------------
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

//Pattern 3: The CRTP ----------------------------------
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

"""






class Refactor:
    def __init__(self):
        self.apiKey = None
        self.oAImodel = None

    def setApiKey(self, apiKey):
        self.apiKey = apiKey

    def setOaimodel(self, model):
        self.oAImodel = model

    def generateCppFile(self, cpp_file, h_file, output_file):
        index = Index.create()

        # Parse the two files
        tu_cpp = index.parse(cpp_file, args=['-x', 'c++'])
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


    def extractCode(self,text):
        # If there are no triple backticks in the text, return the whole text
        if '```' not in text:
            return text.strip()

        # Pattern to match code blocks (``` some code ```)
        pattern = r'```.*?\n(.*?)```'

        # Use re.DOTALL to match across line breaks
        matches = re.findall(pattern, text, re.DOTALL)

        # Concatenate all the matched code blocks
        code = '\n'.join(matches)
        return code


    def send_prompt_to_cgpt(self, cppFile):
        
        openai.api_key = self.apiKey
        
        cppCode = ""
        with open(cppFile, "r") as f:
            for line in f.readlines():
                cppCode += line

        response = openai.ChatCompletion.create(
        model= self.oAImodel,
        messages=[
                {"role": "system", "content": "You are a code refactoring assistant that refactors C++ code by implementing certain design patterns."},
                {"role": "user", "content": "I will first show you some EXAMPLES of the design patterns: " + designPatterns},
                {"role": "assistant", "content": "Okay I have learned and understood the patterns."}, 
                {"role": "user", "content": "Now before I give you some code to refactor I want you to understand this: \
                                            The patterns that should be implemented are written in comments in the code. The CRTP Pattern \
                                            means that you have to refactor the entire class. All other patterns are method specific. \
                                            There can be multiple patterns per class or method that must be implemented at once. Once you are done just give back the C++ code and do not write a main function."},
                {"role": "assistant", "content": "Okay I understood the requirements. I am ready for you to provide me with the code to refactor."},
                {"role": "user", "content": "Remember: Respond ONLY WITH THE CODE and do not write a main function or any explanations. Further, implement all patterns that are indicated by the comments. Here is the code to refactor: " + cppCode}                
            ]
        )

        return self.extractCode(response.choices[0].message['content'])
    



    def send_Custom_prompt_to_cgpt(self, orgFile, refFile, customPrompt):
    
        openai.api_key = self.apiKey
        
        orgCode = ""
        with open(orgFile, "r") as f:
            for line in f.readlines():
                orgCode += line

        refCode = ""
        with open(refFile, "r") as f:
            for line in f.readlines():
                refCode += line


        response = openai.ChatCompletion.create(
        model= self.oAImodel,
        messages=[
                {"role": "system", "content": "You are a code refactoring assistant that refactors C++ code by implementing certain design patterns."},
                {"role": "user", "content": "These are the design patterns I have shown you: " + designPatterns},
                {"role": "assistant", "content": "Okay I looked at them again."}, 
                {"role": "user", "content": "Then I gave you this code: " + orgCode + "and you have refactored it to this code: " + refCode},
                {"role": "assistant", "content": "Okay, do you want me to try again?."},
                {"role": "user", "content": "yes refactor this code: " + orgCode + " again (only give back the refactored code) but this time pay attention to this: " + customPrompt}
                 
            ]
        )

        return self.extractCode(response.choices[0].message['content'])