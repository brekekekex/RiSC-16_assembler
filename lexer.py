
class Lexer:
    def __init__(self, source_filepath):
        self.source_filepath = source_filepath
    
    def Lex(self):
        self.tokenized_file = []
        for line_num, source_line in enumerate(open(self.source_filepath, 'r')):
            if source_line[0] == '#' or source_line.isspace():
                continue
            else:
                self.tokenized_file.append(self._Tokenize(source_line.split('#')[0].strip(), line_num))
        return self.tokenized_file
        
    def _Tokenize(self, source_line, source_line_num):
        directive_table = {'nop', 'halt', 'lli', 'movi', '.fill', '.space'}
        instruction_table = {'add', 'addi', 'nand', 'lui', 'sw', 'lw', 'beq', 'jalr'}
        
        tokenized_line = TokenizedLine()
        # Pad with whitespace tokens
        line = ' ' + source_line + ' '
        # Compress whitespace
        while '  ' in line or '\t' in line or ',' in line:
            if '\t ' in line or ' \t' in line:
                print('WARNING: Mixed tabs and spaces found at [Source line: ' + str(source_line_num) + ']')
            if ',,' in line:
                print('WARNING: Repeated comma delimiter found at [Source line: ' + str(source_line_num) + ']')
            line = line.replace(',', ' ')
            line = line.replace('\t', ' ')
            line = line.replace('  ', ' ')
        # Identify whitespace and text tokens
        for string in line.split(' ')[1:-1]:
            tokenized_line.appendToken(WhitespaceToken(source_line_num))
            tokenized_line.appendToken(TextToken(source_line_num, string))
        # Remove whitespace front padding
        tokenized_line.removeToken(0)
        # Identify label token
        label_flag = False
        for ID, Token in enumerate(tokenized_line.getStructure()):
            if isinstance(Token, TextToken):
                if ':' in Token.get_text():
                    if label_flag:
                        raise SyntaxError('Multiple label tokens found at [Source line: ' + str(source_line_num) + ']')
                    label_flag = True
                    tokenized_line.replaceTokenwith(ID, LabelToken(source_line_num, Token.get_text().split(':')[0]))
        # Grammar check condition on label
        if label_flag:
            texttoken_flag = False
            for Token in tokenized_line.getStructure()[1:]:
                if isinstance(Token, TextToken):
                    texttoken_flag = True
                    break
            if not texttoken_flag:
                raise SyntaxError('Lone label found at [Source line: ' + str(source_line_num) + ']')
        # Identify directive token
        directive_flag = False
        directive_pos = 0
        for ID, Token in enumerate(tokenized_line.getStructure()):
            if isinstance(Token, TextToken):
                if Token.get_text() in directive_table:
                    if directive_flag:
                        raise SyntaxError('Multiple directive tokens found at [Source line: ' + str(source_line_num) + ']')
                    directive_flag = True
                    tokenized_line.replaceTokenwith(ID, DirectiveToken(source_line_num, Token.get_text()))
                    directive_pos = ID
        # Grammar check condition on directive
        if directive_flag:
            directive_args = 0
            for Token in tokenized_line.getStructure()[directive_pos+1:]:
                if isinstance(Token, TextToken):
                    directive_args += 1     
            if (tokenized_line.getStructure()[directive_pos].get_text() == 'nop' or 
                tokenized_line.getStructure()[directive_pos].get_text() == 'halt') and directive_args != 0:
                raise SyntaxError(tokenized_line.getStructure()[directive_pos].get_text() + 
                                  ' directive expects 0 arguments; ' + str(directive_args) + 
                                  ' given at [Source line: ' + str(source_line_num) + ']')
            elif (tokenized_line.getStructure()[directive_pos].get_text() == '.fill' or 
                  tokenized_line.getStructure()[directive_pos].get_text() == '.space') and directive_args != 1:
                raise SyntaxError(tokenized_line.getStructure()[directive_pos].get_text() + 
                                  ' directive expects 1 argument; ' + str(directive_args) + 
                                  ' given at [Source line: ' + str(source_line_num) + ']')
            elif (tokenized_line.getStructure()[directive_pos].get_text() == 'lli' or 
                  tokenized_line.getStructure()[directive_pos].get_text() == 'movi') and directive_args != 2:
                raise SyntaxError(tokenized_line.getStructure()[directive_pos].get_text() + 
                                  ' directive expects 2 arguments; ' + str(directive_args) + 
                                  ' given at [Source line: ' + str(source_line_num) + ']')
        # Identify instruction token
        instruction_flag = False
        instruction_pos = 0
        for ID, Token in enumerate(tokenized_line.getStructure()):
            if isinstance(Token, TextToken):
                if Token.get_text() in instruction_table:
                    if instruction_flag:
                        raise SyntaxError('Multiple instruction tokens found at [Source line: ' + str(source_line_num) + ']')
                    instruction_flag = True
                    tokenized_line.replaceTokenwith(ID, InstructionToken(source_line_num, Token.get_text()))
                    instruction_pos = ID
        # Grammar check condition on instruction
        if instruction_flag:
            instruction_args = 0
            for Token in tokenized_line.getStructure()[instruction_pos+1:]:
                if isinstance(Token, TextToken):
                    instruction_args += 1    
            if (tokenized_line.getStructure()[instruction_pos].get_text() == 'add' or 
                tokenized_line.getStructure()[instruction_pos].get_text() == 'addi' or
                tokenized_line.getStructure()[instruction_pos].get_text() == 'nand' or
                tokenized_line.getStructure()[instruction_pos].get_text() == 'sw' or
                tokenized_line.getStructure()[instruction_pos].get_text() == 'lw' or
                tokenized_line.getStructure()[instruction_pos].get_text() == 'beq') and instruction_args != 3:
                raise SyntaxError(tokenized_line.getStructure()[instruction_pos].get_text() + 
                                  ' instruction expects 3 arguments; ' + str(instruction_args) + 
                                  ' given at [Source line: ' + str(source_line_num) + ']')
            elif tokenized_line.getStructure()[instruction_pos].get_text() == 'lui' and instruction_args != 2:
                raise SyntaxError(tokenized_line.getStructure()[instruction_pos].get_text() + 
                                  ' instruction expects 2 arguments; ' + str(instruction_args) + 
                                  ' given at [Source line: ' + str(source_line_num) + ']')
            elif tokenized_line.getStructure()[instruction_pos].get_text() == 'jalr' and (instruction_args != 2 and instruction_args != 3):
                raise SyntaxError(tokenized_line.getStructure()[instruction_pos].get_text() + 
                                  ' instruction expects 2 (or 3) arguments; ' + str(instruction_args) + 
                                  ' given at [Source line: ' + str(source_line_num) + ']')
        # Identify instruction arguments
        if instruction_flag:
            argument_pos = instruction_pos + 2
            tokenized_line.replaceTokenwith(argument_pos, RegisterToken(source_line_num, tokenized_line.getStructure()[argument_pos].get_text()))
            argument_pos += 2
            if tokenized_line.getStructure()[instruction_pos].get_text() == 'lui':
                tokenized_line.replaceTokenwith(argument_pos, UnsignedImmediateToken(source_line_num, tokenized_line.getStructure()[argument_pos].get_text()))
                
            else:
                tokenized_line.replaceTokenwith(argument_pos, RegisterToken(source_line_num, tokenized_line.getStructure()[argument_pos].get_text()))
                argument_pos += 2
                if (tokenized_line.getStructure()[instruction_pos].get_text() == 'add' or 
                tokenized_line.getStructure()[instruction_pos].get_text() == 'nand'):
                    tokenized_line.replaceTokenwith(argument_pos, RegisterToken(source_line_num, tokenized_line.getStructure()[argument_pos].get_text()))
                    
                elif (tokenized_line.getStructure()[instruction_pos].get_text() == 'addi' or 
                tokenized_line.getStructure()[instruction_pos].get_text() == 'sw' or
                tokenized_line.getStructure()[instruction_pos].get_text() == 'lw' or
                tokenized_line.getStructure()[instruction_pos].get_text() == 'beq'):
                    tokenized_line.replaceTokenwith(argument_pos, SignedImmediateToken(source_line_num, tokenized_line.getStructure()[argument_pos].get_text()))
                
                # Handle jalr
                elif (tokenized_line.getStructure()[instruction_pos].get_text() == 'jalr') and len(tokenized_line.getStructure()) > argument_pos:
                    tokenized_line.replaceTokenwith(argument_pos, SignedImmediateToken(source_line_num, tokenized_line.getStructure()[argument_pos].get_text()))
        # Identify directive arguments
        if directive_flag:
            if tokenized_line.getStructure()[directive_pos].get_text() == '.fill':
                tokenized_line.replaceTokenwith(directive_pos+2, SignedImmediateToken(source_line_num, tokenized_line.getStructure()[directive_pos+2].get_text(),fill_mode = True))
            elif tokenized_line.getStructure()[directive_pos].get_text() == '.space':
                tokenized_line.replaceTokenwith(directive_pos+2, UnsignedImmediateToken(source_line_num, tokenized_line.getStructure()[directive_pos+2].get_text()))
            elif tokenized_line.getStructure()[directive_pos].get_text() == 'lli' or tokenized_line.getStructure()[directive_pos].get_text() == 'movi':
                tokenized_line.replaceTokenwith(directive_pos+2, RegisterToken(source_line_num, tokenized_line.getStructure()[directive_pos+2].get_text()))
                tokenized_line.replaceTokenwith(directive_pos+4, SignedImmediateToken(source_line_num, tokenized_line.getStructure()[directive_pos+4].get_text()))
            
        return tokenized_line


