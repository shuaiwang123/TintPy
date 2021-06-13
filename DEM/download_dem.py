#!/usr/bin/env python3
# -*- coding:utf-8 -*-
##################################################
# Download SRTM DEM [30m 90m] or ALOS DSM [30m]  #
# Copyright (c) 2020, Lei Yuan                   #
##################################################
import argparse
import math
import os
import sys
import urllib.request


no_srtm_dem = """01_01-01_03-01_04-01_05-01_06-01_08-01_09-01_10-01_11-01_13-
01_14-01_20-01_22-01_23-01_24-02_03-02_04-02_05-02_06-02_10-02_11-02_12-02_18-
02_19-02_20-02_21-02_22-02_23-02_24-03_03-03_04-03_05-03_06-03_07-03_10-03_11-
03_12-03_13-03_14-03_17-03_18-03_19-03_20-03_21-03_22-03_23-03_24-04_03-04_04-
04_05-04_06-04_07-04_09-04_10-04_13-04_17-04_18-04_19-04_20-04_21-04_22-04_23-
04_24-05_03-05_04-05_05-05_06-05_07-05_10-05_11-05_13-05_15-05_18-05_19-05_20-
05_21-05_22-05_23-05_24-06_02-06_03-06_04-06_05-06_06-06_07-06_08-06_10-06_11-
06_12-06_18-06_19-06_20-06_21-06_22-06_23-06_24-07_02-07_03-07_04-07_05-07_06-
07_07-07_08-07_09-07_10-07_11-07_12-07_13-07_14-07_18-07_19-07_20-07_21-07_22-
07_23-07_24-08_02-08_03-08_04-08_05-08_06-08_07-08_08-08_09-08_10-08_11-08_12-
08_13-08_19-08_20-08_21-08_22-08_23-08_24-09_02-09_03-09_04-09_05-09_06-09_07-
09_08-09_09-09_10-09_11-09_12-09_13-09_18-09_19-09_20-09_21-09_22-09_23-09_24-
10_03-10_04-10_05-10_06-10_07-10_08-10_09-10_10-10_11-10_12-10_13-10_14-10_15-
10_16-10_19-10_20-10_21-10_22-10_23-10_24-11_04-11_05-11_06-11_07-11_08-11_09-
11_10-11_11-11_12-11_13-11_14-11_15-11_16-11_18-11_19-11_20-11_21-11_22-11_23-
11_24-12_07-12_08-12_09-12_10-12_11-12_12-12_13-12_14-12_15-12_16-12_18-12_19-
12_20-12_21-12_22-12_23-12_24-13_09-13_10-13_11-13_12-13_13-13_14-13_15-13_16-
13_17-13_18-13_19-13_20-13_21-13_22-13_23-13_24-14_10-14_11-14_12-14_13-14_14-
14_15-14_16-14_17-14_18-14_19-14_20-14_21-14_22-14_23-14_24-15_11-15_12-15_13-
15_14-15_15-15_16-15_17-15_19-15_20-15_21-15_22-15_23-15_24-16_10-16_11-16_12-
16_13-16_14-16_15-16_16-16_17-16_18-16_19-16_20-16_21-16_22-16_23-16_24-17_10-
17_11-17_12-17_13-17_14-17_15-17_16-17_17-17_18-17_19-17_20-17_21-17_22-17_23-
17_24-18_11-18_14-18_15-18_16-18_17-18_18-18_19-18_20-18_21-18_22-18_23-18_24-
19_14-19_15-19_16-19_17-19_18-19_19-19_20-19_21-19_22-19_23-19_24-20_15-20_16-
20_17-20_20-20_21-20_22-20_23-20_24-21_17-21_20-22_06-22_07-23_05-23_06-23_07-
23_08-24_05-24_07-24_08-24_22-24_24-25_05-25_06-25_07-25_08-25_09-25_21-25_22-
25_24-26_01-26_02-26_04-26_05-26_06-26_07-26_08-26_09-26_10-26_20-26_21-26_22-
26_23-26_24-27_02-27_03-27_04-27_05-27_06-27_07-27_08-27_09-27_10-27_11-27_19-
27_20-27_21-27_22-27_23-27_24-28_02-28_03-28_04-28_05-28_06-28_07-28_08-28_09-
28_10-28_11-28_12-28_18-28_19-28_20-28_21-28_22-28_23-28_24-29_01-29_02-29_03-
29_04-29_05-29_06-29_07-29_08-29_09-29_10-29_11-29_12-29_17-29_18-29_19-29_20-
29_21-29_22-29_24-30_01-30_02-30_03-30_04-30_06-30_07-30_08-30_09-30_10-30_11-
30_12-30_15-30_16-30_17-30_18-30_19-30_20-30_21-30_22-30_23-31_01-31_02-31_03-
31_04-31_06-31_07-31_08-31_10-31_11-31_12-31_13-31_14-31_15-31_16-31_18-31_19-
31_20-31_21-31_22-31_23-31_24-32_01-32_02-32_03-32_04-32_06-32_07-32_08-32_11-
32_12-32_13-32_14-32_15-32_16-32_17-32_18-32_19-32_20-32_21-32_22-32_23-32_24-
33_01-33_02-33_03-33_04-33_05-33_11-33_12-33_13-33_14-33_15-33_16-33_17-33_18-
33_19-33_20-33_21-33_22-33_23-33_24-34_03-34_04-34_05-34_06-34_12-34_13-34_15-
34_16-34_17-34_18-34_19-34_22-34_23-34_24-35_13-35_14-35_15-35_17-35_18-35_19-
35_20-35_22-35_23-35_24-36_13-36_14-36_15-36_16-36_17-36_18-36_19-36_20-36_21-
36_22-36_23-36_24-37_12-37_13-37_14-37_15-37_16-37_17-37_18-37_19-37_20-37_21-
37_22-37_24-38_14-38_15-38_16-38_17-38_18-38_19-38_20-38_21-38_22-38_23-38_24-
39_19-39_20-39_21-39_22-39_23-39_24-40_20-40_21-40_22-40_23-40_24-41_20-41_21-
41_22-41_23-41_24-42_20-42_21-42_22-42_23-42_24-43_20-43_21-43_22-43_23-43_24-
44_18-44_19-44_20-44_21-44_23-44_24-45_14-45_19-45_20-45_21-45_22-45_23-45_24-
46_13-46_19-46_20-46_21-46_22-46_23-46_24-47_12-47_17-47_18-47_19-47_20-47_21-
47_23-47_24-48_10-48_11-48_12-48_18-48_19-48_20-48_21-48_22-48_23-48_24-49_08-
49_09-49_10-49_11-49_12-49_13-49_14-49_15-49_17-49_18-49_19-49_20-49_21-49_22-
49_23-49_24-50_09-50_10-50_11-50_12-50_13-50_14-50_15-50_17-50_18-50_19-50_20-
50_21-50_24-51_15-51_16-51_17-51_18-51_19-51_20-51_21-51_24-52_12-52_13-52_14-
52_15-52_16-52_17-52_18-52_19-52_21-52_22-52_23-52_24-53_12-53_13-53_14-53_15-
53_16-53_17-53_18-53_19-53_20-53_21-53_22-53_23-53_24-54_10-54_11-54_12-54_13-
54_14-54_15-54_16-54_17-54_18-54_19-54_20-54_21-54_22-54_23-54_24-55_12-55_13-
55_14-55_15-55_16-55_17-55_18-55_19-55_20-55_21-55_22-55_23-55_24-56_14-56_16-
56_17-56_18-56_19-56_20-56_21-56_22-56_23-56_24-57_15-57_16-57_17-57_18-57_19-
57_20-57_21-57_22-57_23-57_24-58_16-58_17-58_18-58_19-58_20-58_21-58_22-58_23-
58_24-59_15-59_16-59_20-59_21-59_22-59_23-59_24-60_21-60_22-60_23-60_24-61_20-
61_21-61_22-61_23-61_24-62_09-62_20-62_21-62_22-62_23-62_24-63_09-63_10-63_20-
63_21-63_22-63_23-63_24-64_07-64_09-64_12-64_21-64_22-64_23-64_24-65_09-65_12-
65_22-65_23-65_24-66_02-66_05-66_06-66_07-66_12-66_22-66_23-66_24-67_04-67_05-
67_06-67_07-67_09-67_10-67_21-67_22-67_23-67_24-68_04-68_05-68_06-68_07-68_08-
68_09-68_10-68_12-68_18-68_20-68_21-68_22-69_03-69_04-69_05-69_06-69_07-69_08-
69_09-69_12-69_13-69_18-69_19-69_20-69_21-69_22-69_23-69_24-70_03-70_04-70_05-
70_06-70_07-70_08-70_19-70_20-70_24-71_01-71_03-71_04-71_05-71_06-71_07-71_08-
71_09-71_14-71_18-71_23-71_24-72_01-72_03-72_04-72_05-72_06-72_07-72_08-72_09-
72_10-72_11-72_12-72_17-72_18-72_19-72_23-72_24"""


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


