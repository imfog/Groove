# coding:utf-8
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPainter, QPen
from PyQt5.QtWidgets import QWidget

from .navigation_button import PushButton, ToolButton, CreatePlaylistButton
from .search_line_edit import SearchLineEdit
from .basic_navigation_widget import BasicNavigationWidget
from my_widget.my_scrollArea import ScrollArea


class NavigationWidget(BasicNavigationWidget):
    """ 侧边导航窗口 """

    def __init__(self, parent):
        super().__init__(parent)
        # 创建滚动区域
        self.scrollArea = ScrollArea(self)
        self.scrollWidget = ScrollWidget(self)
        # 创建搜索框
        self.searchLineEdit = SearchLineEdit(self)
        # 创建按钮
        self.__createButtons()
        # 初始化界面
        self.__initWidget()

    def __createButtons(self):
        """实例化按钮 """
        self.showBarButton = ToolButton(
            r'resource\images\navigationBar\黑色最大化导航栏.png', parent=self)
        self.musicGroupButton = PushButton(
            r'resource\images\navigationBar\黑色我的音乐.png', '我的音乐', self.scrollWidget,
            (400, 60), (60, 62))
        self.historyButton = PushButton(
            r'resource\images\navigationBar\黑色最近播放.png', '最近播放的内容', self.scrollWidget,
            (400, 62), (60, 62))
        self.playingButton = PushButton(
            r'resource\images\navigationBar\黑色导航栏正在播放.png', '正在播放', self.scrollWidget,
            (400, 62), (60, 62))
        self.playlistButton = PushButton(
            r'resource\images\navigationBar\黑色播放列表.png', '播放列表', self.scrollWidget,
            (340, 60))
        self.createPlaylistButton = CreatePlaylistButton(self.scrollWidget)
        self.settingButton = PushButton(
            r'resource\images\navigationBar\黑色设置按钮.png', '设置', self, (400, 62),
            (60, 62))
        # 创建播放列表名字按钮
        self.playlistName_list = self.getPlaylistNames()
        self.playlistNameButton_list = [PushButton(
            r'resource\images\navigationBar\黑色我喜欢_60_62.png', i, self.scrollWidget,
            (400, 62), (60, 62)) for i in self.playlistName_list]
        # 设置当前按钮
        self.currentButton = self.musicGroupButton
        # todo:设置可选中的按钮列表
        self._selectableButton_list = [
            self.musicGroupButton, self.historyButton, self.playingButton,
            self.playlistButton, self.settingButton] + self.playlistNameButton_list
        # todo:设置可选中的按钮名字列表
        self._selectableButtonName_list = [
            'musicGroupButton', 'historyButton', 'playingButton',
            'playlistButton', 'settingButton'
        ] + self.playlistName_list

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(400, 800)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setSelectedButton(self.musicGroupButton)
        # 将按钮的点击信号连接到槽函数
        self._connectButtonClickedSigToSlot()
        # 初始化布局
        self.__initLayout()

    def __initLayout(self):
        """ 初始化布局 """
        self.scrollArea.move(0, 162)
        self.scrollArea.setWidget(self.scrollWidget)
        # 将按钮添加到滚动区域
        self.historyButton.move(0, 62)
        self.showBarButton.move(0, 40)
        self.playingButton.move(0, 124)
        self.playlistButton.move(0, 186)
        self.searchLineEdit.move(15, 108)
        self.createPlaylistButton.move(340, 186)
        self.settingButton.move(0, self.height() - 187)
        self.__addPlaylistNameButtonsToScrollWidget()
        # 调整滚动区域的高度
        self.__adjustScrollWidgetHeight()

    def resizeEvent(self, e):
        """ 调整小部件尺寸 """
        self.scrollArea.resize(self.width(), self.height() - 347)
        self.scrollWidget.resize(self.width(), self.scrollWidget.height())
        self.settingButton.move(0, self.height() - 62 - 115 - 10)

    def paintEvent(self, e):
        """ 绘制分隔符 """
        painter = QPainter(self)
        pen = QPen(QColor(0, 0, 0, 30))
        painter.setPen(pen)
        painter.drawLine(15, self.settingButton.y() - 1,
                         self.width() - 15, self.settingButton.y() - 1)

    def getPlaylistNames(self):
        """ 扫描播放列表名字 """
        if not os.path.exists('Playlists'):
            os.mkdir('Playlists')
        playlists = [i[:-5]
                     for i in os.listdir('Playlists') if i.endswith('.json')]
        return playlists

    def __addPlaylistNameButtonsToScrollWidget(self):
        """ 将播放列表名字按钮添加到滚动部件上 """
        for index, button in enumerate(self.playlistNameButton_list):
            button.move(0, 246 + index * 62)
            button.show()

    def __adjustScrollWidgetHeight(self):
        """ 调整滚动部件的高度 """
        buttonHeight = 246 + 62 * len(self.playlistName_list)
        height = self.height() - 346 if self.height() - \
            346 > buttonHeight else buttonHeight
        self.scrollWidget.resize(400, height)

    def updateWindow(self):
        """ 更新界面 """
        # 扫描播放列表
        playlistName_list = self.getPlaylistNames()
        if playlistName_list == self.playlistName_list:
            return
        # 删除旧按钮
        for i in range(len(self.playlistNameButton_list)):
            button = self.playlistNameButton_list.pop()
            button.deleteLater()
        # 创建新按钮
        self.playlistName_list = playlistName_list
        self.playlistNameButton_list = [PushButton(
            r'resource\images\navigationBar\黑色我喜欢_60_62.png', i, self.scrollWidget,
            (400, 62), (60, 62)) for i in playlistName_list]
        # 移动按钮
        self.__addPlaylistNameButtonsToScrollWidget()
        self.__adjustScrollWidgetHeight()
        self.update()


class ScrollWidget(QWidget):
    """ 滚动部件 """

    def __init(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, e):
        """ 绘制分隔符 """
        painter = QPainter(self)
        pen = QPen(QColor(0, 0, 0, 30))
        painter.setPen(pen)
        # 前两个参数为第一个坐标，后两个为第二个坐标
        painter.drawLine(15, 185, self.width() - 15, 185)
