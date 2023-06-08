# requires adafruit_ov7670.mpy and adafruit_st7735r.mpy in the lib folder
import time
from displayio import (
    Bitmap,
    Group,
    TileGrid,
    FourWire,
    release_displays,
    ColorConverter,
    Colorspace,
)
from adafruit_st7735r import ST7735R
import board
import busio
import digitalio
from adafruit_ov7670 import (
    OV7670,
    OV7670_SIZE_DIV1,
    OV7670_SIZE_DIV8,
    OV7670_SIZE_DIV16,
)
from ulab import numpy as np

smoothingKernel = np.array([0.006, 0.061, 0.242, 0.383, 0.242, 0.061, 0.006])
edgeKernel = np.array([-0.5,0,0.5])
numRows = 5
def getCOM(bitmap,numRows,ek,sk):
    # Takes in a bitmap and returns the center of mass (COM)
    # Inputs:
    # - bitmap - 2D array, 60 wide, 80 tall, 16 bit color
    # - numRows - number of rows to consider
    # - ek - edge detection kernel
    # - sk - smoothing kernel
    # Output: 
    # - COM - center of mass, 0 if centered, 1 if max right, -1 if max left

    red = np.zeros((numRows,60))
    green = np.zeros((numRows,60))
    blue = np.zeros((numRows,60))
    redEdge = np.zeros((numRows,62))
    greenEdge = np.zeros((numRows,62))
    blueEdge = np.zeros((numRows,62))

    increment = int(80/(numRows+1)) # Incremental number of pixels between rows
    for i in range(numRows): # Iterate over the number of rows
        for j in range(60): # Iterate over all the pixels in a row
            red[i,j] = ((bitmap[increment*(i+1),j]>>5)&0x3F)/0x3F # Grab the red brightness
            green[i,j] = ((bitmap[increment*(i+1),j])&0x1F)/0x1F # Grab the green brightness
            blue[i,j] = (bitmap[increment*(i+1),j]>>11)/0x1F # Grab the blue brightness
        redEdge[i,:] = abs(np.convolve(red[i,:],edgeKernel))
        greenEdge[i,:] = abs(np.convolve(green[i,:],edgeKernel))
        blueEdge[i,:] = abs(np.convolve(blue[i,:],edgeKernel))
            
    # There should be a change in color between the background color and the line color, 
    # so we will use convolution to detect this edge
    # I have decided that the new metric should just be a combination of these three
    metric = (redEdge+greenEdge+blueEdge)/100
    n = np.size(redEdge,axis=1)

    initialCOM = np.zeros(numRows) # Set up an array to hold the COM for each row
    for i in range(numRows):
        initialCOM[i] = np.sum(np.linspace(1,n,num=n)*metric[i,:])/(n*np.sum(metric[i,:])/2) - 1
    COM = np.mean(initialCOM)
    print(COM)
    return COM


release_displays()
spi = busio.SPI(clock=board.GP2, MOSI=board.GP3)
display_bus = FourWire(spi, command=board.GP0, chip_select=board.GP1, reset=None)
display = ST7735R(display_bus, width=160, height=128, rotation=90) 


# Ensure the camera is shut down, so that it releases the SDA/SCL lines,
# then create the configuration I2C bus

with digitalio.DigitalInOut(board.GP10) as reset:
    reset.switch_to_output(False)
    time.sleep(0.001)
    bus = busio.I2C(board.GP9, board.GP8) #GP9 is SCL, GP8 is SDA

# Set up the camera (you must customize this for your board!)
cam = OV7670(
    bus,
    data_pins=[
        board.GP12,
        board.GP13,
        board.GP14,
        board.GP15,
        board.GP16,
        board.GP17,
        board.GP18,
        board.GP19,
    ],  # [16]     [org] etc
    clock=board.GP11,  # [15]     [blk]
    vsync=board.GP7,  # [10]     [brn]
    href=board.GP21,  # [27/o14] [red]
    mclk=board.GP20,  # [16/o15]
    shutdown=None,
    reset=board.GP10,
)  # [14]

width = display.width
height = display.height

bitmap = None
# Select the biggest size for which we can allocate a bitmap successfully, and
# which is not bigger than the display
for size in range(OV7670_SIZE_DIV1, OV7670_SIZE_DIV16 + 1):
    #cam.size = size # for 4Hz
    #cam.size = OV7670_SIZE_DIV16 # for 30x40, 9Hz
    cam.size = OV7670_SIZE_DIV8 # for 60x80, 9Hz
    if cam.width > width:
        continue
    if cam.height > height:
        continue
    try:
        bitmap = Bitmap(cam.width, cam.height, 65535)
        break
    except MemoryError:
        continue

print(width, height, cam.width, cam.height)
if bitmap is None:
    raise SystemExit("Could not allocate a bitmap")
time.sleep(4)
g = Group(scale=1, x=(width - cam.width) // 2, y=(height - cam.height) // 2)
tg = TileGrid(
    bitmap, pixel_shader=ColorConverter(input_colorspace=Colorspace.BGR565_SWAPPED)
)
g.append(tg)
display.show(g)

t0 = time.monotonic_ns()
display.auto_refresh = False
uart = busio.UART(board.GP4, board.GP5, baudrate=9600) #tx pin, rx pin
while True:
    # input()
    cam.capture(bitmap)
    com = getCOM(bitmap,numRows,edgeKernel,smoothingKernel)
    value_str = str(com)+'\n'
    uart.write(value_str.encode())
    print(value_str)
    bitmap.dirty()
    display.refresh(minimum_frames_per_second=0)
    t1 = time.monotonic_ns()
    # print("fps", 1e9 / (t1 - t0))
    t0 = t1