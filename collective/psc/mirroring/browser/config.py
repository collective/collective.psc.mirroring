from zope.formlib import form
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from five.formlib import formbase

from collective.psc.mirroring.interfaces import IFSMirrorConfiguration

_ = MessageFactory('collective_psc_mirroring')

class FSMirrorConfigurationForm(formbase.EditFormBase):
    form_fields = form.Fields(IFSMirrorConfiguration)

    label = _(u"Settings for FS mirroring")




def grab_utility(context):
    return getUtility(IFSMirrorConfiguration)
