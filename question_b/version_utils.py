import re


def is_version_gt(version_a, version_b):
    """

    :param str version_a: version a number
    :param str version_b: version b number
    :return: int - whether one is greater than, equal, or less than the other:
        1 - version_a is greater than version_b
        0 - version_a is equal to version_b
        -1 - version_a is less than version_b
    """
    # Params validation

    if not isinstance(version_a, str):
        raise ValueError(
            "version_a must be a string"
        )

    if not isinstance(version_b, str):
        raise ValueError(
            "version_b must be a string"
        )

    # Get the version number by regular expresion
    try:
        version_a_value = re.search(r'([\d.]+)', version_a.strip()).group(1)
    except AttributeError:
        raise ValueError(
            "version_b doesn't contain a version number"
        )
    try:
        version_b_value = re.search(r'([\d.]+)', version_b.strip()).group(1)
    except AttributeError:
        raise ValueError(
            "version_b doesn't contain a version number"
        )

    if version_a_value > version_b_value:
        return 1
    elif version_a_value < version_b_value:
        return -1
    else:
        return 0
