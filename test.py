# coding:utf-8

import sys
from enum import Enum

from PyQt5.QtCore import (QEasingCurve, QParallelAnimationGroup, QPoint,
                          QPropertyAnimation, Qt, QRect, QDateTime)
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QWidget

from song_info_card import SongInfoCard


class SongInfoCardChute(QWidget):
    """ 
        歌曲卡滑槽，有三个歌曲卡在循环滑动，当前歌曲卡切换时就切换歌曲
        当前下标为0时，不能换到上一首， 当前下标为len-1时，不能换到下一首
    """

    def __init__(self, parent=None, playlist=None):
        super().__init__(parent)
        self.cnt = 0
        self.shiftLeftTime = 0
        self.shiftRightTime = 0
        # 引用播放列表
        self.playlist = playlist
        self.currentIndex = 0
        self.songInfoCard_list = []
        # 创建并行动画组
        self.parallelAniGroup = QParallelAnimationGroup(self)
        self.__initWidget()
        self.now = QDateTime.currentDateTime().toMSecsSinceEpoch()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1300, 970)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.__createWidgets()
        for songInfoCard in self.songInfoCard_list:
            songInfoCard.resize(self.width(), 136)
        self.parallelAniGroup.finished.connect(self.switchSongInfoCard)

    def __createWidgets(self):
        """ 创建小部件 """
        # 创建三个歌曲信息卡，分别为last, current, next
        self.songInfoCard_list = [SongInfoCard(self) for i in range(3)]
        # 引用当前歌曲卡
        self.lastSongInfoCard = self.songInfoCard_list[0]
        self.curSongInfoCard = self.songInfoCard_list[1]
        self.nextSongInfoCard = self.songInfoCard_list[2]
        # 创建动画
        self.songInfoCardAni_list = [QPropertyAnimation(
            self.songInfoCard_list[i], b'geometry') for i in range(3)]
        self.lastSongInfoCardAni = self.songInfoCardAni_list[0]
        self.curSongInfoCardAni = self.songInfoCardAni_list[1]
        self.nextSongInfoCardAni = self.songInfoCardAni_list[2]
        # 将动画添加到动画组中
        for ani in self.songInfoCardAni_list:
            self.parallelAniGroup.addAnimation(ani)
        # 先隐藏所有歌曲信息卡并设置位置
        for i in range(3):
            self.songInfoCard_list[i].move(
                (i - 1) * self.width(), self.height() - 204)
            self.songInfoCard_list[i].hide()
        # 初始化歌曲卡
        if self.playlist:
            self.curSongInfoCard.updateCard(self.playlist[0])
            self.curSongInfoCard.show()
            if len(self.playlist) >= 2:
                self.nextSongInfoCard.show()
                self.nextSongInfoCard.updateCard(self.playlist[1])

    def mousePressEvent(self, e: QMouseEvent):
        """ 按钮按下时记录鼠标位置 """
        self.mousePressPosX = e.pos().x()
        self.lastMousePosX = e.pos().x()
        # 记下按下的时间
        self.mousePressTime = QDateTime.currentDateTime().toMSecsSinceEpoch()

    def mouseMoveEvent(self, e: QMouseEvent):
        """ 鼠标按下可拖动歌曲信息卡 """
        for songInfoCard in self.songInfoCard_list:
            songInfoCard.move(songInfoCard.x(
            )-(self.lastMousePosX-e.pos().x()), songInfoCard.y())
        # 更新鼠标位置
        self.lastMousePosX = e.pos().x()

    def mouseReleaseEvent(self, e: QMouseEvent):
        """ 鼠标松开时重新设置歌曲卡位置 """
        # 记下松开的时间
        self.mouseReleaseTime = QDateTime.currentDateTime().toMSecsSinceEpoch()
        mouseDeltaTime = self.mouseReleaseTime - self.mousePressTime
        # self.mouseDeltaX > 0代表向右移动
        self.mouseDeltaX = self.lastMousePosX - self.mousePressPosX
        # 设置默认循环移位方式
        self.loopMode = SongInfoCardLoopMode.NO_LOOP
        if self.playlist:
            if len(self.playlist) == 1:
                # 只有1个歌曲卡时不管移动距离是多少都把该歌曲卡放回原位
                self.__restoreCardPosition()
            # 播放列表长度为2
            elif len(self.playlist) == 2:
                if (self.currentIndex == 0 and self.mouseDeltaX > 0) or (self.currentIndex == len(self.playlist)-1 and self.mouseDeltaX < 0):
                    self.__restoreCardPosition()
                    print('恢复原位')
                else:
                    if mouseDeltaTime < 1000 and abs(self.mouseDeltaX) >= 120:
                        self.__twoCardShift()
                    else:
                        # 移动距离小于窗口宽度1/2
                        if abs(self.mouseDeltaX) < int(self.width() / 2):
                            self.__restoreCardPosition()
                        # 移动距离超过窗口宽度的1/2或者鼠标移动速度够快时
                        else:
                            self.__twoCardShift()
            # 播放列表长度大于等于3
            elif len(self.playlist) >= 3:
                # 下标为0时右移或者下标为len-1左移都恢复原状
                if (self.currentIndex == 0 and self.mouseDeltaX > 0) or (self.currentIndex == len(self.playlist)-1 and self.mouseDeltaX < 0):
                    self.__restoreCardPosition()
                else:
                    if mouseDeltaTime < 1000 and abs(self.mouseDeltaX) >= 120:
                        self.__threeCardShift()
                    else:
                        if abs(self.mouseDeltaX) < int(self.width() / 2):
                            self.__restoreCardPosition()
                        else:
                            self.__threeCardShift()
            self.parallelAniGroup.start()
            print('动画开始')

    def switchSongInfoCard(self):
        """ 交换对底层歌曲卡对象的引用 """
        print('动画结束')
        # 两卡片左移后(播放下一首)，此时不能再左移
        if self.loopMode == SongInfoCardLoopMode.TWO_CARD_SHIFT_LEFT:
            self.curSongInfoCard = self.songInfoCard_list[2]
            self.lastSongInfoCard = self.songInfoCard_list[1]
            self.nextSongInfoCard = None
            # 更新并行动画组
            self.parallelAniGroup.addAnimation(self.lastSongInfoCardAni)
            # self.parallelAniGroup.removeAnimation(self.nextSongInfoCardAni)
            # 更新下标
            self.currentIndex += 1

        # 两卡片右移后(播放上一首)，此时不能再右移
        elif self.loopMode == SongInfoCardLoopMode.TWO_CARD_SHIFT_RIGHT:
            self.curSongInfoCard = self.songInfoCard_list[1]
            self.lastSongInfoCard = self.songInfoCard_list[0]
            self.nextSongInfoCard = self.songInfoCard_list[2]
            self.songInfoCard_list[0].hide()
            # 更新并行动画组
            self.parallelAniGroup.addAnimation(self.nextSongInfoCardAni)
            # self.parallelAniGroup.removeAnimation(self.lastSongInfoCardAni)
            # 更新下标
            self.currentIndex -= 1

        # 三卡片循环左移
        elif self.loopMode == SongInfoCardLoopMode.THREE_CARD_SHIFT_LEFT:
            self.__resetRef(moveDirection=0)
            # 更新动画组
            self.parallelAniGroup.addAnimation(self.lastSongInfoCardAni)
            # 移动底层对象
            self.__moveObject(
                self.songInfoCard_list[[2, 0, 1][self.shiftLeftTime]], self.width())
            # 更新下标
            self.currentIndex += 1
            if self.currentIndex != len(self.playlist) - 1:
                # 更新歌曲信息卡
                self.updateCards()
                self.nextSongInfoCard.show()
            else:
                self.nextSongInfoCard.hide()
                print('隐藏卡片', self.songInfoCard_list.index(self.nextSongInfoCard))

        # 三卡片循环右移
        elif self.loopMode == SongInfoCardLoopMode.THREE_CARD_SHIFT_RIGHT:
            self.__resetRef(moveDirection=1)
            # 更新动画组
            self.parallelAniGroup.addAnimation(self.nextSongInfoCardAni)
            # 移动底层对象
            self.__moveObject(
                self.songInfoCard_list[[0, 2, 1][self.shiftRightTime]], -self.width())
            # 更新下标
            self.currentIndex -= 1
            if self.currentIndex != 0:
                self.updateCards()
                self.lastSongInfoCard.show()
            else:
                self.lastSongInfoCard.hide()

        self.cnt += 1
        print('更新对象\n'+'=='*20)

    def __twoCardShift(self):
        """ 两卡片移动 """
        if self.mouseDeltaX > 0:
            # 播放播放列表的上一首歌(歌曲卡右移)
            self.loopMode = SongInfoCardLoopMode.TWO_CARD_SHIFT_RIGHT
            self.__setAnimation(self.curSongInfoCardAni,
                                self.curSongInfoCard, self.width())
            self.__setAnimation(self.lastSongInfoCardAni,
                                self.lastSongInfoCard, 0)
            self.songInfoCard_list[0].move(-self.width(), self.height() - 204)
            self.parallelAniGroup.removeAnimation(self.nextSongInfoCardAni)
        else:
            # 播放播放列表的下一首歌(歌曲卡左移)
            self.loopMode = SongInfoCardLoopMode.TWO_CARD_SHIFT_LEFT
            self.__setAnimation(self.curSongInfoCardAni,
                                self.curSongInfoCard, -self.width())
            self.__setAnimation(self.nextSongInfoCardAni,
                                self.nextSongInfoCard, 0)
            self.songInfoCard_list[0].move(-2 *
                                           self.width(), self.height() - 204)
            self.parallelAniGroup.removeAnimation(self.lastSongInfoCardAni)

    def __threeCardShift(self):
        """ 三卡片移动 """
        if self.mouseDeltaX > 0:
            # 播放播放列表的上一首(右移歌曲卡)
            self.loopMode = SongInfoCardLoopMode.THREE_CARD_SHIFT_RIGHT
            self.__setAnimation(self.curSongInfoCardAni,
                                self.curSongInfoCard, self.width())
            self.__setAnimation(self.lastSongInfoCardAni,
                                self.lastSongInfoCard, 0)
            self.parallelAniGroup.removeAnimation(self.nextSongInfoCardAni)
        elif self.mouseDeltaX < 0:
            # 播放播放列表的下一首(左移歌曲卡)
            self.loopMode = SongInfoCardLoopMode.THREE_CARD_SHIFT_LEFT
            self.__setAnimation(self.curSongInfoCardAni,
                                self.curSongInfoCard, -self.width())
            self.__setAnimation(self.nextSongInfoCardAni,
                                self.nextSongInfoCard, 0)
            self.parallelAniGroup.removeAnimation(self.lastSongInfoCardAni)

    def __setAnimation(self, animation: QPropertyAnimation, songInfoCard, endX):
        """ 设置动画 """
        animation.setEasingCurve(QEasingCurve.OutQuart)
        animation.setTargetObject(songInfoCard)
        animation.setDuration(500)
        # 设置起始值
        animation.setStartValue(QRect(songInfoCard.x(), songInfoCard.y(),
                                      songInfoCard.width(), songInfoCard.height()))
        # 设置结束值
        animation.setEndValue(
            QRect(endX, songInfoCard.y(), songInfoCard.width(), songInfoCard.height()))
        print(f'开始位置X：{songInfoCard.x()}，结束位置X：{endX}')

    def __restoreCardPosition(self):
        """ 恢复卡片位置 """
        self.__setAnimation(self.curSongInfoCardAni,
                            self.curSongInfoCard, 0)
        if self.nextSongInfoCard:
            print('nextSongCard恢复位置')
            self.__setAnimation(self.nextSongInfoCardAni,
                                self.nextSongInfoCard, self.width())
        if self.lastSongInfoCard:
            print('lastSongCard恢复位置')
            self.__setAnimation(self.lastSongInfoCardAni,
                                self.lastSongInfoCard, -self.width())

    def updateCards(self):
        """ 更新三个歌曲信息卡 """
        if self.curSongInfoCard:
            self.curSongInfoCard.updateCard(
                self.playlist[self.currentIndex])
        if self.lastSongInfoCard:
            self.lastSongInfoCard.updateCard(
                self.playlist[self.currentIndex - 1])
        if self.nextSongInfoCard:
            self.nextSongInfoCard.updateCard(
                self.playlist[self.currentIndex + 1])

    def resizeEvent(self, e):
        """ 改变窗口大小时也改变歌曲卡的大小 """
        super().resizeEvent(e)
        for i in range(3):
            self.songInfoCard_list[i].resize(self.width(), 136)
            self.songInfoCard_list[i].move(
                self.songInfoCard_list[i].x(), self.height() - 204)

    def __moveObject(self, songInfoCardObj, x):
        """ 移动底层对象 """
        songInfoCardObj.hide()
        songInfoCardObj.move(x, self.height() - 204)
        songInfoCardObj.show()

    def __resetRef(self, moveDirection=0):
        """ 设置变量对底层对象的引用，moveDirection = 0 代表左移，moveDirection = 1 代表右移 """
        # 循环左移
        if moveDirection == 0:
            self.shiftLeftTime = (self.shiftLeftTime + 1) % 3
            self.shiftRightTime = (self.shiftRightTime - 1) % 3
            if self.shiftLeftTime == 0:
                self.__resetRefIndex(0, 1, 2)
            elif self.shiftLeftTime == 1:
                self.__resetRefIndex(1, 2, 0)
            elif self.shiftLeftTime == 2:
                self.__resetRefIndex(2, 0, 1)
        # 循环右移
        elif moveDirection == 1:
            self.shiftLeftTime = (self.shiftLeftTime - 1) % 3
            self.shiftRightTime = (self.shiftRightTime + 1) % 3
            if self.shiftRightTime == 0:
                self.__resetRefIndex(0, 1, 2)
            elif self.shiftRightTime == 1:
                self.__resetRefIndex(2, 0, 1)
            elif self.shiftRightTime == 2:
                self.__resetRefIndex(1, 2, 0)

    def __resetRefIndex(self, lastIndex, curIndex, nextIndex):
        """ refsetFunc的子函数 """
        self.curSongInfoCard = self.songInfoCard_list[curIndex]
        self.lastSongInfoCard = self.songInfoCard_list[lastIndex]
        self.nextSongInfoCard = self.songInfoCard_list[nextIndex]


class SongInfoCardLoopMode(Enum):
    """ 歌曲卡循环移位方式枚举类 """
    NO_LOOP = 0
    # last ← current, current ← next
    TWO_CARD_SHIFT_LEFT = 1
    # last → current,  current → next
    TWO_CARD_SHIFT_RIGHT = 2
    # 循环左移：last ← current ← next ← last
    THREE_CARD_SHIFT_LEFT = 3
    # 循环右移：next → last → current → next
    THREE_CARD_SHIFT_RIGHT = 4
    # 循环左移
    CYCLE_LEFT_SHIFT = 5
    # 循环右移
    CYCLE_RIGHT_SHIFT = 6


if __name__ == "__main__":
    app = QApplication(sys.argv)
    playlist = [{'songName': 'ハッピーでバッドな眠りは浅い',
                 'songer': '鎖那',
                 'album': ['ハッピーでバッドな眠りは浅い']},
                {'songName': '猫じゃらし',
                 'songer': 'RADWIMPS',
                 'album': ['猫じゃらし - Single']}, ]
    demo = SongInfoCardChute(playlist=playlist)
    demo.show()
    sys.exit(app.exec_())
