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

from matplotlib import pyplot as plt
from cStringIO import StringIO
from PIL import Image
import numpy as np
import os.path as op
import time

from .terminals import remove_none
from .core import resource
from . import errors

@resource('init')
def init(ctx, a):
    """ No-op for Init.vi """
    pass
    

@resource('new')
def new(ctx, a):
    """ Create a new figure, and initialize the axes.
    
    Returns a string integer with the new plot ID.
    """
    import random
    
    PLOT_TYPES = {0: 'rect', 1: 'polar'}
    SCALES = {0: 'linear', 1: 'linear', 2: 'log', 3: 'symlog'}
    
    kind        = a.enum('kind', PLOT_TYPES)
    xscale      = a.enum('xscale', SCALES)
    yscale      = a.enum('yscale', SCALES)
    bgcolor     = a.color('bgcolor')
    axiscolor   = a.color('axiscolor')
    left        = a.float('left')
    right       = a.float('right')
    top         = a.float('top')
    bottom      = a.float('bottom')
    aspect      = a.float('aspect')

    # Check polar arguments for consistency
    if kind == 'polar' and xscale != 'linear':
        raise errors.LogNotSupported("Polar plots support only linear scales for X")

    # Right/top default margins are smaller as there are no labels
    left    = left if left is not None else 0.12
    bottom  = bottom if bottom is not None else 0.12
    right   = right if right is not None else 0.10
    top     = top if top is not None else 0.10
    
    width = (1.-left-right)
    height = (1.-bottom-top)
    
    # Catch reversed margins
    if width < 0:
        width = -1*width
        left = right
    if height < 0:
        height = -1*width
        bottom = top
        
    if aspect <= 0:
        aspect = None
        
    k = {   'axisbg':      axiscolor,
            'polar':       kind == 'polar',
            'aspect':      aspect, }
    remove_none(k)
        
    plotid = random.randint(1,2**30)
    f = ctx.new(plotid)
    
    ctx.polar = (kind == 'polar')
    
    plt.axes((left, bottom, width, height), **k)
    if bgcolor is not None:
        f.set_facecolor(bgcolor)
    else:
        f.set_facecolor('w')
            
    # Manually setting the scale to linear screws up the default axis range
    if xscale != 'linear':
        plt.xscale(xscale)#, nonposx='clip')
    if yscale != 'linear':
        plt.yscale(yscale)#, nonposy='clip')
    
    ctx.xscale = xscale
    ctx.yscale = yscale
        
    return str(plotid)
    

@resource('close')
def close(ctx, a):
    """ Close a Plot ID, ignoring any error. """
    
    plotid = a.plotid()
    
    try:
        ctx.set(plotid)
        ctx.close()
    except Exception:
        pass
        
        
@resource('isvalid')
def isvalid(ctx, a):
    """ Test if an identifier is known.
    
    Returns a string '1' if valid, '0' otherwise.
    """
    
    plotid = a.plotid()
    
    return "%d" % (1 if ctx.isvalid(plotid) else 0)
    
    
@resource('view')
def view(ctx, a):
    """ Represents View.vi, optimized for rendering to a Picture."""
    
    plotid = a.plotid()
        
    f = ctx.set(plotid)
    
    sio = StringIO()
                        
    # Step 1: Save the figure to a raw RGBA buffer
    plt.savefig(sio, format='rgba', dpi=f.get_dpi(), facecolor=f.get_facecolor())
    sio.seek(0)

    # Step 2: Import the image into PIL
    xsize, ysize = f.canvas.get_width_height()
    img = Image.fromstring("RGBA", (xsize, ysize), sio.read())
    
    sio.close()
    
    # Step 3: Process the alpha channel out
    img.load()
    newimg = Image.new('RGB', img.size, (255, 255, 255))
    newimg.paste(img, mask=img.split()[3])
    
    # Step 4: Generate ARGB buffer (in little-endian format)
    r, g, b = tuple(np.fromstring(x.tostring(), dtype='u1') for x in newimg.split())
    a = np.empty((xsize*ysize,4), dtype='u1')
    a[:,0] = b
    a[:,1] = g
    a[:,2] = r
    a[:,3] = 0
    
    # Step 4: Return to LabVIEW, with size headers
    sio = StringIO()
    sio.write(np.array(ysize, 'u4').tostring())
    sio.write(np.array(xsize, 'u4').tostring())
    sio.write(a.tostring())
    sio.seek(0)
    
    return sio.read()        


@resource('save')
def save(ctx, a):
    """ Represents Save.vi. """
    
    EXTENSIONS = {  '.pdf':     'pdf',
                    '.png':     'png',
                    '.bmp':     'bmp',
                    '.tif':     'tiff',
                    '.tiff':    'tiff',
                    '.jpg':     'jpeg',
                    '.jpeg':    'jpeg',
                    '.gif':     'gif', }
        
    plotid  = a.plotid()
    name    = a.string('path')
    
    f = ctx.set(plotid)
    
    root, ext = op.splitext(name)
    ext = ext.lower()
    if len(ext) == 0:
        raise errors.UnrecognizedFileExtension('No file extension: "%s"' % name)
    if ext not in EXTENSIONS:
        raise errors.UnrecognizedFileExtension('Unknown file extension: "%s"' % ext)
    format = EXTENSIONS[ext]

    vector_formats = ('pdf',)
    
    sio = StringIO()
    
    # PDF doesn't need further processing by PIL,
    # so we can short-circuit and return here.
    if format in vector_formats:
        plt.savefig(sio, format=format)
        sio.seek(0)
        return sio.read()
                
    # Step 1: Save the figure to a raw RGBA buffer
    plt.savefig(sio, format='rgba', dpi=f.get_dpi(), facecolor=f.get_facecolor())
    sio.seek(0)

    # Step 2: Import the image into PIL
    xsize, ysize = f.canvas.get_width_height()
    img = Image.fromstring("RGBA", (xsize, ysize), sio.read())
 
    # Step 3: Process the alpha channel out
    img.load()
    newimg = Image.new('RGB', img.size, (255, 255, 255))
    newimg.paste(img, mask=img.split()[3])
    img = newimg
        
    # Step 4: Export from PIL to the destination format
    sio = StringIO()
    img.save(sio, format=format)
    sio.seek(0)
    
    return sio.read()
