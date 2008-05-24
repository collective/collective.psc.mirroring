from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective_psc_mirroring')

class IFSMirrorConfiguration(Interface):
    """ Holds configuration information for mirrorring onto the FS. """

    path = schema.TextLine(title=_(u"The path to store files in"),
                           required=True)

    index = schema.TextLine(title=_(u"The name of the index file"),
                            default=u'index')

