

def overlap(line_a, line_b):
    """
    This function accepts two lines on the x-axis and returns whether they
    overlap

    :param tuple line_a: x, y coordinates of the first line
    :param tuple line_b:  x, y coordinates of the second line
    :return: bool
    """

    # Params validation
    if not isinstance(line_a, tuple):
        raise ValueError("line_a must be a tuple instance")
    if not isinstance(line_b, tuple):
        raise ValueError("line_b must be a tuple instance")

    a_x, a_y = line_a
    b_x, b_y = line_b

    # Verify if lines overlap
    return (b_x <= a_y and b_x >= a_x) or (a_x <= b_y and a_x >= b_x)
