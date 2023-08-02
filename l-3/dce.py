import json
import sys
import itertools

sys.path.insert(0, '/home/nouman/Code/CS-6120/l-2')
from cfg import form_blocks


def simple_dead_code_elimination(func):
    # get basic blocks
    blocks = list(form_blocks(func['instrs']))

    # keeps track of whether any basic block got changed
    flag = True
    while flag:
        # keeps track of arguments
        used = set()

        # loop over blocks and add variables used as arguments to the set
        for block in blocks:
            for ins in block:
                used.update(ins.get('args', []))
        

        flag = False
        for block in blocks:
            # add instruction to new block if instruction does not have 'dest' attribute or if dest value is in used set 
            new_block = [ins for ins in block if 'dest' not in ins or ins['dest'] in used]
            if (len(new_block) != len(block)):
                flag = True

            block[:] = new_block

    func['instrs'] = list(itertools.chain(*blocks))

def removing_unused_assignments(block):
    # definitions not used in assignments
    flag = True

    while flag:
        def_to_insNum = {}
        delete_ins = set()

        for i, ins in enumerate(block):
            for arg in ins.get('args', []):
                if arg in def_to_insNum:
                    del def_to_insNum[arg]

            if 'dest' in ins:
                if ins['dest'] in def_to_insNum:
                    delete_ins.add(def_to_insNum[ins['dest']])
                def_to_insNum[ins['dest']] = i
        
        new_block = [ins for i, ins in enumerate(block) if 
                     i not in delete_ins]

        flag = False
        if (len(new_block) != len(block)):
            flag = True
        block[:] = new_block

def wrapper_rua(func):
    blocks = list(form_blocks(func['instrs']))
    for block in blocks:
        removing_unused_assignments(block)
    
    func['instrs'] = list(itertools.chain(*blocks))

def print_block(blocks):
    for block in blocks:
        for ins in block:
            print(ins)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if (sys.argv[1] == '-s'):
            opt = simple_dead_code_elimination
        elif (sys.argv[1] == '-l'):
            opt = wrapper_rua
        else:
            print('Wrong command-line argument')
            sys.exit()
    else:
        opt = simple_dead_code_elimination

    # read json from stdin
    prog = json.load(sys.stdin)

    for func in prog['functions']:
        opt(func)

    json.dump(prog, sys.stdout, indent=2, sort_keys=True)
