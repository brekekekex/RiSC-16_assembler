from lexer import *
from symbolizer import *
from generator import *

class Assembler:
    def __init__(self, source_filepath, verbose_lexer = False, verbose_symbolizer = False, verbose_generator = True, writeBin = False):
        self.source_filepath = source_filepath
        self.target_filepath = source_filepath.split('.asm')[0] + '.o'
        self.verbose_lexer = verbose_lexer
        self.verbose_symbolizer = verbose_symbolizer
        self.verbose_generator = verbose_generator
        self.writeBin = writeBin
        
    def assemble(self):
        myLexer = Lexer(self.source_filepath)
        print('\nTokenizing assembly file...')
        self.tokenized_file = myLexer.Lex()
        if self.verbose_lexer:
            print('\nDumping tokenized file...')
            for line_num, line in enumerate(self.tokenized_file):
                print('[Source Line: ' + str(line_num) + ']')
                print(line)
        mySymbolizer = Symbolizer(self.tokenized_file)
        print('\nSymbolizing assembly file...')
        self.symbol_table = mySymbolizer.Symbolize()
        if self.verbose_symbolizer:
            print('\nDumping symbol table...')
            print(self.symbol_table)
        myGenerator = Generator(self.tokenized_file, self.symbol_table)
        print('\nGenerating object file...')
        self.object_code = myGenerator.Generate()
        if self.verbose_generator:
            print('\nDumping generated code...')
            print('\n[PC]\t[Instruction]')
            for pc, line in enumerate(self.object_code):
                if self.writeBin:
                    print('0x{0:0{1}X}'.format(pc,4)[2:])
                else: 
                    print('0x{0:0{1}X}'.format(pc,4)[2:] + '\t' + '0x{0:0{1}X}'.format(int(line,2),4)[2:])        
        print('\nWriting to ' + self.target_filepath + '...\n')
        f = open(self.target_filepath, "w")
        for line in self.object_code:
            if self.writeBin:
                f.write(line + '\n')
            else: 
                f.write('0x{0:0{1}X}'.format(int(line,2),4)[2:] + '\n')
        f.close()
        
    
        
        
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('--vl', required = False, action='store_true', help='verbose lexer--show tokenization')
    parser.add_argument('--vs', required = False, action='store_true', help='verbose symoblizer--show symbol table')
    parser.add_argument('--novg', required = False, action='store_false', help='no verbose generator--do not output object code to console (will still write to file)')
    parser.add_argument('--bin', required = False, action='store_true', help='write to target file in binary')
    argument = parser.parse_args()

    myAssembler = Assembler(argument.filename, argument.vl, argument.vs, argument.novg, argument.bin)
    myAssembler.assemble()
    
