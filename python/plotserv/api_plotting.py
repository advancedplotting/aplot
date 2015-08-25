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
    Handles VIs in "plotting".
"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import ticker

from .terminals import remove_none
from .core import resource
from . import filters, errors

@resource('tiles')
def tiles(ctx, a):
    """ Represents Tiles.vi """
    
    plotid  = a.plotid()
    z       = a.dbl_2d('z')
    x       = a.dbl_1d('x')
    y       = a.dbl_1d('y')
    cmap    = a.colormap()
    line    = a.line()
    display = a.display()
    
    ctx.set(plotid)
    ctx.fail_if_polar()

    # No data, no plot
    if len(z) == 0:
        return
        
    # Determine if default x/y are to be used
    if len(x) < 2 or np.any(~np.isfinite(x)):
        x = np.arange(z.shape[1]+1)
    if len(y) < 2 or np.any(~np.isfinite(y)):
        y = np.arange(z.shape[0]+1)
        
    # NaNs break the entire plot
    if np.any(~np.isfinite(z)):
        z = np.ma.masked_invalid(z)

    # MPL has crazy defaults; fix them
    if line.style is not None and line.color is None:
        line.color = 'k'
    if line.width is not None and (line.style is None and line.color is None):
        line.color = 'k'
    
    k = {   'cmap': cmap.map,
            'norm': cmap._norm(),
            'edgecolor': line.color,
            'linestyle': line.style,
            'linewidth': line.width, 
            'antialiased': (display.alpha is not None and display.alpha < 1)}
    k.update(display._k())
    remove_none(k)
    
    out = plt.pcolormesh(x, y, z, **k)
    
    ctx.mappable = out
    

@resource('bar')
def bar(ctx, a):
    """ Represents Bar.vi. """

    plotid  = a.plotid()    
    x       = a.dbl_1d('x')
    height  = a.dbl_1d('height')
    width   = a.dbl_1d('width')
    bottom  = a.dbl_1d('bottom')
    legend  = a.string('legend')
    
    color   = a.color('color')
    line    = a.line()
    display = a.display()
    
    ctx.set(plotid)
    
    # Do this first, so we still advance the color cycle if bailing out
    if color is None:
        color = ctx.next_color(bar=True)
    ctx.errorbar_color(color)

    # Apply defaults for optional args
    if len(x) == 0:
        x = np.arange(len(height))
    if len(width) == 0:
        width = np.ones(len(height))*0.8
    if len(bottom) == 0:
        bottom = np.zeros(len(height))
        
    # Docs say negative widths are permitted
    width = np.abs(width)
    
    # Hack to completely remove width-0 bars; MPL plots a weird artifact
    width[width==0] = np.nan
    
    # Make all same size and remove NaNs    
    x, height, bottom, width = filters.filter_1d(x, height, bottom, width)

    # All the data got filtered out, or height was empty to start with
    if len(height) == 0:
        return
        
    k = {   'align':        'center',
            'width':        width,
            'bottom':       bottom,
            'color':        color,
            'linewidth':    line.width,
            'edgecolor':    line.color,
            'linestyle':    line.style,
            'alpha':        display.alpha,
            'zorder':       display.zorder,
            'log':          ctx.yscale == 'log'}
    remove_none(k)
            
    out = plt.bar(x, height, **k)

    if len(legend) != 0:
        ctx.legend_entries.append((out, legend))


