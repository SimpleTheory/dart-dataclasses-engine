import re
from pathlib import Path
import warnings
import functools


def project_root():
    return Path(__file__).parent.parent.parent

def find_and_replace(pattern: str | re.Pattern, replacement: str, text: str) -> tuple[str, list[re.Match]]:
    """
    Find all matches with a regex pattern and replace all instances with the replacement string.
    Return the new string with all instances of the regex matches replaced and a list of all matches found.

    :param pattern: The regex pattern to find matches. Can be a string or a re.Pattern object.
    :param replacement: The string to replace the matches with.
    :param text: The original text to search and replace in.
    :return: A tuple containing the new text and a list of matches found.
    """
    # If pattern is a string, compile it to a re.Pattern object
    if isinstance(pattern, str):
        pattern = re.compile(pattern)

    # Find all matches using the compiled pattern's findall method
    matches = list(pattern.finditer(text))

    # Replace all instances using the compiled pattern's sub method
    new_text = pattern.sub(replacement, text)

    return new_text, matches

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)
    return new_func

def suppress_syntax_warning(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            return func(*args, **kwargs)
    return wrapper

