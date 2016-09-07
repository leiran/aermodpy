#!/usr/bin/env python
"""Python interface to AERMOD modeling system files.

design notes:
+ Bug on POST processing; only processes 996 hours
   - proposed fix: in-place averaging, discard hourly data

developed for python 3.x
   """

# docstring metadata
__author__ = "Leiran Biton"
__copyright__ = "Copyright 2015"
__credits__ = []
__license__ = "GPL"
__version__ = "0.11"
__maintainer__ = "Leiran Biton"
__email__ = "leiranbiton@gmail.com"
__status__ = "Production"

# standard library imports
import os.path
import datetime
import numpy
import csv

# internal package imports
from aermodpy.support import pollutant_dict, vars_indices, ordinal

class point(object):
    def __init__(self, num, **kwargs):
        """Point object 
        
        mandatory arguments:
        num - number of points
        
        optional arguments:
        Xs  - array of x locations for # of points. default = zeros
        Ys  - array of y locations for # of points. default = zeros
        Zs  - array of z locations for # of points. default = zeros
        XYs - array shape=(num, 2) of x and y locations for # of points. replaces Xs & Ys.
        XYZs - array shape=(num, 3) of x, y, and z locations for # of points. replaces Xs, Ys, and Zs.
        """
        self.num = num
        self.X = kwargs.get("Xs", numpy.zeros(num))
        self.Y = kwargs.get("Ys", numpy.zeros(num))
        self.Z = kwargs.get("Zs", numpy.zeros(num))
        if "XYs" in kwargs:
            self.X = kwargs["XYs"][:,0]
            self.Y = kwargs["XYs"][:,1]
        if "XYZs" in kwargs:
            self.X = kwargs["XYZs"][:,0]
            self.Y = kwargs["XYZs"][:,1]
            self.Z = kwargs["XYZs"][:,2]

