#========================================
#    author: Changlong.Zang
#      mail: zclongpop123@163.com
#      time: Fri Apr 12 17:20:19 2019
#========================================
import os, re, string
import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as OpenMaya
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
def get_current_camera():
    '''
    '''
    camera = 'persp'

    if OpenMaya.MGlobal.mayaState() == OpenMaya.MGlobal.kInteractive:
        panels = mc.getPanel(vis=True)
        for pan in panels:
            if pan not in mc.getPanel(typ='modelPanel'):
                continue

            cam = mc.modelPanel(pan, q=True, cam=True)
            if mc.nodeType(cam) != 'transform':
                cam = mc.listRelatives(cam, p=True)[0]

            if cam not in ('persp', 'top', 'front', 'side'):
                camera = cam
                mc.modelEditor(pan, e=True, alo=False)
                mc.modelEditor(pan, e=True, pm=True, av=True, da='smoothShaded')                
                break

    else:
        for cam in mc.listRelatives(mc.ls(cameras=True), p=True):
            if mc.getAttr('{0}.renderable'.format(cam)):
                camera = cam
                break

    return camera




def get_current_audio(start_frame=1):
    '''
    '''
    sound_file = 'audio.wav'
    if OpenMaya.MGlobal.mayaState() == OpenMaya.MGlobal.kInteractive:
        sound_node = mc.timeControl(mel.eval('string $temp = $gPlayBackSlider'), q=True, s=True)
        if sound_node:
            sound_file = mc.sound(sound_node, q=True, f=True)

    else:
        audios = mc.ls(typ='audio')
        for audio in audios:
            if mc.getAttr('{0}.offset'.format(audio)) == start_frame:
                sound_file = mc.getAttr('{0}.filename'.format(audio))
    return sound_file




def get_next_version(filePath):
    '''
    '''
    if not os.path.isfile(filePath):
        return filePath

    fname, fextension = os.path.splitext(filePath)
    res = re.search('(?<=_V)\d{3}$', fname)
    if res:
        index = string.zfill(int(res.group()) + 1, 3)
        fname  = re.sub('(?<=_V)\d{3}$', index, fname)
    else:
        fname  = '{0}_V001'.format(fname)

    new_file_path = '{0}{1}'.format(fname.encode('utf-8'), fextension)

    return get_next_version(new_file_path.decode('utf-8'))
