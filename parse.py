'''
parses file for:
    Blocks that start with 'crypto map CRYPTO'
    All crypto map entries using PFS Group 2
    All maps not using AES (based on the transform set name. Print these 
        entries and their corresponding transform set name.
'''

from ciscoconfparse import CiscoConfParse

def match_block(filename, expression):
    '''
    Function that matches the expression as a block of IOS config.

    Parameters
    ==========
    filename : string, the name of the file. Path is relaitve to where the
                scrit is called from
    expression :  string, the expression to be matched.

    Returns
    =======
    None

    Outputs
    =======
    Prints result to stdout
    '''
    parse = CiscoConfParse(filename)
    parse.find_blocks(expression)
    crypto_map_match_l = parse.find_blocks('crypto map CRYPTO')
    for line in crypto_map_match_l:
            print line

if __name__ == '__main__':
    match_block('ciscoconfig','crypto map CRYPTO')
