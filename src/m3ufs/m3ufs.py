#!/usr/bin/env python
"""
    @author: jldupont
    @date: Jul 26, 2010
"""
import sys
import os
import errno, stat

try:
    import fuse           #@UnresolvedImport
    from fuse import Fuse #@UnresolvedImport
except:
    print "m3ufs: requires python-fuse"
    sys.exit(1)
    
try:
    import mutagen  #@UnusedImport
except:
    print "m3ufs: requires python-mutagen"
    sys.exit(1)
    
from mp3file import get_id3_params
from m3ufile import M3uFile

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
        self.symlinks={}
        self.music=[]
        self.unknown=[]
        self.m3ufile=None
        self.logger=None
        
    def set_logger(self, logger):
        self.logger=logger
    def fsinit(self, *_):
        self.logger.info("fsinit")
        
    def fsdestroy(self, *_):
        self.logger.info("fsdestroy")
        self.logger.destroy()
        
    def getattr(self, path):
        self.logger.info("getattr: path: %s" % path)
        st = BlankStat()
        if path == '/' or path=="/unknown" or path=="/music":
            st.st_mode = stat.S_IFDIR | 0755
            st.st_nlink = 2
        else:
            st.st_mode = stat.S_IFLNK | 0777
            st.st_nlink = 2  
        return st

    def readdir(self, path, offset):
        self.logger.info("readdir: path: %s - offset: %s" % (path, offset))
        dirNames=[".", ".."]
        
        if path=="/":
            dirNames.extend(["music", "unknown"])
            
        if path=="/music" or path=="/unknown":
            r=self._processM3uFile()
            if r:
                self._processMp3Files()
                self._generateSymlinks()
            
        if path=="/music":
            dirNames.extend(self.symlinks.keys())
                
        if path=="/unknown":
            dirNames.extend(self.unknown)
            
        for i in dirNames:
            yield fuse.Direntry(i)

    def readlink(self, path):
        self.logger.info("readlink: path: %s" % path)
        
        if path.startswith("/music/"):
            ln=path[7:]
            return self.symlinks[ln]
            
        if path.startswith("/unknown/"):
            link_name=path[9:]
            return link_name
        
        return -errno.ENOENT
            
        
    def _processM3uFile(self):
        if self.m3ufile is None:
            self.m3ufile=M3uFile(self.m3u, self.logger)
            
        return self.m3ufile.refresh()
        
    def _processMp3Files(self):
        self.music=[]
        self.unknown=[]
        
        for file in self.m3ufile.files:
            try:    
                artist, album, title=get_id3_params(file)
                self.music.append((file, artist, album, title))
            except:
                self.unknown.append(file)
                
        self.logger.info("music:   %s" % len(self.music))
        self.logger.info("unknown: %s" % len(self.unknown))

    def _generateSymlinks(self):
        self.symlinks={}
        
        for entry in self.music:
            file, artist, album, title=entry
            ln="%s-%s-%s.mp3" % (artist, album, title)
            link_name=ln.encode("UTF-8")
            self.symlinks[link_name]=file
            self.logger.info(">> symlink: [%s] -> [%s]" % (link_name, file))
        

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
    fs.parser.add_option(mountopt="m3u", default="", help=".m3u file path")
    fs.flags = 0
    fs.multithreaded = False
    fs.parse(values=fs, errex=1)
    logger=create_logger(fs.m3u, "m3ufs")
    fs.set_logger(logger)
    try:
        fs.main()
    except Exception,e:
        print e

if __name__ == "__main__":
    main()
    
