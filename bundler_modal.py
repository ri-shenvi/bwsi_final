from tkinter import *
from tkinter.ttk import *
from os import listdir
from lib.bundle import bundle_data
import lib.file_utils as file_util
import lib.filter_utils as filters
import processor.heatmap as hp
from gui.partials.filter_conf_panel import FilterConfigPanel

# A modal to edit the config


class BundlerModal(object):

    def __init__(self, root: Tk) -> None:

        self.root = Toplevel(root)
        self.root.grab_set()

        self.root.title("Create Bundle")

        fileselect_title = Label(
            self.root, text="Select Files to Bundle", font=("Helvetica", 16))
        fileselect_title.pack()

        self.files = Variable(value=[])
        self.csv_files = Variable(value=[])
        self.update_files()
        self.file_box = Listbox(self.root, height=40, width=70,
                                listvariable=self.files, selectmode=MULTIPLE)
        self.file_box.pack()

        self.filter_config = FilterConfigPanel(self.root)

        preview_button = Button(
            self.root, text="Preview", command=self.preview)
        preview_button.pack()

        generate_button = Button(
            self.root, text="Create Bundle", command=self.generate)
        generate_button.pack()

    def preview(self) -> None:

        # get file names
        file_indicies = self.file_box.curselection()
        files = self.file_box.get(0, END)

        # if we selected no files, do nothing
        if len(file_indicies) == 0:
            return

        # if we selected more than 2 files, do nothing
        if len(file_indicies) > 2:
            return

        # get a pkl
        path = ""

        for i in file_indicies:
            if files[i].endswith(".pkl"):
                path = "data/" + files[i]

        data = file_util.read_data_file(path)

        # get filter strength
        strength = self.filter_config.filter_strength.get()
        boost_thresh = self.filter_config.boost_threshold.get()
        
        filtered_data = filters.apply_scipy_gausian_filter(
            data, strength=strength, boost_thresh=boost_thresh)

        # generate the plot
        hp.generate_heatmap(filtered_data)

    def update_files(self) -> None:
        files = listdir("./data")

        # only files ending in .pkl
        pkl_files = [f for f in files if f.endswith(".pkl")]

        # only files ending in .csv
        csv_files = [f for f in files if f.endswith(".csv")]

        self.files.set(pkl_files + csv_files)

    def generate(self):

        # get file names
        file_indicies = self.file_box.curselection()
        files = self.file_box.get(0, END)

        # if we selected no files, do nothing
        if len(file_indicies) == 0:
            return

        # if we selected more than 2 files, do nothing
        if len(file_indicies) > 2:
            return

        # figure out which selected files are csvs and which are pkls
        csv = ""
        pkl = ""

        for i in file_indicies:
            name = files[i]
            if name.endswith(".csv"):
                csv = name
            elif name.endswith(".pkl"):
                pkl = name

        # get the first csv
        csv_file_name = "data/" + csv

        # get the first pkl
        file_name = "data/" + pkl

        # bundle it

        strength = self.filter_config.filter_strength.get()
        boost_thresh = self.filter_config.boost_threshold.get()
        bundle_name = bundle_data(
            file_name, csv_file_name, filter_strength=strength, filter_boost_thresh=boost_thresh)

        print("Bundled data saved to " + bundle_name)

        # close the window
        self.root.destroy()
