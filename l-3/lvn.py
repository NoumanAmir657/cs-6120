import json
import sys
from collections import OrderedDict
import itertools

sys.path.insert(0, '/home/nouman/Code/CS-6120/l-2')
from mycfg import form_blocks

def print_block(blocks):
    for block in blocks:
        for ins in block:
            print(ins)

def change_block_main(func):
    blocks = list(form_blocks(func['instrs']))
    newVar = {}
    cnt = 0
    
    for block in blocks:
        for ins in block:
            if 'args' in ins:
                for i, arg in enumerate(ins['args']):
                    ins['args'][i] = newVar[ins['args'][i]]
            if 'dest' in ins:
                newName = 'v' + str(cnt)
                newVar[ins['dest']] = newName
                ins['dest'] = newName
                cnt += 1
    func['instrs'] = list(itertools.chain(*blocks))

def change_block(blocks):
    newVar = {}
    cnt = 0
    
    for block in blocks:
        for ins in block:
            if 'args' in ins:
                for i, arg in enumerate(ins['args']):
                    ins['args'][i] = newVar[ins['args'][i]]
            if 'dest' in ins:
                newName = 'v' + str(cnt)
                newVar[ins['dest']] = newName
                ins['dest'] = newName
                cnt += 1
    
def lvn(func):
    blocks = list(form_blocks(func['instrs']))

    change_block(blocks)
    
    BINARY = ['add', 'sub', 'mul', 'div', 'eq', 'lt', 'gt', 'le', 'ge']
    table = OrderedDict()
    var2num = {}
    num = -1

    for block in blocks:
        for ins in block:            
            # assuming op will always be in the instruction i.e no labels since local optimization
            op = ins.get('op')

            if op == 'const':
                value = (op, ins.get('value'))
            elif op in BINARY:
                value = (op, var2num.get(ins.get('args')[0]), var2num.get(ins.get('args')[1]))
            elif op == 'print' or op == 'id':
                value = (op, var2num.get(ins.get('args')[0]))

            if value in table:
                if op == 'const':
                    var2num[ins.get('dest')] = var2num[table[value]]
                    
                    # instruction change
                    ins['op'] = 'id'
                    ins['args'] = [table[value]]
                    del ins['value']
    
                elif op in BINARY:
                    var2num[ins.get('dest')] = var2num[table[value]]
                    
                    # instruction change
                    ins['op'] = 'id'
                    ins['args'] = [table[value]]

                elif op == 'print':
                    # instruction change
                    ins['args'][0] = list(table.items())[value[1]][1]

                elif op == 'id':
                    #instruction change
                    var2num[ins.get('dest')] = var2num[table[value]]
                    ins['args'][0] = table[value]
                    
            else:
                num += 1

                if op in BINARY or op == 'const' or op == 'id':
                    dest = ins.get('dest')

                    if op == 'id':
                        table[value] = ins.get('args')[0]
                        var2num[dest] = var2num[ins.get('args')[0]]
                    else:
                        table[value] = dest
                        var2num[dest] = num

                    # instruction change
                    for i, arg in enumerate(ins.get('args', [])):
                        ins.get('args')[i] = list(table.items())[var2num.get(arg)][1]
                elif op == 'print':
                    table[value] = None
                    ins['args'][0] = list(table.items())[value[1]][1]


    func['instrs'] = list(itertools.chain(*blocks))

if __name__ == '__main__':
    # read json from stdin
    prog = json.load(sys.stdin)

    if sys.argv[1] == '-c':
        for func in prog['functions']:
            change_block_main(func)

    elif sys.argv[1] == '-l':
        for func in prog['functions']:
            lvn(func)

    json.dump(prog, sys.stdout, indent=2, sort_keys=True)