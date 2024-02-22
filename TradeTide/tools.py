import numbers


def percent_to_float(string_value):
    """
    Converts a percentage string to a float.

    If the input is already a number, it returns the input as-is. If the input is a string formatted as a percentage
    (e.g., "50.5%"), it converts this string to a float representing the decimal form of the percentage (e.g., 0.505).

    Parameters:
        string_value (str or numbers.Number): The percentage string or a numeric value.

    Returns:
        float: The input percentage as a decimal if the input is a string, or the original numeric value if the input is a number.
    """
    if isinstance(string_value, numbers.Number):
        return string_value

    if '%' not in string_value:
        return float(string_value)

    else:
        return float(string_value.replace(',', '.')[:-1]) / 100
