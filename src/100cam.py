import cv2
import numpy as np
import os
import termios, tty, sys

# Set the number of pixels based on a 4:3 image size.
WIDTH  = 320 
HEIGHT = 240
magnification = 4 

WIDTH  *= magnification
HEIGHT *= magnification

# The coefficient for adjusting vignetting. The optimum value varies dependig on the brightness of the image and other factors
gainFactor      = 0.8  #default = 0.8
distanceFactor  = 0.71 #default = 0.71
cosIndex        = 4    #default = 4

# Parameters for correcting the optical axis of the lens and image sensor of a film camera
offsetRight     = 32 * magnification
offsetUp        = 32 * magnification

# The number of exposures for multiple exposures.
overlay = 1 

# Exposure time
exposureTime = 500 

# Correct for vignetting?
gainFlag = False

# Correct optical axis?
opticalAxisOffset = False

pictureNum = 0

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
capture.set(cv2.CAP_PROP_FPS,1.0)
capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
os.system('v4l2-ctl -d /dev/video0 -c auto_exposure=1')                  # 0:auto 1:manual
os.system('v4l2-ctl -d /dev/video0 -c exposure_time_absolute=' + str(exposureTime))     # 1to10000
os.system('v4l2-ctl -d /dev/video0 -c exposure_metering_mode=0')

# If you need to set more conditions, you may use the following commdands.
#os.system('v4l2-ctl -d /dev/video0 -c exposure_dynamic_framerate=1')
#os.system('v4l2-ctl -d /dev/video0 -c iso_sensitivity_auto=1')          # 0:manual 1:auto
#os.system('v4l2-ctl -d /dev/video0 -c iso_sensitivity=0')               # 0,1,2,3,4
#os.system('v4l2-ctl -d /dev/video0 -c auto_exposure_bias=24')            #-24 to 24
#os.system('v4l2-ctl -d /dev/video0 -c scene_mode=8')
#os.system('v4l2-ctl --set-ctrl auto_exposure=1,exposure_time_absolute=10000,auto_exposure_bias=12,iso_sensitivity=4')

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    ch = sys.stdin.read(1)
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def takePicture():

    global overlay, gainFlag, opticalAxisOffset, offsetRight, offsetUp, pictureNum

    for i in range(overlay):
        print("number of shot = ",i)
        ret, frame = capture.read()
        ret, frame = capture.read()
        if ret is False:
            print("cap error")

        if i == 0:
            frameO = frame/overlay
        else:
            frameO = frameO + frame/overlay

    if opticalAxisOffset == True:
        retsu = np.zeros((moveRight,3))
        gyou = np.zeros((moveUp,moveRight + WIDTH,3))
        frameO = np.insert(frameO,[0],retsu,axis=1)
        frameO = np.insert(frameO,[0],gyou,axis=0)


    if gainFlag == True:
        h, w = frame.shape[:2]
        size = max([h, w])
        print("size = " ,size)

        x = np.linspace(-w/size, w/size, w)
        y = np.linspace(-h/size, h/size, h)
        xx, yy = np.meshgrid(x, y)
        r = np.sqrt(xx**2 + yy**2)
#        print(r)
        gain = 1 / np.power(np.cos(r * distanceFactor), cosIndex) * gainFactor
        gainmap = np.dstack([gain, gain, gain])
#        print(gainmap)
#        frame = frame**2.2
        frameO = np.clip(frameO * gainmap, 0., 255.0)
#        frame = frame**(1/2.2)

    cv2.imwrite("pic" + str(pictureNum) + ".jpg", frameO)
    pictureNum += 1
    print("Next = " + str(pictureNum) + " push [s] to take pic / [q] to quit")

    if capture.isOpened() is False:
        raise IOError


print("ready")
print("Next = " + str(pictureNum) + " push [s] to take pic / [q] to quit")
while True:
    key = getch()

    if key == "q":
        break
    elif key == "s":
        print("shutter!")
        takePicture()
    

capture.release()