@resource('contour_auto')
def contour_auto(ctx, a):
    """ Represents Contour_Automatic.vi (line contours). """
    
    plotid      = a.plotid()
    z           = a.dbl_2d('z')
    x           = a.dbl_1d('x')
    y           = a.dbl_1d('y')
    levels      = a.int('n')

    contour_min = a.float('levelmin')
    contour_max = a.float('levelmax')
    
    label       = a.bool('label')
    line        = a.line()
    display     = a.display()

    ctx.set(plotid)
    ctx.fail_if_polar()
    ctx.fail_if_log_symlog()

    # Apply defaults for optional args
    if len(x) == 0:
        x = np.arange(z.shape[1])
    if len(y) == 0:
        y = np.arange(z.shape[0])
        
    # Make all the same size, and filter out rows/cols corresponding to NaN
    x, y, z = filters.filter_2d(x, y, z)
    
    # Can't contour datasets which end up smaller than 2x2
    if z.shape[0] < 2 or z.shape[1] < 2:
        return
        
    # MPL pitches a fit if any elements are NaN, so use a masked array
    if np.any(~np.isfinite(z)):
        z = np.ma.masked_invalid(z)

    if levels < 0:
        levels = 10
        
    elif levels > 500:
        # MPL raises an exception for too many levels
        levels = 500

    elif levels == 0:
        # MPL also doesn't like levels == 0, so bail out instead
        return
        
    # Note we do this after checking len(z) != 0, or min/max raise an exception
    if contour_min is None: 
        contour_min = z.min()
    if contour_max is None: 
        contour_max = z.max()

    # Bail out if contour ranges reversed (by definition nothing can be plotted)
    if contour_max < contour_min:
        return

    # For this next bit see also Matplotlib ContourSet._autolev
    
    locator = ticker.MaxNLocator(levels + 1)
    levels = locator.tick_values(contour_min, contour_max)
    levels = levels[(levels > contour_min) & (levels < contour_max)]
    
    # Note we handle line props manually, as contour uses non-standard
    # naming for the keyword arguments.
    k = {   'colors':       'k' if line.color is None else line.color,
            'linestyles':   line.style,
            'linewidths':   line.width, }
    k.update(display._k())
    remove_none(k)

    contourset = plt.contour(x, y, z, levels, **k)
    
    if label:
        plt.clabel(contourset)


@resource('contour_manual')
def contour_manual(ctx, a):
    """ Represents Contour_Manual.vi (line contours). """
    
    plotid      = a.plotid()
    z           = a.dbl_2d('z')
    x           = a.dbl_1d('x')
    y           = a.dbl_1d('y')
    levels      = a.dbl_1d('levels')

    label       = a.bool('label')
    line        = a.line()
    display     = a.display()

    ctx.set(plotid)
    ctx.fail_if_polar()
    ctx.fail_if_log_symlog()

    # Apply defaults for optional args
    if len(x) == 0:
        x = np.arange(z.shape[1])
    if len(y) == 0:
        y = np.arange(z.shape[0])
        
    # Make all the same size, and filter out rows/cols corresponding to NaN
    x, y, z = filters.filter_2d(x, y, z)
    
    # Can't contour datasets which end up smaller than 2x2
    if z.shape[0] < 2 or z.shape[1] < 2:
        return
        
    # MPL pitches a fit if any elements are NaN, so use a masked array
    if np.any(~np.isfinite(z)):
        z = np.ma.masked_invalid(z)

    # MPL doesn't like this
    if len(levels) == 0:
        return

    # Limit to 500 to avoid "MAXTICKS" issue
    levels = levels[0:500]

    # Note we handle line props manually, as contour uses non-standard
    # naming for the keyword arguments.
    k = {   'colors':       'k' if line.color is None else line.color,
            'linestyles':   line.style,
            'linewidths':   line.width, }
    k.update(display._k())
    remove_none(k)

    contourset = plt.contour(x, y, z, levels, **k)
    
    if label:
        plt.clabel(contourset)
        

