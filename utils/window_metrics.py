"""Return the outer (window) size that yields an exact client-area size.

Usage:
    outer_w, outer_h = outer_from_client(1920, 1001)
"""

import sys

def outer_from_client(w: int, h: int) -> tuple[int, int]:
    """
    Given desired *client* width/height, return the outer window size that
    produces it on the current platform.
    """
    if sys.platform != "win32":
        # On macOS/Linux the decoration is usually <10 px, negligible.
        return w, h

    import ctypes
    # Win32 system-metric constants
    SM_CXFRAME  = 32   # thick frame width
    SM_CYFRAME  = 33   # thick frame height
    SM_CYCAPTION = 4   # title-bar height

    border_x = ctypes.windll.user32.GetSystemMetrics(SM_CXFRAME)
    border_y = ctypes.windll.user32.GetSystemMetrics(SM_CYFRAME)
    caption  = ctypes.windll.user32.GetSystemMetrics(SM_CYCAPTION)

    outer_w = w + border_x * 2
    outer_h = h + caption + border_y * 2
    return outer_w, outer_h
