import unittest
import os
import shutil
from os.path import join

from zope.testing import doctestunit
from zope.component import testing
from zope.component import getUtility
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.Archetypes.event import ObjectEditedEvent
from Products.PloneSoftwareCenter.tests import base
from ZODB.POSException import ConflictError 

from zope.formlib import form
from zope.event import notify
from zope.publisher.browser import TestRequest

from collective.psc.mirroring.interfaces import IFSMirrorConfiguration
import collective.psc.mirroring

ptc.setupPloneSite(products=["collective.psc.mirroring"])

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.psc.mirroring)
            fiveconfigure.debug_mode = False
            ztc.installPackage('collective.psc.mirroring')

        @classmethod
        def tearDown(cls):
            pass

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        self.psc = self.portal.psc
        self.proj = self.portal.psc.proj
        self.proj.invokeFactory('PSCReleaseFolder', 'relfolder')
        self.proj.relfolder.invokeFactory('PSCRelease', 'rel') 
        self.proj.relfolder.rel.invokeFactory('PSCFile', 'file')
        self.file_path = join(os.path.dirname(__file__), 'files')
        if not os.path.exists(self.file_path):
            os.mkdir(self.file_path)

        config = IFSMirrorConfiguration(self.portal)
        mirror_form = form.Fields(IFSMirrorConfiguration)
        mirror_form.get("path").field.set(config, unicode(self.file_path))
        self.edited = ObjectEditedEvent(self.proj.relfolder.rel.file)

    def tearDown(self):
        shutil.rmtree(self.file_path)

    def test_copied(self):
        # let's notify a IObjectEditedEvent event
        notify(self.edited)
       
        # we should have a file now in the folder
        contents = os.listdir(self.file_path)
        self.assertEquals(contents, ['file'])

    def test_lock(self):
        # let's lock the file
        from collective.psc.mirroring.locker import with_lock
        filename = join(self.file_path, 'file')

        def locked_state(file_):
            # let's try to notify here, we should get a conflict error
            self.assertRaises(ConflictError, notify, self.edited)  
        
        with_lock(filename, 'wb', locked_state)

    def test_same_file_exists(self):
        # we want to avoid copying a file that is already there
        # using MD5 keys
        pass

def test_suite():
    return unittest.TestSuite((unittest.makeSuite(TestCase),))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
