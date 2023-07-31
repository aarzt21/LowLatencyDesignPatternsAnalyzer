import customtkinter as ctk
import subprocess
from pygments import highlight
import time
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
from tkinter import filedialog, END, StringVar, BooleanVar
import glob
import shutil

class View(ctk.CTkTabview):

    def __init__(self, master, model):
        super().__init__(master, fg_color="grey11")

        self.model = model
        # Analysis Tab ===============================================================================
        analyze_tab = self.add("Analyze")

        top_frame = ctk.CTkFrame(master=analyze_tab)
        top_frame.pack(pady = (20, 20), fill="both", expand = True)
        
        top_left_frame = ctk.CTkFrame(master=top_frame)
        top_left_frame.pack(side="left", fill="both", expand=False)

        dir_label = ctk.CTkLabel(master=top_left_frame, text="Directory", font=("Arial", 20, 'bold'))
        dir_label.pack(pady=(80, 10), padx=10)

        self.dir_entry = ctk.CTkEntry(master=top_left_frame, placeholder_text="Directory Path", font=("Arial", 20))
        self.dir_entry.pack(pady=10, padx=10, ipady=10)

        main_file_label = ctk.CTkLabel(master=top_left_frame, text="Main File", font=("Arial", 20, 'bold'))
        main_file_label.pack(pady=10, padx=10)
        self.main_file_var = StringVar()
        self.main_file_combobox = ctk.CTkComboBox(master=top_left_frame, font=("Arial", 20))
        self.main_file_combobox.pack(pady=10, padx=10)
        self.main_file_combobox.set('')

        button_0 = ctk.CTkButton(master=top_left_frame, command=self.model.open_directory_dialog, text="Open Project", font=("Arial", 20))
        button_0.pack(pady=50, padx=10, ipady=10)

        top_middle_frame = ctk.CTkFrame(master=top_frame)
        top_middle_frame.pack(side="left", fill="both", expand=True)

        additional_files_label = ctk.CTkLabel(master=top_middle_frame, text="Additional C++ Source Files", font=("Arial", 20, 'bold'))
        additional_files_label.pack(pady=(20,5), padx=10, fill = "both")

        self.additional_files_switches = []

        self.scrollable_frame = ctk.CTkScrollableFrame(master=top_middle_frame, fg_color="grey15")
        self.scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)

        top_right_frame = ctk.CTkFrame(master=top_frame)
        top_right_frame.pack(side="left", fill="both", expand=False)

        top_right_frame.grid_rowconfigure(0, weight=1)
        top_right_frame.grid_columnconfigure(0, weight=1)
        top_right_frame.grid_columnconfigure(1, weight=1)

        for i in range(5):
            top_right_frame.grid_rowconfigure(i, weight=1)

        self.crtp_var = BooleanVar()
        self.crtp_check = ctk.CTkCheckBox(master=top_right_frame, text='CRTP', variable=self.crtp_var, font=("Arial", 22))
        self.crtp_check.grid(row=0, column=0, padx=10, pady=(40, 0), sticky="w")

        self.tbbe_var = BooleanVar()
        self.tbbe_check = ctk.CTkCheckBox(master=top_right_frame, text='TBBE', variable=self.tbbe_var, font=("Arial", 22))
        self.tbbe_check.grid(row=1, column=0, padx=10, pady=(0, 0), sticky="w")


        self.cci_var = BooleanVar()
        self.cci_check = ctk.CTkCheckBox(master=top_right_frame, text='Cold Code Isolation', variable=self.cci_var, font=("Arial", 22))
        self.cci_check.grid(row=2, column=0, padx=10, pady=(0, 0), sticky="w")


        self.dod_var = BooleanVar()
        self.dod_check = ctk.CTkCheckBox(master=top_right_frame, text='DOD', variable=self.dod_var, font=("Arial", 22))
        self.dod_check.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="w")

        button_1 = ctk.CTkButton(master=top_right_frame, command=self.model.compile_and_run_code, text="Analyze", font=("Arial", 20, "bold"))
        button_1.grid(row=4, column=0, pady=(30, 30), padx=30, ipady=10, sticky="w")


        status_frame = ctk.CTkFrame(master=analyze_tab)
        status_frame.pack( fill="both", expand=False, pady=(5, 30))

        status_label = ctk.CTkLabel(master=status_frame, text="Progress", font=("Arial", 20, 'bold'))
        status_label.pack(pady=(20, 10), padx=10, anchor='w')


        self.progress_bar = ctk.CTkProgressBar(master=status_frame)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=20, padx=20, fill="both", expand=False)

        bottom_frame = ctk.CTkFrame(master=analyze_tab)
        bottom_frame.pack(side="bottom", fill="both", expand=True)

        stdout_label = ctk.CTkLabel(master=bottom_frame, text="Output", font=("Arial", 20, 'bold'))
        stdout_label.pack(pady=(20, 10), padx=10, anchor='w')


        self.output_text = ctk.CTkTextbox(master=bottom_frame, width=400, height=140, font=("Arial", 20))
        self.output_text.pack(pady=15, padx=15, fill="both", expand=True)

    

        # Refactor Tab ===============================================================================
        refactor_tab = self.add("Refactor")
