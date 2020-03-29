import tkinter
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Separator

# initializarea ferestrei main


class TextApp:
    def __init__(self):
        # creeam window
        self.gui = Tk()  # titlul aplicatiei

        # title cred ca este mai bun decat className fiindca
        # desi className="TILN - Recognize time" aplicatia avea titlul "tILN - Recognize time"
        # nu stiu de ce primul caracter este transformat lowercase
        self.gui.title("TILN - Recognize time")
        # full screen
        self.gui.state("zoomed")

        # setam fontul global
        self.gui.option_add("*Font", ("Consolas", "13"))

        # ar fi mai bine sa lasam butonul sa-si modifice dimensiunea in functie de font
        self.browse = Button(self.gui, text="Browse", command=self.file_dialog)
        self.browse.grid(row=0, column=0, pady=5, padx=5, sticky="nw")
        # am adaugat padx si pady pentru a nu parea inghesuita interfata
        # sticky="nw" face butonul sa ramana sus in drepta
        Separator(self.gui).grid(row=1, column=0, pady=5, padx=5, sticky="we")

        # este mai bine sa lasam tkinterul sa se ocupe de dimensiunea exacta
        # fiindca se ia in considerare si redimensionarea ferestrei
        self.frame_time = Frame(self.gui, background="white")
        # din nou inlocuim place cu grid din acelasi motiv
        self.frame_time.grid(row=2, column=0, sticky="nsew", pady=5, padx=5)

        # vrem ca partea principala a aplicatiei sa ocupe cat mai mult din ecran
        self.gui.grid_rowconfigure(2, weight=1)
        self.gui.grid_columnconfigure(0, weight=1)
        self.gui.mainloop()

    def file_dialog(self):
        # cred ca in cazul nostru askopenfilename este mai bun decat askopenfile
        # fiindca nu trebuie sa mai specificam modul de deschidere;
        # adaugam constrangerea sa se poata deschide doar fisiere xml;
        # functia returneaza numele fisierului ales;
        # daca utilizatorul da Cancel returneaza "";
        filename = tkinter.filedialog.askopenfilename(filetypes=[("xml files", "*.xml")])

        if filename:
            # adaugam numele fisierului deschis la titlul aplicatiei in maniera Notepad din Windows
            self.gui.title(f"TILN - Recognize time - {filename}")
            with open(filename) as file_descriptor:
                self.display(file_descriptor.read())

    def display(self, contents):
        # aici trebuie afisat
        pass


my_gui = TextApp()
