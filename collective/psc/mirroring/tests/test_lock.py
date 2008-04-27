import unittest
import os

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

