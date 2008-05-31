import os
from os.path import join

from collective.psc.mirroring.locker import write_content
from collective.psc.mirroring.locker import AlreadyLocked
from collective.psc.mirroring.locker import file_hash 
from collective.psc.mirroring.locker import string_hash
from collective.psc.mirroring.locker import remove_file

from zope.component import getUtility 
from ZODB.POSException import ConflictError

from collective.psc.mirroring.interfaces import IFSMirrorConfiguration 
from Products.CMFCore.utils import getToolByName

files_shown = ('alpha', 'beta', 'final', 'release-candidate')


def handle_state_change(context, event):
    """ Handle a release being modified """
    wf = getToolByName(context, 'portal_workflow')

    state = wf.getInfoFor(context, 'review_state', None)

    # getting the folder
    util = getUtility(IFSMirrorConfiguration) 
    root = util.path
    if root is None:
        # nothing to be done on an unset path
        return
    if not os.path.exists(root):
        raise IOError('%s does not exists' % root)

    if not os.path.isdir(root):
        raise IOError('%s should be a directory' % root)
   
    
    index = join(root, util.index)
    
    
    files = [(os.path.realpath(os.path.join(root, id_)), ob)
             for id_, ob in context.objectItems()]

    if state in files_shown:
        # need to show the files
        for path, file in files:
            # getting the file to push there
            file = file.getDownloadableFile()
            # let's get the data 
            data = file.get_data()
            if index == path:
                raise IOError('Cannot use the same name than the index file')

            # if the MD5 is equal, we don't do anything
            if os.path.exists(path):
                if file_hash(path, index) == string_hash(data):
                    return
            try:
                write_content(path, data, index)
            except AlreadyLocked:
                raise ConflictError('%s is locked' % path)
    else:
        # need to remove them
        for path, file in files:
            if os.path.exists(path):
                try:
                    remove_file(path)
                except AlreadyLocked:
                    raise ConflictError('%s is locked' % path)

