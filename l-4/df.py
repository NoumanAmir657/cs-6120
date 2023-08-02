import sys
sys.path.insert(0, '../l-2')
import json

from cfg import form_blocks

def print_blocks(blocks):
    for block in blocks:
        for ins in block:
            print(ins)

def rd(func):
    blocks = list(form_blocks(func['instrs']))

    print_blocks(blocks)


if __name__ == '__main__':
    prog = json.load(sys.stdin)

    for func in prog['functions']:
        rd(func)
