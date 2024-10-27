import sys

import napari


def main():
    viewer = napari.Viewer()
    viewer.window.add_plugin_dock_widget(plugin_name='plugin-fmi')
    sys.exit(napari.run())


if __name__ == '__main__':
    main()
