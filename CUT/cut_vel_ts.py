#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#####################################################
# cut velocity or timeseries data using kml or kmz  #
# Author: Yuan Lei, 2021                            #
#####################################################
import argparse
import os
import numpy as np
from xml.dom.minidom import parse
import zipfile
import sys
from multiprocessing import Process

EXAMPLE = """Example:
  python3 cut_vel_ts.py -d vel.txt -f v -k cut.kml
  python3 cut_vel_ts.py -d vel.txt -f v -k cut_multi.kml -n f -a m
  python3 cut_vel_ts.py -d ts.txt -f t -k cut.kmz
  python3 cut_vel_ts.py -d ts.txt -f t -k cut_multi.kmz -n f -a m
"""


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description="cut velocity or timeseries data using kml or kmz",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)
    parser.add_argument('-d',
                        dest='data_file',
                        required=True,
                        help='original velocity or timeseries data')
    parser.add_argument(
        '-f',
        dest='data_flag',
        required=True,
        help='flag of data, t for timeseries data, v for velocity data')
    parser.add_argument('-k',
                        dest='kml',
                        required=True,
                        help='kml or kmz file for cutting data')
    parser.add_argument(
        '-n',
        dest='number_flag',
        default='t',
        help='first column of data is point number [t] or not [f] (default: t)'
    )
    parser.add_argument(
        '-a',
        dest='area_flag',
        default='s',
        help='cut single area [s] or cut multi area [m] (default: s)')

    inps = parser.parse_args()
    return inps


def intersect(point, s_point, e_point):
    # parallel and coincident with the ray，s_point coincides with s_point
    if s_point[1] == e_point[1]:
        return False
    # line segment is above the ray
    if s_point[1] > point[1] and e_point[1] > point[1]:
        return False
    # line segment under the ray
    if s_point[1] < point[1] and e_point[1] < point[1]:
        return False
    # point coincides with s_point
    if s_point[1] == point[1] and e_point[1] > point[1]:
        return False
    # point coincides with e_point
    if e_point[1] == point[1] and s_point[1] > point[1]:
        return False
    # line segment is to the left of the ray
    if s_point[0] < point[0] and e_point[0] < point[0]:
        return False
    # find the intersection
    xseg = e_point[0] - (e_point[0] - s_point[0]) * (e_point[1] - point[1]) / (
        e_point[1] - s_point[1])
    # intersection is to the left of point
    if xseg < point[0]:
        return False
    return True


def inpolygon(point, polygon):
    num = 0  # number of intersection
    for i in range(len(polygon) - 1):
        if intersect(point, polygon[i], polygon[i + 1]):
            num += 1
    return True if num % 2 == 1 else False


def kml2polygon_dict(kml_file):
    # unzip kmz to get kml
    doc_kml = ''
    if kml_file.endswith('.kmz'):
        dir_name = os.path.dirname(kml_file)
        with zipfile.ZipFile(kml_file, 'r') as f:
            files = f.namelist()
            f.extract(files[0], dir_name)
        doc_kml = os.path.join(dir_name, 'doc.kml')
        kml_file = doc_kml

    domTree = parse(kml_file)
    if os.path.isfile(doc_kml):
        os.remove(doc_kml)
    rootNode = domTree.documentElement
    Placemarks = rootNode.getElementsByTagName('Placemark')

    polygon_dict = {}
    j = 0

    for Placemark in Placemarks:
        name = Placemark.getElementsByTagName('name')[0].childNodes[0].data
        ploygon = Placemark.getElementsByTagName('Polygon')[0]
        outerBoundaryIs = ploygon.getElementsByTagName('outerBoundaryIs')[0]
        LinearRing = outerBoundaryIs.getElementsByTagName('LinearRing')[0]
        coordinates = LinearRing.getElementsByTagName(
            'coordinates')[0].childNodes[0].data
        lon_lat = [i.split(',')[0:2] for i in coordinates.strip().split(' ')]
        polygon_dict[name + '-' + str(j)] = np.asarray(lon_lat,
                                                       dtype='float64')
        j += 1
    return polygon_dict


def get_lon_lat(polygon):
    lon_min = np.min(polygon[:, 0])
    lon_max = np.max(polygon[:, 0])
    lat_min = np.min(polygon[:, 1])
    lat_max = np.max(polygon[:, 1])

    return lon_min, lon_max, lat_min, lat_max


def filter_data(orig_data, polygon, data_flag, number_flag):
    def filter_ts(orig_data, lonlat):
        lon_min, lon_max, lat_min, lat_max = lonlat
        lon_data = orig_data[1:, 1]
        lat_data = orig_data[1:, 2]
        lon_index = ((lon_data > lon_min) == (lon_data < lon_max))
        lat_index = ((lat_data > lat_min) == (lat_data < lat_max))
        index = (lon_index & lat_index)
        first_row = orig_data[0, :]
        left_row = orig_data[1:, :]
        cutted_data = np.vstack((first_row, left_row[index, :]))

        return cutted_data

    def filter_vel(orig_data, lonlat):
        lon_min, lon_max, lat_min, lat_max = lonlat
        lon_data = orig_data[:, 1]
        lat_data = orig_data[:, 2]
        lon_index = ((lon_data > lon_min) == (lon_data < lon_max))
        lat_index = ((lat_data > lat_min) == (lat_data < lat_max))
        index = (lon_index & lat_index)
        cutted_data = orig_data[index, :]

        return cutted_data

    lonlat = get_lon_lat(polygon)

    if number_flag == 't':
        if data_flag == 't':
            return filter_ts(orig_data, lonlat)
        else:
            return filter_vel(orig_data, lonlat)
    else:
        if data_flag == 't':
            number = np.arange(-1, orig_data.shape[0] - 1).reshape((-1, 1))
            orig_data = np.hstack((number, orig_data))
            return filter_ts(orig_data, lonlat)
        else:
            number = np.arange(0, orig_data.shape[0]).reshape((-1, 1))
            orig_data = np.hstack((number, orig_data))
            return filter_vel(orig_data, lonlat)


