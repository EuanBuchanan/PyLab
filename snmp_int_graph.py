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
import logging

class Network_Devices(object):
    '''
    Class to hold snmp variables and methos
    '''

    def __init__(self, name, ip, snmp_username, aut_key, encrypt_key, snmp_port,
            ifDescr_fa4, ifInOctets_fa4, ifUcastPkts_fa4, ifOutOctets_fa4,
            ifOutUcastPkts_fa4):
        self.name, self.ip, self.snmpusername = name, ip, snmp_username
        self.aut_key, self.encrypt_key = aut_key, encrypt_key
        self.snmp_port, self.ifDescr_fa4 = snmp_port, ifDescr_fa4
        self.ifInOctets_fa4, self.ifUcastPkts_fa4 = ifInOctets_fa4, ifUcastPkts_fa4
        self.ifOutOctets_fa4, self.ifOutUcastPkts_fa4 = ifOutOctets_fa4, ifUcastPkts_fa4


def load_yaml():
    '''
    Loads per device information from yaml file
    '''

    logger = logging.getLogger('load_yaml')
    with open('device_graph.yaml') as infile:
        device_d = yaml.load(infile)
    logger.info('device_d: %s', device_d)


def main():
    load_yaml()
if __name__ == '__main__':
    setup_logging()
    main()

