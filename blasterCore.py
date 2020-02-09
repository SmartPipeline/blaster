# coding: utf-8
#========================================
#    author: Changlong.Zang
#      mail: zclongpop123@163.com
#      time: Fri Apr 12 13:41:08 2019
#========================================
import os, re, time, math, uuid, glob, json, yaml
import getpass, tempfile, subprocess
import maya.cmds as mc
import maya.mel as mel
import blasterUtil

this_dir = os.path.dirname(__file__)
with open(os.path.join(this_dir, 'config.yml'), 'r') as f:
    config = yaml.load(f, Loader=yaml.Loader) 
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
def playblast(output, start_frame=None, end_frame=None, artist=None, view=True):
    '''
    '''
    # - make blast image dir  | Exp: C:/Users/zangchanglong/Documents/playblast
    image_dir = config['image_dir'].format(os.path.dirname(tempfile.mktemp()))
    if not os.path.isdir(image_dir):
        os.makedirs(image_dir)

    #- close all camera gate
    for cam in mc.ls(typ='camera'):
        mc.camera(cam, e=True, dfg=False, dfo=False, dfp=False, dr=False, dsa=True, dst=False, overscan=1.0)

    #- get time range
    if start_frame is None:
        start_frame = mc.playbackOptions(q=True, ast=True)

    if end_frame is None:
        end_frame = mc.playbackOptions(q=True, aet=True)

    #- playblast images
    BLAST_PREFIX  = os.path.join(image_dir, '{0}_{1}'.format(time.strftime("%b%d%H%M%S", time.localtime()), uuid.uuid4().hex[::4].upper()))
    FRAME_PADDING = int(math.ceil(math.log(max(start_frame, end_frame)+1, 10)))
    mc.playblast(filename = BLAST_PREFIX,
                 fmt = 'image',
                 compression = config['image_fmt'],

                 width  = config['width'],
                 height = config['height'],

                 startTime = start_frame,
                 endTime   = end_frame,
                 framePadding = FRAME_PADDING,

                 percent = 100,
                 quality = 100,

                 viewer = False,
                 offScreen = True,
                 clearCache = True,
                 showOrnaments = False)

    #- getting infomation
    image_pattern = '{0}.{1}.{2}'.format(BLAST_PREFIX, '?'*FRAME_PADDING, config['image_fmt'])
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
    comp_process_cmds  = [config['processor'].format(this_dir), 'comp_blast_video', info_file]
    print comp_process_cmds
    subprocess.check_call(' '.join(comp_process_cmds).encode('utf-8'))

    #- auto delete images
    if config['auto_delete_image']:
        images = glob.glob(image_pattern)
        for img in images:
            os.remove(img)

    #- delete job file
    if os.path.isfile(info_file):
        os.remove(info_file)

    #- view output
    if view and os.path.isfile(config['rv_bin']):
        rv_view_cmds = [config['rv_bin'], output.encode('utf-8')]
        subprocess.Popen(' '.join(rv_view_cmds))

    return True    




def batch_playblast(path):
    '''
    '''
    for filePath in glob.glob('{0}/*.mb'.format(path)):

        #- open file
        if re.search('\.ma$', filePath):
            f_type = 'mayaAscii'

        elif re.search('\.mb$', filePath):
            f_type = 'mayaBinary'

        else:
            continue

        mc.file(filePath, typ=f_type, o=True, f=True, prompt=False, ignoreVersion=True)


        #- checking lost reference files
        unload_refs = [ref for ref in mc.file(q=True, r=True) if not mc.referenceQuery(ref, il=True)]
        lost_refs   = [ref for ref in unload_refs if not os.path.isfile(ref.split('{')[0])]
        if lost_refs:
            continue

        #- checking cameras
        cameras = [cam for cam in mc.listRelatives(mc.ls(cameras=True), p=True) or list()]
        cameras = [cam for cam in cameras if re.match('Ep', cam, re.I)]
        cameras.append('persp')

        #- set panels
        panels = mc.getPanel(vis=True)
        for pan in panels:
            if pan in mc.getPanel(typ='modelPanel'):
                mc.modelEditor(pan, e=True, alo=False)
                mc.modelEditor(pan, e=True, cam=cameras[0], pm=True, av=True, da='smoothShaded')
                break

        #- blast
        vide_name = '{0}.mov'.format(os.path.splitext(filePath)[0])
        playblast(vide_name, view=False)

    return True
