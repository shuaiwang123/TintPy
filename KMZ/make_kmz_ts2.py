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
import base64

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from lxml import etree
from pykml.factory import KML_ElementMaker as KML

EXAMPLE = r"""Example:
  # Windows
  python make_kmz_ts2.py ts.txt D:\kmz\ts.kmz
  python make_kmz_ts2.py ts.txt D:\kmz\ts.kmz -v -60 60 -c jet_r -j D:\kmz\dygraph-combined.js
  python make_kmz_ts2.py ts.txt D:\kmz\ts.kmz -v -60 60 -c jet_r -j D:\kmz\dygraph-combined.js -s 0.6 -f vel
  # Linux
  python3 make_kmz_ts2.py ts.txt /home/ly/ts
  python3 make_kmz_ts2.py ts.txt /home/ly/ts -j /home/ly/tsdygraph-combined.js
  python3 make_kmz_ts2.py ts.txt /home/ly/ts -j /home/ly/tsdygraph-combined.js -s 0.6 -f disp
  # data format
    -1   -1   -1    -1       date1       date2       date3 ...
  num1 lon1 lat1  vel1 date1-disp1 date2-disp1 date3-disp1 ...
  num2 lon2 lat2  vel2 date1-disp2 date2-disp2 date3-disp2 ...
  num3 lon3 lat3  vel3 date1-disp3 date2-disp3 date3-disp3 ...
  ...
"""

DOT_STR = b"""iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAABGdBTUEAALGPC
/xhBQAAAAlwSFlzAAAPYQAAD2EBqD+naQAABNhJREFUeNrtmmlSGlEUhRvnGVxByA7YgZ0VJO6A
Kkv9KVlBcAEW4FTiUNEdsAM7KwjZgVlBcJ4l53T1JZeXlsR002h8r+rWa+CHnu+dN93bKeeVt5Q
FYAFYABaABWABWAAWgAVgAVgAFoAF0KU2NzeXQecickEvrRn8Dw1EPQhvb2+v8V8AgHCKLSDeDw
wMOP39/X709fU5qdSvP91sNp2Hhwfn/v7ej7u7uwN8vQ8Q3osEEAgvQWhuaGjIGRwcdAhAIFC8Q
BDx7APxftzc3Di3t7cefvsIEPUXASCwehHCloaHhx2KZ08AAuExAOIAiodwPwjh+vqaUQGEwrMG
EIg/hMjcyMiIwxAI2gUyDSheAOjRZ0/xFK4AOJeXl3X89i7u9SEVk3gubocQmRkbG3NGR0d98Rq
CuCAMgDH/2wBcXV1RvPR1/BYrhFRMI/8VQrMUziCETi6g/c0pIADE+iI+GP1WnJ+fxwohDgAceX
d8fNwXLg6QIADtApkGBCA7gJ4Ceu4TgDjg4uKiFYBQq1arsz0HAPGfIKZI0RMTE04YhDAXaABsd
IBe/QWAHnklXqKws7NT6RkAiM/S+hCbEfHsKV5AaBcQhN4N9BQw7S+jr2zf6s/OzqRv4Lu3UadC
FACfISY/OTnpCxcIOvR6IFPhTy3M+mrUWxAYp6enRUyF5cQBBAvfD4okAIY8ixPM6UDb/22jGyh
cRl0Lh2j/mT1dgOdILvhXAEuwcVnEiwtMN8iU0PP9KRAolCBkxAWA9EHkt7e3D5IGcIhRdTUAE4
YE5/u/Nq4JpviQqG1sbMwmDaCpBU9NTbU9ixto/aiNDpBRPzk5aRMffG5UKpXpxABA/Aws7VGoC
H+sf8q8f6xxa1Ri23oJfH67u7t7lBQAXm1rAsAEIUEXxNVM0SYAhIt14EtSAD5h+yum0+mWcP0s
ALj4xdW4GIaJPz4+ls/u1tZWcgCwnxf1yAsAHdz742qyDuhRV+L5bAEkCWAGU8B7zVNgBoug12k
RlC0xwUUwi0Xwe2LngPn5+WanbVAiyiFIH4ZEsD4LKPGNUqmU3DlAToIQ6IYdhHTEeRAyQ4Gora
6uJn4SXIK4Mvd6U7wcgeU5jqOwvgCFRB5H4cTvAmkIa4RdhvStUCLKZSjkCqzvBY2VlZXpKA6Ll
A+AuLx5+ZEwEyNPORbz+GtmgSQRogGgL66trS33CsAbbId1iM2YwqUX8TpB2qkxO8SMEMUzMWLk
AducwFwAIlutVo97mhOEyKJOgnTKCzIdxrygLo9JVthMiOqcoOQFjCmRX19fP4i6yEbOCmNLPIR
oV9veTI/rpKjOCptpcakICQCdFzScUCuXy73PCsuCyJMhhOcoWgMwawNmecwsjYWUxH7LDLMugN
6Nav24K0NvAghZXRPolBIPqw3qaaALIypB6ovHsTcW8bEB0E6A8JwefV0gNUvkui6gU+OPuMADi
A9xio8VgLTFxcUShBd0RYi9lMd1aUxXhnRxRAMInFDEaW/Z6ULr1vsBM7wyI1xdGNULoOmAsPI4
AHgAUNjc3PzmdKl19Q0R7BC8OucBIW/avwOABqIGAPsQ/sXpckvsJamFhQVeo10AyGHxyxgAjoL
wkhDdEwDPtVkAFoAFYAFYABaABWABWAAWgAXwOttPxi1EjO7EVwYAAAAASUVORK5CYII="""


