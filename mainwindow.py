import os.path

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa: E402 # need to call require_version before we can call this

gi.require_version('Gdk', '3.0')
from gi.repository import Gdk  # noqa: E402 # need to call require_version before we can call this


class MainWindow(Gtk.ApplicationWindow):
    """
    Main application window
    """
    
    def __init__(self):
        Gtk.Window.__init__(self, title="PiJu")
        self.connect("destroy", self.on_quit)
        self.fullscreen()

        icon_filename = os.path.join(os.path.dirname(__file__), 'window-close-solid.png')
        close_icon = Gtk.Image.new_from_file(icon_filename)
        close = Gtk.Button.new()
        close.set_image(close_icon)
        close.connect('clicked', self.on_quit)
        top_right = Gtk.Alignment.new(1, 0, 0, 0)
        top_right.add(close)
        self.add(top_right)
        
    def on_quit(self, *args):
        Gtk.main_quit()