class post:
    "POST file processor"
    
    verbose = False
    DEBUG   = False
    
    # default data
    formatstring = "(3(1X,F13.5),3(1X,F8.2),3X,A5,2X,A8,2X,A4,6X,A8,2X,I8)"
    vars_index = None
    
    
    def __init__(self
                ,filename
                ,directory="."
                ,receptors=0
                ,formatstring_override=False
                ,century=20
                ,vars_index=vars_indices["post"]
                ,verbose=True
                ,DEBUG=False
                ):
        self.POSTfile = self.openfile(filename, directory=directory, mode="rU")
        self.century = century
        self.datetimes = [] # empty list for datetime objects
        self.modeldoc  = []
        self.datatypes = []
        self.POSTdata  = {}
        self.receptors = point(receptors)
        self.formatstring_override = formatstring_override
        self.vars_index = vars_index
        self.verbose = verbose
        self.DEBUG = DEBUG
        
    def decode_format_datastring(self
                                ,formatstring):
        """placeholder function for decoding a string describing POST file dataformat"""
        # example format '*         FORMAT: (3(1X,F13.5),3(1X,F8.2),3X,A5,2X,A8,2X,A4,6X,A8,2X,I8)'
        return formatstring
    
    def decode_data(self
                   ,dataline
                   #,formatstring=formatstring
                   ):
        # example format '*         FORMAT: (3(1X,F13.5),3(1X,F8.2),3X,A5,2X,A8,2X,A4,6X,A8,2X,I8)'
        # example head   '*         X             Y      AVERAGE CONC    ZELEV    ZHILL    ZFLAG    AVE     GRP       HIVAL    NET ID   DATE(CONC)\n
        # example data   ' 569830.00000 4909393.00000    3065.99300   494.10   747.20     0.00    1-HR  ALL                           08033104\n'
        #if self.formatstring_override:
        #    self.decode_format_datastring(self, formatstring)
        if all([datetime_part in self.vars_index for datetime_part in ("year","month","day","hour")]):
            dt = datetime.datetime(self.vars_index["year"]["type"](dataline[self.vars_index["year"]["start"]:
                                                                            self.vars_index["year"]["end"  ]]) + self.century*100
                                  ,self.vars_index["month"]["type"](dataline[self.vars_index["month"]["start"]:
                                                                             self.vars_index["month"]["end"  ]])
                                  ,self.vars_index["day"]["type"](dataline[self.vars_index["day"]["start"]:
                                                                           self.vars_index["day"]["end"  ]])
                                  ,self.vars_index["hour"]["type"](dataline[self.vars_index["hour"]["start"]:
                                                                            self.vars_index["hour"]["end"  ]]) - 1
                                  )
        else: 
            dt = None
        return [self.vars_index[var]["type"](dataline[self.vars_index[var]["start"]:self.vars_index[var]["end"]]) 
                    for var in ["x", "y", "zflag","conc"]
               ],  dt
            
    def add_buildings(self
                     ,filename
                     ,directory="."
                     ,nosources=False
                     ):
        
        self.building_vertices = {}
        self.sources = {}
        
        if self.verbose: print("--> opening building data file")
        self.building_file = self.openfile(filename, directory, "rU")
        
        # throw away header data
        [next(self.building_file) for header in range(2)]
        
        units, unit_value = next(self.building_file).split()
        if self.DEBUG: print("DEBUG: units / unit_value:", units, unit_value)
        
        utmy, trash = next(self.building_file).split()
        num_bldgs = int(next(self.building_file))
        if self.DEBUG: print("DEBUG: number of buildings:", num_bldgs)
        
        for building in range(num_bldgs):
            try:
                name, stories, elev = self.building_header()
                self.process_building(name, stories, elev)
            except:
                raise Exception("No more buildings to process")
        if not nosources:
            num_srcs = int(next(self.building_file))
            for src in range(num_srcs):
                try:
                    raw_source_line = next(self.building_file).strip()
                    source_descriptors = raw_source_line.replace("'", "").split(sep=None, maxsplit=5)
                    if len(source_descriptors) == 5:
                        name, elev, height, x, y = source_descriptors
                    else:
                        trash, elev, height, x, y, name = source_descriptors
                    name = name.strip()
                    if self.DEBUG: print("DEBUG: source name:", name, x, y)
                    self.sources[(name)] = \
                        point(1, Xs=numpy.array(float(x))
                               , Ys=numpy.array(float(y))
                               )
                    if self.verbose: print("adding source:", self.sources[(name)].X, self.sources[(name)].Y)
                except:
                    raise Exception("No more sources to process")
    
    def building_header(self):
        """get building data for new building"""
        building_descriptors = next(self.building_file).split(sep=None, maxsplit=3)
        if len(building_descriptors) == 3:
           name_padded, stories, base_elevation = building_descriptors
        else:
           trash, stories, base_elevation, name_padded = building_descriptors
        if self.verbose: print("adding building: ", name_padded.strip(), stories, base_elevation)
        
        return name_padded.strip().replace("'",""), int(stories), float(base_elevation)
    
    def process_building(self
                        ,name
                        ,stories
                        ,base_elevation
                        ):
        """adds building data to the self.building_vertices dictionary"""
        for story in range(stories):
            self.process_building_story(name, story+1)
    
    def process_building_story(self
                              ,name
                              ,story
                              ):
        """process a building story"""
        vertices, height = next(self.building_file).split()
        vertices = int(vertices)
        height   = float(height)
        vs = numpy.array([(float(X), float(Y)) for (X, Y) in \
                         [next(self.building_file).split() for v in range(vertices)] \
                         ]).reshape(vertices, 2)
        self.building_vertices[(name, story)] = point(vertices, XYs=vs)
    
    def openfile(self
                ,filename
                ,directory="."
                ,mode="rU"
                ):
        # files
        try: 
            filepath = directory + os.path.sep + filename
        except TypeError:
            raise TypeError("Invalid 'directory' or 'filename' inputs!")
        
        if self.verbose: print("Opening file:", filepath)
        if self.verbose: print("                 mode =", mode)
        try: openfile = open(filepath, mode)
        except:
            raise IOError("Filepath '%s' failed to open. Check the address and mode." % filepath)
        
        return openfile
    
    def getPOSTfileMetaData(self):
        """Get metadata from POSTfile"""
        try:
            [filetype_doc
            ,optionsflag_doc
            ,modeloptions_doc
            ,datatype_doc
            ,receptors_doc
            ,dataformat_doc
            ] = [next(self.POSTfile) for i in range(6)]
            
        except:
            raise Exception("POST file does not contain proper header metadata")
        
        # extract format string from data format documentation
        if self.DEBUG: print("DEBUG: filetype_doc =", filetype_doc)
        if self.DEBUG: print("DEBUG: dataformat_doc =", dataformat_doc)
        dataformat_string = dataformat_doc[dataformat_doc.index(":")+1:].strip()
        # decode data format string
        dataformat = self.decode_format_datastring(dataformat_string)
        
        if self.formatstring_override:
            # function still in development
            self.formatstring = dataformat
        else: 
            self.modeldoc.append((filetype_doc
                                 ,optionsflag_doc
                                 ,modeloptions_doc
                                 ,datatype_doc
                                 ,receptors_doc
                                 ,dataformat_doc
                                 ))
            datatype_metadata = datatype_doc.split()
            r_type = datatype_metadata[datatype_metadata.index("VALUES")-1]
            r_form = datatype_metadata[datatype_metadata.index("OF")+1:\
                                       datatype_metadata.index("VALUES")-1]
            r_form = " ".join(r_form)
            source_group = datatype_metadata[-1]
            if self.DEBUG: print("DEBUG:", r_type, r_form, source_group)
            self.datatypes.append((r_type, r_form, source_group))
            self.POSTdata[(r_type, r_form, source_group)] = numpy.zeros([self.receptors.num, 1])
        
        if len(self.modeldoc) == 1:
            n_receptors = [int(s) for s in receptors_doc.split() if s.isdigit()][0]
            self.receptors = point(n_receptors)
        
    def getPOSTfileHeader(self):
        """Get metadata from POSTfile"""
        self.fileheader = next(self.POSTfile).strip()
        next(self.POSTfile) # -------- line
        
    def printResults(self, filename, r_type, **kwargs):
        """print(r_type results data array to outfile as comma separated values)"""
        outfile = self.openfile(filename, directory=kwargs.get("directory", "."), mode="w")
        self.POSTdata[(r_type, r_form, source_group)].tofile(outfile, sep=",")
        outfile.close()
        
    def scalePOSTdata(self, r_type, **kwargs):
        """scales POSTdata result_type using optional "scalar" keyword argument. if omitted, 1.0."""
        if self.DEBUG: print("DEBUG: scaling %s results by" % r_type, kwargs.get("scalar", 1.0))
        self.POSTdata[(r_type, r_form, source_group)] *= kwargs.get("scalar", 1.0)
        
    def processPOSTData(self
                       ,ranked=1
                       ,annual=False
                       ):
        """Process stored POST file data"""
        if self.verbose: print("--> processing open data file")
        
        while True:
            try:
                self.getPOSTfileMetaData()
                self.getPOSTfileHeader()
                
                self.POSTdata[self.datatypes[-1]] = numpy.zeros([self.receptors.num, ranked])
                h = 0
                if "hour" in self.vars_index:
                    while True:
                        try:
                            self.getPOSTfileData(h=h, annual=annual, ranked=ranked)
                            h += 1
                        except Exception as e:
                            if self.DEBUG: 
                                print("DEBUG: reached exception during file processing")
                                print("DEBUG:", "Unexpected error:", e)
                                print("      ", self.datetimes[-1])
                            return
                else:
                    try:
                        self.getPOSTfileData(h=h, annual=annual, ranked=ranked)
                        if self.DEBUG: 
                            print("DEBUG: got 1 instance of POST data")
                    except:
                        return
            except:
                return
        
    def getPOSTfileData(self
                       ,h=0
                       ,annual=False
                       ,ranked=1
                       ):
        """Get data from POSTfile, process for average number of hours"""
        if self.verbose: print("--> retrieving data")
        
        if h == 0:
            self.POSTdata[self.datatypes[-1]] = numpy.zeros([self.receptors.num, ranked])
            if annual:
                self.POSTdata[self.datatypes[-1]] = numpy.expand_dims(self.POSTdata[self.datatypes[-1]], axis=2)
        
        for r in range(self.receptors.num):
            line = next(self.POSTfile)
            
            # decode data
            data4hour, dt = self.decode_data(line)
            
            # build datetime list
            if r == 0:
                if self.DEBUG: print("DEBUG:", "processing for", dt)
                if annual and (h > 0) and (dt.year > self.datetimes[-1].year):
                    self.POSTdata[self.datatypes[-1]] = numpy.append(self.POSTdata[self.datatypes[-1]]
                                                                    ,numpy.zeros([self.receptors.num, ranked, 1])
                                                                    ,axis=2
                                                                    )
                self.datetimes.append(dt)
            
            # populate receptor location values
            if h == 0:
                self.receptors.X[r] = data4hour[0]
                self.receptors.Y[r] = data4hour[1]
                self.receptors.Z[r] = data4hour[2]
            
            if annual:
                receptor_data = numpy.append(self.POSTdata[self.datatypes[-1]][r,:,-1], [data4hour[3]], axis=1)
                receptor_data.sort()
                self.POSTdata[self.datatypes[-1]][r,:,-1] = receptor_data[::-1][:ranked]
            else:
                receptor_data = numpy.append(self.POSTdata[self.datatypes[-1]][r,:], [data4hour[3]], axis=1)
                receptor_data.sort()
                self.POSTdata[self.datatypes[-1]][r,:] = receptor_data[::-1][:ranked]
        return
    
    def draw_building(self
                     ,building
                     ,story
                     ,axis
                     ,origin=point(1,Xs=[0],Ys=[0])
                     ,**kwargs
                     ):
        
        import matplotlib.patches as patches
        from matplotlib.path import Path
        
        """method for drawing buildings"""
        
        # create polygon using path method
        verts = [(x-origin.X, y-origin.Y) \
                 for (x, y)              \
                 in zip(self.building_vertices[(building, story)].X
                       ,self.building_vertices[(building, story)].Y
                       )]
        verts.append(verts[0])  # add first point to close polygon
        codes     = [Path.LINETO for coords in verts]
        codes[0]  = Path.MOVETO
        codes[-1] = Path.CLOSEPOLY
        path = Path(verts, codes)
        patch = patches.PathPatch(path
                                 ,facecolor=kwargs.get("color", "white")
                                 ,edgecolor='black'
                                 ,linewidth=kwargs.get("linewidth", 0.4)
                                 ,alpha=kwargs.get("alpha", 1.00)
                                 )
        axis.add_patch(patch)
        if kwargs.get("building_name", False) and (story == 1):
            axis.annotate(str(building)
                         ,xy=((self.building_vertices[(building, story)].X - origin.X).mean()
                             ,(self.building_vertices[(building, story)].Y - origin.Y).mean())
                         ,va="center"
                         ,ha="center"
                         ,color="blue"
                         ,size=kwargs.get("max_textsize", 8)
                         )
    
    def printdata(self
                ,r_type
                ,r_form # datatype key for POSTdata
                ,source_group
                ,filename="aermod_results.csv"
                ,directory="."
                ,**kwargs
                ):
        with self.openfile(filename, directory, "w") as csvoutfile:
            csvoutfile.write(r_type+"\n")
            csvoutfile.write(r_form+"\n")
            csvoutfile.write(source_group+"\n")
            w = csv.writer(csvoutfile)
            rank = kwargs.get("ranked_data", 0)
            rank_index = 0 if rank == 0 else rank-1
            if kwargs.get("exclude_flagpole_receptors", False):
                concs = self.POSTdata[(r_type, r_form, source_group)][:,rank_index][self.receptors.Z==0] * kwargs.get("scalar", 1.0) + kwargs.get("add_background", 0.0)
            else:
                concs = self.POSTdata[(r_type, r_form, source_group)][:,rank_index] * kwargs.get("scalar", 1.0) + kwargs.get("add_background", 0.0)
            outlist = [kwargs.get("scale_decimals","%0.0f") % concs.max()]
            w.writerow(outlist)
    
    def gridplot(self
                ,r_type
                ,r_form # datatype key for POSTdata
                ,source_group
                ,levels=[0,10,20,30,40,50,60,70,80,90,100,150,200,250,300]
                ,**kwargs
                ):
        """creates an individual grid plot based on input concentration array
        
        kwargs:
        contours   - width of contour lines to draw. no contour lines if omitted
        levels     - list of levels to be used in the contour plots
        receptor_size - an integer for sizing the receptors to be plotted. default = 15. enter 0 to omit.
        plot_max   - an integer for sizing the datapoint for the max conc in the domain. enter 0 to omit.
        distance_from_origin - 
        receptor_type - receptor representation as matplotlib marker indicators (default=".")
        max_plot - if 0, maximum point omitted.
        tickinterval - interval of x and y axes
        noticks - if True, omit x-y ticks
        labelsize - size of colorbar and x-y tick labels
        labelgap - gap between ticks and labels
        nocolorbar - if True: colorbar omitted
        scale_decimals - colorbar number formatting (e.g. "%0.0f")
        filename - string for filename. default: "aermod.png"
        colorbar_spacing - "uniform" or "proportional" (default = "proportional")
        interpolation_method - linear cubic nearest
        contour_colors - list of contour colors to use for contours. if omitted, hot colorscale is used.
        colorslevels - colors and levels
        scalar - multiplier for concentration data
        exclude_flagpole_receptors - Default = False, set to True to exclude flagpole receptors
        add_background - Default value = 0.0
        ranked_data - use ranked dataset of value n. Default=1.
        annual - POSTdata has annual values (default=False)
        """
        import matplotlib
        import matplotlib.pyplot as plt
        #from scipy.interpolate import griddata
        from matplotlib.mlab import griddata
        
        if kwargs.get("exclude_flagpole_receptors", False):
            if self.DEBUG: print("DEBUG: removing flagpole receptors")
            receptor_array = numpy.column_stack((self.receptors.X[self.receptors.Z==0]
                                               ,self.receptors.Y[self.receptors.Z==0]
                                               ,self.receptors.Z[self.receptors.Z==0]))
        else:
            receptor_array = numpy.column_stack((self.receptors.X, self.receptors.Y, self.receptors.Z))
        
        receptor_num = len(receptor_array)
        receptors = point(receptor_num
                         ,XYZs=receptor_array)
        
        rank = kwargs.get("ranked_data", 0)
        rank_index = 0 if rank == 0 else rank-1
        
        if kwargs.get("annual", False):
            if self.DEBUG: print("DEBUG: 'annual' flag is on. Averaging all years.")
            if kwargs.get("exclude_flagpole_receptors", False):
                if self.DEBUG: print("DEBUG: removing flagplot data")
                concs = numpy.mean(self.POSTdata[(r_type, r_form, source_group)][:,rank_index,:], axis=1)[self.receptors.Z==0] * kwargs.get("scalar", 1.0) + kwargs.get("add_background", 0.0)
            else:
                concs = numpy.mean(self.POSTdata[(r_type, r_form, source_group)][:,rank_index,:], axis=1) * kwargs.get("scalar", 1.0) + kwargs.get("add_background", 0.0)
        else:
            if kwargs.get("exclude_flagpole_receptors", False):
                if self.DEBUG: print("DEBUG: removing flagplot data")
                concs = self.POSTdata[(r_type, r_form, source_group)][:,rank_index][self.receptors.Z==0] * kwargs.get("scalar", 1.0) + kwargs.get("add_background", 0.0)
            else:
                concs = self.POSTdata[(r_type, r_form, source_group)][:,rank_index] * kwargs.get("scalar", 1.0) + kwargs.get("add_background", 0.0)
        
        # define grid.
        
        x_range = receptors.X.max() - receptors.X.min()
        y_range = receptors.Y.max() - receptors.Y.min()
        xi = numpy.linspace(receptors.X.min(), receptors.X.max(), round(receptors.num**0.85))
        yi = numpy.linspace(receptors.Y.min(), receptors.Y.max(), round(receptors.num**0.85))
        
        distance_from_origin = kwargs.get("distance_from_origin", max(x_range/2, y_range/2))
        if self.DEBUG: print("DEBUG: distance_from_origin -", distance_from_origin)
        
        origin = point(1)
        origin.X = (receptors.X.max() + receptors.X.min())/2
        origin.Y = (receptors.Y.max() + receptors.Y.min())/2
        
        # instantiate figure
        figure = plt.figure(num=None
                           ,figsize=(6.5, 6) if kwargs.get("nocolorbar", False) else (8, 6)
                           ,dpi=80
                           ,facecolor="white"
                           ,edgecolor="black"
                           )
        ax = figure.add_subplot(111
                               ,aspect="equal"
                               )
        
        # grid the data.
        if self.DEBUG: print("DEBUG: receptors.X:", type(receptors.X), receptors.X)
        if self.DEBUG: print("DEBUG: receptors.X:", type(receptors.Y), receptors.Y)
        zi = griddata(receptors.X - origin.X,
                      receptors.Y - origin.Y,
                      concs, 
                      0, 0,
                      interp = kwargs.get("interpolation_method", "linear"))
        if self.DEBUG: print("DEBUG:", zi)
        
        # define contour levels and colors
        if kwargs.get("colorslevels", None):
            levels = [level for level, color, label in kwargs["colorslevels"]]
            kwargs["levels"] = levels
            kwargs["contour_colors"] = [color for level, color, label in kwargs["colorslevels"]]
        
        # draw the contours using contour(X,Y,Z,V) formulation (see documentation)
        CS = plt.contour(xi - origin.X,  # X
                         yi - origin.Y,  # Y
                         zi,             # Z
                         levels,         # V
                         linewidths=float(kwargs.get("contours", 0)),
                         colors="black")
        
        # fill the contours
        if kwargs.get("contour_colors", None):
            cmap, norm = matplotlib.colors.from_levels_and_colors(levels=levels
                                                                 ,colors=kwargs.get("contour_colors", ["white" for level in levels])[:-1]
                                                                 ,extend="neither"
                                                                 )
        else:
            cmap = plt.cm.hot_r
            norm = matplotlib.colors.Normalize(vmin=0, vmax=1)
        
        CS = plt.contourf(xi - origin.X
                         ,yi - origin.Y
                         ,zi
                         ,levels
                         ,cmap=cmap
                         ,norm=norm
                         )
        
        # prepare the colorbar
        if not kwargs.get("nocolorbar", False):
            matplotlib.rcParams['xtick.direction'] = 'out'
            matplotlib.rcParams['ytick.direction'] = 'out'
            
            if kwargs.get("colorslevels", False):
                if self.DEBUG: print("DEBUG: setting colorbar labels")
                labels = [label for level, color, label in kwargs.get("colorslevels", False)]
            else:
                labels = ["" for level in levels]
            
            colorbar = figure.colorbar(CS
                                      ,ax=ax
                                      ,format=kwargs.get("scale_decimals", "%0.1f")
                                      ,spacing=kwargs.get("colorbar_spacing", "proportional")
                                      ,shrink=1.0 # same size as map
                                      )
            
            display_units = pollutant_dict[kwargs["pollutant"]][1]
            colorbar.set_label("Concentration (%s)" %display_units
                              ,size=kwargs.get("max_textsize", 10)
                              )
            
            colorbar.set_ticks(levels)
            colorbar.set_ticklabels(labels)
            colorbar.ax.tick_params(labelsize=kwargs.get("labelsize", 10)
                                   ,colors="black"
                                   ,axis="both"
                                   ,direction="out"
                                   )
            
        if kwargs.get("tickinterval", None):
            tickinterval = kwargs.get("tickinterval", 100)
            
            # build ticks
            aticks = ["0m"]
            ticks  = [0]
            j = tickinterval
            while j <= distance_from_origin:
                aticks = [-j] + aticks + [j]
                ticks  = [-j] +  ticks + [j]
                j += tickinterval
            ticks = numpy.array(ticks)
            
            CS.ax.set_xticks(ticks)
            CS.ax.set_yticks(ticks)
            CS.ax.set_xticklabels(aticks, rotation=90)
            CS.ax.set_yticklabels(aticks)
        else:
            if self.DEBUG: print("DEBUG: ticklabels set")
            ax.ticklabel_format(axis="both"
                                ,style="plain"
                                ,useOffset=0
                                )
        # set tick interval
        ax.set_xlim(-distance_from_origin, distance_from_origin)
        ax.set_ylim(-distance_from_origin, distance_from_origin)
        
        # format tick marks
        ax.tick_params(axis="both"
                      ,direction="out"
                      ,length=0 if kwargs.get("noticks", False) else 4 # default tick length is 4. Can be omitted if requested using noticks option
                      ,color="grey"
                      ,width=1
                      ,pad=kwargs.get("labelgap",4)
                      ,labelsize=kwargs.get("labelsize", 10)
                      )
        
        # plot data points.
        if kwargs.get("receptor_size", 12):
            scat = ax.scatter(receptors.X - origin.X
                             ,receptors.Y - origin.Y
                             ,marker=kwargs.get("receptor_type", "o")
                             ,c=(1,1,1,0) # in place of marker_style which I can't get to work
                             ,s=kwargs.get("receptor_size", 12)
                             ,zorder=10
                             )
        if kwargs.get("max_plot", True):
            max_point = point(1
                             ,Xs=numpy.array([receptors.X[concs.argmax()] - origin.X])
                             ,Ys=numpy.array([receptors.Y[concs.argmax()] - origin.Y])
                             )
            if self.DEBUG: 
                print("DEBUG: max plot:")
                print("    X =", max_point.X[0])
                print("    Y =", max_point.Y[0])
                print("    c =", concs.max())
            ax.annotate('+ Maximum Concentration: '+ kwargs.get("scale_decimals","%0.0f") % concs.max()
                       ,(0.5, 0)
                       ,(0, -40 + (kwargs.get("max_textsize", 10)))
                       ,xycoords='axes fraction'
                       ,ha="center"
                       ,va="top"
                       ,textcoords='offset points'
                       ,size=kwargs.get("max_textsize", 10)
                       )
                
            ax.scatter(max_point.X
                      ,max_point.Y
                      ,marker="+"
                      ,c=(0,0,0) # in place of marker_style which I can't get to work
                      ,s=kwargs.get("max_plot", 50)
                      ,zorder=10
                      )
        if kwargs.get("add_background", False):
            ax.annotate('Includes background\nconcentration: '+ kwargs.get("scale_decimals","%0.0f") % kwargs.get("add_background", 0.0)
                       ,(1.05, 0)
                       ,(0, -32 + (kwargs.get("max_textsize", 10)))
                       ,xycoords='axes fraction'
                       ,ha="left"
                       ,va="top"
                       ,textcoords='offset points'
                       ,size=kwargs.get("max_textsize", 10)
                       )
            
        if kwargs.get("transparent_buildings", False):
            if self.DEBUG: print("DEBUG: transparent buildings")
            building_color = "#FFFFFF00"
        else:
            building_color = "white"
        if kwargs.get("buildings", False):
            for name, story in sorted(self.building_vertices.keys()):
                self.draw_building(name, story, ax, origin=origin
                                  ,color=kwargs.get("building_color", building_color)
                                  ,linewidth=kwargs.get("building_linewidth", 0.4)
                                  ,building_name=kwargs.get("building_name", False)
                                  )
        
        if kwargs.get("sources", False):
            for name, source in self.sources.items():
                if self.DEBUG: 
                    print("DEBUG: source:", name, source.X, source.Y)
                ax.scatter(source.X - origin.X
                          ,source.Y - origin.Y
                          ,marker="o"
                          ,c=(0,0,0) 
                          ,s=kwargs.get("sources", 10)
                          ,zorder=10
                          )
            if self.DEBUG: print("DEBUG: sources successfully plotted")
        
        ax.set_title(pollutant_dict[kwargs.get("pollutant", "PM2.5")][0] + " " + \
                     ("" if r_form is "CONCURRENT" else r_type )+ "\n" + \
                     ("%s HIGHEST " %(ordinal(rank)) if rank else "")  + \
                     ("HOURLY" if (r_form == "CONCURRENT") else r_form)
                    ,size=kwargs.get("title_size", 10)
                    ,loc="left"
                    ,ha="left"
                    ,position=(0.05,1.012)
                    )
        
        ax.set_title("SOURCE(S): \n"+source_group
                    ,size=kwargs.get("title_size", 10)
                    ,loc="right"
                    ,ha="left"
                    ,position=(0.75,1.012)
                    )
        
        plt.savefig(kwargs.get("filename", "aermod.png"))
        plt.close("all")
    
