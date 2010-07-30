"""
    @author: jldupont
    @date: Jul 29, 2010
"""
import logging

__all__=["Logger"]

class Logger(object):
    def __init__(self, path, name):
        self.name=name
        self.path=path
        self.logger=logging.getLogger(name)
        self.hdlr=logging.FileHandler(self.path)
        formatter=logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.hdlr.setFormatter(formatter)
        self.logger.addHandler(self.hdlr)
        self.logger.setLevel(logging.INFO)        

        self.logger.info("starting")

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)
        
    def error(self, msg):
        self.logger.error(msg)

    def destroy(self):
        self.hdlr.flush()
        self.hdlr.close()
        self.logger.removeHandler(self.hdlr)
        logging.shutdown()


if __name__=="__main__":
    logger=Logger("/tmp/ftest.log", "logger_test")
    logger.info("test!")
    logger.destroy()
