from lexer import *

DEFAULT_PROGRAM_START_ADDRESS = 0



class Symbolizer:
    def __init__(self, tokenizedFile):
        self.currentAddress = 0
        self.symbol_table = {}
        
        for tokenizedLine in tokenizedFile:
            if isinstance(tokenizedLine.getStructure()[0], LabelToken):
                self.symbol_table[tokenizedLine.getStructure()[0].get_text()] = self.currentAddress
            