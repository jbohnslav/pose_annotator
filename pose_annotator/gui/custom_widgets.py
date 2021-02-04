from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import (QGroupBox, QFormLayout, QLabel, QLineEdit, QVBoxLayout, QWidget, QMainWindow)
from PySide2.QtCore import Qt, Signal, Slot, QPoint
from PySide2.QtGui import QPainter, QBrush, QPen, QPixmap, QColor
from typing import Union, Tuple
import os
import warnings

import cv2
from vidio import VideoReader
import numpy as np
import matplotlib.pyplot as plt


def numpy_to_qpixmap(image: np.ndarray) -> QtGui.QPixmap:
    if isinstance(image.flat[0], np.floating):
        image = float_to_uint8(image)
    H, W, C = int(image.shape[0]), int(image.shape[1]), int(image.shape[2])
    if C == 4:
        format = QtGui.QImage.Format_RGBA8888
    elif C == 3:
        format = QtGui.QImage.Format_RGB888
    else:
        raise ValueError('Aberrant number of channels: {}'.format(C))
    qpixmap = QtGui.QPixmap(QtGui.QImage(image, W,
                                         H, image.strides[0],
                                         format))
    # print(type(qpixmap))
    return qpixmap


def float_to_uint8(image: np.ndarray) -> np.ndarray:
    if image.dtype == np.float:
        image = (image * 255).clip(min=0, max=255).astype(np.uint8)
    # print(image)
    return image


def initializer(nframes: int):
    print('initialized with {}'.format(nframes))


class ClickableScene(QtWidgets.QGraphicsScene):
    click = QtCore.Signal(QtGui.QMouseEvent)
    move = QtCore.Signal(QtGui.QMouseEvent)
    release = QtCore.Signal(QtGui.QMouseEvent)
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def mousePressEvent(self, event):
        if event.buttons():
            self.click.emit(event)
            event.ignore()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.move.emit(event)
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        self.release.emit(event)
        super().mouseReleaseEvent(event)
        

class VideoFrame(QtWidgets.QGraphicsView):
    frameNum = Signal(int)
    initialized = Signal(int)
    
    def __init__(self, videoFile: Union[str, os.PathLike] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.videoView = QtWidgets.QGraphicsView()
        self.scene = ClickableScene(self) # QtWidgets.QGraphicsScene(self)
        # self.scene = CroppingOverlay(parent=self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self.scene.addItem(self._photo)

        # self.videoView.setScene(self.scene)
        self.setScene(self.scene)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(640, 480))
        # self.setObjectName("videoView")
        
        self.vid = None
        
        if videoFile is not None:
            self.initialize_video(videoFile)
            self.update()
        self.setStyleSheet("background:transparent;")
        
    
    def initialize_image(self, imagefile: Union[str, os.PathLike])    : 
        self.videofile = imagefile
        assert os.path.isfile(imagefile)
        
        im = cv2.imread(imagefile, 1)
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        self.frame = im

        self.initialized.emit(1)

        # the frame in the videoreader is the position of the reader. If you've read frame 0, the current reader
        # position is 1. This makes cv2.CAP_PROP_POS_FRAMES match vid.fnum. However, we want to keep track of our
        # currently displayed image, which is fnum - 1
        self.current_fnum = 0
        # print('new fnum: {}'.format(self.current_fnum))
        self.show_image(self.frame)
        self.frameNum.emit(self.current_fnum)

        # print(self.palette())

    def initialize_video(self, videofile: Union[str, os.PathLike]):
        if self.vid is not None:
            self.vid.close()
            # if hasattr(self.vid, 'cap'):
            #     self.vid.cap.release()
        self.videofile = videofile
        self.vid = VideoReader(videofile)
        # self.frame = next(self.vid)
        self.initialized.emit(len(self.vid))
        # there was a bug where sometimes subsequent videos with the same frame would not update the image
        self.update_frame(0, force_update=True)

    def update_frame(self, value, force_update: bool=False):
        # print('updating')
        # print('update to: {}'.format(value))
        # print(self.current_fnum)
        # previous_frame = self.current_fnum
        if not hasattr(self, 'vid'):
            return
        value = int(value)
        if hasattr(self, 'current_fnum'):
            if self.current_fnum == value and not force_update:
                # print('already there')
                return
        if value < 0:
            # warnings.warn('Desired frame less than 0: {}'.format(value))
            value = 0
        if value >= self.vid.nframes:
            # warnings.warn('Desired frame beyond maximum: {}'.format(self.vid.nframes))
            value = self.vid.nframes - 1

        self.frame = self.vid[value]

        # the frame in the videoreader is the position of the reader. If you've read frame 0, the current reader
        # position is 1. This makes cv2.CAP_PROP_POS_FRAMES match vid.fnum. However, we want to keep track of our
        # currently displayed image, which is fnum - 1
        self.current_fnum = self.vid.fnum - 1
        # print('new fnum: {}'.format(self.current_fnum))
        self.show_image(self.frame)
        self.frameNum.emit(self.current_fnum)
        
    def next_frame(self):
        self.update_frame(self.current_fnum + 1)

    def previous_frame(self):
        self.update_frame(self.current_fnum - 1)

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.scene.setSceneRect(rect)
            # if self.hasPhoto():
            unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            viewrect = self.viewport().rect()
            scenerect = self.transform().mapRect(rect)
            factor = min(viewrect.width() / scenerect.width(),
                         viewrect.height() / scenerect.height())
            # print(factor, viewrect, scenerect)
            self.scale(factor, factor)
            self._zoom = 0

    def adjust_aspect_ratio(self):
        if not hasattr(self, 'vid'):
            raise ValueError('Trying to set GraphicsView aspect ratio before video loaded.')
        if not hasattr(self.vid, 'width'):
            self.vid.width, self.vid.height = self.frame.shape[1], self.frame.shape[0]
        video_aspect = self.vid.width / self.vid.height
        H, W = self.height(), self.width()
        new_width = video_aspect * H
        if new_width < W:
            self.setFixedWidth(new_width)
        new_height = W / self.vid.width * self.vid.height
        if new_height < H:
            self.setFixedHeight(new_height)

    def show_image(self, array):
        qpixmap = numpy_to_qpixmap(array)
        # THIS LINE CHANGES THE SCENE WIDTH AND HEIGHT
        self._photo.setPixmap(qpixmap)

        self.fitInView()
        self.update()
        # self.show()

    def resizeEvent(self, event):
        if hasattr(self, 'vid'):
            self.fitInView()


