# -*- coding: utf-8 -*-
#
# plt_hms_challenger.py
#
# purpose:  Plot HMS Challenger track.
# author:   Filipe P. A. Fernandes
# e-mail:   ocefpaf@gmail
# web:      http://ocefpaf.github.io/
# created:  04-Sep-2013
# modified: Wed 04 Sep 2013 01:45:41 PM BRT
#
# obs: http://www.rmg.co.uk/server/show/ConMediaFile.16073
#

import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


def make_map(projection='robin', resolution='c'):
    fig, ax = plt.subplots(figsize=(10, 4))
    m = Basemap(projection=projection, resolution=resolution,
                lon_0=0, ax=ax)
    m.drawcoastlines()
    m.fillcontinents(color='0.85')
    parallels = np.arange(-60, 90, 30.)
    meridians = np.arange(-360, 360, 60.)
    m.drawparallels(parallels, labels=[1, 0, 0, 0])
    m.drawmeridians(meridians, labels=[0, 0, 1, 0])
    return fig, m


if __name__ == '__main__':
    fig, m = make_map()
    lon, lat = np.loadtxt('challenger_path.csv', delimiter=',',
                          unpack=True)
    m.plot(*m(lon, lat), color='#FF9900', linestyle='none', marker='o',
           markersize=5)

    fname = 'challenger.png'
    fig.savefig(fname, dpi=75, transparent=True)
    os.system('convert -trim %s %s' % (fname, fname))
