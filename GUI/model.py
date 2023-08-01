import sys
sys.path.append("../SRC")
from tbbe import analyze_tbbe
from crtp import analyze_crtp
from coldCode import analyze_coldCode
from dod import analyze_dod
from Refactorer import Refactor
import os
import shutil

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




class Model():

    def __init__(self, application):
        self.app = application
        self.view = None
        self.refactorer = Refactor()

    def set_view(self, view):
        self.view = view

    def comment_checker(self, comments, new_comments):
        for line, comment in new_comments.items():
            if line in comments:
                comments[line] += '\n//' + comment
            else:
                comments[line] = comment
        return comments
    
    def delete_junk(self, target_dir):
        all_files_in_coverage_out = glob.glob(os.path.join(target_dir, "*"))
        for file in all_files_in_coverage_out:
            if not file.endswith('.cpp.gcov'):
                try:
                    os.remove(file)
                except Exception as e:
                    print(f"Error while deleting file : {file}")
                    print(e)


    def transform_path(self, path):
        directory, filename = os.path.split(path)
        base_filename = os.path.splitext(filename)[0]
        new_directory = os.path.join(directory, 'COVERAGE_OUT')
        new_filename = base_filename + '.cpp.gcov'
        return os.path.join(new_directory, new_filename)


    def open_directory_dialog(self):
        dirname = filedialog.askdirectory()
        if not dirname:
            return
        
        self.view.progress_bar.set(0)

        self.view.dir_entry.delete(0, END)
        self.view.dir_entry.insert(0, dirname)

        cpp_files = [f for f in os.listdir(dirname) if f.endswith('.cpp')]
        self.view.main_file_combobox.configure(values=cpp_files)

        # Delete existing checkboxes from frame
        for widget in self.view.scrollable_frame.winfo_children():
            widget.destroy()

        # Clear existing switches
        self.view.additional_files_switches.clear()

        # Insert new checkboxes
        for i, f in enumerate(cpp_files):
            checkbox = ctk.CTkCheckBox(master=self.view.scrollable_frame, text=f)
            checkbox.grid(row=i, column=0, padx=10, pady=(0, 20), sticky="w")

            # Add switch to the additional_files_switches list
            self.view.additional_files_switches.append(checkbox)

    def list_stuff_in_HTML_OUT(self):
        dirname = filedialog.askdirectory()
        if not dirname:
            return
        
        self.view.rdir_entry.delete(0, END)
        self.view.rdir_entry.insert(0, dirname)

        self.updateRefactorScrollWindow(dirname)


    def updateRefactorScrollWindow(self, dirname):
        files = [f for f in os.listdir(dirname) if f.endswith('.cpp') or f.endswith('.html')]
 
        # Delete existing checkboxes from frame
        for widget in self.view.rscrollable_frame.winfo_children():
            widget.destroy()

        # Clear existing switches
        self.view.radditional_files_switches.clear()

        # Insert new checkboxes
        for i, f in enumerate(files):
            checkbox = ctk.CTkCheckBox(master=self.view.rscrollable_frame, text=f)
            checkbox.grid(row=i, column=0, padx=10, pady=(0, 20), sticky="w")

            # Add switch to the additional_files_switches list
            self.view.radditional_files_switches.append(checkbox)



    def compile_and_run_code(self):

        if not self.view.dir_entry.get():
            self.view.output_text.delete("1.0", "end")  
            self.view.output_text.insert("end", "Please select a C++ project first.")
            return
        else:
            self.view.output_text.delete("1.0", "end") 
            self.view.output_text.insert("end", "Running ==========================")
            self.app.update_idletasks()  

        self.view.progress_bar.set(0)

        directory = self.view.dir_entry.get()
        main_file = os.path.join(directory, self.view.main_file_combobox.get())
        additional_files = [os.path.join(directory, switch.cget(
            'text')) for switch in self.view.additional_files_switches if switch.get()]

        # prepend directory path to the executable name
        executable_path = os.path.join(directory, "OUT")
        # use the path to the executable in the g++ command
        cmd = f"g++ -fprofile-arcs -ftest-coverage {main_file} {' '.join(additional_files)} -o {executable_path}"

        process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

    
        if stdout:
            self.view.output_text.insert("end", "\n" + stdout.decode())
            self.app.update_idletasks()
        if stderr:
            self.view.output_text.insert("end", "\n" + stderr.decode())
            self.app.update_idletasks()

        # use the path to the executable here as well
        process = subprocess.Popen(
            executable_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stdout:
            self.view.output_text.insert("end", "\n\nStandard Out: \n \t" + stdout.decode())
            self.app.update_idletasks()
        if stderr:
            self.view.output_text.insert("end", "\n" + stderr.decode())
            self.app.update_idletasks()

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
                self.view.output_text.insert("end", stderr.decode())

        # delete all unnecessary files in the COVERAGE_OUT directory
        self.delete_junk(coverage_out_dir)

        # Change the working directory back to the original one
        os.chdir(original_directory)

        html_out_dir = os.path.join(directory, 'HTML_OUT')
        os.makedirs(html_out_dir, exist_ok=True)


        files_to_analyze = [main_file] + additional_files

        total_files_to_process = len(files_to_analyze) * (self.view.crtp_var.get() or self.view.tbbe_var.get() or self.view.cci_check.get())
        if self.view.dod_var.get():
            total_files_to_process += len(additional_files)
        
        processed_files = 0


        if self.view.dod_var.get():
            html_file = os.path.join(html_out_dir, 'hot_attributes.html')
            with open(html_file, 'w') as f:
                f.write(html_code)

                for file in additional_files:
                    gcov_file = self.transform_path(file)
                    hot_attributes = analyze_dod(file, gcov_file, factor=2)

                    for class_name, attributes in hot_attributes.items():
                        for attr, count in attributes:
                            f.write(f"<tr><td>{file}</td><td>{class_name}</td><td>{attr}</td><td>{count}</td></tr>")
                    processed_files += 1
                    progress_percentage = (processed_files / total_files_to_process) 
                    self.view.progress_bar.set(progress_percentage)
                    self.app.update_idletasks()

                f.write("</table></body></html>")
            
        
        for file in files_to_analyze:

            with open(file, 'r') as f:
                source_code = f.read()

            comments = {}
            if self.view.crtp_var.get():
                new_comments = analyze_crtp(file)
                comments = self.comment_checker(comments, new_comments)

            if self.view.tbbe_var.get():
                new_comments = analyze_tbbe(file)
                comments = self.comment_checker(comments, new_comments)

            if self.view.cci_check.get():
                new_comments = analyze_coldCode(file, self.transform_path(file), 0.1)
                comments = self.comment_checker(comments, new_comments)

            source_lines = source_code.split('\n')
            for line, comment in sorted(comments.items(), reverse=True):
                source_lines.insert(line, f"// {comment}")
            new_source_code = '\n'.join(source_lines)

            html_file = os.path.join(
                html_out_dir, os.path.basename(file) + '.html')
            formatted_code = highlight(
                new_source_code, CppLexer(), HtmlFormatter(full=True))

            with open(html_file, 'w') as f:
                f.write(formatted_code)
            
            processed_files += 1
            progress_percentage = (processed_files / total_files_to_process) 
            self.view.progress_bar.set(progress_percentage)
            self.app.update_idletasks()
        

        self.view.output_text.insert("end", "\nAnalysis Done ======================")
        self.app.update_idletasks()  
    
    
    def printFile(self):
            directory = self.view.rdir_entry.get()
            files = [os.path.join(directory, switch.cget(
            'text')) for switch in self.view.radditional_files_switches if switch.get()]
            if len(files) != 1:
                self.view.routput_text.delete("1.0", "end") 
                self.view.routput_text.insert("end", "Please select one single file to print to the output console.")
                return 
            
            self.view.routput_text.delete("1.0", "end")
            with open(files[0], "r") as file:
                for line in file.readlines():
                    self.view.routput_text.insert("end", line)



    def createCppFileFromHTML(self):
        directory = self.view.rdir_entry.get()
        parentDirectory = directory.replace("/HTML_OUT", "")

        html_files = [os.path.join(directory, switch.cget(
                            'text')) for switch in self.view.radditional_files_switches if switch.get()]
        
        if len(html_files) == 0:
            self.view.routput_text.delete("1.0", "end") 
            self.view.routput_text.insert("end", "Please select at least one .html file to convert into a .cpp file.")
            return 

        self.view.routput_text.delete("1.0", "end")

        processed_files = []


        for htmlFileFullPath in html_files: 
            _, html_file = os.path.split(htmlFileFullPath)
            
            if not html_file.endswith(".html"):
                self.view.routput_text.insert("end", "ignoring " + html_file + " since it is not a .html file")
                continue
            
            #merge cpp file with header
            cppFileFullPath = htmlFileFullPath.replace(".html", "")

            # copy .h file from parentDirectory to HTML_OUT
            for file_fullPath in os.listdir(parentDirectory):
                _, file = os.path.split(file_fullPath)
                if file == html_file.replace(".cpp.html", ".h"):
                    shutil.copy(os.path.join(parentDirectory, file), directory)

            self.refactorer._convertHTMLtoCPP(htmlFileFullPath, cppFileFullPath)
            self.refactorer.generateCppFile(cppFileFullPath, cppFileFullPath.replace(".cpp", ".h"), cppFileFullPath)
            processed_files.append(html_file)
                
        self.updateRefactorScrollWindow(directory)
        self.view.routput_text.delete("1.0", "end")
        processed_filesStr = ', '.join(processed_files)  # Join the strings with a space between each one
        processed_filesStr = "[" + processed_filesStr + "]"
        self.view.routput_text.insert("end", "Successfully converted all of " + processed_filesStr + " to .cpp files.")


    def refactorUsingCGPT(self):
        pass