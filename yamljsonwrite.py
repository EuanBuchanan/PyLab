'''
Progrm writes a list wwhich includes a dictionary contatining at least two 
keys.  Program writes this list out to file in both JSON and YAML format 
(using the expanded form)
'''

import logging.config
import os
import yaml

def setup_logging(
    default_path='access_6_logging.yaml',
    default_level=logging.INFO,
    env_key='LOG_CFG'
    ):
    """Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def listwrite():
    '''
    Writes list, including a dictionary with at least two keys
    '''

    logger = logging.getLogger()

    the_list = [ 'Element', 1, ('x','y'), {"Luna" : "Princess",
        "Littlepip" : "Stable Dweller"} ]
    logger.setLevel('DEBUG')
    logger.debug('the_list: %s', the_list)
    logger.setLevel('INFO')
    return the_list

def yamldump():
    '''
    Dumps list to yaml in long format.
    '''

    with open('YAML_the_list.yaml', 'w') as outfile:
        yaml.dump(listwrite(), outfile, default_flow_style=False)
        

if __name__ == '__main__':


    setup_logging()
    yamldump()