class TokenizedLine:
    def __init__(self):
        self.structure = []
        
    def getStructure(self):
        return self.structure
        
    def appendToken(self, Token):
        self.structure.append(Token)
        
    def removeToken(self, index):
        del self.structure[index]
    
    def replaceTokenwith(self, index, Token):
        self.structure[index] = Token
        
    def containsDirective(self):
        for position, Token in enumerate(self.structure):
            if isinstance(Token, DirectiveToken):
                return position
        return -1
        
    def __repr__(self):
        listing = ''
        for Token in self.structure:
            listing += Token.__str__() +'\n'
        return listing
        
class SyntaxToken:
    def __init__(self, line_num):
        self.line_num = line_num
        if self.line_num < 0:
            raise IndexError('Invalid syntax token index at [Source line: ' + str(self.line_num) + ']')
        
    def get_line_num(self):
        return self.line_num
    
class WhitespaceToken(SyntaxToken):
    def __init__(self, line_num):
        SyntaxToken.__init__(self, line_num)
    
    def __str__(self):
        return 'Whitespace Token ( )'

class TextToken(SyntaxToken):
    def __init__(self, line_num, text_string):
        self.text = text_string
        SyntaxToken.__init__(self, line_num)
        verification = self.text
        verification = verification.replace(':', 'a1')
        verification = verification.replace(',', 'a1')
        verification = verification.replace('.', 'a1')
        verification = verification.replace('-', 'a1')
        if not verification.isalnum():
            raise SyntaxError('Invalid character found in text token at [Source line: ' + str(self.line_num)+ ']')

    def get_text(self):
        return self.text

    def __str__(self):
        return 'Text Token (' + self.text + ')'
    
