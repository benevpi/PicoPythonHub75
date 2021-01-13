import rp2
import time
from machine import Pin
import array
import math
import _thread
#TODO
#* work out how to place pixels in different places
#* buffering??

clock_pin = 16
data_pin_start = 0
latch_pin_start = 12
row_pin_start = 6

row_bits = 3
data_bits = 192 # note must be divisible by 32

row_ar_len = 50

@rp2.asm_pio(out_shiftdir=1, autopull=True, pull_thresh=24, out_init=(rp2.PIO.OUT_HIGH, rp2.PIO.OUT_LOW, rp2.PIO.OUT_HIGH,
                                                                    rp2.PIO.OUT_HIGH, rp2.PIO.OUT_HIGH, rp2.PIO.OUT_HIGH), sideset_init=(rp2.PIO.OUT_LOW))
def data_hub75():
    #pull # actually, can I use autopull?
    #is this a bit weird? better to use nops with side set?
    #really simple clocking out of pins?
    #not 100% sure how this will work as pulling in 32 bits at a time, but out won't line up with this?
    #do I need some dummy bits?
    #wrap_target()
    
    #nop() .side(0)
    out(pins, 6) .side(1)
    out(pins, 6) .side(0)
    #wrap()
    
@rp2.asm_pio(out_shiftdir=1, autopull=False,out_init=(rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,
            rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW), sideset_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW))

def row_hub75():
    wrap_target()
    pull()
    
    nop()     .side(2) 
    out(pins, 5)   [2]#note 3 as only three pins needed for 32x32 screen. This might be wrong. Might needs all five still
    nop()      .side(3) #this triggers the latch
    nop()      .side(2) #this disables the latch
    nop()      .side(0) 
    

#setup state machines
#can I run them at full tilt, or do they need slowing down?
sm_data = rp2.StateMachine(0,data_hub75, out_base=Pin(data_pin_start), sideset_base=Pin(clock_pin), freq=55000000)
sm_row = rp2.StateMachine(1, row_hub75, out_base=Pin(row_pin_start),sideset_base=Pin(latch_pin_start), freq=1000000)

#note - L is unsigned long - 32 bits. 
a_rows = array.array("I", [0xffff, 0xffff]) # try and put some row data in there?
a_data = array.array("I", [0xffff for _ in range(row_ar_len)])

#test, let's make everything white (note - I have a good power supply!)
#for i in range(row_ar_len):
#    a_data[i] = 0x1000 # chuck some data in and work it out later
    
sm_row.active(1)
sm_data.active(1)

counter = 0

toggle = False

#data format
#-- send data in 24-bit blocks
# 8 24 bit blocks per 'row'
#how many 'rows'? 15? 16?
#data is sequential rgb bits

rows = []
blocks_per_row = 24 #each block has 24 bits, so 8 pixels
num_rows = 16

#fill with white
'''
for j in range(num_rows):
    rows.append([])
    for i in range(blocks_per_row):
        rows[j].append(0xffffffff)
'''

#fill with black
for j in range(num_rows):
    rows.append([])
    for i in range(blocks_per_row):
        rows[j].append(0x00000000)

#let's light up an individual pixel
#each block has (I think) 8 pixels (with rgb values for each)
#each'row' has 64 pixels
        
#there are 32x32 pixels, so our data size needs to match this.
# if there are only 12 'rows', then each row has to be 86-ish pixels long
# (do I need dummy pixels to make rows the right lenght?
# this is 11 'blocks'
def set_pixel(row, col, red, green, blue):
    block = math.floor(col/8) # 8 is number of pixes in block (24 bits)
    block_posn = col%8
    #set red
    rows[row][block] = rows[row][block] | red << (block_posn * 3)
    #set green
    rows[row][block] = rows[row][block] | (green << (block_posn * 3)+1)
    #set blue
    rows[row][block] = rows[row][block] | (blue << (block_posn * 3)+2)


#odd numbers for columns causing problems


        
def rejig(x, y, even_col, odd_col):
    if x > 15: x=x+1
    flip_x = 32-x
    if flip_x < 17:
        col = even_col
        row = flip_x-1
    else:
        col = odd_col
        row = flip_x-16-2
    return row, col
    
        
