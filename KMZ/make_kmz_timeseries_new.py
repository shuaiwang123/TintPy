#!/usr/bin/env python3
# -*- coding:utf-8 -*-
####################################################################################
# Display velocity and time-series displacement derived by InSAR in Google Earth   #
# Author: Yuan Lei, 2020                                                           #
####################################################################################
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
  python make_kmz_timeseries.py -t ts.txt -o D:\kmz\ts.kmz
  python make_kmz_timeseries.py -t ts.txt -o D:\kmz\ts.kmz -j D:\kmz\dygraph-combined.js
  python make_kmz_timeseries.py -t ts.txt -o D:\kmz\ts.kmz -j D:\kmz\dygraph-combined.js -s 0.7 -f vel
  # Linux
  python3 make_kmz_timeseries.py -t ts.txt -o D:\kmz\ts.kmz
  python3 make_kmz_timeseries.py -t ts.txt -o D:\kmz\ts.kmz -j D:\kmz\dygraph-combined.js
  python3 make_kmz_timeseries.py -t ts.txt -o D:\kmz\ts.kmz -j D:\kmz\dygraph-combined.js -s 0.7 -f disp
  # data format
    -1   -1   -1    -1       date1       date2       date3 ...
  num1 lon1 lat1  vel1 date1-disp1 date2-disp1 date3-disp1 ...
  num2 lon2 lat2  vel2 date1-disp2 date2-disp2 date3-disp2 ...
  num3 lon3 lat3  vel3 date1-disp3 date2-disp3 date3-disp3 ...
  ...
