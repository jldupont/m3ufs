"""
    @author: jldupont
    @date: Jul 29, 2010
"""
import os
__all__=["M3uFile"]


class M3uFile(object):
    def __init__(self, path, logger):
        self.path=os.path.expanduser(path)
        self.logger=logger
        self.modif=None
        self.files=[]

    def refresh(self):
        """
        Verifies if the underlying .m3u changed
        since the last processing
        
        @return: False: no change, True: change detected
        """
        try:
            mtime=os.path.getmtime(self.path)
        except:
            self.logger.error("Error accessing .m3u file")
            return
        
        if mtime==self.modif:
            return False
        
        self.modif=mtime
        
        self.logger.info("Processing .m3u file")
        self._process()
        return True
        
    def _process(self):
        self.files=[]
        try:
            file=open(self.path, "r")
            for line in file:
                l=line.lstrip()
                if l.startswith("#"):
                    continue
                self.files.append(l)
                
            self.logger.info("Number of entries: %s" % len(self.files))
                
        except Exception,e:
            self.logger.error("Error processing .m3u file (%s)" % e)
        finally:
            try:    file.close()
            except: pass

    


if __name__=="__main__":
    class Logger(object):
        def info(self, msg):
            print "info: "+msg
        def error(self, msg):
            print "error: "+msg
            
    l=Logger()
    mf=M3uFile("~/MyTopRated.m3u", l)
    mf.refresh()
    
    
