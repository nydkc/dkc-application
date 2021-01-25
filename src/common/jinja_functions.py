import re
from datetime import datetime
from typing import Iterable
from google.cloud import ndb
from common.timezone import UTC, Eastern


def datetimeformat(value, format="%B %d, %Y - %I:%M %p %Z"):
    try:
        value = value.replace(tzinfo=UTC())
        value = value.astimezone(Eastern)
        return value.strftime(format)
    except:
        return value


def byteConversion(size):
    i = 0
    while size > 1024:
        size /= 1024
        i += 1
    notation = ["B", "KB", "MB", "GB"][i]
    return "{:.2f} {}".format(size, notation)


def toFileInfo(gcs_obj_ref_keys):
    file_infos = []
    for key in gcs_obj_ref_keys:
        obj_ref = key.get()
        file_infos.append(
            {
                "key": obj_ref.key.urlsafe().decode("utf-8"),
                "filename": obj_ref.filename,
                "content_type": obj_ref.content_type,
                "size": byteConversion(obj_ref.bytes_size),
            }
        )
    return file_infos


def splitString(value, separator=" "):
    return value.split(separator)


def splitRegex(value, seperator_pattern):
    return re.split(seperator_pattern, value)


def search(value, search):
    if value == None:  # Hack to take care of Nonetype
        value = "None"
    value_lower = value.lower()
    search_lower = search.lower()
    found_indexes = []
    i = 0
    while value_lower.find(search_lower, i) != -1:
        i = value_lower.find(search_lower, i)
        found_indexes.append(i)
        i += 1

    if len(found_indexes) > 0:
        s = 0
        start = 0
        result = ""
        while s < len(found_indexes):
            pos = found_indexes[s]
            result += (
                value[start:pos] + "<mark>" + value[pos : pos + len(search)] + "</mark>"
            )
            start = pos + len(search)
            s += 1
        result += value[start:]
        return result
    else:
        return value


def getVars(classobject):
    return [
        attr
        for attr in dir(classobject)
        if not callable(attr) and not attr.startswith("_")
    ]


JINJA_OPTIONS = {
    "extensions": ["jinja2.ext.autoescape"],
}

ADDITIONAL_JINJA_FILTERS = {
    "datetimeformat": datetimeformat,
    "byteconvert": byteConversion,
    "to_file_info": toFileInfo,
    "split_string": splitString,
    "split_regex": splitRegex,
    "highlight_search": search,
    "getvars": getVars,
}

ADDITIONAL_JINJA_GLOBALS = {
    "zip": zip
}