class LabelToken(TextToken):
    def __init__(self, line_num, label):
        if label == '':
            raise SyntaxError('Empty name found in label token at [Source line: ' + str(line_num)+ ']')
        TextToken.__init__(self, line_num, label)
    
    def setLocation(self, programaddress):
        self.location = programaddress
        return
    
    def __str__(self):
        return 'Label Token (' + self.text + ')'
    
class DirectiveToken(TextToken):
    def __init__(self, line_num, directive):
        TextToken.__init__(self, line_num, directive)
    
    def __str__(self):
        return 'Directive Token (' + self.text + ')'
    
class InstructionToken(TextToken):
    def __init__(self, line_num, instruction):
        TextToken.__init__(self, line_num, instruction)
    
    def __str__(self):
        return 'Instruction Token (' + self.text + ')'
    
class RegisterToken(TextToken):
    def __init__(self, line_num, register):
        if not register.replace('r','').isdigit():
            raise SyntaxError('Invalid register reference found in register token at [Source line: ' + str(line_num)+ ']')
        if int(register.replace('r','')) not in range(8):
            raise SyntaxError('Invalid register reference found in register token at [Source line: ' + str(line_num)+ ']')
        TextToken.__init__(self, line_num, register.replace('r', ''))

    def __str__(self):
        return 'Register Token (' + self.text + ')'

