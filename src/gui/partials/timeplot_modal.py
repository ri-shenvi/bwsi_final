from tkinter import *
from tkinter.ttk import *
from os import listdir
import processor.heatmap as hp
from gui.state import get_state
import lib.filter_utils as filters
import lib.file_utils as file_util
import lib.image_utils as image_util
import numpy as np
from gui.partials.filter_conf_panel import FilterConfigPanel

# A modal to edit the config


class TimePlotModal(object):

    def __init__(self, root: Tk, latest=False) -> None:

        if latest:
            file_name = self.getLatestFile()
            path = "./data/" + file_name
            print(path)
            data = file_util.read_data_file(path)
            data["data"] = np.log10(data["data"])
            hp.generate_heatmap(data, "m")
            return

        self.root = Toplevel(root)
        self.root.grab_set()

        self.root.title("Generate Range-Time Plot")

        fileselect_title = Label(
            self.root, text="Select File", font=("Helvetica", 16))
        fileselect_title.pack()

        self.files = Variable(value=[])
        self.update_files()
        self.file_box = Listbox(self.root, height=20, width=70,
                                listvariable=self.files)
        self.file_box.pack()

        generate_button = Button(
            self.root, text="Generate", command=self.generate)
        generate_button.pack()

        self.selected_filter = StringVar(value="B")
        generate_filter_selection = Radiobutton(self.root, text="SciPy Gausian", variable=self.selected_filter, value="A")
        generate_filter_selection.pack()
        generate_filter_selection2 = Radiobutton(self.root, text="Custom denoisers", variable=self.selected_filter, value="B")
        generate_filter_selection2.pack()

        self.filter_strength = IntVar(value=8)

        self.filter_config = FilterConfigPanel(self.root)

        generate_filter_button = Button(
            self.root, text="Generate Filtered", command=self.generate_filtered)
        generate_filter_button.pack(pady=10)

    def update_files(self) -> None:
        files = listdir("./data")

        # only files ending in .pkl
        files = [f for f in files if f.endswith(".pkl")]

        self.files.set(files)

    def getLatestFile(self) -> str:
        files = listdir("./data")

        # only files ending in .pkl
        files = [f for f in files if f.endswith(".pkl")]

        # sort by name
        files.sort()

        return files[-1]

    def generate(self):

        # get unit preference
        unit = get_state("config")["ui"]["units"]

        # get file name
        file_name = self.file_box.get(self.file_box.curselection())

        # construct path
        path = "./data/" + file_name

        data = file_util.read_data_file(path)

        data = filters.apply_log(data)

        corr_threshold = self.filter_config.corr_threshold.get()
        data = image_util.get_radar_start_time(data, correlation_threshold=corr_threshold, reduce_dimentions_by=3)

        # generate the plot
        hp.generate_heatmap(data, unit, show_start_time=True)


    def generate_filtered(self):

        # get unit preference
        unit = get_state("config")["ui"]["units"]

        # get file name
        file_name = self.file_box.get(self.file_box.curselection())

        # construct path
        path = "./data/" + file_name

        data = file_util.read_data_file(path)

        filtered_data = filters.apply_log(data)

        #controls what set of filters to apply, 1 - Joris's filters, 2 - Aiden's filters
        #filter_set=1

        if self.selected_filter.get() == "B":
            # good results with value_threshold=70, count_threshold=2
            filtered_data = filters.iterative_denoise(filtered_data, value_threshold=70, count_threshold=2)
            
            #filtered_data = filters.iterative_denoise(filtered_data, value_threshold=50, count_threshold=4)
            filtered_data = filters.iterative_5x5_denoise(filtered_data, value_threshold=60, count_threshold=5)

            filter_type = "gausian"
            #filter_threshold=45
            filtered_data = filters.apply_5x5_filter(radar_data=filtered_data, filter_name=filter_type, filter_threshold=47)
            
            #filter_threshold=35
            filtered_data = filters.apply_5x5_avg_filter(radar_data=filtered_data, filter_threshold=35)
            #filtered_data = filters.remove_streaks(filtered_data)

            # value_threshold=60, count_threshold=7
            filtered_data = filters.iterative_5x5_denoise(filtered_data, value_threshold=60, count_threshold=8)            

        else:
            strength = self.filter_config.filter_strength.get()
            boost_thresh = self.filter_config.boost_threshold.get()
            filtered_data = filters.apply_scipy_gausian_filter(radar_data=filtered_data, strength=strength, boost_thresh=boost_thresh)

        filtered_data = filters.remove_streaks(filtered_data)

        #add start time analysis details to the filtered_data dictionary
        corr_threshold = self.filter_config.corr_threshold.get()
        filtered_data = image_util.get_radar_start_time(filtered_data, correlation_threshold=corr_threshold , reduce_dimentions_by=3)

        # generate the plot
        hp.generate_heatmap(filtered_data, unit, show_start_time=True)
