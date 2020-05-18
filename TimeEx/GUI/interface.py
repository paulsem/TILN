import sys
import json
import xml
import os.path
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font
import tkinter.colorchooser
import tkinter.filedialog
import tkinter.messagebox


# Unele label uri pot fi editate cu right click -> Edit
# Elementele pot fi collapsed cu right click -> Collapse si expanded cu right click -> Expand
# Ctrl + Z - Undo la ultimele edit uri
# Ctrl + Y - Redo la utimele edit uri
# File -> Browse : Alege fisier si extrage
# File -> Save : Salveaza fisierul xml
# File -> Exit : Close la aplicatie
# Tools -> Expand all: Da expand la toate elementele colapsed
# Tools -> Attributes: Se pot alege culorile elementelor si cuvintelor in text cu anumite tipuri si 
# se poate da toggle la visibilitatea lor
# Tools -> Preferences: Se poate alege: background ul aplicatiei
#                                       background ul si foreground ul label urilor
#                                       fontul si marimea lui pentru label urile visibile
#                                       fontul si marimea lui pentru label urile collapsed
#                                       fontul si marimea lui pentru label urile visibile



tiln_directory = os.path.abspath(os.path.dirname(os.path.dirname(sys.argv[0])))
path_dictionary = {
    "tiln directory": tiln_directory,
    "gui directory": os.path.join(tiln_directory, "GUI"),
    "input directory": os.path.join(tiln_directory, "input"),
    "output directory": os.path.join(tiln_directory, "output"),
    "parsing directory": os.path.join(tiln_directory, "PARSARE"),
    "xml directory": os.path.join(tiln_directory, "XML")
}

sys.path = list(set(sys.path + list(path_dictionary.values())))

import proiect


def read_config(path=os.path.join(path_dictionary["gui directory"], "guiconfig.json")):
    with open(path, "r") as file_descriptor:
        return json.load(file_descriptor)


