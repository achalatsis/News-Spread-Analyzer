#!/usr/bin/env python

import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
import pylab

from ConfigBundle import *


class BarChart():

    def __init__(self, values, labels):

        #initiate chart
        self.fig, self.ax1 = pyplot.subplots(figsize=(13, 8))
        pyplot.subplots_adjust(left=0.2, right=0.9)

        #set title, subtitle, and legend
        self.ax1.set_title(applicationConfig.chartTitle)
        pyplot.text(50, 0.1, applicationConfig.chartSubtitle, horizontalalignment='center', size='medium')

        #label position: place them at the center of each bar
        pos = numpy.arange(len(values))+0.5
        bars = self.ax1.barh(pos, values, align='center', height=0.5, color='b')

        self.ax1.axis([0, max(values), 0, len(values)])
        pylab.yticks(pos, labels)


        #write each value inside the bar for easy recognition
        for bar in bars:
            value = int(bar.get_width())

            xloc = value - 0.2
            yloc = bar.get_y() + bar.get_height() / 2.0

            self.ax1.text(xloc, yloc, str(value), horizontalalignment='right', verticalalignment='center', color='white', weight='bold')


    def saveAsPNG(self, filename):
        pyplot.savefig(filename, dpi=200, format='png')


    def saveAsSVG(self, filename):
        pyplot.savefig(filename, dpi=200, format='svg')



if __name__ == "__main__":
    print("Nothing to run here! Execute the main application file instead!")
