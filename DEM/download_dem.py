#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#################################################################################
# Download SRTM (30m[only get download link] or 90m) or ALOS (30m) DEM          #
# Copyright (c) 2020, Lei Yuan                                                  #
#################################################################################
import argparse
import math
import os
import urllib.request


def alos_dem(s, n, w, e):
    download_urls = []
    lon_lat_list = []
    HEADER = "https://www.eorc.jaxa.jp/ALOS/aw3d30/data/release_v1903/"
    # calculate latitude and longitude, it must be a multiple of 5
    lon_min = int(w // 5 * 5)
    lon_max = math.ceil(e / 5) * 5
    lat_min = int(s // 5 * 5)
    lat_max = math.ceil(n / 5) * 5

    # format num, add 0
    def format_num(num, flag):
        if num < 0:
            zero_num = flag - len(str(num)[1:])
            if zero_num > 0:
                return "0" * zero_num + str(num)[1:]
            else:
                return str(num)[1:]
        else:
            zero_num = flag - len(str(num))
            if zero_num > 0:
                return "0" * zero_num + str(num)
            else:
                return str(num)

    # traverse to get download urls
    for i in range(lat_min, lat_max, 5):
        for j in range(lon_min, lon_max, 5):
            i_5, j_5 = i + 5, j + 5
            i_0 = "S{}".format(format_num(i, 3)) if i < 0 else "N{}".format(
                format_num(i, 3))
            j_0 = "W{}".format(format_num(j, 3)) if j < 0 else "E{}".format(
                format_num(j, 3))
            i_5 = "S{}".format(format_num(
                i_5, 3)) if i_5 < 0 else "N{}".format(format_num(i_5, 3))
            j_5 = "W{}".format(format_num(
                j_5, 3)) if j_5 < 0 else "E{}".format(format_num(j_5, 3))
            # determine the positive and negative of latitude and longitude
            tmp_lon_s = int(j_0[1:] if 'E' in j_0 else '-' + j_0[1:])
            tmp_lon_b = int(j_5[1:] if 'E' in j_5 else '-' + j_5[1:])
            tmp_s = int(i_0[1:] if 'N' in i_0 else '-' + i_0[1:])
            tmp_lat_b = int(i_5[1:] if 'N' in i_5 else '-' + i_5[1:])
            lon_lat = "({}° ~ {}° , {}° ~ {}°)".format(tmp_lon_s, tmp_lon_b,
                                                       tmp_s, tmp_lat_b)
            lon_lat_list.append(lon_lat)
            name = "{}{}_{}{}.tar.gz".format(i_0, j_0, i_5, j_5)
            url = HEADER + name
            download_urls.append(url)
    return lon_lat_list, download_urls


def srtm_dem(s, n, w, e, flag):
    number = 1
    if flag.upper() == 'SRTM90':
        number = 3
    HEADER = "https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL{}.003/2000.02.11/".format(
        number)
    download_urls = []
    lon_lat_list = []
    lon_min = math.floor(w)
    lon_max = math.ceil(e)
    lat_min = math.floor(s)
    lat_max = math.ceil(n)

    def add_zero(i, flag):
        s = str(abs(i))
        if flag == 'SN':
            if len(s) == 1:
                return '0' + s
            else:
                return s
        if flag == 'WE':
            if len(s) == 1:
                return '00' + s
            elif len(s) == 2:
                return '0' + s
            else:
                return s

    for i in range(lat_min, lat_max):
        for j in range(lon_min, lon_max):
            lon_lat = "({}° ~ {}° , {}° ~ {}°)".format(j, j + 1, i, i + 1)
            lon_lat_list.append(lon_lat)
            if i >= 0:
                if j >= 0:
                    name = "N{}E{}.SRTMGL{}.hgt.zip".format(
                        add_zero(i, 'SN'), add_zero(j, 'WE'), number)
                else:
                    name = "N{}W{}.SRTMGL{}}.hgt.zip".format(
                        add_zero(i, 'SN'), add_zero(j, 'WE'), number)
            else:
                if j >= 0:
                    name = "S{}E{}.SRTMGL{}.hgt.zip".format(
                        add_zero(i, 'SN'), add_zero(j, 'WE'), number)
                else:
                    name = "S{}W{}.SRTMGL{}.hgt.zip".format(
                        add_zero(i, 'SN'), add_zero(j, 'WE'), number)
            download_urls.append(HEADER + name)

    return lon_lat_list, download_urls


def get_urls(flag, bound):
    lon_lat = []
    download_urls = []
    # check boundary
    if len(bound) == 4:
        s, n, w, e = bound[0], bound[1], bound[2], bound[3]
        if w >= e or s >= n:
            print('Error bound, please reset it (S N W E)!')
        else:
            if flag.upper() == 'SRTM90':
                lon_lat, download_urls = srtm_dem(s, n, w, e, flag)
            elif flag.upper() == 'SRTM30':
                lon_lat, download_urls = srtm_dem(s, n, w, e, flag)
            elif flag.upper() == 'ALOS':
                lon_lat, download_urls = alos_dem(s, n, w, e)
            else:
                print('Error flag, please reset it (alos ALOS srtm SRTM)!')
    else:
        print('Error bound, please reset it (S N W E)!')
    print("\nDownload urls of all DEM:")
    for i, j in zip(lon_lat, download_urls):
        if lon_lat.index(i) == len(lon_lat) - 1:
            print("{}: {}\n".format(i, j))
        else:
            print("{}: {}".format(i, j))
    return download_urls


def download_progress(blocknum, blocksize, totalsize):
    """
    :param blocknum: downloaded block number
    :param blocksize: block size
    :param totalsize: file size
    """
    percent = 100.0 * blocknum * blocksize / totalsize
    if percent > 100:
        percent = 100
        print("\rDownloaded: " + "#" * int(percent / 2) + " %.2f%%" % percent,
              end=" ",
              flush=True)
    else:
        print("\rDownloading: " + "#" * int(percent / 2) + " %.2f%%" % percent,
              end=" ",
              flush=True)


def download_dem(url, save_path):
    abs_path = os.path.join(save_path, url.split('/')[-1])
    try:
        urllib.request.urlretrieve(url, abs_path, download_progress)
    except Exception as e:
        print(f'{e}')


EXAMPLE = '''Example:
  # only get urls of srtm30 or srtm90
  python download_dem.py -f srtm30 -b 30 40 100 105
  # get urls of alos DEM and download them
  python download_dem.py -f alos -b 30 40 100 105 -o /ly/dem
'''


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description=
        'Download SRTM DEM [only get download link] or ALOS DSM [30m].',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)
    parser.add_argument(
        '-f',
        dest='flag',
        required=True,
        type=str,
        help='DEM type (alos, ALOS, srtm90, srtm30, SRTM90, SRTM30)')
    parser.add_argument('-b',
                        dest='bound',
                        required=True,
                        type=float,
                        nargs=4,
                        help='DEM bound (S N W E)')
    parser.add_argument('-o',
                        dest='out_dir',
                        type=str,
                        help='directory path of saving DEM')
    return parser


def main():
    # argument parser
    parser = cmdline_parser()
    args = parser.parse_args()
    flag = args.flag
    bound = args.bound
    out_dir = os.path.abspath(args.out_dir)
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    # get urls of DEM
    download_urls = get_urls(flag, bound)
    # download DEM
    if flag.upper() == 'ALOS':
        print("Start to download all ALOS DSM:")
        for url in download_urls:
            print(f"{url.split('/')[-1]}")
            download_dem(url, out_dir)
    else:
        print('cannot download SRTM DEM, you have to download them manually.')


if __name__ == "__main__":
    main()
