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
        # top_right.halign = Gtk.Align.END
        # close.valign = Gtk.Align.START

        self.artist_label = Gtk.Label()

        self.track_name_label = Gtk.Label()

        layout_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        layout_column.pack_start(self.artist_label, expand=True, fill=True, padding=30)
        layout_column.pack_start(self.track_name_label, expand=True, fill=True, padding=30)

        overlay = Gtk.Overlay()
        overlay.add(layout_column)
        overlay.add_overlay(top_right)
        
        self.add(overlay)
        
    def on_quit(self, *args):
        Gtk.main_quit()

    def show_artist(self, artist):
        self.artist_label.set_label(artist)

    def show_track_name(self, track_name):
        self.track_name_label.set_label(track_name)
