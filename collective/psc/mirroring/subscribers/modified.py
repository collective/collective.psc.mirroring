import os
from os.path import join

from collective.psc.mirroring.locker import write_content
from collective.psc.mirroring.locker import AlreadyLocked

from zope.component import getUtility 
from ZODB.POSException import ConflictError

from collective.psc.mirroring.interfaces import IFSMirrorConfiguration 

def handlePSCFileModifed(context, event):
    """ Handle a PSC File being modified """
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

    # getting the file to push there
    file = context.getDownloadableFile()
    # the id is the file name
    id_ = context.getId()
    # let's get the data 
    data = file.get_data()
    
    # let's write it 
    fullpath = os.path.realpath(os.path.join(root, id_))
    if index == fullpath:
        raise IOError('Cannot use the same name than the index file')

    try:
        write_content(fullpath, data, index)
    except AlreadyLocked:
        raise ConflictError('%s is locked' % fullpath)
        
