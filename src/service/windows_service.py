import win32gui
import win32con
import win32api
import win32ui

import numpy as np
import pygetwindow as gw


def enum_windows_callback(hwnd, window_list):
    window_text = win32gui.GetWindowText(hwnd)
    window_list.append((hwnd, window_text))


class WindowsService:

    def capture_screen(self, window_name: str):
        hwnd = self.get_window(window_name)[0]
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

        hdc = win32gui.GetWindowDC(hwnd)
        src_dc = win32ui.CreateDCFromHandle(hdc)
        mem_dc = src_dc.CreateCompatibleDC()

        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(src_dc, width, height)
        mem_dc.SelectObject(bitmap)

        mem_dc.BitBlt((0, 0), (width, height), src_dc, (left, top), win32con.SRCCOPY)

        signed_ints_array = bitmap.GetBitmapBits(True)
        img = np.fromstring(signed_ints_array, dtype='uint8')
        img.shape = (height, width, 4)

        src_dc.DeleteDC()
        mem_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hdc)
        win32gui.DeleteObject(bitmap.GetHandle())

        return img

    @staticmethod
    def get_all_windows():
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        return windows

    def get_window(self, window_name: str):
        res = list(filter(lambda wnd: window_name in wnd[1], self.get_all_windows()))
        return res[0] if res else None

    @staticmethod
    def get_window_gw(window_name: str):
        res = list(filter(lambda wnd: window_name in wnd.title, gw.getAllWindows()))
        return res[0] if res else None
