import os
import uuid

def make_safe_filename(oldfilename):
    fn, ext = os.path.splitext(oldfilename)
    return str(uuid.uuid1()).replace('-', '')+ext.lower()