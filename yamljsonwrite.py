'''
Progrm writes a list wwhich includes a dictionary contatining at least two 
keys.  Program writes this list out to file in both JSON and YAML format 
(using the expanded form)
'''

import json
import os
import yaml



def listwrite():
    '''
    Writes list, including a dictionary with at least two keys
    '''


    the_list = [ 'Element', 1, ('x','y'), {"Luna" : "Princess",
        "Littlepip" : "Stable Dweller"} ]
    return the_list

def yamldump():
    '''
    Dumps list to yaml in long format.
    '''

    with open('YAML_the_list.yaml', 'w') as outfile:
        yaml.dump(listwrite(), outfile, default_flow_style=False)
        
def jsondump():
    '''
    Dumps list to json
    '''
    with open('JSON-the_list.json', 'w') as outfile:
        json.dump(listwrite(), outfile)

if __name__ == '__main__':


    yamldump()
    jsondump()
