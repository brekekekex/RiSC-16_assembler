from lexer import *
from symbolizer import *

class Generator:
    _RRR = {'add': '000', 'nand': '010'}
    _RRI = {'addi': '001', 'sw': '101', 'lw': '100', 'beq': '110', 'jalr': '111'}
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
                    object_line = object_line + self._registers[tokenized_line.getStructure()[action_index+6].get_text()]
                    self.object_code.append(object_line)
                    continue
                if tokenized_line.getStructure()[action_index].get_text() in self._RRI:
                    object_line = object_line + self._RRI[tokenized_line.getStructure()[action_index].get_text()]
                    object_line = object_line + self._registers[tokenized_line.getStructure()[action_index+2].get_text()]
                    object_line = object_line + self._registers[tokenized_line.getStructure()[action_index+4].get_text()]
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
                    
        return self.object_code 
                        
    def _s_7imm_to_bin(self, s_int):
        # Via user Xiang, https://stackoverflow.com/a/34887286 
        return '{0:{fill}{width}b}'.format((s_int + 2**7) % 2**7, fill = '0', width = 7)
                
    def _u_10imm_to_bin(self, u_int):
        return '{0:{fill}{width}b}'.format(u_int, fill = '0', width = 10)
        
            