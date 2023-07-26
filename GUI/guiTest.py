import os

import customtkinter as ctk
import subprocess
from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
from tkinter import filedialog, END, StringVar, BooleanVar

import sys
sys.path.append("../SRC")
from crtp import analyze_crtp
from tbbe import analyze_tbbe


def open_directory_dialog():
    dirname = filedialog.askdirectory()
    dir_entry.delete(0, END)
    dir_entry.insert(0, dirname)

    cpp_files = [f for f in os.listdir(dirname) if f.endswith('.cpp')]
    main_file_combobox.configure(values=cpp_files)

    # Delete existing checkboxes from frame
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    
    # Clear existing switches
    additional_files_switches.clear()

    # Insert new checkboxes
    for i, f in enumerate(cpp_files):
        checkbox = ctk.CTkCheckBox(master=scrollable_frame, text=f)
        checkbox.grid(row=i, column=0, padx=10, pady=(0, 20), sticky="w")
        
        # Add switch to the additional_files_switches list
        additional_files_switches.append(checkbox)


def compile_and_run_code():
    directory = dir_entry.get()
    main_file = os.path.join(directory, main_file_combobox.get())
    additional_files = [os.path.join(directory, switch.cget('text')) for switch in additional_files_switches if switch.get()]

    executable_path = os.path.join(directory, "OUT")  # prepend directory path to the executable name
    cmd = f"g++ {main_file} {' '.join(additional_files)} -o {executable_path}"  # use the path to the executable in the g++ command

    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    output_text.delete("1.0", "end")
    if stdout:
        output_text.insert("end", stdout.decode())
    if stderr:
        output_text.insert("end", stderr.decode())

    process = subprocess.Popen(executable_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # use the path to the executable here as well
    stdout, stderr = process.communicate()
    if stdout:
        output_text.insert("end", stdout.decode())
    if stderr:
        output_text.insert("end", stderr.decode())

    html_out_dir = os.path.join(directory, 'HTML_OUT')
    os.makedirs(html_out_dir, exist_ok=True)
    
    if crtp_var.get():
        files_to_analyze = [main_file] + additional_files

        for file in files_to_analyze:
            with open(file, 'r') as f:
                source_code = f.read()
            comments = analyze_crtp(source_code, file)
            source_lines = source_code.split('\n')
            for line, comment in sorted(comments.items(), reverse=True):
                source_lines.insert(line - 1, f"// {comment}\n")
            new_source_code = '\n'.join(source_lines)
            
            html_file = os.path.join(html_out_dir, os.path.basename(file) + '.html')
            formatted_code = highlight(new_source_code, CppLexer(), HtmlFormatter(full=True))

            with open(html_file, 'w') as f:
                f.write(formatted_code)



ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1100x900")
app.title("C++ Low Latency Design Patterns Analyzer")

main_frame = ctk.CTkFrame(master=app)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

top_frame = ctk.CTkFrame(master=main_frame)
top_frame.pack(side="top", fill="both")

top_left_frame = ctk.CTkFrame(master=top_frame)
top_left_frame.pack(side="left", fill="both", expand=False)

dir_label = ctk.CTkLabel(master=top_left_frame, text="Directory", font=("Arial", 20, 'bold'))
dir_label.pack(pady=(80, 10), padx=10)

dir_entry = ctk.CTkEntry(master=top_left_frame, placeholder_text="Directory Path", font=("Arial", 20))
dir_entry.pack(pady=10, padx=10, ipady=10)

main_file_label = ctk.CTkLabel(master=top_left_frame, text="Main File", font=("Arial", 20, 'bold'))
main_file_label.pack(pady=10, padx=10)

main_file_var = StringVar()
main_file_combobox = ctk.CTkComboBox(master=top_left_frame, font=("Arial", 20))
main_file_combobox.pack(pady=10, padx=10)
main_file_combobox.set('')

button_0 = ctk.CTkButton(master=top_left_frame, command=open_directory_dialog, text="Open Project", font=("Arial", 20))
button_0.pack(pady=50, padx=10, ipady=10)

top_middle_frame = ctk.CTkFrame(master=top_frame)
top_middle_frame.pack(side="left", fill="both", expand=True)

additional_files_label = ctk.CTkLabel(master=top_middle_frame, text="Additional C++ Source Files:", font=("Arial", 20,'bold'))
additional_files_label.pack(pady=10, padx=10)

additional_files_switches = []

scrollable_frame = ctk.CTkScrollableFrame(master=top_middle_frame)
scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)

top_right_frame = ctk.CTkFrame(master=top_frame)
top_right_frame.pack(side="left", fill="both", expand=False)

top_right_frame.grid_rowconfigure(0, weight=1)
top_right_frame.grid_columnconfigure(0, weight=1)
top_right_frame.grid_columnconfigure(1, weight=1)

crtp_var = BooleanVar()
crtp_check = ctk.CTkCheckBox(master=top_right_frame, text='CRTP', variable=crtp_var)
crtp_check.grid(row=0, column=0, pady=(20,10), padx=(0, 10), sticky="e") 

tbbe_var = BooleanVar()
tbbe_check = ctk.CTkCheckBox(master=top_right_frame, text='TBBE', variable=tbbe_var)
tbbe_check.grid(row=0, column=1, pady=(20,10), padx=(10, 0), sticky="w") 

button_1 = ctk.CTkButton(master=top_right_frame, command=compile_and_run_code, text="Compile and Run", font=("Arial", 20))
button_1.grid(row=1, column=0, columnspan=2, pady=(10, 10), padx=10, ipady=10)


bottom_frame = ctk.CTkFrame(master=main_frame)
bottom_frame.pack(side="bottom", fill="both", expand=True)

stdout_label = ctk.CTkLabel(master=bottom_frame, text="Std Out:", font=("Arial", 20, 'bold'))
stdout_label.pack(pady=(10, 10), padx=10, anchor='w')

output_text = ctk.CTkTextbox(master=bottom_frame, width=400, height=140, font=("Arial", 20))
output_text.pack(pady=15, padx=15, fill="both", expand=True)



app.mainloop()