#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#######################################################
# Display velocity derived by InSAR in Google Earth   #
# Author: Yuan Lei, 2020                              #
#######################################################
import argparse
import os
import random
import sys
import zipfile

import matplotlib as mpl
import matplotlib.patches as mpathes
import matplotlib.pyplot as plt
import numpy as np
from lxml import etree
from pykml.factory import KML_ElementMaker as KML

EXAMPLE = r"""Example:
  # Windows
  python make_kmz.py -v vels.txt -o D:\kmz\vels.kmz
  python make_kmz.py -v vels.txt -o D:\kmz\vels.kmz -r 0.5
  python make_kmz.py -v vels.txt -o D:\kmz\vels.kmz -r 0.5 -s 0.5
  # Linux
  python3 make_kmz.py -v vels.txt -o D:\kmz\vels.kmz
  python3 make_kmz.py -v vels.txt -o D:\kmz\vels.kmz -r 0.5
  python3 make_kmz.py -v vels.txt -o D:\kmz\vels.kmz -r 0.5 -s 0.5
  # data format
  num1 lon1 lat1 vel1
  num2 lon2 lat2 vel2
  num3 lon3 lat3 vel3
  ...
"""


def create_parser():
    parser = argparse.ArgumentParser(
        description='Display velocity derived by InSAR in Google Earth.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)
    parser.add_argument('-v',
                        dest='vel_file',
                        required=True,
                        help='velocity file for generate KML file')
    parser.add_argument('-o',
                        dest='out_file',
                        required=True,
                        help='output KMZ file (path)')
    parser.add_argument(
        '-r',
        dest='rate',
        default=1,
        type=float,
        help=
        'rate of keeping points (default: 1, keep all points) [random downsample]'
    )
    parser.add_argument('-s',
                        dest='scale',
                        default=0.5,
                        type=float,
                        help='scale of point for displaying (default: 0.5)')
    return parser


def cmdline_parser():
    parser = create_parser()
    inps = parser.parse_args()
    return inps


def gen_symbol_name(bounds):
    """generate symbol names"""
    names = []
    for i in range(len(bounds) - 1):
        names.append(f"{bounds[i]}~{bounds[i+1]}")
    return names


def plot_symbol(colors, bounds, dir_name, dpi):
    """plot symbol for displaying points"""
    symbol_name = gen_symbol_name(bounds)
    for i in range(len(colors)):
        fig, ax = plt.subplots(figsize=(1, 1))
        ax.set_axis_off()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        circle = mpathes.Circle((0.5, 0.5), 0.49, color=colors[i])
        ax.add_patch(circle)
        symbol_path = os.path.join(dir_name, f"{symbol_name[i]}.png")
        fig.savefig(symbol_path,
                    transparent=True,
                    dpi=dpi,
                    bbox_inches='tight')


def plot_colorbar(colors, bounds, dir_name, dpi):
    """plot colorbar for display"""
    fig, ax = plt.subplots(figsize=(1, 8))
    fig.subplots_adjust(left=0.1, right=0.4)

    cmap = mpl.colors.ListedColormap(colors)
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    fig.colorbar(mpl.cm.ScalarMappable(cmap=cmap, norm=norm),
                 cax=ax,
                 ticks=bounds,
                 spacing='uniform',
                 orientation='vertical',
                 label='mm/yr')
    fig.patch.set_alpha(1)
    colorbar_path = os.path.join(dir_name, 'colorbar.png')
    fig.savefig(colorbar_path, dpi=dpi, bbox_inches='tight')


def load_data(vel_file):
    """load velocity data"""
    content = np.loadtxt(vel_file, np.float64)
    nums = content[:, 0]
    lons = content[:, 1]
    lats = content[:, 2]
    vels = content[:, 3]

    return nums, lons, lats, vels


def random_downsample(nums, lons, lats, vels, rate):
    """downsample data"""
    point_num = lons.shape[0]
    index = random.sample(range(point_num), int(point_num * rate) + 1)
    return nums[index], lons[index], lats[index], vels[index]


def get_description_string(lon, lat, vel):
    """Description information of each data point."""
    # des_str = "<font size={}>".format(font_size)
    # des_str += "Longitude: {} <br /> \n".format(lon)
    # des_str += "Latitude: {} <br /> \n".format(lat)
    # des_str += "Mean LOS velocity [mm/year]: {} <br /> \n".format(vel)
    # des_str += "</font>"
    # return des_str
    des_str = '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">'
    des_str += '<head>'
    des_str += '<META http-equiv="Content-Type" content="text/html">'
    des_str += '<meta http-equiv="content-type" content="text/html; charset=UTF-8">'
    des_str += '<style>td{padding:5px;}</style>'
    des_str += '</head>'
    des_str += '<body style="margin:0px 0px 0px 0px;overflow:auto;background:#FFFFFF;">'
    des_str += '<table style="font-family:Arial,Verdana,Times;font-size:12px;text-align:left;\
        width:100%;border-spacing:1px;padding:3px 3px 3px 3px;">'

    des_str += '<tr bgcolor="#F5F5F5"><td>Longitude</td><td>{}</td></tr>'.format(
        lon)
    des_str += '<tr bgcolor="#F5F5F5"><td>Latitude</td><td>{}</td></tr>'.format(
        lat)
    des_str += '<tr bgcolor="#F5F5F5"><td>Mean LOS velocity</td><td>{}</td></tr>'.format(
        vel)
    des_str += '</table>'
    des_str += '</body>'
    des_str += '</html>'
    return des_str


def check_inps(inps):
    """check input data"""
    vel_file = os.path.abspath(inps.vel_file)
    out_file = os.path.abspath(inps.out_file)
    rate = inps.rate
    scale = inps.scale
    # check vel_file
    if not os.path.isfile(vel_file):
        print("{} doesn't exist.".format(vel_file))
        sys.exit()
    # check out_file
    if not out_file.endswith('.kmz'):
        out_file += '.kmz'
    dir_name = os.path.dirname(out_file)
    if not os.path.isdir(dir_name):
        print("{} doesn't exist.".format(dir_name))
        sys.exit()
    # check rate
    if rate < 0:
        print('rate cannot smaller than 0.')
        sys.exit()
    if rate > 1:
        rate = 1
    # check scale
    if scale < 0:
        print('scale cannot smaller than 0.')
        sys.exit()
    if scale == 0:
        print('scale cannot be equal to 0.')
        sys.exit()

    return vel_file, out_file, rate, scale


def write_kmz(vel_file,
              out_file,
              rate,
              scale,
              colors,
              bounds,
              symbol_dpi=30,
              colorbar_dpi=300):
    """write kml file and unzip files into kmz"""
    if len(colors) != len(bounds) - 1:
        print('length of colors must be equal to length of bounds plus one.')
        sys.exit()
    print('Writing data {}'.format(out_file))
    # get nums, lons, lats, vels
    try:
        nums, lons, lats, vels = load_data(vel_file)
        if rate < 1:
            nums, lons, lats, vels = random_downsample(nums, lons, lats, vels,
                                                       rate)
    except:
        print('error format of {}'.format(vel_file))
        sys.exit()
    # create document
    doc = KML.kml(
        KML.Document(KML.Folder(KML.name(os.path.basename(out_file)))))
    # create icon style
    symbol_name = gen_symbol_name(bounds)
    for s in symbol_name:
        style = KML.Style(KML.IconStyle(
            KML.Icon(KML.href(s + '.png')),
            KML.scale(str(scale))),
                          KML.LabelStyle(KML.color('00000000'),
                                         KML.scale('0.000000')),
                          id=s)
        doc.Document.append(style)
    # create placemark
    for num, lon, lat, vel in zip(nums, lons, lats, vels):
        for i in range(len(bounds) - 1):
            min_vel = int(bounds[i])
            max_vel = int(bounds[i + 1])
            if vel >= min_vel and vel < max_vel:
                id = f"{min_vel}~{max_vel}"
            elif vel < int(bounds[0]):
                id = f"{bounds[0]}~{bounds[1]}"
            elif vel > int(bounds[-1]):
                id = f"{bounds[-2]}~{bounds[-1]}"
        description = get_description_string(lon, lat, vel)
        placemark = KML.Placemark(
            KML.name(str(int(num))), KML.description(description),
            KML.styleUrl(f"#{id}"),
            KML.Point(KML.altitudeMode('clampToGround'),
                      KML.coordinates(f"{lon},{lat},{vel}")))
        doc.Document.Folder.append(placemark)
    # create legend
    legend = KML.ScreenOverlay(
        KML.name('colorbar'),
        KML.Icon(KML.href('colorbar.png')),
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
            x="0.05",
            y="0.5",
            xunits="fraction",
            yunits="fraction",
        ),
    )
    doc.Document.Folder.append(legend)
    kml_str = etree.tostring(doc, pretty_print=True)
    # write kml file
    dir_name = os.path.dirname(out_file)
    kml_file = os.path.join(dir_name, 'doc.kml')
    with open(kml_file, 'wb') as f:
        f.write(kml_str)
    # plot symbol
    plot_symbol(colors, bounds, dir_name, symbol_dpi)
    # plot colorbar
    plot_colorbar(colors, bounds, dir_name, colorbar_dpi)
    # unzip kml, symbol, colorbar, dygraph_file
    with zipfile.ZipFile(out_file, 'w') as f:
        os.chdir(dir_name)
        f.write('doc.kml')
        os.remove('doc.kml')
        f.write('colorbar.png')
        os.remove('colorbar.png')
        for s in symbol_name:
            f.write(f"{s}.png")
            os.remove(f"{s}.png")
    print('Done, enjoy it!')


if __name__ == "__main__":

    colors = [
        '#AA0000', '#FF0000', '#FF5500', '#FFAA00', '#FFFF00', '#008B00',
        '#008B00', '#00FFFF', '#00AAFF', '#0055FF', '#0000FF', '#0000AA'
    ]
    bounds = sorted([-60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60])

    inps = cmdline_parser()
    vel_file, out_file, rate, scale = check_inps(inps)
    write_kmz(vel_file,
              out_file,
              rate,
              scale,
              colors,
              bounds,
              symbol_dpi=30,
              colorbar_dpi=300)