def create_parser():
    parser = argparse.ArgumentParser(
        description='Display velocity (or cumulative displacement) and time-series displacement derived by InSAR in Google Earth.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)
    parser.add_argument(
        'ts_file',
        help='formatted timeseries file for generating KMZ file')
    parser.add_argument('out_file',
                        help='output KMZ file')
    parser.add_argument('-v', dest='vlim', nargs=2, metavar=('MIN', 'MAX'), type=float, default=(-60, 60),
                        help='value limits for plotting (default: -60 60)')
    parser.add_argument('-c', dest='colormap', default='jet',
                        help='colormap for plotting (default: jet)')
    parser.add_argument(
        '-j',
        dest='js_file',
        default='dygraph-combined.js',
        help='javascript file for drawing timeseries graph (default: dygraph-combined.js)'
    )
    parser.add_argument('-s',
                        dest='scale',
                        default=0.8,
                        type=float,
                        help='scale of point for display (default: 0.8)')
    parser.add_argument(
        '-f',
        dest='flag',
        default='vel',
        type=str,
        help='basemap of kmz (default: vel) [velocity(vel) or cumulative displacement(disp)]'
    )
    return parser


def cmdline_parser():
    parser = create_parser()
    inps = parser.parse_args()
    return inps


def plot_shaded_dot(file_name, dir_name):
    """write shaed_dot.png for display"""
    path = os.path.join(dir_name, file_name)
    with open(path, 'wb') as f:
        f.write(base64.b64decode(DOT_STR))


def plot_colorbar(dir_name, vmin, vmax, flag, cmap, figsize=(0.18, 3.6), nbins=7):
    fig, cax = plt.subplots(figsize=figsize)
    fig.subplots_adjust(left=0.1, right=0.5)

    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    cbar = mpl.colorbar.ColorbarBase(cax, cmap=plt.get_cmap(
        cmap), norm=norm, orientation='vertical')

    if flag == 'vel':
        label = 'mean LOS velocity [mm/yr]'
    else:
        label = 'cumulative LOS displacement [mm]'
    cbar.set_label('{}'.format(label), fontsize=6)

    cbar.locator = mpl.ticker.MaxNLocator(nbins=nbins)
    cbar.update_ticks()
    cbar.ax.tick_params(which='both', labelsize=6)
    fig.patch.set_facecolor('white')
    fig.patch.set_alpha(1)
    colorbar_path = os.path.join(dir_name, 'colorbar.png')
    fig.savefig(colorbar_path, bbox_inches='tight',
                facecolor=fig.get_facecolor(), dpi=300)


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
    js_file = inps.js_file
    if js_file == 'dygraph-combined.js':
        js_file = os.path.join(sys.path[0], 'dygraph-combined.js')
    else:
        js_file = os.path.abspath(js_file)
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
    if scale <= 0:
        print('scale cannot less than or equal to 0')
        sys.exit()
    # check flag
    if flag not in ['vel', 'disp']:
        print('flag must be vel or disp')
        sys.exit()

    return ts_file, out_file, js_file, scale, flag


def get_hex_color(v, colormap, norm):
    """Get color name in hex format.
    Parameters: v        : float, number of interest
                colormap : matplotlib.colors.Colormap instance
                norm     : matplotlib.colors.Normalize instance
    Returns:    c_hex    : color name in hex format
    """
    rgba = colormap(norm(v))  # get rgba color components for point velocity
    c_hex = mpl.colors.to_hex(
        [rgba[3], rgba[2], rgba[1], rgba[0]], keep_alpha=True)[1:]
    return c_hex


def write_kmz(ts_file,
              out_file,
              js_file,
              scale,
              flag,
              vlim,
              colormap):
    """write kml file and unzip files into kmz"""
    print('Writing data to {}'.format(out_file))
    # get lons, lats, vels, ts, dates
    try:
        data, dates = load_data(ts_file)
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
    # create placemark
    for j in range(lons.shape[0]):
        num, lon, lat, vel, disp = nums[j], lons[j], lats[j], vels[j], ts[j, :]
        description_str = get_description_string(
            lon, lat, vel, disp[-1]) + generate_js_datastring(
                dates, js_file, disp)
        description = KML.description(description_str)
        name = KML.name(str(int(num)))

        # Set and normalize colormap to defined vlim
        colormap = mpl.cm.get_cmap(colormap)
        norm = mpl.colors.Normalize(vmin=vlim[0], vmax=vlim[1])

        if flag == 'vel':
            color = get_hex_color(vel, colormap, norm)
        else:
            color = get_hex_color(disp[-1], colormap, norm)
        style = KML.Style(
            KML.IconStyle(KML.color(color), KML.scale(str(scale)),
                          KML.Icon(KML.href("shaded_dot.png"))),
            KML.LabelStyle(KML.color('00000000'), KML.scale('0.0')))
        point = KML.Point(KML.altitudeMode('clampToGround'),
                          KML.coordinates(f"{lon},{lat}"))
        placemark = KML.Placemark(name, style, description, point)
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
            x="0.08",
            y="0.48",
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
    # plot colorbar
    plot_colorbar(dir_name, vlim[0], vlim[1], flag, colormap)
    # unzip kml, symbol, colorbar, dygraph_file
    with zipfile.ZipFile(out_file, 'w') as f:
        os.chdir(dir_name)
        f.write('doc.kml')
        os.remove('doc.kml')
        f.write('colorbar.png')
        os.remove('colorbar.png')
        plot_shaded_dot('shaded_dot.png', dir_name)
        f.write('shaded_dot.png')
        os.remove('shaded_dot.png')
        os.chdir(os.path.dirname(js_file))
        f.write(os.path.basename(js_file))
    print('Done, enjoy it!')


if __name__ == "__main__":
    inps = cmdline_parser()
    ts_file, out_file, js_file, scale, flag = check_inps(inps)
    write_kmz(ts_file,
              out_file,
              js_file,
              scale,
              flag,
              inps.vlim,
              inps.colormap)
