import clang.cindex
from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
import os

def analyze_tbbe(filename):
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

    index = clang.cindex.Index.create()
        
    translation_unit = index.parse(filename)  # Parse the file
    if translation_unit.diagnostics:
        for diag in translation_unit.diagnostics:
            print("Diagnostic:", diag)
        return

    tu_cursor = translation_unit.cursor
    lines_to_comment = []
    find_functions_with_args_in_if_statements(tu_cursor, filename, lines_to_comment)

    comments = {}
    for line in lines_to_comment:
        comments[line] = "Refactor this method by applying the TBBE Pattern."
    
    return comments
