import tkinter
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Separator
from xml.etree import ElementTree
from tkinter.simpledialog import askstring
from PARSARE import proiect


class TextApp(Tk):

    APPLICATION_TITLE = "Time recognizer"
    GLOBAL_FONT = ("Consolas", 11)
    VIEW_BACKGROUND = "lightblue"
    CONTENT_FRAME_PADX = 50
    CONTENT_FRAME_PADY = 4
    CONTENT_FRAME_INTERN_PADX = 4
    CONTENT_FRAME_INTERN_PADY = 4
    VISIBLE_LABEL_FONT = ("Consolas", 12)
    HIDDEN_LABEL_FONT = ("Consolas", 6)

    def __init__(self):
        super().__init__()
        self.title(TextApp.APPLICATION_TITLE)
        self.state("zoomed")
        self.option_add("*Font", TextApp.GLOBAL_FONT)
        self.toolbar = Toolbar(self)
        self.toolbar.grid(row=0, column=0, sticky="we", padx=5, pady=5)
        Separator(self).grid(row=1, column=0, pady=5, padx=5, sticky="we")
        self.view = View(self)
        self.view.grid(row=2, column=0, pady=5, padx=5, sticky="nswe")
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.mainloop()

    def display(self, root):
        frame = self.view.frame
        frame.display_node(root, do_grid=False)


class ContentFrame(Frame):

    def __init__(self, master, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)
        self.configure(bg=TextApp.VIEW_BACKGROUND)
        self.visible = True
        self.header_frame, self.footer_frame, self.text_frame, self.contents = [None for _ in range(4)]

    def display_node(self, node, padx=TextApp.CONTENT_FRAME_PADX, pady=TextApp.CONTENT_FRAME_PADY, do_grid=True):
        self.header_frame = HeaderFrame(self, node)
        text = node.text
        stripped_text = text.strip() if text else text
        self.text_frame = TextFrame(self, text) if text and stripped_text else None
        self.contents = []
        if len(node):
            for child in node:
                frame = ContentFrame(self)
                frame.display_node(child)
                self.contents.append(frame)
        self.footer_frame = FooterFrame(self, node)
        if do_grid:
            self.grid(row=len(self.master.winfo_children()), column=0, padx=padx, pady=pady, sticky="nw")

    def collapse(self):
        if self.visible:
            for child in self.winfo_children()[1:]:
                child.grid_remove()
            for child in self.header_frame.winfo_children():
                child.configure(font=TextApp.HIDDEN_LABEL_FONT)
        else:
            for child in self.winfo_children()[1:]:
                child.grid()
            for child in self.header_frame.winfo_children():
                child.configure(font=TextApp.VISIBLE_LABEL_FONT)
        self.visible = not self.visible


class HeaderFrame(Frame):

    def __init__(self, master, node, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)
        self.configure(background=TextApp.VIEW_BACKGROUND)
        tag, attributes = node.tag, node.attrib
        font = TextApp.VISIBLE_LABEL_FONT
        padx, pady = TextApp.CONTENT_FRAME_INTERN_PADX, TextApp.CONTENT_FRAME_INTERN_PADY
        label = Label(self, text=f"<{tag}", font=font)
        label.grid(row=0, column=1, sticky="nw", padx=padx, pady=pady)
        self.tag_menu = Menu(label, tearoff=0)
        self.tag_menu.add_command(label="Collapse", command=self.master.collapse)

        self.attribute_menu = Menu(label, tearoff=0)
        self.attribute_menu.add_command(label="Edit", command=self.edit)
        self.attribute_menu.add_command(label="Collapse", command=self.master.collapse)
        label.bind("<Button-3>", self.right_click)
        if not attributes:
            label.configure(text=label.cget("text") + ">")
        for attribute in attributes:
            label = Label(self, text=f"{attribute}={attributes[attribute]}", font=font)
            label.grid(row=0, column=len(self.winfo_children()), sticky="nw", padx=padx, pady=pady)
            label.bind("<Button-3>", self.right_click)
            label.type = attribute
            label.value = attributes[attribute]
        if attributes:
            label = Label(self, text=">", font=font)
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
        label_type, label_value = label.type, label.value
        response = askstring("Edit", f"Change {label_type}", initialvalue=label_value,
                             parent=self.winfo_toplevel())
        if response:
            label.value = response
            if label_type != "tag text":
                label.configure(text=f"{label_type}={response}")
            else:
                label.configure(text=response)


class FooterFrame(Frame):

    def __init__(self, master, node, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)
        label = Label(self, text=f"</{node.tag}>", font=TextApp.VISIBLE_LABEL_FONT)
        label.grid(row=0, column=0, sticky="nw")
        self.grid(row=len(self.master.winfo_children()), column=0, sticky="nw", padx=TextApp.CONTENT_FRAME_INTERN_PADX,
                  pady=TextApp.CONTENT_FRAME_INTERN_PADY)


class TextFrame(Frame):

    def __init__(self, master, text, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)

        label = Label(self, text=text, font=TextApp.VISIBLE_LABEL_FONT)
        label.grid(row=0, column=1, sticky="nw", padx=TextApp.CONTENT_FRAME_INTERN_PADX,
                   pady=TextApp.CONTENT_FRAME_INTERN_PADY)
        label.type = "tag text"
        label.value = text
        label.bind("<Button-3>", self.master.header_frame.right_click)
        row = len(master.winfo_children())
        self.grid(row=row, column=0, sticky="nw",
                  padx=TextApp.CONTENT_FRAME_PADX, pady=TextApp.CONTENT_FRAME_INTERN_PADY)


class Toolbar(Frame):

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        Button(self, text="Browse", command=self.browse).grid(row=0, column=0)

    def browse(self):
        filename = tkinter.filedialog.askopenfilename(filetypes=[("txt files", "*.txt")])
        if filename:
            self.master.title(f"{TextApp.APPLICATION_TITLE} - {filename}")
            proiect.setare_input(filename)
            proiect.rulare(False)
            with open(r"..\..\output\exemplu.xml") as xml_file:
                tree = ElementTree.parse(xml_file)
                self.master.display(tree.getroot())


class View(Frame):

    def __init__(self, master):
        super().__init__(master)
        canvas = Canvas(self, bg=TextApp.VIEW_BACKGROUND, bd=0, highlightthickness=0, relief='ridge')
        self.canvas = canvas
        self.frame = ContentFrame(canvas)
        y_scroll = Scrollbar(self, command=canvas.yview)
        x_scroll = Scrollbar(self, command=canvas.xview, orient=HORIZONTAL)
        canvas.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set, scrollregion=canvas.bbox(ALL))
        canvas.grid(row=0, column=0, sticky="nswe")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="we")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        def scroll(event):
            start, end = canvas.yview()
            if start != 0 or end != 1:
                canvas.yview_scroll(-event.delta // 100, "units")
                return
            start, end = canvas.xview()
            if start != 0 or end != 1:
                canvas.xview_scroll(-event.delta // 100, "units")

        canvas.bind_all("<MouseWheel>", scroll)
        self.frame.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox(ALL)))
        canvas.create_window((0, 0), window=self.frame, anchor="nw")


my_gui = TextApp()
