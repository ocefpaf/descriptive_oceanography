# -*- coding: utf-8 -*-
#
# woa09_vertical.py
#
# purpose:  Plot vertical sections from WOA09
# author:   Filipe P. A. Fernandes
# e-mail:   ocefpaf@gmail
# web:      http://ocefpaf.github.io/
# created:  01-Sep-2013
# modified: Wed 04 Sep 2013 05:15:05 PM BRT
#
# obs:
#

import os

import gsw
import numpy as np
import matplotlib.pyplot as plt

from pandas import read_hdf
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from ctd import plot_section
from oceans.colormaps import cm
from oceans.datasets import woa_subset

longitude = 337.5  # -25.5


def plt_cross_section(dataset, cmap=None, levels=0.02):
    levels = np.arange(dataset.min().min(), dataset.max().max(), levels)

    fig, ax, cbar = plot_section(dataset, cmap=cmap, marker=None,
                                 levels=levels)
    X = ax.get_xticks()
    offset = 1.01
    ax.set_xlim(X.min() * offset, X.max() * offset)
    new_labels = np.int_(np.linspace(dataset.lat.min(), dataset.lat.max(),
                                     len(X)))
    new_labels = [u'%s\u00B0' % num for num in new_labels]
    ax.set_xticklabels(new_labels)
    ax.set_ylabel('Profundidade [m]')

    # Global inset map.
    axin = inset_axes(ax, width="40%", height="40%", loc=4)
    inmap = Basemap(projection='ortho', lon_0=longitude, lat_0=0,
                    ax=axin, anchor='NE')
    inmap.bluemarble()
    inmap.plot(dataset.lon, dataset.lat, 'r', latlon=True)
    return fig, ax


def get_data(fname, key):
    dataset = read_hdf(fname, key)
    lat = dataset.columns.values.astype(float)
    depth = dataset.index.values.astype(float)
    lon = len(lat) * [longitude]
    return lon, lat, depth, dataset


if not os.path.isfile('woa09_salinity_at%s.h5' % longitude):
    dataset = woa_subset(var='salinity', clim_type='annual',
                            resolution='1deg', levels=slice(0, 40),
                            llcrnrlat=-70, urcrnrlat=70,
                            llcrnrlon=longitude, urcrnrlon=longitude)
    dataset = dataset['OA Climatology']['annual'].squeeze().T
    dataset.to_hdf('woa09_salinity_at%s.h5' % longitude, 'salinity')


if not os.path.isfile('woa09_temperature_at%s.h5' % longitude):
    dataset = woa_subset(var='temperature', clim_type='annual',
                            resolution='1deg', levels=slice(0, 40),
                            llcrnrlat=-70, urcrnrlat=70,
                            llcrnrlon=longitude, urcrnrlon=longitude)
    dataset = dataset['OA Climatology']['annual'].squeeze().T
    dataset.to_hdf('woa09_temperature_at%s.h5' % longitude, 'temperature')


if __name__ == '__main__':
    fmt = 'png'
    kfig = dict(format=fmt, transparent=True, dpi=75)

    # Atlantic cross section -- Salinity.
    lon, lat, depth, salinity = get_data('woa09_salinity_at337.5.h5',
                                         'salinity')
    salinity.lon, salinity.lat, = lon, lat
    fig, ax = plt_cross_section(salinity, cmap=cm.odv, levels=0.02)
    ax.set_xlabel(u'Seção de Salinidade climatológica (WOA09)'
                  u' no Atlântico (em longitude %3.1f\u00B0)' % longitude)
    fname = 'cross_section_salinity_woa09.%s' % fmt
    fig.savefig(fname, **kfig)
    os.system('convert -trim %s %s' % (fname, fname))

    # Profile.
    fig, ax = salinity[-18.5].plot(label=u'Salinidade Prática (SP)',
                                   linewidth=2, figsize=(5.5, 6))
    if False:  # FIXME.
        SA = gsw.SA_from_SP(salinity[-18.5],
                            temperature.index.values.astype(float),
                            -25.5, -18.5)
    SA = gsw.SR_from_SP(salinity[-18.5])
    ax.plot(SA, salinity.index, linewidth=2,
            label='Salnidade Absoluta (SA')
    ax.grid()
    ax.set_xlabel(u"[g kg$^{-1}$]")
    ax.set_ylabel("Profundidade [m]")
    ax.legend(numpoints=1, loc='lower right')

    fname = 'profile_temperature_woa09.%s' % fmt
    fig.savefig(fname, **kfig)
    os.system('convert -trim %s %s' % (fname, fname))


    # Atlantic cross section -- Temperature.
    lon, lat, depth, temperature = get_data('woa09_temperature_at337.5.h5',
                                            'temperature')
    temperature.lat = lat
    temperature.lon = lon
    fig, ax = plt_cross_section(temperature, cmap=cm.odv, levels=0.1)
    ax.set_xlabel(u'Seção de Temperatura climatológica (WOA09)'
                  u' no Atlântico (em longitude %3.1f\u00B0)' % longitude)
    fname = 'cross_section_temperature_woa09.%s' % fmt
    fig.savefig(fname, **kfig)
    os.system('convert -trim %s %s' % (fname, fname))

    # Profile.
    fig, ax = temperature[-18.5].plot(label='Temperatura in-situ (t)',
                                      linewidth=2,
                                      figsize=(5.5, 6))
    CT = gsw.CT_from_t(salinity[-18.5], temperature[-18.5],
                       temperature.index.values.astype(float))
    ax.plot(CT, temperature.index, linewidth=2,
            label='Temperatura Conservativa ($\Theta$)')
    ax.grid()
    ax.set_xlabel(u"[\u00B0C]")
    ax.set_ylabel("Profundidade [m]")
    ax.legend(numpoints=1, loc='lower right')

    fname = 'profile_temperature_woa09.%s' % fmt
    fig.savefig(fname, **kfig)
    os.system('convert -trim %s %s' % (fname, fname))
