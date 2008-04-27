import unittest
import os

curdir = os.path.dirname(__file__)

from collective.psc.mirroring import locker

class TestLocker(unittest.TestCase):
    
    def setUp(self):
        self.my_file = os.path.join(curdir, 'sample')

    def tearDown(self):
        if os.path.exists(self.my_file):
            os.remove(self.my_file)

    def test_basic_locking(self):
        def my_process(the_file):
            the_file.write('to it')
        # let's lock a file
        locker.with_lock(self.my_file, 'w', my_process)
        # we should have some content
        content = open(self.my_file).read()
        self.assertEquals(content, 'to it')

def test_suite():
    return unittest.TestSuite((unittest.makeSuite(TestLocker),))
    

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

