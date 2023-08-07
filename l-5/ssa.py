import sys
sys.path.insert(0, '../l-2')

import json
from collections import defaultdict

from cfg import form_blocks, block_map, add_terminators, edges, reassemble
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

def insert_phis(name_to_block, phi_args, phi_dests, types):
    for block, instrs in name_to_block.items():
        for dest, pairs in sorted(phi_args[block].items()):
            phi = {
                'op': 'phi',
                'dest': phi_dests[block][dest],
                'type': types[dest],
                'labels': [p[0] for p in pairs],
                'args': [p[1] for p in pairs],
            }
            instrs.insert(0, phi)

def get_types(func):
    types = {arg['name']: arg['type'] for arg in func.get('args', [])}
    for instr in func['instrs']:
        if 'dest' in instr:
            types[instr['dest']] = instr['type']
    return types


def rename_variables(phi_nodes_loc, name_to_block, succ, dom_tree):
    stack = defaultdict(list)
    phi_args = {block: {var: [] for var in phi_nodes_loc[block]} for block in phi_nodes_loc}
    phi_dests = {block: {var: None for var in phi_nodes_loc[block]} for block in phi_nodes_loc}
    var_name_counter = defaultdict(int)

    def get_new_name(var):
        new_name = '{}.{}'.format(var, var_name_counter[var])
        var_name_counter[var] += 1
        stack[var].insert(0, new_name)
        return new_name

    def _rename(block):
        old_s = {var: list(stck) for var, stck in stack.items()}

        for var in phi_nodes_loc[block]:
            phi_dests[block][var] = get_new_name(var)

        for ins in name_to_block[block]:
            if 'args' in ins:
                new_args = [stack[arg][0] if stack[arg] else arg for arg in ins['args']]
                ins['args'] = new_args
            if 'dest' in ins:
                ins['dest'] = get_new_name(ins['dest'])
        
        for s in succ[block]:
            for var in phi_nodes_loc[s]:
                if stack[var]:
                    phi_args[s][var].append((block, stack[var][0]))
                else:
                    phi_args[s][var].append((block, '__undefined'))

        for b in sorted(dom_tree[block]):
            _rename(b)
        
        stack.clear()
        stack.update(old_s)
    
    entry = list(name_to_block.keys())[0]
    _rename(entry)
        
    return phi_args, phi_dests

if __name__ == '__main__':
    prog = json.load(sys.stdin)

    for func in prog['functions']:
        basic_blocks = form_blocks(func['instrs'])
        name_to_block = block_map(basic_blocks)
        add_terminators(name_to_block)
        pred, succ = edges(name_to_block)

        Defs = get_Defs(name_to_block)
        dom = get_dom(func)
        dom_tree = get_dom_tree(dom)
        dom_fronts = get_dom_fronts(dom, func)
        types = get_types(func)

        phi_nodes_loc = get_phi_nodes_loc(Defs, dom_fronts, name_to_block)

        phi_args, phi_dests =  rename_variables(phi_nodes_loc, name_to_block, succ, dom_tree)

        insert_phis(name_to_block, phi_args, phi_dests, types)

        func['instrs'] = reassemble(name_to_block)

    print(json.dumps(prog, indent=2, sort_keys=True))