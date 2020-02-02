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
            if isinstance(tokenized_line.getStructure()[action_index], DirectiveToken):
                action_index = 2
            # Handle instructions
            if isinstance(tokenized_line.getStructure()[action_index], InstructionToken):
                if tokenized_line.getStructure()[action_index].getText() in self._RRR:
                    object_line = object_line + self._RRR[tokenized_line.getStructure()[action_index].getText()]
                    object_line = object_line + self._registers[tokenized_line.getStructure()[action_index+2].getText()]
                    object_line = object_line + self._registers[tokenized_line.getStructure()[action_index+4].getText()]
                    object_line = object_line + self._registers[tokenized_line.getStructure()[action_index+6].getText()]
                    self.object_code.append(object_line)
                    continue
                if tokenized_line.getStructure()[action_index].getText() in self._RRI:
                    object_line = object_line + self._RRI[tokenized_line.getStructure()[action_index].getText()]
                    object_line = object_line + self._registers[tokenized_line.getStructure()[action_index+2].getText()]
                    object_line = object_line + self._registers[tokenized_line.getStructure()[action_index+4].getText()]
                    # Handle symbolic immediate
                    if tokenized_line.getStructure()[action_index+6].symbolic:
                        if tokenized_line.getStructure()[action_index+6].getText() in self.symbol_table:
                            # Check out of bounds
                            if self.symbol_table[tokenized_line.getStructure()[action_index+6].getText()] > 63:
                                raise SyntaxError('Target out of range in symbolic immediate token at [Source line: ' + str(tokenized_line.getStructure()[action_index+6].get_line_num())+ ']')
                            else:
                                object_line = object_line + self._s_7imm_to_bin(self.symbol_table[tokenized_line.getStructure()[action_index+6].getText()])
                                self.object_code.append(object_line)
                                continue
                        else:
                            raise SyntaxError('Undefined label in symbolic immediate token at [Source line: ' + str(tokenized_line.getStructure()[action_index+6].get_line_num())+ ']')
                    else:
                        
                        
    def _s_7imm_to_bin(self, s_int):
        # Via user Xiang, https://stackoverflow.com/a/34887286 
        return '{0:{fill}{width}b}'.format((s_int + 2**7) % 2**7, fill = '0', width = 7)
                
            
            