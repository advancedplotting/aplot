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
    Python-side representation of VIs in api_figure.
"""

from matplotlib import pyplot as plt

from .terminals import remove_none
from .core import resource
from . import filters

@resource('limits')
def limits(ctx, a):
    """ Represents api_figure/Limits.vi. """
    
    plotid  = a.plotid()
    xmin    = a.float('xmin')
    xmax    = a.float('xmax')
    ymin    = a.float('ymin')
    ymax    = a.float('ymax')
        
    ctx.set(plotid)

    kx = {'xmin': xmin, 'xmax': xmax}
    ky = {'ymin': ymin, 'ymax': ymax}
    remove_none(kx)
    remove_none(ky)
    
    # Only invoke if the user actually specified a min or max
    if len(kx) != 0:
        ctx.fail_if_polar()
        plt.xlim(**kx)
    if len(ky) != 0:
        plt.ylim(**ky)
        

def scales(ctx, a, whichscale):
    """ Represents XScale and YScale """
    
    SCALES = {0: 'linear', 1: 'linear', 2: 'log', 3: 'symlog'}
        
    plotid      = a.plotid()
    scale      = a.enum('scale', SCALES)
    base       = a.float('base')
    linthresh  = a.float('linthresh')
    
    ctx.set(plotid)
    
    # Raises confusing errors deep inside matplotlib.
    # Our solution is to ignore invalid bases.
    if base is not None and base <= 1:
        base = None
    
    # Same here.
    if linthresh is not None and linthresh <= 0:
        linthresh = None

    if whichscale == 'x':
        k = {'basex': base, 'linthreshx': linthresh, 'nonposx': 'clip'}
        remove_none(k)
        plt.xscale(scale, **k)
    
    elif whichscale == 'y':
        k = {'basey': base, 'linthreshy': linthresh, 'nonposy': 'clip'}
        remove_none(k)
        plt.yscale(scale, **k)

@resource('xscale')
def xscale(ctx, a):
    return scales(ctx, a, 'x')
    
@resource('yscale')
def yscale(ctx, a):
    return scales(ctx, a, 'y')
    
    
@resource('size')  
def size(ctx, a):
    """ Represents api_figure/Size.vi. """
    
    plotid  = a.plotid()
    xsize   = a.float('xsize')
    ysize   = a.float('ysize')
    dpi     = a.float('dpi')
        
    f = ctx.set(plotid)
    
    oldxsize, oldysize = f.get_size_inches()
    olddpi = f.get_dpi()
    
    if dpi is None or dpi <= 10:
        dpi = olddpi
        
    # Convert to pixels and apply limit logic
    if xsize is None or xsize <= 1:
        xsize = oldxsize*olddpi
    if ysize is None or ysize <= 1:
        ysize = oldysize*olddpi

    f.set_dpi(dpi)
    f.set_size_inches(xsize/dpi, ysize/dpi)
       
       
@resource('ticks')
def ticks(ctx, a):
    """ Handles TicksPriv.vi """
    
    AXIS = {0: 'xaxis', 1: 'yaxis'}

    plotid      = a.plotid()
    axis        = a.enum('axis', AXIS)
    ticks       = a.dbl_1d('ticks')
    ticklabels  = a.string_1d('ticklabels')
    text        = a.text()

    ctx.set(plotid)
    ctx.fail_if_log_symlog()
    
    ax = plt.gca()
                
    if len(ticklabels) != 0:
        ticks, ticklabels = filters.filter_1d(ticks, ticklabels)
    else:
        ticks, = filters.filter_1d(ticks)
            
    if axis == 'xaxis':
    
        if len(ticks) != 0:
            ax.set_xticks(ticks)
            
            if len(ticklabels) != 0:
                ax.set_xticklabels(ticklabels)
            
        # Text keywords
        k = text._k()  
        for t in ax.get_xticklabels():
            t.set(**k)
            
    elif axis == 'yaxis':

        if len(ticks) != 0:
            ax.set_yticks(ticks)
            
            if len(ticklabels) != 0:
                ax.set_yticklabels(ticklabels)
            
        # Text keywords
        k = text._k()  
        for t in ax.get_yticklabels():
            t.set(**k)
        
        
@resource("grids")
def grids(ctx, a):
    """ Represents Grids.vi. """

    plotid  = a.plotid()
    x       = a.bool('x')
    y       = a.bool('y')
    line    = a.line()

    ctx.set(plotid)
    
    k = {   'color':        line.color,
            'linestyle':    line.style,
            'linewidth':    line.width, }
    remove_none(k)
        
    # If keywords are present, they force the grids on (MPL bug?)
    kx = k if x else {}
    ky = k if y else {}
    
    plt.grid(x, axis='x', **kx)
    plt.grid(y, axis='y', **ky)
