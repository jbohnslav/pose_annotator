from collections import OrderedDict
from copy import deepcopy
from functools import partial
import os
import sys

import numpy as np
from omegaconf import OmegaConf, DictConfig
import pandas as pd
from PySide2 import QtCore, QtWidgets, QtGui

from pose_annotator.gui.mainwindow import Ui_MainWindow
from pose_annotator.gui.custom_widgets import KeypointGroup, KeypointButtons, simple_popup_question
from pose_annotator import utils

image_endings = ['.png', '.jpg', '.tiff', '.tif', '.bmp']
video_endings = ['.mov', '.mp4', '.avi']


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, cfg: DictConfig):
        super().__init__()
        
        self.cfg = cfg
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('Pose Annotator')
        
        self.player = self.ui.widget
        # for convenience
        self.scene = self.player.scene
        # self.player.videoView.initialize_image('/media/jim/DATA_SSD/armo/dataset_for_labeling/images/SS21_190508_140054_002526/SS21_190508_140054_002526_right_post_l.png')
        # self.player.videoView.initialize_video('/media/jim/DATA_SSD/armo/dataset_for_labeling/images/SS21_190508_140054_002526')
        
        keys = OmegaConf.to_container(cfg.keypoints)
        self.keypoint_dict = OrderedDict({key: [] for key in keys})
        # self.keypoint_dict = {key: [] for key in keys}
        self.keypoints = None
        
        self.keypoints = KeypointGroup(self.keypoint_dict, self.player.videoView.scene, 
                                       parent=self.player, colormap=self.cfg.colormap, radius=self.cfg.radius)
        
        self.keypoint_selector = KeypointButtons(keys, colormap=cfg.colormap, parent=self)
        self.ui.verticalLayout_2.addWidget(self.keypoint_selector)
        
        # should do this somewhere else
        self.ui.keypoints_box.setStyleSheet('QGroupBox {background-color: rgb(80,80,80)}'
                                            'QGroupBox::title {background: transparent}')
        self.ui.toolbox.setStyleSheet('QGroupBox {background-color: rgb(80,80,80)}'
                                            'QGroupBox::title {background: transparent}')
        # self.ui.keypoints_box.title().setStyleSheet('background: transparent')
        
        # connect signals and slots
        self.scene.click.connect(self.keypoints.receive_click)
        self.scene.move.connect(self.keypoints.receive_move)
        self.scene.release.connect(self.keypoints.receive_release)
        self.keypoints.data.connect(self.update_data_buffer)
        
        # these link the keypoint click area with the toolbar on the left
        self.keypoint_selector.selected.connect(self.keypoints.set_selected)
        self.keypoints.selected.connect(self.keypoint_selector.set_selected)
        self.player.videoView.frameNum.connect(self.update_framenum)
        # menu buttons
        self.ui.actionOpen_image.triggered.connect(self.open_image_file)
        self.ui.actionOpen_image_directory.triggered.connect(self.open_image_directory)
        self.ui.actionOpen_video.triggered.connect(self.open_video)
        
        # hotkeys
        save_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+S'), self)
        save_shortcut.activated.connect(self.save)
        nextframe_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Right'), self)
        nextframe_shortcut.activated.connect(self.player.videoView.next_frame)
        prevframe_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Left'), self)
        prevframe_shortcut.activated.connect(self.player.videoView.previous_frame)
        down_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Down'), self)
        down_shortcut.activated.connect(self.keypoints.increment_selected)
        space_shorcut = QtWidgets.QShortcut(QtGui.QKeySequence('Space'), self)
        space_shorcut.activated.connect(self.keypoints.increment_selected)
        up_shorcut = QtWidgets.QShortcut(QtGui.QKeySequence('Up'), self)
        up_shorcut.activated.connect(self.keypoints.decrement_selected)
        delete_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Delete'), self)
        delete_shortcut.activated.connect(self.keypoints.clear_selected)
        backspace_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Backspace'), self)
        backspace_shortcut.activated.connect(self.keypoints.clear_selected)
        
        self.data = []
        self.saved = True
        self.framenum = 0
        self.save_loc = None
        # self.initialize_save_loc()
        self.save_filename = None
        if cfg.path is not None:
            assert os.path.exists(cfg.path)
            ending = os.path.splitext(cfg.path)[1]
            if ending.lower() in image_endings:
                filetype = 'image'
            elif ending.lower() in video_endings:
                filetype = 'video'
            elif os.path.isdir(cfg.path):
                filetype = 'video'
            else:
                raise ValueError('filetype of input not known: {}'.format(cfg.path))
            self.initialize_new_file(cfg.path, filetype)
        
        self.show()
        
    def get_save_loc(self):
        saveloc = self.cfg.save_loc
        if saveloc is not None:
            assert os.path.isdir(saveloc)
        return saveloc
        
    def open_file_browser(self, filestring, prompt, filetype):
        options = QtWidgets.QFileDialog.Options()
        # filestring = 'VideoReader files (*.h5 *.avi *.mp4 *.png *.jpg *.mov)'
        # prompt = "Click on video to open. If a directory full of images, click any image"
        if filetype == 'file':
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, prompt, '',
                                                    filestring, options=options)
            if not os.path.isfile(filename):
                raise ValueError('file does not exist: {}'.format(filename))
        elif filetype == 'directory':
            filename = QtWidgets.QFileDialog.getExistingDirectory(self, prompt, '', options=options)
            if not os.path.isdir(filename):
                raise ValueError('directory does not exist: {}'.format(filename))
        else:
            raise NotImplementedError
        
        return filename
    
    def open_image_file(self):
        filestring = 'Image files (*.jpg *.png *.tif *.bmp)'
        prompt = 'Click an image file to open'
        filename = self.open_file_browser(filestring, prompt, 'file')
        
        self.initialize_new_file(filename, 'image')
        
    def open_video(self):
        filestring = 'VideoReader files (*.h5 *.avi *.mp4 *.png *.jpg *.mov)'
        prompt = 'Click a video file to open'
        filename = self.open_file_browser(filestring, prompt, 'file')
        
        self.initialize_new_file(filename, 'video')
        
    def open_image_directory(self):
        filestring = ''
        prompt = 'Click a directory containing image files'
        filename = self.open_file_browser(filestring, prompt, 'directory')
        
        self.initialize_new_file(filename, 'video')
        
    def initialize_new_file(self, filename, filetype):
        self.prompt_for_save()
        
        # hack for startup: we will open on frame zero, so have to have a 1-element list when initialize-image or 
        # initialize-video is called, because that will trigger the "update_framenum" slot
        self.data = [deepcopy(self.keypoint_dict) for i in range(1)]
        
        if filetype == 'image':
            self.player.videoView.initialize_image(filename)
            N = 1
        elif filetype == 'video':
            self.player.videoView.initialize_video(filename)
            N = len(self.player.videoView.vid)
        else:
            raise ValueError('unknown file type: {}'.format(filetype))
        
        save_loc = self.get_save_loc()
        if save_loc is None:
            save_loc = os.path.dirname(filename)
        
        self.save_filename = os.path.join(save_loc, 
                                          os.path.splitext(os.path.basename(filename))[0] + '_keypoints.csv')
        self.data = [deepcopy(self.keypoint_dict) for i in range(N)]
        if os.path.isfile(self.save_filename):
            self.load(self.save_filename)
        
        
    def initialize_keypoint_group(self, keypoints: dict):
        self.clear_keypoints()
        self.keypoints.set_data(keypoints)
        # self.keypoints = KeypointGroup(keypoints, self.player.videoView.scene, 
        #                                parent=self.player, colormap=self.cfg.colormap, radius=self.cfg.radius)
        

    def clear_keypoints(self):
        if self.keypoints is not None:
            # print('clearing')
            self.keypoints.clear_data()
        # else:
        #     print('not clearing')
    
    @QtCore.Slot(dict)
    def update_data_buffer(self, data):
        # without copying, could have an issue where the underlying keypoint gui state changes. we want to only 
        # keep the real data
        self.data[self.framenum] = deepcopy(data)
        self.saved = False
        # print(self.data)
        # print(data)
        # print(self.keypoint_dict)
            
    @QtCore.Slot(int)
    def update_framenum(self, framenum, force: bool=False):
        if self.framenum != framenum or force:
            # convenience: rather than dig this value out of the widgets, the app will have this attribute
            self.framenum = framenum
            keypoints = self.data[framenum]
            self.initialize_keypoint_group(keypoints)
            
            # radio button will be set to the first keypoint that hasn't been placed on this frame
            first_nonzero = len(keypoints) - 1
            for i, (key, value) in enumerate(keypoints.items()):
                if len(value) == 0 or np.sum(np.isnan(value)) > 0 or value is None:
                    if i < first_nonzero:
                        first_nonzero = i
                        break

            self.keypoint_selector.set_selected(first_nonzero)
    
    
    def save(self):
        # has_any_data = []
        # for element in self.data:
        #     frame_has_data = False
        #     for key, value in element.items():
        #         if len(value) > 0:
        #             frame_has_data = True
        #             break
        #     has_any_data.append(frame_has_data)
        
        # data = {}
        # for i, element in enumerate(self.data):
        #     row = {}
        #     if not has_any_data[i]:
        #         continue
        #     for key, value in element.items():
        #         if value is None:
        #             value = [np.nan, np.nan, 0]
        #         row[key + '_x'] = value[0]
        #         row[key + '_y'] = value[1]
        #         row[key + '_p'] = 1
        #     data[i] = row
            
        # df = pd.DataFrame(data)
        # # switch rows and columns
        # df = df.T
        df = utils.convert_data_to_df(self.data)
        df.to_csv(self.save_filename)
        print('saving to {}'.format(self.save_filename))
        return df
    
    def load(self, filename):
        assert os.path.isfile(filename)
        print('loading from {}'.format(filename))
        df = pd.read_csv(filename, index_col=0)
        # data is initialized when we load our video
        data = utils.convert_df_to_data(df, len(self.data), self.keypoint_dict)
        df.head()
        self.data = data
        # do this to re-load the zeroth frame with data
        self.update_framenum(0, force=True)
            
    def prompt_for_save(self):
        if self.saved:
            return
        if simple_popup_question(self, 'You have unsaved changes. Do you want to save?'):
            self.save()
        
        
            
