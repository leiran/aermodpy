#!/usr/bin/env python
"""Python interface to AERMOD modeling system files."""

# docstring metadata
__author__ = "Leiran Biton"
__copyright__ = "Copyright 2015"
__credits__ = []
__license__ = "GPL"
__version__ = "0.03"
__maintainer__ = "Leiran Biton"
__email__ = "lbiton@nescaum.org"
__status__ = "Production"

# import statements
import os.path
import datetime
import calendar
import numpy

# color_dict contains a dictionary of levels
color_dicts = {
 "post" :    ((   0, "#FFFFFF", "    0")
             ,( 250, "#FFFF99", "")
             ,( 500,  "yellow", "")
             ,(1000, "#FFCC00", "1,000")
             ,(1500,  "orange", "")
             ,(2000,     "red", "2,000")
             ,(4000, "magenta", "4,000")
             ,(8000, "#993399", "8,000")
             )
,"grf"  :    ((  0, "#FFFFFF", "    0")
             ,( 25, "#FFFF99", "")
             ,( 50,  "yellow", "")
             ,(100, "#FFCC00", "100")
             ,(150,  "orange", "")
             ,(200,     "red", "200")
             ,(400, "magenta", "400")
             ,(800, "#993399", "800")
             )
,"24h-pm":   ((  0, "#FFFFFF", " 0")
             ,(  4, "#FFFF99", " 4")
             ,( 10,  "yellow", "10")
             ,( 20, "#FFCC00", "20")
             ,( 35,  "orange", "35")
             ,( 40,     "red", "40")
             ,( 50, "magenta", "50")
             ,( 60, "#993399", "60")
             )
,"24h-pm-fine":   (
              (  0, "#FFFFFF", " 0")
             ,(1.2, "#fbfdfe", " 1.2 (SIL)")
             ,(  4, "#f2f9fc", " 4 (SMC)")
             ,(  9, "#eaf5fb", " 9 (increment)")
             ,( 10, "#fefebe", "")
             ,( 15, "#FDFD96", "15")
             ,( 20, "#FFFF00", "20")
             ,( 25, "#FFF700", "25")
             ,( 30, "#FFEF00", "30")
             ,( 35, "#FFB347", "35 (NAAQS)")
             ,( 40, "#FFA812", "40")
             ,( 45, "#FF7F00", "45")
             ,( 50, "#FF6700", "50")
             ,( 55, "#CC5500", "55")
             ,( 60, "red", "60")
             )
,"annual-pm-fine":   (
              (  0, "#FFFFFF", " ")
             ,(0.3, "#fbfdfe", " 0.3 (SIL)")
             ,(  2, "#f2f9fc", " 2")
             ,(  4, "#eaf5fb", " 4 (increment)")
             ,(  6, "#fefebe", " 6")
             ,(  8, "#FDFD96", " 8")
             ,( 10, "#FFF700", "10")
             ,( 12, "#FFA812", "12 (NAAQS)")
             ,( 14, "#FF8C00", "14")
             ,( 16, "#FF6700", "16")
             ,( 18, "red", "18")
             ,( 20, "#CE1620", "20")
             ,( 22, "#B31B1B", "22")
             )
              }

pollutant_dict = {"PM2.5" : (r'$\mathregular{PM_{2.5}}$', r'$\mu\mathregular{g/m^3}$')
                 ,"CO"    : ("Carbon Monoxide", "ppm")
                 }

