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

    if start_frame is None:
        start_frame = mc.playbackOptions(q=True, ast=True)

    if end_frame is None:
        end_frame = mc.playbackOptions(q=True, aet=True)

    BLAST_PREFIX  = os.path.join(blasterEnv.BLAST_IMAGE_DIR, '{0}_{1}'.format(time.strftime("%b%d%H%M%S", time.localtime()), uuid.uuid4().hex[::4].upper()))
    FRAME_PADDING = int(math.ceil(math.log(max(start_frame, end_frame)+1, 10)))
    mc.playblast(fmt='image',
                 compression = blasterEnv.BLAST_IMAGE_FMT,

                 percent = 100,
                 quality = 100,
                 viewer = False,
                 clearCache = True,
                 showOrnaments = False,

                 startTime = start_frame,
                 endTime = end_frame,
                 framePadding = FRAME_PADDING,

                 width = mc.getAttr('defaultResolution.width'),
                 height = mc.getAttr('defaultResolution.height'),

                 filename = BLAST_PREFIX)

    #-
    camera = blasterUtil.get_current_camera()
    focal  = str(mc.getAttr('{0}.focalLength'.format(camera)))
    if not artist:
        artist = getpass.getuser()

    sound_node = mc.timeControl(mel.eval('string $temp = $gPlayBackSlider'), q=True, s=True)
    sound_file = 'audio.wav'
    if sound_node:
        sound_file = mc.sound(sound_node, q=True, f=True)

    #- add mask and text
    image_path_pattern = '{0}.{1}.{2}'.format(BLAST_PREFIX, '?'*FRAME_PADDING, blasterEnv.BLAST_IMAGE_FMT)
    text_process_cmds  = [blasterEnv.PROCESSOR, 'add_text', image_path_pattern, camera, focal, artist]
    subprocess.check_call(' '.join(text_process_cmds))

    #- comp images to video
    video_process_cmds = [blasterEnv.PROCESSOR, 'comp_to_video', image_path_pattern.replace('?', '@'), '--output {0}'.format(output), '--audio {0}'.format(sound_file), '--view-output {0}'.format(int(view))]
    subprocess.check_call(' '.join(video_process_cmds))

    #- auto delete images
    if blasterEnv.AUTO_DELETE_IMAGE:
        images = glob.glob(image_path_pattern)
        for img in images:
            os.remove(img)    

    return True    
