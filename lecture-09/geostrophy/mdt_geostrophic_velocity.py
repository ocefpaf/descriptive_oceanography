# -*- coding: utf-8 -*-
#
# mdt_geostrophic_velocity.py
#
# purpose:  Compute geostrophic currents using MDT
# author:   Filipe P. A. Fernandes
# e-mail:   ocefpaf@gmail
# web:      http://ocefpaf.github.io/
# created:  26-Sep-2013
# modified: Thu 26 Sep 2013 12:03:24 PM BRT
#
# obs: Need `mdt_cnes_cls2009_global_v1.1.nc`.
#

import iris
import numpy as np
import seawater as sw
import iris.plot as iplt
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cartopy.feature as cfeature

from scipy.spatial import KDTree
from brewer2mpl import brewer2mpl
from oceans.ff_tools.ocfis import uv2spdir, spdir2uv
from oceans.ff_tools import wrap_lon360, wrap_lon180
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

# Colormap.
cmap = brewer2mpl.get_map('RdYlGn', 'diverging', 11, reverse=True).mpl_colormap


def geostrophic_current(ix, lat):
    g = sw.g(lat.mean())
    f = sw.f(lat.mean())
    v = ix * g / f
    return v


def fix_axis(lims, p=0.1):
    """Ajusta eixos + ou - p dos dados par exibir melhor os limites."""
    min = lims.min() * (1 - p) if lims.min() > 0 else lims.min() * (1 + p)
    max = lims.max() * (1 + p) if lims.max() > 0 else lims.max() * (1 - p)
    return min, max


def plot_mdt(mdt, projection=ccrs.PlateCarree(), figsize=(12, 10)):
    """Plota 'Mean Dynamic Topography' no mapa global."""
    fig = plt.figure(figsize=figsize)
    ax = plt.axes(projection=projection)
    ax.add_feature(cfeature.LAND, facecolor='0.75')
    cs = iplt.pcolormesh(mdt, cmap=cmap)
    ax.coastlines()
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1.5,
                      color='gray', alpha=0.5, linestyle='--')
    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    cbar = fig.colorbar(cs, extend='both', orientation='vertical', shrink=0.6)
    cbar.ax.set_title('[m]')
    return fig, ax


def get_position(fig, ax):
    """Escolhe dois pontos para fazer o cálculo."""
    points = np.array(fig.ginput(2))
    lon, lat = points[:, 0], points[:, 1]
    kw = dict(marker='o', markerfacecolor='k', markeredgecolor='w',
              linestyle='none', alpha=0.65, markersize=5)
    ax.plot(lon, lat, transform=ccrs.Geodetic(), **kw)
    ax.set_title('')
    plt.draw()
    return lon, lat


def get_nearest(xi, yi, cube):
    """Encontra os dados mais próximos aos pontos escolhidos."""
    x, y = cube.dim_coords
    X, Y = np.meshgrid(x.points, y.points)
    xi = wrap_lon360(xi)

    tree = KDTree(zip(X.ravel(), Y.ravel()))
    dist, indices = tree.query(np.array([xi, yi]).T)
    indices = np.unravel_index(indices, X.shape)
    lon = X[indices]
    lat = Y[indices]

    maskx = np.logical_and(x.points >= min(lon), x.points <= max(lon))
    masky = np.logical_and(y.points >= min(lat), y.points <= max(lat))
    maxnp = len(np.nonzero(maskx)[0]) + len(np.nonzero(masky)[0])

    lons = np.linspace(lon[0], lon[1], maxnp)
    lats = np.linspace(lat[0], lat[1], maxnp)

    # Find all x, y, data in that line using the same KDTree obj.
    dist, indices = tree.query(np.array([lons, lats]).T)
    indices = np.unique(indices)
    indices = np.unravel_index(indices, X.shape)

    lons, lats = X[indices], Y[indices]
    elvs = cube.data.T[indices]

    dist, angle = sw.dist(lats, lons, 'km')
    dist *= 1e3
    dist = np.r_[0, dist.cumsum()]
    return (lons, lats), (elvs, dist, angle)


def mid_point(arr):
    return (arr[1:] + arr[:-1]) / 2

cube = iris.load_cube('mdt_cnes_cls2009_global_v1.1.nc',
                      iris.Constraint('Mean Dynamic Topography'))

