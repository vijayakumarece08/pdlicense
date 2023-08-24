import shutil
import tkinter as tk
import tkinter.ttk as ttk
import tempfile
import zipfile, re, os
from time import sleep
from tkinter import *
from tkinter import filedialog
from pathlib import Path
import tkinter.messagebox
from fpdf import FPDF
from create_table_fpdf2 import PDF
from survey_metadata import get_file, segregation
from measurement_metadata import get_file_measurement, segregation_measurement
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import ctypes  # An included library with Python install.
import subprocess

DEPTH = 2
EXCLUDES = {'__MACOSX', 'resources'}


class HomePage(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.notebook = ttk.Notebook()  # Create a notebook widget
        self.add_tab1()
        self.notebook.grid(row=0)
        self.notebook.pack(expand=1, fill="both")

    def add_tab1(self):
        tab1 = tab_one(self.notebook)
        self.notebook.add(tab1, text="Home")


class data_table(object):
    def __init__(self, site, panels_count, tev_count):
        self.site = site
        self.panels_count = panels_count
        self.tev_count = tev_count


class tab_one(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        # Creating frames on the window/canvas for the first tab
        frame_selectfile = tk.LabelFrame(self, text="Step 1: Zip File Extraction ", bd=6)  # Frame1 on the window/canvas
        frame_selectfile.grid(column=0, row=0, padx=10, pady=10, sticky='NSEW')  # Positioning frame1
        frame_selectfile.configure(borderwidth=1)
        self.grid_columnconfigure(1, weight=1)  # Configuring the column for the main window/canvas
        self.grid_rowconfigure(1, weight=1)  # Configuring the row for the main window/canvas

        frame_checkpd = tk.LabelFrame(self, text="Step 2: Check PD ", bd=6)  # Frame2 on the window/canvas
        frame_checkpd.grid(column=1, row=0, padx=10, pady=10, sticky='NSEW')  # Positioning frame2
        frame_checkpd.configure(borderwidth=1)
        self.grid_columnconfigure(1, weight=1)  # Configuring the column for the main window/canvas
        self.grid_rowconfigure(1, weight=1)  # Configuring the row for the main window/canvas

        # Frame to display data in treeview
        frame_tree = tk.LabelFrame(self, text="PD Results ", bd=6)  # Frame2 on the window/canvas
        frame_tree.grid(column=0, row=1, columnspan=2, rowspan=2, padx=10, pady=10, sticky='NSEW')  # Positioning frame2
        frame_tree.configure(borderwidth=1)
        self.grid_columnconfigure(1, weight=1)  # Configuring the column for the main window/canvas
        self.grid_rowconfigure(1, weight=1)  # Configuring the row for the main window/canvas

        # Initializing all variables in frame_selectfile
        file_ID = tk.StringVar()
        location_id = tk.StringVar()
        unzip_status = tk.StringVar()
        tmpdir = tempfile.TemporaryDirectory().name
        self.create_dir_ifnot_exist(tmpdir)
        f_tem_sdir = open(os.getcwd() + "\\temp_dir.txt", "w")
        f_tem_sdir.write(tmpdir)
        f_tem_sdir.close()
        zip_filename = tk.StringVar()
        site_id = tk.StringVar()
        site_id.set("0")
        data_table_list = []

        middleframe = tk.LabelFrame(frame_selectfile, bd=5)
        databaseView = ttk.Treeview(middleframe, selectmode="browse")
        label_filename = tk.Label(frame_selectfile, text=" ", width=10, relief='flat').grid(column=0, row=1, padx=5,
                                                                                            pady=5, sticky='NW')
        label_filelocation = tk.Label(frame_selectfile, text="File Location:", width=12, relief='flat').grid(column=0,
                                                                                                             row=2,
                                                                                                             padx=5,
                                                                                                             pady=5,
                                                                                                             sticky='NW')

        filename_Entry = tk.Label(frame_selectfile, width=52, textvariable=file_ID)
        filename_Entry.grid(column=1, row=1, padx=5, pady=5, sticky='NW')
        filename_Entry.configure(state='normal')

        filelocation_Entry = tk.Entry(frame_selectfile, width=63, textvariable=location_id)
        filelocation_Entry.grid(column=1, row=2, padx=5, pady=5, sticky='W')
        filelocation_Entry.configure(background='palegreen', foreground='black')

        unzip_status.set("")
        label_unzipstatus = tk.Label(frame_selectfile, width=20, relief='flat', textvariable=unzip_status)
        label_unzipstatus.grid(column=1, row=5, padx=5, pady=5, sticky='NSEW')

        selectzip_button = tk.Button(frame_selectfile, width=20, text="Select Zip File",
                                     command=lambda: self.upload_action(location_id, zip_filename, tmpdir))
        selectzip_button.grid(column=1, row=3, padx=5, pady=3, ipady=3, sticky='SW')

        unzip_button = tk.Button(frame_selectfile, width=20, text="Extract",
                                 command=lambda: self.extract_nested_zip(databaseView, data_table_list,
                                                                         location_id.get(), tmpdir, zip_filename,
                                                                         site_id, False, 0))
        unzip_button.grid(column=1, row=3, padx=5, pady=3, ipady=3, sticky='NE')

        # Creating LabelFrame in frame_unzip
        upperframe = tk.LabelFrame(frame_selectfile, bd=0)
        frame_selectfile.rowconfigure(0, weight=1)
        frame_selectfile.columnconfigure(2, weight=1)
        upperframe.grid(column=0, row=6, columnspan=2, sticky='W')

        # middleframe = tk.LabelFrame(frame_selectfile, bd=5)
        middleframe.configure(borderwidth=1)
        frame_selectfile.columnconfigure(2, weight=1)
        frame_selectfile.rowconfigure(1, weight=1)
        middleframe.grid(column=0, row=7, columnspan=2, sticky="NSEW")

        lowerframe = tk.LabelFrame(frame_selectfile, bd=0)
        lowerframe.grid(column=0, row=7)
        frame_selectfile.columnconfigure(2, weight=1)
        frame_selectfile.rowconfigure(2, weight=0)

        # Labels in frame_unzip
        label18 = tk.Label(upperframe, text="Number of sites:", relief='flat')
        label18.grid(column=0, row=0, padx=5, pady=5, sticky='W')

        site_Entry = tk.Entry(upperframe, width=61, textvariable=site_id)
        site_Entry.grid(column=1, row=0, padx=10, pady=5, sticky='E')
        site_Entry.configure(state='normal', background='palegreen', foreground='black')

        label_details = tk.Label(upperframe, text=" ", relief='flat')
        label_details.grid(column=0, row=2, padx=5, pady=0, sticky='W')

        databaseView.columnconfigure(2, weight=1)
        databaseView.grid(column=0, row=0, columnspan=2, sticky="NSEW")

        # Creating treeview in frame_unzip
        vsb = Scrollbar(middleframe, orient="vertical", command=databaseView.yview())
        hsb = Scrollbar(middleframe, orient="horizontal")

        middleframe.columnconfigure(0, weight=1)
        middleframe.rowconfigure(0, weight=1)
        databaseView["show"] = "headings"
        databaseView["columns"] = ("site", "panels", "tevs")
        vsb.configure(command=databaseView.yview)
        vsb.grid(column=1, row=0, sticky="NS")

        # Treeview column headings
        databaseView.heading("site", text="Site")
        databaseView.column("site", anchor='w', width=250)
        databaseView.heading("panels", text="Number of Panels")
        databaseView.column("panels", anchor='center', width=150)
        databaseView.heading("tevs", text="Number of TEVs")
        databaseView.column("tevs", anchor='center', width=200)

        findpd_btn = tk.Button(frame_checkpd, width=20, text="Find PDs",
                               command=lambda: self.run_pd_model_exe(tmpdir, zip_filename, parent_tree, tree))
        findpd_btn.grid(column=0, row=0, padx=5, pady=5, sticky='EW')
        export_pdf_btn = tk.Button(frame_checkpd, width=20, text="Export to PDF",
                                   command=lambda: self.export_to_pdf(tmpdir, location_id.get()))
        export_pdf_btn.grid(column=1, row=0, padx=5, pady=5, sticky='EW')
        find_files_btn = tk.Button(frame_checkpd, width=20, text="Clear All",
                                   command=lambda: self.clear_all_files(tmpdir, parent_tree, tree, databaseView,
                                                                        site_id))
        find_files_btn.grid(column=2, row=0, padx=5, pady=5, sticky='EW')

        my_img = Image.open("logo.png")
        my_img_resized = my_img.resize((179, 50), Image.ANTIALIAS)
        self.my_img_resized = ImageTk.PhotoImage(my_img_resized)

        label_logo1 = tk.Label(frame_checkpd, width=20, image=self.my_img_resized)
        label_logo1.grid(column=3, row=0, sticky='NSEW')

        scrollbary = Scrollbar(frame_tree, orient=VERTICAL)
        scrollbarx = Scrollbar(frame_tree, orient=HORIZONTAL)

        parentframe = tk.LabelFrame(frame_checkpd, bd=0)
        frame_checkpd.rowconfigure(1, weight=1)
        frame_checkpd.columnconfigure((0, 1, 2, 3), weight=1, uniform=1)
        parentframe.grid(column=0, row=1, columnspan=4, sticky='NSEW')

        # PARENT TREE
        parent_tree = ttk.Treeview(parentframe,
                                   columns=("1", "2",
                                            "3", "4",
                                            "5", "6",
                                            "7", "8"),
                                   selectmode="extended")
        parent_tree.grid(row=1, column=0, pady=2, sticky=N + S + E + W)

        parentframe.rowconfigure(1, weight=1)
        parentframe.columnconfigure(0, weight=1)

        vsbb = Scrollbar(parentframe, orient="vertical", command=parent_tree.yview())

        vsbb.configure(command=parent_tree.yview)
        vsbb.grid(column=2, row=1, sticky="NS")

        parent_tree.heading("#0", text="")
        parent_tree.heading("1", text="File ID")
        parent_tree.heading("2", text="Date")
        parent_tree.heading("3", text="No")
        parent_tree.heading("4", text="Engineer")
        parent_tree.heading("5", text="Station")
        parent_tree.heading("6", text="Voltage (kV)")
        parent_tree.heading("7", text="Max dB")
        parent_tree.heading("8", text="Max PD (%)")

        # parent_tree.heading("8", text = "Panel No")
        parent_tree.column('#0', stretch=YES, minwidth=0, width=3, anchor=CENTER)
        parent_tree.column('#1', stretch=YES, minwidth=0, width=115, anchor=CENTER)
        parent_tree.column('#2', stretch=YES, minwidth=0, width=115, anchor=CENTER)
        parent_tree.column('#3', stretch=YES, minwidth=0, width=110, anchor=CENTER)
        parent_tree.column('#4', stretch=YES, minwidth=0, width=115, anchor=CENTER)
        parent_tree.column('#5', stretch=YES, minwidth=0, width=115, anchor=CENTER)
        parent_tree.column('#6', stretch=YES, minwidth=0, width=110, anchor=CENTER)
        parent_tree.column('#7', stretch=YES, minwidth=0, width=110, anchor=CENTER)
        parent_tree.column('#8', stretch=YES, minwidth=0, width=110, anchor=CENTER)

        # CHILD TREE
        tree = ttk.Treeview(frame_tree,
                            columns=("1", "2", "3", "4"
                                     , "5", "6", "7", "8"
                                     , "9"),
                            selectmode="extended",
                            yscrollcommand=scrollbary.set,
                            xscrollcommand=scrollbarx.set)
        tree.grid(row=0, column=0, pady=2, sticky=N + S + E + W)

        frame_tree.rowconfigure(0, weight=1)
        frame_tree.columnconfigure(0, weight=1)

        #         scrollbary.config(command=tree.yview)
        #         scrollbary.grid(row=0, column=1, pady=2, sticky=N + S)
        #
        #         scrollbarx.config(command=tree.xview)
        #         scrollbarx.grid(row=2, column=0, sticky=W + E)

        tree_vsb = Scrollbar(frame_tree, orient="vertical", command=tree.yview())
        tree_hsb = Scrollbar(frame_tree, orient="horizontal")
        tree_vsb.configure(command=tree.yview)
        tree_vsb.grid(column=1, row=0, sticky="NS")

        tree.heading("#0", text="")
        tree.heading("1", text="Panel No")
        tree.heading("2", text="TEV Name")
        tree.heading("3", text="Component")
        tree.heading("4", text="Sublocation")
        tree.heading("5", text="Phase Ref Lock")
        tree.heading("6", text="dB")
        tree.heading("7", text="PRPD")
        tree.heading("8", text="Pulse Wave")
        tree.heading("9", text="PD %")

        tree.column('#0', stretch=NO, minwidth=0, width=0, anchor=CENTER)
        tree.column('#1', stretch=YES, minwidth=0, width=150, anchor=CENTER)
        tree.column('#2', stretch=YES, minwidth=0, width=150, anchor=CENTER)
        tree.column('#3', stretch=YES, minwidth=0, width=150, anchor=CENTER)
        tree.column('#4', stretch=YES, minwidth=0, width=150, anchor=CENTER)
        tree.column('#5', stretch=YES, minwidth=0, width=150, anchor=CENTER)
        tree.column('#6', stretch=YES, minwidth=0, width=150, anchor=CENTER)
        tree.column('#7', stretch=YES, minwidth=0, width=150, anchor=CENTER)
        tree.column('#8', stretch=YES, minwidth=0, width=150, anchor=CENTER)
        tree.column('#9', stretch=YES, minwidth=0, width=150, anchor=CENTER)

    def clear_all_files(self, dir_path, p_tree, db_tree, databaseView_tree, site_id):
        site_id.set(0)
        # Clear the current data in the table
        for x in p_tree.get_children():
            p_tree.delete(x)
        for x in db_tree.get_children():
            db_tree.delete(x)
        for x in databaseView_tree.get_children():
            databaseView_tree.delete(x)

        shutil.rmtree(dir_path)

    def export_to_pdf(self, target_folder, parent_dirname):
        output_file_name = target_folder + "\\exe_out.txt"
        # html_template = os.getcwd() + "\\html_template.html"
        temp_array = parent_dirname.split("/")
        temp_array.pop()
        _pdf_path = "/".join(temp_array)
        output_pdf_path = _pdf_path + "\\pdf_output"

        # file1 = open(output_file_name, "r+")
        # print("Output of Readlines function is ")
        # # print(file1.readlines())
        # str = " ".join(file1.readlines())
        # print(str)
        # file1.close()
        #
        # pdf = FPDF('p', 'mm', 'A4')
        # pdf.add_page()
        # pdf.set_font('Arial', 'B', 9)
        # with open(output_file_name, 'r') as f:
        #     for line in f:
        #         pdf.cell(0, 10, line)
        #         pdf.ln(h='')
        #
        # pdf.output('pdf1.pdf')
        # f.close()

        # pisa.showLogging()
        # template = open(html_template)
        # pdf = pisa.CreatePDF(template.read(), open(output_pdf_file_name, "wb"))
        print(parent_dirname)
        print(output_pdf_path)
        self.create_dir_ifnot_exist(output_pdf_path)

        path = target_folder  # folder path
        files_list = os.listdir(path)  # list of files

        for file_name in files_list:
            fpdf = PDF('p', 'mm', 'A4')
            fpdf.add_page()
            fpdf.set_font('Times', size=10)
            if 'exe_out.txt' in file_name:
                print("skipping Exe_out")
            elif '.txt' in file_name:

                with open(f'{path}\\{file_name}', 'r') as data_file:
                    survey = ['Scanned Date', 'Job Number', 'Engineer Name',
                              'Station Name', 'Operator.Voltage ', 'Max dB', 'Max PD']

                    measurement = [['Panel Num', 'TEV Name', 'Component', 'Sublocation',
                                    'PhaseRef', 'dB', 'PRPD', 'Pulse Wave', 'PD%']]
                    for line in data_file:
                        data_strip = line.strip().split(',')
                        data = [s.strip() for s in data_strip]
                        if len(survey) == len(data):

                            fpdf.cell(w=((fpdf.get_string_width(survey[0])) + 2.5), h=5, txt=f'{survey[0]}',
                                      align="R")  # scanned data
                            fpdf.cell(w=((fpdf.get_string_width(data[0])) + 5.5), h=5, txt=f'{data[0]}', align="C",
                                      border=1)  # scanned data value
                            fpdf.cell(w=((fpdf.get_string_width(survey[1])) + 15.5), h=5, txt=f'{survey[1]}',
                                      align="R")  # job number
                            fpdf.cell(w=((fpdf.get_string_width(data[1])) + 5.5), h=5, txt=f'{data[1]}', align="C",
                                      border=1)  # job number value
                            fpdf.cell(w=((fpdf.get_string_width(survey[2])) + 15.5), h=5, txt=f'{survey[2]}',
                                      align="R")  # engineer name
                            fpdf.cell(w=((fpdf.get_string_width(data[2])) + 5.5), h=5, txt=f'{data[2]}', align="C",
                                      border=1, new_x="LMARGIN", new_y="NEXT")  # engineer name value
                            # empty space
                            fpdf.cell(new_x="LMARGIN", new_y="NEXT", h=5.0, align='L', w=0, border=0)
                            # second line
                            fpdf.cell(w=((fpdf.get_string_width(survey[3])) + 2.5), h=5, txt=f'{survey[3]}',
                                      align="R")  # station name data
                            fpdf.cell(w=((fpdf.get_string_width(data[3])) + 5.5), h=5, txt=f'{data[3]}', align="C",
                                      border=1)  # station name value
                            fpdf.cell(w=((fpdf.get_string_width(survey[4])) + 15.5), h=5, txt=f'{survey[4]}',
                                      align="R")  # operator voltage number
                            fpdf.cell(w=((fpdf.get_string_width(data[4])) + 5.5), h=5, txt=f'{data[4]}', align="C",
                                      border=1)  # operator voltage value
                            fpdf.cell(w=((fpdf.get_string_width(survey[5])) + 15.5), h=5, txt=f'{survey[5]}',
                                      align="R")  # max db
                            fpdf.cell(w=((fpdf.get_string_width(data[5])) + 5.5), h=5, txt=f'{data[5]}', align="C",
                                      border=1)  # max db value
                            fpdf.cell(w=((fpdf.get_string_width(survey[6])) + 15.5), h=5, txt=f'{survey[6]}',
                                      align="R")  # max pd
                            fpdf.cell(w=((fpdf.get_string_width(data[6])) + 5.5), h=5, txt=f'{data[6]}', align="C",
                                      border=1, new_x="LMARGIN", new_y="NEXT")  # max pd
                            # empty space
                            fpdf.cell(new_x="LMARGIN", new_y="NEXT", h=5.0, align='L', w=0, border=0)
                            fpdf.cell(new_x="LMARGIN", new_y="NEXT", h=5.0, align='L', w=0, border=0)
                            # third line
                            fpdf.cell(w=((fpdf.get_string_width(data[6])) + 1.5), h=5,
                                      txt=f'Note - Operator is Urged to check if PD%> {data[6]}%', new_x="LMARGIN",
                                      new_y="NEXT")
                        elif len(survey) != len(data):
                            measurement.append(data)

                    fpdf.set_xy(10, 60)
                    fpdf.create_table(table_data=measurement, data_size=5, title_size=6,
                                      cell_width=[40, 40, 15, 15, 15, 15, 15, 15, 15])
                    file_name = file_name[:-4]
                    fpdf.output(f'{output_pdf_path}\{file_name}.pdf')

    def run_pd_model_exe(self, target_folder, parent_dirname, p_tree, db_tree):

        current_dir = self.Remove_Spaces(os.getcwd())
        targ_folder = self.Remove_Spaces(target_folder)
        # current_dir = os.getcwd()
        # targ_folder = target_folder
        exe_file_name = current_dir + "\\20201006_create_exe.exe"
        model_file_name = os.getcwd() + "\\20201006_model.joblib"
        output_file_name = target_folder + "\\exe_out.txt"
        input_data_path = target_folder + "\\" + parent_dirname.get()

        cmd = exe_file_name + " \"" + input_data_path + "\\\\\" \"" + model_file_name + "\" > \"" + output_file_name + "\""
        print(input_data_path)
        print(exe_file_name)
        print(cmd)
        os.system(cmd)
        # sleep(60)
        # subprocess.call(cmd)
        # global pd_percent
        # pd_percent="0"
        f = open(target_folder + "//exe_out.txt", "r")
        exe_out_lines = f.readlines()
        maxsurvey_db = {}
        maxpd_percent = {}
        for list in exe_out_lines:
            if list.find(":\\") == -1:
                par_folder = (list.split(","))[0]
                sub_folder = (list.split(","))[1]
                sub_sub_folder = (list.split(","))[2]
                prpd = (list.split(","))[3].strip()
                pulse_wave = (list.split(","))[4].strip()
                measure_data_file_path = input_data_path + "\\" + par_folder.strip() + "\\" + sub_folder.strip() + "\\" + sub_sub_folder.strip() + "\\measurement_metadata.js"
                print(measure_data_file_path)
                measure_metadata = get_file_measurement(measure_data_file_path)
                survey_data = segregation_measurement(measure_metadata)
                fileObj = open(target_folder + "//" + par_folder + ".txt", "a")
                if par_folder in maxsurvey_db:
                    if survey_data["db"] != '':
                        maxsurvey_db[par_folder].append(survey_data["db"])
                else:
                    if survey_data["db"] != '':
                        maxsurvey_db[par_folder] = [survey_data["db"]]

                if (prpd == "Yes" and pulse_wave == "Yes"):
                    pd_percent = "100"
                    if par_folder in maxpd_percent:
                        maxpd_percent[par_folder].append(int(pd_percent))
                    else:
                        maxpd_percent[par_folder] = [int(pd_percent)]
                    pd_values = (list.split(","))[3].strip() + "," + (list.split(","))[4].strip() + "," + pd_percent
                    fileObj.write(
                        "\n" + sub_folder + "," + sub_sub_folder + "," + survey_data["component"] + "," + survey_data[
                            "sublocation"] + "," + survey_data[
                            "phasereflock"] + "," + str(survey_data["db"]) + "," + pd_values)
                elif (prpd == "Yes" and pulse_wave == "No"):
                    pd_percent = "20"
                    if par_folder in maxpd_percent:
                        maxpd_percent[par_folder].append(int(pd_percent))
                    else:
                        maxpd_percent[par_folder] = [int(pd_percent)]
                    pd_values = (list.split(","))[3].strip() + "," + (list.split(","))[4].strip() + "," + pd_percent
                    fileObj.write(
                        "\n" + sub_folder + "," + sub_sub_folder + "," + survey_data["component"] + "," + survey_data[
                            "sublocation"] + "," + survey_data[
                            "phasereflock"] + "," + str(survey_data["db"]) + "," + pd_values)
                elif (prpd == "No" and pulse_wave == "Yes"):
                    pd_percent = "50"
                    if par_folder in maxpd_percent:
                        maxpd_percent[par_folder].append(int(pd_percent))
                    else:
                        maxpd_percent[par_folder] = [int(pd_percent)]
                    pd_values = (list.split(","))[3].strip() + "," + (list.split(","))[4].strip() + "," + pd_percent
                    fileObj.write(
                        "\n" + sub_folder + "," + sub_sub_folder + "," + survey_data["component"] + "," + survey_data[
                            "sublocation"] + "," + survey_data[
                            "phasereflock"] + "," + str(survey_data["db"]) + "," + pd_values)
                elif (prpd.strip() == "No" and pulse_wave == "No"):
                    pd_percent = "0"
                    if par_folder in maxpd_percent:
                        maxpd_percent[par_folder].append(int(pd_percent))
                    else:
                        maxpd_percent[par_folder] = [int(pd_percent)]
                    pd_values = (list.split(","))[3].strip() + "," + (list.split(","))[4].strip() + "," + pd_percent
                    fileObj.write(
                        "\n" + sub_folder + "," + sub_sub_folder + "," + survey_data["component"] + "," + survey_data[
                            "sublocation"] + "," + survey_data[
                            "phasereflock"] + "," + str(survey_data["db"]) + "," + pd_values)

                fileObj.close()

        print(maxsurvey_db)
        print(maxpd_percent)
        f.close()

        path = target_folder  # folder path
        files_list = os.listdir(path)  # list of files
        i = 1
        for file_name in files_list:
            if 'exe_out.txt' in file_name:
                print("skipping Exe_out")
            elif '.txt' in file_name:
                with open(f'{path}\\{file_name}', 'r') as file:
                    maxdb = max(maxsurvey_db[file_name.split(".")[0]])
                    maxpd = max(maxpd_percent[file_name.split(".")[0]])
                    contents = file.read()
                    lines = contents.splitlines()

                    items = lines[0].split(",")
                    items[5] = str(maxdb)
                    items[6] = str(maxpd)
                    new_items = ','.join(items)
                    lines[0] = new_items

                    new_contents = '\n'.join(lines)

                with open(f'{path}\\{file_name}', "w") as file:
                    file.write(new_contents)

                with open(f'{path}\\{file_name}', 'r+') as data_file:

                    maxdb = max(maxsurvey_db[file_name.split(".")[0]])
                    maxpd = max(maxpd_percent[file_name.split(".")[0]])

                    measurement = [['Panel Num', 'TEV Name', 'Component', 'Sublocation',
                                    'PhaseRef', 'dB', 'PRPD', 'Pulse Wave', 'PD%']]
                    for line in data_file:
                        data = line.split(',')

                        # Insert parent notepad details into step 2 treeview
                        p_tree.insert("", 'end', iid=i, open=True,
                                      values=(file_name, data[0], data[1], data[2], data[3], data[4], maxdb, maxpd))
                        # p_tree.insert("", 'end', iid='2', open=True,
                        # values=("2", "fest2", "fest3]", "fest4]", "fest", "fest", "fest7"))
                        break
            i = i + 1

        p_tree.bind('<ButtonRelease-1>',
                    lambda event: self.select_tree_view(event, p_tree, db_tree, target_folder))

    def Remove_Spaces(self, dir_path):
        init_list = []
        for str in dir_path.split("\\"):
            count = 0
            # loop for search each index
            for i in range(0, len(str)):
                # Check each char
                # is blank or not
                if str[i] == " ":
                    count += 1
            if count > 0:
                init_list.append("\"" + str + "\"")
            else:
                init_list.append(str)

        return ("\\".join(init_list))

    def select_tree_view(self, event, parent_tree, child_tree, target_folder):
        # Clear treeview
        for x in child_tree.get_children():
            child_tree.delete(x)
        # Insert child data into 2nd Treeview
        selected_iid = parent_tree.focus()
        print(selected_iid)
        selected_values = parent_tree.item(selected_iid)
        selected_text = selected_values.get("values")[0]
        print(selected_text)
        f_new = open(target_folder + "//" + selected_text, "r")
        file_out_lines = f_new.readlines()
        maxsurvey_db = []
        maxpd_percent = []
        i = 1
        for list in file_out_lines:
            if i > 1:
                child_tree.insert("", 'end', iid=i, open=True,
                                  values=((list.split(","))[0], (list.split(","))[1], (list.split(","))[2],
                                          (list.split(","))[3], (list.split(","))[4], (list.split(","))[5],
                                          (list.split(","))[6], (list.split(","))[7], (list.split(","))[8]))
            i = i + 1

        f_new.close()

    def copyClipboard(event=None, copytext=None):
        toeclip = Tk()
        toeclip.clipboard_clear()
        toeclip.clipboard_append(copytext)
        toeclip.destroy()

    def upload_action(self, file_location=None, zip_file_name=None, tmp_location=None):
        filename = filedialog.askopenfilename()
        print('Selected:', filename)
        file_location.set(filename)
        zip_filename = Path(filename).with_suffix('').name
        zip_file_name.set(zip_filename)
        Path(tmp_location + "\\" + zip_filename).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def unzip_action(filelocation=None, unzip_status=None):
        tmpdir = tempfile.TemporaryDirectory().name
        Path(tmpdir).mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(filelocation, "r") as zf:
            zf.extractall(tmpdir)
        zf.close()
        unzip_status.set('Successfully extracted files at location: ' + tmpdir)

    def extract_nested_zip(self, databaseView, data_table_list, source_zip_file=None, target_folder=None,
                           parent_dirname=None, site_count=None, remove_zip=False, initialize_extract=0):
        #      if not remove_zip:
        #          target_folder += "\\" + parent_dirname.get()

        if initialize_extract == 0:
            site_count.set(0)
            for x in databaseView.get_children():
                databaseView.delete(x)
            extract_count = 1

        site_count_local = int(site_count.get())
        abs_parent_dirname = target_folder + "\\" + parent_dirname.get()
        with zipfile.ZipFile(source_zip_file, 'r') as zfile:
            zfile.extractall(path=abs_parent_dirname)

        if remove_zip:
            os.remove(source_zip_file)
        for root, dirs, files in os.walk(target_folder):
            if root == abs_parent_dirname:
                for filename in files:
                    if re.search(r'\.zip$', filename):
                        file_name_wo_ext = root + "\\" + Path(filename).with_suffix('').name
                        self.create_dir_ifnot_exist(file_name_wo_ext)
                        file_spec = os.path.join(root, filename)
                        site_count_local += 1
                        site_count.set(site_count_local)
                        self.extract_nested_zip(databaseView, data_table_list, file_spec, file_name_wo_ext,
                                                tk.StringVar(), site_count, True, 1)
                        self.update_data_table(databaseView, data_table_list, file_name_wo_ext, target_folder)

    @staticmethod
    def update_data_table(databaseView, data_table_list, panel_dir_name, target_folder):
        sub_dir_count = 0
        panels_count = len(set(os.walk(panel_dir_name).__next__()[1]).difference(EXCLUDES))
        for root, dirs, files in os.walk(panel_dir_name):
            dirs[:] = [d for d in dirs if d not in EXCLUDES]
            if root[len(panel_dir_name):].count(os.sep) < DEPTH:
                for dirname in dirs:
                    if panel_dir_name != root:
                        sub_dir_count += 1
                    print(" > " + dirname)
                print("dir count: " + str(len(dirs)) + ", sub_dir_count: " + str(sub_dir_count))
        databaseView.insert("", "end", values=(Path(panel_dir_name).name, panels_count, sub_dir_count))
        data_table_list.append(data_table(Path(panel_dir_name).name, panels_count, sub_dir_count))
        f = open(target_folder + "\\" + Path(panel_dir_name).name + ".txt", "w")
        survey_data_file_path = panel_dir_name + "\\survey_metadata.js"
        survey_metadata = get_file(survey_data_file_path)
        survey_data = segregation(survey_metadata)
        f.write(
            survey_data["Scanned Date"] + "," + survey_data["Job Number"] + "," + survey_data["Engineer Name"] + "," +
            survey_data["Station Name"] + "," + survey_data["Operating Voltage (kV)"] + ",,")
        f.close()

    @staticmethod
    def create_dir_ifnot_exist(file_path):
        Path(file_path).mkdir(parents=True, exist_ok=True)
        print('directory successfully created: ', file_path)

    # def messagebox(self, title, text):
    # easygui.msgbox(text, title=title)


if __name__ == '__main__':
    present = datetime.now()
    l_date = datetime(2023, 4, 7)
    # if (l_date > present):
    # ctypes.windll.user32.MessageBoxW(0, str((l_date - present).days) + " Days to Expire", "License Window", 1)
    homePage = HomePage()
    homePage.title("Partial Discharge Waveform Identifier System")  # Window title
    screen_width = homePage.winfo_screenwidth()
    screen_height = homePage.winfo_screenheight()
    width = 1600
    height = 850
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    homePage.geometry("%dx%d+%d+%d" % (width, height, x, y))
    homePage.resizable(1, 1)
    homePage.mainloop()
    print('The window is closed. Temp Path cleared')
    f_temdir = open(os.getcwd() + "\\temp_dir.txt", "r")
    temp_path = f_temdir.readline()
    f_temdir.close()
    print(temp_path)
    try:
        shutil.rmtree(temp_path)
    except:
        print("trying to remove directory after clear All")
    # else:
    # ctypes.windll.user32.MessageBoxW(0, "License Expired", "Please renew", 1)

"""
    todo:
    1) find PD, then generate pdf
    2) create exe file using pyInstaller
    3) Inno Setup

    need to implement clear button -
     - clear all UI values and tree values
     - delete all txt files and folders from temp path
     - Max PD and MAX pd_percent
"""
