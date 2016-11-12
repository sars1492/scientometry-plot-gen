scientomery-plot-gen
====================

A scientometric plot generator that uses *matplotlib* to generate set of
scientometric plots for publishing purposes.


Introduction:
-------------

The *scientometry-plot-gen* is the command line plot generator that produces a
set of bar chart plots visualizing publication and citation statistics over
range of years.  All relevant metadata for individual plots are defined by YAML
file.  Plot data are being loaded from the set of data files in CSV format
located in the same directory.


Synopsis:
---------

```
./scientometry-plot-gen.py [-h] [-m MEATADATA_FILE] [PLOT [PLOT ...]]

Generate set of scientometric plots defined by METADATA_FILE. If no PLOT is
specified, all plots defined in METADATA_FILE will be generated.

positional arguments:
  PLOT               plot name defined in METADATA_FILE

optional arguments:
  -h, --help         show this help message and exit
  -m MEATADATA_FILE  load metadata from METADATA_FILE. Uses 'plot_metadata.yaml'
                     as default.
```


Metadata YAML file:
-------------------

The metadata YAML files has `defaults` section that is being applied to all
plots and individual plot sections that has to have the same names as individual
data files (without `.csv` extension).  Text in the YAML file can contain UTF-8
characters.

*Metadata keys:*

* `format` -- Format of the output file
* `resolution` -- Output resolution in dpi
* `figsize` -- Dimensions of the output figure (in cm)
* `suptitle_fontsize` -- Font size of the supreme title (in pt)
* `title_fontsize` -- Font size of the plot title (in pt)
* `ticklabel_fontsize` -- Font size of the tick labels (in pt)
* `axislabel_fontsize` -- Font size of the axis labels (in pt)
* `legend_fontsize` -- Font size of the legend labels (in pt)
* `barwidth` -- Relative width of the bars
* `barcolors` -- Bar colors for individual data sets
* `legend` -- Legend labels for individual data sets
* `suptitle` -- Supreme title of the figure
* `title` -- Plot title
* `title_y` -- Vertical shift of the plot title (relatively to plot border)
* `xlabel` -- Label of the x-axis
* `ylabel` -- Label of the y-axis
* `ymax` -- Maximal value of y-axis.

*Example:*

```yaml
defaults:
  format: png
  resolution: 150 # [dpi]
  figsize:
    - 25.4 # width [cm]
    - 15.5 # height [cm]
  suptitle_fontsize: 14
  title_fontsize: 12
  ticklabel_fontsize: 11
  axislabel_fontsize: 11
  legend_fontsize: 11
  title_y: 1.007
  barwidth: 0.3
  barcolors:
    - 'blue'
    - 'red'
  legend:
    - "Scopus"
    - "WoS"
  xlabel: "Year of Publishing"


# Biology Department Citations Plot
bio-citations:
  suptitle: "Biology Department"
  title: "Citations over 2000-2016"
  ylabel: "Citation Count"
  ymax: 90

# Biology Department Publication Activity Plot
bio-publications:
  suptitle: "Biology Department"
  title: "Publication activity over 2000-2016"
  ylabel: "Publication Count"
  ymax: 7.5
```


Examples:
---------

1. Generate all plots defined in metadata YAML file:

   `$ ./scientometry_plot_gen.py`

2. Generate plots named `all-publications` and `all-citations` that are defined
   in `plot-metadata.yaml` (the default metadata YAML file).

   `$ ./scientometry_plot_gen.py all-publications all-citations`

3. Since data file names have to match plot names, you can use names of the data
   files as well, the `.csv` suffix will be ignored.  That comes very handy
   when using Tab completition:

   `$ ./scientometry_plot_gen.py all-publications.csv all-citations.csv`

4. You can also load metadata from the alternative metadata YAML file.
   Following command generates all plots defined in `my-plots.yaml`:

   `$ ./scientometry_plot_gen.py -m my-plots.yaml`


License
-------

Copyright (C) 2016  Juraj Szász (juraj.szasz3@gmail.com)

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see http://www.gnu.org/licenses/.