# Data clean-up.
data = cube.data.filled(fill_value=np.NaN).copy()
data[data == 9999.0] = np.NaN
data = np.ma.masked_invalid(data)
cube.data = data

if __name__ == '__main__':
    fig, ax = plot_mdt(cube, projection=ccrs.PlateCarree(), figsize=(12, 10))
    _ = ax.set_title('Escolha dois pontos.')

    lon, lat = get_position(fig, ax)
    print('Longitude: %s\nLatitude: %s' % (lon, lat))

    fig, ax = plot_mdt(cube, projection=ccrs.PlateCarree(), figsize=(8, 6))
    kw = dict(marker='o', markerfacecolor='k', markeredgecolor='w',
              linestyle='none', alpha=0.65, markersize=5)
    _ = ax.plot(lon, lat, transform=ccrs.PlateCarree(), **kw)

    (lons, lats), (elvs, dist, angle) = get_nearest(lon, lat, cube)
    ix = np.diff(elvs) / np.diff(dist)
    v = geostrophic_current(ix, lats.mean())
    maxi = ix == ix.max()
    dist *= 1e-3

    fig, ax = plt.subplots(figsize=(10, 2))
    fig.subplots_adjust(bottom=0.25)
    ax.plot(dist, elvs)
    ax.axis('tight')
    ax.set_ylabel('Height [m]')
    ax.set_xlabel('Distance [km]')
    ax.set_title('Sea Surface Slope')
    vmax = v.max() if v.max() > np.abs(v.min()) else v.min()
    symbol = r'$\bigotimes$' if vmax > 0 else r'$\bigodot$'
    _ = ax.text(dist[maxi], elvs[maxi], symbol, va='center', ha='center')

    arrowprops = dict(rrowstyle="->", alpha=0.65,
                      connectionstyle="angle3,angleA=0,angleB=-90")
    _ = ax.annotate(r'%2.2f m s$^{-1}$' % vmax, xy=(dist[maxi], elvs[maxi]),
                    xycoords='data', xytext=(-50, 30),
                    textcoords='offset points',
                    arrowprops=arrowprops)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_title('Jet profile')
    ax.set_xlabel('Distance [m]')
    ax.set_ylabel(r'Velocity [m $^{-1}$]')
    xm = mid_point(dist)
    xm *= 1e-3
    kw = dict(scale_units='xy', angles='xy', scale=1)
    qk = ax.quiver(xm, [0]*len(xm), [0]*len(v), v, **kw)
    _ = ax.set_ylim(fix_axis(v))
    _ = ax.set_xlim(fix_axis(xm))

    rot = 180 - np.abs(angle.mean())  # FIXME!
    ang, spd = uv2spdir(0, v, rot=rot)
    ui, vi = spdir2uv(spd, ang, deg=False)

    dx = dy = 10
    lon = wrap_lon360(lon)
    xmin, xmax = map(int, [lon[0]-dx, lon[1]+dx])
    ymin, ymax = map(int, (lat[0]-dy, lat[1]+dy))
    coord_values = {'latitude': lambda cell: ymin <= cell <= ymax,
                    'longitude': lambda cell: xmin <= cell <= xmax}
    cube = iris.load_cube('mdt_cnes_cls2009_global_v1.1.nc',
                          iris.Constraint(name='Mean Dynamic Topography',
                                          coord_values=coord_values))

    kw = dict(marker='o', markeredgecolor='w',
              linestyle='none', alpha=0.65, markersize=5)

    fig, ax = plot_mdt(cube, projection=ccrs.PlateCarree(), figsize=(10, 10))
    ax.plot(lons, lats, transform=ccrs.PlateCarree(),
            markerfacecolor='r', **kw)
    ax.plot(lon, lat, transform=ccrs.PlateCarree(),
            markerfacecolor='k', **kw)
    x, y = map(mid_point, (lons, lats))
    kw = dict(color='k', units='inches', alpha=0.65)
    Q = ax.quiver(x, y, ui, vi, transform=ccrs.PlateCarree(), **kw)
    ax.axis([wrap_lon180(xmin), wrap_lon180(xmax), ymin, ymax])
    qk = ax.quiverkey(Q, 0.5, 0.05, 0.5, r'0.5 m s${-1}$',
                      fontproperties={'weight': 'bold'})
