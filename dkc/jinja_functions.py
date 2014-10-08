from google.appengine.ext import blobstore

def getBlobData(blob_keys):
    blobs = []
    for blob_key in blob_keys:
        blob_info = blobstore.BlobInfo.get(blob_key)
        blobs.append({
            "blob_key": blob_key,
            "filename": blob_info.filename,
            "content_type": blob_info.content_type,
            "size": blob_info.size
        })
    return blobs

from timezone import UTC, Eastern

def datetimeformat(value, format='%B %d, %Y - %I:%M %p'):
    try:
        value = value.replace(tzinfo=UTC())
        value = value.astimezone(Eastern)
        return value.strftime(format)
    except:
        return None

def byteConversion(size):
    i = 0
    while (size > 1024):
        size = size >> 10
        i += 1
    notation = {0: "B", 1: "KB", 2: "MB", 3: "GB"}[i]
    return "%s %s" % (size, notation)
