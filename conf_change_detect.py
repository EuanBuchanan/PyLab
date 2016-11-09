'''
Script that detects when a router or router's configuration changes and emails
alert.
'''

import setup_logging
import yaml
from collections import namedtuple

def rtr_config_yaml_load(confdir = '.',
                        conffile = 'rtr_snmp_config.yaml'):
    '''
    Loads SNMP infromation from yaml file as a dicitinary:

    Key: Router name (string)
    Value: list of strings -
            snmp_username,
            aut_key,
            encrypt_key,
            router_ip,
            snmp_port,
            running_last_changed,
            running_last_saved,
            startup_last_changed

    '''

    return
