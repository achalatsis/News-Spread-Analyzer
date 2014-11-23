#!/usr/bin/env python

import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
import pylab

from ConfigBundle import *


##  @package Visualization
#   Provides an interface for exporting data in charts


##  Class for creating a bar chart
class BarChart():

    ##  Creates a new chart with the supplied data. Bars are created in a descending order on the data provided.
    #   @param      chartTitle      Title to use when exported. This field must contain only ASCII characters.
    #   @param      values          The value to use for each bar
    #   @param      labels          Label to use for each bar
    def __init__(self, chartTitle, values, labels):

        #create a new chart plot, and size the canvas appropriately
        self.fig, self.ax1 = pyplot.subplots(figsize=(13, 8))
        pyplot.subplots_adjust(left=0.2, right=0.9)

        #set title, subtitle, and legend
        self.ax1.set_title(chartTitle)
        pyplot.text(50, 0.1, applicationConfig.chartSubtitle, horizontalalignment='center', size='medium')

        #label positioning: place them at the center of each bar
        pos = numpy.arange(len(values))+0.5
        bars = self.ax1.barh(pos, values, align='center', height=0.5, color='b')

        #minimum value for the axis is 0, maximum is the largest value of the ones supplied
        self.ax1.axis([0, max(values), 0, len(values)])
        pylab.yticks(pos, labels)

        #write each value inside the bar for easy recognition
        for bar in bars:
            #width of the bar is created based on it's value,
            #so it's easy to get the value back
            value = int(bar.get_width())

            #position the label insinde the bar
            xloc = value - 0.2
            yloc = bar.get_y() + bar.get_height() / 2.0

            #write the bar
            self.ax1.text(xloc, yloc, str(value), horizontalalignment='right', verticalalignment='center', color='white', weight='bold')


    ##  Export the chart in PNG format
    #   @param      filename        The name of the file to save
    def saveAsPNG(self, filename):
        pyplot.savefig(filename + '.png', dpi=200, format='png')


    ##  Export the chart in SVG format
    #   @param      filename        The name of the file to save
    def saveAsSVG(self, filename):
        pyplot.savefig(filename + '.svg', dpi=200, format='svg')



#nothing to run directly from here
if __name__ == "__main__":
    print("Nothing to run here! Execute the main application file instead!")
