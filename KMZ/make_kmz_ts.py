#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################################################################
# Display velocity (or cumulative displacement) and time-series displacement derived by InSAR in Google Earth  #
# Author: Yuan Lei, 2020                                                                                       #
################################################################################################################
import argparse
import os
import sys
import zipfile

import matplotlib as mpl
import matplotlib.patches as mpathes
import matplotlib.pyplot as plt
import numpy as np
from lxml import etree
from pykml.factory import KML_ElementMaker as KML

EXAMPLE = r"""Example:
  python3 make_kmz_ts.py ts.txt /home/ly/ts
  python3 make_kmz_ts.py ts.txt /home/ly/ts -j /home/ly/tsdygraph-combined.js
  python3 make_kmz_ts.py ts.txt /home/ly/ts -j /home/ly/tsdygraph-combined.js -s 0.6 -f disp -n f -l 100 101 31 32
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
        'Display velocity (or cumulative displacement) and time-series displacement derived by InSAR in Google Earth.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)
    parser.add_argument('ts_file',
                        help='timeseries file for generating KMZ file')
    parser.add_argument('out_file',
                        help='output KMZ file')
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
                        help='scale of point for display (default: 0.5)')
    parser.add_argument(
        '-f',
        dest='display_flag',
        default='vel',
        type=str,
        help=
        'basemap of kmz (default: vel) [velocity(vel) or cumulative displacement(disp)]'
    )
    parser.add_argument(
        '-n',
        dest='number_flag',
        default='t',
        help='first column of data is point number [t] or not [f] (default: t)'
    )
    parser.add_argument(
        '-l',
        dest='lonlat',
        default=(-180, 180, -90, 90),
        type=float,
        nargs=4,
        help=
        'longitude and latitude (W E S N) of points for display [default: all points]'
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


def plot_colorbar(colors, bounds, dir_name, dpi, display_flag):
    """plot colorbar for display"""
    fig, ax = plt.subplots(figsize=(1, 8))
    fig.subplots_adjust(left=0.1, right=0.4)

    cmap = mpl.colors.ListedColormap(colors)
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    if display_flag == 'vel':
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


def filter_data(lon_data, lat_data, lonlat):
    lon_min, lon_max, lat_min, lat_max = lonlat
    lon_index = ((lon_data > lon_min) == (lon_data < lon_max))
    lat_index = ((lat_data > lat_min) == (lat_data < lat_max))
    index = (lon_index & lat_index)

    return index


def load_data(ts_file, number_flag, lonlat):
    """load timeseries data"""
    content = np.loadtxt(ts_file, np.float64)
    # add points number
    if number_flag == 'f':
        number = np.arange(-1, content.shape[0] - 1)
        content = np.hstack((number.reshape(-1, 1), content))
    # get dates
    dates = np.asarray(content[0, 4:], np.int64)
    dates = [
        str(d)[0:4] + '-' + str(d)[4:6] + '-' + str(d)[6:8] for d in dates
    ]
    # filte data
    lon_data = content[1:, 1]
    lat_data = content[1:, 2]
    index = filter_data(lon_data, lat_data, lonlat)
    filted_data = content[1:, :][index, :]

    return filted_data, dates


def get_description_string(lon, lat, vel, cum_disp):
    """Description information of each data point."""
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
                    return v.toFixed(2)
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
    display_flag = inps.display_flag
    number_flag = inps.number_flag.lower()
    lonlat = inps.lonlat
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
    if scale <= 0:
        print('scale cannot less than or equal to 0')
        sys.exit()
    # check display_flag
    if display_flag not in ['vel', 'disp']:
        print('display_flag must be vel or disp')
        sys.exit()
    # check number_flag
    if number_flag not in ['t', 'f']:
        print(
            "Error number_flag, first column of data is point number [t] or not [f] (default: t)"
        )
        sys.exit()
    # check lonlat
    lon_min, lon_max, lat_min, lat_max = lonlat
    if lon_min >= lon_max:
        print('Error lonlat, {} {}'.format(lon_min, lon_max))
        sys.exit(1)
    if lat_min >= lat_max:
        print('Error lonlat, {} {}'.format(lat_min, lat_max))
        sys.exit(1)

    return ts_file, out_file, js_file, scale, display_flag, number_flag, lonlat


def get_id(d, bounds):
    """get the interval of d"""
    for i in range(len(bounds) - 1):
        min_d = bounds[i]
        max_d = bounds[i + 1]
        if d >= min_d and d < max_d:
            id = f"{min_d}~{max_d}"
        elif d < bounds[0]:
            id = f"{bounds[0]}~{bounds[1]}"
        elif d > bounds[-1]:
            id = f"{bounds[-2]}~{bounds[-1]}"

    return id


def write_kmz(ts_file,
              out_file,
              js_file,
              scale,
              display_flag,
              number_flag,
              lonlat,
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
        data, dates = load_data(ts_file, number_flag, lonlat)
        nums = data[:, 0]
        lons = data[:, 1]
        lats = data[:, 2]
        vels = data[:, 3]
        ts = data[:, 4:]
    except Exception:
        print('Error format of {}'.format(ts_file))
        sys.exit()
    # create document
    doc = KML.kml(
        KML.Document(KML.Folder(KML.name(os.path.basename(out_file[:-4])))))
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
        if display_flag == 'vel':
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
    plot_colorbar(colors, bounds, dir_name, colorbar_dpi, display_flag)
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
        '#FF2A00', '#FF6600', '#FFA600', '#FFD300', '#FFFF00', '#55FF00',
        '#55FF00', '#21E5FF', '#3B9DFF', '#3358FF', '#1E32FF', '#0808FF'
    ]
    bounds = sorted([-60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60])

    inps = cmdline_parser()
    ts_file, out_file, js_file, scale, display_flag, number_flag, lonlat = check_inps(
        inps)
    write_kmz(ts_file,
              out_file,
              js_file,
              scale,
              display_flag,
              number_flag,
              lonlat,
              colors,
              bounds,
              symbol_dpi=30,
              colorbar_dpi=300)
