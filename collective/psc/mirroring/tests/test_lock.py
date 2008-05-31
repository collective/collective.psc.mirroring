import unittest
import os
import threading
import time

curdir = os.path.dirname(__file__)

from collective.psc.mirroring import locker

class TestLocker(unittest.TestCase):
    
    def setUp(self):
        self.my_file = os.path.join(curdir, 'sample')
        self.target = os.path.join(curdir, 'target.tar.gz')
        self.index = os.path.join(curdir, 'index')

    def tearDown(self):
        for f in (self.target, self.my_file, self.index):
            if os.path.exists(f):
                os.remove(f)

    def test_basic_locking(self):
        def my_process(the_file):
            self.assert_(locker.is_locked(self.my_file))
            the_file.write('to it')
        
        # let's lock a file
        locker.with_lock(self.my_file, 'w', my_process)
        # we should have some content
        content = open(self.my_file).read()
        self.assertEquals(content, 'to it')
        self.assert_(not locker.is_locked(self.my_file))  

    def test_file_hash(self):
        open(self.target, 'w').write('ok')
        hash = locker.file_hash(self.target)
        self.assertEquals(hash, '444bcb3a3fcf8389296c49467f27e1d6')

    def test_thread_access(self):
        # make sure the lock is really preventing several
        # thread to conflict
        class Worker(threading.Thread):
            def __init__(self, filename, name):
                threading.Thread.__init__(self, name=name)
                self.filename = filename

            def _write(self, file_):
                for i in range(10):  
                    file_.write('%s\n' % self.getName())
                    time.sleep(0.4)

            def run(self):
                locker.with_lock(self.filename, 'w', self._write)
        
        w1 = Worker(self.my_file, 'worker1')
        w1.start()
        self.assert_(locker.is_locked(self.my_file))
        self.assertRaises(locker.AlreadyLocked, 
                          locker.with_lock,
                          self.my_file, 'w', lambda f: f.write('.'))
        w1.join()


    def test_write_content(self):
        content = open(os.path.join(curdir, 'sample.tar.gz'))
        locker.write_content(self.target, content)

        # make sure it does the job for real
        wanted = open(os.path.join(curdir, 'sample.tar.gz')).read()
        res = open(self.target).read()
        
        self.assertEquals(wanted, res)
       
    def test_basic_locking_with_index(self):
        
        def my_process2(the_file):
            self.assert_(locker.is_locked(self.my_file))
            the_file.write('to it 2')

        def my_process(the_file):
            self.assert_(locker.is_locked(self.my_file))
            the_file.write('to it')
        
        # let's lock a file
        locker.with_lock(self.my_file, 'w', my_process, self.index)

        # we should have some content
        content = open(self.my_file).read()
        self.assertEquals(content, 'to it')
        self.assert_(not locker.is_locked(self.my_file))  
        
        # let's check the index file
        index_file = open(self.index).readlines()
        indexes = [f.split('#') for f in index_file]
        index = indexes[0]
        self.assertEquals(index[0], self.my_file)
        self.assertEquals(index[1].strip(), 
                          '6a94cc3e2b33c83937018b3ce365643c')

        locker.with_lock(self.my_file, 'w', my_process2, self.index)

        # the md5 should have changed
        index_file = open(self.index).readlines()
        indexes = [f.split('#') for f in index_file]
        index = indexes[0] 
        self.assertEquals(index[1].strip(), 
                          '39d03242196d6cbf4389bfcfe2f2b989') 
 
    def test_time_lock(self):
        # make sure the lock is removed after a while
        old = locker.MAX_LOCK_TIME
        locker.MAX_LOCK_TIME = 0.5
        
        def my_process2(the_file):
            self.assert_(locker.is_locked(self.my_file))

        def my_process(the_file):
            self.assert_(locker.is_locked(self.my_file))
            time.sleep(1)
            locker.with_lock(self.my_file, 'w', my_process2)

        # let's lock a file
        try:
            locker.with_lock(self.my_file, 'w', my_process)
        finally:
            locker.MAX_LOCK_TIME = old

    def test_decorator(self):
        # we also have a decorator
        @locker.locked(self.my_file)
        def something_done():
            self.assert_(locker.is_locked(self.my_file))

    def test_deletion(self):

        def my(f):
            f.write('wwww')

        locker.with_lock(self.my_file, 'w', my, self.index)
        
        content = open(self.index).read().split('#') 
        self.assertEquals(content[-1].strip(), 
                          'e34a8899ef6468b74f8a1048419ccc8b')

        # let's remove a file
        locker.remove_file(self.my_file, self.index)
        # should be gone
        assert not os.path.exists(self.my_file)

        # should be gone from index
        content = open(self.index).read()    
        self.assertEquals(content, '')

def test_suite():
    return unittest.TestSuite((unittest.makeSuite(TestLocker),))
    

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

