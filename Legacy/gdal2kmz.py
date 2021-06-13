#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#####################################################
# Convert data supported by gdal to KMZ for display #
# Author: Yuan Lei, 2020                            #
#####################################################

import argparse
import os
import zipfile

import gdal
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from lxml import etree
from pykml.factory import KML_ElementMaker as KML

mpl.use('Agg')

EXAMPLE = r"""Example:
  # Windows
  python gdal2kmz.py -f 20200202_disp
  python gdal2kmz.py -f 20200202_disp -m -3 -M 3 -c rainnbow -u mm
  # Ubuntu
  python3 gdal2kmz.py -f 20200202_disp
  python3 gdal2kmz.py -f 20200202_disp -c rainnbow -u mm -s 100 -w yes -g 4 
"""


def create_parser():
    parser = argparse.ArgumentParser(
        description='Convert file supported by gdal to KMZ for display.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)
    parser.add_argument('-f',
                        dest='file',
                        type=str,
                        required=True,
                        help='file used to make kmz')
    parser.add_argument('-m',
                        dest='min',
                        type=float,
                        default=None,
                        help='minimun value of colorscale')
    parser.add_argument('-M',
                        dest='max',
                        type=float,
                        default=None,
                        help='maximun value of colorscale')
    parser.add_argument('-d',
                        dest='dpi',
                        type=int,
                        default=300,
                        help='dpi of the png image (default: 300)')
    parser.add_argument('-c',
                        dest='color_map',
                        type=str,
                        default='jet',
                        help='masplotlib colormap (default: jet)')
    parser.add_argument('-u',
                        dest='unit',
                        default='',
                        help='unit in whick data is displayed')
    parser.add_argument(
        '-s',
        dest='scale',
        type=float,
        default=1.0,
        help='scale factor to scale the data before display (default: 1.0)')
    parser.add_argument('-w',
                        dest='rewrap',
                        type=str,
                        default='no',
                        help='rewrap data [yes or no] (default: no)')
    parser.add_argument('-g',
                        dest='rewrap_range',
                        default=3.14,
                        type=float,
                        help='range to rewrap data (default: 3.14)')
    parser.add_argument(
        '-n',
        dest='band_number',
        type=int,
        default=1,
        help='band number if multiple bands exist (default: 1)')
    return parser


def cmdline_parser():
    parser = create_parser()
    inps = parser.parse_args()
    return inps


def get_lon_lat(file):
    ds = gdal.Open(file)
    b = ds.GetRasterBand(1)

    width, length = b.XSize, b.YSize

    min_lon = ds.GetGeoTransform()[0]
    delta_lon = ds.GetGeoTransform()[1]
    max_lon = min_lon + width * delta_lon

    max_lat = ds.GetGeoTransform()[3]
    delta_lat = ds.GetGeoTransform()[5]
    min_lat = max_lat + length * delta_lat

    return min_lat, max_lat, min_lon, max_lon


def rewrap(data, re_range):
    re_range = abs(re_range)
    rewrapped = data - np.round(data / (2 * re_range)) * 2 * re_range
    return rewrapped


def plot_colorbar(inps, figsize=(0.18, 3.6), nbins=7):
    img_file = os.path.abspath(inps.file)
    vmin = inps.min
    vmax = inps.max
    cmap = inps.color_map
    out_file = img_file + '_colorbar.png'
    fig, cax = plt.subplots(figsize=figsize)
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.get_cmap(cmap)
    cbar = mpl.colorbar.ColorbarBase(cax,
                                     cmap=cmap,
                                     norm=norm,
                                     orientation='vertical')
    if inps.unit:
        cbar.set_label(inps.unit, fontsize=12)
    cbar.locator = mpl.ticker.MaxNLocator(nbins=nbins)
    cbar.update_ticks()
    cbar.ax.tick_params(which='both', labelsize=12)
    fig.patch.set_facecolor('white')
    fig.patch.set_alpha(0.7)
    fig.savefig(out_file,
                bbox_inches='tight',
                facecolor=fig.get_facecolor(),
                dpi=300)

    return out_file


def plot_img(inps):
    img_file = os.path.abspath(inps.file)
    out_file = img_file + '.png'
    ds = gdal.Open(img_file)
    b = ds.GetRasterBand(inps.band_number)
    data = b.ReadAsArray()
    data = data * inps.scale
    data[data == 0] = np.nan

    if inps.rewrap == 'yes':
        data = rewrap(data, inps.rewrap_range)

    if inps.min is None:
        inps.min = np.nanmin(data)

    if inps.max is None:
        inps.max = np.nanmax(data)

    fig = plt.figure(frameon=False)
    ax = fig.add_axes([0., 0., 1., 1.])
    ax.set_axis_off()
    cmap = plt.get_cmap(inps.color_map)

    ax.imshow(data, aspect='auto', vmax=inps.max, vmin=inps.min, cmap=cmap)
    ax.set_xlim([0, b.XSize])
    ax.set_ylim([b.YSize, 0])
    fig.savefig(out_file,
                pad_inches=0.0,
                transparent=True,
                interpolation='nearest',
                dpi=inps.dpi)

    return out_file


def write_kmz(img, colorbar_img, inps):
    file = os.path.abspath(inps.file)
    south, north, west, east = get_lon_lat(file)

    doc = KML.kml(KML.Folder(KML.name(os.path.basename(file))))
    img_displayed = KML.GroundOverlay(
        KML.name(os.path.basename(img)),
        KML.Icon(KML.href(os.path.basename(img))),
        KML.LatLonBox(KML.north(str(north)), KML.south(str(south)),
                      KML.east(str(east)), KML.west(str(west))))
    doc.Folder.append(img_displayed)

    legend = KML.ScreenOverlay(
        KML.name('colorbar'),
        KML.Icon(KML.href(os.path.basename(colorbar_img)),
                 KML.viewBoundScale(0.75)),
        KML.overlayXY(
            x="0.0",
            y="1",
            xunits="fraction",
            yunits="fraction",
        ), KML.screenXY(
            x="0.0",
            y="1",
            xunits="fraction",
            yunits="fraction",
        ),
        KML.rotationXY(
            x="0.",
            y="1.",
            xunits="fraction",
            yunits="fraction",
        ), KML.size(
            x="0",
            y="250",
            xunits="pixel",
            yunits="pixel",
        ), KML.visibility(1), KML.open(0))

    doc.Folder.append(legend)

    kml_str = etree.tostring(doc, pretty_print=True)
    kml_name = file + '.kml'
    with open(kml_name, 'wb') as f:
        f.write(kml_str)

    kmz_name = file + '.kmz'
    with zipfile.ZipFile(kmz_name, 'w') as f:
        os.chdir(os.path.dirname(file))
        f.write(os.path.basename(kml_name))
        os.remove(os.path.basename(kml_name))
        f.write(os.path.basename(file + '.png'))
        os.remove(os.path.basename(file + '.png'))
        f.write(os.path.basename(file + '_colorbar.png'))
        os.remove(os.path.basename(file + '_colorbar.png'))


def run_kmz():
    inps = cmdline_parser()
    print('writing kmz')
    img = plot_img(inps)
    colorbar = plot_colorbar(inps)
    write_kmz(img, colorbar, inps)
    print('done')


if __name__ == "__main__":
    run_kmz()
