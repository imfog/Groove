# coding:utf-8

from copy import deepcopy
from json import dump

from PyQt5.QtCore import QEvent, QMargins, QPoint, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QContextMenuEvent, QPainter, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QListWidgetItem, QWidget

from my_dialog_box import PropertyPanel, SongInfoEditPanel
from my_widget.my_listWidget import ListWidget

from .song_card import AlbumInterfaceSongCard, SongTabSongCard
from .song_card_type import SongCardType


class BasicSongListWidget(ListWidget):
    """ 基本歌曲列表控件 """

    emptyChangedSig = pyqtSignal(bool)                   # 歌曲卡是否为空信号
    removeItemSignal = pyqtSignal(int)
    songCardNumChanged = pyqtSignal(int)
    addSongToPlayingSignal = pyqtSignal(dict)            # 将一首歌添加到正在播放
    checkedSongCardNumChanged = pyqtSignal(int)
    editSongCardSignal = pyqtSignal(dict, dict)          # 编辑歌曲卡完成信号
    selectionModeStateChanged = pyqtSignal(bool)
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)    # 将歌曲添加到新的自定义播放列表
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)  # 将歌曲添加到已存在的自定义播放列表

    def __init__(self, songInfo_list: list, songCardType: SongCardType, parent=None, viewportMargins=QMargins(0, 0, 0, 0), paddingBottomHeight: int = 116):
        """ 创建歌曲卡列表控件对象

        Parameters
        ----------
        songInfo_list : 歌曲信息列表\n
        songCardType : 歌曲卡类型\n
        parent : 父级窗口\n
        viewportMargins : 视口的外边距\n
        paddingBottomHeight : 列表视图底部留白
        """
        super().__init__(parent)
        self.__songCardType = songCardType
        self.paddingBottomHeight = paddingBottomHeight
        # 使用指定的歌曲卡类创建歌曲卡对象
        self.__SongCard = [SongTabSongCard,
                           AlbumInterfaceSongCard][songCardType.value]
        self.songInfo_list = songInfo_list if songInfo_list else []
        self.currentIndex = 0
        self.playingIndex = 0  # 正在播放的歌曲卡下标
        self.playingSongInfo = self.songInfo_list[0] if songInfo_list else None
        # 初始化标志位
        self.isInSelectionMode = False
        self.isAllSongCardsChecked = False
        # 初始化列表
        self.item_list = []
        self.songCard_list = []
        self.checkedSongCard_list = []
        # 创建导航标签标签
        self.__createGuideLabel()
        # 交错颜色
        self.setAlternatingRowColors(True)
        # 设置边距
        self.setViewportMargins(viewportMargins)

    def createSongCards(self, connectSongCardToSlotFunc):
        """ 清空列表并创建新歌曲卡，该函数必须被子类重写
        Parameter
        ----------
        connectSongCardSigToSlotFunc : 将歌曲卡信号连接到槽函数的函数对象 """
        self.clearSongCards()
        for songInfo in self.songInfo_list:
            # 添加空项目
            self.appendOneSongCard(songInfo, connectSongCardToSlotFunc)
        # 设置导航标签是否隐藏
        self.guideLabel.setHidden(bool(self.songCard_list))
        # 添加一个空白item来填补playBar所占高度
        self.__createPaddingBottomItem()

    def __createGuideLabel(self):
        """ 创建导航标签 """
        self.guideLabel = QLabel('这里没有可显示的内容。请尝试其他筛选器。', self)
        self.guideLabel.setStyleSheet(
            "color: black; font: 25px 'Microsoft YaHei'")
        self.guideLabel.resize(500, 26)
        self.guideLabel.move(35, 286)

    def appendOneSongCard(self, songInfo: dict, connectSongCardSigToSlotFunc=None):
        """ 在列表尾部添加一个歌曲卡
        Parameters
        ----------
        songInfo : 歌曲信息字典\n
        connectSongCardSigToSlotFunc : 将歌曲卡信号连接到槽函数的函数对象
        """
        item = QListWidgetItem()
        songCard = self.__SongCard(songInfo)
        songCard.itemIndex = len(self.songCard_list)
        songCard.resize(1150, 60)
        item.setSizeHint(QSize(songCard.width(), 60))
        self.addItem(item)
        self.setItemWidget(item, songCard)
        # 将项目添加到项目列表中
        self.songCard_list.append(songCard)
        self.item_list.append(item)
        # 将歌曲卡信号连接到槽函数
        if connectSongCardSigToSlotFunc:
            # 调用子类的方法
            connectSongCardSigToSlotFunc(songCard)
        else:
            self.__connectSongCardSignalToSlot(songCard)

    def setCurrentIndex(self, index):
        """ 设置当前下标 """
        if not self.isInSelectionMode:
            # 不处于选择模式时将先前选中的歌曲卡设置为非选中状态
            if index != self.currentIndex:
                self.songCard_list[self.currentIndex].setSelected(False)
                self.songCard_list[index].setSelected(True)
        else:
            # 如果处于选中模式下点击了歌曲卡则取反选中的卡的选中状态
            songCard = self.songCard_list[index]  # type:SongCard
            songCard.setChecked(not songCard.isChecked)
        self.currentIndex = index

    def removeSongCard(self, index):
        """ 删除选中的一个歌曲卡 """
        songCard = self.songCard_list.pop(index)
        songCard.deleteLater()
        self.item_list.pop(index)
        self.takeItem(index)
        # 更新下标
        for i in range(index, len(self.songCard_list)):
            self.songCard_list[i].itemIndex = i
        if self.currentIndex > index:
            self.currentIndex -= 1
        # 发送信号
        self.removeItemSignal.emit(index)
        self.update()

    def setPlay(self, index):
        """ 设置歌曲卡播放状态 """
        if not self.songCard_list:
            return
        self.songCard_list[self.playingIndex].setPlay(False)
        self.songCard_list[self.currentIndex].setSelected(False)
        self.currentIndex = index
        self.playingIndex = index  # 更新正在播放的下标
        if index >= 0:
            self.songCard_list[index].setPlay(True)
            self.playingSongInfo = self.songInfo_list[index]

    def showPropertyPanel(self, songInfo: dict = None):
        """ 显示selected的歌曲卡的属性 """
        songInfo = self.songCard_list[self.currentRow(
        )].songInfo if not songInfo else songInfo
        propertyPanel = PropertyPanel(songInfo, self.window())
        propertyPanel.exec_()

    def showSongInfoEditPanel(self, songCard=None):
        """ 显示编辑歌曲信息面板 """
        if not songCard:
            # 歌曲卡默认为当前右键点击的歌曲卡
            songCard = self.songCard_list[self.currentRow()]
        # 获取歌曲卡下标和歌曲信息
        index = self.songCard_list.index(songCard)
        newSongInfo = songCard.songInfo
        oldSongInfo = deepcopy(newSongInfo)
        songInfoEditPanel = SongInfoEditPanel(newSongInfo, self.window())
        songInfoEditPanel.saveInfoSig.connect(
            lambda: self.__saveModifidiedSongInfo(oldSongInfo, newSongInfo))
        songInfoEditPanel.exec_()

    def __saveModifidiedSongInfo(self, oldSongInfo, newSongInfo):
        """ 保存被更改的歌曲信息 """
        # 更新歌曲卡和歌曲信息列表
        self.updateOneSongCard(oldSongInfo, newSongInfo)
        # 发出歌曲卡被更改信息
        self.editSongCardSignal.emit(oldSongInfo, newSongInfo)

    def updateOneSongCard(self, oldSongInfo: dict, newSongInfo, isNeedWriteToFile=True):
        """ 更新一个歌曲卡 """
        if oldSongInfo not in self.songInfo_list:
            return
        index = self.songInfo_list.index(
            oldSongInfo)
        self.songInfo_list[index] = newSongInfo
        self.songCard_list[index].updateSongCard(
            newSongInfo)
        if isNeedWriteToFile:
            # 将修改的信息存入json文件
            with open('Data\\songInfo.json', 'w', encoding='utf-8') as f:
                dump(self.songInfo_list, f)

    def updateMultiSongCards(self, oldSongInfo_list: list, newSongInfo_list: list):
        """ 更新多个歌曲卡 """
        for oldSongInfo, newSongInfo in zip(oldSongInfo_list, newSongInfo_list):
            self.updateOneSongCard(oldSongInfo, newSongInfo, False)
        # 将修改的信息存入json文件
        with open('Data\\songInfo.json', 'w', encoding='utf-8') as f:
            dump(self.songInfo_list, f)

    def resizeEvent(self, e):
        """ 更新item的尺寸 """
        super().resizeEvent(e)
        margins = self.viewportMargins()  # type:QMargins
        for item in self.item_list:
            item.setSizeHint(
                QSize(self.width() - margins.left() - margins.right(), 60))
        self.paddingBottomItem.setSizeHint(
            QSize(self.width() - margins.left() - margins.right(), self.paddingBottomHeight))

    def songCardCheckedStateChangedSlot(self, itemIndex: int, isChecked: bool):
        """ 歌曲卡选中状态改变对应的槽函数 """
        songCard = self.songCard_list[itemIndex]
        # 如果歌曲卡不在选中的歌曲列表中且该歌曲卡变为选中状态就将其添加到列表中
        if songCard not in self.checkedSongCard_list and isChecked:
            self.checkedSongCard_list.append(songCard)
            self.checkedSongCardNumChanged.emit(
                len(self.checkedSongCard_list))
        # 如果歌曲卡已经在列表中且该歌曲卡变为非选中状态就弹出该歌曲卡
        elif songCard in self.checkedSongCard_list and not isChecked:
            self.checkedSongCard_list.pop(
                self.checkedSongCard_list.index(songCard))
            self.checkedSongCardNumChanged.emit(
                len(self.checkedSongCard_list))
        # 如果先前不处于选择模式那么这次发生选中状态改变就进入选择模式
        if not self.isInSelectionMode:
            # 更新当前下标
            self.setCurrentIndex(itemIndex)
            # 所有歌曲卡进入选择模式
            self.__setAllSongCardSelectionModeOpen(True)
            # 发送信号要求主窗口隐藏播放栏
            self.selectionModeStateChanged.emit(True)
            # 更新标志位
            self.isInSelectionMode = True
        else:
            if not self.checkedSongCard_list:
                # 所有歌曲卡退出选择模式
                self.__setAllSongCardSelectionModeOpen(False)
                # 发送信号要求主窗口显示播放栏
                self.selectionModeStateChanged.emit(False)
                # 更新标志位
                self.isInSelectionMode = False

    def __setAllSongCardSelectionModeOpen(self, isOpenSelectionMode: bool):
        """ 设置所有歌曲卡是否进入选择模式 """
        # 更新光标样式
        cursor = [Qt.PointingHandCursor, Qt.ArrowCursor][isOpenSelectionMode]
        for songCard in self.songCard_list:
            songCard.setSelectionModeOpen(isOpenSelectionMode)
            songCard.setClickableLabelCursor(cursor)

    def setAllSongCardCheckedState(self, isAllChecked: bool):
        """ 设置所有的歌曲卡checked状态 """
        if self.isAllSongCardsChecked == isAllChecked:
            return
        self.isAllSongCardsChecked = isAllChecked
        for songCard in self.songCard_list:
            songCard.setChecked(isAllChecked)

    def unCheckSongCards(self):
        """ 取消所有已处于选中状态的歌曲卡的选中状态 """
        checkedSongCard_list_copy = self.checkedSongCard_list.copy()
        for songCard in checkedSongCard_list_copy:
            songCard.setChecked(False)

    def updateAllSongCards(self, songInfo_list: list, connectSongCardSigToSlotFunc=None):
        """ 更新所有歌曲卡，根据给定的信息决定创建或者删除歌曲卡，该函数必须被子类重写
        Parameters
        ----------
        songInfo_list : 歌曲信息列表\n
        connectSongCardSigToSlotFunc : 将歌曲卡信号连接到槽函数的函数对象 """
        # 删除旧占位行
        self.removeItemWidget(self.paddingBottomItem)
        self.takeItem(len(self.songCard_list))
        # 长度相等就更新信息，不相等就根据情况创建或者删除item
        if self.songCard_list:
            self.songCard_list[self.currentIndex].setPlay(False)
        deltaLen = len(songInfo_list) - len(self.songInfo_list)
        oldSongInfoLen = len(self.songInfo_list)
        if deltaLen > 0:
            # 添加item
            for songInfo in songInfo_list[oldSongInfoLen:]:
                self.appendOneSongCard(songInfo, connectSongCardSigToSlotFunc)
                # QApplication.processEvents()
        elif deltaLen < 0:
            # 删除多余的item
            for i in range(oldSongInfoLen - 1, len(songInfo_list) - 1, -1):
                self.item_list.pop()
                songCard = self.songCard_list.pop()
                songCard.deleteLater()
                self.takeItem(i)
        # 更新部分歌曲卡
        if not (bool(self.songInfo_list) and bool(songInfo_list)):
            # 当两个列表是否为空的的布尔值不同时发送歌曲卡列表是否为空信号
            self.emptyChangedSig.emit(not bool(songInfo_list))
        self.songInfo_list = songInfo_list if songInfo_list else []
        iterRange = range(
            len(self.songInfo_list) - deltaLen) if deltaLen > 0 else range(len(self.songInfo_list))
        for i in iterRange:
            songInfo_dict = self.songInfo_list[i]
            self.songCard_list[i].updateSongCard(songInfo_dict)
        # 更新样式和当前下标
        self.currentIndex = 0
        self.playingIndex = 0
        self.playingSongInfo = None
        for songCard in self.songCard_list:
            songCard.setPlay(False)
        # 如果歌曲卡为空就显示导航标签
        self.guideLabel.setHidden(bool(self.songCard_list))
        # 创建新占位行
        self.__createPaddingBottomItem()
        # 发出歌曲卡数量改变信号
        if deltaLen != 0:
            self.songCardNumChanged.emit(len(self.songInfo_list))

    def clearSongCards(self):
        """ 清空歌曲卡 """
        self.item_list.clear()
        self.clear()
        # 释放内存
        for songCard in self.songCard_list:
            songCard.deleteLater()
        self.songCard_list.clear()
        self.currentIndex = 0
        self.playingIndex = 0

    def sortSongInfo(self, key: str, isReverse=True):
        """ 依据指定的键排序歌曲信息列表
        Parameters
        ----------
        key : 排序依据，有'modifiedTime'、'songName'、'songer'和'tracknumber'四种\n
        isReverse : 是否降序，只对前三种排序方式有效 """
        if key != 'tracknumber':
            self.songInfo_list.sort(
                key=lambda songInfo: songInfo[key], reverse=isReverse)
        else:
            self.songInfo_list.sort(
                key=lambda songInfo: int(songInfo['tracknumber']))

    def __createPaddingBottomItem(self):
        """ 创建底部占位行 """
        self.paddingBottomItem = QListWidgetItem(self)
        # 创建占位窗口
        self.paddingBottomWidget = QWidget(self)
        self.paddingBottomWidget.setStyleSheet('background:white')
        self.paddingBottomWidget.setFixedHeight(self.paddingBottomHeight)
        # 将窗口加到Item中
        margins = self.viewportMargins()  # type:QMargins
        width = self.width() - margins.left() - margins.right()
        self.paddingBottomWidget.resize(width, self.paddingBottomHeight)
        self.paddingBottomItem.setSizeHint(
            QSize(width, self.paddingBottomHeight))
        self.setItemWidget(self.paddingBottomItem, self.paddingBottomWidget)
        self.addItem(self.paddingBottomItem)

    @property
    def songCardType(self) -> SongCardType:
        return self.__songCardType

    def __connectSongCardSignalToSlot(self, songCard):
        """ 将一个歌曲卡的信号连接到槽函数 """
        # 必须被子类重写
        raise NotImplementedError
