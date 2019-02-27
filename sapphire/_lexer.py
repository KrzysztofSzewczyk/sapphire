import re
import sys

class Token(object):

    def __init__(self, type, val, pos):
        self.type = type
        self.val = val
        self.pos = pos

    def __str__(self):
        return '%s(%s) at %s' % (self.type, self.val, self.pos)

class LexerError(Exception):

    def __init__(self, pos):
        self.pos = pos

class Lexer(object):

    def __init__(self, rules, skip_whitespace=True):
        idx = 1
        regex_parts = []
        self.group_type = {}

        for regex, type in rules:
            groupname = 'GROUP%s' % idx
            regex_parts.append('(?P<%s>%s)' % (groupname, regex))
            self.group_type[groupname] = type
            idx += 1

        self.regex = re.compile('|'.join(regex_parts))
        self.skip_whitespace = skip_whitespace
        self.re_ws_skip = re.compile('\S')

    def input(self, buf):
        self.buf = buf
        self.pos = 0

    def token(self):
        if self.pos >= len(self.buf):
            return None
        else:
            if self.skip_whitespace:
                m = self.re_ws_skip.search(self.buf, self.pos)

                if m:
                    self.pos = m.start()
                else:
                    return None

            m = self.regex.match(self.buf, self.pos)
            if m:
                groupname = m.lastgroup
                tok_type = self.group_type[groupname]
                tok = Token(tok_type, m.group(groupname), self.pos)
                self.pos = m.end()
                return tok

            raise LexerError(self.pos)

    def tokens(self):
        while 1:
            tok = self.token()
            if tok is None: break
            yield tok

def lex(code):
    rules = [
        ('asm\(\".*?\"\)', 'ASM'),
        ('\'.\'', 'CHAR'),
        ('\".*?\"', 'STR'),
        ('(0x([0-9A-Fa-f]+))|(\d+)', 'NUM'),
        ('[a-zA-Z0-9_]+', 'ID'),
        ('\/\*', '/*'),('\*\/', '*/'),
        ('\+', '+'),('\-', '-'),
        ('\*', '*'),('\/', '/'),
        ('\[', '['),('\]', ']'),
        ('\{', '{'),('\}', '}'),
        ('\(', '('),('\)', ')'),
        ('\.', '.'),('\,', ','),
        ('==', '=='),('!=', '!='),
        ('<=', '<='),('>=', '>='),
        ('<', '<'),('>', '>'),(':', ':'),
        ('\+=', '+='),('\-=', '-='),
        ('\(=', '*='),('\/=', '/='),
        ('\=', '='),('\;', ';'),]

    lx = Lexer(rules, skip_whitespace=True)
    lx.input(code)
    output = ''
    ign = False
    fob = False
    ftc = []

    try:
        for tok in lx.tokens():
            v = tok.val
            if v == '/*':
                ign = True
                continue
            if v == '*/':
                ign = False
                continue
            if ign: continue
            if v == 'in': output += ' in '
            elif v == 'if': output += 'if_'
            elif v == 'return': output += 'return '
            elif v == 'fn':
                output += 'def '
                fob = True
            elif v == 'for':
                output += ' for '
            elif v == 'else': output += 'else_()'
            elif v == 'while': output += 'while_'
            elif v == '{':
                if fob:
                    output += ':\n pass;'
                    fob = False
                    ftc += ['f']
                else:
                    output += ';'
                    ftc += ['b']
            elif v == '}':
                e = ftc.pop()
                if e == 'b':
                    output += 'end_();'
                elif e == 'f':
                    output += '\n'
            elif tok.type == 'CHAR': output += '_Int(%d)' % ord(eval(v))
            elif tok.type == 'NUM': output += '_Int(%d)' % eval(v)
            elif tok.type == 'ASM': output += '_%s' % v
            elif tok.type == 'ID': output += '_%s' % v
            elif tok.type == 'STR':
                v = eval(v)
                output += '_List(['
                x = ['_Int(%s)' % str(ord(e)) for e in list(v)]
                output += '%s])' % ','.join(x)
            else:
                output += v
    except LexerError as err:
        sys.exit('error: invalid syntax (<sapphire>, line %d)' %
            (code[:int(err.pos)].count('\n')+1))

    return output+'_asm("end")'
