"""
locking system 

XXX load the whole file in memory
"""
import os
from md5 import md5
import time
from os.path import join, dirname, basename, exists

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

class Index(dict):
    
    def __init__(self, filename=None):
        if filename is not None and exists(filename):
            self.load(filename)

    def load(self, filename):
    
        content = _read_file(filename).split('\n')
        for line in content:
            line = line.split('#')
            if len(line) == 2:
                self[line[0].strip()] = line[1].strip()

    def add_file(self, filename):
        """Upgrades an index file with md5 hash"""
        self[filename] = file_hash(filename)

    def synchronize(self, index_file):
        """writes the index"""
        index = open(index_file, 'w')
        try:
            for key, value in self.items():
                index.write('%s#%s\n' % (key, value))
        finally:
            index.close()

def _remove_from_index(index, filename):
    if is_locked(index):
        raise AlreadyLocked('%s is already locked.' % filename)
    lock(index)
    try:
        i = Index(index)
        if filename in i:
            del i[filename]
        i.synchronize(index)
    finally:
        unlock(index)    

def _update_index(index, filename):
    lock(index)
    try:
        i = Index(index)
        i.add_file(filename)
        i.synchronize(index)
    finally:
        unlock(index)

#
# lock API
#
MAX_LOCK_TIME = 60 * 5 

class AlreadyLocked(Exception):
    pass

def lock(filename):
    """lock a file, if already locked, raises"""
    if is_locked(filename):
        raise AlreadyLocked('%s is already locked.' % filename)
    file_lock = _get_lock_name(filename)
    _write_file(file_lock, str(time.time()))

def unlock(filename):
    """unlock a file"""
    file_lock = _get_lock_name(filename)
    if os.path.exists(file_lock):
        os.remove(file_lock)

def is_locked(filename):
    """Returns True if the filename is locked."""
    file_lock = _get_lock_name(filename)
    if exists(file_lock):
        # if the file was lock for too long, we 
        # remove the lock
        lock_date = float(_read_file(file_lock))
        if lock_date + MAX_LOCK_TIME > time.time():
            return True
    return False

def _get_lock_name(filename):
    """give a lock name, given a file"""
    name = basename(filename)
    return join(dirname(filename), '%s_lck' % name)

def locked(filename, index=None):
    def _locked(function):
        def __locked(*args, **kw):
            lock(filename)
            try:
                return function(*args, **kw)
            finally:
                _update_index(filename, index)
                unlock(filename)
        return __locked
    return _locked

def with_lock(filename, mode, callable_, index=None):
    """Used to lock a file, open it, then
    call the callable_ with the file object.
    
    filename is the file to lock, mode is the open mode.

    The file is closed when the callable returns.
    """
    filename = os.path.realpath(filename)
    lock(filename)
    file_ = open(filename, mode)
    try:
        try:
            callable_(file_) 
        finally:
            file_.close()
        if index is not None:
             _update_index(index, filename)            
    finally:
        unlock(filename)

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
    if index is not None and os.path.exists(index):
        content =  _read_file(index)
        content = [line.strip() for line in content.split('\n')
                   if line.strip() != '']
        content = dict([line.split('#') for line in content])
        if filename in content:
            return content[filename]
    return md5(open(filename).read()).hexdigest()

def remove_file(filename, index=None):
    """Used to remove a file"""
    filename = os.path.realpath(filename)
    if is_locked(filename):
        raise AlreadyLocked('%s is already locked.' % filename)
    os.remove(filename)
    if index is not None:
        _remove_from_index(index, filename)

