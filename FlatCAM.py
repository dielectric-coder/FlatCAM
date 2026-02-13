import os
import sys

if hasattr(sys, 'frozen'):
    os.environ['PATH'] = os.path.dirname(sys.executable) + os.pathsep + os.environ.get('PATH', '')

from PyQt5 import QtWidgets, QtGui, QtCore
from FlatCAMApp import App
from multiprocessing import freeze_support
import VisPyPatches

if sys.platform == "win32":
    # cx_freeze 'module win32' workaround
    import OpenGL.platform.win32

def debug_trace():
    """
    Set a tracepoint in the Python debugger that works with Qt
    :return: None
    """
    from PyQt5.QtCore import pyqtRemoveInputHook
    #from pdb import set_trace
    pyqtRemoveInputHook()
    #set_trace()

# All X11 calling should be thread safe otherwise we have strange issues
# QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
# NOTE: Never talk to the GUI from threads! This is why I commented the above.

if __name__ == '__main__':
    freeze_support()

    debug_trace()
    VisPyPatches.apply_patches()

    app = QtWidgets.QApplication(sys.argv)

    # Force a light Fusion style so icons designed for light backgrounds
    # remain visible regardless of the system/desktop dark theme.
    app.setStyle('Fusion')
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(240, 240, 240))
    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(233, 233, 233))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(255, 255, 220))
    palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.Text, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(240, 240, 240))
    palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 0, 0))
    palette.setColor(QtGui.QPalette.Link, QtGui.QColor(0, 0, 255))
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(76, 163, 224))
    palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
    app.setPalette(palette)

    fc = App()
    sys.exit(app.exec_())

