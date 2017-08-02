from __future__ import unicode_literals

import six


def merge_dicts(*dict_args):
    """
    Given any number of dict, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def is_string(text):
    """
    :param text: input content
    check if the text is string type, return True if it is, else return False.
    """
    if six.PY2:
        return isinstance(text, basestring)
    else:
        return isinstance(text, (str, bytes))


def convert_to_unicode(text):
    """
    :param text: input content
    If text is utf8 encoded, then decode it with utf8 and return it, else just return it.
    """
    assert is_string(text), 'text must be string types.'

    try:
        return text.decode('utf-8')
    except UnicodeEncodeError:  # python2 will raise this exception when decode unicode.
        return text
    except AttributeError:  # python3 will raise this exception when decode unicode.
        return text
