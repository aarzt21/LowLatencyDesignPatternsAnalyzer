import clang.cindex
import sys


def find_if_statements_in_node(node, function_args):
    arg_in_if_statement = False
    if node.kind == clang.cindex.CursorKind.IF_STMT:
        for expr in node.walk_preorder():
            if expr.kind == clang.cindex.CursorKind.DECL_REF_EXPR and expr.spelling in function_args:
                arg_in_if_statement = True
                break
    else:
        for child in node.get_children():
            if find_if_statements_in_node(child, function_args):
                arg_in_if_statement = True
                break
    return arg_in_if_statement



def find_functions_with_args_in_if_statements(node, filename, lines_to_comment):
    if (node.kind == clang.cindex.CursorKind.FUNCTION_DECL or 
        node.kind == clang.cindex.CursorKind.CXX_METHOD) and node.location.file and node.location.file.name == filename:
        
        function_name = node.spelling
        function_args = [arg.spelling for arg in node.get_arguments()]

        for child in node.get_children():
            if find_if_statements_in_node(child, function_args):
                lines_to_comment.append(node.location.line)
                break

    for child in node.get_children():
        find_functions_with_args_in_if_statements(child, filename, lines_to_comment)




def main():
    index = clang.cindex.Index.create()
    lines = sys.stdin.readlines()  # Read piped input
    with open("temp.cpp", 'w') as temp_file:  # Write piped input to a temporary file
        temp_file.writelines(lines)
        
    translation_unit = index.parse("temp.cpp")  # Parse the temporary file
    if translation_unit.diagnostics:
        for diag in translation_unit.diagnostics:
            print("Diagnostic:", diag)
        return

    tu_cursor = translation_unit.cursor
    lines_to_comment = []
    find_functions_with_args_in_if_statements(tu_cursor, "temp.cpp", lines_to_comment)

    # Now we insert the comments into the source code
    for line in sorted(lines_to_comment, reverse=True):
        lines.insert(line-1, "// This function uses an argument in one of its branches -> if the argument is known at compile time then consider the TBBE Pattern.\n")

    for line in lines:
        print(line, end='')


if __name__ == "__main__":
    main()
