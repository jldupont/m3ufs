#!/usr/bin/env python
"""
    @author: jldupont
    @date: Jul 26, 2010
"""
import sys
import os
import errno, stat

try:
    import fuse
    from fuse import Fuse
except:
    print "m3ufs: requires python-fuse"
    sys.exit(1)
    

thisdir=os.path.dirname(__file__)
sys.path.insert(0, thisdir)

from logger import Logger #@UnresolvedImport

usage="""\nM3U filesystem\n Mount point with symlinks to files listed in .m3u playlist"""

class BlankStat(fuse.Stat):
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

class M3uFS(Fuse):
    """
    M3U filesystem
    """
    def __init__(self, *args, **kargs):
        Fuse.__init__(self, *args, **kargs)
        self.m3u=None
        
    def set_logger(self, logger):
        self.logger=logger
    def fsinit(self, *_):
        self.logger.info("fsinit")
        
    def fsdestroy(self, *_):
        self.logger.info("fsdestroy")
        self.logger.destroy()
        
    def getattr(self, path):
        st = BlankStat()
        if path == '/':
            st.st_mode = stat.S_IFDIR | 0755
            st.st_nlink = 2
        else:
            st.st_mode = stat.S_IFLNK | 0777
            st.st_nlink = 2  
        return st

    def readdir(self, path, offset):
        self.logger.info("readdir: path: %s - offset: %s" % (path, offset))
        dirNames=[".", "..", "files"]
        
        for i in dirNames:
            yield fuse.Direntry(i)

    def readlink(self, path):
        return "/tmp/symlink"
        
def create_logger(m3ufilepath, name):
    if m3ufilepath is None:
        print "m3ufs: invalid m3u file path"
        sys.exit(1)
        
    logfilename=m3ufilepath+".log"
        
    try:
        logger=Logger(logfilename, name)
    except Exception,e:
        print "m3ufs: cannot create log file: %s -- exception: %s" % (logfilename,e)
        sys.exit(1)
        
    return logger

    

def main():
    fuse.fuse_python_api=(0, 2)
    fs = M3uFS(version="%prog "+fuse.__version__, usage=usage, dash_s_do="setsingle")
    fs.parser.add_option(mountopt="m3u", default="", help="M3u file path")
    fs.flags = 0
    fs.multithreaded = False
    fs.parse(values=fs, errex=1)
    logger=create_logger(fs.m3u, "m3ufs")
    fs.set_logger(logger)
    print fs.m3u
    try:
        fs.main()
    except Exception,e:
        print e

if __name__ == "__main__":
    main()
    
