from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from interfaces import IFSMirrorConfiguration

from OFS.SimpleItem import SimpleItem

class FSMirrorConfiguration(SimpleItem):
    implements(IFSMirrorConfiguration)
    
    path = FieldProperty(IFSMirrorConfiguration['path'])
    index = FieldProperty(IFSMirrorConfiguration['index'])

