import sys
sys.path.insert(0, '../l-2')

import json
from collections import defaultdict

from cfg import form_blocks, block_map, add_terminators, edges
from dominator import get_dom_tree, get_dom_fronts, get_dom

def get_Defs(name_to_block):
    out = defaultdict(set)

    for block_name, block in name_to_block.items():
        for ins in block:
            if 'dest' in ins:
                out[ins['dest']].add(block_name)

    return out

def get_phi_nodes_loc(Defs, dom_fronts, name_to_block):
    phi_node_loc = {block_name: set() for block_name in name_to_block}

    for var, blocks in Defs.items():
        list_blocks = list(blocks)
        for block in list_blocks:
            for df in dom_fronts[block]:
                if df not in phi_node_loc[df]:
                    phi_node_loc[df].add(var)
                if df not in list_blocks:
                    list_blocks.append(df)
    
    return phi_node_loc

if __name__ == '__main__':
    prog = json.load(sys.stdin)

    for func in prog['functions']:
        basic_blocks = form_blocks(func['instrs'])
        name_to_block = block_map(basic_blocks)
        add_terminators(name_to_block)
        pred, succ = edges(name_to_block)

        Defs = get_Defs(name_to_block)
        dom_tree = get_dom(func)
        dom_fronts = get_dom_fronts(dom_tree, func)

        phi_nodes_loc = get_phi_nodes_loc(Defs, dom_fronts, name_to_block)
        