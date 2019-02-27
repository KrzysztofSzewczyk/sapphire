from sys import *
from subprocess import *
from os.path import *
import _lexer
import _parser

if __name__ == '__main__':

    if len(argv) < 3:
        exit('usage: sapphire <file.sph> <file.b> [options]\n'
            ' options:\n'
            ' -S                output assembler to stdout\n')

    options = argv[3:]
    path = dirname(__file__) + '/'
    if path == '/': path = ''
    f = open(argv[1], 'r')
    code = f.read()
    f.close()
    py = _lexer.lex(code)
    #print(py)
    err = False
    try:
        py = compile(py, '<sapphire>', 'exec')
        exec(py, vars(_parser))
    except Exception as e:
        stderr.write('error: %s\n' % str(e))
        err = True
    if err: exit()
    asm = _parser._asm.code.strip()
    bf = run([path+'bfasm'], stdout=PIPE, input=asm, encoding='ascii')
    
    if '-S' in options:
        print(asm)
    else:
        f = open(argv[2], 'w')
        f.write(bf.stdout)
        f.close()
