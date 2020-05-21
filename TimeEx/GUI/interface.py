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
# Tools -> Expand all: Da expand la toate elementele collapsed
# Tools -> Attributes: Se pot alege culorile elementelor si cuvintelor in text cu anumite tipuri si 
# se poate da toggle la visibilitatea lor
# Tools -> Preferences: Se poate alege: background ul aplicatiei
#                                       background ul si foreground ul label urilor
#                                       fontul si marimea lui pentru label urile visibile
#                                       fontul si marimea lui pentru label urile collapsed
#                                       fontul si marimea lui pentru label urile visibile


tiln_directory = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
path_dictionary = {
    "tiln directory": tiln_directory,
    "gui directory": os.path.join(tiln_directory, "GUI"),
    "input directory": os.path.join(tiln_directory, "input"),
    "output directory": os.path.join(tiln_directory, "output"),
    "parsing directory": os.path.join(tiln_directory, "PARSARE"),
    "xml directory": os.path.join(tiln_directory, "XML")
}

sys.path = list(set(sys.path + list(path_dictionary.values())))

from TimeEx.PARSARE import proiect


def read_config(path=os.path.join(path_dictionary["gui directory"], "guiconfig.json")):
    with open("TimeEx/GUI/guiconfig.json", "r") as file_descriptor:
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
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="news")
        self.view = View(self)
        self.view.grid(row=0, column=0, pady=5, padx=5, sticky="news")
        self.notebook.add(self.view, text="Xml")
        self.text_view = None
        OptionsView(self).grid(row=0, column=0, pady=5, padx=5, sticky="news")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.config_bind()
        self.mainloop()

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
                self.xml_path = r"output\exemplu.xml"
                self.opened_file = filename
                self.title(f"{TextApp.gui['application title']} - {filename} - {self.xml_path}")
                with open(self.xml_path) as xml_file:
                    tree = xml.etree.ElementTree.parse(xml_file)
                    self.display(tree.getroot())
                    self.highlight_attributes()
                if len(self.notebook.tabs()) == 1:
                    self.text_view = TextView(self)
                    self.notebook.add(self.text_view, text="Text")
                self.text_view.set(self.opened_file)
        except TypeError as exception:

            tkinter.messagebox.showerror("Exception", str(exception))

    def set_background(self):
        self.view.canvas.configure(background=TextApp.gui["view background"])
        self.view.frame.set_background()

    def highlight_attributes(self):
        self.view.frame.highlight_attributes()
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
            if type_ in TextApp.gui["attributes background"] and TextApp.gui["attributes background"][type_]["highlighted"]:
                background = TextApp.gui["attributes background"][type_]["background"]
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
            if type_ in TextApp.gui["attributes background"] and TextApp.gui["attributes background"][type_]["highlighted"]:
                background = TextApp.gui["attributes background"][type_]["background"]
            if None not in (type_, value_, background):
                texts.append((value_, background))
            if content["contents"]:
                texts.extend(TextApp.get_texts_from_contents(content["contents"]))
        return texts

    @staticmethod
    def save_config():
        with open(os.path.join(path_dictionary["gui directory"], "guiconfig.json"), "w") as file_descriptor:
            json.dump(TextApp.gui, file_descriptor, indent=4)

    @staticmethod
    def create_button(master, image, tooltip=None, *args, **kwargs):
        image = tk.PhotoImage(file=os.path.join(path_dictionary["gui directory"], "icons", image))
        button = tk.Button(master, image=image, relief=tk.SOLID, *args, **kwargs)
        button.image = image
        if tooltip:
            ToolTip(button, tooltip)
        return button


# sursa: https://stackoverflow.com/a/36221216
class ToolTip(object):

    def __init__(self, widget, text=None):
        self.waittime = 500
        self.wraplength = 180
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, _=None):
        self.schedule()

    def leave(self, _=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, _=None):
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify=tk.LEFT, background="#ffffff", relief=tk.RIDGE, borderwidth=2,
                         wraplength=self.wraplength, font=TextApp.gui["tooltip font"])
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()


