#========================================
#    author: Changlong.Zang
#      mail: zclongpop123@163.com
#      time: Fri Apr 12 13:41:08 2019
#========================================
import os, subprocess, getpass, time
import maya.cmds as mc
import maya.mel as mel
import blasterEnv, blasterUtil
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
def playblast(output, start_frame=None, end_frame=None, artist=None, view=True):
    '''
    '''
    # - make blast image dir  | Exp: C:/Users/zangchanglong/Documents/playblast
    if not os.path.isdir(blasterEnv.IMAGE_PATH):
        os.makedirs(blasterEnv.IMAGE_PATH)

    #- close all camera gate
    for cam in mc.ls(typ='camera'):
        mc.camera(cam, e=True, displayFilmGate=False, displayResolution=False, overscan=1.0)

    if start_frame is None:
        start_frame = mc.playbackOptions(q=True, ast=True)

    if end_frame is None:
        end_frame = mc.playbackOptions(q=True, aet=True)

    blast_prefix = os.path.join(blasterEnv.IMAGE_PATH, time.strftime("%b%d%H%M%S", time.localtime()))
    mc.playblast(fmt='image',
                 compression = blasterEnv.IMAGE_FMT,

                 fp=4,
                 percent = 100,
                 quality = 100,
                 viewer = False,
                 clearCache = True,
                 showOrnaments = False,

                 startTime = start_frame,
                 endTime = end_frame,

                 width = mc.getAttr('defaultResolution.width'),
                 height = mc.getAttr('defaultResolution.height'),

                 filename = blast_prefix)

    #-
    camera = blasterUtil.get_current_camera()
    focal  = str(mc.getAttr('{0}.focalLength'.format(camera)))
    if not artist:
        artist = getpass.getuser()

    sound_node = mc.timeControl(mel.eval('string $temp = $gPlayBackSlider'), q=True, s=True)
    sound_file = 'audio.wav'
    if sound_node:
        sound_file = mc.sound(sound_node, q=True, f=True)

    #-
    text_process_cmds = [blasterEnv.PROCESSOR, 'add_text', '{0}.*.{1}'.format(blast_prefix, blasterEnv.IMAGE_FMT), camera, focal, artist, str(int(start_frame))]
    subprocess.check_call(' '.join(text_process_cmds))

    #-
    video_process_cmds = [blasterEnv.PROCESSOR, 'comp_to_video', '{0}.#.{1}'.format(blast_prefix, blasterEnv.IMAGE_FMT), '--output {0}'.format(output), '--audio {0}'.format(sound_file), '--view-output {0}'.format(int(view))]
    subprocess.check_call(' '.join(video_process_cmds))    

    return True    
