'''
Using SNMPv3 create two SVG image files.

The first image file should graph the input and output octets on interface FA4
on pynet-rtr1 every five minutes for an hour.  Use the pygal library to create
the SVG graph file. Note, you should be doing a subtraction here (i.e. the
input/output octets transmitted during this five minute interval).

The second SVG graph file should be the same as the first except graph the
unicast packets received and transmitted
'''

from collections import namedtuple, defaultdict
from datetime import datetime
from setup_logging import setup_logging
from snmp_helper import snmp_get_oid_v3, snmp_extract
import logging
import pygal
import time
import yaml

class Network_Devices(object):
    '''
    Class to hold snmp variables and methods
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
        Helper function to return integer of returned oid
        '''

        oid_int = int(snmp_extract(snmp_get_oid_v3(
             self.snmp_device, self.snmp_user, oid)))
        return oid_int

    def ret_oid_d(self):
        '''
        Gathers SNMP polling data. Returns dictionary
        '''

        oid_d = defaultdict(list)
        logger = logging.getLogger('ret_oid_d')
        oid_d = {'timestamp': time.time(),
                'ifInOctets_fa4': self.get_oid(self.ifInOctets_fa4),
                'ifInUcastPkts_fa4': self.get_oid(self.ifInUcastPkts_fa4),
                'ifOutUcastPkts_fa4': self.get_oid(self.ifOutUcastPkts_fa4),
                'ifOutOctets_fa4': self.get_oid(self.ifOutOctets_fa4)}
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

def poller(devices_l, period=300, duration=3600):

    '''
    Iterates over devcies to execute polling at intervales of 'period'
    until 'duration' is reached in seconds.

    Returns
    -------
    oid_d {<device_name> :
               <oid_name> : [ num, num...],
               ...
           <start counts> :
               <oid_name>: num
               ...
               timestamp: num
          <timestamp>:
               time.time()
               ...
               }
    '''

    logger = logging.getLogger('poller')
    logger.info('Polling for %s seconds with period %s seconds', duration,\
            period)
    end_time = time.time() + duration
    oid_d = defaultdict(list)
    for device in devices_l:
        oid_d[device.name] = defaultdict(list)
        oid_d[device.name]['start time'] = time.time()
        oid_d[device.name]['start counts'] = dict()
        for oid, value in device.ret_oid_d().iteritems():
            oid_d[device.name]['start counts'][oid] = value
        while time.time() < end_time:
            time.sleep(period)
            for oid, value in device.ret_oid_d().iteritems():
                oid_d[device.name][oid].append(value)
            logger.info('oid_d %s', repr(oid_d))
    logger.info('Polling completed')
    return oid_d


def sum_counts(in_l, start_count):
    '''
    Helper function that takes absolute counts and returns list of deltas
    '''

    ret_l = []
    for count in in_l:
        ret_l.append(count - start_count)
        start_count = count
    return ret_l


def graph_draw(oid_d):
    '''
    Takes dictionary from poller, uses values to write two svg graphs to disk
    '''

    logger = logging.getLogger('graph_draw')
    for device in oid_d.keys():
        ts = oid_d[device]['timestamp']
        x_labels = []
        x_labels = [datetime.fromtimestamp(timestamp).strftime\
                ('%M:%S') for timestamp in ts]
        fa4_in_octets = []
        fa4_in_octets_st_ct = oid_d[device]['start counts']['ifInOctets_fa4']
        fa4_in_octets.extend(sum_counts(oid_d[device]['ifInOctets_fa4'],
            fa4_in_octets_st_ct))
        fa4_out_octets = []
        fa4_out_octets_st_ct = oid_d[device]['start counts']['ifOutOctets_fa4']
        fa4_out_octets.extend(sum_counts(oid_d[device]['ifOutOctets_fa4'],
            fa4_out_octets_st_ct))
        fa4_in_packets = []
        fa4_in_packets_st_ct = oid_d[device]['start counts']['ifInUcastPkts_fa4']
        fa4_in_packets.extend(sum_counts(oid_d[device]['ifInUcastPkts_fa4'],
            fa4_in_packets_st_ct))
        fa4_out_packets = []
        fa4_out_packets_st_ct = oid_d[device]['start counts']['ifOutUcastPkts_fa4']
        fa4_out_packets.extend(sum_counts(oid_d[device]['ifOutUcastPkts_fa4'],
            fa4_out_packets_st_ct))

    octet_chart = pygal.Line()
    octet_chart.title = 'Input/Output octets'
    octet_chart.x_labels = x_labels
    octet_chart.add('fa4_InOctets', fa4_in_octets)
    octet_chart.add('fa4_OutOctets', fa4_out_octets)
    octet_chart.render_to_file('octet.svg')
    logger.info('octet.svg written')

    packet_chart = pygal.Line()
    packet_chart.title = 'Input/Output packets'
    packet_chart.x_labels = x_labels
    packet_chart.add('fa4_InPackets', fa4_in_packets)
    packet_chart.add('fa4_OutPackets', fa4_out_packets)
    packet_chart.render_to_file('packet.svg')
    logger.info('packet.svg written')



def save_object_yaml(py_object, yaml_file='default.yaml'):
    '''
    Helper function that save a python object to a yaml file
    Mostly used for development to save time by using the same data set for
    different graph experiements.
    '''

    with open(yaml_file, 'w') as outfile:
        yaml.dump(py_object, outfile, default_flow_style=False)
    return True

def load_object_yaml(yaml_file='default.yaml'):
    '''
    Used to load a preveiously collected set of SNMP data for development 
    puproses, commented out in main()
    '''

    with open(yaml_file, 'r') as infile:
        oid_l = yaml.load(infile)
    return oid_l


def main():

    logger = logging.getLogger('main')
    device_d = load_yaml()
    devices_l = create_objects(device_d)
    oid_d = poller(devices_l)
    save_object_yaml(oid_d)

# Comment out device_d, devices_l, oid_d and save_object_yaml and uncomment
# loaded_oid in order to load perviously collected data and graph.
#    loaded_oid = load_object_yaml() 
    graph_draw(oid_d)

if __name__ == '__main__':
    setup_logging()
    main()