@resource('contourf_auto')
def contourf_auto(ctx, a):
    """ Represents ContourFilled.vi (line contours). """
    
    plotid      = a.plotid()
    z           = a.dbl_2d('z')
    x           = a.dbl_1d('x')
    y           = a.dbl_1d('y')
    levels      = a.int('n')

    contour_min = a.float('levelmin')
    contour_max = a.float('levelmax')
    
    display     = a.display()
    cmap        = a.colormap()

    ctx.set(plotid)
    ctx.fail_if_polar()
    ctx.fail_if_log_symlog()

    # Apply defaults for optional args
    if len(x) == 0:
        x = np.arange(z.shape[1])
    if len(y) == 0:
        y = np.arange(z.shape[0])
        
    # Make all the same size, and filter out rows/cols corresponding to NaN
    x, y, z = filters.filter_2d(x, y, z)
    
    # Can't contour datasets which end up smaller than 2x2
    if z.shape[0] < 2 or z.shape[1] < 2:
        return

    # MPL pitches a fit if any elements are NaN, so use a masked array
    if np.any(~np.isfinite(z)):
        z = np.ma.masked_invalid(z)
        
    if levels < 0:
        levels = 10
        
    elif levels > 500:
        # MPL raises an exception if levels > 500
        levels = 500
        
    elif levels == 0:
        # Reject to match behavior of Contour.vi
        return
        
    # Note we do this after checking len(z) != 0, or min/max raise an exception
    if contour_min is None: 
        contour_min = z.min()
    if contour_max is None: 
        contour_max = z.max()

    locator = ticker.MaxNLocator(levels + 1)
    levels = locator.tick_values(contour_min, contour_max)
    
    k = {   'cmap':     cmap.map,
            'norm':     cmap._norm(), 
            'antialiased': True}
    k.update(display._k())
    remove_none(k)
    
    # Plot colored contours just behind the filled contours to fill in the
    # white lines.
    if display.alpha is None or display.alpha == 1:
        k2 = k.copy()
        k2['zorder'] = (1 if display.zorder is None else display.zorder) - 0.01
        k2['linewidths'] = 2
        plt.contour(x, y, z, levels, **k2)
        
    out = plt.contourf(x, y, z, levels, **k)
    
    # So that Colorbar.vi will work
    ctx.mappable = out


@resource('contourf_manual')
def contourf_manual(ctx, a):
    """ Represents ContourFilled_Manual.vi (line contours). """
    
    plotid      = a.plotid()
    z           = a.dbl_2d('z')
    x           = a.dbl_1d('x')
    y           = a.dbl_1d('y')
    levels      = a.dbl_1d('levels')

    display     = a.display()
    cmap        = a.colormap()

    ctx.set(plotid)
    ctx.fail_if_polar()
    ctx.fail_if_log_symlog()
    
    # Apply defaults for optional args
    if len(x) == 0:
        x = np.arange(z.shape[1])
    if len(y) == 0:
        y = np.arange(z.shape[0])
        
    # Make all the same size, and filter out rows/cols corresponding to NaN
    x, y, z = filters.filter_2d(x, y, z)
    
    # Can't contour datasets which end up smaller than 2x2
    if z.shape[0] < 2 or z.shape[1] < 2:
        return

    # MPL pitches a fit if any elements are NaN, so use a masked array
    if np.any(~np.isfinite(z)):
        z = np.ma.masked_invalid(z)

    # Remove NaNs and Infs, sort, and remove duplicates
    levels = levels[np.isfinite(levels)]
    levels = np.unique(levels)
    
    # Avoid MAXTICKS issue
    levels = levels[0:500]
    
    # MPL can't handle a zero-length levels array
    if len(levels) == 0:
        return

    # With explicit limits, MPL does not add implicit min() and max()
    mn = z.min()
    mx = z.max()
    
    if len(levels) == 0 or mn == mx:
        levels = 0  # This is the only way to get MPL to behave consistently
        
    else:
        if mn < levels.min():   # Add implicit lower bound
            levels = np.hstack(([mn], levels))
        if mx > levels.max():   # Add implicit upper bound
            levels = np.hstack((levels, [mx]))
    
    k = {   'cmap':     cmap.map,
            'norm':     cmap._norm(), 
            'antialiased': True}
    k.update(display._k())
    remove_none(k)
    
    # Plot colored contours just behind the filled contours to fill in the
    # white lines.
    if display.alpha is None or display.alpha == 1:
        k2 = k.copy()
        k2['zorder'] = (1 if display.zorder is None else display.zorder) - 0.01
        k2['linewidths'] = 1
        plt.contour(x, y, z, levels, **k2)

    out = plt.contourf(x, y, z, levels, **k)

    # So that Colorbar.vi will work
    ctx.mappable = out
    
    

