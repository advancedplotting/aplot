"""
    Generates colormap documentation.
"""

from matplotlib import pyplot as plt
import numpy as np
from collections import OrderedDict

MAPS = OrderedDict([
    ('Rainbow',          'jet'),
    ('Hot and Cold',     'seismic'),
    ('White to Black',   'binary'),
    ('White to Blue',    'Blues'),
    ('White to Green',   'Greens'),
    ('White to Red',     'Reds'),
    ('Fire',             'hot'),
    ('Water',            'ocean'),
    ('Earth',            'gist_earth'),
    ('Air',              'cool'),
    ('Pastel',           'Accent'),
    ('Banded',           'Paired'),
    ('Stepped',          'prism')    ])
    
def plot_color_gradients():
    fig, axes = plt.subplots(nrows=len(MAPS))
    fig.subplots_adjust(top=0.99, bottom=0.01, left=0.01, right=0.79)

    for ax, name in zip(axes, MAPS.keys()):
        ax.imshow(gradient, aspect='auto', cmap=MAPS[name])
        pos = list(ax.get_position().bounds)
        x_text = pos[2] + 0.02
        y_text = pos[1] + pos[3]/2.
        fig.text(x_text, y_text, name, va='center', ha='left', fontsize=14)

    # Turn off *all* ticks & spines, not just the ones with colormaps.
    for ax in axes:
        ax.set_axis_off()

gradient = np.linspace(0, 1, 256)
gradient = np.vstack((gradient, gradient))

plot_color_gradients()
plt.show()