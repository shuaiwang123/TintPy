# -*- coding:utf-8 -*-
# xyz2kmz
# leiyuan, 2020-08-10
import os
import sys
import zipfile

import matplotlib.patches as mpathes
import matplotlib.pyplot as plt
from lxml import etree
from pykml.factory import KML_ElementMaker as KML

cb = {
    '#AA0000': '50-60',
    '#FF0000': '40-50',
    '#FF5500': '30-40',
    '#FFAA00': '20-30',
    '#FFFF00': '10-20',
    '#008B00': '0-10',
    '#008B01': '-10-0',
    '#00FFFF': '-20--10',
    '#00AAFF': '-30--20',
    '#0055FF': '-40--30',
    '#0000FF': '-50--40',
    '#0000AA': '-60--50'
}


def plot_symbol(cb, save_path):
    for color, label in cb.items():
        fig, ax = plt.subplots(figsize=(1, 1))
        ax.set_axis_off()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        circle = mpathes.Circle((0.5, 0.5), 0.49, color=color)
        ax.add_patch(circle)
        path = os.path.join(save_path, label + '.png')
        fig.savefig(path, transparent=True, dpi=12)
        # plt.show()


def plot_colorbar(cb, save_path):
    fig, ax = plt.subplots(figsize=(4, 14))
    ax.set_axis_off()
    ax.set_xlim(0, 1.5)
    ax.set_ylim(0, 6.5)
    plt.subplots_adjust(top = 1, bottom = 0.05, right = 0.9, left = 0.1, hspace = 1, wspace = 0)
    y = 0.05
    tmp = list(cb.keys())[::-1]
    for color in tmp:
        # circle = mpathes.Circle((0.5, y), 0.3, color=color)
        rect = plt.Rectangle((0, y), 1, 0.5, color=color)
        y += 0.5
        ax.add_patch(rect)
    yy = 0
    for i in range(-60, 70, 10):
        ax.text(1.2, yy, str(i), fontsize=30)
        yy += 0.5
    ax.text(0.1, 6.2, 'mm/yr', fontsize=30)
    path = os.path.join(save_path, 'colorbar.png')
    fig.savefig(path, dpi=100)
    # plt.show()


def txt2llv(txt):
    lons = []
    lats = []
    vels = []
    with open(txt, 'r') as f:
        for l in f.readlines():
            tmp = l.strip().split()
            lons.append(tmp[0])
            lats.append(tmp[1])
            vels.append(tmp[2])
    return lons, lats, vels


def gen_description(lon, lat, vel):
    description = """<![CDATA[<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">
<head>
<META http-equiv="Content-Type" content="text/html">
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
</head>
<body style="margin:0px 0px 0px 0px;overflow:auto;background:#FFFFFF;">
<table style="font-family:Arial,Verdana,Times;font-size:12px;text-align:left;width:100%;border-collapse:collapse;padding:3px 3px 3px 3px">
<tr style="text-align:center;font-weight:bold;background:#9CBCE2">
<td>velocity</td>
</tr>
<tr>
<td>
<table style="font-family:Arial,Verdana,Times;font-size:12px;text-align:left;width:100%;border-spacing:0px; padding:3px 3px 3px 3px">
<tr>
<td>longitude</td>
<td>{}</td>
</tr>
<tr bgcolor="#D4E4F3">
<td>latitude</td>
<td>{}</td>
</tr>
<tr>
<td>velocity</td>
<td>{}</td>
</tr>
<tr bgcolor="#D4E4F3">
<td>style</td>
<td>point</td>
</tr>
</table>
</td>
</tr>
</table>
</body>
</html>
""".format(lon, lat, vel)
    return description


def write_kml(lons, lats, vels, cb, file_name):
    doc = KML.kml(
        KML.Document(KML.Folder(KML.name(os.path.basename(file_name)))))
    for color in cb.values():
        style = KML.Style(KML.IconStyle(KML.Icon(KML.href(color + '.png')),
                                        KML.scale('0.5')),
                          KML.LabelStyle(KML.color('00000000'),
                                         KML.scale('0.000000')),
                          id=color)
        doc.Document.append(style)

    for lon, lat, vel in zip(lons, lats, vels):
        # sys.stdout.write(f'\rprocess point: {lons.index(lon) + 1}/{len(lons)}')
        # sys.stdout.flush()
        # print('')
        for i in list(range(-60, 60, 10)):
            min = int(i)
            max = min + 10
            if float(vel) >= min and float(vel) < max:
                id = f"{min}-{max}"
        description = gen_description(lon, lat, vel)
        placemark = KML.Placemark(
            KML.name(str(lons.index(lon) + 1)), KML.description(description),
            KML.styleUrl(f"#{id}"),
            KML.Point(KML.altitudeMode('clampToGround'),
                      KML.coordinates(f"{lon},{lat},{vel}")))
        doc.Document.Folder.append(placemark)

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
            y="0.6",
            xunits="fraction",
            yunits="fraction",
        ),
    )
    doc.Document.Folder.append(colorbar)
    kmlstr = etree.tostring(doc, pretty_print=True)
    # print(kmlstr)
    kml_path = os.path.join(os.path.dirname(file_name), 'doc.kml')
    with open(kml_path, 'wb') as f:
        f.write(kmlstr)

    if os.path.isfile(file_name):
        os.remove(file_name)

    with zipfile.ZipFile(file_name, 'a') as f:
        f.write(kml_path)
        f.write('colorbar.png')
        for i in cb.values():
            f.write(i + '.png')


def del_files(path):
    for i in cb.values():
        tmp = os.path.join(path, i + '.png')
        if os.path.isfile(tmp):
            os.remove(tmp)
    for i in ['colorbar.png', 'doc.kml']:
        tmp = os.path.join(path, i)
        if os.path.isfile(tmp):
            os.remove(tmp)


if __name__ == "__main__":
    vel_file = 'vels14_gacos05_ds.txt'
    kmz = 'vels14_gacos05_ds.kmz'
    dir_name = os.path.dirname(kmz)

    lons, lats, vels = txt2llv(vel_file)
    print('plot symbol...')
    plot_symbol(cb, dir_name)
    print('plot colorbar...')
    plot_colorbar(cb, dir_name)
    print('write kml...')
    write_kml(lons, lats, vels, cb, kmz)
    print('delete files...')
    del_files(dir_name)
    print('all done.')