def srtm_dem9055(s, n, w, e):
    # 90m srtm dem of 5*5 degrees
    download_urls = []
    lon_lat_list = []
    HEADER = "http://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF/srtm_"
    # latitude and longitude of starting point for calculating dem number
    lon_min = -180
    lat_max = 60
    # calculate dem number
    num_min_lon = (w - lon_min) / 5 + 1
    num_max_lon = (e - lon_min) / 5 + 1
    num_min_lat = (lat_max - n) / 5 + 1
    num_max_lat = (lat_max - s) / 5 + 1
    if num_min_lon > int(num_min_lon):
        num_min_lon = int(num_min_lon)
    if num_max_lon > int(num_max_lon):
        num_max_lon = int(num_max_lon + 1)
    if num_min_lat > int(num_min_lat):
        num_min_lat = int(num_min_lat)
    if num_max_lat > int(num_max_lat):
        num_max_lat = int(num_max_lat + 1)
    # traverse to get download urls
    for i in range(int(num_min_lon), int(num_max_lon)):
        for j in range(int(num_min_lat), int(num_max_lat)):
            # calculate the longitude and latitude range of dem
            w = i * 5 - 180
            e = w - 5
            s = 60 - j * 5
            n = s + 5
            # add 0
            w = "0" + str(w) if len(str(w)) == 1 else str(w)
            e = "0" + str(e) if len(str(e)) == 1 else str(e)
            s = "0" + str(s) if len(str(s)) == 1 else str(s)
            n = "0" + str(n) if len(str(n)) == 1 else str(n)
            lon_lat = "({}° ~ {}° , {}° ~ {}°)".format(e, w, s, n)
            lon_lat_list.append(lon_lat)
            num_lon = str(i)
            num_lat = str(j)
            if len(num_lon) == 1:
                num_lon = "0" + num_lon
            if len(num_lat) == 1:
                num_lat = "0" + num_lat
            name = "srtm_{}_{}.zip".format(num_lon, num_lat)
            if name not in no_srtm_dem:
                url = "{}{}_{}.zip".format(HEADER, num_lon, num_lat)
                download_urls.append(url)
            else:
                download_urls.append('No SRTM DEM')
    return lon_lat_list, download_urls