def light_xy(x,y, r, g, b):
    #I'm sure there's a better way to do this. What am I missing?
    if y == 31:
        row, col = rejig(x, y, 190, 191)
    elif y == 30:
        row, col = rejig(x, y, 188, 189)
    elif y == 29:
        row, col = rejig(x, y, 182, 183)
    elif y == 28:
        row, col = rejig(x, y, 180, 181)
    elif y == 27:
        row, col = rejig(x, y, 174, 175)
    elif y == 26:
        row, col = rejig(x, y, 172, 173)
    elif y == 25:
        row, col = rejig(x, y, 166, 167)
    elif y == 24:
        row, col = rejig(x, y, 164, 165)
    elif y == 23:
        row, col = rejig(x, y, 158, 159)
    elif y == 22:
        row, col = rejig(x, y, 156, 157)
    elif y == 21:
        row, col = rejig(x, y, 150, 151)
    elif y == 20:
        row, col = rejig(x, y, 148, 149)
    elif y == 19:
        row, col = rejig(x, y, 142, 143)
    elif y == 18:
        row, col = rejig(x, y, 140, 141)
    elif y == 17:
        row, col = rejig(x, y, 134, 135)
    elif y == 16:
        row, col = rejig(x, y, 132, 133)
    elif y == 15:
        row, col = rejig(x, y, 126, 127)
    elif y == 14:
        row, col = rejig(x, y, 124, 125)
    elif y == 13:
        row, col = rejig(x, y, 118, 119)
    elif y == 12:
        row, col = rejig(x, y, 116, 117)  
    elif y == 11:
        row, col = rejig(x, y, 110, 111)        
    elif y == 10:
        row, col = rejig(x, y, 108, 109)
    elif y == 9:
        row, col = rejig(x,y, 102, 103)
    elif y == 8:
        row, col = rejig(x, y, 100, 101)
    elif y == 7:
        row, col = rejig(x, y, 94, 95)
    elif y == 6:
        row, col = rejig(x, y, 92, 93)
    elif y == 5:
        row, col = rejig(x, y, 86, 87)
    elif y == 4:
        row, col = rejig(x, y, 84, 85)
    elif y == 3:
        row, col = rejig(x, y, 78, 79)
    elif y == 2:
        row, col = rejig(x, y, 76, 77)
    elif y == 1:
        row, col = rejig(x, y, 70, 71)
    elif y == 0:
        row, col = rejig(x, y, 68, 69)
    set_pixel(row, col, r, g, b)
    
#p-shape
#should these really be stored as datapoints?
def p_draw(init_x, init_y, r, g, b):
    #line 10 pixels high
    for i in range(10):
        light_xy(init_x, init_y+i, r, g, b)
    #line 4 pixesl across
    for i in range(4):
        light_xy(init_x+i, init_y, r, g, b)
    for i in range(4):
        light_xy(init_x+i, init_y+4, r, g, b)
    for i in range(3):
        light_xy(init_x+4, init_y+i+1, r, g, b)
        
def i_draw(init_x, init_y, r, g, b):
    for i in range(4):
        light_xy(init_x, init_y+i+2, r, g, b)
    light_xy(init_x, init_y, r, g, b)
    
def c_draw(init_x, init_y, r, g, b):
    for i in range(4):
        light_xy(init_x, init_y+i+1, r, g, b)
    for i in range(3):
        light_xy(init_x+1+i, init_y, r, g, b)
        light_xy(init_x+1+i, init_y+5, r, g, b)
        
def o_draw(init_x, init_y, r, g, b):
    for i in range(4):
        light_xy(init_x, init_y+i+1, r, g, b)
        light_xy(init_x+4, init_y+i+1, r, g, b)
    for i in range(3):
        light_xy(init_x+1+i, init_y, r, g, b)
        light_xy(init_x+1+i, init_y+5, r, g, b)

text_y = 14
direction = 1

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
    
draw_text()
draw_counter = 0

#going to need double-buffering

writing = False

out_rows = rows

    
while(True):

    sm_row.put(counter)

    for i in range(blocks_per_row):
        sm_data.put(out_rows[counter][i])

    counter = counter +1
    if (counter > 15):
        counter = 0
        if writing == False:
            out_rows = rows.copy()
            _thread.start_new_thread(draw_text, ())
    

