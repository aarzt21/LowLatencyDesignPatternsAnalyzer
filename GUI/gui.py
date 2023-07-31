
import sys
sys.path.append("../SRC")
from tbbe import analyze_tbbe
from crtp import analyze_crtp
from coldCode import analyze_coldCode
from dod import analyze_dod
import os

import customtkinter as ctk
import subprocess
from pygments import highlight
import time
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
from tkinter import filedialog, END, StringVar, BooleanVar
import glob
import shutil


html_code = """<html><head>
                <style>
                body {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f3f3f3;
                    font-family: Arial, sans-serif;
                }
                table {
                    border-collapse: collapse;
                    width: 80%;
                    max-width: 900px;
                }
                th, td {
                    border: 1px solid #dddddd;
                    text-align: left;
                    padding: 8px;
                }
                tr:nth-child(even) {
                    background-color: #dddddd;
                }
                </style>
                </head><body><table><tr><th>File</th><th>Class</th><th>Hot Attribute</th><th>Access Count</th></tr>"""




def comment_checker(comments, new_comments):
    for line, comment in new_comments.items():
        if line in comments:
            comments[line] += '\n//' + comment
        else:
            comments[line] = comment
    return comments


def delete_junk(target_dir):
    all_files_in_coverage_out = glob.glob(os.path.join(target_dir, "*"))
    for file in all_files_in_coverage_out:
        if not file.endswith('.cpp.gcov'):
            try:
                os.remove(file)
            except Exception as e:
                print(f"Error while deleting file : {file}")
                print(e)

def transform_path(path):
    directory, filename = os.path.split(path)
    base_filename = os.path.splitext(filename)[0]
    new_directory = os.path.join(directory, 'COVERAGE_OUT')
    new_filename = base_filename + '.cpp.gcov'
    return os.path.join(new_directory, new_filename)


def open_directory_dialog():
    dirname = filedialog.askdirectory()
    if not dirname:
        return
    
    progress_bar.set(0)

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

    if not dir_entry.get():
        output_text.delete("1.0", "end")  
        output_text.insert("end", "Please select a C++ project first.")
        return
    else:
        output_text.delete("1.0", "end") 
        output_text.insert("end", "Running ==========================")
        app.update_idletasks()  

    progress_bar.set(0)

    directory = dir_entry.get()
    main_file = os.path.join(directory, main_file_combobox.get())
    additional_files = [os.path.join(directory, switch.cget(
        'text')) for switch in additional_files_switches if switch.get()]

    # prepend directory path to the executable name
    executable_path = os.path.join(directory, "OUT")
    # use the path to the executable in the g++ command
    cmd = f"g++ -fprofile-arcs -ftest-coverage {main_file} {' '.join(additional_files)} -o {executable_path}"

    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

   
    if stdout:
        output_text.insert("end", "\n" + stdout.decode())
        app.update_idletasks()
    if stderr:
        output_text.insert("end", "\n" + stderr.decode())
        app.update_idletasks()

    # use the path to the executable here as well
    process = subprocess.Popen(
        executable_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if stdout:
        output_text.insert("end", "\n\nStandard Out: \n \t" + stdout.decode())
        app.update_idletasks()
    if stderr:
        output_text.insert("end", "\n" + stderr.decode())
        app.update_idletasks()

    # Generate gcov files and move them to COVERAGE_OUT directory
    coverage_out_dir = os.path.join(directory, 'COVERAGE_OUT')
    os.makedirs(coverage_out_dir, exist_ok=True)

    # Move .gcno and .gcda files to COVERAGE_OUT directory
    for ext in ["gcno", "gcda"]:
        files = glob.glob(os.path.join(directory, f"*.{ext}"))
        for file in files:
            shutil.move(file, coverage_out_dir)

    # Save the current working directory
    original_directory = os.getcwd()

    # Change the working directory to the coverage output directory
    os.chdir(coverage_out_dir)

    cpp_files = glob.glob(os.path.join(directory, "*.cpp"))
    for file in cpp_files:
        directory, filename = os.path.split(file)
        base_filename = os.path.splitext(filename)[0]
        base_file = os.path.join(directory, f"OUT-{base_filename}")
        cmd = f"gcov -o {coverage_out_dir} {base_file} > /dev/null 2>&1"
        process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if stderr:
            output_text.insert("end", stderr.decode())

    # delete all unnecessary files in the COVERAGE_OUT directory
    delete_junk(coverage_out_dir)

    # Change the working directory back to the original one
    os.chdir(original_directory)

    html_out_dir = os.path.join(directory, 'HTML_OUT')
    os.makedirs(html_out_dir, exist_ok=True)


    files_to_analyze = [main_file] + additional_files

    total_files_to_process = len(files_to_analyze) * (crtp_var.get() or tbbe_var.get() or cci_check.get())
    if dod_var.get():
        total_files_to_process += len(additional_files)
    
    processed_files = 0


    if dod_var.get():
        html_file = os.path.join(html_out_dir, 'hot_attributes.html')
        with open(html_file, 'w') as f:
            f.write(html_code)

            for file in additional_files:
                gcov_file = transform_path(file)
                hot_attributes = analyze_dod(file, gcov_file, factor=2)

                for class_name, attributes in hot_attributes.items():
                    for attr, count in attributes:
                        f.write(f"<tr><td>{file}</td><td>{class_name}</td><td>{attr}</td><td>{count}</td></tr>")
                processed_files += 1
                progress_percentage = (processed_files / total_files_to_process) 
                progress_bar.set(progress_percentage)
                app.update_idletasks()

            f.write("</table></body></html>")
        
    
    for file in files_to_analyze:

        with open(file, 'r') as f:
            source_code = f.read()

        comments = {}
        if crtp_var.get():
            new_comments = analyze_crtp(file)
            comments = comment_checker(comments, new_comments)

        if tbbe_var.get():
            new_comments = analyze_tbbe(file)
            comments = comment_checker(comments, new_comments)

        if cci_check.get():
            new_comments = analyze_coldCode(file, transform_path(file), 0.1)
            comments = comment_checker(comments, new_comments)

        source_lines = source_code.split('\n')
        for line, comment in sorted(comments.items(), reverse=True):
            source_lines.insert(line-1 , f"// {comment}")
        new_source_code = '\n'.join(source_lines)

        html_file = os.path.join(
            html_out_dir, os.path.basename(file) + '.html')
        formatted_code = highlight(
            new_source_code, CppLexer(), HtmlFormatter(full=True))

        with open(html_file, 'w') as f:
            f.write(formatted_code)
        
        processed_files += 1
        progress_percentage = (processed_files / total_files_to_process) 
        progress_bar.set(progress_percentage)
        app.update_idletasks()
    

    output_text.insert("end", "\nAnalysis Done ======================")
    app.update_idletasks()  
    
    


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1100x1000")
app.title("C++ Low Latency Design Patterns Analyzer")

main_frame = ctk.CTkFrame(master=app)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

top_frame = ctk.CTkFrame(master=main_frame)
top_frame.pack(side="top", fill="both")

top_left_frame = ctk.CTkFrame(master=top_frame)
top_left_frame.pack(side="left", fill="both", expand=False)

dir_label = ctk.CTkLabel(master=top_left_frame,
                         text="Directory", font=("Arial", 20, 'bold'))
dir_label.pack(pady=(80, 10), padx=10)

dir_entry = ctk.CTkEntry(master=top_left_frame,
                         placeholder_text="Directory Path", font=("Arial", 20))
dir_entry.pack(pady=10, padx=10, ipady=10)

main_file_label = ctk.CTkLabel(
    master=top_left_frame, text="Main File", font=("Arial", 20, 'bold'))
main_file_label.pack(pady=10, padx=10)

main_file_var = StringVar()
main_file_combobox = ctk.CTkComboBox(master=top_left_frame, font=("Arial", 20))
main_file_combobox.pack(pady=10, padx=10)
main_file_combobox.set('')

button_0 = ctk.CTkButton(master=top_left_frame, command=open_directory_dialog,
                         text="Open Project", font=("Arial", 20))
button_0.pack(pady=50, padx=10, ipady=10)

top_middle_frame = ctk.CTkFrame(master=top_frame)
top_middle_frame.pack(side="left", fill="both", expand=True)

additional_files_label = ctk.CTkLabel(
    master=top_middle_frame, text="Additional C++ Source Files", font=("Arial", 20, 'bold'))
additional_files_label.pack(pady=10, padx=10)

additional_files_switches = []

scrollable_frame = ctk.CTkScrollableFrame(master=top_middle_frame)
scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)

