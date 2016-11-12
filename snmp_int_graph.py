'''
Using SNMPv3 create two SVG image files.

The first image file should graph the input and output octets on interface FA4
on pynet-rtr1 every five minutes for an hour.  Use the pygal library to create
the SVG graph file. Note, you should be doing a subtraction here (i.e. the
input/output octets transmitted during this five minute interval).

The second SVG graph file should be the same as the first except graph the
unicast packets received and transmitted
'''
import yaml
from setup_logging import setup_logging
from collections import namedtuple, defaultdict
import logging
from snmp_helper import snmp_get_oid_v3, snmp_extract
import time
import threading

class Network_Devices(object):
    '''
    Class to hold snmp variables and methos
    '''

    def __init__(self, name, ip, snmp_username, aut_key, encrypt_key,
            snmp_port, ifDescr_fa4, ifInOctets_fa4, ifInUcastPkts_fa4,
            ifOutOctets_fa4, ifOutUcastPkts_fa4):
        '''
        Iniitialize variables for object
        '''

        self.name, self.ip, self.snmp_username = name, ip, snmp_username
        self.aut_key, self.encrypt_key = aut_key, encrypt_key
        self.snmp_port, self.ifDescr_fa4 = snmp_port, ifDescr_fa4
        self.ifInOctets_fa4, self.ifInUcastPkts_fa4 = ifInOctets_fa4,\
            ifInUcastPkts_fa4
        self.ifOutOctets_fa4, self.ifOutUcastPkts_fa4 = ifOutOctets_fa4,\
            ifOutUcastPkts_fa4
        self.snmp_device = (ip, snmp_port)
        self.snmp_user = (snmp_username, aut_key, encrypt_key)


    
    def get_oid(self, oid):
        '''
        Helper function to return integer of oid
        '''
        oid_int = int(snmp_extract(snmp_get_oid_v3(
             self.snmp_device, self.snmp_user, oid)))
        return oid_int

    def ret_oid_d(self):
        '''
        Gathers SNMP polling data. Returns dictionary
        '''
        logger = logging.getLogger('ret_oid_d')
        oid_d = {
            self.ifInOctets_fa4: self.get_oid(self.ifInOctets_fa4),
            self.ifInUcastPkts_fa4: self.get_oid(self.ifInUcastPkts_fa4),
            self.ifOutUcastPkts_fa4: self.get_oid(self.ifOutUcastPkts_fa4),
            self.ifOutOctets_fa4: self.get_oid(self.ifOutOctets_fa4)}
        logger.debug('oid_d %s', oid_d)
        return oid_d

def load_yaml():
    '''
    Loads per device information from yaml file
    '''

    logger = logging.getLogger('load_yaml')
    with open('device_graph.yaml') as infile:
        device_d = yaml.load(infile)
    logger.debug('device_d: %s', device_d)
    return device_d

def create_objects(device_d):
    '''
    Returns list of Network_Devices objects
    '''

    logger = logging.getLogger('create_objects')
    device_l = []
    for key, values in device_d['routers'].iteritems():
        device = Network_Devices(
                key, values['ip'], values['snmp_username'],
                values['aut_key'], values['encrypt_key'], values['snmp_port'],
                values['ifDescr_fa4'], values['ifInOctets_fa4'],
                values['ifInUcastPkts_fa4'], values['ifOutOctets_fa4'],
                values['ifOutUcastPkts_fa4'])
        device_l.append(device)
    logger.debug('device_l: %s', device_l)
    logger.info('Network objects created')
    return device_l

def poller(devices_l, period=5, duration=10):

    logger = logging.getLogger('poller')
    logger.info('Polling for %s seconds with period %s seconds', duration,\
            period)
    end_time = time.time() + duration
    oid_d = defaultdict(list)
    while time.time() < end_time:
        time.sleep(period)
        for device in devices_l:
            for oid, value in device.ret_oid_d().iteritems():
                oid_d[oid].append(value)
            logger.info('oid_d %s', repr(oid_d))
    logger.info('Polling completed')
    return oid_d

def save_object_yaml(py_object, yaml_file='default.yaml'):
    '''
    Helper function that save a python object to a yaml file
    '''
    with open(yaml_file, 'w') as outfile:
        yaml.dump(py_object, outfile, default_flow_style=False)
    return True

def load_object_yaml(yaml_file='default.yaml'):
    with open(yaml_file, 'r') as infile:
        oid_l = yaml.load(infile)
    return oid_l


def main():

    logger = logging.getLogger('main')
    device_d = load_yaml()
    devices_l = create_objects(device_d)
    oid_d = poller(devices_l)
    save_object_yaml(oid_d)
    loaded_oid = load_object_yaml()
    print(loaded_oid)
if __name__ == '__main__':
    setup_logging()
    main()

