DEFAULT_START_PROG_ADDR = 0
# Fixed-length instructions (one word)
DEFAULT_INSTR_SIZE = 1

class Assembler:
    # Store asm lines in tokenized form
    _asm_lines = []
    # Write machine code as binary strings
    _object_lines = []
    
    _location_counter = DEFAULT_START_PROG_ADDR
    
    # Labels and associated locations
    _symbol_table = {}
    
    # Handle opcodes
    _opcode_table = {'add': '000',
                     'addi': '001',
                     'nand': '010',
                     'lui': '011',
                     'sw': '101',
                     'lw': '100',
                     'beq': '110',
                     'jalr': '111'}
    
    # Handle register names
    _register_table = {'0': '000',
                       '1': '001',
                       '2': '010',
                       '3': '011',
                       '4': '100',
                       '5': '101',
                       '6': '110',
                       '7': '111'}
     
    def __init__(self, asm_source, verbose = 0):
        self.verbosity = verbose
        self.filename  = asm_source
        for line in open(self.filename, 'r'):
           # Remove blank and commented-out lines
           if line[0] == '#':
               continue
           elif line.isspace():
               continue
           self._asm_lines.append(self._parse_asm(line))
                
    def _parse_asm(self, line):
        tokens = {}
        # Remove leading and trailing whitespace
        parsed_line = line.strip()
        # Remove trailing comments
        parsed_line = parsed_line.split('#', 1)[0]
        # Replace tabs with spaces
        parsed_line = parsed_line.replace('\t', ' ')
        #parsed_line = parsed_line.replace('    ', ' ')
        parsed_line = parsed_line.replace('     ', ' ')
        # Add terminating space
        parsed_line = parsed_line + ' '
        # Handle labels
        if ':' in parsed_line:
            tokens['label_name'] = parsed_line.split(':', 1)[0]
            # Remove label
            parsed_line = parsed_line.split(':', 1)[1]
        else: # no label, add leading space (safety)
            parsed_line = ' ' + parsed_line
        # Handle directives
        if((' nop ' in parsed_line) or 
            (' halt ' in parsed_line) or 
            (' lli ' in parsed_line) or 
            (' movi ' in parsed_line) or 
            (' .fill ' in parsed_line) or
            (' .space ' in parsed_line)
            ):
            tokens['directive'] = parsed_line.split(' ', 2)[1]
            # Remove directive
            parsed_line = parsed_line.split(' ', 2)[2]
            # Handle directive arguments 
            if tokens['directive'] == 'nop' or tokens['directive'] == 'halt':
                return tokens
            elif tokens['directive'] == 'lli' or tokens['directive'] == 'movi':
                tokens['directive_arg1'] = parsed_line.split(',')[0].strip()
                tokens['directive_arg2'] = parsed_line.split(',')[1].strip()
                return tokens    
            elif tokens['directive'] == '.fill' or tokens['directive'] == '.space':
                tokens['directive_arg1'] = parsed_line.strip()
                return tokens
        # Handle instructions
        else:
            tokens['opcode'] = parsed_line.split(' ', 2)[1]
            # Remove opcode
            parsed_line = parsed_line.split(' ', 2)[2]
            tokens['opcode_arg1'] = parsed_line.split(',')[0].strip()
            tokens['opcode_arg2'] = parsed_line.split(',')[1].strip()
            # Handle RI instruction (only two arguments)
            if tokens['opcode'] == 'lui':
                return tokens
            # Handle RRI and RRR instructions (three arguments)
            else:
                # jalr is technically a three-argument instruction but last immediate is hidden
                if tokens['opcode'] == 'jalr':
                    return tokens
                tokens['opcode_arg3'] = parsed_line.split(',')[2].strip()
                return tokens
    
    def _symbolize(self):
        for line in self._asm_lines:
            # Add symbol (label) and instruction location to symbol table
            if 'label_name' in line:
                self._symbol_table[line['label_name']] = self._location_counter
            # Handle directives
            if 'directive' in line:
                if line['directive'] == 'movi':
                    self._location_counter += 2*DEFAULT_INSTR_SIZE
                    continue
                elif line['directive'] == '.space':
                    self._location_counter += (line['directive_arg1'])*DEFAULT_INSTR_SIZE
                    continue
            self._location_counter += DEFAULT_INSTR_SIZE
    
    def _s_7imm_to_bin(self, s_int):
        # Via user Xiang, https://stackoverflow.com/a/34887286 
        return '{0:{fill}{width}b}'.format((s_int + 2**7) % 2**7, fill = '0', width = 7)
   
    def _generate(self):
        for line in self._asm_lines:
            # Handle directives
            if 'directive' in line:
                if line['directive'] == 'nop':
                    self._object_lines.append(self._opcode_table['add'] + '0000000000000')
                    continue
                elif line['directive'] == 'halt':
                    self._object_lines.append(self._opcode_table['jalr'] + '000000' + self._s_7imm_to_bin(1))
                    continue
                elif line['directive'] == '.fill':
                    # Handle if .fill argument is label
                    if line['directive_arg1'] in self._symbol_table:
                        # Via user Xiang, https://stackoverflow.com/a/34887286 
                        self._object_lines.append("{0:{fill}16b}".format(self._symbol_table[line['directive_arg1']], fill='0'))
                    else:
                        self._object_lines.append('{0:{fill}{width}b}'.format((int(line['directive_arg1']) + 2**16) % 2**16, fill = '0', width = 16))
                    continue
                elif line['directive'] == '.space':
                    # .fill 0 n-times
                    for i in range(line['directive_arg1']):
                        self._object_lines.append("{0:{fill}16b}".format(0, fill='0'))
                    continue
                elif line['directive'] == 'lli':
                    self._object_lines.append(self._opcode_table['addi'] + 
                                              2*self._register_table[line['directive_arg1'].replace('r','')] +
                                              '0'+ '{0:{fill}6b}'.format((int(line['directive_arg2'], 2) & 63), fill='0')
                                              )
                    continue
                elif line['directive'] == 'movi':
                    if line['directive_arg2'] in self._symbol_table:
                        #p#rint(int(self._symbol_table[line['directive_arg2']])
                        self._object_lines.append(self._opcode_table['lui'] +
                                              self._register_table[line['directive_arg1'].replace('r','')] +
                                              '{0:{fill}10b}'.format(self._symbol_table[line['directive_arg2']], fill='0')
                                              )
                        self._object_lines.append(self._opcode_table['addi'] + 
                                              2*self._register_table[line['directive_arg1'].replace('r','')] +
                                              '0'+ '{0:{fill}6b}'.format((self._symbol_table[line['directive_arg2']]) & 63, fill='0')
                                              )
                        continue
                    else:
                        self._object_lines.append(self._opcode_table['lui'] +
                                                  self._register_table[line['directive_arg1'].replace('r','')] +
                                                  '{0:{fill}10b}'.format((int(line['directive_arg2'], 2)), fill='0')
                                                  )
                        self._object_lines.append(self._opcode_table['addi'] + 
                                                  2*self._register_table[line['directive_arg1'].replace('r','')] +
                                                  '0'+ '{0:{fill}6b}'.format((int(line['directive_arg2'], 2) & 63), fill='0')
                                                  )
                        continue
                
            # Handle RRR-type
            elif line['opcode'] == 'and' or line['opcode'] == 'nand':
                self._object_lines.append(self._opcode_table[line['opcode']] + 
                                          self._register_table[line['opcode_arg1'].replace('r','')] +
                                          self._register_table[line['opcode_arg2'].replace('r','')] +
                                          4*'0' +
                                          self._register_table[line['opcode_arg3'].replace('r','')])
                continue
            # Handle RRI-type
            elif((line['opcode'] == 'addi') or
                (line['opcode'] == 'sw') or
                (line['opcode'] == 'lw') or
                (line['opcode'] == 'beq') or
                (line['opcode'] == 'jalr')
                ):
                if line['opcode'] == 'jalr':
                    self._object_lines.append(self._opcode_table[line['opcode']] +
                                              self._register_table[line['opcode_arg1'].replace('r','')] +
                                              self._register_table[line['opcode_arg2'].replace('r','')] +
                                              7*'0'
                                              )
                    continue
                if line['opcode_arg3'] in self._symbol_table:
                    self._object_lines.append(self._opcode_table[line['opcode']] + 
                                              self._register_table[line['opcode_arg1'].replace('r','')] +
                                              self._register_table[line['opcode_arg2'].replace('r','')] +
                                              "{0:{fill}7b}".format(self._symbol_table[line['opcode_arg3']], fill='0')
                                              )
                    continue
                else:
                    self._object_lines.append(self._opcode_table[line['opcode']] + 
                                              self._register_table[line['opcode_arg1'].replace('r','')] +
                                              self._register_table[line['opcode_arg2'].replace('r','')] +
                                              self._s_7imm_to_bin(int(line['opcode_arg3']))
                                              )
                    continue
            # Handle RI-type
            elif line['opcode'] == 'lui':
                if line['opcode_arg2'] in self._symbol_table:
                    self._object_lines.append(self._opcode_table[line['opcode']]+
                                              self._register_table[line['opcode_arg1'].replace('r','')] +
                                              "{0:{fill}10b}".format(self._symbol_table[line['opcode_arg2']], fill='0')
                                              )
                    continue
                else:
                    self._object_lines.append(self._opcode_table[line['opcode']]+
                                              self._register_table[line['opcode_arg1'].replace('r','')] +
                                              "{0:{fill}10b}".format(int(line['opcode_arg2']), fill='0')
                                              )
                    continue
            
    def assemble(self):
        if self.verbosity:
            print('parsing assembly...')
            for line_num, line in enumerate(self._asm_lines):
                print('P: ' + str(line_num) + '\t'+ str(line))
            print('\ngenerating symbol table...')
            self._symbolize()
            print(self._symbol_table)
            print('\ngenerating machine code...')
            self._generate()
            for line_num, line in enumerate(self._object_lines):
                print('M: ' + str(line_num) + '\t'+ '0x{0:0{1}X}'.format(int(line, 2),4) + '\t' + '0b' + line)
            print('\nexiting...')
        else:
            print('parsing assembly...')
            print('\ngenerating symbol table...')
            self._symbolize()
            print('\ngenerating machine code...')
            self._generate()
            print('\nexiting...')
        with open(self.filename[:-4]+'.o', 'w') as f:
            for line in self._object_lines:
                f.write('0x{0:0{1}X}'.format(int(line, 2), 4)+'\n')
        return
    
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('--verbose', required = False, action='store_true')
    argument = parser.parse_args()
    
    if argument.verbose:
        assembler = Assembler(argument.filename, argument.verbose)
    else:
        assembler = Assembler(argument.filename)
    assembler.assemble()
    
    