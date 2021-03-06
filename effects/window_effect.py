# coding:utf-8

from ctypes import c_bool, cdll
from ctypes.wintypes import DWORD, HWND, LPARAM

from win32 import win32gui
from win32.lib import win32con


class WindowEffect():
    """ 调用windowEffect.dll来设置窗口外观 """
    dll = cdll.LoadLibrary('dll\\windowEffect.dll')

    def setAcrylicEffect(self, hWnd: HWND, gradientColor: str = 'FF000066', isEnableShadow: bool = False, animationId: int = 0):
        """ 给窗口开启Win10的亚克力效果

        Parameters
        ----------
        hWnd : 窗口句柄\n
        gradientColor : 十六进制亚克力混合色，对应rgba四个分量\n
        isEnableShadow : 控制是否启用窗口阴影\n
        animationId : 控制磨砂动画
        """
        # 设置阴影
        accentFlags = DWORD(0x20 | 0x40 | 0x80 |
                            0x100) if isEnableShadow else DWORD(0)
        # 设置和亚克力效果相叠加的背景颜色
        gradientColor = gradientColor[6:] + gradientColor[4:6] + \
            gradientColor[2:4] + gradientColor[:2]
        gradientColor = DWORD(int(gradientColor, base=16))
        # 设置窗口动画
        animationId = DWORD(animationId)
        self.dll.setAcrylicEffect(hWnd, accentFlags, gradientColor,
                                  animationId)

    def setAeroEffect(self, hWnd: HWND):
        """ 开启Aero效果 """
        self.dll.setAeroEffect(hWnd)

    def setShadowEffect(self, class_amended: c_bool, hWnd: HWND, newShadow=True):
        """ 去除窗口自带阴影并决定是否添加新阴影 """
        class_amended = c_bool(
            self.dll.setShadowEffect(class_amended, hWnd, c_bool(newShadow)))
        return class_amended

    def addShadowEffect(self, hWnd: HWND, isShadowEnable: bool = True):
        """ 直接添加新阴影 """
        self.dll.addShadowEffect(c_bool(isShadowEnable), hWnd)

    def setWindowFrame(self, hWnd: HWND, left: int, top, right, buttom):
        """ 设置客户区的边框大小 """
        self.dll.setWindowFrame(hWnd, left, top, right, buttom)

    def setWindowAnimation(self, hWnd):
        """ 打开窗口动画效果 """
        style = win32gui.GetWindowLong(hWnd, win32con.GWL_STYLE)
        win32gui.SetWindowLong(
            hWnd, win32con.GWL_STYLE, style | win32con.WS_MAXIMIZEBOX
                                            | win32con.WS_CAPTION
                                            | win32con.CS_DBLCLKS
                                            | win32con.WS_THICKFRAME)

    def adjustMaximizedClientRect(self, hWnd: HWND, lParam: int):
        """ 窗口最大化时调整大小 """
        self.dll.adjustMaximizedClientRect(hWnd, LPARAM(lParam))

    def moveWindow(self, hWnd: HWND):
        """ 移动窗口 """
        self.dll.moveWindow(hWnd)

    def setWindowStayOnTop(self, hWnd, isStayOnTop: bool):
        """ 设置窗口是否置顶 """
        flag = win32con.HWND_TOPMOST if isStayOnTop else win32con.HWND_NOTOPMOST
        win32gui.SetWindowPos(hWnd, flag, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE |
                              win32con.SWP_NOSIZE |
                              win32con.SWP_NOACTIVATE)
