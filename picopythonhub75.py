import rp2
import time
from machine import Pin
import array
import math
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
    
    nop()     .side(2) [2]
    out(pins, 5)   [2]#note 3 as only three pins needed for 32x32 screen. This might be wrong. Might needs all five still
    nop()      .side(3) [2]
    nop()      .side(2) [2]
    nop()      .side(0) [2]
    

#setup state machines
#can I run them at full tilt, or do they need slowing down?
sm_data = rp2.StateMachine(0,data_hub75, out_base=Pin(data_pin_start), sideset_base=Pin(clock_pin), freq=1000000)
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

for i in range(num_rows):
    for j in range(blocks_per_row*8):
        if j==125:
            #set_pixel(i,j,1,0,0)
            pass

#not even avove, 102, 103, 108, 109, 110, 111, 116, 117, 118, 119
#why do some pixels not exist? e.g. 0,98 / 10,10
#is it any col less than 100? no
    #yes
    #no there's 128 pixels under 100 that do light up
    #1,93 exists
    #93 exists with all odd rows
    #92 exists with even1rows
    #87?
    #86 exists with even rows
    #85 exists with odd rows
    #84 exists with even rows
    #79 exists with odd rows
    #78 exists with even rows
    #77 exists with odd rows
    #76 exists with even rows
    #71 exists with odd rows
    #70 exists with even rows
    #69 exists with odd rows
    #68 exists with even rows
        
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
    if y == 30:
        row, col = rejig(x, y, 188, 189)
    if y == 29:
        row, col = rejig(x, y, 182, 183)
    if y == 28:
        row, col = rejig(x, y, 180, 181)
    if y == 27:
        row, col = rejig(x, y, 174, 175)
    if y == 26:
        row, col = rejig(x, y, 172, 173)
    if y == 25:
        row, col = rejig(x, y, 166, 167)
    if y == 24:
        row, col = rejig(x, y, 164, 165)
    if y == 23:
        row, col = rejig(x, y, 158, 159)
    if y == 22:
        row, col = rejig(x, y, 156, 157)
    if y == 21:
        row, col = rejig(x, y, 150, 151)
    if y == 20:
        row, col = rejig(x, y, 148, 149)
    if y == 19:
        row, col = rejig(x, y, 142, 143)
    if y == 18:
        row, col = rejig(x, y, 140, 141)
    if y == 17:
        row, col = rejig(x, y, 134, 135)
    if y == 16:
        row, col = rejig(x, y, 132, 133)
    if y == 15:
        row, col = rejig(x, y, 126, 127)
    if y == 14:
        row, col = rejig(x, y, 124, 125)
    if y == 13:
        row, col = rejig(x, y, 118, 119)
    if y == 12:
        row, col = rejig(x, y, 116, 117)  
    if y == 11:
        row, col = rejig(x, y, 110, 111)        
    if y == 10:
        row, col = rejig(x, y, 108, 109)
    if y == 9:
        row, col = rejig(x,y, 102, 103)
    if y == 8:
        row, col = rejig(x, y, 100, 101)
    if y == 7:
        row, col = rejig(x, y, 94, 95)
    if y == 6:
        row, col = rejig(x, y, 92, 93)
    if y == 5:
        row, col = rejig(x, y, 86, 87)
    if y == 4:
        row, col = rejig(x, y, 84, 85)
    if y == 3:
        row, col = rejig(x, y, 78, 79)
    if y == 2:
        row, col = rejig(x, y, 76, 77)
    if y == 1:
        row, col = rejig(x, y, 70, 71)
    if y == 0:
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
    
        
p_draw(3, 10, 0, 1, 0)
i_draw(9, 14, 0, 1, 0)
c_draw(11, 14, 0, 1, 0)
o_draw(16, 14, 0, 1, 0)

while(True):
    #select row -- not sure how to interleave. Work this out later
    #a_rows[0]=0xffff # this isn't working on either 0 or 1?
    #print("looping")
    #(100u * (1u << bit) << 5))
    sm_row.put(counter)
    #print("row selected")
    #time.sleep(0.0001)
    
    if not toggle:
        for i in range(blocks_per_row):
            sm_data.put(rows[counter][i])
            #sm_data.put(0x00000000)
        #for i in range(blocks_per_row):
        #    sm_data.put(rows[counter][i])
    else:
        for i in range(blocks_per_row):
           sm_data.put(0x00000000)
    #sm_data.put(0x00000000)
        
        
    #sm_data.put(a_data)
    '''
    for x in range(4):
        sm_data.put(toggle)
        sm_data.put(toggle)
    '''
    #sm_data.put(0)
    counter = counter +1
    if (counter > (num_rows-1)):
        counter = 0
        if toggle:
            toggle = False
        else:
            toggle = False
    #time.sleep(1)
    #output 192 bits of data
    #repeat
    
