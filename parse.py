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
    print "\nBlocks matcing '" + expression + "'\n---\n"
    for line in crypto_map_match_l:
            print line

def match_entries_w_expr(filename, parent, child):
    '''
    Fucntion that matches expression and prints parents contiaining them.

    Pareamaters
    ===========
    filename : string, the name of the file. Path is relaitve to where the
                scrit is called from
    parent:  string, matches parent specs to be searched
    child:  string, matches child specs to be searched

    Returns
    =======
    None

    Outputs
    =======
    Prints result to stdout
    '''

    parse = CiscoConfParse(filename)
    expr_match_l = parse.find_parents_w_child(parent, child)
    print "\nCrypto map entries containing '" + child + "'\n---\n"
    for line in expr_match_l:
        print line

def match_entries_wo_expression(filename, parent, child):
    '''
    Function that maches expression and prints parents not containing them

    Pareamaters
    ===========
    filename : string, the name of the file. Path is relaitve to where the
                scrit is called from
    parent:  string, matches parent specs to be searched
    child:  string, matches child specs to be searched

    Returns
    =======
    None

    Outputs
    =======
    Prints result to stdout
    '''

    parse = CiscoConfParse(filename)
    expr_match_l = parse.find_parents_wo_child(parent,child)
    print "\nCrypto map entries not contiaing '" + child + "\n---\n"
    for line in expr_match_l:
        child_match = parse.find_children_w_parents(line,'transform-set')
        print line
        print child_match[0]


if __name__ == '__main__':
    match_block('ciscoconfig','crypto map CRYPTO')
    match_entries_w_expr('ciscoconfig', 'crypto map', 'pfs group2')
    match_entries_wo_expression('ciscoconfig', 'crypto map',
            'transform-set AES-SHA')
