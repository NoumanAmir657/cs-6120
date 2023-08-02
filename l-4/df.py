import sys
sys.path.insert(0, '../l-2')

import json

from cfg import form_blocks, block_map, add_terminators

def print_blocks(blocks):
    for block in blocks:
        for ins in block:
            print(ins)


def rd(func):
    blk_map = block_map((form_blocks(func['instrs'])))
    add_terminators(blk_map)

    for name, block in blk_map.items():
        print(name)
        print('     ', block)


if __name__ == '__main__':
    prog = json.load(sys.stdin)

    for func in prog['functions']:
        rd(func)