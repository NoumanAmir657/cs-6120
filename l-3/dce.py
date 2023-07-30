import json
import sys

sys.path.insert(0, '/home/nouman/Code/CS-6120/l-2')

from mycfg import form_blocks


def simple_dead_code_elimination(blocks):
    flag = True
    while flag:
        used = set()

        for block in blocks:
            for ins in block:
                used.update(ins.get('args', []))
        
        flag = False
        for block in blocks:
            new_block = [ins for ins in block if 'dest' not in ins or ins['dest'] in used]
            if (len(new_block) != len(block)):
                flag = True

            block[:] = new_block

    return blocks

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
        
        new_block = [ins for i, ins in enumerate(block) if i not in delete_ins]

        flag = False
        if (len(new_block) != len(block)):
            flag = True
        block[:] = new_block

def wrapper_rua(blocks):
    for block in blocks:
        removing_unused_assignments(block)

def print_block(block):
    for block in blocks:
        for ins in block:
            print(ins)

if __name__ == '__main__':
    prog = json.load(sys.stdin)

    blocks = []
    for func in prog['functions']:
        blocks = form_blocks(func['instrs'])

    print('Before opt')
    print_block(blocks)

    if len(sys.argv) > 1:
        if (sys.argv[1] == 'simple'):
            simple_dead_code_elimination(blocks)
        elif (sys.argv[1] == 'local'):
            wrapper_rua(blocks)
        else:
            print('Wrong command-line argument')
            sys.exit()
    else:
        simple_dead_code_elimination(blocks)

    print('After opt')
    print_block(blocks)