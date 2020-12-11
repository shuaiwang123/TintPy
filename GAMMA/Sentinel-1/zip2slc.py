#!/usr/bin/env python3
###############################################################################
# Generate SLC from Sentinel-1 raw data with orbit correction using GAMMA     #
# Copyright (c) 2020, Lei Yuan                                                #
###############################################################################

import os
import re
import sys
import glob
import datetime
import argparse
import shutil


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Generate SLC from Sentinel-1 raw data with orbit correction using GAMMA.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=EXAMPLE)

    parser.add_argument('s1_zip_dir', help='Sentinel-1 zip directory')
    parser.add_argument(
        'orbit_dir', help='precise orbit directory path for orbit correction')
    parser.add_argument('slc_dir', help='directory path for saving slc')
    parser.add_argument('iw_num',
                        help='IW number. e.g., 1 or 1 2 or 1 2 3',
                        type=int,
                        nargs='+')
    parser.add_argument(
        '--rlks',
        help='range looks for generating amplitude image (default: 20)',
        type=int,
        default=20)
    parser.add_argument(
        '--alks',
        help='azimuth looks for generating amplitude image (default: 5)',
        type=int,
        default=5)
    inps = parser.parse_args()

    return inps


EXAMPLE = """Example:
  # for iw1
  ./zip2slc.py /ly/zip_dir /ly/orbits /ly/slc 1
  # for iw1 iw2 and iw3
  ./zip2slc.py /ly/zip_dir /ly/orbits /ly/slc 1 2 3 --rlks 8 --alks 2
"""


def get_s1_date(zip_file):
    file = os.path.basename(zip_file)
    date = re.findall(r'\d{8}', file)[0]
    return date


def get_s1_date_and_frequency(zip_files):
    dates = []
    date_dict = {}
    for file in zip_files:
        name = os.path.basename(file)
        date = re.findall(r'\d{8}', name)[0]
        dates.append(date)
    for d in dates:
        date_dict[d] = dates.count(d)
    return date_dict


def get_satellite(zip_file):
    if 'S1A_IW_SLC_' in os.path.basename(zip_file):
        satellite = 'S1A'
    else:
        satellite = 'S1B'

    return satellite


def get_orbit_date(s1_date):
    date = datetime.datetime(int(s1_date[0:4]), int(s1_date[4:6]),
                             int(s1_date[6:8]))
    delta = datetime.timedelta(days=-1)
    tmp = date + delta
    orbit_date = tmp.strftime('%Y%m%d')
    return orbit_date


def get_orbit_file_name(s1_date, orbit_dir, zip_file):
    satellite = get_satellite(zip_file)
    orbit_date = get_orbit_date(s1_date)
    orbit_file_name = None
    for i in os.listdir(orbit_dir):
        if orbit_date in i and i.endswith('.EOF') and i.startswith(satellite):
            orbit_file_name = i
    return orbit_file_name


def read_gamma_par(par_file, keyword):
    value = ''
    with open(par_file, 'r') as f:
        for l in f.readlines():
            if l.count(keyword) == 1:
                tmp = l.split(':')
                value = tmp[1].strip()
    return value


def check_inputs(zip_file, orbit_dir, slc_dir, iw_num):
    # check zip file
    if not os.path.exists(zip_file):
        print('cannot find {}.'.format(zip_file))
        sys.exit(1)
    # check orbit directory
    if not os.path.exists(orbit_dir):
        print('{} not exists.'.format(orbit_dir))
        sys.exit(1)
    # check slc directory
    if not os.path.exists(slc_dir):
        os.mkdir(slc_dir)
    # check iw number
    for i in iw_num:
        if not i in [1, 2, 3]:
            print('IW{} not exists.'.format(i))
            sys.exit(1)


def unzip_file(safe_dir, zip_file, zip_file_dir, aux_file):
    if not os.path.isdir(safe_dir):
        call_str = 'unzip ' + zip_file + ' -d ' + zip_file_dir + ' > ' + aux_file
        print('\nunzip {}......'.format(zip_file))
        os.system(call_str)
        print('done.\n')


