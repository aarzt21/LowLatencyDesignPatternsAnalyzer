import clang.cindex

def analyze_crtp(source_code, filename):
    def find_virtual_functions(node, filename):
        result = []
        if node.location.file and node.location.file.name == filename:
            if node.kind == clang.cindex.CursorKind.CXX_METHOD and node.is_virtual_method():
                result.append((node.displayname, node.location.line))
        for child in node.get_children():
            result.extend(find_virtual_functions(child, filename))
        return result

    def find_virtual_function_calls(node, filename):
        result = []
        if node.location.file and node.location.file.name == filename:
            if node.kind == clang.cindex.CursorKind.CALL_EXPR: #if node is func call proceed with further checks
                children = list(node.get_children())
                if children and children[0].kind == clang.cindex.CursorKind.MEMBER_REF_EXPR:
                    base_expr = next(children[0].get_children(), None)
                    #check for pointer access
                    if base_expr and base_expr.type.kind in {clang.cindex.TypeKind.POINTER, clang.cindex.TypeKind.LVALUEREFERENCE, clang.cindex.TypeKind.RVALUEREFERENCE}:
                        # check if the function being called is a virtual method
                        called_function = children[0].get_definition()
                        if called_function is not None and called_function.is_virtual_method():
                            result.append((children[0].displayname, children[0].location.line))
        for child in node.get_children():
            result.extend(find_virtual_function_calls(child, filename))
        return result

    def create_warnings(warnings):
        comment_dict = {}
        for warning in warnings:
            name, line = warning
            comment_dict[line] = f"WARNING: Virtual method '{name}'. Consider using the Curiously Recurring Template Pattern (CRTP) instead."
        return comment_dict

    index = clang.cindex.Index.create()

    translation_unit = index.parse(filename, unsaved_files=[(filename, source_code)])

    tu_cursor = translation_unit.cursor
    virtual_funcs = find_virtual_functions(tu_cursor, filename)
    virtual_func_calls = find_virtual_function_calls(tu_cursor, filename)

    warnings = virtual_funcs + virtual_func_calls

    return create_warnings(warnings)
