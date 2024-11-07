import sys

import napari
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

def main():
    viewer = napari.Viewer()
    viewer.window.add_plugin_dock_widget(plugin_name='plugin-fmi')
    sys.exit(napari.run())

if __name__ == '__main__':
    main()