top_right_frame = ctk.CTkFrame(master=top_frame)
top_right_frame.pack(side="left", fill="both", expand=False)

top_right_frame.grid_rowconfigure(0, weight=1)
top_right_frame.grid_columnconfigure(0, weight=1)
top_right_frame.grid_columnconfigure(1, weight=1)



for i in range(5):
    top_right_frame.grid_rowconfigure(i, weight=1)

crtp_var = BooleanVar()
crtp_check = ctk.CTkCheckBox(
    master=top_right_frame, text='CRTP', variable=crtp_var, font=("Arial", 22))
crtp_check.grid(row=0, column=0, padx=10, pady=(40, 0), sticky="w")

tbbe_var = BooleanVar()
tbbe_check = ctk.CTkCheckBox(
    master=top_right_frame, text='TBBE', variable=tbbe_var, font=("Arial", 22))
tbbe_check.grid(row=1, column=0, padx=10, pady=(0, 0), sticky="w")


cci_var = BooleanVar()
cci_check = ctk.CTkCheckBox(
    master=top_right_frame, text='Cold Code Isolation', variable=cci_var, font=("Arial", 22))
cci_check.grid(row=2, column=0, padx=10, pady=(0, 0), sticky="w")


dod_var = BooleanVar()
dod_check = ctk.CTkCheckBox(
    master=top_right_frame, text='DOD', variable=dod_var, font=("Arial", 22))
dod_check.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="w")

button_1 = ctk.CTkButton(master=top_right_frame, command=compile_and_run_code,
                         text="Analyze", font=("Arial", 20, "bold"))
button_1.grid(row=4, column=0, pady=(30, 30), padx=30, ipady=10, sticky="w")



border_frame = ctk.CTkFrame(master=main_frame, fg_color="grey43", height=2, width = 1100)
border_frame.pack(pady=(1, 1))

status_frame = ctk.CTkFrame(master=main_frame)
status_frame.pack(side="top", fill="both", expand=False, pady=(30, 30))

status_label = ctk.CTkLabel(
    master=status_frame, text="Progress", font=("Arial", 20, 'bold'))
status_label.pack(pady=(20, 10), padx=10, anchor='w')


progress_bar = ctk.CTkProgressBar(master=status_frame)
progress_bar.set(0)
progress_bar.pack(pady=20, padx=20, fill="both", expand=False)

bottom_frame = ctk.CTkFrame(master=main_frame)
bottom_frame.pack(side="bottom", fill="both", expand=True)

stdout_label = ctk.CTkLabel(
    master=bottom_frame, text="Output", font=("Arial", 20, 'bold'))
stdout_label.pack(pady=(20, 10), padx=10, anchor='w')


output_text = ctk.CTkTextbox(
    master=bottom_frame, width=400, height=140, font=("Arial", 20))
output_text.pack(pady=15, padx=15, fill="both", expand=True)


app.mainloop()
