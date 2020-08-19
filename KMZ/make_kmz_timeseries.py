#!/usr/bin/env python3
# -*- coding:utf-8 -*-
####################################################################################
# display velocity and time-series displacement derived by InSAR in Google Earth   #
# Author: Yuan Lei, 2020                                                           #
####################################################################################
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
  python make_kmz_timeseries.py -t ts.txt -o D:\kmz\ts.kmz
  python make_kmz_timeseries.py -t ts.txt -o D:\kmz\ts.kmz -j D:\kmz\dygraph-combined.js
  python make_kmz_timeseries.py -t ts.txt -o D:\kmz\ts.kmz -j D:\kmz\dygraph-combined.js -r 0.5 -s 0.7
"""


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description=
        'Display velocity and time-series displacement derived by InSAR in Google Earth.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)
    parser.add_argument('-t',
                        dest='ts_file',
                        required=True,
                        help='timeseries file for generate KML file')
    parser.add_argument('-o',
                        dest='out_file',
                        required=True,
                        help='output KMZ file(path)')
    parser.add_argument(
        '-j',
        dest='js_file',
        default='dygraph-combined.js',
        help=
        'javascript file for drawing timeseries graph (default: dygraph-combined.js)'
    )
    parser.add_argument(
        '-r',
        dest='rate',
        default=1,
        type=float,
        help='rate of keeping points (default: 1, keep all points)')
    parser.add_argument('-s',
                        dest='scale',
                        default=0.5,
                        type=float,
                        help='scale of point for displaying (default: 0.5)')
    return parser


def get_scale(cb):
    scale = []
    for i in cb.keys():
        scale.append(i.split('~')[0])
        scale.append(i.split('~')[1])
    scale = sorted(list(set(scale)), key=lambda i: float(i))
    return scale


def plot_symbol(cb, dir_name, dpi=12):
    """plot symbol for displaying points"""
    for label, color in cb.items():
        fig, ax = plt.subplots(figsize=(1, 1))
        ax.set_axis_off()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        circle = mpathes.Circle((0.5, 0.5), 0.49, color=color)
        ax.add_patch(circle)
        file_path = os.path.join(dir_name, label + '.png')
        fig.savefig(file_path, transparent=True, dpi=dpi, bbox_inches='tight')
        # plt.show()


def plot_colorbar(cb, dir_name, dpi=100):
    """plot colorbar for display"""
    fig, ax = plt.subplots(figsize=(4, 12))
    ax.set_axis_off()
    ax.set_xlim(0, 1.5)
    ax.set_ylim(0, len(cb.keys()) * 0.5 + 0.5)
    # plt.subplots_adjust(top = 1, bottom = 0.05, right = 0.9, left = 0.1, hspace = 1, wspace = 0)
    y = 0.05
    for color in list(cb.values())[::-1]:
        # circle = mpathes.Circle((0.5, y), 0.3, color=color)
        rect = plt.Rectangle((0, y), 1, 0.45, color=color)
        y += 0.5
        ax.add_patch(rect)
    yy = -0.05
    for i in get_scale(cb):
        ax.text(1.2, yy, i, fontsize=30)
        yy += 0.5
    ax.text(0.15, 0.5 * len(cb.keys()) + 0.2, 'mm/yr', fontsize=30)
    file_path = os.path.join(dir_name, 'colorbar.png')
    fig.savefig(file_path, dpi=dpi, bbox_inches='tight')
    # plt.show()


def load_data(txt):
    """load timeseries data"""
    content = np.loadtxt(txt, np.float64)
    dates = np.asarray(content[0, 4:], np.int64)
    dates = [
        str(d)[0:4] + '-' + str(d)[4:6] + '-' + str(d)[6:8] for d in dates
    ]
    nums = content[1:, 0]
    lons = content[1:, 1]
    lats = content[1:, 2]
    vels = content[1:, 3]
    ts = content[1:, 4:]

    return nums, lons, lats, vels, ts, dates


def random_downsample(nums, lons, lats, vels, ts, rate):
    """downsample data"""
    point_num = lons.shape[0]
    index = random.sample(range(point_num), int(point_num * rate) + 1)
    return nums[index], lons[index], lats[index], vels[index], ts[index, :]


def get_description_string(lon, lat, vel, cum_disp, font_size=4):
    """Description information of each data point."""
    des_str = "<font size={}>".format(font_size)
    des_str += "Longitude: {}˚ <br /> \n".format(lon)
    des_str += "Latitude: {}˚ <br /> \n".format(lat)
    des_str += " <br /> \n"
    des_str += "Mean LOS velocity [mm/year]: {} <br /> \n".format(vel)
    des_str += "Cumulative displacement [mm]: {} <br /> \n".format(cum_disp)
    des_str += "</font>"
    des_str += " <br />  <br /> "
    des_str += "*Double click to reset plot <br /> <br />\n"
    des_str += "\n\n"
    return des_str


def generate_js_datastring(dates, dygraph_file, ts):
    """String of the Java Script for interactive plot of diplacement time-series"""
    dygraph_file = '{}'.format(os.path.basename(dygraph_file))
    js_data_string = "<script type='text/javascript' src='{}'></script>".format(
        dygraph_file)
    js_data_string += """
        <div id='graphdiv'> </div>
        <style>
            .dygraph-legend{
                left: 230px !important;
                width: 265px !important;
            }
        </style>
        <script type='text/javascript'>
            g = new Dygraph( document.getElementById('graphdiv'),
            "Date, displacement\\n" +
    """

    # append the date/displacement data
    num_date = len(dates)
    for k in range(num_date):
        date = dates[k]
        dis = ts[k]
        date_displacement_string = "\"{}, {}\\n\" + \n".format(date, dis)
        js_data_string += date_displacement_string

    js_data_string += """
    
    "",
       {
         width: 500,
         height: 300,
         axes: {
             x: {
                 axisLabelFormatter: function (d, gran) {
                     var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                     var date = new Date(d)
                     var dateString = months[date.getMonth()] + ' ' + date.getFullYear()
                     return dateString;
                 },
                 valueFormatter: function (d) {
                     var date = new Date(d)
                     var dateString = 'Date: ' + ('0' + date.getDate()).slice(-2) + 
                                      '/' + ('0' + (date.getMonth() + 1)).slice(-2) +
                                      '/' + date.getFullYear()
                     return dateString;
                 },
                 pixelsPerLabel: 90
             },
             y: {
                 valueFormatter: function(v) {
                    if(v >= 0){
                        return (' 000' + v.toFixed(2)).slice(-8)
                    }else{
                        return '-'+(' 000' + Math.abs(v).toFixed(2)).slice(-7)
                    }
                 }
             }
         },
         ylabel: 'LOS displacement [mm]',
         yLabelWidth: 18,
         drawPoints: true,
         strokeWidth: 0,
         pointSize: 3,
         highlightCircleSize: 6,
         axisLabelFontSize: 12,
         xRangePad: 30,
         yRangePad: 30,
         hideOverlayOnMouseOut: false,
         panEdgeFraction: 0.0
       });
       </script>
    
    """
    return js_data_string


def write_kml(nums, lons, lats, vels, ts, dates, cb, dygraph_file, scale, out_file):
    """write kml file and unzip files into kmz"""
    # create document
    doc = KML.kml(
        KML.Document(KML.Folder(KML.name(os.path.basename(out_file)))))
    # create icon style
    for label in cb.keys():
        style = KML.Style(KML.IconStyle(KML.Icon(KML.href(label + '.png')),
                                        KML.scale(str(scale))),
                          KML.LabelStyle(KML.color('00000000'),
                                         KML.scale('0.000000')),
                          id=label)
        doc.Document.append(style)
    # create placemark
    for j in range(lons.shape[0]):
        num, lon, lat, vel, disp = nums[j], lons[j], lats[j], vels[j], ts[j, :]
        scale = get_scale(cb)
        for i in range(len(scale) - 1):
            min_vel = int(scale[i])
            max_vel = int(scale[i + 1])
            if vel >= min_vel and vel < max_vel:
                id = f"{min_vel}~{max_vel}"
            elif vel < int(scale[0]):
                id = f"{scale[0]}~{scale[1]}"
            elif vel > int(scale[-1]):
                id = f"{scale[-2]}~{scale[-1]}"
        description = get_description_string(
            lon, lat, vel, disp[-1]) + generate_js_datastring(
                dates, dygraph_file, disp)
        placemark = KML.Placemark(
            KML.name(str(int(num))), KML.description(description),
            KML.styleUrl(f"#{id}"),
            KML.Point(KML.altitudeMode('clampToGround'),
                      KML.coordinates(f"{lon},{lat},{vel}")))
        doc.Document.Folder.append(placemark)
    # create colorbar
    colorbar = KML.ScreenOverlay(
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
    doc.Document.Folder.append(colorbar)
    kml_str = etree.tostring(doc, pretty_print=True)
    # write kml file
    dir_name = os.path.dirname(out_file)
    kml_file = os.path.join(dir_name, 'doc.kml')
    with open(kml_file, 'wb') as f:
        f.write(kml_str)
    # unzip kml, symbol, colorbar, dygraph_file
    with zipfile.ZipFile(out_file, 'w') as f:
        os.chdir(dir_name)
        f.write('doc.kml')
        f.write('colorbar.png')
        for i in cb.keys():
            f.write(i + '.png')
        os.chdir(os.path.dirname(dygraph_file))
        f.write(os.path.basename(dygraph_file))


def del_files(dir_name):
    """delete files(doc.kml symbol colorbar)"""
    for i in cb.keys():
        tmp = os.path.join(dir_name, i + '.png')
        if os.path.isfile(tmp):
            os.remove(tmp)
    for j in ['colorbar.png', 'doc.kml']:
        tmp = os.path.join(dir_name, j)
        if os.path.isfile(tmp):
            os.remove(tmp)


def main():
    # get inputs
    parser = cmdline_parser()
    inps = parser.parse_args()
    ts_file = os.path.abspath(inps.ts_file)
    out_file = os.path.abspath(inps.out_file)
    js_file = os.path.abspath(inps.js_file)
    rate = inps.rate
    scale = inps.scale
    # check ts_file
    if not os.path.isfile(ts_file):
        print("{} doesn't exist.".format(ts_file))
        sys.exit()
    # check js_file
    if not os.path.isfile(js_file):
        print("{} doesn't exist.".format(js_file))
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
    # get lons, lats, vels, ts, dates
    try:
        nums, lons, lats, vels, ts, dates = load_data(ts_file)
        if rate < 1:
            nums, lons, lats, vels, ts = random_downsample(nums, lons, lats, vels, ts, rate)
    except:
        print('error format of {}'.format(ts_file))
        sys.exit()
    # plot symbol
    print('plot symbol...')
    plot_symbol(cb, dir_name, dpi=12)
    print('done.')
    # plot colorbar
    print('plot colorbar...')
    plot_colorbar(cb, dir_name, dpi=100)
    print('done.')
    # write kml and zip all files
    print('write kml...')
    write_kml(nums, lons, lats, vels, ts, dates, cb, js_file, scale, out_file)
    print('done.')
    # delete files
    print('delete files...')
    del_files(dir_name)
    print('done.\n')


if __name__ == "__main__":
    # label and color
    cb_r = {
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
    cb = {
        '50~60': '#0000AA',
        '40~50': '#0000FF',
        '30~40': '#0055FF',
        '20~30': '#00AAFF',
        '10~20': '#00FFFF',
        '0~10': '#008B00',
        '-10~0': '#008B00',
        '-20~-10': '#FFFF00',
        '-30~-20': '#FFAA00',
        '-40~-30': '#FF5500',
        '-50~-40': '#FF0000',
        '-60~-50': '#AA0000',
    }
    main()