def generate_slc(safe_dir, slc_path, s1_date, iw_num, aux_file):
    measurement_dir = safe_dir + '/measurement'
    annotation_dir = safe_dir + '/annotation'
    calibration_dir = safe_dir + '/annotation/calibration'

    slc_tab = slc_path + '/' + s1_date + '_slc_tab'
    if os.path.isfile(slc_tab):
        os.remove(slc_tab)

    for i in iw_num:
        slc = slc_path + '/' + s1_date + '.iw' + str(i) + '.slc'
        slc_par = slc_path + '/' + s1_date + '.iw' + str(i) + '.slc.par'
        tops_par = slc_path + '/' + s1_date + '.iw' + str(i) + '.slc.tops_par'

        call_str = 'echo ' + slc + ' ' + slc_par + ' ' + tops_par + ' > ' + slc_tab
        os.system(call_str)

        MEASUREMENT = glob.glob(measurement_dir + '/*iw' + str(i) + '*vv*tiff')
        ANNOTATION = glob.glob(annotation_dir + '/*iw' + str(i) + '*vv*xml')
        CALIBRATION = glob.glob(calibration_dir + '/calibration*' + 'iw' +
                                str(i) + '*vv*')
        NOISE = glob.glob(calibration_dir + '/noise*' + 'iw' + str(i) + '*vv*')

        if not NOISE:
            call_str = 'par_S1_SLC ' + MEASUREMENT[0] + ' ' + ANNOTATION[
                0] + ' ' + CALIBRATION[
                    0] + ' - ' + slc_par + ' ' + slc + ' ' + tops_par + ' >> ' + aux_file
        else:
            call_str = 'par_S1_SLC ' + MEASUREMENT[0] + ' ' + ANNOTATION[
                0] + ' ' + CALIBRATION[0] + ' ' + NOISE[
                    0] + ' ' + slc_par + ' ' + slc + ' ' + tops_par + ' >> ' + aux_file
        print('generate SLC parameter and image files......')
        os.system(call_str)
        print('done.\n')


def orbit_correction(s1_date, orbit_dir, slc_path, aux_file, zip_file):
    orbit_file_name = get_orbit_file_name(s1_date, orbit_dir, zip_file)
    if orbit_file_name:
        orbit_file_path = os.path.join(orbit_dir, orbit_file_name)
    else:
        print('cannot find precisce orbit.')
        orbit_file_path = ''
    # orbit correction
    slc_pars = glob.glob(slc_path + '/*.iw*.slc.par')
    for i in range(len(slc_pars)):
        if orbit_file_path:
            call_str = 'S1_OPOD_vec.vec' + ' ' + slc_pars[
                i] + ' ' + orbit_file_path + ' >> ' + aux_file
            print('orbit correction......')
            os.system(call_str)
            print('done.\n')


def generate_amp(slc_path, aux_file, rlks, alks):
    slcs = glob.glob(slc_path + '/*.iw*.slc')
    for slc in slcs:
        slc_par = slc + '.par'
        bmp = slc + '.bmp'
        width = read_gamma_par(slc_par, 'range_samples:')
        call_str = 'rasSLC ' + slc + ' ' + width + ' 1 0 ' + str(
            rlks) + ' ' + str(
                alks) + ' 1. .35 1 0 0 ' + bmp + ' >> ' + aux_file
        print('generate amplitude file......')
        os.system(call_str)
        print('done.\n')


def main():
    inps = cmdLineParse()
    # get inputs
    zip_dir = inps.s1_zip_dir
    orbit_dir = inps.orbit_dir
    slc_dir = inps.slc_dir
    iw_num = inps.iw_num
    rlks = inps.rlks
    alks = inps.alks
    # get all zip
    zip_files = glob.glob(zip_dir + '/S1*_IW_SLC*.zip')
    s1_date_frequency = get_s1_date_and_frequency(zip_files)

    for zip_file in zip_files:
        s1_date = get_s1_date(zip_file)

        # one date has multi images
        frequency = s1_date_frequency[s1_date]
        if frequency == 1:
            slc_path = os.path.join(slc_dir, s1_date)
        else:
            for i in range(1, frequency + 1):
                date_dir = os.path.join(slc_dir, s1_date + '-' + str(i))
                tmp = glob.glob(os.path.join(date_dir, '*.slc'))
                if not tmp:
                    slc_path = date_dir
                    break

        aux_file = os.path.join(slc_path, s1_date + '_aux')

        # check inputs
        check_inputs(zip_file, orbit_dir, slc_dir, iw_num)

        if not os.path.exists(slc_path):
            os.mkdir(slc_path)

        if len(os.path.dirname(zip_file)) == 0:
            zip_file_dir = sys.path[0]
        else:
            zip_file_dir = os.path.dirname(zip_file)

        safe_dir = zip_file.replace('.zip', '.SAFE')

        # unzip
        unzip_file(safe_dir, zip_file, zip_file_dir, aux_file)

        # generate slc
        generate_slc(safe_dir, slc_path, s1_date, iw_num, aux_file)

        # orbit_correction
        orbit_correction(s1_date, orbit_dir, slc_path, aux_file, zip_file)

        # generate amplitude file
        generate_amp(slc_path, aux_file, rlks, alks)

        # delete safe directory and slc_tab
        if os.path.isdir(safe_dir):
            shutil.rmtree(safe_dir)
        slc_tab = slc_path + '/' + s1_date + '_slc_tab'
        if os.path.isfile(slc_tab):
            os.remove(slc_tab)

        print("ZIP to SLC for %s is done!\n" % s1_date)
    sys.exit(1)


if __name__ == "__main__":
    main()
