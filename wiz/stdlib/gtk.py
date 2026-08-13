try:
    import gi

    gi.require_version("Gtk", "3.0")

    from gi.repository import Gtk, GLib

    GTK_AVAILABLE = True
except Exception:
    Gtk = None
    GLib = None
    GTK_AVAILABLE = False

from errors import WizError


class GtkModule:

    interpreter = None

    def __init__(self):

        if not GTK_AVAILABLE:
            return

        self._windows = []
        self._main = None

        self.functions = {
            # Window
            "window": self.window,
            "title": self.title,
            "size": self.size,
            "show": self.show,
            "show_all": self.show_all,
            "mainloop": self.mainloop,
            "run": self.mainloop,
            "quit": self.quit,
            "destroy": self.destroy,
            "timeout": self.timeout,
            # Containers
            "box": self.box,
            "frame": self.frame,
            "notebook": self.notebook,
            "add": self.add,
            "pack_start": self.pack_start,
            "pack_end": self.pack_end,
            "grid": self.grid,
            # Widgets
            "label": self.label,
            "button": self.button,
            "entry": self.entry,
            "textarea": self.textarea,
            "checkbox": self.checkbox,
            "radio": self.radio,
            "slider": self.slider,
            "combo": self.combo,
            "image": self.image,
            "progressbar": self.progressbar,
            "spinner": self.spinner,
            # State
            "value": self.value,
            "set": self.set,
            "set_text": self.set_text,
            "clear": self.clear,
            "sensitive": self.sensitive,
            "show_widget": self.show_widget,
            "hide_widget": self.hide_widget,
            "append": self.append,
            "selected": self.selected,
            # Events
            "connect": self.connect,
            "on_click": self.on_click,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _check(self):
        if not GTK_AVAILABLE or Gtk is None:
            raise WizError(
                "The 'gtk' module requires PyGObject (python3-gi)."
            )

    def _wrap(self, callback):

        if callback is None:
            return None

        interpreter = self.interpreter

        def handler(*_args):
            if interpreter is not None and hasattr(callback, "statement"):
                return interpreter.call_wiz_function(callback, [])
            if callable(callback):
                return callback()
            return None

        return handler

    # ------------------------------------------------------------------
    # Window
    # ------------------------------------------------------------------

    def window(self, title="Wiz", size=None):

        self._check()

        win = Gtk.Window()

        win.set_title(str(title))

        if size:
            win.set_default_size(int(size[0]), int(size[1]))

        win.connect("destroy", Gtk.main_quit)

        self._windows.append(win)
        self._main = win

        return win

    def title(self, win, text):
        win.set_title(str(text))
        return True

    def size(self, win, width, height):
        win.set_default_size(int(width), int(height))
        return True

    def show(self, win):
        win.show()
        return True

    def show_all(self, win):
        win.show_all()
        return True

    def mainloop(self):
        self._check()
        Gtk.main()

    def quit(self):
        self._check()
        Gtk.main_quit()
        return True

    def destroy(self, win):
        win.destroy()
        return True

    def timeout(self, ms, callback):

        self._check()

        interpreter = self.interpreter

        def handler(*_args):
            if interpreter is not None and hasattr(callback, "statement"):
                interpreter.call_wiz_function(callback, [])
            return False

        return GLib.timeout_add(int(ms), handler)

    # ------------------------------------------------------------------
    # Containers
    # ------------------------------------------------------------------

    def box(self, orientation="vertical", spacing=0):

        self._check()

        if orientation in ("horizontal", "h"):
            orient = Gtk.Orientation.HORIZONTAL
        else:
            orient = Gtk.Orientation.VERTICAL

        return Gtk.Box(orientation=orient, spacing=int(spacing))

    def frame(self, label=""):
        self._check()
        return Gtk.Frame(label=str(label))

    def notebook(self):
        self._check()
        return Gtk.Notebook()

    def add(self, parent, widget):
        parent.add(widget)
        return widget

    def pack_start(self, box, widget, expand=False, fill=False, padding=0):
        box.pack_start(widget, bool(expand), bool(fill), int(padding))
        return widget

    def pack_end(self, box, widget, expand=False, fill=False, padding=0):
        box.pack_end(widget, bool(expand), bool(fill), int(padding))
        return widget

    def grid(self, grid, child, row=0, column=0, rowspan=1, columnspan=1,
             xpadding=0, ypadding=0):
        grid.attach(
            child,
            int(column),
            int(row),
            int(columnspan),
            int(rowspan),
            int(xpadding),
            int(ypadding)
        )
        return child

    # ------------------------------------------------------------------
    # Widgets
    # ------------------------------------------------------------------

    def label(self, parent=None, text=""):
        self._check()
        label = Gtk.Label(label=str(text))
        if parent is not None:
            parent.add(label)
        return label

    def button(self, parent=None, text="", command=None):
        self._check()
        button = Gtk.Button(label=str(text))
        if command is not None:
            button.connect("clicked", self._wrap(command))
        if parent is not None:
            parent.add(button)
        return button

    def entry(self, parent=None, value=""):
        self._check()
        entry = Gtk.Entry()
        entry.set_text(str(value))
        if parent is not None:
            parent.add(entry)
        return entry

    def textarea(self, parent=None, value=""):
        self._check()
        view = Gtk.TextView()
        view.set_wrap_mode(Gtk.WrapMode.WORD)
        if value:
            view.get_buffer().set_text(str(value))
        if parent is not None:
            parent.add(view)
        return view

    def checkbox(self, parent=None, text="", command=None):
        self._check()
        check = Gtk.CheckButton(label=str(text))
        if command is not None:
            check.connect("toggled", self._wrap(command))
        if parent is not None:
            parent.add(check)
        return check

    def radio(self, parent=None, group=None, text="", command=None):
        self._check()
        radio = Gtk.RadioButton.new_with_label_from_widget(group, str(text))
        if command is not None:
            radio.connect("toggled", self._wrap(command))
        if parent is not None:
            parent.add(radio)
        return radio

    def slider(self, parent=None, from_=0, to=100, value=None, command=None):

        self._check()

        adjustment = Gtk.Adjustment(
            value=float(value if value is not None else from_),
            lower=float(from_),
            upper=float(to),
            step_increment=1,
            page_increment=10,
            page_size=0
        )

        slider = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            adjustment=adjustment
        )

        if command is not None:
            slider.connect("value-changed", self._wrap(command))

        if parent is not None:
            parent.add(slider)

        return slider

    def combo(self, parent=None, values=None, value=None, command=None):

        self._check()

        combo = Gtk.ComboBoxText()

        for item in values or []:
            combo.append_text(str(item))

        if value is not None:
            combo.set_active(int(value))

        if command is not None:
            combo.connect("changed", self._wrap(command))

        if parent is not None:
            parent.add(combo)

        return combo

    def image(self, parent=None, filename=None):
        self._check()
        image = Gtk.Image.new_from_file(str(filename))
        if parent is not None:
            parent.add(image)
        return image

    def progressbar(self, parent=None, value=None, maximum=100):
        self._check()
        bar = Gtk.ProgressBar()
        bar.set_max_value(float(maximum))
        if value is not None:
            bar.set_value(float(value))
        if parent is not None:
            parent.add(bar)
        return bar

    def spinner(self, parent=None, active=False):
        self._check()
        spinner = Gtk.Spinner()
        if active:
            spinner.start()
        if parent is not None:
            parent.add(spinner)
        return spinner

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def value(self, widget):
        if hasattr(widget, "get_text"):
            return widget.get_text()
        if hasattr(widget, "get_value"):
            return widget.get_value()
        if hasattr(widget, "get_active"):
            return bool(widget.get_active())
        if hasattr(widget, "get_active_iter"):
            return bool(widget.get_active_iter())
        return None

    def set(self, widget, value):
        if hasattr(widget, "set_text"):
            widget.set_text(str(value))
        elif hasattr(widget, "set_value"):
            widget.set_value(float(value))
        elif hasattr(widget, "set_active"):
            widget.set_active(bool(value))
        return True

    def set_text(self, widget, text):
        if hasattr(widget, "set_text"):
            widget.set_text(str(text))
        elif hasattr(widget, "get_buffer"):
            widget.get_buffer().set_text(str(text))
        return True

    def clear(self, widget):
        if hasattr(widget, "get_buffer"):
            widget.get_buffer().set_text("")
        elif hasattr(widget, "set_text"):
            widget.set_text("")
        return True

    def sensitive(self, widget, enabled=True):
        widget.set_sensitive(bool(enabled))
        return True

    def show_widget(self, widget):
        widget.show()
        return True

    def hide_widget(self, widget):
        widget.hide()
        return True

    def append(self, widget, text):
        if hasattr(widget, "append_text"):
            widget.append_text(str(text))
        elif hasattr(widget, "get_buffer"):
            widget.get_buffer().insert_at_cursor(str(text))
        return True

    def selected(self, widget):
        if hasattr(widget, "get_active"):
            return widget.get_active()
        return None

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def connect(self, widget, signal, callback):
        widget.connect(signal, self._wrap(callback))
        return True

    def on_click(self, widget, callback):
        widget.connect("clicked", self._wrap(callback))
        return True
