"""Clipboard utilities."""

import subprocess
import shutil
import sys
from typing import Tuple


def copy(text: str) -> Tuple[bool, str]:
    """
    Copy text to clipboard using available system tools.
    
    Returns:
        Tuple[bool, str]: (Success, Message)
    """
    # 1. Try pyperclip first (if installed)
    try:
        import pyperclip
        pyperclip.copy(text)
        return True, "Copied to clipboard using pyperclip!"
    except ImportError:
        pass

    # 2. Try native system tools
    
    # Wayland (wl-copy)
    if shutil.which('wl-copy'):
        try:
            subprocess.run(['wl-copy'], input=text.encode('utf-8'), check=True)
            return True, "Copied to clipboard using wl-copy!"
        except subprocess.SubprocessError:
            pass

    # X11 (xclip)
    if shutil.which('xclip'):
        try:
            # Try both primary and clipboard selections
            subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode('utf-8'), check=True)
            return True, "Copied to clipboard using xclip!"
        except subprocess.SubprocessError:
            pass

    # X11 (xsel)
    if shutil.which('xsel'):
        try:
            subprocess.run(['xsel', '--clipboard', '--input'], input=text.encode('utf-8'), check=True)
            return True, "Copied to clipboard using xsel!"
        except subprocess.SubprocessError:
            pass

    return False, "Could not find a clipboard tool. Please install xclip, xsel, or wl-copy."
