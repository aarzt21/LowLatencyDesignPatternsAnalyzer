from clang.cindex import Index, CursorKind, AccessSpecifier, TypeKind
from bs4 import BeautifulSoup

access_specifier_map = {
    AccessSpecifier.INVALID: 'INVALID',
    AccessSpecifier.PUBLIC: 'public:',
    AccessSpecifier.PROTECTED: 'protected:',
    AccessSpecifier.PRIVATE: 'private:'
}

class Refactor:
    def __init__(self, apiKey):
        self.apiKey = apiKey

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
