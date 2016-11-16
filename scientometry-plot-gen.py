#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# scientometry-plot-gen.py -- Scientometric plot generator
#
# Copyright (C) 2016  Juraj Szász <juraj.szasz3@gmail.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""Generate set of scientometric plots defined by METADATA_FILE.  If no PLOT is
specified, all plots defined in METADATA_FILE will be generated.
"""

from __future__ import unicode_literals
import argparse
import yaml
import numpy as np
from matplotlib import rc
import matplotlib.pyplot as plt

CM_PER_INCH = 2.54


class PlotMetadata:

    def __init__(self, plot_name, plot_metadata):
        self.plot_file = "plot-" + plot_name + "." + plot_metadata['format']
        self.data_file = plot_name + ".csv"
        self.suptitle = plot_metadata['suptitle']
        self.title = plot_metadata['title']
        self.xlabel = plot_metadata['xlabel']
        self.ylabel = plot_metadata['ylabel']
        self.ymax = plot_metadata['ymax']
        self.barcolors = plot_metadata['barcolors']
        self.barwidth = plot_metadata['barwidth']
        self.legend = plot_metadata['legend']
        self.format = plot_metadata['format']
        self.resolution = plot_metadata['resolution']
        self.figsize = [x / CM_PER_INCH for x in plot_metadata['figsize']]
        self.suptitle_fontsize = plot_metadata['suptitle_fontsize']
        self.title_fontsize = plot_metadata['title_fontsize']
        self.title_y = plot_metadata['title_y']
        self.ticklabel_fontsize = plot_metadata['ticklabel_fontsize']
        self.axislabel_fontsize = plot_metadata['axislabel_fontsize']
        self.legend_fontsize = plot_metadata['legend_fontsize']


class PlotMetadataFactory:

    def __init__(self, plot_metadata_file, selected_plots):
        with open(plot_metadata_file, 'r') as yaml_file:
            yaml_metadata = yaml.load(yaml_file)

        plot_metadata_list = []
        default_metadata = yaml_metadata['defaults']

        for plot, metadata in yaml_metadata.iteritems():
            if plot != 'defaults' and (not selected_plots or plot in selected_plots):
                plot_metadata_list.append(PlotMetadata(plot, dict(default_metadata.items() + metadata.items())))

        self.plot_metadata_list = plot_metadata_list

    def get_plots(self, plot_selection=None):
        return self.plot_metadata_list


class PlotData:

    def __init__(self, data_file):

        self.plot_data = np.genfromtxt(data_file, dtype=int, delimiter=',')

    def count(self):

        return self.plot_data.shape[0]

    def dataset_count(self):

        return self.plot_data.shape[1] - 1

    def get_x(self):

        return self.plot_data[:, 0]

    def get_y(self):

        return self.plot_data[:, 1:].transpose()


class Plot:

    def __init__(self, plot_metadata):
        self.metadata = plot_metadata
        self.data = PlotData(self.metadata.data_file)

    def render(self):

        rc('font', family='Liberation Sans')

        fig = plt.figure(figsize=self.metadata.figsize)

        plt.tick_params(labelsize=11)

        fig.suptitle(self.metadata.suptitle, fontsize=self.metadata.suptitle_fontsize, fontweight='bold')

        ax = fig.add_subplot(111)

        ind = np.arange(self.data.count())
        width = self.metadata.barwidth
        X = self.data.get_x()
        Y = self.data.get_y()

        print self.data.dataset_count()

        legend_handles = []
        for i in xrange(self.data.dataset_count()):
            bar = ax.bar(ind + i*width, Y[i], width, color=self.metadata.barcolors[i])
            legend_handles.append(bar[0])

        # axes and labels
        ax.set_xlim(-width, len(ind)+width)
        ax.set_ylim(0, self.metadata.ymax)
        ax.set_xlabel(self.metadata.xlabel, fontsize=self.metadata.axislabel_fontsize)
        ax.set_ylabel(self.metadata.ylabel, fontsize=self.metadata.axislabel_fontsize)

        ax.set_title(self.metadata.title, fontsize=self.metadata.title_fontsize, y=self.metadata.title_y)
        ax.set_xticks(ind+width)

        xtick_names = ax.set_xticklabels([str(year) for year in X])
        plt.setp(xtick_names, fontsize=self.metadata.ticklabel_fontsize, fontweight='bold')

        # add grid
        plt.grid()

        # add a legend
        ax.legend(legend_handles, self.metadata.legend, fontsize=self.metadata.legend_fontsize)

        fig.savefig(self.metadata.plot_file, format=self.metadata.format, dpi=self.metadata.resolution, bbox_inches='tight')


def main():
    """Run initial code when this module is executed as a script.

    1. Parse command line arguments using argparse.ArgumentParser object.
    2. Extract plot metadata from YAML file into the list of PlotMetadata
       objects using PlotMetadataFactory object.
    3. Instantiate Plot objects in a loop and render all output files.

    """
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument("-m", metavar="MEATADATA_FILE", dest='metadata_file', default="plot-metadata.yaml",
                            help="load metadata from METADATA_FILE. Uses 'plot_metadata.yaml' as default.")
    arg_parser.add_argument("plots", metavar="PLOT", nargs='*',
                            help="plot name defined in METADATA_FILE")
    args = arg_parser.parse_args()

    # Following line contains lambda function that removes '.csv' suffix from
    # the arguments and thus allows to specify data file names instead of plot
    # names.  This comes very handy when using tab completition.
    plot_metadata_factory = PlotMetadataFactory(args.metadata_file, [x.rsplit(".csv", 1)[0] for x in args.plots])
    plot_metadata_dict = plot_metadata_factory.get_plots()

    for plot_metadata in plot_metadata_dict:
        plot = Plot(plot_metadata)
        print "Generating", plot_metadata.plot_file, "..."
        plot.render()


if __name__ == "__main__":
    # This code is executed only when scientometry-plot-gen is being run
    # directly as a script.  Since local variables are allocated much faster
    # than global variables, it is a good practice to encapsulate whole initial
    # code into the main() function.
    main()
