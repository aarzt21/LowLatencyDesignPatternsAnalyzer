import clang.cindex
from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
import os

def analyze_tbbe(filename):
    def getIfStmntInVertex(knot, function_args):
        argInIfStmnt = False
        if knot.kind == clang.cindex.CursorKind.IF_STMT:
            for ausdrk in knot.walk_preorder():
                if ausdrk.kind == clang.cindex.CursorKind.DECL_REF_EXPR and ausdrk.spelling in function_args:
                    argInIfStmnt = True
                    break
        else:
            for descdnt in knot.get_children():
                if getIfStmntInVertex(descdnt, function_args):
                    argInIfStmnt = True
                    break
        return argInIfStmnt

    def findMethodsWithArgsInIfStatements(knot, filename, lines_to_comment):
        if (knot.kind == clang.cindex.CursorKind.FUNCTION_DECL or 
            knot.kind == clang.cindex.CursorKind.CXX_METHOD) and knot.location.file and knot.location.file.name == filename:
            
            funcName = knot.spelling
            funcArgs = [arg.spelling for arg in knot.get_arguments()]

            for kid in knot.get_children():
                if getIfStmntInVertex(kid, funcArgs):
                    lines_to_comment.append(knot.location.line)
                    break

        for kid in knot.get_children():
            findMethodsWithArgsInIfStatements(kid, filename, lines_to_comment)

    idx = clang.cindex.Index.create()
        
    TU = idx.parse(filename)  # Parse the file
    if TU.diagnostics:
        for diag in TU.diagnostics:
            print("Diagnostic:", diag)
        return

    tu_cursor = TU.cursor
    lines_to_comment = []
    findMethodsWithArgsInIfStatements(tu_cursor, filename, lines_to_comment)

    comments = {}
    for line in lines_to_comment:
        comments[line] = "Refactor this method by applying the TBBE Pattern."
    
    return comments