vars_indices = {
    
    "post" : 
           {"x"    : {"start":  0, "end": 14, "type": float}
           ,"y"    : {"start": 15, "end": 28, "type": float}
           ,"conc" : {"start": 29, "end": 42, "type": float}
           ,"z"    : {"start": 43, "end": 51, "type": float}
           ,"zhill": {"start": 52, "end": 60, "type": float}
           ,"zflag": {"start": 61, "end": 69, "type": float}
           ,"ave"  : {"start": 70, "end": 77, "type": str  }
           ,"group": {"start": 78, "end": 87, "type": str  }
           ,"netid": {"start": 98, "end":107, "type": str  }
           ,"year" : {"start": 89, "end": 91, "type": int  }
           ,"month": {"start": 91, "end": 93, "type": int  }
           ,"day"  : {"start": 93, "end": 95, "type": int  }
           ,"hour" : {"start": 95, "end": 97, "type": int  }
           }
   ,"grf"  : 
           {"x"    : {"start":  0, "end": 14, "type": float}
           ,"y"    : {"start": 15, "end": 28, "type": float}
           ,"conc" : {"start": 29, "end": 42, "type": float}
           ,"z"    : {"start": 43, "end": 51, "type": float}
           ,"zhill": {"start": 52, "end": 60, "type": float}
           ,"zflag": {"start": 61, "end": 69, "type": float}
           ,"ave"  : {"start": 70, "end": 77, "type": str  }
           ,"group": {"start": 78, "end": 87, "type": str  }
           ,"n_yrs": {"start": 88, "end": 97, "type": int  }
           ,"netid": {"start": 98, "end":107, "type": str  }
           }

               }


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
        print "WARNING: placeholder 'decode_format_datastring' called. this method is still in development."
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
        
        if self.verbose: print "--> opening building data file"
        self.building_file = self.openfile(filename, directory, "rU")
        
        # throw away header data
        [self.building_file.next() for header in range(2)]
        
        units, unit_value = self.building_file.next().split()
        if self.DEBUG: print "DEBUG: units / unit_value:", units, unit_value
        
        utmy, trash = self.building_file.next().split()
        num_bldgs = int(self.building_file.next())
        if self.DEBUG: print "DEBUG: number of buildings:", num_bldgs
        
        for building in range(num_bldgs):
            try:
                name, stories, elev = self.building_header()
                self.process_building(name, stories, elev)
            except:
                raise
        if not nosources:
            num_srcs = int(self.building_file.next())
            for src in range(num_srcs):
                try:
                    name, trash, elev, height, x, y = self.building_file.next().split()
                    name = name.strip().replace("'","")
                    if self.DEBUG: print "DEBUG: source name:", name, x, y
                    self.sources[(name)] = \
                        point(1, Xs=numpy.array(float(x))
                               , Ys=numpy.array(float(y))
                               )
                    if self.DEBUG: print "DEBUG: source:", self.sources[(name)].X, self.sources[(name)].Y
                except:
                    raise
    
    def building_header(self):
        """get building data for new building"""
        name_padded, stories, base_elevation = self.building_file.next().split()
        return name_padded.replace("'",""), int(stories), float(base_elevation)
    
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
        vertices, height = self.building_file.next().split()
        vertices = int(vertices)
        height   = float(height)
        vs = numpy.array([(float(X), float(Y)) for (X, Y) in \
                         [self.building_file.next().split() for v in range(vertices)] \
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
        
        if self.verbose: print "Opening file:", filepath
        if self.verbose: print "                 mode =", mode
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
            ] = [self.POSTfile.next() for i in range(6)]
            
        except:
            raise Exception("POST file does not contain proper header metadata")
        
        # extract format string from data format documentation
        if self.DEBUG: print "DEBUG: filetype_doc =", filetype_doc
        if self.DEBUG: print "DEBUG: dataformat_doc =", dataformat_doc
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
            if self.DEBUG: print "DEBUG:", r_type, r_form, source_group
            self.datatypes.append((r_type, r_form, source_group))
            self.POSTdata[(r_type, r_form, source_group)] = numpy.empty([self.receptors.num, 1])
        
        if len(self.modeldoc) == 1:
            n_receptors = [int(s) for s in receptors_doc.split() if s.isdigit()][0]
            self.receptors = point(n_receptors)
        
    def getPOSTfileHeader(self):
        """Get metadata from POSTfile"""
        self.fileheader = self.POSTfile.next().strip()
        self.POSTfile.next() # -------- line
        
    def printResults(self, filename, r_type, **kwargs):
        """print r_type results data array to outfile as comma separated values"""
        outfile = self.openfile(filename, directory=kwargs.get("directory", "."), mode="w")
        self.POSTdata[(r_type, r_form, source_group)].tofile(outfile, sep=",")
        outfile.close()
        
    def scalePOSTdata(self, r_type, **kwargs):
        """scales POSTdata result_type using optional "scalar" keyword argument. if omitted, 1.0."""
        if self.DEBUG: print "DEBUG: scaling %s results by" % r_type, kwargs.get("scalar", 1.0)
        self.POSTdata[(r_type, r_form, source_group)] *= kwargs.get("scalar", 1.0)
        
    def processPOSTData(self
                       ):
        """Process stored POST file data"""
        if self.verbose: print "--> processing open data file"
        
        while True:
            try:
                self.getPOSTfileMetaData()
                self.getPOSTfileHeader()
                self.getPOSTfileData()
            except:
                break
        
    
    def getPOSTfileData(self
                       ,h=0
                       ):
        """Get data from POSTfile, process for average number of hours"""
        if self.verbose: print "--> retrieving data"
        if self.DEBUG: print "DEBUG:", self.receptors.num, "receptors" 
        
        for r in range(self.receptors.num):
            line = self.POSTfile.next()
            if r == 0:
                if self.DEBUG: print "DEBUG: receptor 0 for hour", h
                if h == 0:
                    self.POSTdata[self.datatypes[-1]] = numpy.empty([self.receptors.num, 1])
                    if self.DEBUG: print "DEBUG: array successfully created at hour", h
                else:
                    self.POSTdata[self.datatypes[-1]] = \
                        numpy.append(self.POSTdata[self.datatypes[-1]]
                                    ,numpy.empty([self.receptors.num, 1])
                                    ,axis=1
                                    )
                    if self.DEBUG: print "DEBUG: array successfully expanded at hour", h
            
            # decode data
            data4hour, dt = self.decode_data(line)
            
            # build datetime list
            if r == 0:
                self.datetimes.append(dt)
                if self.DEBUG: print "DEBUG:", "processing for", dt
            
            # populate receptor location values
            if h == 0:
                self.receptors.X[r] = data4hour[0]
                self.receptors.Y[r] = data4hour[1]
                self.receptors.Z[r] = data4hour[2]
            
            self.POSTdata[self.datatypes[-1]][r,-1] = data4hour[3]
            
            if "hour" in self.vars_index and (r+1 == self.receptors.num): 
                try: 
                    self.getPOSTfileData(h+1)
                except:
                    return
    
    def draw_building(self
                     ,building
                     ,story
                     ,plot
                     ,origin=point(1,Xs=[0],Ys=[0])
                     ,**kwargs
                     ):
        """method for drawing buildings"""
        plot.fill(self.building_vertices[(building, story)].X - origin.X
                 ,self.building_vertices[(building, story)].Y - origin.Y
                 ,color=kwargs.get("color", "white")
                 ,linewidth=kwargs.get("linewidth", 0.4)
                 ,alpha=kwargs.get("alpha", 1.00)
                 ,ec="black"
                 )
    
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
        """
        import matplotlib
        import matplotlib.ticker
        import matplotlib.pyplot as plt
        from scipy.interpolate import griddata
        
        if kwargs.get("exclude_flagpole_receptors", False):
            if self.DEBUG: print "DEBUG: removing flagpole receptors"
            receptor_array = numpy.column_stack((self.receptors.X[self.receptors.Z==0]
                                               ,self.receptors.Y[self.receptors.Z==0]
                                               ,self.receptors.Z[self.receptors.Z==0]))
        else:
            receptor_array = numpy.column_stack((self.receptors.X, self.receptors.Y, self.receptors.Z))
        
        receptor_num = len(receptor_array)
        receptors = point(receptor_num
                         ,XYZs=receptor_array)
        
        if kwargs.get("exclude_flagpole_receptors", False):
            if self.DEBUG: print "DEBUG: removing flagplot data"
            concs = self.POSTdata[(r_type, r_form, source_group)][:,kwargs.get("slice", 0)][self.receptors.Z==0] * kwargs.get("scalar", 1.0) + kwargs.get("add_background", 0.0)
        else:
            concs = self.POSTdata[(r_type, r_form, source_group)][:,kwargs.get("slice", 0)] * kwargs.get("scalar", 1.0) + kwargs.get("add_background", 0.0)
        
        # define grid.
        
        x_range = receptors.X.max() - receptors.X.min()
        y_range = receptors.Y.max() - receptors.Y.min()
        xi = numpy.linspace(receptors.X.min(), receptors.X.max(), round(receptors.num**0.85))
        yi = numpy.linspace(receptors.Y.min(), receptors.Y.max(), round(receptors.num**0.85))
        
        if kwargs.get("colorslevels", None):
            levels = [level for level, color, label in kwargs["colorslevels"]]
            kwargs["levels"] = levels
            kwargs["contour_colors"] = [color for level, color, label in kwargs["colorslevels"]]
        
        distance_from_origin = kwargs.get("distance_from_origin", max(x_range/2, y_range/2))
        if self.DEBUG: print "DEBUG: distance_from_origin -", distance_from_origin
        
        origin = point(1)
        origin.X = (receptors.X.max() + receptors.X.min())/2
        origin.Y = (receptors.Y.max() + receptors.Y.min())/2
        
        # instantiate figure
        if kwargs.get("nocolorbar", False):
            plt.figure(num=None, figsize=(6.5, 6), dpi=80, facecolor='w', edgecolor='k')
        else:
            plt.figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
        
        # grid the data.
        
        zi = griddata((receptors.X - origin.X, receptors.Y - origin.Y)
                     ,concs
                     ,(xi[None,:] - origin.X, yi[:,None] - origin.Y)
                     ,method=kwargs.get("interpolation_method", "linear")
                     )
        
        if kwargs.get("contours", 0):
            CS = plt.contour(xi - origin.X, yi - origin.Y, zi
                            ,len(levels)+1
                            ,linewidths=float(kwargs.get("contours", 0))
                            ,colors='black'
                            ,levels=levels
                            )
        if kwargs.get("contour_colors", None):
            CS = plt.contourf(xi - origin.X, yi - origin.Y, zi
                             ,len(levels)+1
                             ,colors=kwargs["contour_colors"]
                             ,levels=levels)
        else:
            CS = plt.contourf(xi - origin.X, yi - origin.Y, zi
                             ,len(levels)+1
                             ,cmap=plt.cm.hot_r
                             ,levels=levels)
        CS.ax.set_aspect(1)
        
        if "hour" in self.vars_index:
            plt.text(1.0
                    ,1.012
                    ,self.datetimes[kwargs.get("slice", 0)].strftime("%Y-%m-%d %H:00")
                    ,horizontalalignment='right'
                    ,verticalalignment='bottom'
                    ,transform=CS.ax.transAxes
                    ,fontsize=kwargs.get("labelsize", 10)
                    ,color="#333333"
                    )
        
        
        if not kwargs.get("nocolorbar", False):
            matplotlib.rcParams['xtick.direction'] = 'out'
            matplotlib.rcParams['ytick.direction'] = 'out'
            colorbar = plt.colorbar(format=kwargs.get("scale_decimals", "%0.1f")
                                   ,spacing=kwargs.get("colorbar_spacing", "proportional")
                                   ,ticks=levels
                                   )
            
            colorbar.ax.tick_params(labelsize=kwargs.get("labelsize", 10))
            
            if kwargs.get("colorslevels", False):
                if self.DEBUG: print "DEBUG: setting colorbar labels"
                labels = [label for level, color, label in kwargs.get("colorslevels", False)]
                if kwargs.get("pollutant", None):
                    labels[-1] += " " + pollutant_dict[kwargs["pollutant"]][1]
                colorbar.set_ticklabels(labels)
            
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
            if self.DEBUG: print "DEBUG: ticklabels set"
            plt.ticklabel_format(axis="both"
                                ,style="plain"
                                ,useOffset=0
                                )
        # set tick interval
        plt.xlim(-distance_from_origin, distance_from_origin)
        plt.ylim(-distance_from_origin, distance_from_origin)
        
        # format tick marks
        plt.tick_params(direction="out"
                       ,length=4
                       ,color="grey"
                       ,width=1
                       ,pad=kwargs.get("labelgap",4)
                       ,labelsize=kwargs.get("labelsize", 10)
                       )
        
        # remove tick marks
        if kwargs.get("noticks", False):
            plt.xticks([])
            plt.yticks([])
        
        # plot data points.
        if kwargs.get("receptor_size", 12):
            scat = plt.scatter(receptors.X - origin.X
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
                print "DEBUG: max plot:"
                print "    X =", max_point.X[0]
                print "    Y =", max_point.Y[0]
                print "    c =", concs.max()
            plt.annotate('+ Maximum Concentration: '+ kwargs.get("scale_decimals","%0.0f") % concs.max()
                        ,(0.5, 0)
                        ,(0, -40 + (kwargs.get("max_textsize", 10)))
                        ,xycoords='axes fraction'
                        ,ha="center"
                        ,va="top"
                        ,textcoords='offset points'
                        ,size=kwargs.get("max_textsize", 10)
                        )
                
            plt.scatter(max_point.X
                       ,max_point.Y
                       ,marker="+"
                       ,c=(0,0,0) # in place of marker_style which I can't get to work
                       ,s=kwargs.get("max_plot", 50)
                       ,zorder=10
                       )
        if kwargs.get("add_background", False):
            plt.annotate('Includes background\nconcentration: '+ kwargs.get("scale_decimals","%0.0f") % kwargs.get("add_background", 0.0)
                        ,(1.05, 0)
                        ,(0, -32 + (kwargs.get("max_textsize", 10)))
                        ,xycoords='axes fraction'
                        ,ha="left"
                        ,va="top"
                        ,textcoords='offset points'
                        ,size=kwargs.get("max_textsize", 10)
                        )
            
        if kwargs.get("transparent_buildings", False):
            if self.DEBUG: print "DEBUG: transparent buildings"
            building_color = "#FFFFFF00"
        else:
            building_color = "white"
        if kwargs.get("buildings", False):
            for name, story in sorted(self.building_vertices.keys()):
                self.draw_building(name, story, plt, origin=origin
                                  ,color=kwargs.get("building_color", building_color)
                                  ,linewidth=kwargs.get("building_linewidth", 0.4)
                                  )
        
            if kwargs.get("sources", False):
                for name, source in self.sources.items():
                    if self.DEBUG: 
                        print "DEBUG: source:", name, source.X, source.Y
                        plt.scatter(source.X - origin.X
                                   ,source.Y - origin.Y
                                   ,marker="o"
                                   ,c=(0,0,0) 
                                   ,s=kwargs.get("sources", 10)
                                   ,zorder=10
                                   )
        
        plt.title(pollutant_dict[kwargs.get("pollutant", "PM2.5")][0] + " " + \
                  ("" if r_form is "CONCURRENT" else r_type )+ "\n" + \
                  ("HOURLY" if r_form is "CONCURRENT" else r_form)
                 ,size=kwargs.get("title_size", 10)
                 ,ha="left"
                 ,position=(0.05,1.012)
                 )
        plt.figtext(0.6,0.95
                 ,"SOURCE(S): "+source_group
                 ,size=kwargs.get("title_size", 10)
                 ,ha="left"
                 )
        
        plt.savefig(kwargs.get("filename", "aermod.png"))
        plt.close("all")
    
