# PicoPythonHub75

Hub75 LED panels are an affordable way of adding lots of colourful lights to a build. This project shows you how to control a 32x32 RGB LED panel using MicroPython. Pico’s PIO lets you output data fast enough for smooth animations.

PIO handles both the addressing and the outputting of data. 

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
