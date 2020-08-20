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
    parser.add_argument('-r',
                        dest='reverse_cmap',
                        type=str,
                        default='no',
                        help='reverse color map [yes or no] (default: no)')
    parser.add_argument('-w',
                        dest='rewrap',
                        type=str,
                        default='no',
                        help='rewrap data [yes or no] (default: no)')
    parser.add_argument('-g',
                        dest='rewarp_range',
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


def reverse_colourmap(cmap, name='my_cmap_r'):
    """
    In: 
    cmap, name 
    Out:
    my_cmap_r

    Explanation:
    t[0] goes from 0 to 1
    row i:   x  y0  y1 -> t[0] t[1] t[2]
                   /
                  /
    row i+1: x  y0  y1 -> t[n] t[1] t[2]

    so the inverse should do the same:
    row i+1: x  y1  y0 -> 1-t[0] t[2] t[1]
                   /
                  /
    row i:   x  y1  y0 -> 1-t[n] t[2] t[1]
    """
    reverse = []
    k = []

    for key in cmap._segmentdata:
        k.append(key)
        channel = cmap._segmentdata[key]
        data = []

        for t in channel:
            data.append((1 - t[0], t[2], t[1]))
        reverse.append(sorted(data))

    LinearL = dict(zip(k, reverse))
    my_cmap_r = mpl.colors.LinearSegmentedColormap(name, LinearL)
    return my_cmap_r


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


def display(inps):
    file = os.path.abspath(inps.file)
    ds = gdal.Open(file)
    b = ds.GetRasterBand(inps.band_number)
    data = b.ReadAsArray()
    data = data * inps.scale
    data[data == 0] = np.nan

    if inps.rewrap == 'yes':
        data = rewrap(data, inps.rewarp_range)

    if inps.min is None:
        inps.min = np.nanmin(data)

    if inps.max is None:
        inps.max = np.nanmax(data)

    width, length = b.XSize, b.YSize

    fig = plt.figure(frameon=False)
    ax = plt.Axes(
        fig,
        [0., 0., 1., 1.],
    )
    ax.set_axis_off()
    fig.add_axes(ax)

    cmap = plt.get_cmap(inps.color_map)
    if inps.reverse_cmap == 'yes':
        cmap = reverse_colourmap(cmap)
    cmap.set_bad(alpha=0.0)
    try:
        ax.imshow(data, aspect='auto', vmax=inps.max, vmin=inps.min, cmap=cmap)
    except:
        ax.show(data, aspect='auto', cmap=cmap)
    ax.set_xlim([0, width])
    ax.set_ylim([length, 0])

    fig_name = file + '.png'
    plt.savefig(fig_name, pad_inches=0.0, transparent=True, dpi=inps.dpi)

    pc = plt.figure(figsize=(1.3, 2))
    axc = pc.add_subplot(111)
    cmap = mpl.cm.get_cmap(name=inps.color_map)
    if inps.reverse_cmap == 'yes':
        cmap = reverse_colourmap(cmap)
    norm = mpl.colors.Normalize(vmin=inps.min, vmax=inps.max)
    clb = mpl.colorbar.ColorbarBase(axc,
                                    cmap=cmap,
                                    norm=norm,
                                    orientation='vertical')
    clb.set_label(inps.unit)
    pc.subplots_adjust(left=0.25, bottom=0.1, right=0.4, top=0.9)
    plt.savefig(file + '_colorbar.png', dpi=300)

    return file + '.png', file + '_colorbar.png'


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
        KML.Icon(KML.href(os.path.basename(colorbar_img))),
        KML.overlayXY(
            x="0.0",
            y="1",
            xunits="fraction",
            yunits="fraction",
        ),
        KML.screenXY(
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
        ),
        KML.size(
            x="0",
            y="0.3",
            xunits="fraction",
            yunits="fraction",
        ),
    )

    doc.Folder.append(legend)

    kml_str = etree.tostring(doc, pretty_print=True)
    kml_name = file + '.kml'
    with open(kml_name, 'wb') as f:
        f.write(kml_str)

    kmz_name = file + '.kmz'
    with zipfile.ZipFile(kmz_name, 'w') as f:
        os.chdir(os.path.dirname(file))
        f.write(os.path.basename(kml_name))
        f.write(os.path.basename(file + '.png'))
        f.write(os.path.basename(file + '_colorbar.png'))

    # delete files
    for f in [kml_name, file + '.png', file + '_colorbar.png']:
        if os.path.isfile(f):
            os.remove(f)


def run_kmz():
    inps = cmdline_parser()
    img, colorbar = display(inps)
    write_kmz(img, colorbar, inps)


if __name__ == "__main__":
    run_kmz()
