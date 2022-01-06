import numpy as np
x = np.uint8(0xf7)
y = np.int8(x)
print('{:02x}'.format(x))
print(y)




"""
from blessed import Terminal

term = Terminal()
print(term.home + term.clear + term.move_y(term.height // 2))
print(term.black_on_darkkhaki(term.center('press any key to continue.')))

with term.cbreak(), term.hidden_cursor():
    inp = term.inkey()

print(term.move_down(2) + 'You pressed ' + term.bold(repr(inp)))

def changeColor(number):
    number = number % 3
    if (number == 0):
        print(term.white, end='')
    elif (number == 1):
        print(term.blue, end='')
    elif (number == 2):
        print(term.cyan, end='')
    return

bytes = [11,22,33,44,55,66,77,88,99,11,22,33,44,55,66,77,88]
x = 0
y = 0
print(term.home + term.clear, end='')
for m in range(0,10):
    x = 0
    changeColor(y)
    print(term.move_y(y), end='')
    y = y + 1
    for b in bytes:
        print(term.move_x(x), end='')
        print(b, end='')
        x = x + 3
print(term.normal)

"""
