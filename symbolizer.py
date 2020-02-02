from lexer import *

DEFAULT_PROGRAM_START_ADDRESS = 0
DEFAULT_INSTRUCTION_SIZE = 1

class Symbolizer:
    def __init__(self, tokenizedFile):
        self.tokenizedFile = tokenizedFile
        self.currentAddress = 0
        self.symbol_table = {}
        
        
    def Symbolize(self):
        for tokenizedLine in self.tokenizedFile:
            if isinstance(tokenizedLine.getStructure()[0], LabelToken):
                self.symbol_table[tokenizedLine.getStructure()[0].get_text()] = self.currentAddress
            if tokenizedLine.containsDirective() != -1:
                if tokenizedLine.getStructure()[tokenizedLine.containsDirective()].get_text() == 'movi':
                    self.currentAddress += 2*DEFAULT_INSTRUCTION_SIZE
                elif tokenizedLine.getStructure()[tokenizedLine.containsDirective()].get_text() == '.space':
                    self.currentAddress += int(tokenizedLine.getStructure()[tokenizedLine.containsDirective() + 2].get_text())*DEFAULT_INSTRUCTION_SIZE 
                else:
                    self.currentAddress += 1*DEFAULT_INSTRUCTION_SIZE
            else:
                self.currentAddress += 1*DEFAULT_INSTRUCTION_SIZE
        
        return self.symbol_table