def srtm_dem11(s, n, w, e, flag):
    # 30m or 90m srtm dem of 1*1 degree
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
    s, n, w, e = bound[0], bound[1], bound[2], bound[3]
    if w >= e or s >= n:
        print('Error bound, please reset it (S N W E)!')
        sys.exit()
    else:
        if flag.upper() == 'SRTM9011':
            lon_lat, download_urls = srtm_dem11(s, n, w, e, flag)
        elif flag.upper() == 'SRTM3011':
            lon_lat, download_urls = srtm_dem11(s, n, w, e, flag)
        elif flag.upper() == 'SRTM9055':
            lon_lat, download_urls = srtm_dem9055(s, n, w, e)
        elif flag.upper() == 'ALOS':
            lon_lat, download_urls = alos_dem(s, n, w, e)
        else:
            print('Error flag, please reset it!')
            sys.exit()
    print("\nDownloading urls of all DEM:")
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
  # only get urls of srtm30 or srtm90 (1*1 degree)
  python download_dem.py srtm30 30 40 100 105
  # get urls srtm90 and download them (5*5 degrees)
  python download_dem.py srtm9055 30 40 100 105 /ly/dem
  # get urls of alos DEM and download them
  python download_dem.py alos 30 40 100 105 /ly/dem
'''


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description=
        'Download SRTM DEM [30m 90m] or ALOS DSM [30m].',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)
    parser.add_argument('flag',
        type=str,
        help='DEM type (alos, ALOS, srtm9011, srtm3011, SRTM9011, SRTM3011, srtm9055, SRTM9055)')
    parser.add_argument('bound',
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
    out_dir = args.out_dir
    if out_dir:
        out_dir = os.path.abspath(out_dir)
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
    # get urls of DEM
    download_urls = get_urls(flag, bound)
    # download DEM
    if flag.upper() in ['ALOS', 'SRTM9055'] and out_dir:
        print("start to download:")
        for url in download_urls:
            print(f"{url.split('/')[-1]}")
            download_dem(url, out_dir)
    if flag.upper() in ['SRTM3011', 'SRTM9011'] and out_dir:
        print('cannot download SRTM DEM (1*1 degree), you have to download them manually.')


if __name__ == "__main__":
    main()
