from lexer import *
from symbolizer import *

class Generator:
    _RRR = {'add': '000', 'nand': '010'}
    _RRI = {'addi': '001', 'sw': '100', 'lw': '101', 'beq': '110', 'jalr': '111'}
    _RI = {'lui': '011'}
    
    _registers = {'0': '000', '1': '001', '2': '010', '3': '011', '4': '100', '5': '101', '6': '110', '7': '111'}
    
    def __init__(self, tokenized_file, symbol_table):
        self.tokenized_file = tokenized_file
        self.symbol_table = symbol_table
    
    def Generate(self):
        self.object_code = []
        for tokenized_line in self.tokenized_file:
            object_line = ''
            action_index = 0
            if isinstance(tokenized_line.getStructure()[action_index], LabelToken):
                action_index = action_index + 2
            # Handle instructions
            if isinstance(tokenized_line.getStructure()[action_index], InstructionToken):
                if tokenized_line.getStructure()[action_index].get_text() in self._RRR:
                    object_line = object_line + self._RRR[tokenized_line.getStructure()[action_index].get_text()]
                    object_line = object_line + self._registers[tokenized_line.getStructure()[action_index+2].get_text()]
                    object_line = object_line + self._registers[tokenized_line.getStructure()[action_index+4].get_text()]
                    object_line = object_line + '0000' + self._registers[tokenized_line.getStructure()[action_index+6].get_text()]
                    self.object_code.append(object_line)
                    continue
                if tokenized_line.getStructure()[action_index].get_text() in self._RRI:
                    object_line = object_line + self._RRI[tokenized_line.getStructure()[action_index].get_text()]
                    object_line = object_line + self._registers[tokenized_line.getStructure()[action_index+2].get_text()]
                    object_line = object_line + self._registers[tokenized_line.getStructure()[action_index+4].get_text()]
                    # beq symbolic check
                    if tokenized_line.getStructure()[action_index+6].symbolic and tokenized_line.getStructure()[action_index].get_text() == 'beq':
                        if tokenized_line.getStructure()[action_index+6].get_text() in self.symbol_table:
                            object_line = object_line + self._s_7imm_to_bin(self.symbol_table[tokenized_line.getStructure()[action_index+6].get_text()]-1-len(self.object_code))
                            self.object_code.append(object_line)
                            continue
                        else:
                            raise SyntaxError('Undefined label in symbolic immediate token at [Source line: ' + str(tokenized_line.getStructure()[action_index+6].get_line_num())+ ']')
                    
                    
                    
                    
                    # jalr check
                    if tokenized_line.getStructure()[action_index].get_text() == 'jalr' and action_index+6 > len(tokenized_line.getStructure()):
                        object_line = object_line + '0000000'
                        self.object_code.append(object_line)
                        continue
                    # Handle symbolic immediate
                    if tokenized_line.getStructure()[action_index+6].symbolic:
                        if tokenized_line.getStructure()[action_index+6].get_text() in self.symbol_table:
                            object_line = object_line + self._s_7imm_to_bin(self.symbol_table[tokenized_line.getStructure()[action_index+6].get_text()])
                            self.object_code.append(object_line)
                            continue
                        else:
                            raise SyntaxError('Undefined label in symbolic immediate token at [Source line: ' + str(tokenized_line.getStructure()[action_index+6].get_line_num())+ ']')
                    else:
                        object_line = object_line + self._s_7imm_to_bin(int(tokenized_line.getStructure()[action_index+6].get_text()))
                        self.object_code.append(object_line)
                        continue
                if tokenized_line.getStructure()[action_index].get_text() in self._RI:
                    object_line = object_line + self._RI[tokenized_line.getStructure()[action_index].get_text()]
                    object_line = object_line + self._registers[tokenized_line.getStructure()[action_index+2].get_text()]
                    # Handle symbolic immediate
                    if tokenized_line.getStructure()[action_index+4].symbolic:
                        if tokenized_line.getStructure()[action_index+4].get_text() in self.symbol_table:
                            object_line = object_line + self._u_10imm_to_bin(self.symbol_table[tokenized_line.getStructure()[action_index+4].get_text()])
                            self.object_code.append(object_line)
                            continue
                        else:
                            raise SyntaxError('Undefined label in symbolic immediate token at [Source line: ' + str(tokenized_line.getStructure()[action_index+4].get_line_num())+ ']')
                    else:
                        object_line = object_line + self._u_10imm_to_bin(int(tokenized_line.getStructure()[action_index+4].get_text()))
                        self.object_code.append(object_line)
                        continue
            if isinstance(tokenized_line.getStructure()[action_index], DirectiveToken):
                if tokenized_line.getStructure()[action_index].get_text() == 'nop':
                    object_line = '0'*16
                    self.object_code.append(object_line)
                    continue
                if tokenized_line.getStructure()[action_index].get_text() == 'halt':
                    # non zero jalr immediate
                    object_line = '111' + '000' + '000' + '1110001'
                    self.object_code.append(object_line)
                    continue
                if tokenized_line.getStructure()[action_index].get_text() == '.fill':
                    # Handle symbolic immediate
                    if tokenized_line.getStructure()[action_index+2].symbolic:
                        if tokenized_line.getStructure()[action_index+2].get_text() in self.symbol_table:
                            object_line = self._u_16imm_to_bin(self.symbol_table[tokenized_line.getStructure()[action_index+2].get_text()])
                            self.object_code.append(object_line)
                            continue
                        else:
                            raise SyntaxError('Undefined label in symbolic immediate token at [Source line: ' + str(tokenized_line.getStructure()[action_index+2].get_line_num())+ ']')
                    else:
                        if int(tokenized_line.getStructure()[action_index+2].get_text()) > (2**15-1) or int(tokenized_line.getStructure()[action_index+2].get_text()) < (-2**15):
                            raise ValueError('Invalid value found in signed immediate token at [Source line: ' + str(tokenized_line.getStructure()[action_index+2].get_line_num())+ ']')
                        object_line = self._s_16imm_to_bin(int(tokenized_line.getStructure()[action_index+2].get_text()))
                        self.object_code.append(object_line)
                        continue
                if tokenized_line.getStructure()[action_index].get_text() == '.space':
                    for i in range(int(tokenized_line.getStructure()[action_index+2].get_text())):
                        self.object_code.append('0'*16)
                    continue
                if tokenized_line.getStructure()[action_index].get_text() == 'lli':
                    object_line = object_line + self._RRI['addi']
                    object_line = object_line + self._registers[tokenized_line.getStructure()[action_index+2].get_text()]*2
                    # Handle symbolic immediate
                    if tokenized_line.getStructure()[action_index+4].symbolic:
                        if tokenized_line.getStructure()[action_index+4].get_text() in self.symbol_table:
                            object_line = object_line + '0' + self._s_7imm_to_bin(self.symbol_table[tokenized_line.getStructure()[action_index+4].get_text()] & 63)[-6:]
                            self.object_code.append(object_line)
                            continue
                        else:
                            raise SyntaxError('Undefined label in symbolic immediate token at [Source line: ' + str(tokenized_line.getStructure()[action_index+4].get_line_num())+ ']')
                    else:
                        object_line = object_line + '0' + self._s_7imm_to_bin(int(tokenized_line.getStructure()[action_index+4].get_text()) & 63)
                        self.object_code.append(object_line)
                        continue
                if tokenized_line.getStructure()[action_index].get_text() == 'movi':
                    object_line = object_line + self._RI['lui']
                    object_line = object_line + self._registers[tokenized_line.getStructure()[action_index+2].get_text()]
                    # Handle symbolic immediate
                    if tokenized_line.getStructure()[action_index+4].symbolic:
                        if tokenized_line.getStructure()[action_index+4].get_text() in self.symbol_table:
                            object_line = object_line + self._u_10imm_to_bin(self.symbol_table[tokenized_line.getStructure()[action_index+4].get_text()])
                            self.object_code.append(object_line)
                            object_line = ''
                            object_line = object_line + self._RRI['addi']
                            object_line = object_line + self._registers[tokenized_line.getStructure()[action_index+2].get_text()]*2
                            # Handle symbolic immediate
                            if tokenized_line.getStructure()[action_index+4].symbolic:
                                if tokenized_line.getStructure()[action_index+4].get_text() in self.symbol_table:
                                    object_line = object_line + '0' + self._s_7imm_to_bin(self.symbol_table[tokenized_line.getStructure()[action_index+4].get_text()] & 63)[-6:]
                                    self.object_code.append(object_line)
                                    continue
                                else:
                                    raise SyntaxError('Undefined label in symbolic immediate token at [Source line: ' + str(tokenized_line.getStructure()[action_index+4].get_line_num())+ ']')
                            else:
                                object_line = object_line + '0' + self._s_7imm_to_bin(int(tokenized_line.getStructure()[action_index+4].get_text()) & 63)
                                self.object_code.append(object_line)
                                continue
                        else:
                            raise SyntaxError('Undefined label in symbolic immediate token at [Source line: ' + str(tokenized_line.getStructure()[action_index+4].get_line_num())+ ']')
                    else:
                        object_line = object_line + self._u_10imm_to_bin(int(tokenized_line.getStructure()[action_index+4].get_text()))
                        self.object_code.append(object_line)
                        object_line = ''
                            
                        object_line = object_line + self._RRI['addi']
                        object_line = object_line + self._registers[tokenized_line.getStructure()[action_index+2].get_text()]*2
                        # Handle symbolic immediate
                        if tokenized_line.getStructure()[action_index+4].symbolic:
                            if tokenized_line.getStructure()[action_index+4].get_text() in self.symbol_table:
                                object_line = object_line + '0' + self._s_7imm_to_bin(self.symbol_table[tokenized_line.getStructure()[action_index+4].get_text()] & 63)[-6:]
                                self.object_code.append(object_line)
                                continue
                            else:
                                raise SyntaxError('Undefined label in symbolic immediate token at [Source line: ' + str(tokenized_line.getStructure()[action_index+4].get_line_num())+ ']')
                        else:
                            object_line = object_line + '0' + self._s_7imm_to_bin(int(tokenized_line.getStructure()[action_index+4].get_text()) & 63)
                            self.object_code.append(object_line)
                            continue
                        
        return self.object_code 
                        
    def _s_7imm_to_bin(self, s_int):
        # Via user Xiang, https://stackoverflow.com/a/34887286 
        return '{0:{fill}{width}b}'.format((s_int + 2**7) % 2**7, fill = '0', width = 7)
                
    def _u_10imm_to_bin(self, u_int):
        return '{0:{fill}{width}b}'.format(u_int, fill = '0', width = 10)
        
    def _u_16imm_to_bin(self, u_int):
        return '{0:{fill}{width}b}'.format(u_int, fill = '0', width = 16)
        
    def _s_16imm_to_bin(self, s_int):
        # Via user Xiang, https://stackoverflow.com/a/34887286 
        return '{0:{fill}{width}b}'.format((s_int + 2**16) % 2**16, fill = '0', width = 16)
            