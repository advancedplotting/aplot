# Copyright 2014-2026 open-source contributors
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
    This module provides the PlotContext object, in addition to the
    color cycle, the RESOURCES dictionary used for method dispatch,
    and a few other miscellaneous pieces.
    
    Crucially, it imports all of the api_* modules, which triggers
    population of RESOURCES.  Once this module is successfully imported,
    RESOURCES is ready to go.
    
    This is also the location where Matplotlib global settings are made.
    Matplotlib should not be imported before this module is loaded, or
    the settings will not be effective.
"""

import matplotlib as m
m.use('Agg')
m.rcParams['mathtext.fontset'] = 'stixsans'

from matplotlib import pyplot as plt
from matplotlib import colors as mcolors

from .import errors
    
RESOURCES = {}  # Dict mapping string resource names to callables


def resource(name):
    """ Decorator which binds a callable to the given resource name """
    
    def w(cls):
        RESOURCES[name] = cls
        return cls
        
    return w

def blend_color(color):

    alpha = 0.65
    rgb = mcolors.colorConverter.to_rgb(color)
    rgb = tuple((x*alpha + 1.0*(1 - alpha)) for x in rgb)
    return rgb
    
COLOR_CYCLE = ['b', 'g', 'r', 'c', 'm', 'y', '#444444', '#ff00ff']
COLOR_CYCLE_BAR = [blend_color(x) for x in COLOR_CYCLE]

class PlotContext(object):

    """
        Stateful context object for dealing with plots.
        
        Used in the api_* functions to set and get plot information, and
        to handle the color cycle.
    """
    
    def __init__(self):
        self._plots = set()         # All Plot IDs which are alive
        self._color_indexes = {}    # Dict mapping plot id -> color cycle position
        self._mappable = {}         # Dict mapping plot id -> bool if colormapped object present
        self._polar = {}            # Dict mapping plot id -> bool if polar axes
        self._plotid = None         # The active plot id
        self._xscales = {}          # Maps plot id -> scale mode string
        self._yscales = {}
        self._errorbar_colors = {}
        self._legend_entries = {}   # PlotID -> list of 2-tuples
        
    def set(self, plotid):
        """ Set "plotid" as the active plot. 
        
        Returns the MPL figure.
        """
        if not plotid in self._plots:
            raise errors.InvalidIdentifier("Plot ID 0x%X does not exist" % plotid)
        self._plotid = plotid
        return plt.figure(plotid)
        
    def new(self, plotid):
        """ Register a new figure with the context object.
        
        Also sets the current plot to plotid and returns the MPL figure.
        """
        if plotid in self._plots:
            raise ValueError("Plot ID %d already exists" % plotid)
        self._plots.add(plotid)
        
        return self.set(plotid)
        
    def close(self):
        """ Close a figure and forget the id """
        plotid = self._plotid
        f = self.set(plotid)
        plt.close(f)
        self._plotid = None
        self._plots.remove(plotid)
        self._color_indexes.pop(plotid, None)
        self._mappable.pop(plotid, None)
        self._polar.pop(plotid, None)
        self._xscales.pop(plotid, None)
        self._yscales.pop(plotid, None)
        self._errorbar_colors.pop(plotid, None)
        
    def isvalid(self, plotid):
        """ Determine if a plot identifier is valid """
        return plotid in self._plots

    @property
    def mappable(self):
        """ Mappable for which we should create the colorbar.  None means
        no mappable has been created yet."""
        return self._mappable.get(self._plotid, None)
        
    @mappable.setter
    def mappable(self, m):
        self._mappable[self._plotid] = m

    @property
    def polar(self):
        """ Bool determining if axes are polar """
        return self._polar[self._plotid]  # KeyError is desired, as all plots must have this property
        
    @polar.setter
    def polar(self, value):
        if self._plotid in self._polar:
            raise AttributeError("Attempt to set .polar property twice")
        else:
            self._polar[self._plotid] = value
            
    @property
    def xscale(self):
        """ Scale mode """
        return self._xscales.get(self._plotid)
        
    @xscale.setter
    def xscale(self, value):
        self._xscales[self._plotid] = value

    @property
    def yscale(self):
        """ Scale mode """
        return self._yscales.get(self._plotid)
        
    @yscale.setter
    def yscale(self, value):
        self._yscales[self._plotid] = value
        
    @property
    def legend_entries(self):
        """ Return the list of legend entries """
        return self._legend_entries.setdefault(self._plotid, [])
        
    def next_color(self, bar=False):
        """ Get a color, and advance the cycle.
        
        If *bar*, return a slightly less eye-piercing version.
        """
        idx = self._color_indexes.setdefault(self._plotid, 0)
        self._color_indexes[self._plotid] += 1
        if bar:
            return COLOR_CYCLE_BAR[idx%len(COLOR_CYCLE_BAR)]
        else:
            return COLOR_CYCLE[idx%len(COLOR_CYCLE)]
        
    def last_color(self):
        """ Get the last-used color (or the first in the cycle, if none 
        has been used) """
        idx = self._color_indexes.get(self._plotid)
        if idx is not None:
            return COLOR_CYCLE[(idx-1) % len(COLOR_CYCLE)]
        return COLOR_CYCLE[0]
        
    def errorbar_color(self, color=None):
        if color is not None:
            self._errorbar_colors[self._plotid] = color
        return self._errorbar_colors.get(self._plotid, self.last_color())
            
    def fail_if_polar(self):
        if self.polar:
            raise errors.PolarNotSupported("This VI does not support polar axes")

    def fail_if_symlog(self):
        if self.xscale == 'symlog' or self.yscale == 'symlog':
            raise errors.LogNotSupported("This VI does not support symlog axis scales")
                
    def fail_if_log_symlog(self):
        if self.xscale != 'linear' or self.yscale != 'linear':
            raise errors.LogNotSupported("This VI does not support log or symlog axis scales")
            

# Trigger population of RESOURCES
from . import api_core, api_figure, api_plotting, api_annotations
