import sys
sys.path.insert(0, '../l-2')

import json

from cfg import form_blocks, block_map, add_terminators, edges

def print_blocks(blocks):
    for block in blocks:
        for ins in block:
            print(ins)


def worklist_algo(blocks, direction, init, transfer, merge):
    pre, suc = edges(blocks)

    in_ = {}
    out_ = {}

    entry_block = list(blocks.keys())[0]
    
    in_[entry_block] = init
    for block in blocks:
        out_[block] = init

    worklist = list(blocks.keys())

    while worklist:
        b = worklist.pop(0)

        in_[b] = merge([out_[p] for p in pre[b]])        
        outv = transfer(blocks[b], in_[b])

        if outv != out_[b]:
            out_[b] = outv
            worklist += suc[b]
    
    return in_, out_

def union(sets):
    out = set()
    
    for s in sets:
        out.update(s)
    
    return out

def rd_transfer(block, inv):
    outv = set()
    outv.update([ins['dest'] for ins in block if 'dest' in ins])
    outv.update(inv)

    return outv



def rd(func):
    blk_map = block_map((form_blocks(func['instrs'])))
    add_terminators(blk_map)
    
    in_, out_ = worklist_algo(blk_map, 'f', set([arg['name'] for arg in func['args']]), rd_transfer, union)

    for block in blk_map:
        print(block)
        print('\t', in_[block])
        print('\t', out_[block])
        print('\n')


if __name__ == '__main__':
    prog = json.load(sys.stdin)

    for func in prog['functions']:
        rd(func)