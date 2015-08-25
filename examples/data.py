
"""
    Module to generate data used by example VIs.
"""

from matplotlib import pyplot as plt
import numpy as np
import os.path as op

def localpath(name):
    p = op.join(op.dirname(__file__), name)
    
def blob(show=False):
    """ Data suitable for imshow, contour, contourf. """
    
    zx, zy = np.mgrid[-50:50,-50:50]
    
    z = np.sin(zx*(3.14/50) + 3.14*1.2)*np.cos(zy*(3.14/50)+0.5*3.14/2) + zx*0.01 + zy*0.03 + 0.5
    
    z = z[:,::-1]
    
    np.savetxt('blob.txt', z)
    
    if show:
        f = plt.figure(199)
        plt.clf()
        plt.imshow(z)

 
def hist_1d(show=False):
    """ Random data for 1D histogram """
    
    np.random.seed(100)
    data = np.random.normal(size=1000)
    
    if show:
        f = plt.figure(199)
        plt.clf()
        plt.hist(data, 50)
        
    np.savetxt('hist_1d.txt', data)
    
    
def hist_2d(show=False):
    """ Random data for 2D histogram """
    
    np.random.seed(101)
    datax = np.random.normal(size=5000)
    datay = np.random.normal(size=5000)

    if show:
        f = plt.figure(199)
        plt.clf()
        plt.hist2d(datax, datay, bins=[30,30])
        
    np.savetxt('hist_2d_x.txt', datax)
    np.savetxt('hist_2d_y.txt', datay)
      
        
def scatter(show=False):
    """ Data for scatterplot """
    
    np.random.seed(200)
    
    xx = np.arange(40, dtype='f')
    yy = xx.copy()
    
    xx += np.random.normal(size=40)*4
    yy += np.random.normal(size=40)*3
    
    if show:
        f = plt.figure(199)
        plt.clf()
        plt.scatter(xx, yy)
        
    np.savetxt('scatter_x.txt', xx)
    np.savetxt('scatter_y.txt', yy)
    
    
def scatter_cycle(show=False):
    """ Demo for color cycle """
    
    N = 6
    
    datax = np.zeros((N,100),dtype='f')
    datay = datax.copy()
    
    np.random.seed(300)
    
    for idx in xrange(N):
        datax[idx] = np.random.normal(idx*2, size=100)
        datay[idx] = np.random.normal(idx*2, size=100)
        
    if show:
        f = plt.figure(199)
        plt.clf()
        colors = ['b', 'g', 'r', 'c', 'm', 'y']
        outs = [plt.scatter(datax[idx], datay[idx], color=colors[idx]) for idx in xrange(N)]
    plt.legend(outs, [('Set %d' % x) for x in xrange(6)], loc=2)
            
    np.savetxt('scatter_cycle_x.txt', datax)
    np.savetxt('scatter_cycle_y.txt', datay)
    

def vectorfield(show=False):
    """ Data for vectorfield """
    
    R = 7.0
    J = 100.0
    
    YY, XX = np.mgrid[-10:10,-10:10]
        
    print XX
    print YY
    
    MAG = np.sqrt(XX**2 + YY**2)
    
    FIELDX_IN = np.zeros_like(XX)
    FIELDY_IN = np.zeros_like(YY)
    FIELDX_OUT = FIELDX_IN.copy()
    FIELDY_OUT = FIELDY_IN.copy()
    
    FIELDX_IN = -1*YY*(J/2.)
    FIELDY_IN = XX*(J/2.)

    FIELDX_OUT = ((R**2*J)/(2*(XX**2 + YY**2)))*(-1*YY)
    FIELDY_OUT = ((R**2*J)/(2*(XX**2 + YY**2)))*(XX)

    FIELDX = np.zeros_like(XX)
    FIELDY = np.zeros_like(YY)
    
    MAG = np.sqrt(XX**2 + YY**2)
    
    FIELDX[MAG<R] = FIELDX_IN[MAG < R]
    FIELDX[MAG>=R] = FIELDX_OUT[MAG >= R]
    
    FIELDY[MAG<R] = FIELDY_IN[MAG < R]
    FIELDY[MAG>=R] = FIELDY_OUT[MAG >= R]
    
    np.savetxt('vectorfield_x.txt', FIELDX)
    np.savetxt('vectorfield_y.txt', FIELDY)
    
    if show:
        f = plt.figure(199)
        plt.clf()
        plt.jet()
        plt.quiver(FIELDX, FIELDY, (FIELDX**2 + FIELDY**2))    


def mandelbrot(show=False):
    """ Data suitable for imshow, colorbar, etc. """

    NX = 500
    NY = 500
    
    def n_to_escape(c):
        z = 0
        for idx in xrange(200):
            z = z**2 + c
            if np.abs(z) > 2:
                break
        return idx
        
    img, real = np.mgrid[-0.68:-0.63:NX*1j,0.11:0.16:NY*1j]
    plane = real + img*(1.0j)
    
    print plane
    
    escape = np.zeros((NX,NY), dtype='f')
    
    for xx in xrange(NX):
        for yy in xrange(NY):
            escape[xx,yy] = n_to_escape(plane[xx,yy])
        
    print escape
    
    np.savetxt('mandelbrot.txt', escape)
    
    if show:
        f = plt.figure(199)
        plt.clf()
        plt.imshow(escape)