def cut_vel_single(kml_file, vel_file, number_flag):
    out_vel_file = os.path.splitext(vel_file)[0] + '_cut.txt'
    polygon_dict = kml2polygon_dict(kml_file)
    vel = np.loadtxt(vel_file)
    for _, polygon in polygon_dict.items():
        filter_vel = filter_data(vel, polygon, 'v', number_flag)
        out_data = np.arange(vel.shape[1])
        for line in filter_vel:
            if inpolygon(line[1:3], polygon):
                if number_flag == 't':
                    out_data = np.vstack((out_data, line))
                else:
                    out_data = np.vstack((out_data, line[1:4]))
        if out_data.size > vel.shape[1]:
            np.savetxt(out_vel_file, out_data[1:, :], fmt='%4f')
    print('all done, enjoy it.')


def cut_ts_single(kml_file, ts_file, number_flag):
    out_ts_file = os.path.splitext(ts_file)[0] + '_cut.txt'
    polygon_dict = kml2polygon_dict(kml_file)
    data = np.loadtxt(ts_file)
    for _, polygon in polygon_dict.items():
        filter_ts = filter_data(data, polygon, 't', number_flag)
        out_data = data[0, :]
        for line in filter_ts[1:, :]:
            if inpolygon(line[1:3], polygon):
                if number_flag == 't':
                    out_data = np.vstack((out_data, line))
                else:
                    out_data = np.vstack((out_data, line[1:]))
        if out_data.size > filter_ts[1:, :].shape[1]:
            np.savetxt(out_ts_file, out_data, fmt='%4f')
    print('all done, enjoy it.')


def cut_vel_multi(kml_file, vel_file, number_flag):
    print('loading...')
    vel = np.loadtxt(vel_file)
    polygon_dict = kml2polygon_dict(kml_file)
    num = len(polygon_dict)
    i = 0
    for name, polygon in polygon_dict.items():
        i += 1
        print(f'\rProcessing: {i}/{num}', end=" ", flush=True)
        out_data = np.arange(vel.shape[1])
        filter_vel = filter_data(vel, polygon, 'v', number_flag)
        for line in filter_vel:
            if inpolygon(line[1:3], polygon):
                if number_flag == 't':
                    out_data = np.vstack((out_data, line))
                else:
                    out_data = np.vstack((out_data, line[1:4]))
        out_file = name + '-vel.txt'
        if out_data.size > vel.shape[1]:
            np.savetxt(out_file, out_data[1:, :], fmt='%4f')
    print(f'\rProcessed: {i}/{num}, enjoy it.', end=" ", flush=True)


def cut_ts_multi(kml_file, ts_file, number_flag):
    print('loading...')
    data = np.loadtxt(ts_file)
    polygon_dict = kml2polygon_dict(kml_file)
    num = len(polygon_dict)
    i = 0
    for name, polygon in polygon_dict.items():
        i += 1
        print(f'\rProcessing: {i}/{num}', end="", flush=True)
        out_data = data[0, :]
        filter_ts = filter_data(data, polygon, 't', number_flag)
        for line in filter_ts[1:, :]:
            if inpolygon(line[1:3], polygon):
                if number_flag == 't':
                    out_data = np.vstack((out_data, line))
                else:
                    out_data = np.vstack((out_data, line[1:]))
        out_file = name + '-ts.txt'
        if out_data.size > filter_ts[1:, :].shape[1]:
            np.savetxt(out_file, out_data, fmt='%4f')
    print(f'\rProcessed: {i}/{num}, enjoy it.', end=" ", flush=True)


def main():
    inps = cmdline_parser()
    data_file = os.path.abspath(inps.data_file)
    kml = os.path.abspath(inps.kml)
    data_flag = inps.data_flag.lower()
    number_flag = inps.number_flag.lower()
    area_flag = inps.area_flag.lower()

    # check data_file
    if not os.path.isfile(data_file):
        print('cannot find file {}'.format(data_file))
        sys.exit()
    # check kml
    if not os.path.isfile(kml):
        print('cannot find file {}'.format(kml))
        sys.exit()
    # check data_flag
    if data_flag not in ['t', 'v']:
        print('Error data_flag, t for timeseries data, v for velocity data')
        sys.exit()
    # check number_flag
    if number_flag not in ['t', 'f']:
        print(
            'Error number_flag, first column of data is point number [t] or not [f] (default: t)'
        )
        sys.exit()
    # check area_flag
    if area_flag not in ['m', 's']:
        print(
            'Error area_flag, cut single area [s] or cut multi area [m] (default: s)'
        )
        sys.exit()

    # cut timeseries data
    if data_flag == 't':
        if area_flag == 's':
            # cut_ts_single(kml, data_file, number_flag)
            p = Process(target=cut_ts_single,
                        args=(kml, data_file, number_flag))
        else:
            # cut_ts_multi(kml, data_file, number_flag)
            p = Process(target=cut_ts_multi,
                        args=(kml, data_file, number_flag))
    # cut velocity data
    else:
        if area_flag == 's':
            # cut_vel_single(kml, data_file, number_flag)
            p = Process(target=cut_vel_single,
                        args=(kml, data_file, number_flag))
        else:
            # cut_vel_multi(kml, data_file, number_flag)
            p = Process(target=cut_vel_multi,
                        args=(kml, data_file, number_flag))

    p.start()
    p.join()


if __name__ == "__main__":
    main()
