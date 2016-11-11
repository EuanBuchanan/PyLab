'''
Script that detects when a router or router's configuration changes and emails
alert.
'''


from collections import namedtuple
from email_helper import send_mail
from pprint import pprint
from setup_logging import setup_logging
from snmp_helper import snmp_get_oid_v3, snmp_extract
import logging
import os
import time
import yaml

class Network_Device(object):

    '''
    Creates a Router_device object
    '''

    def __init__(self, device_name , device_ip, running_last_changed,
            running_last_saved, startup_last_changed, snmp_username,
            snmp_aut, snmp_port, encrypt_key):
        self.device_name = device_name
        self.device_ip = device_ip
        self.running_last_changed = running_last_changed
        self.running_last_saved = running_last_saved
        self.startup_last_changed = startup_last_changed
        self.snmp_username = snmp_username
        self.snmp_aut = snmp_aut
        self.snmp_port = snmp_port
        self.encrypt_key = encrypt_key
        self.update_run_chg_ref = '0'
        self.update_run_sav_ref = '0'
        self.update_start_ref = '0'
        self.snmp_device = (self.device_ip, self.snmp_port)
        self.snmp_user = (self.snmp_username, self.snmp_aut, self.encrypt_key)


    def set_reference(self):
        self.update_run_chg_ref = int(
                snmp_extract(snmp_get_oid_v3(self.snmp_device, self.snmp_user,
                self.running_last_changed)))
        self.update_run_sav_ref = int(
                snmp_extract(snmp_get_oid_v3(self.snmp_device, self.snmp_user,
                self.running_last_saved)))
        self.update_start_ref = int(
                snmp_extract(snmp_get_oid_v3(self.snmp_device, self.snmp_user,
                self.startup_last_changed)))

    def get_current(self):

        Current = namedtuple('Current','running_last_changed running_last_saved\
            startup_last_changed')

        current = Current(
                int(snmp_extract(snmp_get_oid_v3(self.snmp_device,
                    self.snmp_user, self.running_last_changed))),
                int(snmp_extract(snmp_get_oid_v3(self.snmp_device,
                    self.snmp_user, self.running_last_saved))),
                int(snmp_extract(snmp_get_oid_v3(self.snmp_device,
                    self.snmp_user, self.startup_last_changed))))
        return current





def rtr_config_yaml_load(confdir = '.',
                        conffile = 'rtr_snmp_config.yaml'):
    '''
    Loads device infromation from yaml file and returns dictionary:

    Key: Router name (string)
    Value: list of strings -
            snmp_username,
            aut_key,
            encrypt_key,
            snmp_port,
            running_last_changed,
            running_last_saved,
            startup_last_changed
            device_ip,
    '''

    logger = logging.getLogger('rtr_config_yaml_loader')
    filepath = os.path.join(confdir, conffile)
    with open(filepath, 'r') as infile:
        logger.info('Loading router snmp config from %s', filepath)
        rtr_config = yaml.load(infile)
        #logger.debug('Router snmp config\n %s', pprint.pprint(rtr_config))

    return rtr_config


def create_network_objects():
    '''
    Iterates over network_devices_l to create an instance of Network_Device
    for each device. Returns list of class objects
    '''

    logger = logging.getLogger('create_network_objects')
    network_devices_l = []
    rtr_config = rtr_config_yaml_load()
    for key, values in rtr_config['routers'].iteritems():
        network_device = Network_Device(key, values['device_ip'],
                values['running_last_changed'], values['running_last_saved'],
                values['startup_last_changed'], values['snmp_username'],
                values['aut_key'], values['snmp_port'], values['encrypt_key'])
        network_devices_l.append(network_device)
        logger.info('Created device %s ', network_device.device_name)
    return network_devices_l

def send_email(device):

    logger = logging.getLogger('send_email')


    recipient = 'euan_b_oz@hotmail.com'
    logger.debug('recipient %s', recipient)
    subject = device.device_name + ' running config changed'
    logger.debug('subject %s', subject)
    message = 'Running conifguration on ' + device.device_name +\
            ' ' + device.device_ip + ' has been changed.'
    logger.debug('message %s', message)
    sender = 'ebuchanan@twb-tech.com'
    logger.debug('sender %s', sender)

    send_mail(recipient, subject, message, sender)



def main():
    '''
    Polls list of devices by SNMP every 60 seconds checking if the
    configuration has been changed. Logs warning and emails alert if running
    config is changed.
    '''

    setup_logging()
    logger = logging.getLogger('main')
    network_devices_l = create_network_objects()
    logger.debug('network_devices_l %s ', network_devices_l)
    for device in network_devices_l:
        device.set_reference()
        logger.info('run_chg_ref: %s, run_sav_ref: %s, start_chg_ref: %s',
                device.update_run_chg_ref, device.update_run_chg_ref,
                device.update_start_ref)

    while True:
        for device in network_devices_l:
            logger.info('Polling device %s', device.device_name)
            current = device.get_current()
            logger.debug('run_chg_ref: %s', device.update_run_chg_ref)
            logger.debug('run_chg_cur: %s', current.running_last_changed)
            if device.update_run_chg_ref < current.running_last_changed:
                logger.warn('Device: %s IP: %s running config has changed!',
                        device.device_name, device.device_ip)
                send_email(device)
                device.update_run_chg_ref = current.running_last_changed
        time.sleep(60)

if __name__ == '__main__':

    main()
