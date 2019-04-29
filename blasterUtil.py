#========================================
#    author: Changlong.Zang
#      mail: zclongpop123@163.com
#      time: Fri Apr 12 17:20:19 2019
#========================================
import os, re, string
import maya.cmds as mc
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
def get_current_camera():
    '''
    '''
    camera = 'persp'

    panels = mc.getPanel(vis=True)
    if mc.getPanel(wf=True):
        panels.insert(0, mc.getPanel(wf=True))

    for panel in panels:
        if panel not in mc.getPanel(typ='modelPanel'):
            continue

        cam = mc.modelPanel(panel, q=True, cam=True)
        if mc.nodeType(cam) == 'transform':
            camera = cam
        else:
            camera = mc.listRelatives(cam, p=True)[0]
        break

    return camera



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
