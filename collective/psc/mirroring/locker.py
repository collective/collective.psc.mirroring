"""
locking system 

XXX load the whole file in memory
"""
import fcntl
import os
from md5 import md5
from os.path import join, dirname, basename, exists

class AlreadyLocked(Exception):
    pass

def _get_lock_name(filename):
    name = basename(filename)
    return join(dirname(filename), '%s_lck' % name)

def _read_file(filename):
    f = open(filename)
    try:
        return f.read()
    finally:
        f.close()

def _write_file(filename, content, mode='w'):
    f = open(filename, mode)
    try:
        return f.write(content)
    finally:
        f.close()

def _update_index(index, filename):
    """Upgrades an index file with md5 hash"""
    md5 = file_hash(filename)
    if os.path.exists(index):
        content = _read_file(index).split('\n')
        content = dict([line.split('#') for line in content 
                        if line.split('#') == 2]) 
        content[filename] = md5
    else:
        content = {filename: md5}
    index = open(index, 'w')
    try:
        for key, value in content.items():
            index.write('%s#%s\n' % (key, value))
    finally:
        index.close()

def with_lock(filename, mode, callable_, index=None):
    """Uses fcntl to lock a file, open it, then
    call the callable_ with the file object.
    
    filename is the file to lock, mode is the open mode.

    The file is closed when the callable returns.
    """
    filename = os.path.realpath(filename)
    file_ = open(filename, mode)
    file_lock = _get_lock_name(filename)
    if exists(file_lock):
        raise AlreadyLocked('%s is already locked.' % filename)
    _write_file(file_lock, 'locked')
    fcntl.flock(file_.fileno(), fcntl.LOCK_EX)
    try:
        try:
            callable_(file_) 
        finally:
            file_.close()
        if index is not None:
             _update_index(index, filename)            
    finally:
        os.remove(file_lock)

def is_locked(filename):
    """Returns True if the filename is locked.""" 
    return exists(_get_lock_name(filename)) 

def write_content(filename, stream, index=None):
    """Writes stream content into filename.
    
    stream can be an iterator or an open file object."""
    def _write(f):
        for line in stream:
            f.write(line)
    with_lock(filename, 'wb', _write, index)

def string_hash(string):
    """returns a string hash"""
    return md5(string).hexdigest()

def file_hash(filename, index=None):
    """returns a file hash"""
    if index is not None:
        content =  _read_file(index)
        content = [line.strip() for line in content.split('\n')
                   if line.strip() != '']
        content = dict([line.split('#') for line in content])
        if filename in content:
            return content[filename]
    return md5(open(filename).read()).hexdigest()

