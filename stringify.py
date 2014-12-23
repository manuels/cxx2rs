from parser import *

def stringify_variable_declaration(node):
    if node.type.get_canonical() != node.type:
        return "\t(%s) %s [%s]" % (
            node.type.spelling,
            node.spelling,
            node.type.get_canonical().spelling)
    else:
        return "\t(%s) %s" % (
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
    canonical = node.type.get_canonical().get_declaration()
    node = node.type.get_declaration()

    res = "struct %s\n" % node.spelling
    for c in canonical.get_children():
        res += "\t%s\n" % stringify_variable_declaration(c)
    return res
