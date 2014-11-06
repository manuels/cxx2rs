import clang.cindex
clang.cindex.Config.set_library_file('/usr/lib/x86_64-linux-gnu/libclang-3.5.so.1')

import os.path

link_name = None

def get_nodes(node, filename, kind_list):
    try:
        is_kind = (node.kind in kind_list)
    except ValueError as e:
        # unknown cursor kind
        is_kind = False

    if not is_kind:
        for c in node.get_children():
            for node in get_nodes(c, filename, kind_list):
                yield node
    else:

        if node.location.file is not None:
            path = os.path.dirname(filename)
            fname = os.path.dirname(str(node.location.file))
            is_in_dir = (os.path.commonprefix([fname, path]) == path)

            if is_in_dir:
                yield node


def get_functions(node, filename):
    kind_list = [clang.cindex.CursorKind.FUNCTION_DECL, clang.cindex.CursorKind.CXX_METHOD]
    return get_nodes(node, filename, kind_list)


def get_structs(node, filename):
    kind_list = [clang.cindex.CursorKind.STRUCT_DECL]
    
    nodes = get_nodes(node, filename, kind_list)
    structs = map(lambda n: n.type.get_declaration(), nodes)

    res = []
    for s in structs:
        if s not in res:
            res.append(s)
    return res


def parent_path(node):
    parent = node.semantic_parent

    if parent.spelling is None:
        return []
    else:
        res = parent_path(parent) + [parent]
        return res

def canonical_function_name(node):
    res = ""
    for p in parent_path(node):
        if p.kind == clang.cindex.CursorKind.CLASS_DECL:
            res += "%s." % p.spelling
        elif p.kind == clang.cindex.CursorKind.NAMESPACE:
            res += "%s::" % p.spelling
        elif p.kind == clang.cindex.CursorKind.TRANSLATION_UNIT:
            pass
        else:
            assert(False)

    return res + node.spelling
