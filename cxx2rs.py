#!/usr/bin/env python
""" Usage: call with <filename> <typename>
"""

import sys
import re
import os.path
import clang.cindex
clang.cindex.Config.set_library_file('/usr/lib/x86_64-linux-gnu/libclang-3.5.so.1')


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


def stringify_variable_declaration(node):
    if node.type.get_canonical() != node.type:
        return "\t%s %s [%s]" % (
            node.type.spelling,
            node.spelling,
            node.type.get_canonical().spelling)
    else:
        return "\t%s %s" % (
            node.type.spelling,
            node.spelling)


def stringify_function_declaration(node):
    res = ""
    if node.result_type.get_canonical() != node.result_type:
        res += "%s %s() [%s]\n" % (
            node.result_type.spelling,
            canonical_function_name(node),
            node.result_type.get_canonical().spelling)
    else:
        res += "%s %s()\n" % (
            node.result_type.spelling,
            canonical_function_name(node))

    for c in node.get_arguments():
        res += "%s\n" % stringify_variable_declaration(c)
    return res
    
def stringify_struct_declaration(node):
    node = node.type.get_declaration()
    res = "struct %s [%s]\n" % (node.spelling, node.type.spelling)
    for c in node.get_children():
        res += "\t%s\n" % stringify_variable_declaration(c)
    return res


def rustify_variable_declaration(node):
    keywords = ['priv', 'loop', 'ref', 'in', 'type']

    name = node.spelling
    while name in keywords:
        name += "_"

    return "%s: %s" % (
            name,
            rustify_type(node.type))
#            rustify_type(node.type.get_canonical()))


def rustify_function_pointer(node):
    clang_types = clang.cindex.TypeKind

    canonical = node.get_canonical()
    canonical_pointee = canonical.get_pointee().get_canonical()

    assert canonical_pointee.kind is clang_types.FUNCTIONPROTO

    args = ", ".join(map(rustify_type, canonical_pointee.argument_types()))
    res = 'extern fn(%s)' % args

    if node.get_result().get_canonical().kind not in [clang_types.VOID, clang_types.INVALID]:
        res += " -> %s" % rustify_type(node.get_result().get_canonical())
    return res


def rustify_pointer(node):
    clang_types = clang.cindex.TypeKind

    canonical = node.get_canonical()
    canonical_pointee = canonical.get_pointee().get_canonical()

    if canonical_pointee.kind == clang_types.FUNCTIONPROTO:
        return rustify_function_pointer(node)
    else:
        if canonical.is_const_qualified():
           return '*mut ' + rustify_type(canonical_pointee)
        else:
           return '*const ' + rustify_type(canonical_pointee)


def rustify_function_prototype(node):
    canonical = node.get_canonical()

    args = ",".join(map(rustify_type, canonical.argument_types()))
    ret = rustify_type(node.get_result().get_canonical())

    return "extern fn (%s) -> %s" % (args, ret)
#    return "libc::c_int/*FUNCTIONPROTO %s(%s)*/" % (ret,  args)
#        return "libc::c_int/*FUNCTIONPROTO %s*/" % rustify_function_declaration(node)


def rustify_type(node):
    clang_types = clang.cindex.TypeKind
    mapping = {
        clang_types.INT: 'libc::c_int',
        clang_types.CHAR_S: 'libc::c_char',
        clang_types.CHAR_U: 'libc::c_uchar',
        clang_types.VOID: 'libc::c_void',
        clang_types.LONG: 'libc::c_long',
        clang_types.ENUM: 'libc::c_uint',
    }

    canonical = node.get_canonical()
    canonical_kind = canonical.kind
    if canonical_kind == clang_types.POINTER:
        return rustify_pointer(node)
    elif canonical_kind is clang_types.RECORD:
        return re.sub('^struct ', '', re.sub('^const ', '', canonical.spelling))
    elif canonical_kind == clang_types.FUNCTIONPROTO:
        return rustify_function_prototype(node)
    elif canonical_kind == clang_types.INCOMPLETEARRAY:
         return 'libc::c_int /* INCOMPLETEARRAY /*'
    elif canonical_kind in mapping:
        return mapping[canonical_kind]
    else:
        #raise Exception("Not implemented: Type=%s" % canonical_kind)
        return "%s" %   node.get_canonical().kind


def rustify_function_declaration(node):
    args = ", ".join(map(rustify_variable_declaration, node.get_arguments()))

    res = "fn %s(%s)" % (canonical_function_name(node), args)

    if node.result_type.get_canonical().kind is not clang.cindex.TypeKind.VOID:
        res += ' -> %s' % rustify_type(node.result_type.get_canonical())

    return '#[link(name="%s")]\nextern "C" {\n\t%s;\n\t}\n' % (link_name, res)


def rustify_struct_declaration(node):
    node = node.type.get_declaration()
    res =  "#[repr(C)]\n"
    res += "struct %s" % node.spelling

    members = " {\n"
    for c in node.get_children():
        members += "\t%s,\n" % rustify_variable_declaration(c)

    if len(members) > 3:
        members += "}\n"
        res += members
    else:
        res += ';\n'
    return res

link_name = None
def main():
    global link_name

    index = clang.cindex.Index.create()
    link_name = sys.argv[1]
    tu = index.parse(sys.argv[2])

    print """
    extern crate libc;
    """

    for func in get_functions(tu.cursor, tu.spelling):
        print "/*%s*/" % stringify_function_declaration(func)
        print rustify_function_declaration(func)
        print

    for struct in get_structs(tu.cursor, tu.spelling):
        print "/*%s*/" % stringify_struct_declaration(struct)
        print rustify_struct_declaration(struct)


main()