@resource('line')
def line(ctx, a):
    """ Represents Line.vi. """
        
    plotid  = a.plotid()
    y       = a.dbl_1d('y')
    x       = a.dbl_1d('x')
    legend  = a.string('legend')
    
    line    = a.line()
    marker  = a.marker()
    display = a.display()
    
    ctx.set(plotid)

    # Use color cycle if no explicit color.
    # Do this first, in case we bail out early with len(y) == 0
    if line.color is None:
        color = ctx.next_color()
    else:
        color = line.color
    ctx.errorbar_color(color)

    # Apply defaults for optional args
    if len(x) == 0:
        x = np.arange(len(y))
    
    # Filter out NaNs, make same size
    x, y = filters.filter_1d(x, y)
    
    # All filtered out, or len(y) == 0 to start with
    if len(y) == 0:
        return
        
    k = {   'linestyle':    line.style,
            'linewidth':    line.width,
            'color':        color,
            'marker':       marker.style,
            'markerfacecolor': marker.color,
            'markersize':   marker.size, }
    k.update(display._k())
    remove_none(k)

    out = plt.plot(x, y, **k)

    if len(legend) != 0:
        ctx.legend_entries.append((out[0], legend))


@resource('scatter')
def scatter(ctx, a):
        
    plotid  = a.plotid()
    x       = a.dbl_1d('x')
    y       = a.dbl_1d('y')
    s       = a.dbl_1d('s')  # Marker size array
    c       = a.dbl_1d('c')  # Value array for colormap
    legend  = a.string('legend')

    marker  = a.marker()
    line    = a.line()
    cmap    = a.colormap()
    display = a.display()
    
    ctx.set(plotid)

    # Color priority: (1) explicit marker color, (2) color array, (3) cycle
    # Do this early so the color cycle is advanced even if we bail out
    if marker.color is not None:
        color = marker.color
    elif len(c) != 0:
        color = c
    else:
        color = ctx.next_color()
    if not isinstance(color, np.ndarray):
        ctx.errorbar_color(color)

    # Apply defaults for optional args
    if len(s) == 0:
        s = np.ones(len(y))*20

    # Make all the same size, and remove non-finite entries
    if isinstance(color, np.ndarray):
        x, y, s, color = filters.filter_1d(x, y, s, color)
    else:
        x, y, s = filters.filter_1d(x, y, s)
        
    # All filtered, or x/y had zero length to start with
    if len(x) == 0:
        return
        
    # Docs say negative sizes are clipped to 0
    s[s<0] = 0
                
    # Prefer explicitly specified marker size if given
    if marker.size is not None:
        sizes = marker.size**2   # MPL expects the "s" argument in pt^2
    else:
        sizes = s
        
    # By default we don't show the outlines
    if line.style is None and line.width is None and line.color is None:
        line.width = 0
        
    k = {   's':            sizes,
            'c':            color,
            'marker':       marker.style,
            'cmap':         cmap.map,
            'norm':         cmap._norm(),
            'linestyles':   line.style,
            'linewidths':   line.width,
            'edgecolors':   line.color, }
    k.update(display._k())
    remove_none(k)
        
    obj = plt.scatter(x, y, **k)
    
    if isinstance(color, np.ndarray):
        ctx.mappable = obj

    if len(legend) != 0:
        ctx.legend_entries.append((obj, legend))
        

