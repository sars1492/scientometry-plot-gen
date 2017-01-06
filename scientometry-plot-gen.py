#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#
# scientometry-plot-gen.py -- A scientometric plot generator script.
#n
# Copyright (C) 2016, 2017  Juraj Szász <juraj.szasz3@gmail.com>
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

"""A scientometry plot generator script.

usage: scientometry-plot-gen.py [-h] [-m MEATADATA_FILE] [PLOT [PLOT ...]]

Generate set of scientometric plots defined by METADATA_FILE
('plot-metadata.yaml' as default).  Individual PLOT entries has to match
sections of the metadata file.  If no PLOT is specified, all plots defined
in METADATA_FILE will be generated.

positional arguments:
  PLOT               plot name defined in METADATA_FILE

optional arguments:
  -h, --help         show this help message and exit

  -m MEATADATA_FILE  load metadata from METADATA_FILE

Data for each individual plot are loaded from a file in CSV format, named
'<PLOT_NAME>.csv', which has to be located in the working directory. The data
file name can be also specified instead of plot name when selecting a subset of
plots via PLOT argument(s). This comes very handy when using tab completititon.

"""

from __future__ import unicode_literals
from __future__ import division
import argparse
import yaml
import unicodecsv
import numpy as np
from matplotlib import rc
import matplotlib.pyplot as plt

__version__ = "0.3"


CM_PER_INCH = 2.54
"""Unit conversion constant (centimeters per inch)."""


class PlotMetadata(object):

    """Metadata container for a single plot.

    PlotMetadata object stores metadata for a single plot in the format that can
    be directly passed to to Plot object.

    Attributes:
    output_file -- output image file name
    format -- output image format
    resolution -- output image resolution (in DPI)
    figsize -- physical size of output image (in inches)
    data_file -- data file name
    suptitle -- supereme title of the figure
    suptitle_fontsize -- font size of the supreme title (in pt)
    title -- title of the plot
    title_fontsize -- font size of the plot title (in pt)
    title_y -- vertical shift of the plot title (in y-axis units)
    xlabel -- label of the x-axis
    ylabel -- label of the y-axis
    axislabel_fontsize -- font size of the axis labels (in pt)
    ticklabel_fontsize -- font size of the tick labels (in pt)
    ymax -- maximal value of the y-axis range
    legend -- list of dataset labels in the legend box
    legend_fontsize -- font size of the dataset labels in legend box (in pt)
    legend_loc -- legend box location ('right', 'center left', 'upper right',
                  'lower right', 'best', 'center', 'lower left', 'center right',
                  'upper left', 'upper center' or 'lower center')
    barcolors -- list of bar colors of the individual datasets
    barwidth -- bar width (in x-axis units)

    """

    def __init__(self, plot_name, plot_metadata):
        """Initialize PlotMetadata object.

        Encapsulates plot metadata loaded by MetadataFileParser into a container
        object (PlotMetadata).  The 'output_file' and 'data_file' attributes are
        automatically derived from the 'plot_name' argument.  The output image
        dimensions ('figsize') is converted into inches, because Plot object
        requires it in inches.

        Positional arguments:
        plot_name -- name of the plot
        plot_metadata -- metadata dictionary extracted by MetadataFileParser

        """
        self.output_file = "plot-" + plot_name + "." + plot_metadata['format']
        self.format = plot_metadata['format']
        self.resolution = plot_metadata['resolution']
        self.figsize = [x / CM_PER_INCH for x in plot_metadata['figsize']]
        self.data_file = plot_name + ".csv"
        self.suptitle = plot_metadata['suptitle']
        self.suptitle_fontsize = plot_metadata['suptitle_fontsize']
        self.title = plot_metadata['title']
        self.title_fontsize = plot_metadata['title_fontsize']
        self.title_y = plot_metadata['title_y']
        self.xlabel = plot_metadata['xlabel']
        self.ylabel = plot_metadata['ylabel']
        self.axislabel_fontsize = plot_metadata['axislabel_fontsize']
        self.ticklabel_fontsize = plot_metadata['ticklabel_fontsize']
        self.ymax = plot_metadata['ymax']
        self.legend = plot_metadata['legend']
        self.legend_fontsize = plot_metadata['legend_fontsize']
        self.legend_loc = plot_metadata['legend_loc']
        self.barcolors = plot_metadata['barcolors']
        self.barwidth = plot_metadata['barwidth']


