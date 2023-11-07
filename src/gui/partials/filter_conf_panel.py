from tkinter import *
from tkinter.ttk import *


class FilterConfigPanel(Frame):

    def __init__(self, root: Tk):
        Frame.__init__(self, root)
        self.root = root

        self.filter_strength = IntVar(value=8)

        self.filter_strength_text = StringVar(value="Filter Strength: 8")
        filter_strength_title = Label(
            self.root, textvariable=self.filter_strength_text, font=("Helvetica", 10))
        filter_strength_title.pack()

        filter_strength_scale = Scale(
            self.root, from_=0, to=12, orient=HORIZONTAL, variable=self.filter_strength, length=500, command=self.update_filter_strength)

        # leave space between buttons
        filter_strength_scale.pack(pady=10)

        self.boost_threshold = IntVar(value=2)

        self.boost_threshold_text = StringVar(value="Boost Threshold: 2")

        boost_threshold_title = Label(
            self.root, textvariable=self.boost_threshold_text, font=("Helvetica", 10))

        boost_threshold_title.pack()

        boost_threshold_scale = Scale(
            self.root, from_=0, to=10, orient=HORIZONTAL, variable=self.boost_threshold, length=500, command=self.update_boost_threshold)

        # make a little space above this pack
        boost_threshold_scale.pack(pady=10)

        #set correlation threshold
        self.corr_threshold = DoubleVar(value=0.92)

        self.corr_threshold_text = StringVar(value="Correlation threshold: 0.92")
        corr_threshold_title = Label(
            self.root, textvariable=self.corr_threshold_text, font=("Helvetica", 10))
        corr_threshold_title.pack()

        corr_threshold_scale = Scale(
            self.root, from_=0, to=1, orient=HORIZONTAL, variable=self.corr_threshold, length=500, command=self.update_corr_threshold)
        corr_threshold_scale.pack()

    def update_filter_strength(self, value) -> None:

        # chop to 2 decimal places
        value = float(value)
        value = round(value, 2)

        self.filter_strength_text.set("Filter Strength: " + str(value))

    def update_boost_threshold(self, value) -> None:

        # chop to 2 decimal places
        value = float(value)
        value = round(value, 2)

        self.boost_threshold_text.set("Boost Threshold: " + str(value))

    def update_corr_threshold(self, value) -> None:
        # chop to 2 decimal places
        value = float(value)
        value = round(value, 2)
        self.corr_threshold_text.set("Correlation threshold: " + str(value))