class UnsignedImmediateToken(TextToken):
    def __init__(self, line_num, value):
        self.mag = value
        self.octal = False
        self.dec = False
        self.hex = False

        if value[0] == '-':
            raise ValueError('Negative unsigned immediate found in unsigned immediate token at [Source line: ' + str(line_num)+ ']')
        if self.mag.startswith('0') and not self.mag.startswith('0x'):
            self.symbolic = False
            self.octal = True
        elif self.mag.startswith('0x'):
            self.symbolic = False
            self.hex = True
        elif self.mag.isdigit():
            self.symbolic = False
            self.dec = True
        else:
            self.symbolic = True
        
        if self.symbolic:
            TextToken.__init__(self, line_num, self.mag) 
        else:
            if self.octal:
                try:
                    self.integer = int(self.mag, 8)
                except:
                    raise ValueError('Invalid value found in unsigned immediate token at [Source line: ' + str(line_num)+ ']')
            elif self.dec:
                try:
                    self.integer = int(self.mag, 10)
                except:
                    raise ValueError('Invalid value found in unsigned immediate token at [Source line: ' + str(line_num)+ ']')
            else:
                try:
                    self.integer = int(self.mag, 16)
                except:
                    raise ValueError('Invalid value found in unsigned immediate token at [Source line: ' + str(line_num)+ ']')

            if (self.integer > 1023 or self.integer < 0):
                raise ValueError('Value out of bounds in unsigned immediate token at [Source line: ' + str(line_num)+ ']')
            else:
                TextToken.__init__(self, line_num, str(self.integer))
                
           
    def __str__(self):
        if self.symbolic:
            return 'Symbolic Unsigned Immediate Token (' + self.text + ')'
        else:
            return 'Unsigned Immediate Token (' + self.text + ')'
        
        
class SignedImmediateToken(TextToken):
    def __init__(self, line_num, value, fill_mode = False):
        self.fill_mode = fill_mode
        self.negative = False
        self.mag = value
        self.octal = False
        self.dec = False
        self.hex = False

        if value[0] == '-':
            self.symbolic = False
            self.negative = True
            self.mag = value[1:]
        if self.mag.startswith('0') and not self.mag.startswith('0x'):
            self.symbolic = False
            self.octal = True
        elif self.mag.startswith('0x'):
            self.symbolic = False
            self.hex = True
        elif self.mag.isdigit():
            self.symbolic = False
            self.dec = True
        else:
            self.symbolic = True
        
        if self.symbolic:
            TextToken.__init__(self, line_num, value) 
        else:
            if self.negative:
                self.mag = '-' + self.mag
            if self.octal:
                try:
                    self.integer = int(self.mag, 8)
                except:
                    raise ValueError('Invalid value found in signed immediate token at [Source line: ' + str(line_num)+ ']')
            elif self.dec:
                try:
                    self.integer = int(self.mag, 10)
                except:
                    raise ValueError('Invalid value found in signed immediate token at [Source line: ' + str(line_num)+ ']')
            else:
                try:
                    self.integer = int(self.mag, 16)
                except:
                    raise ValueError('Invalid value found in signed immediate token at [Source line: ' + str(line_num)+ ']')

            if (self.integer > 63 or self.integer < -64) and not self.fill_mode:
                raise ValueError('Value out of bounds in signed immediate token at [Source line: ' + str(line_num)+ ']')
            else:
                TextToken.__init__(self, line_num, str(self.integer))
                
        
    def __str__(self):
        if self.symbolic:
            return 'Symbolic Signed Immediate Token (' + self.text + ')'
        else:
            return 'Signed Immediate Token (' + self.text + ')'
        

