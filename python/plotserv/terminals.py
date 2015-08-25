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
    Provides a smart dictionary "Adapter" class, which handles conversion
    between the raw strings POST-ed to the service and Python objects.
"""

import numpy as np
from matplotlib import mathtext

MATH_PARSER = mathtext.MathTextParser('agg')


def remove_none(dct):
    """ Remove entries from a dict whose value is None. """
    tmp = dict((x, y) for (x, y) in dct.iteritems() if y is not None)
    dct.clear()
    dct.update(tmp)


class Terminals(dict):

    """
        Python-side representation of a VI's terminals.
        
        To access data on a particular terminal, call the method
        corresponding to the terminal's type, with the name of the
        terminal.
        
        Example: For a VI with a standard PlotID terminal:
        
            plotid = t.int('plotid')
            
        Non-finite values for floats are converted to None.
    """
    
    def _check(self, name):
        if not name in self:
            raise ValueError("Required key %s not present" % name)
                
    def plotid(self):
        """ Retrieve standard PlotID entry """
        return self.int('plotid')
        
    def int(self, name):
        """ Get an integer. """
        self._check(name)
        return int(self[name])

    def float(self, name, raw=False):
        """ Get a float.  Non-finite values become None. """
        self._check(name)
        f = float(np.frombuffer(self[name], dtype='<f8', count=1))
        if not raw and not np.isfinite(f):
            return None
        return f
        
    def enum(self, name, enum):
        """ Get the member of an enum.
        
        "enum" should be a dict mapping ints to objects.  If the terminal's
        int doesn't appear in "enum", ValueError is raised.
        """
        self._check(name)
        i = int(self[name])
        if i not in enum:
            raise ValueError("Illegal enum value %d" % i)
        return enum[i]
        
    def string(self, name):
        """ Get a string.  None is never returned. """
        # Strings are sent with 4-byte length header.
        # We can ignore this, as the buffer size tells us the string length.
        self._check(name)
        s = self[name][4:]
        
        # Until proper Unicode support we replace non-ASCII chars with '?'
        s = s.decode('ascii', 'replace').encode('ascii', 'replace')
        
        try:
            MATH_PARSER.parse(s)
        except ValueError:
            s = s.replace('$', '\$')
        return s
        
    def color(self, name):
        """ Get a Matplotlib color expression.
        
        0. If the string "none", returns None (LabView "Automatic")
        1. If alpha=FF, a plain RGB string as a workaround for pyplot bugs
        2. Otherwise, convert to a 4-tuple of 0-1 float ranges (may introduce
           small rounding errors)
        """
        self._check(name)
        val = self[name]
                
        if val == 'none':
            return None
            
        if val.endswith('FF'):
            return val[0:7]
        
        val = val[1:] # strip off leading "#"
        r = int(val[0:2], base=16)
        g = int(val[2:4], base=16)
        b = int(val[4:6], base=16)
        a = int(val[6:8], base=16)
        
        return tuple(x/255.0 for x in (r,g,b,a))
        
    def dbl_1d(self, name):
        """ Get a 1D array of floats. """
        self._check(name)
        return np.fromstring(self[name][4:], dtype='<f8')
        
    def string_1d(self, name):
        """ Get a 1D array of strings """
        self._check(name)
        s = self[name]

        length = np.fromstring(s[0:4], dtype='<u4', count=1).item()
        strings = []
        ptr = 4
        for idx in xrange(length):
            slength = np.fromstring(s[ptr:ptr+4], dtype='<u4', count=1).item()
            ptr += 4
            strings.append(s[ptr:ptr+slength])
            ptr += slength
            
        # Nuke non-ASCII chars (replace with '?')
        strings = [x.decode('ascii', 'replace').encode('ascii', 'replace') for x in strings]

        return np.array(strings)

    def dbl_2d(self, name):
        """ Get a 2D array of floats."""
        self._check(name)
        data = self[name]
        dims = np.fromstring(data, dtype='<i4', count=2)
        data = np.fromstring(data[8:], dtype='<f8')
        return data.reshape(dims)
        
    def bool(self, name):
        """ Get a bool. None is never returned. """
        self._check(name)
        s = {'True': True, 'False': False}[self[name]]
        return s

    def line(self):
        """ Get an object representing a Line cluster """
        return Line(self)
        
    def text(self):
        """ Get an object representing a Text cluster """
        return Text(self)
        
    def colormap(self):
        """ Get an object representing a Colormap cluster """
        return Colormap(self)
        
    def marker(self):
        """ Get an object representing a Marker cluster """
        return Marker(self)
        
    def display(self):
        """ Get an object representing a Display cluster """
        return Display (self)
        
        
class Line(object):

    """
        Represents properties/Line.ctl.
    """
    
    STYLES = {0: None, 1: 'solid', 2: 'dashed', 3: 'dotted',
              4: 'dashdot', 5: 'None'}
    
    
    def __init__(self, a):
        
        self.style = a.enum('line.style', self.STYLES)
        self.width = a.float('line.width')
        self.color = a.color('line.color')
        
        # Hack as not all locations in MPL can handle 'None'
        if self.style == 'None':
            self.style = 'solid'
            self.width = 0
        
        
class Colormap(object):

    """
        Represents properties/Colormap.ctl.
    """
    
    MAPS = {0:  'jet',
            1:  'jet',
            2:  'seismic',
            3:  'binary',
            4:  'Blues',
            5:  'Greens',
            6:  'Reds',
            7:  'hot',
            8:  'ocean',
            9:  'gist_earth',
            10: 'cool',
            11: 'Accent',
            12: 'Paired',
            13: 'prism', }

    SCALES = {0: 'linear', 1: 'linear', 2: 'log10'}
    
    def __init__(self, a):
        
        self.map = a.enum('cmap.map', self.MAPS)
        self.vmin = a.float('cmap.vmin')
        self.vmax = a.float('cmap.vmax')
        
        self.reverse = a.bool('cmap.reverse')
        self.scale = a.enum('cmap.scale', self.SCALES)
        
        if self.reverse:
            self.map = self.map+'_r'
        
        
    def _norm(self):
        """ Get an appropriate Normalize instance """
        from matplotlib import colors
        
        k  = {  'vmin': self.vmin,
                'vmax': self.vmax }
        remove_none(k)
        
        if self.scale == 'linear':
            return colors.Normalize(**k)
        elif self.scale == 'log10':
            return colors.LogNorm(**k)
        else:
            raise ValueError('Unknown colormap scale "{}"'.format(self.scale))
        
        
class Marker(object):

    """
        Represents properties/Marker.ctl.
    """
    
    MARKERS = { 0: None, 
                1: 'o', 
                2: 's',
                3: '^',
                4: 'D',
                5: '*',
                6: 'None'}
    
    def __init__(self, a):
        
        self.style = a.enum('marker.style', self.MARKERS)
        self.color = a.color('marker.color')
        self.size = a.float('marker.size')
        
        
class Text(object):

    """
       Represents properties/Text.ctl.
    """
    
    SIZES = {0: None, -1: 'xx-small', -2: 'x-small', -3: 'small',
             -4: 'medium', -5: 'large', -6: 'x-large', -7: 'xx-large'}
             
    STYLES = {0: None, 1: 'normal', 2: 'italic', 3: 'bold'}
    
    def __init__(self, a):
        
        self.color = a.color('text.color')
        self.backgroundcolor = a.color('text.backgroundcolor')
        self.fontstyle = a.enum('text.fontstyle', self.STYLES)
        self.rotation = a.float('text.rotation')
        self.weight = None

        if self.fontstyle == 'bold':
            self.fontstyle = None
            self.weight = 'bold'
            
        fs = a.int('text.fontsize')
        if fs < 0 and fs not in self.SIZES:
            fs = None
        else:
            fs = self.SIZES.get(fs, fs)
        self.fontsize = fs
            
    def _k(self):
        """ Get a dict containing MPL-style text keywords """
        
        k = {   'color': self.color,
                'backgroundcolor': self.backgroundcolor,
                'fontsize': self.fontsize,
                'fontstyle': self.fontstyle,
                'rotation': self.rotation,
                'weight': self.weight, }
        remove_none(k)
        
        return k

       
class Display(object):

    """
        Represents properties/Display.ctl
    """

    def __init__(self, a):
        self.alpha = a.float('display.alpha')
        self.zorder = a.float('display.zorder')
        
        if self.alpha is not None:
            if self.alpha > 1 or self.alpha < 0:
                self.alpha = None
                
    def _k(self):
        k = {   'alpha':    self.alpha,
                'zorder':   self.zorder, }
        remove_none(k)
        return k