@resource('vectorfield')
def vectorfield(ctx, a):
    """ Represents VectorField.vi. """

    plotid = a.plotid()
    
    x       = a.dbl_1d('x')     # X loc of arrows
    y       = a.dbl_1d('y')     # Y loc of arrows
    u       = a.dbl_2d('u')     # Arrow X component
    v       = a.dbl_2d('v')     # Arrow Y component
    c       = a.dbl_2d('c')     # Vals for colormap

    color   = a.color('color')  # Explicit arrow color
    scale   = a.float('scale')  # Scale factor
    cmap    = a.colormap()
    display = a.display()
        
    ctx.set(plotid)
    ctx.fail_if_polar()
    ctx.fail_if_log_symlog()
    
    # Ensure X/Y are populated before filtering
    if len(x) == 0:
        x = np.arange(u.shape[1])
    if len(y) == 0:
        y = np.arange(u.shape[0])
        
    # Make sizes of the arrays consistent, while removing NaNs from X/Y
    # and from the corresponding 2D array locations
    if len(c) == 0:
        x, y, u, v = filters.filter_2d(x, y, u, v)
    else:
        x, y, u, v, c = filters.filter_2d(x, y, u, v, c)
        
    # Either we had no data to begin with, or it was all filtered out
    if len(u) == 0:
        return
        
    # Invalid scale values are ignored
    if scale is not None and scale <= 0:
        scale = None
        
    # Use 2D colormap values only if they're provided, and an explicit
    # color is not available.
    if len(c) != 0 and color is None:
        args = (x, y, u, v, c)
    else:
        args = (x, y, u, v)
        
    k = {   'color':    color,
            'units':    'dots',
            'scale':    scale,
            'pivot':    'tail',
            'cmap':     cmap.map,
            'norm':     cmap._norm(),
            'alpha':    display.alpha,
            'zorder':   display.zorder, }
    remove_none(k)

    out = plt.quiver(*args, **k)
        
    # Set for Colorbar.vi if using colormap
    if len(args) == 5:
        ctx.mappable = out


@resource('streamline')
def streamline(ctx, a):
    """ Represents Streamline.vi. """
    
    plotid      = a.plotid()
    x           = a.dbl_1d('x')     # X loc of arrows
    y           = a.dbl_1d('y')     # Y loc of arrows
    u           = a.dbl_2d('u')     # Arrow X component
    v           = a.dbl_2d('v')     # Arrow Y component
    c           = a.dbl_2d('c')     # Vals for colormap
    
    density     = a.float('density')
    arrowsize   = a.float('arrowsize')    
    line        = a.line()
    cmap        = a.colormap()

    ctx.set(plotid)
    ctx.fail_if_polar()
    ctx.fail_if_log_symlog()
    
    # All dimensions must be greater than 5 or pyplot.streamplot breaks
    if any([(dim==2 or dim==4) for dim in (u.shape+v.shape)]):
        return

    # We need some data to plot; if not present, simply return (no error)
    if np.product(u.shape + v.shape) == 0:
        return
        
    # Apply default values for optional args
    if len(x) == 0:
        x = np.arange(u.shape[1])
    if len(y) == 0:
        y = np.arange(u.shape[0])
        
    # Check for MPL-required regularity
    def check_coords(arr):
        if np.any(~np.isfinite(arr)):
            return False
        tol = 1e-5
        arr = arr[1:] - arr[0:-1] # get deltas (1st der)
        arr = arr[1:] - arr[0:-1] # deltas of deltas (2nd der)
        return not np.any(np.abs(arr) > tol)
        
    if not check_coords(x):
        raise errors.InputNotRegular("X Coordinate array elements must be monotonic, uniformly spaced, and contain only finite values")
    if not check_coords(y):
        raise errors.InputNotRegular("Y Coordinate array elements must be monotonic, uniformly spaced, and contain only finite values")

    # Clip all to same size and remove NaNs
    if len(c) != 0:
        x, y, u, v, c = filters.filter_2d(x, y, u, v, c)
    else:
        x, y, u, v = filters.filter_2d(x, y, u, v)
    
    # Data must be at least 2x2
    if u.shape[0] < 2 or u.shape[1] < 2:
        return

    # Ignore invalid values
    if density is not None and density < 0:
        density = None
    if density is not None and density == 0:
        return  # MPL can't handle this
    if arrowsize is not None and arrowsize < 0:
        arrowsize = None
                    
    # Bug in MPL
    if arrowsize is not None and arrowsize == 0:
        arrowsize = 0.00001
        
    # Color priority: (1) line.color, (2) 2D colormap array, (3) black
    if line.color is not None:
        color = line.color
    elif len(c) != 0:
        color = c
    else:
        color = 'k'
        
    # There's a bug in MPL which breaks colormapping with the default options
    # to Normalize.  Only happens with streamplot.  So we manually initialize
    # the Normalize range.
    if isinstance(color, np.ndarray):
        from matplotlib import colors
        vmin = cmap.vmin if cmap.vmin is not None else color.min()
        vmax = cmap.vmax if cmap.vmax is not None else color.max()
        norm = colors.Normalize(vmin=vmin, vmax=vmax)
    else:
        norm = None
        
    # Better-looking defaults
    if density is None:
        density = 1.5
        
    k = {   'density':      density,
            'arrowsize':    arrowsize,
            'color':        color,
            'linewidth':    line.width,
            'cmap':         cmap.map,
            'norm':         norm }
    remove_none(k)
        

    
    out = plt.streamplot(x, y, u, v, **k)

    # For Colorbar.vi
    if isinstance(color, np.ndarray):
        # MPL's streamplot return object is bizarre and can't be used directly
        # as an argument to colorbar().  So use the .line attribute.
        ctx.mappable = out.lines


