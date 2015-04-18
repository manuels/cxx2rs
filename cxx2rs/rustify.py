import clang.cindex
import re

from parser import *

def rustify_variable_declaration(node):
    keywords = ['priv', 'loop', 'ref', 'in', 'type', 'where', 'impl', 'self', 'as', 'pub']

    name = node.spelling
    while name in keywords:
        name += "_"
    if len(name) == 0:
        name = "_"

    return "%s: %s" % (
            name,
#            rustify_type(node.type))
            rustify_type(node.type.get_canonical()))


def rustify_function_pointer(node):
    clang_types = clang.cindex.TypeKind

    canonical = node.get_canonical()
    canonical_pointee = canonical.get_pointee().get_canonical()

    assert canonical_pointee.kind is clang_types.FUNCTIONPROTO

    args = ", ".join(map(rustify_type, canonical_pointee.argument_types()))
    res = 'extern fn(%s)' % args

    if canonical_pointee.get_result().get_canonical().kind not in [clang_types.VOID, clang_types.INVALID]:
        res += " -> %s" % rustify_type(canonical_pointee.get_result().get_canonical())
    return "Option<%s>" % res # nullable


def rustify_pointer(node):
    clang_types = clang.cindex.TypeKind

    canonical = node.get_canonical()
    canonical_pointee = canonical.get_pointee().get_canonical()

    if canonical_pointee.kind == clang_types.FUNCTIONPROTO:
        return rustify_function_pointer(node)
    else:
        if canonical_pointee.is_const_qualified():
           return '*const ' + rustify_type(canonical_pointee)
        else:
           return '*mut ' + rustify_type(canonical_pointee)


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
        clang_types.INT:       'libc::c_int',
        clang_types.UINT:      'libc::c_uint',
        clang_types.CHAR_S:    'libc::c_char',
        clang_types.CHAR_U:    'libc::c_uchar',
        clang_types.SHORT:     'libc::c_short',
        clang_types.USHORT:    'libc::c_ushort',
        clang_types.UCHAR:     'libc::c_uchar',
        clang_types.VOID:      'libc::c_void',
        clang_types.LONG:      'libc::c_long',
        clang_types.ULONG:     'libc::c_ulong',
        clang_types.ULONGLONG: 'libc::c_ulonglong',
        clang_types.LONGLONG:  'libc::c_longlong',
        clang_types.DOUBLE:    'libc::c_double',
        clang_types.FLOAT:     'libc::c_float',
        clang_types.ENUM:      'libc::c_uint',
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
        #return 'libc::c_int /* INCOMPLETEARRAY */'
        return "*mut %s /* INCOMPLETEARRAY */" % rustify_type(canonical.get_array_element_type())
    elif canonical_kind == clang_types.CONSTANTARRAY:
        return "[%s; %i]" % (rustify_type(canonical.get_array_element_type()),
                canonical.get_array_size())
    elif canonical_kind in mapping:
        return mapping[canonical_kind]
    else:
        #raise Exception("Not implemented: Type=%s" % canonical_kind)
        return "%s" %   node.get_canonical().kind


def rustify_function_declaration(node, link_name=None):
    args = ", ".join(map(rustify_variable_declaration, node.get_arguments()))

    res = "pub fn %s(%s)" % (canonical_function_name(node), args)

    if node.result_type.get_canonical().kind is not clang.cindex.TypeKind.VOID:
        res += ' -> %s' % rustify_type(node.result_type.get_canonical())

    res = 'extern "C" {\n\t%s;\n}\n' % res
    if link_name is not None:
        res = '#[link(name="%s")]\n%s' % (link_name, res)

    return res


def rustify_struct_declaration(node):
    canonical = node.type.get_canonical().get_declaration()
    node = node.type.get_declaration()
    res =  "#[repr(C)]\n"
    res += "pub struct %s" % node.spelling

    members = " {\n"
    for c in canonical.get_children():
        members += "\tpub %s,\n" % rustify_variable_declaration(c)

    if len(members) > 3:
        members += "}\n"
        res += members
    else:
        res += ';\n'
    return res

def rustify_enum_declaration(node):
    name = node.spelling
    if len(name) == 0:
        name = node.referenced.type.spelling

    if len(name) > 0:
        all_positive = all(map(lambda c: c.enum_value > -1, node.get_children()))

        if all_positive:
            typ = ("u32", "libc::c_uint")
        else:
            typ = ("i32", "libc::c_int")

        res = "bitflags! {\n"
        res += "\tflags %s: %s {\n" % (name, typ[1])
        for c in node.get_children():
            res += "\t\tconst %s =\t%i as %s,\n" % (c.spelling, c.enum_value, typ[1])
        res += "\t}\n"
        res += "}\n"
        res += "\n"
    else:
        res = ""
        for c in node.get_children():
            res += "pub const %s: i32 = %i;\n" % (c.spelling, c.enum_value)

    return res

def rustify_macro_declaration(macro):
    val = ''.join(map(lambda x: x.spelling, list(macro.get_tokens())[1:-1]))

    for base in [10, 16]:
        try:
            return "pub const %s: i32 = %i;\n" % (macro.displayname, int(val,base))
        except ValueError:
            pass

    return ""
