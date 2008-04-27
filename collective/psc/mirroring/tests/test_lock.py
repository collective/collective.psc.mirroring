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

    def tearDown(self):
        for f in (self.target, self.my_file):
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
        
def test_suite():
    return unittest.TestSuite((unittest.makeSuite(TestLocker),))
    

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

