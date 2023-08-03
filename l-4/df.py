import sys
sys.path.insert(0, '../l-2')

import json

from cfg import form_blocks, block_map, add_terminators, edges

def print_analysis(blk_map, in_, out_):
    for block in blk_map:
        print(block)
        print('\t', in_[block])
        print('\t', out_[block])
        print('\n')

def union(sets):
    out = set()
    
    for s in sets:
        out.update(s)
    
    return out

def worklist_algo(blocks, direction, init, transfer, merge):
    if direction:
        pre, suc = edges(blocks)
        entry_block = list(blocks.keys())[0]
    else:
        suc, pre = edges(blocks)
        entry_block = list(blocks.keys())[-1]

    in_ = {}
    out_ = {}

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
    
    if direction:
        return in_, out_
    else:
        return out_, in_

def rd(func):
    blk_map = block_map((form_blocks(func['instrs'])))
    add_terminators(blk_map)
    
    def rd_transfer(block, inv):
        outv = set()
        outv.update([ins['dest'] for ins in block if 'dest' in ins])
        outv.update(inv)

        return outv

    in_, out_ = worklist_algo(blk_map, True, set(), rd_transfer, union)
    
    print_analysis(blk_map, in_, out_)


def live(func):
    blk_map = block_map((form_blocks(func['instrs'])))
    add_terminators(blk_map)

    def live_transfer(block, inv):
        defined = set()
        used = set()

        for ins in block:
            used.update(arg for arg in ins.get('args', []) if arg not in defined)
            if 'dest' in ins:
                defined.add(ins['dest'])


        return used.union(inv - {ins['dest'] for ins in block if 'dest' in ins})    
    
    in_, out_ = worklist_algo(blk_map, False, set(), live_transfer, union)

    print_analysis(blk_map, in_, out_)


if __name__ == '__main__':
    prog = json.load(sys.stdin)

    if len(sys.argv) > 1:
        if sys.argv[1] == 'define':
            df = rd
        elif sys.argv[1] == 'live':
            df = live
    else:
        df = rd
 
    for func in prog['functions']:
        df(func)