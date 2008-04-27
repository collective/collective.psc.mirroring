import fcntl
import os
from os.path import join, dirname, basename, exists

class AlreadyLocked(Exception):
    pass

def _get_lock_name(filename):
    name = basename(filename)
    return join(dirname(filename), '%s_lck' % name)

def with_lock(filename, mode, callable_):
    """Uses fcntl to lock a file, open it, then
    call the callable_ with the file object.
    
    filename is the file to lock, mode is the open mode.

    The file is closed when the callable returns.
    """
    file_ = open(filename, mode)
    file_lock = _get_lock_name(filename)
    if exists(file_lock):
        raise AlreadyLocked('%s is already locked.' % filename)
    open(file_lock, 'w').write('locked')
    fcntl.flock(file_.fileno(), fcntl.LOCK_EX)
    try:
        callable_(file_) 
    finally:
        file_.close()
        os.remove(file_lock)

def is_locked(filename):
    """Returns True if the filename is locked.""" 
    return exists(_get_lock_name(filename)) 

def write_content(filename, stream):
    """Writes stream content into filename.
    
    stream can be an iterator or an open file object."""
    def _write(f):
        for line in stream:
            f.write(line)
    with_lock(filename, 'wb', _write)