@resource('hist_auto')
def histogram_auto(ctx, a):
    """ Represents Histogram.vi. """   
    
    plotid      = a.plotid()
    data        = a.dbl_1d('data')
    bins        = a.int('n')
    legend      = a.string('legend')

    xmin        = a.float('xmin')
    xmax        = a.float('xmax')
    
    cumulative  = a.bool('cumulative')
    normalize   = a.bool('normalize')
    color       = a.color('color')
    line        = a.line()
    display     = a.display()
    
    ctx.set(plotid)
    
    # Do this up front, so the cycle is advanced in case we have to bail out
    if color is None:
        color = ctx.next_color(bar=True)
    ctx.errorbar_color(color)

    # Apply defaults for optional args
    if bins < 0:
        bins = 10
    elif bins == 0:
        return
        
    # Filter data
    data = data[np.isfinite(data)]
    
    # All filtered (or zero-length to start with)
    if len(data) == 0:
        return
    
    # Note we do this after the len() check, as min/max will raise exceptions
    mn = xmin if xmin is not None else data.min()
    mx = xmax if xmax is not None else data.max()
        
    # Check for data within bounds given
    # Note this also handles the case where limits are reversed
    data_len = np.count_nonzero((data >= mn) & (data <= mx))
    if data_len == 0:
        return
        
    if normalize:
        # Note we've checked for data_len == 0
        weights = 100*np.ones_like(data)/data_len
    else:
        weights = None
 
    range = (mn, mx)
    
    k = {   'bins':         bins,
            'cumulative':   cumulative,
            'color':        color,
            'weights':      weights,
            'range':        range,
            'linestyle':    line.style,
            'edgecolor':    line.color,
            'linewidth':    line.width, 
            'log':          ctx.yscale == 'log'}
    k.update(display._k())
    remove_none(k)
        
    n, bins, patches = plt.hist(data, **k)

    if len(legend) != 0:
        ctx.legend_entries.append((patches[0], legend))
        

@resource('hist_manual')
def histogram_manual(ctx, a):
    """ Represents Histogram.vi. """   
    
    plotid      = a.plotid()
    data        = a.dbl_1d('data')
    bins        = a.dbl_1d('bins')
    legend      = a.string('legend')

    color       = a.color('color')
    cumulative  = a.bool('cumulative')
    normalize   = a.bool('normalize')
    line        = a.line()
    display     = a.display()

    ctx.set(plotid)
    
    # Do this up front, so the cycle is advanced in case we have to bail out
    if color is None:
        color = ctx.next_color(bar=True)
    ctx.errorbar_color(color)

    # Filter data & bins
    data = data[np.isfinite(data)]
    bins = bins[np.isfinite(bins)]
    
    # All filtered (or zero-length to start with)
    # Note we need 2 bin edges to proceed
    if len(data) == 0 or len(bins) < 2:
        return
    
    # MPL requires bin edges be in order
    bins = np.sort(bins)

    # Note we do this after the len() check, as min/max will raise exceptions
    mn, mx = bins.min(), bins.max()
        
    # Check for data within bounds given
    # Note this also handles the case where limits are reversed
    data_len = np.count_nonzero((data >= mn) & (data <= mx))
    if data_len == 0:
        return
        
    if normalize:
        # Note we've checked for data_len == 0
        weights = 100*np.ones_like(data)/data_len
    else:
        weights = None
 
    k = {   'bins':         bins,
            'cumulative':   cumulative,
            'color':        color,
            'weights':      weights,
            'linestyle':    line.style,
            'edgecolor':    line.color,
            'linewidth':    line.width, 
            'log':          ctx.yscale == 'log'}
    k.update(display._k())
    remove_none(k)
        
    n, bins, patches = plt.hist(data, **k)

    if len(legend) != 0:
        ctx.legend_entries.append((patches[0], legend))
    

