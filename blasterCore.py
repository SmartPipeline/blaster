# coding: utf-8
#========================================
#    author: Changlong.Zang
#      mail: zclongpop123@163.com
#      time: Fri Apr 12 13:41:08 2019
#========================================
import os
import time
import math
import uuid
import glob
import json
import getpass
import subprocess
import maya.cmds as mc
import maya.mel as mel
import blasterEnv, blasterUtil
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
def playblast(output, start_frame=None, end_frame=None, artist=None, view=True):
    '''
    '''
    # - make blast image dir  | Exp: C:/Users/zangchanglong/Documents/playblast
    if not os.path.isdir(blasterEnv.BLAST_IMAGE_DIR):
        os.makedirs(blasterEnv.BLAST_IMAGE_DIR)

    #- close all camera gate
    for cam in mc.ls(typ='camera'):
        mc.camera(cam, e=True, displayFilmGate=False, displayResolution=False, overscan=1.0)

    #- get time range
    if start_frame is None:
        start_frame = mc.playbackOptions(q=True, ast=True)

    if end_frame is None:
        end_frame = mc.playbackOptions(q=True, aet=True)

    #- playblast images
    BLAST_PREFIX  = os.path.join(blasterEnv.BLAST_IMAGE_DIR, '{0}_{1}'.format(time.strftime("%b%d%H%M%S", time.localtime()), uuid.uuid4().hex[::4].upper()))
    FRAME_PADDING = int(math.ceil(math.log(max(start_frame, end_frame)+1, 10)))
    mc.playblast(filename = BLAST_PREFIX,
                 fmt = 'image',
                 compression = blasterEnv.BLAST_IMAGE_FMT,

                 width = mc.getAttr('defaultResolution.width'),
                 height = mc.getAttr('defaultResolution.height'),

                 startTime = start_frame,
                 endTime = end_frame,
                 framePadding = FRAME_PADDING,

                 percent = 100,
                 quality = 100,

                 viewer = False,
                 offScreen = True,
                 clearCache = True,
                 showOrnaments = False)

    #- getting infomation
    image_pattern = '{0}.{1}.{2}'.format(BLAST_PREFIX, '?'*FRAME_PADDING, blasterEnv.BLAST_IMAGE_FMT)
    camera = blasterUtil.get_current_camera()
    focal  = mc.getAttr('{0}.focalLength'.format(camera))
    if not artist:
        artist = getpass.getuser()
    sound_node = mc.timeControl(mel.eval('string $temp = $gPlayBackSlider'), q=True, s=True)
    sound_file = 'audio.wav'
    if sound_node:
        sound_file = mc.sound(sound_node, q=True, f=True)

    #- create job-file
    info_data = {
        'ImagePattern': os.path.normpath(image_pattern),
        'Camera': str(camera),
        'Focal': str(focal),
        'Audio': os.path.normpath(sound_file),
        'Output': output,
        'Artist': artist
    }
    info_file = '{0}.json'.format(BLAST_PREFIX)
    with open(info_file, 'w') as f:
        json.dump(info_data, f, indent=4)

    #- call comp process
    comp_process_cmds  = [blasterEnv.PROCESSOR,
                          'comp_blast_video',
                          info_file]
    subprocess.check_call(' '.join(comp_process_cmds).encode('utf-8'))

    #- auto delete images
    if blasterEnv.AUTO_DELETE_IMAGE:
        images = glob.glob(image_pattern)
        for img in images:
            os.remove(img)

    #- delete job file
    if os.path.isfile(info_file):
        os.remove(info_file)

    #- view output
    if view:
        rv_view_cmds = [blasterEnv.RV_BIN, output.encode('utf-8')]
        subprocess.Popen(' '.join(rv_view_cmds))

    return True    
