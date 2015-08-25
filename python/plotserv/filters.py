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

import numpy as np

def _make_mask(q):
    """ Return a boolean mask where False indicates NaN or Inf.
    May be used with any type of array, not just float. """
    if q.dtype.kind == 'f':
        return np.isfinite(q)
    return np.ones(len(q), dtype='bool')
        

def filter_1d(*args):
    """ Filters 1D arrays such that:
    
    1. All have the same length: the length of the smallest one.
    2. Entries in either which are non-finite are dropped from both.
    
    Returns a tuple with modified arguments.
    """
        
    minlen = min([len(x) for x in args])
    
    args = [x[0:minlen] for x in args]
        
    mask = np.ones(minlen, dtype='bool')
    for a in args:
        mask &= _make_mask(a)
    
    if not np.all(mask):
        args = [x[mask] for x in args]
    
    return tuple(args)
    
    
def filter_2d(x, y, *args):
    """ Simultaneously filter 1D arrays x and y, and an arbitrary number of
    2D arrays.
    """
    
    # Mask slicing doesn't like empty arrays
    if any([len(a)==0 for a in ((x,y)+args)]):
        empty_1d = np.empty((0,))
        empty_2d = np.empty((0,0))
        return (empty_1d, empty_1d) + (empty_2d,)*len(args)
    
    xsize = min([len(x)] + [a.shape[1] for a in args])
    ysize = min([len(y)] + [a.shape[0] for a in args])
    
    x = x[0:xsize]
    y = y[0:ysize]
    
    xmask = _make_mask(x)
    ymask = _make_mask(y)
    
    args = [a[0:ysize, 0:xsize] for a in args]
    args = [a[ymask, :] for a in args]
    args = [a[:,xmask] for a in args]

    x = x[xmask]
    y = y[ymask]
      
    return (x,y) + tuple(args)
    

