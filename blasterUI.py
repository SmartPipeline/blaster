#========================================
#    author: Changlong.Zang
#      mail: zclongpop123@163.com
#      time: Fri Apr 12 15:44:55 2019
#========================================
import os, re, getpass
from PySide2 import QtWidgets, QtCore
import maya.OpenMayaUI as OpenMayaUI
import maya.cmds as mc
import shiboken2
import blasterQt, blasterCore, blasterUtil
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
def get_maya_window():
    '''
    '''
    maya_window = OpenMayaUI.MQtUtil.mainWindow()
    if maya_window:
        return shiboken2.wrapInstance(long(maya_window), QtWidgets.QMainWindow)


class BlasterUI(QtWidgets.QMainWindow, blasterQt.Ui_BLASTER_WINDOW):
    '''
    '''
    def __init__(self, parent=get_maya_window()):
        '''
        '''
        super(BlasterUI, self).__init__(parent)
        self.setupUi(self)
        #-
        self.let_artist.setText(getpass.getuser())
        self.on_cbx_updateversion_clicked(self.cbx_updateversion.isChecked())


    def showEvent(self, event):
        '''
        '''
        self.on_cbx_updateversion_clicked(self.cbx_updateversion.isChecked())


    @QtCore.Slot(str)
    def on_let_output_textChanged(self, args=None):
        '''
        '''
        if self.cbx_updateversion.isChecked():
            self.on_cbx_updateversion_clicked(True)


    @QtCore.Slot(bool)
    def on_cbx_updateversion_clicked(self, args=None):
        '''
        '''
        cam = blasterUtil.get_current_camera()
        if re.search('SC\d{2}_S\d{2}_', cam):
            cam = re.sub('_S\d{2}_', '_', cam)

        self.let_videoname.setText('{0}_V001.mov'.format(cam))
        if self.cbx_updateversion.isChecked():
            if not str(self.let_output.text()):
                return
            filePath = os.path.join(str(self.let_output.text()), '{0}_V001.mov'.format(cam))
            self.let_videoname.setText(os.path.basename(blasterUtil.get_next_version(filePath)))


    @QtCore.Slot(bool)
    def on_btn_setoutputpath_clicked(self, args=None):
        '''
        '''
        filePath = mc.fileDialog2(fm=3, okc='Select', startingDirectory=os.path.dirname(mc.file(q=True, sn=True)))
        if filePath:
            self.let_output.setText(filePath[0])


    @QtCore.Slot(bool)
    def on_btn_playblast_clicked(self, args=None):
        '''
        '''
        if self.cbx_updateversion.isChecked():
            self.on_cbx_updateversion_clicked(True)

        output = os.path.join(str(self.let_output.text()), str(self.let_videoname.text()))
        blasterCore.playblast(output, artist=str(self.let_artist.text()), view=self.cbx_viewoutput.isChecked())



def UI():
    wnd = get_maya_window().findChild(QtWidgets.QMainWindow, 'BLASTER_WINDOW')
    if wnd:
        wnd.show()
        wnd.showNormal()
        return

    wnd = BlasterUI()
    wnd.show()