"""


def create_parser():
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
                        help='output KMZ file (path)')
    parser.add_argument(
        '-j',
        dest='js_file',
        default='dygraph-combined.js',
        help=
        'javascript file for drawing timeseries graph (default: dygraph-combined.js)'
    )
    parser.add_argument('-s',
                        dest='scale',
                        default=0.5,
                        type=float,
                        help='scale of point for displaying (default: 0.5)')
    parser.add_argument(
        '-f',
        dest='flag',
        default='vel',
        type=str,
        help=
        'basemap of kmz (default: vel) [velocity(vel) or cumulative displacement(disp)]'
    )
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


def plot_colorbar(colors, bounds, dir_name, dpi, flag):
    """plot colorbar for display"""
    fig, ax = plt.subplots(figsize=(1, 8))
    fig.subplots_adjust(left=0.1, right=0.4)

    cmap = mpl.colors.ListedColormap(colors)
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    if flag == 'vel':
        label = 'mean LOS velocity [mm/yr]'
    else:
        label = 'cumulative LOS displacement [mm]'

    fig.colorbar(mpl.cm.ScalarMappable(cmap=cmap, norm=norm),
                 cax=ax,
                 ticks=bounds,
                 spacing='uniform',
                 orientation='vertical',
                 label=label)
    fig.patch.set_alpha(1)
    colorbar_path = os.path.join(dir_name, 'colorbar.png')
    fig.savefig(colorbar_path, dpi=dpi, bbox_inches='tight')


def load_data(ts_file):
    """load timeseries data"""
    content = np.loadtxt(ts_file, np.float64)
    dates = np.asarray(content[0, 4:], np.int64)
    dates = [
        str(d)[0:4] + '-' + str(d)[4:6] + '-' + str(d)[6:8] for d in dates
    ]

    return content[1:, :], dates


def get_description_string(lon, lat, vel, cum_disp):
    """Description information of each data point."""
    # des_str = "<font size=4>"
    # des_str += "Longitude: {} <br /> \n".format(lon)
    # des_str += "Latitude: {} <br /> \n".format(lat)
    # des_str += " <br /> \n"
    # des_str += "Mean LOS velocity [mm/year]: {} <br /> \n".format(vel)
    # des_str += "Cumulative displacement [mm]: {} <br /> \n".format(cum_disp)
    # des_str += "</font>"
    # des_str += " <br />  <br /> "
    # des_str += "\n\n"
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
    des_str += '<tr bgcolor="#F5F5F5"><td>Cumulative displacement</td><td>{}</td></tr>'.format(
        cum_disp)
    des_str += '</table>'
    des_str += '</body>'
    des_str += '</html>'
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
                     var dateString = 'Date: ' + date.getFullYear() + 
                                      '/' + ('0' + (date.getMonth() + 1)).slice(-2) +
                                      '/' + ('0' + date.getDate()).slice(-2)
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


def check_inps(inps):
    """check input data"""
    ts_file = os.path.abspath(inps.ts_file)
    out_file = os.path.abspath(inps.out_file)
    js_file = os.path.abspath(inps.js_file)
    scale = inps.scale
    flag = inps.flag
    # check ts_file
    if not os.path.isfile(ts_file):
        print("{} doesn't exist".format(ts_file))
        sys.exit()
    # check js_file
    if not os.path.isfile(js_file):
        print("{} doesn't exist".format(js_file))
        sys.exit()
    # check out_file
    if not out_file.endswith('.kmz'):
        out_file += '.kmz'
    dir_name = os.path.dirname(out_file)
    if not os.path.isdir(dir_name):
        print("{} doesn't exist".format(dir_name))
        sys.exit()
    # check scale
    if scale < 0:
        print('scale cannot smaller than 0')
        sys.exit()
    if scale == 0:
        print('scale cannot be equal to 0')
        sys.exit()
    # check flag
    if flag not in ['vel', 'disp']:
        print('flag must be vel or disp')
        sys.exit()

    return ts_file, out_file, js_file, scale, flag


def get_id(d, bounds):
    """get the interval of d"""
    for i in range(len(bounds) - 1):
        min_d = bounds[i]
        max_d = bounds[i + 1]
        if d >= min_d and d < max_d:
            id = f"{min_d}~{max_d}"
        elif d < int(bounds[0]):
            id = f"{bounds[0]}~{bounds[1]}"
        elif d > int(bounds[-1]):
            id = f"{bounds[-2]}~{bounds[-1]}"

    return id


def write_kmz(ts_file,
              out_file,
              js_file,
              scale,
              flag,
              colors,
              bounds,
              symbol_dpi=30,
              colorbar_dpi=300):
    """write kml file and unzip files into kmz"""
    if len(colors) != len(bounds) - 1:
        print('Length of colors plus one must be equal to length of bounds')
        sys.exit()
    print('Writing data to {}'.format(out_file))
    # get lons, lats, vels, ts, dates
    try:
        data, dates = load_data(ts_file)
        nums = data[:, 0]
        lons = data[:, 1]
        lats = data[:, 2]
        vels = data[:, 3]
        ts = data[:, 4:]
    except:
        print('Error format of {}'.format(ts_file))
        sys.exit()
    # create document
    doc = KML.kml(
        KML.Document(KML.Folder(KML.name(os.path.basename(out_file)))))
    # create icon style
    symbol_name = gen_symbol_name(bounds)
    for s in symbol_name:
        style = KML.Style(KML.IconStyle(KML.Icon(KML.href(s + '.png')),
                                        KML.scale(str(scale))),
                          KML.LabelStyle(KML.color('00000000'),
                                         KML.scale('0.000000')),
                          id=s)
        doc.Document.append(style)
    # create placemark
    for j in range(lons.shape[0]):
        num, lon, lat, vel, disp = nums[j], lons[j], lats[j], vels[j], ts[j, :]
        description = get_description_string(
            lon, lat, vel, disp[-1]) + generate_js_datastring(
                dates, js_file, disp)
        if flag == 'vel':
            id = get_id(vel, bounds)
            height = vel
        else:
            id = get_id(disp[-1], bounds)
            height = disp[-1]
        placemark = KML.Placemark(
            KML.name(str(int(num))), KML.description(description),
            KML.styleUrl(f"#{id}"),
            KML.Point(KML.altitudeMode('clampToGround'),
                      KML.coordinates(f"{lon},{lat},{height}")))
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
    plot_colorbar(colors, bounds, dir_name, colorbar_dpi, flag)
    # unzip kml, symbol, colorbar, dygraph_file
    with zipfile.ZipFile(out_file, 'w') as f:
        os.chdir(dir_name)
        f.write('doc.kml')
        os.remove('doc.kml')
        f.write('colorbar.png')
        os.remove('colorbar.png')
        for s in symbol_name:
            f.write(s + '.png')
            os.remove(s + '.png')
        os.chdir(os.path.dirname(js_file))
        f.write(os.path.basename(js_file))
    print('Done, enjoy it!')


if __name__ == "__main__":
    colors = [
        '#AA0000', '#FF0000', '#FF5500', '#FFAA00', '#FFFF00', '#008B00',
        '#008B00', '#00FFFF', '#00AAFF', '#0055FF', '#0000FF', '#0000AA'
    ]
    bounds = sorted(
        [-60, -50, -40, -30, -20, -8.5, 0, 8.5, 20, 30, 40, 50, 60])

    inps = cmdline_parser()
    ts_file, out_file, js_file, scale, flag = check_inps(inps)
    write_kmz(ts_file,
              out_file,
              js_file,
              scale,
              flag,
              colors,
              bounds,
              symbol_dpi=30,
              colorbar_dpi=300)
