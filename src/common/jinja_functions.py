import re
from google.cloud import ndb
# from google.appengine.ext import blobstore
from dkc.timezone import UTC, Eastern
from datetime import datetime
# from models import Settings


# def getBlobData(blob_keys):
#     blobs = []
#     for blob_key in blob_keys:
#         blob_info = blobstore.BlobInfo.get(blob_key)
#         blobs.append({
#             "blob_key": blob_key,
#             "filename": blob_info.filename if blob_info else None,
#             "content_type": blob_info.content_type if blob_info else None,
#             "size": blob_info.size if blob_info else None
#         })
#     return blobs

def datetimeformat(value, format='%B %d, %Y - %I:%M %p %Z'):
    try:
        value = value.replace(tzinfo=UTC())
        value = value.astimezone(Eastern)
        return value.strftime(format)
    except:
        return value

def byteConversion(size):
    i = 0
    while (size > 1024):
        size = size >> 10
        i += 1
    notation = ["B", "KB", "MB", "GB"][i]
    return "%s %s" % (size, notation)

def splitString(value, separator=' '):
    return value.split(separator)

def splitRegex(value, seperator_pattern):
    return re.split(seperator_pattern, value)

def search(value, search):
    if value == None: # Hack to take care of Nonetype
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
            result += value[start:pos] + "<mark>" + value[pos:pos+len(search)] + "</mark>"
            start = pos + len(search)
            s += 1
        result += value[start:]
        return result
    else:
        return value

def getVars(classobject):
    return [attr for attr in dir(classobject) if not callable(attr) and not attr.startswith("_")]

# def getEarlyStatus(value=None):
#     config = ndb.Key(Settings, 'config').get()
#     try:
#         return datetime.now() < config.early_due_date
#     except:
#         return True
