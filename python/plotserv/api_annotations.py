# Copyright (c) 2014-2015, Heliosphere Research LLC
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
    Handles VIs in "api_annotations".
"""

import numpy as np
from matplotlib import pyplot as plt

from .core import resource
from .terminals import remove_none
from . import filters
from . import errors

@resource('text')
def text(ctx, a):
    """ Display text on the plot """
    
    plotid      = a.plotid()
    x           = a.float('x')
    y           = a.float('y')
    s           = a.string('s')
    relative    = a.bool('coordinates')
    textprops   = a.text()
    display     = a.display()
    
    ctx.set(plotid)
    
    ax = plt.gca()
        
    # None-finite values here mean we skip the plot
    if x is None or y is None:
        return
            
    k = textprops._k()
    k.update(display._k())
    k['clip_on'] = True
    if relative:
        k['transform'] = ax.transAxes
    remove_none(k)

    plt.text(x, y, s, **k)

    
@resource('hline')
def hline(ctx, a):
    """ Plot a horizontal line """
    
    plotid  = a.plotid()
    y       = a.float('y')
    xmin    = a.float('xmin')
    xmax    = a.float('xmax')
    line    = a.line()
    display = a.display()
    
    ctx.set(plotid)
    ctx.fail_if_polar()

    # Non-finite value provided
    if y is None:
        return

    k = {   'xmin':     xmin, 
            'xmax':     xmax,
            'linewidth': line.width,
            'linestyle': line.style,
            'color':    line.color if line.color is not None else 'k', }
    k.update(display._k())
    remove_none(k)
    
    plt.axhline(y, **k)
    

@resource('vline')
def vline(ctx, a):
    """ Plot a vertical line """
    
    plotid  = a.plotid()
    x       = a.float('x')
    ymin    = a.float('ymin')
    ymax    = a.float('ymax')
    line    = a.line()
    display = a.display()

    ctx.set(plotid)
    ctx.fail_if_polar()

    # Non-finite value provided
    if x is None:
        return
        
    k = {   'ymin':     ymin, 
            'ymax':     ymax,
            'linewidth': line.width,
            'linestyle': line.style,
            'color':    line.color if line.color is not None else 'k', }
    k.update(display._k())
    remove_none(k)
    
    plt.axvline(x, **k)
    
    
@resource('colorbar')
def colorbar(ctx, a):
    """ Display a colorbar """
    
    plotid      = a.plotid()
    label       = a.string('label')
    ticks       = a.dbl_1d('ticks')
    ticklabels  = a.string_1d('ticklabels')
    
    ctx.set(plotid)
        
    # If no colormapped object has been plotted, MPL complains.
    # We permit this, and simply don't add the colorbar.
    if ctx.mappable is None:
        return
        
    c = plt.colorbar(ctx.mappable)
                
    # Don't bother setting an empty label
    if len(label) > 0:
        c.set_label(label)
    
    # Both specified
    if len(ticks) > 0 and len(ticklabels) > 0:
        ticks, ticklabels = filters.filter_1d(ticks, ticklabels)
        c.set_ticks(ticks)
        c.set_ticklabels(ticklabels)
        
    # Just ticks specified
    elif len(ticks) > 0:
        ticks = ticks[np.isfinite(ticks)]
        c.set_ticks(ticks)
        
    # Just ticklabels specified
    else:
        # Providing zero-length "ticks" array invokes auto-ticking, in which
        # case any ticklabels are ignored.
        pass

    
@resource('legend')
def legend(ctx, a):
    """ Represents Legend.vi.
    
    Note that there is no Positions enum on the Python side; the MPL
    values are hard-coded into the LabView control.
    """
    
    POSITIONS = { 0: 0,
                  1: 1,
                  2: 9,
                  3: 2,
                  4: 6,
                  5: 3,
                  6: 8,
                  7: 4,
                  8: 7,
                  9: 10 }
                  
    plotid      = a.plotid()
    position    = a.enum('position', POSITIONS)

    ctx.set(plotid)
    
    k = {'loc': position, 'fontsize': 'medium'}
    remove_none(k)
    
    if len(ctx.legend_entries) > 0:
        objects, labels = zip(*ctx.legend_entries)
        plt.legend(objects, labels, **k)
        

@resource('label')
def label(ctx, a):
    """ Title, X axis and Y axis labels. """
    
    LOCATIONS = {0: 'title', 1: 'xlabel', 2: 'ylabel'}

    plotid      = a.plotid()
    location    = a.enum('kind', LOCATIONS)
    label       = a.string('label')
    text        = a.text()
        
    ctx.set(plotid)
    
    k = text._k()
    
    if location == 'title':
        plt.title(label, **k)
        
    elif location == 'xlabel':
        plt.xlabel(label, **k)
        
    elif location == 'ylabel':
        ctx.fail_if_polar()
        plt.ylabel(label, **k)
            
    else:
        pass
        
    
@resource('circle')
def circle(ctx, a):
    """ Draw a circle on a rectangular plot """
    
    plotid  = a.plotid()
    x       = a.float('x')
    y       = a.float('y')
    radius  = a.float('radius')
    
    color   = a.color('color')
    line    = a.line()
    display = a.display()
    
    f = ctx.set(plotid)
    ctx.fail_if_polar()
    ctx.fail_if_log_symlog()
    
    # Like Text.vi, if any critical input is Nan we do nothing
    if x is None or y is None or radius is None:
        return
        
    # Catch this before MPL complains
    if radius <= 0:
        return
        
    k = {   'edgecolor':    line.color,
            'linestyle':    line.style,
            'linewidth':    line.width,
            'facecolor':    color if color is not None else '#bbbbbb', }
    k.update(display._k())
    remove_none(k)
    
    c = plt.Circle((x,y), radius, **k)
    
    f.gca().add_artist(c)
    
    
@resource('rectangle')
def rectangle(ctx, a):
    """ Draw a rectangle """
    
    plotid  = a.plotid()
    x       = a.float('x')
    y       = a.float('y')
    width   = a.float('width')
    height  = a.float('height')

    color   = a.color('color')
    line    = a.line()
    display = a.display()
    
    f = ctx.set(plotid)
    ctx.fail_if_symlog()

    # Like Text.vi, if any critical input is Nan we do nothing
    if x is None or y is None or width is None or height is None:
        return
        
    if width == 0 or height == 0:
        return

    k = {   'edgecolor':    line.color,
            'linestyle':    line.style,
            'linewidth':    line.width,
            'facecolor':    color if color is not None else '#bbbbbb', }
    k.update(display._k())
    remove_none(k)
    
    r = plt.Rectangle((x,y), width, height, **k)
    
    f.gca().add_artist(r)