import rp2
import time
from machine import Pin
import array

#does something as long as output enable isn't plugged in?
#Maybe fial down the freq?

clock_pin = 16
data_pin_start = 0
latch_pin_start = 12
row_pin_start = 6

row_bits = 3
data_bits = 192 # note must be divisible by 32

row_ar_len = 50

@rp2.asm_pio(out_shiftdir=0, autopull=True, pull_thresh=24, out_init=(rp2.PIO.OUT_HIGH, rp2.PIO.OUT_LOW, rp2.PIO.OUT_HIGH,
                                                                    rp2.PIO.OUT_HIGH, rp2.PIO.OUT_HIGH, rp2.PIO.OUT_HIGH), sideset_init=(rp2.PIO.OUT_LOW))
def data_hub75():
    #pull # actually, can I use autopull?
    #is this a bit weird? better to use nops with side set?
    #really simple clocking out of pins?
    #not 100% sure how this will work as pulling in 32 bits at a time, but out won't line up with this?
    #do I need some dummy bits?
    #wrap_target()
    
    nop() .side(0)
    out(pins, 6) .side(1)
    #out(pins, 6) .side(1)
    #wrap()
    
@rp2.asm_pio(out_shiftdir=1, autopull=False,out_init=(rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,
            rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW), sideset_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW))

def row_hub75():
    wrap_target()
    pull()
    
    nop()     .side(2)
    out(pins, 5)  #note 3 as only three pins needed for 32x32 screen. This might be wrong. Might needs all five still
    nop()      .side(3)
    nop()      .side(2)
    nop()      .side(0)
    

#setup state machines
#can I run them at full tilt, or do they need slowing down?
sm_data = rp2.StateMachine(0,data_hub75, out_base=Pin(data_pin_start), sideset_base=Pin(clock_pin), freq=500000)
sm_row = rp2.StateMachine(1, row_hub75, out_base=Pin(row_pin_start),sideset_base=Pin(latch_pin_start), freq=100000)

#note - L is unsigned long - 32 bits. 
a_rows = array.array("I", [0xffff, 0xffff]) # try and put some row data in there?
a_data = array.array("I", [0xffff for _ in range(row_ar_len)])

#test, let's make everything white (note - I have a good power supply!)
#for i in range(row_ar_len):
#    a_data[i] = 0x1000 # chuck some data in and work it out later
    
sm_row.active(1)
sm_data.active(1)

counter = 0

toggle = 0xffffffff

while(True):
    #select row -- not sure how to interleave. Work this out later
    #a_rows[0]=0xffff # this isn't working on either 0 or 1?
    #print("looping")
    #(100u * (1u << bit) << 5))
    sm_row.put(counter)
    #print("row selected")
    time.sleep(0.0001)
    
    #sm_data.put(a_data)
    for x in range(4):
        sm_data.put(toggle)
        sm_data.put(toggle)
    #sm_data.put(0)
    counter = counter +1
    if (counter > 15): counter = 0
    
    if toggle == 0xffffffff:
        toggle = 0x00000000
    else:
        toggle = 0xffffffff
    #time.sleep(1)
    #output 192 bits of data
    #repeat
    
