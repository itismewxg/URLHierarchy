#coding:utf8

"""log of the module

    logger.warn("Something is wrong", {"ret_value" : -1234, "dump_obj" : obj})
    logger.info("Drop Table", {"table name" : table_name, "dump_sth" : dump})
"""


import logging 
import sys

class TextFormatter(logging.Formatter):
    """Palo Text Formatter

	typical log: the last part is the key-value dict of the param needed to
	be recorded:
    [WARNING][2013-02-18 21:56:44,801][MainThread:182894116736][log.py:57]
\[func_test][test warning][{'abc': 1234, 'hello': 'setsete'}]
    """

    def __init__(self):
        fmt = "[%(levelname)s][%(asctime)s][%(threadName)s:%(thread)d]\
[%(filename)s:%(lineno)d][%(funcName)s][%(message)s]"
        logging.Formatter.__init__(self, fmt)


    def format(self, record):
        """overload format, a desc + a params dictionary

        Args:
            record, the desc+dict
        Returns:
            formatted as [desc][str(dict)]
        """
        result = logging.Formatter.format(self, record) 
        key_value = ''
        #print record.args
        if record.args:
            try:
                key_value = str(record.args)
            except:
                key_value = 'CONVERT DICT TO STRING FAIL.'
        result = "%s[%s]" % (result, key_value)
        return result

def set_root_logger():
    """set root logger"""
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(TextFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def get_logger(name=None):
    """get the logger, set the name"""
    return logging.getLogger(name)

if __name__ != '__main__':
    set_root_logger()


