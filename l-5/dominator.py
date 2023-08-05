import sys
sys.path.insert(0, '../l-2')

import json

from cfg import form_blocks, block_map, add_terminators, edges

def intersect(sets):
    print(sets)
    sets = list(sets)
    if not sets:
        return set()
    out = set(sets[0])
    for s in sets[1:]:
        out &= s
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
            print(name)
            nDom = intersect([dom[p] for p in pre[name]])
            nDom.add(name)

            print(nDom)

            if nDom != dom[name]:
                dom[name] = nDom
                changed = True
        
        if not changed:
            break

    return dom

if __name__ == '__main__':
    prog = json.load(sys.stdin)

    for func in prog['functions']:
        (get_dom(func))