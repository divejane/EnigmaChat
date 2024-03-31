import gi

# We must specify the GTK Version to use.
gi.require_version("Gtk", "3.0")

# importing the Gtk module from gi. LSP doesn't like this for some reason
from gi.repository import Gtk

# Here we declare a window, and we connect it to the buttons to close out of it
# We also show the window with show_all
win = Gtk.Window(title="Discreet Dial")
win.connect("destroy", Gtk.main_quit)
win.show_all()

# Main loop, similar to tkinter mainloop()
Gtk.main()
