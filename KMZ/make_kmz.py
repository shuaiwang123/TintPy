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


def cmdline_parser():
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


def get_cutoff_vel(colorbar):
    """get cutoff velocity"""
    cutoff_vel = []
    for i in colorbar.keys():
        cutoff_vel.append(i.split('~')[0])
        cutoff_vel.append(i.split('~')[1])
    cutoff_vel = sorted(list(set(cutoff_vel)), key=lambda i: float(i))
    return cutoff_vel


def plot_symbol(colorbar, dir_name, dpi):
    """plot symbol for displaying points"""
    for label, color in colorbar.items():
        fig, ax = plt.subplots(figsize=(1, 1))
        ax.set_axis_off()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        circle = mpathes.Circle((0.5, 0.5), 0.49, color=color)
        ax.add_patch(circle)
        file_path = os.path.join(dir_name, label + '.png')
        fig.savefig(file_path, transparent=True, dpi=dpi, bbox_inches='tight')


def plot_colorbar(colorbar, dir_name, dpi):
    """plot colorbar for display"""
    fig, ax = plt.subplots(figsize=(4, 12))
    ax.set_axis_off()
    ax.set_xlim(0, 1.5)
    ax.set_ylim(0, len(colorbar.keys()) * 0.5 + 0.5)
    y = 0.05
    for color in list(colorbar.values())[::-1]:
        rect = plt.Rectangle((0, y), 1, 0.45, color=color)
        y += 0.5
        ax.add_patch(rect)
    yy = -0.05
    for i in get_cutoff_vel(colorbar):
        ax.text(1.2, yy, i, fontsize=30)
        yy += 0.5
    ax.text(0.15, 0.5 * len(colorbar.keys()) + 0.2, 'mm/yr', fontsize=30)
    file_path = os.path.join(dir_name, 'colorbar.png')
    fig.savefig(file_path, dpi=dpi, bbox_inches='tight')


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


def get_description_string(lon, lat, vel, font_size=4):
    """Description information of each data point."""
    des_str = "<font size={}>".format(font_size)
    des_str += "Longitude: {} <br /> \n".format(lon)
    des_str += "Latitude: {} <br /> \n".format(lat)
    des_str += "Mean LOS velocity [mm/year]: {} <br /> \n".format(vel)
    des_str += "</font>"
    return des_str


def del_files(dir_name):
    """delete files(doc.kml symbol colorbar)"""
    for i in colorbar.keys():
        tmp = os.path.join(dir_name, i + '.png')
        if os.path.isfile(tmp):
            os.remove(tmp)
    for j in ['colorbar.png', 'doc.kml']:
        tmp = os.path.join(dir_name, j)
        if os.path.isfile(tmp):
            os.remove(tmp)


def write_kmz(colorbar, symbol_dpi=12, colorbar_dpi=200):
    """write kml file and unzip files into kmz"""
    # create parser
    parser = cmdline_parser()
    inps = parser.parse_args()
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
    dir_name = os.path.dirname(os.path.abspath(out_file))
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
        print('scale cannot be equal 0.')
        sys.exit()
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
    for label in colorbar.keys():
        style = KML.Style(KML.IconStyle(KML.Icon(KML.href(label + '.png')),
                                        KML.scale(str(scale))),
                          KML.LabelStyle(KML.color('00000000'),
                                         KML.scale('0.000000')),
                          id=label)
        doc.Document.append(style)
    # create placemark
    for num, lon, lat, vel in zip(nums, lons, lats, vels):
        cutoff_vel = get_cutoff_vel(colorbar)
        for i in range(len(cutoff_vel) - 1):
            min_vel = int(cutoff_vel[i])
            max_vel = int(cutoff_vel[i + 1])
            if vel >= min_vel and vel < max_vel:
                id = f"{min_vel}~{max_vel}"
            elif vel < int(cutoff_vel[0]):
                id = f"{cutoff_vel[0]}~{cutoff_vel[1]}"
            elif vel > int(cutoff_vel[-1]):
                id = f"{cutoff_vel[-2]}~{cutoff_vel[-1]}"
        description = get_description_string(lon, lat, vel, font_size=4)
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
            x="0",
            y="0.4",
            xunits="fraction",
            yunits="fraction",
        ),
    )
    doc.Document.Folder.append(legend)
    kml_str = etree.tostring(doc, pretty_print=True)
    # write kml file
    print('writing kmz')
    dir_name = os.path.dirname(out_file)
    kml_file = os.path.join(dir_name, 'doc.kml')
    with open(kml_file, 'wb') as f:
        f.write(kml_str)
    # plot symbol
    plot_symbol(colorbar, dir_name, dpi=symbol_dpi)
    # plot colorbar
    plot_colorbar(colorbar, dir_name, dpi=colorbar_dpi)
    # unzip kml, symbol, colorbar, dygraph_file
    with zipfile.ZipFile(out_file, 'w') as f:
        os.chdir(dir_name)
        f.write('doc.kml')
        f.write('colorbar.png')
        for i in colorbar.keys():
            f.write(i + '.png')
    # delete files
    del_files(dir_name)
    print('done')


if __name__ == "__main__":
    # colorbar for display points
    colorbar_r = {
        '50~60': '#AA0000',
        '40~50': '#FF0000',
        '30~40': '#FF5500',
        '20~30': '#FFAA00',
        '10~20': '#FFFF00',
        '0~10': '#008B00',
        '-10~0': '#008B00',
        '-20~-10': '#00FFFF',
        '-30~-20': '#00AAFF',
        '-40~-30': '#0055FF',
        '-50~-40': '#0000FF',
        '-60~-50': '#0000AA',
    }
    colorbar = {
        '50~60': '#0000AA',
        '40~50': '#0000FF',
        '30~40': '#0055FF',
        '20~30': '#00AAFF',
        '9~20': '#00FFFF',
        '0~9': '#008B00',
        '-9~0': '#008B00',
        '-20~-9': '#FFFF00',
        '-30~-20': '#FFAA00',
        '-40~-30': '#FF5500',
        '-50~-40': '#FF0000',
        '-60~-50': '#AA0000',
    }
    write_kmz(colorbar, symbol_dpi=30, colorbar_dpi=200)
