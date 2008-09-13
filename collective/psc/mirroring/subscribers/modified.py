import os
from os.path import join

from collective.psc.mirroring.locker import write_content
from collective.psc.mirroring.locker import AlreadyLocked
from collective.psc.mirroring.locker import file_hash 
from collective.psc.mirroring.locker import string_hash
from collective.psc.mirroring.locker import remove_file

from zope.component import getUtility 
from zope.component import ComponentLookupError
from ZODB.POSException import ConflictError

from collective.psc.mirroring.interfaces import IFSMirrorConfiguration 
from Products.CMFCore.utils import getToolByName

files_shown = ('alpha', 'beta', 'final', 'release-candidate', 'hidden')

def _get_mirror_config():
    try:
        return getUtility(IFSMirrorConfiguration)
    except ComponentLookupError:
        return None

def _release_visible(rel):
    wf = getToolByName(rel, 'portal_workflow')
    state = wf.getInfoFor(rel, 'review_state', None)
    return state in files_shown

def _write_file(file, path, index):
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


def handle_state_change(context, event):
    """ Handle a release being modified """
    visible = _release_visible(context)

    # getting the folder
    util = _get_mirror_config()
    if util is None or util.path is None:
        # not installed or not configured
        return None

    root = util.path
    if not os.path.exists(root):
        raise IOError('%s does not exists' % root)

    if not os.path.isdir(root):
        raise IOError('%s should be a directory' % root)
   
    index = join(root, util.index)
    files = [(os.path.realpath(os.path.join(root, id_)), ob)
             for id_, ob in context.objectItems()]

    if visible:
        # need to show the files
        for path, file in files:
             _write_file(file, path, index)
    else:
        # need to remove them
        for path, file in files:
            if os.path.exists(path):
                try:
                    remove_file(path)
                except AlreadyLocked:
                    raise ConflictError('%s is locked' % path)

def handle_file_added(context, event):
    """adds/changes a file only if its container release is published
    
    handle_state_change takes care of removing file
    when a release change of state.
    """
    release = context.getParentNode()
    if not _release_visible(release):
        return 
 
    util = _get_mirror_config()     
    if util is None or util.path is None:
        # not installed or not configured
        return
    
    filepath = os.path.join(util.path, context.getId())
    _write_file(context, filepath, util.index)
  
def handle_file_removed(context, event):
    """removes file only if release is published
    
    handle_state_change takes care of removing file
    when a release change of state.
    """
    release = context.getParentNode()
    if not _release_visible(release):
        return

    util = _get_mirror_config()     
    if util is None or util.path is None:
        # not installed or not configured
        return

    root = util.path
    filepath = os.path.join(root, context.getId())
    try:
        remove_file(filepath)
    except AlreadyLocked:
        raise ConflictError('%s is locked' % filepath)

