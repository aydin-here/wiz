try:
    import tkinter as _tk

    from tkinter import filedialog, messagebox, simpledialog

    TK_AVAILABLE = True
except Exception:
    _tk = None
    TK_AVAILABLE = False

from errors import WizError


class TkModule:

    interpreter = None

    def __init__(self):

        if not TK_AVAILABLE:
            return

        self._roots = []
        self._main = None

        self.functions = {
            # Window
            "window": self.window,
            "app": self.window,
            "title": self.title,
            "size": self.size,
            "resizable": self.resizable,
            "mainloop": self.mainloop,
            "run": self.mainloop,
            "destroy": self.destroy,
            "after": self.after,
            "exit": self.exit,
            # Widgets
            "frame": self.frame,
            "label": self.label,
            "button": self.button,
            "entry": self.entry,
            "textarea": self.textarea,
            "checkbox": self.checkbox,
            "radio": self.radio,
            "slider": self.slider,
            "listbox": self.listbox,
            "combo": self.combo,
            "canvas": self.canvas,
            "image": self.image,
            "picture": self.picture,
            "progressbar": self.progressbar,
            # Layout
            "pack": self.pack,
            "grid": self.grid,
            "place": self.place,
            # Canvas drawing
            "draw_line": self.draw_line,
            "draw_rect": self.draw_rect,
            "draw_oval": self.draw_oval,
            "draw_text": self.draw_text,
            # State
            "variable": self.variable,
            "value": self.value,
            "set": self.set,
            "get_text": self.get_text,
            "set_text": self.set_text,
            "clear": self.clear,
            "config": self.config,
            "disable": self.disable,
            "enable": self.enable,
            "focus": self.focus,
            "selected": self.selected,
            # Events
            "bind": self.bind,
            "on_click": self.on_click,
            # Dialogs
            "alert": self.alert,
            "info": self.info,
            "warn": self.warn,
            "error": self.error,
            "confirm": self.confirm,
            "ask_file": self.ask_file,
            "ask_save": self.ask_save,
            "ask_dir": self.ask_dir,
            "ask_color": self.ask_color,
            "ask_text": self.ask_text,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _check(self):
        if not TK_AVAILABLE or _tk is None:
            raise WizError(
                "The 'tk' module requires a Python build with tkinter."
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

    def _geometry(self, size):
        if size:
            width = int(size[0])
            height = int(size[1])
            return f"{width}x{height}"
        return None

    # ------------------------------------------------------------------
    # Window
    # ------------------------------------------------------------------

    def window(self, title="Wiz", size=None, resizable=True):

        self._check()

        root = _tk.Tk()

        root.title(str(title))

        geometry = self._geometry(size)

        if geometry:
            root.geometry(geometry)

        root.resizable(
            bool(resizable) if isinstance(resizable, (bool, int)) else True,
            bool(resizable) if isinstance(resizable, (bool, int)) else True
        )

        self._roots.append(root)
        self._main = root

        return root

    def title(self, win, text):
        win.title(str(text))
        return True

    def size(self, win, width, height):
        win.geometry(f"{int(width)}x{int(height)}")
        return True

    def resizable(self, win, width=True, height=True):
        win.resizable(bool(width), bool(height))
        return True

    def mainloop(self, win=None):
        self._check()
        target = win or self._main
        if target is None:
            raise WizError("No window created yet. Call tk.window(...) first.")
        target.mainloop()

    def destroy(self, win=None):
        target = win or self._main
        if target is not None:
            target.destroy()
            return True
        return False

    def after(self, win, ms, callback):
        win.after(int(ms), self._wrap(callback))
        return True

    def exit(self):
        for root in list(self._roots):
            try:
                root.destroy()
            except Exception:
                pass
        self._roots.clear()
        return True

    # ------------------------------------------------------------------
    # Widgets
    # ------------------------------------------------------------------

    def _widget(self, cls, parent, options, defaults=None):

        self._check()

        kwargs = dict(defaults or {})
        kwargs.update(dict(options or {}))

        command = kwargs.pop("command", None)
        command = self._wrap(command)

        if command is not None:
            kwargs["command"] = command

        return cls(parent, **kwargs)

    def frame(self, parent, **options):
        return self._widget(_tk.Frame, parent, options)

    def label(self, parent, text="", **options):
        return self._widget(
            _tk.Label,
            parent,
            options,
            defaults={"text": str(text)}
        )

    def button(self, parent, text="", command=None, **options):
        options["text"] = str(text)
        options["command"] = command
        return self._widget(_tk.Button, parent, options)

    def entry(self, parent, value="", **options):
        widget = self._widget(_tk.Entry, parent, options)
        widget.insert(0, str(value))
        return widget

    def textarea(self, parent, value="", **options):
        widget = self._widget(_tk.Text, parent, options)
        widget.insert("1.0", str(value))
        return widget

    def checkbox(self, parent, text="", command=None, **options):

        variable = _tk.BooleanVar()

        options["text"] = str(text)
        options["variable"] = variable
        options["command"] = command

        widget = self._widget(_tk.Checkbutton, parent, options)

        return {
            "widget": widget,
            "value": variable
        }

    def radio(self, parent, variable, text="", value=True, command=None, **options):

        options["variable"] = variable
        options["value"] = value
        options["text"] = str(text)
        options["command"] = command

        return self._widget(_tk.Radiobutton, parent, options)

    def slider(self, parent, from_=0, to=100, value=None, command=None, **options):

        variable = _tk.DoubleVar(value=value if value is not None else from_)

        options["variable"] = variable
        options["from_"] = from_
        options["to"] = to
        options["command"] = command

        options.setdefault("orient", "horizontal")

        if options["orient"] == "vertical":
            options["orient"] = _tk.VERTICAL
        else:
            options["orient"] = _tk.HORIZONTAL

        widget = self._widget(_tk.Scale, parent, options)

        return {
            "widget": widget,
            "value": variable
        }

    def listbox(self, parent, values=None, **options):

        widget = self._widget(_tk.Listbox, parent, options)

        for index, item in enumerate(values or []):
            widget.insert(_tk.END, str(item))

        return widget

    def combo(self, parent, values=None, value="", command=None, **options):

        variable = _tk.StringVar(value=str(value))

        options["values"] = list(values or [])
        options["textvariable"] = variable
        options["command"] = command

        try:
            from tkinter import ttk
            widget = self._widget(ttk.Combobox, parent, options)
        except Exception:
            widget = self._widget(_tk.OptionMenu, parent, options)

        return {
            "widget": widget,
            "value": variable
        }

    def canvas(self, parent, width=400, height=300, bg="white", **options):

        options["width"] = int(width)
        options["height"] = int(height)
        options["bg"] = bg

        return self._widget(_tk.Canvas, parent, options)

    def image(self, filename=None, width=None, height=None):

        self._check()

        if filename is None:
            raise WizError("tk.image needs a filename")

        try:
            from PIL import Image, ImageTk

            image = Image.open(filename)

            if width or height:
                image = image.resize(
                    (int(width or image.width), int(height or image.height))
                )

            return ImageTk.PhotoImage(image)

        except Exception:
            return _tk.PhotoImage(file=str(filename))

    def picture(self, parent, filename=None, width=None, height=None, **options):

        photo = self.image(filename, width, height)

        options["image"] = photo

        return self._widget(_tk.Label, parent, options)

    def progressbar(self, parent, value=0, maximum=100, **options):

        try:
            from tkinter import ttk

            options["maximum"] = maximum
            options["value"] = value

            return self._widget(ttk.Progressbar, parent, options)

        except Exception:
            return self._widget(_tk.Scale, parent, options)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def pack(self, widget, side=None, padx=None, pady=None,
             expand=False, fill=None, anchor=None, ipadx=None, ipady=None):

        options = {}

        if side is not None:
            options["side"] = str(side)
        if padx is not None:
            options["padx"] = padx
        if pady is not None:
            options["pady"] = pady
        if expand:
            options["expand"] = True
        if fill is not None:
            options["fill"] = str(fill)
        if anchor is not None:
            options["anchor"] = str(anchor)
        if ipadx is not None:
            options["ipadx"] = ipadx
        if ipady is not None:
            options["ipady"] = ipady

        widget.pack(**options)

        return widget

    def grid(self, widget, row=0, column=0, padx=None, pady=None,
             sticky=None, columnspan=1, rowspan=1):

        options = {
            "row": int(row),
            "column": int(column),
            "columnspan": int(columnspan),
            "rowspan": int(rowspan)
        }

        if padx is not None:
            options["padx"] = padx
        if pady is not None:
            options["pady"] = pady
        if sticky is not None:
            options["sticky"] = str(sticky)

        widget.grid(**options)

        return widget

    def place(self, widget, x=None, y=None, width=None, height=None):

        options = {}

        if x is not None:
            options["x"] = int(x)
        if y is not None:
            options["y"] = int(y)
        if width is not None:
            options["width"] = int(width)
        if height is not None:
            options["height"] = int(height)

        widget.place(**options)

        return widget

    # ------------------------------------------------------------------
    # Canvas drawing
    # ------------------------------------------------------------------

    def draw_line(self, canvas, x1, y1, x2, y2, **options):
        canvas.create_line(x1, y1, x2, y2, **options)
        return True

    def draw_rect(self, canvas, x1, y1, x2, y2, **options):
        canvas.create_rectangle(x1, y1, x2, y2, **options)
        return True

    def draw_oval(self, canvas, x1, y1, x2, y2, **options):
        canvas.create_oval(x1, y1, x2, y2, **options)
        return True

    def draw_text(self, canvas, x, y, text, **options):
        canvas.create_text(x, y, text=str(text), **options)
        return True

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def variable(self, kind="string"):

        self._check()

        if kind in ("bool", "boolean"):
            return _tk.BooleanVar()

        if kind == "int":
            return _tk.IntVar()

        if kind == "double":
            return _tk.DoubleVar()

        return _tk.StringVar()

    def value(self, var):
        if var is None:
            return None
        if hasattr(var, "get"):
            return var.get()
        return var

    def set(self, var, value):
        if hasattr(var, "set"):
            var.set(value)
            return True
        raise WizError("Cannot set a value on this object")

    def get_text(self, widget):
        if hasattr(widget, "get"):
            return widget.get()
        if hasattr(widget, "get_text"):
            return widget.get_text()
        return None

    def set_text(self, widget, text):
        if hasattr(widget, "delete"):
            widget.delete(0, _tk.END)
            widget.insert(0, str(text))
        elif hasattr(widget, "set_text"):
            widget.set_text(str(text))
        return True

    def clear(self, widget):
        if hasattr(widget, "delete"):
            widget.delete(0, _tk.END)
        elif hasattr(widget, "clear"):
            widget.clear()
        return True

    def config(self, widget, **options):
        widget.config(**options)
        return widget

    def disable(self, widget):
        widget.config(state="disabled")
        return True

    def enable(self, widget):
        widget.config(state="normal")
        return True

    def focus(self, widget):
        widget.focus_set()
        return True

    def selected(self, widget):
        if hasattr(widget, "curselection"):
            indexes = widget.curselection()
            return indexes[0] if indexes else None
        if hasattr(widget, "get"):
            return widget.get()
        return None

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def bind(self, widget, event, callback):
        widget.bind(event, self._wrap(callback))
        return True

    def on_click(self, widget, callback):
        widget.bind("<Button-1>", self._wrap(callback))
        return True

    # ------------------------------------------------------------------
    # Dialogs
    # ------------------------------------------------------------------

    def alert(self, title="Wiz", message=""):
        return self.info(title, message)

    def info(self, title="Wiz", message=""):
        self._check()
        messagebox.showinfo(str(title), str(message))
        return True

    def warn(self, title="Wiz", message=""):
        self._check()
        messagebox.showwarning(str(title), str(message))
        return True

    def error(self, title="Wiz", message=""):
        self._check()
        messagebox.showerror(str(title), str(message))
        return True

    def confirm(self, title="Wiz", message="Are you sure?"):
        self._check()
        return messagebox.askyesno(str(title), str(message))

    def ask_file(self, title=None):
        self._check()
        return filedialog.askopenfilename(title=title)

    def ask_save(self, title=None):
        self._check()
        return filedialog.asksaveasfilename(title=title)

    def ask_dir(self, title=None):
        self._check()
        return filedialog.askdirectory(title=title)

    def ask_color(self, title=None):
        self._check()
        return filedialog.askcolor(title=title)[1]

    def ask_text(self, title="Wiz", prompt="Enter text:"):
        self._check()
        return simpledialog.askstring(str(title), str(prompt))
