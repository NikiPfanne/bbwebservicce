import sys as system
import os
import json
import re
from .__init__ import MAIN_PATH

class Config:
    def __init__(self) -> None:
        
        '''The config class loads the config attributes form the config.json file
        if an error occurs the programm will terminate.'''
        
        config_path = MAIN_PATH +"/config/config.json"
        
        with open(config_path,'r') as file:
            error_prefix = '[CONFIG_ERROR]'
            content = ''.join(file.readlines())
            config = json.loads(content)
            if 'ip' in config:
                self.SERVER_IP = config['ip']
            else:
                print(error_prefix," the required property 'ip' is missing.")
                system.exit(0)
            if 'port' in config:
                self.SERVER_PORT = config['port']
            else:
                print(error_prefix," the required property 'port' is missing.")
                system.exit(0)
            if 'queue_size' in config:
                self.QUE_SIZE = config['queue_size']
            else:
                print(error_prefix," the required property 'queue_size' is missing.")
                system.exit(0)
            if 'SSL' in config:
                self.SSL = config['SSL']
            else:
                print(error_prefix," the required property 'SSL' is missing.")
                system.exit(0)
            if self.SSL:
                if 'cert_path' in config:
                    self.CERT_PATH = config['cert_path']
                else:
                    print(error_prefix," the required property 'cert_path' is missing.")
                    system.exit(0)
                if 'key_path' in config:
                    self.KEY_PATH = config['key_path']
                else:
                    print(error_prefix," the required property 'key_path' is missing.")
                    system.exit(0)
           
