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

        upperFrame = ctk.CTkFrame(master=analyze_tab, border_color="grey55", border_width=2)
        upperFrame.pack(pady = (20, 20), fill="both", expand = True)
        
        top_left_frame = ctk.CTkFrame(master=upperFrame)
        top_left_frame.pack(pady = (3, 3), padx = (2, 0), side="left", fill="both", expand=False)

        dir_label = ctk.CTkLabel(master=top_left_frame, text="Directory", font=("Arial", 20, 'bold'))
        dir_label.pack(pady=(80, 10), padx=10)

        self.dir_entry = ctk.CTkEntry(master=top_left_frame, placeholder_text="Directory Path", font=("Arial", 20, "italic"))
        self.dir_entry.pack(pady=10, padx=10, ipady=10)

        main_file_label = ctk.CTkLabel(master=top_left_frame, text="Mock Program", font=("Arial", 20, 'bold'))
        main_file_label.pack(pady=10, padx=10)
        self.main_file_var = StringVar()
        self.main_file_combobox = ctk.CTkComboBox(master=top_left_frame, font=("Arial", 20))
        self.main_file_combobox.pack(pady=10, padx=10)
        self.main_file_combobox.set('')

        button_0 = ctk.CTkButton(master=top_left_frame, command=self.model.open_directory_dialog, text="Open Project", font=("Arial", 20), border_color="grey77", border_width=1)
        button_0.pack(pady=50, padx=10, ipady=10)
        
        top_middle_frame = ctk.CTkFrame(master=upperFrame)
        top_middle_frame.pack(pady = (3,3),side="left", fill="both", expand=True)

        additional_files_label = ctk.CTkLabel(master=top_middle_frame, text="Additional C++ Source Files", font=("Arial", 20, 'bold'))
        additional_files_label.pack(pady=(20,5), padx=10, fill = "both")

        self.additional_files_switches = []

        self.scrollable_frame = ctk.CTkScrollableFrame(master=top_middle_frame, fg_color="grey15")
        self.scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        top_right_frame = ctk.CTkFrame(master=upperFrame)
        top_right_frame.pack(pady = (3,3), padx = (0, 2), side="left", fill="both", expand=False)

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

        button_1 = ctk.CTkButton(master=top_right_frame, command=self.model.compile_and_run_code, text="Analyze", font=("Arial", 20, "bold"), border_color="grey77", border_width=1)
        button_1.grid(row=4, column=0, pady=(30, 30), padx=30, ipady=10, sticky="w")
        

        status_frame = ctk.CTkFrame(master=analyze_tab, border_color="grey55", border_width=2)
        status_frame.pack( fill="both", expand=False, pady=(5, 30))

        status_label = ctk.CTkLabel(master=status_frame, text="Progress", font=("Arial", 20, 'bold'))
        status_label.pack(pady=(20, 10), padx=10, anchor='w')


        self.progress_bar = ctk.CTkProgressBar(master=status_frame)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=20, padx=20, fill="both", expand=False)

        lowerFrame = ctk.CTkFrame(master=analyze_tab, border_color="grey55", border_width=2)
        lowerFrame.pack(side="bottom", fill="both", expand=True)

        output_label = ctk.CTkLabel(master=lowerFrame, text="Output", font=("Arial", 20, 'bold'))
        output_label.pack(pady=(20, 10), padx=10, anchor='w')


        self.output_text = ctk.CTkTextbox(master=lowerFrame, width=400, height=140, font=("Arial", 20))
        self.output_text.pack(pady=15, padx=15, fill="both", expand=True)

    

        # Refactor Tab ===============================================================================
        refactor_tab = self.add("Refactor")
                
        rtop_frame = ctk.CTkFrame(master=refactor_tab, border_color="grey55", border_width=2)
        rtop_frame.pack(pady=(20, 20), fill="both")

        rdir_label = ctk.CTkLabel(master=rtop_frame, text="Directory", font=("Arial", 18, 'bold'))
        self.rdir_entry = ctk.CTkEntry(master=rtop_frame, placeholder_text="Path to HTML_OUT", font=("Arial", 18, "italic"))
        rbutton_0 = ctk.CTkButton(master=rtop_frame, command=self.model.list_stuff_in_HTML_OUT, text="Open HTML_OUT", font=("Arial", 18), border_color="grey77", border_width=1)
    
        # Using grid for better positioning
        rdir_label.grid(row=0, column=0, sticky='w', padx=10, pady=(10, 5))
        self.rdir_entry.grid(row=1, column=0, sticky='ew', padx=10, pady=(0,0), ipady=10)
        rbutton_0.grid(row=2, column=0, sticky='we', padx=10, pady=(10,30), ipady=10)


        apiKeyFieldLabel = ctk.CTkLabel(master=rtop_frame, text="OpenAI API Key", font=("Arial", 18, 'bold'))
        self.apiKeyField = ctk.CTkEntry(master=rtop_frame, placeholder_text="Your API Key", font=("Arial", 18, "italic"))
        self.apiKeyField.grid(row = 1, column = 1, padx=10, pady=(0,0), ipady=10, sticky = "ew")
        apiKeyFieldLabel.grid(row = 0, column = 1, padx=10, pady=(5, 5), sticky = "w")

        # Create a new subframe
        checkbox_subframe = ctk.CTkFrame(master=rtop_frame)
        checkbox_subframe.grid(row=2, column=1, padx=10, pady=(5,40), sticky = "nswe")
        model_label = ctk.CTkLabel(master=checkbox_subframe, text="Choose Your Model", font=("Arial", 14, 'italic'))
        model_label.grid(row = 0, sticky  = "we", columnspan = 2, pady = (10, 10))

        # Add the checkboxes to select Model
        self.gpt3Var = BooleanVar()
        self.gpt3_checkbox = ctk.CTkCheckBox(master=checkbox_subframe, variable=self.gpt3Var, text="GPT-3.5-Turbo", font=("Arial", 14))
        self.gpt3_checkbox.grid(row=1, column=0, padx=10, pady=(5,5), sticky='ns')

        self.gpt4Var = BooleanVar()
        self.gpt4_checkbox = ctk.CTkCheckBox(master=checkbox_subframe,variable=self.gpt4Var, text="GPT-4", font=("Arial", 14))
        self.gpt4_checkbox.grid(row=1, column=1, padx=10, pady=(5,5), sticky='ns')

        # Create a new frame for scrollable_frame
        scrollFrameLabel = ctk.CTkLabel(master=rtop_frame, text="Files", font=("Arial", 18, 'bold'))
        scrollFrameLabel.grid(row = 0, column = 2, sticky = "ew")

        scroll_outer_frame = ctk.CTkFrame(master=rtop_frame)
        scroll_outer_frame.grid(row=1, column=2, rowspan=2, sticky="nsew", pady=(5, 30), padx = 5)

        self.rscrollable_frame = ctk.CTkScrollableFrame(master=scroll_outer_frame, fg_color="grey15")
        self.rscrollable_frame.pack(fill="both", expand=True)
      
        self.radditional_files_switches = []

        cloneButton = ctk.CTkButton(master=rtop_frame, command = self.model.createCppFileFromHTML, text="HTML to C++", font=("Arial", 18), border_color="grey77", border_width=1)
        cloneButton.grid(row = 1, column = 3, padx = (25, 5), sticky = "nswe", pady = (20, 3))
        
        readButton = ctk.CTkButton(master=rtop_frame, command=self.model.printFile, text="Print File", font=("Arial", 18), border_color="grey77", border_width=1)
        readButton.grid(row = 1, column = 4, padx = (5, 5), sticky = "nswe", pady = (20, 3))

        refactorButton = ctk.CTkButton(master=rtop_frame, command = self.model.refactorUsingCGPT, text="AI Refactoring", font=("Arial", 18, "bold"), border_color="grey77", border_width=1)
        refactorButton.grid(row = 2, column = 3, columnspan = 2, padx = (25, 5), pady = (30, 50), sticky = "nswe")


        rmiddle_frame = ctk.CTkFrame(master=refactor_tab, border_color="grey55", border_width=2)
        rmiddle_frame.pack(pady=(10, 10), fill="both", expand=False)

        self.promptField = ctk.CTkEntry(master=rmiddle_frame, placeholder_text="Select the .cpp files to refactor and type in your prompt here.", font=("Arial", 18, "italic"))
        self.promptField.grid(row=0, rowspan = 2, column=0, pady=(10, 10), padx=10, sticky="nswe")

        # Add an empty row to create space
        rmiddle_frame.grid_rowconfigure(1, minsize=20)

        tryAgainButton = ctk.CTkButton(master=rmiddle_frame, command = self.model.refactorAgain, text="Re-RF Using Custom Prompt", font=("Arial", 20, "bold"), border_color="grey77", border_width=1)
        tryAgainButton.grid(row=0, column=1, padx=(5, 15), pady=(30, 5), sticky="ns", ipady = 5)
        rmiddle_frame.grid_columnconfigure(0, weight=1)  # Make column 0 take more horizontal space
        rmiddle_frame.grid_columnconfigure(1, weight=0)  # Make column 0 take more horizontal space


        rbottom_frame = ctk.CTkFrame(master=refactor_tab, border_color="grey55", border_width=2)
        rbottom_frame.pack(pady=(20, 20), fill="both", expand=True)
        
        output_label = ctk.CTkLabel(master=rbottom_frame, text="Output", font=("Arial", 20, 'bold'))
        output_label.grid(row=0, column=0, pady=(20, 10), padx=15, sticky='w')
                
        clearButton = ctk.CTkButton(master=rbottom_frame, command = lambda: self.model.rOutMessage("") , text="Clear Output", border_color="grey77", border_width=1, font = ("Arial", 14))
        clearButton.grid(row=0, column=1, pady=(20, 10), padx=15, sticky="e")

        self.routput_text = ctk.CTkTextbox(master=rbottom_frame, width=400, height=140, font=("Arial", 20))
        self.routput_text.grid(row=1, column=0, columnspan=2, pady=15, padx=15, sticky="nsew")

        rbottom_frame.grid_columnconfigure(0, weight=1)  # Allows column 0 to expand
        rbottom_frame.grid_columnconfigure(1, weight=1)  # Allows column 1 to expand
        rbottom_frame.grid_rowconfigure(1, weight=1)  # Allows row 1 to expand