def set_style(app):
    # https://www.wenzhaodesign.com/devblog/python-pyside2-simple-dark-theme
    # button from here https://github.com/persepolisdm/persepolis/blob/master/persepolis/gui/palettes.py
    app.setStyle(QtWidgets.QStyleFactory.create("fusion"))

    darktheme = QtGui.QPalette()
    darktheme.setColor(QtGui.QPalette.Window, QtGui.QColor(45, 45, 45))
    darktheme.setColor(QtGui.QPalette.WindowText, QtGui.QColor(222, 222, 222))
    darktheme.setColor(QtGui.QPalette.Button, QtGui.QColor(45, 45, 45))
    darktheme.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(222, 222, 222))
    darktheme.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(222, 222, 222))
    # darktheme.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(0, 222, 0))
    darktheme.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(222, 222, 222))
    darktheme.setColor(QtGui.QPalette.Highlight, QtGui.QColor(45, 45, 45))
    darktheme.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Light, QtGui.QColor(60, 60, 60))
    darktheme.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, QtGui.QColor(50, 50, 50))
    darktheme.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText,
                       QtGui.QColor(111, 111, 111))
    darktheme.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QColor(122, 118, 113))
    darktheme.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText,
                       QtGui.QColor(122, 118, 113))
    darktheme.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Base, QtGui.QColor(32, 32, 32))
    app.setPalette(darktheme)
    return app

def run():
    app = QtWidgets.QApplication(sys.argv)
    app = set_style(app)
    
    default_path = os.path.join(os.path.dirname(__file__), 'default_config.yaml')
    
    default = OmegaConf.load(default_path)
    cli = OmegaConf.from_cli()
    cfg = OmegaConf.merge(default, cli)
    OmegaConf.set_struct(cfg, True)

    window = MainWindow(cfg)
    window.resize(1024, 768)
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    # log.info('CWD: {}'.format(os.getcwd()))
    # log.info('Configuration used: {}'.format(cfg.pretty()))
    run()
    