@resource('hist2d_auto')
def histogram_2d_auto(ctx, a):
    
    plotid  = a.plotid()
    xdata   = a.dbl_1d('xdata')
    ydata   = a.dbl_1d('ydata')
    nx      = a.int('nx')
    ny      = a.int('ny')
    
    xmin    = a.float('xmin')
    xmax    = a.float('xmax')
    ymin    = a.float('ymin')
    ymax    = a.float('ymax')

    norm    = a.bool('normalize')
    cmap    = a.colormap()
    display = a.display()

    ctx.set(plotid)
    ctx.fail_if_polar()
    ctx.fail_if_log_symlog()

    # Docs say zero bins are permitted (and make no plot)
    if nx == 0 or ny == 0:
        return
        
    # Apply defaults
    if nx < 0:
        nx = 10
    if ny < 0:
        ny = 10
        
    # Filter out NaNs, make same shape
    xdata, ydata = filters.filter_1d(xdata, ydata)
    
    # All data filtered out (or not present to begin with)
    if len(xdata) == 0:
        return

    # Note we do this after then len() check
    xmn = xmin if xmin is not None else xdata.min()
    xmx = xmax if xmax is not None else xdata.max()
    ymn = ymin if ymin is not None else ydata.min()
    ymx = ymax if ymax is not None else ydata.max()
    
    # Check for data within bounds
    # Note this also handles the case where limits are reversed
    xvalid = (xdata >= xmn) & (xdata <= xmx)
    yvalid = (ydata >= ymn) & (ydata <= ymx)
    data_len = np.count_nonzero(xvalid & yvalid)
    if data_len == 0:
        return
        
    # The MPL "normed" keyword is totally bananas.  So we use weights to
    # express counts as a percent of events.
    if norm:
        weights = 100*np.ones_like(xdata)/data_len
    else:
        weights = None
    
    range = np.array([[xmn,xmx],[ymn,ymx]])
    
    k = {   'bins':     [nx, ny],
            'range':    range,
            'cmap':     cmap.map,
            'norm':     cmap._norm(),
            'weights':  weights }
    k.update(display._k())
    remove_none(k)
    
    out = plt.hist2d(xdata, ydata, **k)
    
    # For Colorbar.vi.  Note a colorbar is always permitted.
    ctx.mappable = out[-1]


@resource('hist2d_manual')
def histogram_2d_manual(ctx, a):
    
    plotid  = a.plotid()
    xdata   = a.dbl_1d('xdata')
    ydata   = a.dbl_1d('ydata')
    xbins   = a.dbl_1d('xbins')
    ybins   = a.dbl_1d('ybins')

    norm    = a.bool('normalize')
    cmap    = a.colormap()
    display = a.display()

    ctx.set(plotid)
    ctx.fail_if_polar()
    ctx.fail_if_log_symlog()

    # Filter out invalid bin values.  MPL also requires sorted bins.
    xbins = xbins[np.isfinite(xbins)]
    ybins = ybins[np.isfinite(ybins)]
    xbins = np.sort(xbins)
    ybins = np.sort(ybins)
    
    # Docs say less than two bin edges are permitted (and make no plot)
    if len(xbins) < 2 or len(ybins) < 2:
        return
        
    # Filter out NaNs, make same shape
    xdata, ydata = filters.filter_1d(xdata, ydata)
    
    # All data filtered out (or not present to begin with)
    if len(xdata) == 0:
        return

    # Note we do this after then len() check
    xmn, xmx = xbins.min(), xbins.max()
    ymn, ymx = ybins.min(), ybins.max()
    
    # Check for data within bounds
    # Note this also handles the case where limits are reversed
    xvalid = (xdata >= xmn) & (xdata <= xmx)
    yvalid = (ydata >= ymn) & (ydata <= ymx)
    data_len = np.count_nonzero(xvalid & yvalid)
    if data_len == 0:
        return
        
    # The MPL "normed" keyword is totally bananas.  So we use weights to
    # express counts as a percent of events.
    if norm:
        weights = 100*np.ones_like(xdata)/data_len
    else:
        weights = None
    
    k = {   'bins':     [xbins, ybins],
            'cmap':     cmap.map,
            'norm':     cmap._norm(),
            'weights':  weights }
    k.update(display._k())
    remove_none(k)
    
    out = plt.hist2d(xdata, ydata, **k)
    
    # For Colorbar.vi.  Note a colorbar is always permitted.
    ctx.mappable = out[-1]
    
    
