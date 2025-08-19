from typing import Any, List


def is_valid_option_value_based(
    option: str, options: List[Any], raise_exception: bool = False
) -> bool:
    """
    Check if the option is valid
    """
    # convert options to string
    options_str = [str(option).lower() for option in options]
    check = option.lower() in options_str
    if raise_exception and not check:
        raise ValueError(f"Invalid option: {option}")
    return check


def is_valid_option_index_based(
    option: str, options: List[Any], raise_exception: bool = False
) -> bool:
    """
    Check if the option is valid based on the index
    """
    if not option.isdigit():
        if raise_exception:
            raise ValueError(f"Invalid option: {option}")
        return False
    if int(option) <= 0:
        if raise_exception:
            raise ValueError(f"Invalid option: {option}")
        return False
    check = int(option) <= len(options)
    if raise_exception and not check:
        raise ValueError(f"Invalid option: {option}")
    return check
