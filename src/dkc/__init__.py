import jinja2
from common import jinja_functions

JINJA_OPTIONS = {
    "extensions": ["jinja2.ext.autoescape"],
}
ADDITIONAL_JINJA_FILTERS = {
    "datetimeformat": jinja_functions.datetimeformat,
    "byteconvert": jinja_functions.byteConversion,
    "to_file_info": jinja_functions.toFileInfo,
    "split_string": jinja_functions.splitString,
    "split_regex": jinja_functions.splitRegex,
    "highlight_search": jinja_functions.search,
    "getvars": jinja_functions.getVars,
}
