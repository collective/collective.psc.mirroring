import fcntl
import os
from os.path import join, dirname, basename, exists

class AlreadyLocked(Exception):
    pass

def _get_lock_name(path):
    name = basename(path)
    return join(dirname(path), '%s_lck' % name)

def with_lock(path, mode, callable):
    file = open(path, mode)
    file_lock = _get_lock_name(path)
    if exists(file_lock):
        raise AlreadyLocked('%s is already locked.' % path)
    open(file_lock, 'w').write('locked')
    fcntl.flock(file.fileno(), fcntl.LOCK_EX)
    try:
        callable(file) 
    finally:
        file.close()
        os.remove(file_lock)

def is_locked(path):
    return exists(_get_lock_name(path)) 

