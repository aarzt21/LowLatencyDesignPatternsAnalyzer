import clang.cindex

def analyze_crtp(filename):
    def findVirtualMethods(vertex, filename):
        result = []
        if vertex.location.file and vertex.location.file.name == filename:
            if vertex.kind == clang.cindex.CursorKind.CXX_METHOD and vertex.is_virtual_method():
                result.append((vertex.displayname, vertex.location.line))
        for child in vertex.get_children():
            result.extend(findVirtualMethods(child, filename))
        return result

    def findVirtualMethodCalls(vertex, filename):
        result = []
        if vertex.location.file and vertex.location.file.name == filename:
            if vertex.kind == clang.cindex.CursorKind.CALL_EXPR: #if node is func call proceed with further checks
                children = list(vertex.get_children())
                if children and children[0].kind == clang.cindex.CursorKind.MEMBER_REF_EXPR:
                    base_expr = next(children[0].get_children(), None)
                    #check for pointer access
                    if base_expr and base_expr.type.kind in {clang.cindex.TypeKind.POINTER, clang.cindex.TypeKind.LVALUEREFERENCE, clang.cindex.TypeKind.RVALUEREFERENCE}:
                        # check if the function being called is a virtual method
                        called_function = children[0].get_definition()
                        if called_function is not None and called_function.is_virtual_method():
                            result.append((children[0].displayname, children[0].location.line))
        for child in vertex.get_children():
            result.extend(findVirtualMethodCalls(child, filename))
        return result

    def createWarnings(warnings):
        comment_dict = {}
        for warning in warnings:
            name, line = warning
            comment_dict[line] = f"Refactor this class using the CRTP to get rid of virtual method."
        return comment_dict

    idx = clang.cindex.Index.create()

    TU = idx.parse(filename)

    tu_cursor = TU.cursor
    virtual_funcs = findVirtualMethods(tu_cursor, filename)
    virtual_func_calls = findVirtualMethodCalls(tu_cursor, filename)

    warnings = virtual_funcs + virtual_func_calls

    return createWarnings(warnings)
