import csv


def safeget(iterable, *keys, **kwargs):
    if not iterable:
        return kwargs.get("default")
    for key in keys:
        try:
            iterable = iterable[key]
        except (KeyError, IndexError):
            return kwargs.get("default")
    return iterable


def get_abs(value):
    """
    This function returns absolute value.
    Args:
        value: int or float. value to be converted
    Returns:
        absolute value: int or float. absolute value
    """
    if value:
        return abs(value)
    return None


def to_csv(header, data):
    """
    This function generates the csv file with required data
    Args:
        header: list. heading of each column
        data: list. value of each row corresponding to a column

    """
    with open("most_volatile_stock.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerow(data)
