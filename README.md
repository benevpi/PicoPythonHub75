# PicoPythonHub75

Hub75 LED panels are an affordable way of adding lots of colourful lights to a build. This project shows you how to control a 32x32 RGB LED panel using MicroPython. Pico’s PIO lets you output data fast enough for smooth animations.

![Hub75 in action](https://github.com/benevpi/PicoPythonHub75/blob/main/IMG_20210119_122102321.jpg)

PIO handles both the addressing and the outputting of data. At the moment, this works on 32x32 LED screens. In principle, it should work on other sizes, but you'll need to sort out the addressing. Actually, the addressing is a bit of a mess. It works, but I don't think it works in the right way -- if you're familiar with hub75 addressing and can see where I've gone wrong, I'd appreciate a pointer in the write direction.

HUB75E Pinout:

```
    /-----\
R0  | o o | G0
B0  | o o | GND
R1  | o o | G1
B1  \ o o | E
A   / o o | B
C   | o o | D
CLK | o o | STB
OEn | o o | GND
    \-----/
```

Wiring:

```
Must be contiguous, in order:
R0 - GPIO0
G0 - GPIO1
B0 - GPIO2
R1 - GPIO3
G1 - GPIO4
B1 - GPIO5

Must be contiguous, somewhat ok to change order:
A - GPIO6
B - GPIO7
C - GPIO8
D - GPIO9
E - GPIO10

Can be anywhere:
CLK - GPIO16

Must be contiguous, in order:
STB - GPIO12
OEn - GPIO13
```

If you want to change the animation, you just need to change the draw_text() method. Currently it's:

```
def draw_text():
    global text_y
    global direction
    global writing
    global current_rows
    global rows
    
    writing = True
    text_y = text_y + direction
    if text_y > 20: direction = -1
    if text_y < 5: direction = 1

    rows = [0]*num_rows

    #fill with black
    for j in range(num_rows):
        rows[j] = [0]*blocks_per_row
            
    p_draw(3, text_y-4, 1, 1, 1)
    i_draw(9, text_y, 1, 1, 0)
    c_draw(11, text_y, 0, 1, 1)
    o_draw(16, text_y, 1, 0, 1)
    writing = False
```

This bounces the word Pico up and down the screen.
