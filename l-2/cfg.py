import json
import sys
from collections import OrderedDict

TERMINATORS = ['jmp', 'br', 'ret']

def successors(instr):
    """Get the list of jump target labels for an instruction.

    Raises a ValueError if the instruction is not a terminator (jump,
    branch, or return).
    """
    if instr['op'] in ('jmp', 'br'):
        return instr['labels']
    elif instr['op'] == 'ret':
        return []  # No successors to an exit block.
    else:
        raise ValueError('{} is not a terminator'.format(instr['op']))

def edges(blocks):
    """Given a block map containing blocks complete with terminators,
    generate two mappings: predecessors and successors. Both map block
    names to lists of block names.
    """
    preds = {name: [] for name in blocks}
    succs = {name: [] for name in blocks}
    for name, block in blocks.items():
        for succ in successors(block[-1]):
            succs[name].append(succ)
            preds[succ].append(name)
    return preds, succs

def add_terminators(blocks):
    """Given an ordered block map, modify the blocks to add terminators
    to all blocks (avoiding "fall-through" control flow transfers).
    """
    for i, block in enumerate(blocks.values()):
        if not block:
            if i == len(blocks) - 1:
                # In the last block, return.
                block.append({'op': 'ret', 'args': []})
            else:
                dest = list(blocks.keys())[i + 1]
                block.append({'op': 'jmp', 'labels': [dest]})
        elif block[-1]['op'] not in TERMINATORS:
            if i == len(blocks) - 1:
                block.append({'op': 'ret', 'args': []})
            else:
                # Otherwise, jump to the next block.
                dest = list(blocks.keys())[i + 1]
                block.append({'op': 'jmp', 'labels': [dest]})

def form_blocks(body):    
    current_block = []
    
    for ins in body:
        if 'op' in ins:
            current_block.append(ins)

            if ins['op'] in TERMINATORS:
                yield current_block
                current_block = []
        else:
            if current_block:
                yield current_block
            
            current_block = [ins]

    if current_block:
        yield current_block

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

def cfg():
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
    cfg()
