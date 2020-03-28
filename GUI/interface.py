import tkinter
from tkinter import *
from tkinter import filedialog

# initializarea ferestrei main

class TextApp:
    def __init__(self):
        """
        gui fereastra principala
        """
        self.gui = Tk(className="TILN - Recognize time")  # titlul aplicatiei
        self.gui.geometry("500x500")  # size

        """
        butonul pentru browse 
        """
        self.browse = Button(self.gui, text="Browse", width=15, height=2, command=self.file_dialog)
        self.browse.grid(row=0, column=0)


        """
        frame pentru afisare date timp
        """
        self.frame_time = Frame(self.gui, width=290, height=400, background="white")
        self.frame_time.place(x=200, y=10)

        self.gui.mainloop()



    """
    In functia asta apelam file dialog
    * aux.name = pathul 
    * w = label unde afisam pathul
    """
    def file_dialog(self):
        aux = tkinter.filedialog.askopenfile(mode="r")
        w = Label(self.gui, text=aux.name)
        w.grid(row=1, column=0)


my_gui = TextApp()