class ScrollbarWithText(QtWidgets.QWidget):
    position = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.horizontalWidget = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalWidget.sizePolicy().hasHeightForWidth())
        self.horizontalWidget.setSizePolicy(sizePolicy)
        self.horizontalWidget.setMaximumSize(QtCore.QSize(16777215, 25))
        self.horizontalWidget.setObjectName("horizontalWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        self.horizontalLayout.setObjectName("horizontalLayout")

        self.horizontalScrollBar = QtWidgets.QScrollBar(self.horizontalWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalScrollBar.sizePolicy().hasHeightForWidth())
        self.horizontalScrollBar.setSizePolicy(sizePolicy)
        self.horizontalScrollBar.setMaximumSize(QtCore.QSize(16777215, 25))
        self.horizontalScrollBar.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalScrollBar.setObjectName("horizontalScrollBar")
        self.horizontalScrollBar.setPageStep(1)
        
        self.horizontalLayout.addWidget(self.horizontalScrollBar)
        
        self.plainTextEdit = QtWidgets.QLineEdit(self.horizontalWidget)
        
        # self.plainTextEdit = QtWidgets.QPlainTextEdit(self.horizontalWidget)
        self.plainTextEdit.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plainTextEdit.sizePolicy().hasHeightForWidth())
        self.plainTextEdit.setSizePolicy(sizePolicy)
        self.plainTextEdit.setMaximumSize(QtCore.QSize(100, 25))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.plainTextEdit.setFont(font)
        # self.plainTextEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.plainTextEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.horizontalLayout.addWidget(self.plainTextEdit)
        self.setLayout(self.horizontalLayout)
        # self.ui.plainTextEdit.textChanged.connect
        
        self.plainTextEdit.returnPressed.connect(self.text_change)
        self.horizontalScrollBar.sliderMoved.connect(self.scrollbar_change)
        self.horizontalScrollBar.valueChanged.connect(self.scrollbar_change)
        # self.initialize_state(0)
        # self.update_state(0)
        self.update()
        # self.show()

    def sizeHint(self):
        return QtCore.QSize(240, 25)

    def text_change(self):
        value = self.plainTextEdit.text()
        value = int(value)
        self.position.emit(value)

    def scrollbar_change(self):
        value = self.horizontalScrollBar.value()
        self.position.emit(value)

    @Slot(int)
    def update_state(self, value: int):
        if self.plainTextEdit.text() != '{}'.format(value):
            self.plainTextEdit.setText('{}'.format(value))

        if self.horizontalScrollBar.value() != value:
            self.horizontalScrollBar.setValue(value)

    @Slot(int)
    def initialize_state(self, value: int):
        # print('nframes: ', value)
        self.horizontalScrollBar.setMaximum(value - 1)
        self.horizontalScrollBar.setMinimum(0)
        # self.horizontalScrollBar.sliderMoved.connect(self.scrollbar_change)
        # self.horizontalScrollBar.valueChanged.connect(self.scrollbar_change)
        self.horizontalScrollBar.setValue(0)
        self.plainTextEdit.setText('{}'.format(0))
        # self.plainTextEdit.textChanged.connect(self.text_change)
        # self.update()


