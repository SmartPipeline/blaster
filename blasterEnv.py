#========================================
#    author: Changlong.Zang
#      mail: zclongpop123@163.com
#      time: Fri Apr 12 13:44:33 2019
#========================================
import os
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
PROCESSOR  = os.path.join(os.path.dirname(__file__), 'processor.exe')

IMAGE_PATH = os.path.expanduser('~/playblast/temp')

IMAGE_FMT  = 'tga'


RVIO_BIN   = 'C:/Program Files/Shotgun/RV-7.1.1/bin/rvio_hw.exe'

RV_BIN     = 'C:/Program Files/Shotgun/RV-7.1.1/bin/rv.exe'


MASK_COLOR = (0, 0, 0)

TEXT_FONT  = os.path.join(os.path.dirname(__file__), 'resource', 'font', 'MONACO.TTF')

TEXT_SIZE  = 25

TEXT_COLOR = (255, 255, 255)

TEXT_BOUND = 12


VIDEO_FPS  = 24

VIDEO_CODEC = 'libx264'