class TextApp(tk.Tk):
    gui = read_config()

    def __init__(self):
        super().__init__()
        self.title(TextApp.gui["application title"])
        self.is_dialog_opened = False
        self.is_file_opened = False
        self.opened_file = None
        self.undo_stack, self.redo_stack = [], []
        self.absolute_path = None
        self.xml_path = None
        self.state("zoomed")
        self.option_add("*Font", TextApp.gui["global font"])
        self.config_menu()
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="news")
        self.view = View(self)
        self.view.grid(row=0, column=0, pady=5, padx=5, sticky="nswe")
        self.notebook.add(self.view, text="Xml")
        self.text_view = None
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.config_bind()
        self.mainloop()

    def config_menu(self):
        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Save", command=self.save, font=TextApp.gui["menu font"])
        file_menu.add_command(label="Browse", command=self.browse, font=TextApp.gui["menu font"])
        file_menu.add_command(label="Exit", command=self.quit, font=TextApp.gui["menu font"])
        menu.add_cascade(label="File", menu=file_menu, font=TextApp.gui["menu font"])
        view_menu = tk.Menu(menu, tearoff=0)
        view_menu.add_command(label="Attributes", command=self.view_attributes, font=TextApp.gui["menu font"])
        view_menu.add_command(label="Expand all", command=lambda: self.view.frame.expand_all(),
                              font=TextApp.gui["menu font"])
        view_menu.add_command(label="Preferences", command=lambda: PreferencesDialog(self),
                              font=TextApp.gui["menu font"])
        menu.add_cascade(label="Tools", menu=view_menu)
        self.config(menu=menu)

    def view_attributes(self):
        AttributesDialog(self)

    def config_bind(self):
        self.bind("<Control-z>", self.undo)
        self.bind("<Control-Z>", self.undo)
        self.bind("<Control-y>", self.redo)
        self.bind("<Control-Y>", self.redo)

    def undo(self, _):
        if self.undo_stack:
            label, text = self.undo_stack.pop(-1)
            self.push_redo(label)
            label.configure(text=text)

    def push_undo(self, label):
        self.undo_stack.append((label, label.cget("text")))

    def push_redo(self, label):
        self.redo_stack.append((label, label.cget("text")))

    def redo(self, _):
        if self.redo_stack:
            label, text = self.redo_stack.pop(-1)
            self.push_undo(label)
            label.configure(text=text)

    def save(self):
        if self.is_file_opened:
            save_xml(self.xml_path, self.get_info())

    def get_info(self):
        if self.is_file_opened:
            return self.view.canvas.winfo_children()[0].get_info()

    def display(self, root):
        self.is_file_opened = True
        for child in self.view.frame.winfo_children():
            child.destroy()
        self.view.frame.display_node(root, do_grid=False)

    def browse(self):
        filename = tkinter.filedialog.askopenfilename(filetypes=[("txt files", "*.txt")])
        self.extract(filename)

    def extract(self, filename):
        try:
            if filename:
                proiect.setare_input(filename)
                proiect.rulare(False)
                self.xml_path = os.path.join(path_dictionary["output directory"], "exemplu.xml")
                self.opened_file = filename
                self.title(f"{TextApp.gui['application title']} - {filename} - {self.xml_path}")
                with open(self.xml_path) as xml_file:
                    tree = xml.etree.ElementTree.parse(xml_file)
                    self.display(tree.getroot())
                    info = []
                    for attribute in TextApp.gui["attributes background"]:
                        type_ = list(attribute.keys())[0]
                        background = attribute[type_]["background"]
                        highlighted = attribute[type_]["highlighted"]
                        info.append((type_, highlighted, background))
                    self.highlight_attributes(info)
                if len(self.notebook.tabs()) == 1:
                    self.text_view = TextView(self)
                    self.notebook.add(self.text_view, text="Text")
                self.text_view.set(self.opened_file)
        except Exception as exception:
            tkinter.messagebox.showerror("Exception", str(exception))

    def set_background(self):
        self.view.canvas.configure(background=TextApp.gui["view background"])
        self.view.frame.set_background()

    def highlight_attributes(self, info):
        self.view.frame.highlight_attributes(info)
        if self.text_view:
            self.text_view.highlight_expressions()

    def update_labels_background(self):
        self.view.frame.update_labels_background()

    def update_labels_foreground(self):
        self.view.frame.update_labels_foreground()

    def update_visible_label_font(self):
        self.view.frame.update_visible_label_font()

    def update_collapsed_label_font(self):
        self.view.frame.update_collapsed_label_font()

    def set_dialog_open(self, flag=True):
        self.is_dialog_opened = flag

    def get_all_texts(self):
        info = self.get_info()
        if info:
            texts = []
            attributes = info["header"]["attributes"]
            type_, value_ = None, info["text"]
            for attribute, value in attributes:
                if attribute == "value":
                    value_ = value.strip()
                if attribute == "type":
                    type_ = value.strip()
            background = None
            for attribute in TextApp.gui["attributes background"]:
                type__ = list(attribute.keys())[0]
                if type_ == type__ and attribute[type_]["highlighted"]:
                    background = attribute[type_]["background"]
            if None not in (type_, value_, background):
                texts.append((value_, background))
            texts.extend(TextApp.get_texts_from_contents(info["contents"]))
            return texts

    @staticmethod
    def get_texts_from_contents(contents):
        texts = []
        for content in contents:
            attributes = content["header"]["attributes"]
            type_, value_ = None, content["text"]
            for attribute, value in attributes:
                if attribute == "value":
                    value_ = value.strip()
                if attribute == "type":
                    type_ = value.strip()
            background = None
            for attribute in TextApp.gui["attributes background"]:
                type__ = list(attribute.keys())[0]
                if type_ == type__ and attribute[type_]["highlighted"]:
                    background = attribute[type_]["background"]
            if None not in (type_, value_, background):
                texts.append((value_, background))
            if content["contents"]:
                texts.extend(TextApp.get_texts_from_contents(content["contents"]))
        return texts

    @staticmethod
    def save_config():
        with open(os.path.join(path_dictionary["gui directory"], "guiconfig.json"), "w") as file_descriptor:
            json.dump(TextApp.gui, file_descriptor, indent=4)