class MetadataFileParser(object):

    """Metadata YAML file parser.

    Parses metadata YAML file and extracts them into a dictionary of PlotMetadata
    objects {'plot_name': PlotMetadata object}, containing metadata of all plots
    found in the parsed metadata file ('plot_metadata_dict').

    Attributes:
    plot_metadata_dict -- dict containing PlotMetadata objects for all plots

    """

    def __init__(self, metadata_file):
        """Initialize MetadataFileParser object.

        Parses metadata YAML file ('metadata_file') and extracts plot metadata
        from the individual sections.  The 'defaults' section is extracted first
        and its content is then merged into every single plot-specific metadata.
        The resulting dictionary is being used for instantiation of the
        PlotMetadata object for each individual plot.  These objects are stored
        into the 'plot_metadata_dict' attribute.

        Positional arguments:
        metadata_file -- metadata YAML file name

        """
        with open(metadata_file, 'r') as yaml_file:
            yaml_dict = yaml.load(yaml_file)

        plot_metadata_dict = {}
        default_metadata = yaml_dict['defaults']

        for section, metadata in yaml_dict.iteritems():
            if section != 'defaults':
                plot_metadata_dict[section] = PlotMetadata(section, dict(default_metadata.items() + metadata.items()))

        self.plot_metadata_dict = plot_metadata_dict

    def select_plots(self, selected_plots=None):
        """Select subset of PlotMetadata objects from 'plot_metadata_dict'.

        Selects subset of PlotMetadata objects defined by the 'selected_plots'
        argument from the 'plot_metadata_dict' attribute.  If the argument is
        undefined, all available PlotMetadata objects will be selected.

        Keyword arguments:
        selected_plots -- list of plot names (default: None)

        Returns list of PlotMetadata objects for the selected plots.

        """
        if selected_plots:
            return [self.plot_metadata_dict[x] for x in selected_plots]
        else:
            return self.plot_metadata_dict.values()


class PlotData(object):

    """Data container for a single plot.

    Parses CSV plot data file and extracts list of dataset labels
    ('dataset_labels'), list of xtick_labels ('xtick_labels') and numpy array of
    the actual data ('plot_data').  Data are saved in a matrix (Y1, Y2, ...),
    where each column contains a vector of Y values for individual dataset.  The
    column order matches the order of 'dataset_labels' entries.

    Attributes:
    plot_data -- numpy array containing data for a single plot
    dataset_names -- list of dataset names (data column headers)
    xtick_names -- list of x-tick names (data row labels)

    """

    def __init__(self, data_file):
        """Parse data file and initialze PlotData object.

        Uses unicodecsv.reader to parse given CSV file ('data_file') and
        extracts its contents into 'plot_data', 'dataset_names' and
        'xtick_names' attributes.  The first line of CSV file is interpreted as
        data header and the headers of the data columns (i.e. all but first
        column) are saved into 'dataset_names'.  List of string values in the
        first column are saved into 'xtick_names'.  Data values are converted
        into float and then saved as numpy array.

        Positional arguments:
        data_file -- data file name

        """
        with open(data_file, 'r') as csv_file:
            csv_reader = unicodecsv.reader(csv_file, encoding='utf-8-sig')
            dataset_names = csv_reader.next()[1:]

            xtick_names = []
            data = []
            for row in csv_reader:
                xtick_names.append(row[0])
                data.append([float(x) for x in row[1:]])

        self.dataset_names = dataset_names
        self.xtick_names = xtick_names
        self.plot_data = np.array(data)

    def count(self):
        """Returns total amount of data (number of rows)."""
        return self.plot_data.shape[0]

    def dataset_count(self):
        """Returns total amount of datasets (number of columns)."""
        return self.plot_data.shape[1]

    def get_y(self):
        """Returns list of lists of y values."""
        return self.plot_data.transpose()


