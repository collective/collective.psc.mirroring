import unittest

from zope.testing import doctestunit
from zope.component import testing
from zope.component import getUtility
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from zope.formlib import form


from collective.psc.mirroring.interfaces import IFSMirrorConfiguration

ptc.setupPloneSite(products=["collective.psc.mirroring"])

from zope.publisher.browser import TestRequest

import collective.psc.mirroring

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
            
    def test_configscreen_exists(self):
        self.setRoles(['Manager'])
        config = self.portal.restrictedTraverse("@@mirroring-config")
        self.assertTrue("Settings for FS mirroring" in config())

    def test_set_path(self):
        self.setRoles(['Manager'])
        config = IFSMirrorConfiguration(self.portal)
        current_path = form.Fields(IFSMirrorConfiguration).get("path").field.get(config)
        new_path = u"/tmp/files"
        form.Fields(IFSMirrorConfiguration).get("path").field.set(config, new_path)
        set_path = form.Fields(IFSMirrorConfiguration).get("path").field.get(config)
        self.assertEquals(new_path, set_path)      
        
        locutil = getUtility(IFSMirrorConfiguration)
        lpath = locutil.current_path = form.Fields(IFSMirrorConfiguration).get("path").field.get(config)
        self.assertEqual(set_path, lpath)

    def test_set_index(self):
        self.setRoles(['Manager'])
        config = IFSMirrorConfiguration(self.portal)
        current_index = form.Fields(IFSMirrorConfiguration).get("index").field.get(config)
        new_index = u"md5"
        form.Fields(IFSMirrorConfiguration).get("index").field.set(config, new_index)
        set_index = form.Fields(IFSMirrorConfiguration).get("index").field.get(config)
        self.assertEquals(new_index, set_index)      
        
        locutil = getUtility(IFSMirrorConfiguration)
        lindex = locutil.current_path = form.Fields(IFSMirrorConfiguration).get("index").field.get(config)
        self.assertEqual(set_index, lindex)



def test_suite():
    return unittest.TestSuite((unittest.makeSuite(TestCase),))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
