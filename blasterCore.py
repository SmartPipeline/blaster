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
                 offScreen = True,

                 startTime = start_frame,
                 endTime = end_frame,
                 framePadding = FRAME_PADDING,

                 width = mc.getAttr('defaultResolution.width'),
                 height = mc.getAttr('defaultResolution.height'),

                 filename = BLAST_PREFIX)


    #- add mask and text
    camera = blasterUtil.get_current_camera()
    focal  = str(mc.getAttr('{0}.focalLength'.format(camera)))
    if not artist:
        artist = getpass.getuser()

    image_path_pattern = '{0}.{1}.{2}'.format(BLAST_PREFIX, '?'*FRAME_PADDING, blasterEnv.BLAST_IMAGE_FMT)
    text_process_cmds  = [blasterEnv.PROCESSOR, 'add_text', image_path_pattern, camera, focal, artist]
    subprocess.check_call(' '.join(text_process_cmds))

    #- comp images to video
    sound_node = mc.timeControl(mel.eval('string $temp = $gPlayBackSlider'), q=True, s=True)
    sound_file = 'audio.wav'
    if sound_node:
        sound_file = mc.sound(sound_node, q=True, f=True)

    sequence = image_path_pattern.replace('?', '@')
    if os.path.isfile(sound_file):
        sequence = '[ {0} {1} ]'.format(sequence, sound_file)

    rvio_cmds = [blasterEnv.RVIO_BIN,
                 sequence,
                 '-outfps {0}'.format(blasterEnv.VIDEO_FPS),
                 '-codec {0}'.format(blasterEnv.VIDEO_CODEC),
                 '-outparams vcc:bf=0',
                 '-quality 1.0',
                 '-o {0}'.format(output),
                 '-rthreads {0}'.format(blasterEnv.RV_R_THREADING),
                 '-wthreads {0}'.format(blasterEnv.RV_W_TRHEADING),
                 '-v']    

    subprocess.check_call(' '.join(rvio_cmds))

    #- auto delete images
    if blasterEnv.AUTO_DELETE_IMAGE:
        images = glob.glob(image_path_pattern)
        for img in images:
            os.remove(img)

    #- view output
    if view:
        rv_view_cmds = [blasterEnv.RV_BIN, output]
        subprocess.Popen(' '.join(rv_view_cmds))

    return True    
