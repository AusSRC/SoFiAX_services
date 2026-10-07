import io
import tarfile
import time
from datetime import datetime


def tarfile_write(tar, filename, content):
    """Helper function for writing content to a tarfile.

    """
    info = tarfile.TarInfo(filename)
    info.size = len(content)
    info.mtime = time.mktime(datetime.now().timetuple())
    tar.addfile(info, io.BytesIO(initial_bytes=content))
