# -*- coding: utf-8 -*-
#
# woa09_horizontal.py
#
# purpose:  Plot horizontal sections from WOA09
# author:   Filipe P. A. Fernandes
# e-mail:   ocefpaf@gmail
# web:      http://ocefpaf.github.io/
# created:  01-Sep-2013
# modified: Wed 04 Sep 2013 05:44:55 PM BRT
#
# obs:
#

import os

import numpy as np
import matplotlib.pyplot as plt

from pandas import read_hdf
from mpl_toolkits.basemap import Basemap

from oceans.colormaps import cm
from oceans.datasets import woa_subset


def make_map(projection='robin', resolution='c'):
    fig, ax = plt.subplots(figsize=(11, 7))
    m = Basemap(projection=projection, resolution=resolution,
                lon_0=0, ax=ax)
    m.drawcoastlines()
    m.fillcontinents(color='0.85')
    parallels = np.arange(-60, 90, 30.)
    meridians = np.arange(-360, 360, 60.)
    m.drawparallels(parallels, labels=[1, 0, 0, 0])
    m.drawmeridians(meridians, labels=[0, 0, 1, 0])
    return fig, m


def get_data(fname='woa09_salinity.h5', key='salinity'):
    dataset = read_hdf(fname, key)
    lon = dataset.columns.values.astype(float)
    lat = dataset.index.values.astype(float)
    lon, lat = np.meshgrid(lon, lat)
    return lon, lat, dataset


def latitudinal_section(dataset):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dataset.index, dataset.mean(axis=1), 'k', linewidth=2)
    ax.set_xlabel('Latitude')
    ticks = -90, -45, 0, 45, 90
    labels = [u'%s\u00B0' % num for num in ticks]
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)
    ax.grid()
    return fig, ax


# Download/load data.
boundary = dict(llcrnrlon=0, urcrnrlon=360,
                llcrnrlat=-90, urcrnrlat=90)

if not os.path.isfile('woa09_salinity.h5'):
    dataset = woa_subset(var='salinity', clim_type='annual',
                         resolution='1deg', levels=slice(0, 1),
                         **boundary)
    dataset = dataset['OA Climatology']['annual'].ix[0]
    dataset.to_hdf('woa09_salinity.h5', 'salinity')

if not os.path.isfile('woa09_temperature.h5'):
    dataset = woa_subset(var='temperature', clim_type='annual',
                         resolution='1deg', levels=slice(0, 1),
                         **boundary)
    dataset = dataset['OA Climatology']['annual'].ix[0]
    dataset.to_hdf('woa09_temperature.h5', 'temperature')

if __name__ == '__main__':
    # Figures options.
    fmt = 'png'
    kfig = dict(format=fmt, transparent=True, dpi=75)
    kcbar = dict(extend='both', shrink=0.5, pad=0.02, fraction=0.1,
                 orientation='horizontal')

    if True:  # Annual Salinity Climatology.
        fig, m = make_map()
        lon, lat, dataset = get_data(fname='woa09_salinity.h5', key='salinity')
        cs = m.pcolormesh(lon, lat, dataset, latlon=True, cmap=cm.odv)
        cs.set_clim(27.5, 37.5)
        fig.colorbar(cs, **kcbar)
        fname = 'surface_salinity_woa09.%s' % fmt
        fig.savefig(fname, **kfig)
        os.system('convert -trim %s %s' % (fname, fname))

        # Latitudinal section.
        fig, ax = latitudinal_section(dataset)
        ax.set_ylabel('Salinidade [g/kg]')
        fname = 'latitudinal_salinity_woa09.%s' % fmt
        fig.savefig(fname, **kfig)
        os.system('convert -trim %s %s' % (fname, fname))

    if True:  # Annual Temperature Climatology.
        fig, m = make_map()
        lon, lat, dataset = get_data(fname='woa09_temperature.h5',
                                     key='temperature')
        cs = m.pcolormesh(lon, lat, dataset, latlon=True, cmap=cm.avhrr)
        cs.set_clim(0, 28)
        fig.colorbar(cs, **kcbar)
        fname = 'surface_temperature_woa09.%s' % fmt
        fig.savefig(fname, **kfig)
        os.system('convert -trim %s %s' % (fname, fname))

        # Latitudinal section.
        fig, ax = latitudinal_section(dataset)
        ax.set_ylabel('Temperatura [%sC]' % u'\u00B0')
        fname = 'latitudinal_temperature_woa09.%s' % fmt
        fig.savefig(fname, **kfig)
        os.system('convert -trim %s %s' % (fname, fname))
