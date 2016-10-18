'''
Reads in json and yaml files, then pretty prints them.
'''

import json
import pprint as pp
import yaml

def jsonread():
    '''
    Reads in and pretty prints json file
    '''

    with open('JSON-the_list.json', 'r') as infile:
        jsonfile = json.load(infile)
    pp.pprint(jsonfile)

def yamlread():
    '''
    Reads in and pretty prints json file
    '''

    with open('YAML_the_list.yaml', 'r') as infile:
        yamlfile = yaml.load(infile)
    pp.pprint(yamlfile)
    
if __name__ == '__main__':
    jsonread()
    yamlread()
