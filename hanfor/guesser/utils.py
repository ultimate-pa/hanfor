from copy import deepcopy


def flatten_list(nested_list):
    """Flatten an arbitrarily nested list, without recursion (to avoid
    stack overflows). Returns a new list, the original list is unchanged.
    >> list(flatten_list([1, 2, 3, [4], [], [[[[[[[[[5]]]]]]]]]]))
    [1, 2, 3, 4, 5]
    >> list(flatten_list([[1, 2], 3]))
    [1, 2, 3]
    """
    nested_list = deepcopy(nested_list)

    while nested_list:
        sublist = nested_list.pop(0)

        if isinstance(sublist, list):
            nested_list = sublist + nested_list
        else:
            yield sublist


umlaut_replacements = {
    "Ä": "Ae",
    "Ö": "Oe",
    "Ü": "Ue",
    "ä": "ae",
    "ö": "oe",
    "ü": "ue",
}

term_replacements = {
    ":=": "==",
    "== ->": "==",
    "==->": "==",
    "!= ->": "!=",
    "!=->": "!=",
    "[": "(",
    "]": ")",
    "{": "",
    "}": "",
    ".": "_",
}

replacements = {**umlaut_replacements, **term_replacements}


def replace_characters(string):
    """
    >>> replace_characters("x := y")
    'x == y'

    :param string:
    :return:
    """
    res = string
    for k, v in replacements.items():
        res = res.replace(k, v)
    return res