class VideoPlayer(QtWidgets.QWidget):
    # added parent here because python-uic, which turns Qt Creator files into python files, always adds the parent
    # widget. so instead of just saying self.videoPlayer = VideoPlayer(), it does
    # self.videoPlayer = VideoPlayer(self.centralWidget)
    # this just means you are required to pass videoFile as a kwarg
    
    def __init__(self, parent=None, videoFile: Union[str, os.PathLike] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout()

        # initialize both widgets and add it to the vertical layout
        self.videoView = VideoFrame(videoFile)
        layout.addWidget(self.videoView)
        self.scrollbartext = ScrollbarWithText()
        layout.addWidget(self.scrollbartext)

        self.setLayout(layout)

        # if you use the scrollbar or the text box, update the video frame
        # self.scrollbartext.horizontalScrollBar.sliderMoved.connect(self.videoView.update_frame)
        # self.scrollbartext.horizontalScrollBar.valueChanged.connect(self.videoView.update_frame)
        # self.scrollbartext.plainTextEdit.textChanged.connect(self.videoView.update_frame)
        self.scrollbartext.position.connect(self.videoView.update_frame)
        self.scrollbartext.position.connect(self.scrollbartext.update_state)

        # if you move the video by any method, update the frame text
        self.videoView.initialized.connect(self.scrollbartext.initialize_state)
        # self.videoView.initialized.connect(initializer)
        self.videoView.frameNum.connect(self.scrollbartext.update_state)

        # I have to do this here because I think emitting a signal doesn't work from within the widget's constructor
        if self.videoView.vid is not None:
            self.videoView.initialized.emit(len(self.videoView.vid))

        # for convenience
        self.scene = self.videoView.scene
        
        self.update()
        
    


class Keypoint(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, xyr=None, color=(255,0,0,255), parent=None):
        super().__init__(parent)
        
        self.xyr = xyr
        
        # self.radius = 30
        self.line_color = QColor(*color)
        self.face_color = QColor(color[0], color[1], color[2], int(color[3]*0.3))
        
        if self.xyr is not None:
            self.cx = self.xyr[0]
            self.cy = self.xyr[1]
            self.radius = self.xyr[2]
            self.draw(self.cx, self.cy, self.radius)
        else:
            self.cx = None
            self.cy = None
            self.radius = None
        # self.ItemIsMovable()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable)
        
        self.pen = QPen(self.line_color, 2, Qt.SolidLine, Qt.FlatCap, Qt.MiterJoin)
        self.brush = QBrush(self.face_color)
        self.setBrush(self.brush)
        # self.painter = QPainter()
        # self.painter.setBrush(self.brush)
        # self.setPainter
        self.setPen(self.pen)
        
    def set_coords(self, cx, cy, r):
        if cx != cx or cy != cy:
            return
        self.cx = cx
        self.cy = cy
        self.radius = r
        # print(cx, cy, r)
        self.draw(self.cx, self.cy, self.radius)
        
    def draw(self, cx, cy, r):        
        # painter = QPainter()
        self.setRect(cx - r, cy - r, r*2, r*2)
        self.setVisible(True)
        # print(self.isVisible())
        # painter.drawEllipse(x, y, self.radius, self.radius)
        
    def clear(self):
        # debug
        # self.cx = 100
        # self.cy = 100
        # self.radius = 20
        # self.draw(self.cx, self.cy, self.radius)
        self.cx = None
        self.cy = None
        self.setVisible(False)
    


class KeypointGroup(QtWidgets.QWidget):
    selected = Signal(int)
    data = Signal(dict)
    
    def __init__(self, keypoint_dict, scene, parent=None, colormap:str='viridis', radius=20):
        super().__init__(parent)
        
        print('constructor')
        
        self.cmap = plt.get_cmap(colormap)
        
        colors = plt.get_cmap(colormap)(np.linspace(0, 1, len(keypoint_dict)))
        self.colors = (colors*255).clip(0, 255).astype(np.uint8)
        
        self.keypoints = {}
        self.keys = list(keypoint_dict.keys())
        
        for i, (key, value) in enumerate(keypoint_dict.items()):
            self.keypoints[key] = Keypoint(color=self.colors[i])
            
        self.N = len(self.keypoints)
        self.radius = radius
        self.add_to_scene(scene)
        self.index = 0
        self.selected.emit(self.index)
        self.scene = scene
        self.tmp_selected = None
        
        self.set_data(keypoint_dict)
        
        # self.data = {}
        # self.scene.viewport().installEventFilter(self)
            
    def broadcast_data(self):
        array = self.get_keypoint_coords()
        data = {self.keys[i]: array[i] for i in range(len(self.keys))}
        self.data.emit(data)
        
    def set_data(self, data: dict):
        for key, value in data.items():
            if value is None:
                continue
            elif isinstance(value, list) and len(value) == 0:
                continue
            else:
                if len(value) == 2:
                    value = (value[0], value[1], self.radius)
                self.keypoints[key].set_coords(*value)
            
    def add_to_scene(self, scene):
        print('add to scene')
        for key, value in self.keypoints.items():
            scene.addItem(value)
            
    def remove_from_scene(self):
        print('remove from scene')
        for key, value in self.keypoints.items():
            self.scene.removeItem(value)
            
    def clear_data(self):
        # self.remove_from_scene()
        for i, key in enumerate(self.keys):
            self.keypoints[key].clear()
        # self.broadcast_data()
        
    def increment_selected(self):
        self.set_selected(self.index + 1)
        
    def decrement_selected(self):
        self.set_selected(self.index - 1)
        
    def clear_selected(self):
        self.get_keypoint(self.index).clear()
            
    @Slot(int)
    def set_selected(self, index: int):
        # print(index)
        if index < 0:
            warnings.warn('index below zero, bug somewhere')
            return
        elif index > self.N:
            warnings.warn('index > len(keypoints)')
            return
        elif index == self.N:
            # happens when you click the final keypoint; tries to increment above the total number
            return
        elif index == self.index:
            # don't do anything. should make sure that there isn't a loop between various widgets that control this
            return
        self.index = index
        self.selected.emit(self.index)
    
    def right_click(self, event):
        pos = event.scenePos()
        x, y = pos.x(), pos.y()
        
        key = self.keys[self.index]
        # self.keypoints[key].setRect(x, y, self.radius, self.radius)
        self.keypoints[key].set_coords(x,y, self.radius)
        self.broadcast_data()
        
        # print(x,y)
        self.set_selected(self.index+1)
        
    def left_click(self, event):
        pos = event.scenePos()
        x, y = pos.x(), pos.y()
        dists = self.get_distance_to_keypoints(x, y)
        
        if np.mean(np.isnan(dists)) > 0.99:
            return
        
        min_ind = np.nanargmin(dists)
        min_dist = dists[min_ind]
        keypoint = self.get_keypoint(min_ind)
        if min_dist < keypoint.radius and keypoint.isVisible():
            self.tmp_selected = min_ind
            # self.set_selected(min_ind)
            # print('inside')    
        # else:
        #     print('not close')
    
    def get_keypoint_coords(self):
        coords = []
        for i, (key, value) in enumerate(self.keypoints.items()):
            x, y = value.cx, value.cy
            if x is None or y is None:
                x, y = np.nan, np.nan
            coords.append([x,y])
        coords = np.array(coords).astype(np.float32)
        return coords
    
    def get_distance_to_keypoints(self, x, y):
        coords = self.get_keypoint_coords()
        dists = np.sqrt((coords[:, 0] - x)**2 + (coords[:, 1] - y)**2)
        return dists
    
    @Slot(QtGui.QMouseEvent)
    def receive_click(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.right_click(event)
        elif event.button() == QtCore.Qt.LeftButton:
            self.left_click(event)
    
    @Slot(QtGui.QMouseEvent)
    def receive_move(self, event):
        # print(event.buttons())
        if event.buttons() == QtCore.Qt.LeftButton:
            # print(self.tmp_selected)
            if self.tmp_selected is None:
                return
            pos = event.scenePos()
            x, y = pos.x(), pos.y()
            
            self.keypoints[self.keys[self.tmp_selected]].set_coords(x, y, self.radius)
            self.broadcast_data()
            # print(event.scenePos())
    
    @Slot(QtGui.QMouseEvent)
    def receive_release(self, event):
        self.tmp_selected = None
        
    def get_keypoint(self, index): 
        if index < 0:
            warnings.warn('index below zero, bug somewhere')
            return
        elif index > self.N:
            warnings.warn('index > len(keypoints)')
            return
        elif index == self.N:
            # happens when you click the final keypoint; tries to increment above the total number
            return
        
        key = self.keys[index]
        return self.keypoints[key]


class KeypointButtons(QtWidgets.QWidget):
    selected = Signal(int)
    
    def __init__(self, keypoint_list, colormap: str='viridis',parent=None):
        super().__init__(parent)
        
        colors = plt.get_cmap(colormap)(np.linspace(0, 1, len(keypoint_list)))
        self.colors = (colors*255).clip(0, 255).astype(np.uint8)
        
        self.layout = QVBoxLayout(self)
        self.button_group = QtWidgets.QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        self.buttons = []
        self.key_index = {}
        for i, key in enumerate(keypoint_list):
            checked = i == 0
            self.make_button(i, key, checked)
            self.key_index[key] = i
        self.N = len(self.key_index)
        self.index = 0
        self.button_group.buttonClicked.connect(self.button_pressed)

        
    def make_button(self, index, name, checked):
        button = QtWidgets.QRadioButton(name)
        button.setChecked(checked)
        
        color = self.colors[index]
        color_string = f'rgb({color[0]},{color[1]},{color[2]})'
        # print(color_string)
        button.setStyleSheet('color: {}'.format(color_string))
        self.buttons.append(button)
        self.layout.addWidget(button)
        self.button_group.addButton(button)
        # button.setGeometry()
        
    def button_pressed(self, event):
        text = self.button_group.checkedButton().text()
        self.set_selected(self.key_index[text])
        # print('button pressed: {}'.format(text))
        # print('index pressed: {}'.format(self.key_index[text]))
        
    @Slot(int)
    def set_selected(self, index: int):
        if index < 0:
            warnings.warn('index below zero, bug somewhere')
            return
        elif index > self.N:
            warnings.warn('index > len(keypoints)')
            return
        elif index == self.N:
            # happens when you click the final keypoint; tries to increment above the total number
            return
        elif index == self.index:
            # don't do anything. should make sure that there isn't a loop between various widgets that control this
            return
        self.index = index
        self.buttons[self.index].setChecked(True)
        self.selected.emit(self.index)

        
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        widget = VideoPlayer(videoFile=r'/media/jim/DATA_SSD/armo/dataset_for_labeling/images/SS21_190508_140054_002526')
        
        kp = {'nose': (50, 50, 5), 
              'forepaw': (100,100,5), 
              'hindpaw': []}
        
        keypoints = KeypointGroup(kp, scene=widget.scene, parent=widget, radius=5)
        widget.scene.click.connect(keypoints.receive_click)
        widget.scene.move.connect(keypoints.receive_move)
        widget.scene.release.connect(keypoints.receive_release)
        # keypoint = Keypoint(100, 100, parent=widget)
        # widget.scene.addItem(keypoint)
        # scene =CroppingOverlay(self)
        # view = QtWidgets.QGraphicsView(scene)
        self.setCentralWidget(widget)


def simple_popup_question(parent, message: str):
    # message = 'You have unsaved changes. Are you sure you want to quit?'
    reply = QtWidgets.QMessageBox.question(parent, 'Message',
                                           message, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
    return reply == QtWidgets.QMessageBox.Yes


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    # testing = VideoPlayer(videoFile=r'/home/jb/Downloads/Basler_acA1300-200um__22273960__20200120_113922411.mp4')
    testing = MainWindow()
    testing.resize(640, 480)
    # volume = VideoPlayer(r'C:\DATA\mouse_reach_processed\M134_20141203_v001.h5')
    # testing = QtWidgets.QMainWindow()
    # testing.initialize(n=6, n_timepoints=15000, debug=True)
    # testing = ShouldRunInference(['M134_20141203_v001',
    #                               'M134_20141203_v002',
    #                               'M134_20141203_v004'],
    #                              [True, True, False])
    # testing = MainWindow()
    # testing.setMaximumHeight(250)
    testing.show()
    app.exec_()
