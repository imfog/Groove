import sys

from PyQt5.QtCore import Qt,QEvent
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QSlider, QWidget
from .play_bar_buttons import VolumeButton, SmallPlayModeButton, MoreActionsButton


class RightWidgetGroup(QWidget):
    """ 播放按钮组 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建小部件
        self.volumeButton = VolumeButton(self)
        self.volumeSlider = QSlider(Qt.Horizontal, self)
        self.smallPlayModeButton = SmallPlayModeButton(self)
        self.moreActionsButton = MoreActionsButton(self)
        self.widget_list = [self.volumeButton, self.volumeSlider,
                            self.smallPlayModeButton, self.moreActionsButton]
        # 创建布局
        self.h_layout = QHBoxLayout()
        # 初始化界面
        self.initWidget()
        self.initLayout()
        #self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(301, 16 + 67)
        self.volumeSlider.setRange(0,100)
        self.volumeSlider.setObjectName('volumeSlider')
        # 将音量滑动条数值改变信号连接到槽函数
        self.volumeSlider.valueChanged.connect(self.setVolume)
        self.volumeSlider.setValue(20)
                            
    def initLayout(self):
        """ 初始化布局 """
        self.__spacing_list = [7, 8, 8, 5, 7]
        self.h_layout.setSpacing(0)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        # 将小部件添加到布局中
        for i in range(4):
            self.h_layout.addSpacing(self.__spacing_list[i])
            self.h_layout.addWidget(self.widget_list[i])
        else:
            self.h_layout.addSpacing(self.__spacing_list[-1])
        self.setLayout(self.h_layout)

    def setVolume(self):
        """ 调整音量并更换图标 """
        if self.volumeSlider.value()==0:
            self.volumeButton.setVolumeLevel(0)
        elif 0 < self.volumeSlider.value() <= 32:
            self.volumeButton.setVolumeLevel(1)
        elif 32 < self.volumeSlider.value() <= 65:
            self.volumeButton.setVolumeLevel(2)
        else:
            self.volumeButton.setVolumeLevel(3)
        

    def setQss(self):
        with open(r'resource\css\playBar.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = RightWidgetGroup()
    demo.show()
    sys.exit(app.exec_())