@resource('errorbar')
def errorbar(ctx, a):
    """ Represents Errorbar.vi. """
    
    plotid      = a.plotid()
    x           = a.dbl_1d('x')
    y           = a.dbl_1d('y')
    xerr        = a.dbl_1d('xerr')
    yerr        = a.dbl_1d('yerr')
    
    color       = a.color('color')
    linewidth   = a.float('linewidth')
    capsize     = a.float('capsize')
    display     = a.display()
        
    ctx.set(plotid)
    ctx.fail_if_polar()

    if color is None:
        color = ctx.errorbar_color()

    # No need in plotting if neither array is present
    if len(xerr) == 0 and len(yerr) == 0:
        return
        
    # Apply defaults
    if len(x) == 0:
        x = np.arange(len(y))

    # Make all the same length, and filter NaNs.
    if len(xerr) != 0 and len(yerr) != 0:
        x, y, xerr, yerr = filters.filter_1d(x, y, xerr, yerr)
    elif len(xerr) != 0:
        x, y, xerr = filters.filter_1d(x, y, xerr)
    elif len(yerr) != 0:
        x, y, yerr = filters.filter_1d(x, y, yerr)

    # All filtered out (or zero-length to start with)    
    if len(y) == 0:
        return
        
    # For keyword filtering
    if len(xerr) == 0:
        xerr = None
    if len(yerr) == 0:
        yerr = None
            
    if linewidth == 0:
        return

    k = {   'xerr':         xerr,
            'yerr':         yerr,
            'ecolor':       color,
            'elinewidth':   linewidth,
            'capthick':     linewidth,
            'capsize':      capsize,    
            'linestyle':    'None'  }
    k.update(display._k())
    remove_none(k)

    plt.errorbar(x, y, **k)


@resource('arrayview')
def arrayview(ctx, a):
    """ ArrayView.vi """
    
    plotid  = a.plotid()
    data    = a.dbl_2d('data')

    xmin    = a.float('xmin')
    xmax    = a.float('xmax')
    ymin    = a.float('ymin')
    ymax    = a.float('ymax')
    
    cmap    = a.colormap()
    display = a.display()

    ctx.set(plotid)
    ctx.fail_if_polar()
    ctx.fail_if_log_symlog()

    if len(data) == 0:
        return
        
    # Apply defaults
    if xmin is None: xmin = 0
    if xmax is None: xmax = xmin + data.shape[1]
    if ymin is None: ymin = 0
    if ymax is None: ymax = ymin + data.shape[0]
    
    # MPL can't handle reversed indices.
    # It flips the entire X axis for some reason.
    if xmax < xmin:
        data = data[:, ::-1]
        xmin, xmax = xmax, xmin
    if ymax < ymin:
        data = data[::-1, :]
        ymin, ymax = ymax, ymin
        
    k = {   'origin':   'lower',
            'extent':   [xmin, xmax, ymin, ymax],
            'aspect':   'auto',
            'cmap':     cmap.map,
            'norm':     cmap._norm(),   }
    k.update(display._k())
    remove_none(k)
    
    out = plt.imshow(data, **k)

    # For Colorbar.vi
    ctx.mappable = out