class Plot(object):

    """Wrapper class for rendering a single plot using matplotlib.

    Renders single plot based on the supplied metadata and data.

    Attributes:
    metadata -- PlotMetadata object containing actual plot metadata
    data -- PlotData object containing actual plot data

    """

    def __init__(self, plot_metadata):
        """Initialize Plot object.

        Initializes both 'metadata' and 'data' attributes from the given
        PlotMetadata object ('plot_metadata' argument).

        Positional arguments:
        plot_metadata -- object containing all metadata for actual plot

        """
        self.metadata = plot_metadata
        self.data = PlotData(self.metadata.data_file)

    def render(self):
        """Render a single plot figure based on actual plot data and metadata.

        Uses matplotlib to render a fancy scientometric bar chart based on the
        'metadata' and 'data' attributes.  The bar chart is now optimized for
        two datasets; nevertheless, it can be easily tweaked to any number of
        datasets.  The figure supreme title and tick labels of x-axis are
        formatted in bold font because it just looks cool.  Note that the
        maximal value of the y-axis range is not calculated by this method.  You
        need to set it explicitly for each plot using 'ymax' parameter.

        """
        # Set global font family
        rc('font', family='Liberation Sans')

        # Initialize figure object
        fig = plt.figure(figsize=self.metadata.figsize)
        fig.suptitle(self.metadata.suptitle, fontsize=self.metadata.suptitle_fontsize, fontweight='bold')

        # Add subplot
        ax = fig.add_subplot(111)
        ax.set_title(self.metadata.title, fontsize=self.metadata.title_fontsize, y=self.metadata.title_y)

        # Define helper variables
        dataset_count = self.data.dataset_count()
        ind = np.arange(self.data.count())    # tick indices for x-axis
        width = self.metadata.barwidth        # width of a bar (in x-axis units)
        group_width = dataset_count*width     # width of a group of bars
        right_edge = len(ind)-1 + group_width # right edge of last plotted bar
        Y = self.data.get_y()                 # matrix of datasets

        # Create bars and legend handles for individual datasets
        legend_handles = []
        for i in xrange(dataset_count):
            bar = ax.bar(ind + i*width, Y[i], width, color=self.metadata.barcolors[i])
            legend_handles.append(bar[0])

        # Set x-axis ticks and labels
        ax.set_xlabel(self.metadata.xlabel, fontsize=self.metadata.axislabel_fontsize)
        ax.set_xlim(-group_width/2, right_edge + group_width/2)
        ax.set_xticks(ind + group_width/2)

        xtick_names = ax.set_xticklabels(self.data.xtick_names)
        plt.setp(xtick_names, fontsize=self.metadata.ticklabel_fontsize, fontweight='bold')

        # Set y-axis ticks and labels
        ax.set_ylabel(self.metadata.ylabel, fontsize=self.metadata.axislabel_fontsize)
        ax.set_ylim(0, self.metadata.ymax)
        plt.tick_params(labelsize=self.metadata.ticklabel_fontsize)

        # Add grid
        plt.grid()

        # Add legend box
        ax.legend(legend_handles, self.metadata.legend, fontsize=self.metadata.legend_fontsize, loc=self.metadata.legend_loc)

        # Export output image
        fig.savefig(self.metadata.output_file, format=self.metadata.format, dpi=self.metadata.resolution, bbox_inches='tight')


def main():
    """Run initial code when this module is executed as a script.

    1. Parse command line arguments using argparse.ArgumentParser object.
    2. Extract plot metadata from YAML file into the list of PlotMetadata
       objects using MetadataFileParser object.
    3. Instantiate Plot objects in a loop and render all output files.

    """
    description = "Generate set of scientometric plots defined by " + \
                  "METADATA_FILE ('plot-metadata.yaml' as default).  If no " + \
                  "PLOT is specified, all plots defined in METADATA_FILE " + \
                  "will be generated."
    epilog = "Data for each individual plot are loaded from a file in CSV " + \
             "format, named  '<PLOT_NAME>.csv', which has to be located in " + \
             "the working directory.  The data file name can be also " + \
             "specified instead of plot name when selecting a subset of " + \
             "plots via PLOT argument(s).  This comes very handy when " + \
             "using tab completititon."
    arg_parser = argparse.ArgumentParser(description=description, epilog=epilog)
    arg_parser.add_argument("-m", metavar="MEATADATA_FILE", dest='metadata_file', default="plot-metadata.yaml",
                            help="load metadata from METADATA_FILE")
    arg_parser.add_argument("plots", metavar="PLOT", nargs='*',
                            help="plot name defined in METADATA_FILE")
    args = arg_parser.parse_args()

    metadata_file_parser = MetadataFileParser(args.metadata_file)
    # The list comprehension in the following line strips '.csv' suffix from the
    # individual args.plots elements before they will be passed to
    # select_plots() method.  This allows user to specify data file names
    # instead of plot names (comes very handy when using tab completition).
    plot_metadata_list = metadata_file_parser.select_plots([x.rsplit(".csv", 1)[0] for x in args.plots])

    for plot_metadata in plot_metadata_list:
        plot = Plot(plot_metadata)
        print "Generating", plot_metadata.output_file, "..."
        plot.render()


if __name__ == "__main__":
    # This code is executed only when scientometry-plot-gen is being run
    # directly as a script.  Since local variables are allocated much faster
    # than global variables, it is a good practice to encapsulate whole initial
    # code into the main() function.
    main()
