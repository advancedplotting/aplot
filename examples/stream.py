import numpy as np
from matplotlib import pyplot as plt
import sympy
from sympy.abc import x, y


XMIN = -3
XMAX = 3
RADIUS = 1.0
N = 25
    
    
def cylinder_stream_function(U=1, R=1):
    r = sympy.sqrt(x**2 + y**2)
    theta = sympy.atan2(y, x)
    return U * (r - R**2 / r) * sympy.sin(theta)
    
def velocity_field(psi):
    """ u, v -> give U or V vector component for position X/Y """
    
    u = sympy.lambdify((x, y), psi.diff(y), 'numpy')
    v = sympy.lambdify((x, y), -psi.diff(x), 'numpy')
    return u, v
    
def plot_streamlines(ax, u, v, xlim=(-1, 1), ylim=(-1, 1)):
    x0, x1 = xlim
    y0, y1 = ylim
    Y, X =  np.ogrid[y0:y1:25j, x0:x1:25j]
    U = u(X,Y)
    V = v(X,Y)
    ax.streamplot(X, Y, u(X, Y), v(X, Y), density=2, color='cornflowerblue')
    #ax.quiver(X,Y,u(X,Y),v(X,Y))
    
def compute_components(domask):
    """ Returns:
    
    x: 1-D array with x coordinates
    y: 1-D array with y coordinates
    u: 2-D array with x vector components
    v: 2-D array with y vector components
    """
    

    
    uf, vf = velocity_field(cylinder_stream_function(R=RADIUS))

    y, x = np.ogrid[XMIN:XMAX:N*1j, XMIN:XMAX:N*1j]
    
    u = uf(x,y)
    v = vf(x, y)
    
    xx, yy = np.mgrid[XMIN:XMAX:N*1j, XMIN:XMAX:N*1j]
    
    r = np.sqrt(xx**2 + yy**2)
    
    mask = r <= RADIUS
    
    if domask:
        u[mask] = 0
        v[mask] = 0
    
    x = x.reshape((N,))
    y = y.reshape((N,))
    
    return x, y, u, v
    

def makeplot(show=False):

    x, y, u, v = compute_components(True)
    
    np.savetxt('streamlines_u.txt', u)
    np.savetxt('streamlines_v.txt', v)
    
    if show:
        mag = np.sqrt(u**2 + v**2)
    
        plt.figure(1)
        plt.clf()
        plt.axes(aspect=True)#, axisbg='#444444')
    
        print x.shape
        plt.streamplot(x,y,u,v,color=mag,cmap='Blues',density=1.5, arrowsize=2)
        plt.colorbar().set_label("Flow speed")
    
        c = plt.Circle((0,0), radius=RADIUS, facecolor='#aaaacc', linewidth=0, zorder=10)
        plt.gca().add_patch(c)
        plt.xlim(-3,3)
        plt.ylim(-3,3)
    