class OptionsView(tk.Frame):

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.font_dictionary =  {
            "Visible xml label font": ("visible label font", self.master.update_visible_label_font),
            "Collapsed xml label font": ("collapsed label font", self.master.update_collapsed_label_font),
            "Text font": ("source font", lambda: self.master.text_view.text.configure(font=TextApp.gui["source font"]) if self.master.text_view else False)
        }
        TextApp.create_button(self, "open.png", tooltip="Open file and extract from it",
                              command=self.master.browse).grid(row=0, column=len(self.winfo_children()), sticky="w", padx=3)
        TextApp.create_button(self, "save.png", tooltip="Save",
                            command=self.master.save).grid(row=0, column=len(self.winfo_children()), sticky="w", padx=3)
        self.add_color_settings("xml background.png", "Change xml background", lambda: self.change_color("view background", self.master.set_background))
        self.add_color_settings("xml label background.png", "Change xml label background", lambda: self.change_color("label background", self.master.update_labels_background))
        self.add_color_settings("xml label foreground.png", "Change xml label foreground", lambda: self.change_color("label foreground", self.master.update_labels_foreground))
        self.add_color_settings("expand.png", "Expand all collapsed labels", self.master.view.frame.expand_all)
        self.add_separator()
        self.add_attribute_options("ZIUA")
        self.add_attribute_options("DURATA")
        self.add_attribute_options("ORA")
        self.add_attribute_options("DATA")
        self.add_separator()
        self.add_font_settings()

    def add_font_settings(self):
        font_families = sorted(tkinter.font.families())
        font_options = list(self.font_dictionary.keys())
        self.choose_font_combobox = ttk.Combobox(self, values=font_options, state="readonly", width=max(map(lambda _: len(_), font_options)))
        self.choose_font_combobox.grid(row=0, column=len(self.winfo_children()), padx=3)
        self.choose_font_combobox.bind("<<ComboboxSelected>>", self.show_font)
        self.choose_font_combobox.set(font_options[0])
        self.choose_font_combobox.unbind_class("TCombobox", "<MouseWheel>")
        self.choose_family_combobox = ttk.Combobox(self, values=font_families, state="readonly", width=20)
        self.choose_family_combobox.bind("<<ComboboxSelected>>", self.change_font)
        self.choose_family_combobox.set(TextApp.gui[self.font_dictionary[self.choose_font_combobox.get()][0]][0])
        self.choose_family_combobox.grid(row=0, column=len(self.winfo_children()), padx=3)
        self.choose_size_combobox = ttk.Combobox(self, values=list(range(8, 41)), state="readonly", width=2)
        self.choose_size_combobox.bind("<<ComboboxSelected>>", self.change_font)
        self.choose_size_combobox.set(TextApp.gui[self.font_dictionary[self.choose_font_combobox.get()][0]][1])
        self.choose_size_combobox.grid(row=0, column=len(self.winfo_children()), padx=3)

    def change_font(self, _):
        font_family = self.choose_family_combobox.get()
        font_size = self.choose_size_combobox.get()
        key, method = self.font_dictionary[self.choose_font_combobox.get()]
        TextApp.gui[key] = (font_family, font_size)
        self.master.save_config()
        method()

    def show_font(self, _):
        font = TextApp.gui[self.font_dictionary[self.choose_font_combobox.get()][0]]
        self.choose_family_combobox.set(font[0])
        self.choose_size_combobox.set(font[1])

    def change_color(self, key, method):
        _, color = tkinter.colorchooser.askcolor()
        if color:
            TextApp.gui[key] = color
            method()
            TextApp.save_config()

    def add_attribute_options(self, attribute):
        tk.Label(self, text=attribute).grid(row=0, column=len(self.winfo_children()), sticky="w", padx=3)
        background = TextApp.gui["attributes background"][attribute]["background"]
        button = TextApp.create_button(self, "palette.png", tooltip="Change background", background=background, width=64, activebackground=background)
        button.configure(command=lambda: self.change_attribute_color(button))
        children_count = len(self.winfo_children())
        button.grid(row=0, column=children_count + 1, sticky="w", padx=3)
        button.type_ = attribute
        variable = tk.BooleanVar()
        variable.set(TextApp.gui["attributes background"][attribute]["highlighted"])
        checkbutton = tk.Checkbutton(self, var=variable, command=lambda: self.toggle_attributes(button))
        checkbutton.variable = variable
        checkbutton.grid(row=0, column=children_count, sticky="w", padx=3)
        ToolTip(checkbutton, "Toggle visibility")
        button.checkbutton = checkbutton

    def add_color_settings(self, image, tooltip, command):
        TextApp.create_button(self, image, tooltip=tooltip, command=command).grid(row=0, column=len(self.winfo_children()), sticky="w", padx=3)

    def add_separator(self):
        tkinter.ttk.Separator(self, orient=tk.VERTICAL).grid(row=0, column=len(self.winfo_children()), sticky='ns')

    def toggle_attributes(self, button):
        type_ = button.type_
        dictionary = TextApp.gui["attributes background"][type_]
        dictionary["highlighted"] = button.checkbutton.variable.get()
        dictionary["background"] = button.cget("background")
        TextApp.save_config()
        self.master.highlight_attributes()

    def change_attribute_color(self, button):
        _, color = tkinter.colorchooser.askcolor()
        if color:
            button.configure(background=color)
            self.toggle_attributes(button)


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
        with open(path, "r", encoding="utf=8") as file_descriptor:
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

    def highlight_attributes(self):
        if self.header_frame:
            header_frame_type = self.header_frame.get_type()
            if header_frame_type in TextApp.gui["attributes background"] and TextApp.gui["attributes background"][header_frame_type]["highlighted"]:
                self.highlight(TextApp.gui["attributes background"][header_frame_type]["background"])
                self.is_highlighted = True
            else:
                self.reset()
                self.is_highlighted = False
            for child in self.winfo_children():
                if type(child) is ContentFrame:
                    child.highlight_attributes()

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