class TextView(tk.Frame):

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.text = tk.Text(self, font=TextApp.gui["source font"], wrap=tk.WORD, state=tk.DISABLED)
        y_scroll = tk.Scrollbar(self, command=self.text.yview)
        self.text.configure(yscrollcommand=y_scroll.set)
        self.text.grid(row=0, column=0, sticky="news")
        y_scroll.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def set(self, path):
        self.text.configure(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        with open(path, "r") as file_descriptor:
            self.text.insert(1.0, file_descriptor.read())
            self.highlight_expressions()
        self.text.configure(state=tk.DISABLED)

    def highlight_expressions(self):
        for tag in self.text.tag_names()[1:]:
            self.text.tag_delete(tag)
        texts = self.master.get_all_texts()
        for color in set(map(lambda _: _[1], texts)):
            self.text.tag_configure(color, background=color)
        for text, color in self.master.get_all_texts():
            start = "1.0"
            while True:
                position = self.text.search(text, start, tk.END)
                if not position:
                    break
                self.text.tag_add(color, position, f"{position}+{len(text)}c")
                start = f"{position}+1c"


class ContentFrame(tk.Frame):

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.configure(bg=TextApp.gui["view background"])
        self.visible = True
        self.is_highlighted = False
        self.header_frame, self.footer_frame, self.text_frame = [None for _ in range(3)]

    def set_background(self):
        if not self.is_highlighted:
            for frame in (self, self.header_frame, self.footer_frame, self.text_frame):
                if frame:
                    frame.configure(background=TextApp.gui["view background"])
        for child in self.winfo_children():
            if type(child) is ContentFrame:
                child.set_background()

    def reset(self):
        self.highlight(TextApp.gui["view background"])

    def highlight(self, background):
        self.configure(background=background)
        self.header_frame.configure(background=background)
        for frame in (self.text_frame, self.footer_frame):
            if frame:
                frame.configure(background=background)

    def highlight_attributes(self, info):
        if self.header_frame:
            header_frame_type = self.header_frame.get_type()
            if not header_frame_type:
                self.reset()
            for type_, highlight, background in info:
                if header_frame_type == type_:
                    if highlight:
                        self.highlight(background)
                        self.is_highlighted = True
                    else:
                        self.reset()
                        self.is_highlighted = False
                    break
            for child in self.winfo_children():
                if type(child) is ContentFrame:
                    child.highlight_attributes(info)

    def display_node(self, node, padx=TextApp.gui["content frame padx"], pady=TextApp.gui["content frame pady"],
                     do_grid=True):
        text = node.text
        stripped_text = text.strip() if text else text
        has_text = text and stripped_text
        self.header_frame = HeaderFrame(self, node, has_text)
        self.text_frame = TextFrame(self, stripped_text) if has_text else None
        if len(node):
            for child in node:
                frame = ContentFrame(self)
                frame.display_node(child)
        if len(node) or self.text_frame:
            self.footer_frame = FooterFrame(self, node)
        if do_grid:
            self.grid(row=len(self.master.winfo_children()), column=0, padx=padx, pady=pady, sticky="nw")

    def collapse(self):
        if self.visible:
            for child in self.winfo_children()[1:]:
                child.grid_remove()
            for child in self.header_frame.winfo_children():
                child.configure(font=TextApp.gui["collapsed label font"])
            self.header_frame.attribute_menu.entryconfigure(1, label="Expand")
            self.header_frame.tag_menu.entryconfigure(0, label="Expand")
        else:
            for child in self.winfo_children()[1:]:
                child.grid()
            for child in self.header_frame.winfo_children():
                child.configure(font=TextApp.gui["visible label font"])
            self.header_frame.attribute_menu.entryconfigure(1, label="Collapse")
            self.header_frame.tag_menu.entryconfigure(0, label="Collapse")
        self.visible = not self.visible

    def expand_all(self):
        if self.header_frame:
            for child in self.winfo_children()[1:]:
                child.grid()
                if type(child) is ContentFrame:
                    child.expand_all()
            for child in self.header_frame.winfo_children():
                child.configure(font=TextApp.gui["visible label font"])
            self.header_frame.attribute_menu.entryconfigure(1, label="Collapse")
            self.header_frame.tag_menu.entryconfigure(0, label="Collapse")
            self.visible = True

    def update_labels_background(self):
        for child in self.winfo_children():
            child.update_labels_background()

    def update_labels_foreground(self):
        for child in self.winfo_children():
            child.update_labels_foreground()

    def update_visible_label_font(self):
        if self.visible and self.header_frame:
            for child in self.header_frame.winfo_children():
                child.configure(font=TextApp.gui["visible label font"])
        for child in self.winfo_children():
            if type(child) is ContentFrame:
                child.update_visible_label_font()
        for frame in (self.text_frame, self.footer_frame):
            if frame:
                frame.winfo_children()[0].configure(font=TextApp.gui["visible label font"])

    def update_collapsed_label_font(self):
        if not self.visible and self.header_frame:
            for child in self.header_frame.winfo_children():
                child.configure(font=TextApp.gui["collapsed label font"])
        for child in self.winfo_children():
            if type(child) is ContentFrame:
                child.update_collapsed_label_font()

    def get_info(self):
        contents = []
        for child in self.winfo_children():
            if type(child) is ContentFrame:
                contents.append(child.get_info())
        text = None if not self.text_frame else self.text_frame.winfo_children()[0].cget("text")
        return {"header": self.header_frame.get_info(), "text": text, "contents": contents}


class HeaderFrame(tk.Frame):

    def __init__(self, master, node, has_text, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.configure(background=TextApp.gui["view background"])
        tag, attributes = node.tag, node.attrib
        font = TextApp.gui["visible label font"]
        padx, pady = TextApp.gui["content frame intern padx"], TextApp.gui["content frame intern pady"]
        label = tk.Label(self, text=f"<{tag}", font=font, justify=tk.LEFT,
                         background=TextApp.gui["label background"], foreground=TextApp.gui["label foreground"])
        label.grid(row=0, column=1, sticky="nw", padx=padx, pady=pady)
        self.tag_menu = tk.Menu(label, tearoff=0)
        self.tag_menu.add_command(label="Collapse", command=self.master.collapse)
        self.attribute_menu = tk.Menu(label, tearoff=0)
        self.attribute_menu.add_command(label="Edit", command=self.edit)
        self.attribute_menu.add_command(label="Collapse", command=self.master.collapse)
        label.bind("<Button-3>", self.right_click)
        if not attributes:
            text = label.cget("text")
            text += " />" if not has_text and not len(node) else ">"
            label.configure(text=text)
        for attribute in attributes:
            label = tk.Label(self, justify=tk.LEFT, text=f"{attribute}={attributes[attribute].strip()}", font=font,
                             background=TextApp.gui["label background"],
                             foreground=TextApp.gui["label foreground"])
            label.grid(row=0, column=len(self.winfo_children()), sticky="nw", padx=padx, pady=pady)
            label.bind("<Button-3>", self.right_click)
            label.type = attribute
            label.value = attributes[attribute].strip()
        if attributes:
            label = tk.Label(self, text=">", font=font, justify=tk.LEFT, background=TextApp.gui["label background"],
                             foreground=TextApp.gui["label foreground"])
            if not has_text and not len(node):
                label.configure(text="/" + label.cget("text"))
            label.grid(row=0, column=len(self.winfo_children()), sticky="nw", padx=padx, pady=pady)
            label.bind("<Button-3>", self.right_click)
        self.grid(row=0, column=0, sticky="nw")
        self.widget = None

    def right_click(self, event):
        self.widget = event.widget
        if hasattr(self.widget, "type"):
            self.attribute_menu.tk_popup(event.x_root, event.y_root)
        else:
            self.tag_menu.tk_popup(event.x_root, event.y_root)

    def edit(self):
        label = self.widget
        label_type = label.type
        label_text = f"Change {label_type}"
        height = 1 if label_type != "tag text" else 10
        dialog = EditDialog(self.winfo_toplevel(), label_text=label_text, initial_value=label.value, height=height)
        if dialog.response:
            self.winfo_toplevel().push_undo(label)
            label.value = dialog.response
            if label_type != "tag text":
                label.configure(text=f"{label_type}={dialog.response}")
            else:
                label.configure(text=f"{dialog.response}")

    def get_info(self):
        children = self.winfo_children()
        tag = children[0].cget("text")
        children = children[1:-1]
        if tag[-1] == ">":
            tag = tag[:-1]
        if tag[-1] == "/":
            tag = tag[:-2]
        tag = tag[1:]
        attributes = []
        for child in children:
            text = child.cget("text")
            index = text.index("=")
            attributes.append((text[:index], text[index + 1:]))
        return {"tag": tag, "attributes": attributes}

    def get_type(self):
        for attribute, value in self.get_info()["attributes"]:
            if attribute == "type":
                return value

    def update_labels_background(self):
        for child in self.winfo_children():
            if type(child) is tk.Label:
                child.configure(background=TextApp.gui["label background"])

    def update_labels_foreground(self):
        for child in self.winfo_children():
            if type(child) is tk.Label:
                child.configure(foreground=TextApp.gui["label foreground"])


class Dialog(tk.Toplevel):

    def __init__(self, parent, title=None, buttons_space=True):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.response = None
        if title:
            self.title(title)
        self.parent = parent
        self.parent.is_dialog_opened = True
        self.body = tk.Frame(self)
        self.buttons = tk.Frame(self)
        self.initial_focus = self.create_body()
        self.create_buttons()
        self.grid_rowconfigure(0, weight=1)
        if buttons_space:
            self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.body.grid(row=0, column=0, padx=7, pady=7, sticky="nsew")
        self.buttons.grid(row=1, column=0, padx=7, pady=7, sticky="nsew")
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.update_idletasks()
        self.parent.update_idletasks()
        width = self.parent.winfo_x() + self.parent.winfo_width() // 2 - self.winfo_width() // 2
        height = self.parent.winfo_y() + self.parent.winfo_height() // 2 - self.winfo_height() // 2
        self.geometry(f"+{width}+{height}")
        self.initial_focus.focus_set()
        self.wait_window(self)

    def create_body(self):
        self.update_idletasks()
        return self.body

    def create_buttons(self):
        self.buttons.grid_columnconfigure(0, weight=1)
        self.buttons.grid_columnconfigure(1, weight=1)
        button = tk.Button(self.buttons, text="Ok", command=self.ok, relief=tk.RIDGE, borderwidth=4)
        button.grid(row=0, column=0, padx=6, pady=6, sticky="e")
        self.bind("<Escape>", self.cancel)
        button = tk.Button(self.buttons, text="Cancel", command=self.cancel, relief=tk.RIDGE, borderwidth=4)
        button.grid(row=0, column=1, padx=6, pady=6, sticky="w")

    def ok(self, _=None):
        if not self.validate():
            self.initial_focus.focus_set()
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()

    def cancel(self, _=None):
        self.parent.is_dialog_opened = False
        self.parent.focus_set()
        self.destroy()

    def validate(self):
        self.update_idletasks()
        return 1

    def apply(self):
        pass


class AttributesDialog(Dialog):

    def __init__(self, parent, title="Attributes"):
        self.info = []
        Dialog.__init__(self, parent, title, buttons_space=False)

    def create_body(self):
        self.frame = tk.LabelFrame(self.body, text="Attributes")
        self.frame.grid(row=0, column=0, sticky="news", padx=5, pady=5)
        i = 0
        for attribute in TextApp.gui["attributes background"]:
            type_ = list(attribute.keys())[0]
            background = attribute[type_]["background"]
            highlighted = attribute[type_]["highlighted"]
            tk.Label(self.frame, text=type_).grid(row=i, column=0, padx=32, pady=8)
            variable = tk.BooleanVar()
            variable.set(highlighted)
            checkbutton = tk.Checkbutton(self.frame, var=variable, command=self.toggle)
            checkbutton.variable = variable
            checkbutton.grid(row=i, column=1, padx=32, pady=8)
            label = tk.Label(self.frame, text=" " * 15, background=background, relief=tk.RIDGE, borderwidth=4)
            label.grid(row=i, column=2, padx=32, pady=8)
            label.type_ = type_
            label.bind("<Button-1>", self.change_color)
            self.frame.grid_rowconfigure(i, weight=1)
            self.info.append((checkbutton, label))
            i += 1
        tk.Button(self.frame, text="Set default", command=self.set_default, relief=tk.RIDGE,
                  borderwidth=4).grid(row=i, column=2, padx=10, pady=10)
        self.frame.grid_rowconfigure(i, weight=1)
        for i in (0, 1, 2):
            self.frame.grid_columnconfigure(i, weight=1)
        self.body.grid_rowconfigure(0, weight=1)
        self.body.grid_columnconfigure(0, weight=1)
        return self.body

    def toggle(self):
        info = []
        TextApp.gui["attributes background"] = []
        for checkbutton, label in self.info:
            type_ = label.type_
            highlighted = checkbutton.variable.get()
            background = label.cget("background")
            TextApp.gui["attributes background"].append({type_: {
                "highlighted": highlighted,
                "background": background
            }})
            info.append((type_, highlighted, background))
            TextApp.save_config()
        self.parent.highlight_attributes(
            list(map(lambda _: (_[1].type_, _[0].variable.get(), _[1].cget("background")), self.info)))

    def set_default(self):
        default = {
            "ZIUA": {
                "highlighted": True,
                "background": "#e3b740"
            },
            "ORA": {
                "highlighted": True,
                "background": "#8eed7e"
            },
            "DURATA": {
                "highlighted": True,
                "background": "#ba87e6"
            },
            "DATA": {
                "highlighted": True,
                "background": "#db747b"
            }
        }
        for checkbutton, label in self.info:
            highlighted = default[label.type_]["highlighted"]
            background = default[label.type_]["background"]
            if highlighted:
                checkbutton.select()
            else:
                checkbutton.deselect()
            label.configure(background=background)
        self.toggle()

    def change_color(self, event):
        _, color = tkinter.colorchooser.askcolor()
        if color:
            event.widget.configure(background=color)
            self.toggle()

    def create_buttons(self):
        pass


class PreferencesDialog(Dialog):

    def __init__(self, parent, title="Preferences"):
        self.label_frame = self.control_panel = self.options_panel = None
        Dialog.__init__(self, parent, title, buttons_space=False)

    def create_body(self):
        self.label_frame = tk.LabelFrame(self.body, text="Preferences")
        self.control_panel = PreferencesControlPanel(self.label_frame, self.parent)
        self.options_panel = PreferencesOptionsPanel(self.label_frame, control_panel=self.control_panel)
        self.label_frame.grid(sticky="nsew", padx=5, pady=5)
        self.options_panel.grid(row=0, column=0, padx=5, pady=5, sticky="nsw")
        self.control_panel.grid(row=0, column=1, padx=5, pady=5, sticky="nswe")
        self.label_frame.grid_rowconfigure(0, weight=1)
        self.label_frame.grid_columnconfigure(1, weight=1)
        self.body.grid_rowconfigure(0, weight=1)
        self.body.grid_columnconfigure(0, weight=1)
        self.bind("<MouseWheel>", lambda _: self.parent.set_dialog_open())
        return self.body

    def create_buttons(self):
        pass


class PreferencesOptionsPanel(tk.LabelFrame):

    def __init__(self, master, control_panel, *args, **kwargs):
        tk.LabelFrame.__init__(self, master, text="Options", background="white", *args, **kwargs)
        label = self.add_label("Color", True)
        self.add_label("Font")
        self.last_highlighted = label
        self.control_panel = control_panel
        self.grid_columnconfigure(0, weight=1)

    def add_label(self, text, highlighted=False):
        label = tk.Label(self, text=text)
        if highlighted:
            label.configure(background="lightgray")
        else:
            label.configure(background="white")
        label.grid(row=len(self.winfo_children()), column=0, sticky="new")
        label.bind("<Button-1>", self.click)
        return label

    def click(self, event):
        label = event.widget
        if self.last_highlighted:
            self.last_highlighted.configure(background=label.cget("background"))
        label.configure(background="lightgray")
        self.last_highlighted = label
        self.control_panel.show(label.cget("text"))


class PreferencesControlPanel(tk.Frame):

    def __init__(self, master, application, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.grid_propagate(False)
        self.color_panel = ColorPanel(self, application)
        self.font_panel = FontPanel(self, application)
        widths, heights = [], []
        for panel in (self.font_panel, self.color_panel):
            if type(panel) is ColorPanel:
                self.font_panel.grid_remove()
            panel.grid(row=0, column=0, sticky="news")
            panel.update_idletasks()
            heights.append(panel.winfo_height())
            widths.append(panel.winfo_width())
        self.configure(width=max(widths), height=max(heights))
        self.last = self.color_panel
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def show(self, panel_name):
        if self.last.panel_name != panel_name:
            self.last.grid_remove()
            for child in self.winfo_children():
                if child.panel_name == panel_name:
                    child.grid(row=0, column=0, sticky="news")
                    self.last = child
                    break


class ColorPanel(tk.LabelFrame):

    def __init__(self, master, application, panel_name="Color", *args, **kwargs):
        tk.LabelFrame.__init__(self, master, text="Color", background="white", *args, **kwargs)
        self.panel_name = panel_name
        self.application = application
        tk.Label(self, text="Change the background of the application",
                 background=self.cget("background")).grid(row=0, column=0, padx=10, pady=10)
        self.view_background_label = tk.Label(self, text=" " * 15, background=TextApp.gui["view background"],
                                              relief=tk.RIDGE, borderwidth=4)
        self.view_background_label.grid(row=0, column=1, padx=10, pady=10)
        self.view_background_label.bind("<Button-1>", self.change_background)
        tk.Label(self, text="Change the background of the labels", background=self.cget("background")).grid(row=1,
                                                                                                            column=0,
                                                                                                            padx=10,
                                                                                                            pady=10)
        self.label_background = tk.Label(self, text=" " * 15, background=TextApp.gui["label background"],
                                         relief=tk.RIDGE, borderwidth=4)
        self.label_background.grid(row=1, column=1, padx=10, pady=10)
        self.label_background.bind("<Button-1>", self.change_label_background)
        tk.Label(self, text="Change the foreground of the labels", background=self.cget("background")).grid(row=2,
                                                                                                            column=0,
                                                                                                            padx=10,
                                                                                                            pady=10)
        self.label_foreground = tk.Label(self, text=" " * 15, background=TextApp.gui["label foreground"],
                                         relief=tk.RIDGE, borderwidth=4)
        self.label_foreground.grid(row=2, column=1, padx=10, pady=10)
        self.label_foreground.bind("<Button-1>", self.change_label_foreground)
        tk.Button(self, text="Set default", command=self.set_default, relief=tk.RIDGE, borderwidth=4).grid(row=3,
                                                                                                           column=1,
                                                                                                           padx=10,
                                                                                                           pady=10)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def change_background(self, _):
        _, color = tkinter.colorchooser.askcolor()
        if color:
            TextApp.gui["view background"] = color
            self.view_background_label.configure(background=color)
            self.application.set_background()
            TextApp.save_config()

    def change_label_background(self, _):
        _, color = tkinter.colorchooser.askcolor()
        if color:
            TextApp.gui["label background"] = color
            self.label_background.configure(background=color)
            self.application.update_labels_background()
            TextApp.save_config()

    def change_label_foreground(self, _):
        _, color = tkinter.colorchooser.askcolor()
        if color:
            TextApp.gui["label foreground"] = color
            self.label_foreground.configure(background=color)
            self.application.update_labels_foreground()
            TextApp.save_config()

    def set_default(self):
        TextApp.gui["view background"] = "lightblue"
        TextApp.gui["label background"] = "lavender"
        TextApp.gui["label foreground"] = "black"
        self.view_background_label.configure(background=TextApp.gui["view background"])
        self.label_background.configure(background=TextApp.gui["label background"])
        self.label_foreground.configure(background=TextApp.gui["label foreground"])
        self.application.set_background()
        self.application.update_labels_background()
        self.application.update_labels_foreground()
        TextApp.save_config()


class FontPanel(tk.LabelFrame):

    def __init__(self, master, application, panel_name="Font", *args, **kwargs):
        tk.LabelFrame.__init__(self, master, text="Font", background="white", *args, **kwargs)
        self.panel_name = panel_name
        self.application = application
        font_families = sorted(tkinter.font.families())
        tk.Label(self, text="Change the visible labels font", background=self.cget("background")).grid(row=0,
                                                                                                       column=0,
                                                                                                       padx=10, pady=10)
        self.visible_label_font_combobox = ttk.Combobox(self, values=font_families, state="readonly")
        self.visible_label_font_combobox.set(TextApp.gui["visible label font"][0])
        self.visible_label_font_combobox.bind("<<ComboboxSelected>>", self.change_visible_label_font)
        self.visible_label_font_combobox.unbind_class("TCombobox", "<MouseWheel>")
        self.visible_label_font_combobox.grid(row=0, column=1, padx=10, pady=10)
        tk.Label(self, text="Change the visible labels font size", background=self.cget("background")).grid(row=1,
                                                                                                            column=0,
                                                                                                            padx=10,
                                                                                                            pady=10)
        self.visible_label_font_size_combobox = ttk.Combobox(self, values=[_ for _ in range(8, 41)], state="readonly")
        self.visible_label_font_size_combobox.set(TextApp.gui["visible label font"][1])
        self.visible_label_font_size_combobox.bind("<<ComboboxSelected>>", self.change_visible_label_font)
        self.visible_label_font_size_combobox.grid(row=1, column=1, padx=10, pady=10)
        tk.Label(self, text="Change the collapsed labels font", background=self.cget("background")).grid(row=2,
                                                                                                         column=0,
                                                                                                         padx=10,
                                                                                                         pady=10)
        self.collapsed_label_font_combobox = ttk.Combobox(self, values=font_families, state="readonly")
        self.collapsed_label_font_combobox.set(TextApp.gui["collapsed label font"][0])
        self.collapsed_label_font_combobox.bind("<<ComboboxSelected>>", self.change_collapsed_label_font)
        self.collapsed_label_font_combobox.grid(row=2, column=1, padx=10, pady=10)
        tk.Label(self, text="Change the collapsed labels font size", background=self.cget("background")).grid(row=3,
                                                                                                              column=0,
                                                                                                              padx=10,
                                                                                                              pady=10)
        self.collapsed_label_font_size_combobox = ttk.Combobox(self, values=[_ for _ in range(8, 41)], state="readonly")
        self.collapsed_label_font_size_combobox.set(TextApp.gui["collapsed label font"][1])
        self.collapsed_label_font_size_combobox.bind("<<ComboboxSelected>>", self.change_collapsed_label_font)
        self.collapsed_label_font_size_combobox.grid(row=3, column=1, padx=10, pady=10)
        tk.Label(self, text="Change the source font", background=self.cget("background")).grid(row=4, column=0,
                                                                                               padx=10, pady=10)
        self.source_font_combobox = ttk.Combobox(self, values=font_families, state="readonly")
        self.source_font_combobox.set(TextApp.gui["source font"][0])
        self.source_font_combobox.bind("<<ComboboxSelected>>", self.change_source_font)
        self.source_font_combobox.grid(row=4, column=1, padx=10, pady=10)
        tk.Label(self, text="Change the source font size", background=self.cget("background")).grid(row=5, column=0,
                                                                                                    padx=10, pady=10)
        self.source_font_size_combobox = ttk.Combobox(self, values=[_ for _ in range(8, 41)], state="readonly")
        self.source_font_size_combobox.set(TextApp.gui["source font"][1])
        self.source_font_size_combobox.bind("<<ComboboxSelected>>", self.change_source_font)
        self.source_font_size_combobox.grid(row=5, column=1, padx=10, pady=10)
        tk.Button(self, text="Set default", command=self.set_default, relief=tk.RIDGE, borderwidth=4).grid(row=6,
                                                                                                           column=1,
                                                                                                           padx=10,
                                                                                                           pady=10)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def change_visible_label_font(self, _=None):
        TextApp.gui["visible label font"] = [self.visible_label_font_combobox.get(),
                                             self.visible_label_font_size_combobox.get()]
        self.application.update_visible_label_font()
        TextApp.save_config()

    def change_collapsed_label_font(self, _=None):
        TextApp.gui["collapsed label font"] = [self.collapsed_label_font_combobox.get(),
                                               self.collapsed_label_font_size_combobox.get()]
        self.application.update_collapsed_label_font()
        TextApp.save_config()

    def change_source_font(self, _=None):
        TextApp.gui["source font"] = [self.source_font_combobox.get(), self.source_font_size_combobox.get()]
        self.application.text_view.text.configure(font=TextApp.gui["source font"])
        TextApp.save_config()

    def set_default(self):
        TextApp.gui["visible label font"] = ("Consolas", 12)
        TextApp.gui["collapsed label font"] = ("Consolas", 8)
        TextApp.gui["source font"] = ("Consolas", 11)
        self.visible_label_font_combobox.set(TextApp.gui["visible label font"][0])
        self.visible_label_font_size_combobox.set(TextApp.gui["visible label font"][1])
        self.collapsed_label_font_combobox.set(TextApp.gui["collapsed label font"][0])
        self.collapsed_label_font_size_combobox.set(TextApp.gui["collapsed label font"][1])
        self.source_font_combobox.set(TextApp.gui["source font"][0])
        self.source_font_size_combobox.set(TextApp.gui["source font"][1])
        self.application.update_visible_label_font()
        self.application.update_collapsed_label_font()
        self.application.text_view.text.configure(font=TextApp.gui["source font"])
        TextApp.save_config()


class EditDialog(Dialog):

    def __init__(self, parent, title="Edit", label_text="", initial_value="", height=5, width=30):
        self.label_text = label_text
        self.entry = None
        self.initial_value = initial_value
        self.width = width
        self.height = height
        Dialog.__init__(self, parent, title, buttons_space=False)

    def create_body(self):
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_rowconfigure(1, weight=1)
        tk.Label(self.body, text=self.label_text).grid(row=0, column=0, sticky="s", padx=3, pady=3)
        self.entry = tk.Text(self.body, height=self.height, width=self.width, wrap=tk.NONE, relief=tk.RIDGE,
                             borderwidth=4)
        self.entry.bind("<MouseWheel>", lambda _: self.parent.set_dialog_open())
        y_scroll = tk.Scrollbar(self.body, command=self.entry.yview)
        y_scroll.grid(row=1, column=1, sticky="ns")
        x_scroll = tk.Scrollbar(self.body, orient=tk.HORIZONTAL, command=self.entry.xview)
        x_scroll.grid(row=2, column=0, sticky="we")
        self.entry.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.entry.grid(row=1, column=0, sticky="nswe", padx=3, pady=3)
        self.entry.insert(tk.END, self.initial_value)
        return self.entry

    def apply(self):
        self.response = self.entry.get(1.0, tk.END)[:-1]
        if self.response[-1] == "\n":
            self.response = self.response[:-1]


class FooterFrame(tk.Frame):

    def __init__(self, master, node, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        label = tk.Label(self, text=f"</{node.tag}>", justify=tk.LEFT, background=TextApp.gui["label background"],
                         font=TextApp.gui["visible label font"], foreground=TextApp.gui["label foreground"])
        label.grid(row=0, column=0, sticky="nw")
        self.grid(row=len(self.master.winfo_children()), column=0, sticky="nw",
                  padx=TextApp.gui["content frame intern padx"],
                  pady=TextApp.gui["content frame intern pady"])

    def update_labels_background(self):
        for child in self.winfo_children():
            if type(child) is tk.Label:
                child.configure(background=TextApp.gui["label background"])

    def update_labels_foreground(self):
        for child in self.winfo_children():
            if type(child) is tk.Label:
                child.configure(foreground=TextApp.gui["label foreground"])


class TextFrame(tk.Frame):

    def __init__(self, master, text, *args, **kwargs):
        tk.Frame.__init__(self, master, background=TextApp.gui["view background"], *args, **kwargs)
        label = tk.Label(self, text=text, font=TextApp.gui["visible label font"],
                         background=TextApp.gui["label background"],
                         foreground=TextApp.gui["label foreground"], justify=tk.LEFT)
        label.grid(row=0, column=1, sticky="nw", padx=TextApp.gui["content frame intern padx"],
                   pady=TextApp.gui["content frame intern pady"])
        label.type = "tag text"
        label.value = text
        label.bind("<Button-3>", self.master.header_frame.right_click)
        row = len(master.winfo_children())
        self.grid(row=row, column=0, sticky="nw", padx=TextApp.gui["content frame padx"],
                  pady=TextApp.gui["content frame intern pady"])

    def update_labels_background(self):
        for child in self.winfo_children():
            if type(child) is tk.Label:
                child.configure(background=TextApp.gui["label background"])

    def update_labels_foreground(self):
        for child in self.winfo_children():
            if type(child) is tk.Label:
                child.configure(foreground=TextApp.gui["label foreground"])


class View(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        canvas = tk.Canvas(self, bg=TextApp.gui["view background"], bd=0, highlightthickness=0, relief='ridge')
        self.canvas = canvas
        self.frame = ContentFrame(canvas)
        y_scroll = tk.Scrollbar(self, command=canvas.yview)
        x_scroll = tk.Scrollbar(self, command=canvas.xview, orient=tk.HORIZONTAL)
        canvas.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set, scrollregion=canvas.bbox(tk.ALL))
        canvas.grid(row=0, column=0, sticky="news")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="we")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        def scroll(event):
            if not self.winfo_toplevel().is_dialog_opened and type(event.widget) is not str:
                start, end = canvas.yview()
                if start != 0 or end != 1:
                    canvas.yview_scroll(-event.delta // 100, "units")
                    return
                start, end = canvas.xview()
                if start != 0 or end != 1:
                    canvas.xview_scroll(-event.delta // 100, "units")
            self.winfo_toplevel().set_dialog_open(False)

        canvas.bind_all("<MouseWheel>", scroll)
        self.frame.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox(tk.ALL)))
        canvas.create_window((0, 0), window=self.frame, anchor="nw")
        canvas.scroll = scroll


def write_xml(dictionary, file_descriptor, indent=0):
    spacing = indent * 4 * " "
    header = dictionary["header"]
    text = dictionary["text"]
    contents = dictionary["contents"]
    tag = header["tag"]
    attributes = header["attributes"]
    string = spacing + "<" + tag
    end = "/>" if not text and not contents else ">"
    if not text and not contents and not attributes:
        end = f" {end}"
    middle = ""
    for attribute, value in attributes:
        middle += f" {attribute}=\"{value}\""
    string += middle + end + "\n"
    if text:
        text = text.replace("\n", "\n" + spacing + 4 * " ")
        string += spacing + 4 * " " + text + "\n"
    file_descriptor.write(string)
    for content in contents:
        write_xml(content, file_descriptor, indent + 1)
    if text or contents:
        string = f"{spacing}</{tag}>\n"
        file_descriptor.write(string)


def save_xml(path, dictionary):
    with open(path, "w") as file_descriptor:
        file_descriptor.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        write_xml(dictionary, file_descriptor)


if __name__ == "__main__":
    TextApp()
