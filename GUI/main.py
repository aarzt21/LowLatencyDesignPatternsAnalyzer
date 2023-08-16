

from model import *
from view import *
import customtkinter as ctk
ctk.set_appearance_mode("dark")

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color="grey11")

        #expand grid in both dimensions
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.model = Model(application=self)
        self.view = View(master=self, model = self.model)
        self.view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.model.set_view(self.view)

        self.geometry("1100x1000")
        self.title("C++ Low Latency Design Patterns Analyzer")


app = App()
app.mainloop()
