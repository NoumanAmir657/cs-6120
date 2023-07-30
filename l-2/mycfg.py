import json
import sys
from collections import OrderedDict

TERMINATORS = ['jmp', 'br', 'ret']

def form_blocks(body):
    blocks = []
    current_block = []
    
    for ins in body:
        if 'op' in ins:
            current_block.append(ins)

            if ins['op'] in TERMINATORS:
                blocks.append(current_block)
                current_block = []
        else:
            if current_block:
                blocks.append(current_block)
            
            current_block = [ins]

    if current_block:
        blocks.append(current_block)
        
    return blocks

def block_map(blocks):
    out = OrderedDict()

    for block in blocks:
        if 'label' in block[0]:
            name = block[0]['label']
            block = block[1:]
        else:
            name = 'b{}'.format(len(out))
        
        out[name] = block
    
    return out

def get_cfg(name2block):
    out = {}

    for i, (name, block) in enumerate(name2block.items()):
        last = block[-1]

        if last['op'] in ('jmp', 'br'):
            succ = last['labels']
        elif last['op'] == 'ret':
            succ = []
        else:
            if i == len(name2block) - 1:
                succ = []
            else:
                succ = [list(name2block.keys())[i + 1]]
        out[name] = succ
    
    return out

def mycfg():
    # prog = json.dumps(json.load(sys.stdin), indent = 2) # for pretty printing on the stdout
    prog = json.load(sys.stdin)
    
    for func in prog['functions']:
        name2block = block_map(form_blocks(func['instrs']))
        for name, block in name2block.items():
            print(name)
            print('     ', block)
        
        print('\n')

        cfg = get_cfg(name2block)
        print(cfg)

if __name__ == "__main__":
    mycfg()
