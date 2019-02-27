class asm:

    def __init__(self):
        self.code = 'stk 16\n'

    def __call__(self, code):
        self.code += '%s\n' % code

_asm = asm()

class memory:

    def __init__(self, size):
        self.u = [True]+[False]*size

    def alloc(self):
        for i in range(len(self.u)):
            if self.u[i] == False:
                self.u[i] = True
                return i

    def free(self, addr):
        self.u[addr] = False

memory = memory(0x10000)

class _Int(object):

    def __init__(self, v=0):
        super(_Int, self).__init__()
        self.addr = memory.alloc()
        self.value = v
        self.iss = False

    def mov(self, r, n):
        if n % 10 == 0:
            _asm('mov %s, %d' % (r, n/10))
            _asm('mul %s, 10' % r)
        elif n % 5 == 0:
            _asm('mov %s, %d' % (r, n/5))
            _asm('mul %s, 5' % r)
        elif n % 4 == 0:
            _asm('mov %s, %d' % (r, n/4))
            _asm('mul %s, 4' % r)
        elif n % 3 == 0:
            _asm('mov %s, %d' % (r, n/3))
            _asm('mul %s, 3' % r)
        elif n % 2 == 0:
            _asm('mov %s, %d' % (r, n/2))
            _asm('mul %s, 2' % r)
        else:
            _asm('mov %s, %d' % (r, n))

    def set(self, v):

        if v == 0: return
        if v == None: return

        if isinstance(v, int):
            self.mov('r2', v)
            _asm('mov r1, %d' % self.addr)
            _asm('sto r1, r2')

    def get(self, reg):

        if self.value != None:
            self.mov(reg, self.value)
        else:
            if not self.iss:
                self.set(self.value)
                self.iss = True
            _asm('rcl %s, %d' % (reg, self.addr))

    def op(self, a, b):
        x = _Int(None)
        b.get('r1')
        self.get('r2')
        _asm('%s r2, r1' % a)
        _asm('mov r1, %d' % x.addr)
        _asm('sto r1, r2')
        return x

    def __add__(self,e):
        if self.value != None and e.value != None:
            return _Int(self.value + e.value)
        return self.op('add',e)
    
    def __sub__(self,e):
        if self.value != None and e.value != None:
            return _Int(self.value - e.value)
        return self.op('sub',e)
    
    def __mul__(self,e):
        if self.value != None and e.value != None:
            return _Int(self.value * e.value)
        return self.op('mul',e)
    
    def __div__(self,e):
        if self.value != None and e.value != None:
            return _Int(self.value / e.value)
        return self.op('div',e)
    
    def __eq__(self,e):
        if self.value != None and e.value != None:
            return _Int(self.value == e.value)
        return self.op('eq_',e)
    
    def __ne__(self,e):
        if self.value != None and e.value != None:
            return _Int(self.value != e.value)
        return self.op('ne_',e)
    
    def __le__(self,e):
        if self.value != None and e.value != None:
            return _Int(self.value <= e.value)
        return self.op('le_',e)
    
    def __ge__(self,e):
        if self.value != None and e.value != None:
            return _Int(self.value >= e.value)
        return self.op('ge_',e)
    
    def __gt__(self,e):
        if self.value != None and e.value != None:
            return _Int(self.value > e.value)
        return self.op('gt_',e)
    
    def __lt__(self,e):
        if self.value != None and e.value != None:
            return _Int(self.value < e.value)
        return self.op('lt_',e)

class _List:

    def __init__(self, x):
        self.x = list(x)

    def __setitem__(self, i, e):
        self.x[i.value] = e

    def __getitem__(self, i):
        if isinstance(i, int):
            return self.x[i]
        else:
            return self.x[i.value]

    def _size(self):
        return _Int(len(self.x))

    def _insert(self, e):
        self.x += [e]

class _io:

    def _putchar(e):
        e.get('r1')
        _asm('out r1')

    def _getchar():
        e = _Int(None)
        _asm('mov r1, %d' % e.addr)
        _asm('in_ r2')
        _asm('sto r1, r2')
        return e

    def _puts(s):
        for c in s.x:
            _io._putchar(c)

labeli = 1
labelx = []
lastix = None

def if_(x):
    global labeli, labelx, lastix
    x.get('r1')
    _asm('jz_ r1, %d' % labeli)
    labelx += [labeli]
    labeli += 1
    lastix = _Int(None)
    x.get('r1')
    _asm('mov r2, %d' % lastix.addr)
    _asm('sto r2, r1')

def else_():
    global labeli, labelx, lastix
    lastix.get('r1')
    _asm('jnz r1, %d' % labeli)
    labelx += [labeli]
    labeli += 1

def end_():
    e = labelx.pop()
    _asm('lbl %d' % e)
