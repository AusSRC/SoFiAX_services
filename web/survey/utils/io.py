import io
import tarfile


def tarfile_write(tar, filename, content):
    """Helper function for writing content to a tarfile.

    """
    info = tarfile.TarInfo(filename)
    info.size = len(content)
    tar.addfile(info, io.BytesIO(initial_bytes=content))
