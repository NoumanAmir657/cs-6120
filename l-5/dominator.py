import sys
sys.path.insert(0, '../l-2')

import json

from cfg import form_blocks, block_map, add_terminators, edges

def intersect(sets):
    sets = list(sets)
    if not sets:
        return set()
    out = set(sets[0])
    for s in sets[1:]:
        out &= s
    return out

def map_inv(map_):
    out = {key: [] for key in map_}
    for p, ss in map_.items():
        for s in ss:
            out[s].append(p)
    return out

def get_dom(func):
    blk_map = block_map(form_blocks(func['instrs']))
    add_terminators(blk_map)
    names_bb = blk_map.keys()

    pre, succ = edges(blk_map)

    dom = {name: set(n for n in names_bb) for name in names_bb}

    while True:
        changed = False

        for name in names_bb:
            nDom = intersect([dom[p] for p in pre[name]])
            nDom.add(name)

            if nDom != dom[name]:
                dom[name] = nDom
                changed = True
        
        if not changed:
            break

    return dom

def get_dom_tree(dom):
    dom_inv = map_inv(dom)

    dom_inv_strict = {a: {b for b in bs if b != a}
                      for a, bs in dom_inv.items()}


    dom_inv_strict_2x = {a: set().union(*(dom_inv_strict[b] for b in bs))
                         for a, bs in dom_inv_strict.items()}

    return {
        a: {b for b in bs if b not in dom_inv_strict_2x[a]}
        for a, bs in dom_inv_strict.items()
    }

def get_dom_fronts(dom, func):
    blk_map = block_map(form_blocks(func['instrs']))
    add_terminators(blk_map)
    _, succ = edges(blk_map)

    dom_inv = map_inv(dom)

    frontiers = {}
    for block in dom:
        dominated_succs = set()
        for dominated in dom_inv[block]:
            dominated_succs.update(succ[dominated])

        frontiers[block] = [b for b in dominated_succs
                            if b not in dom_inv[block] or b == block]

    return frontiers

def wrapper_fronts(prog):
    for func in prog['functions']:
        for k, v in get_dom_fronts(get_dom(func), func).items():
            print(k)
            print(v)


def wrapper_tree(prog):
    for func in prog['functions']:
        for k, v in get_dom_tree(get_dom(func)).items():
            print(k)
            print(v)

if __name__ == '__main__':
    prog = json.load(sys.stdin)

    if sys.argv[1] == '-t':
        wrapper_tree(prog)
    elif sys.argv[1] == '-f':
        wrapper_fronts(prog)
    else:
        wrapper_tree(prog)


    