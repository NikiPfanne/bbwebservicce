import os
import sys
import re

default_config = '''
{
    "ip": "default",
    "port": 5000,
    "queue_size": 10,
	"SSL": false,
	"cert_path" : "",
	"key_path" : ""
}
'''

MAIN_PATH = ''
modules = sys.modules.copy()
for key in modules:
    mod = modules[key]
    if mod.__name__ == '__main__':
        MAIN_PATH = "/".join(re.split('/|\\\\',os.path.abspath(mod.__file__))[:-1])
        
        if not os.path.exists(MAIN_PATH + "/content"):
            os.makedirs(MAIN_PATH + "/content")

        if not os.path.exists(MAIN_PATH + "/config"):
            os.makedirs(MAIN_PATH + "/config")

        if not os.path.exists(MAIN_PATH + "/config/config.json"):#
            with open(MAIN_PATH + "/config/config.json", 'w') as config:
                config.writelines(str(default_config))

        from .webserver import *