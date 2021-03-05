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
    parser = argparse.ArgumentParser(
        description=
        'Generate SLC from Sentinel-1 raw data with orbit correction using GAMMA.',
        formatter_class=argparse.RawTextHelpFormatter,
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
    parser.add_argument(
        '--del_flag',
        help=
        'flag for deleting original Sentinel-1 zip data, t for deleting, f for not (default: f)',
        default='f')
    inps = parser.parse_args()

    return inps


EXAMPLE = """Example:
  # for iw1
  ./zip2slc.py /ly/zip_dir /ly/orbits /ly/slc 1
  # for iw1 iw2 and iw3
  ./zip2slc.py /ly/zip_dir /ly/orbits /ly/slc 1 2 3 --rlks 8 --alks 2 --del_flag t
"""


def get_s1_date(zip_file):
    file = os.path.basename(zip_file)
    date = re.findall(r'\d{8}', file)[0]
    return date


def get_all_s1_date(zip_files):
    dates = []
    for file in zip_files:
        date = get_s1_date(file)
        dates.append(date)
    dates = list(set(dates))
    return dates


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


def get_orbit_file_name(zip_file, orbit_dir):
    satellite = get_satellite(zip_file)
    s1_date = get_s1_date(zip_file)
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


def check_inputs(zip_dir, orbit_dir, slc_dir, iw_num, del_flag):
    # check zip directory
    if not os.path.isdir(zip_dir):
        print('{} not exists.'.format(zip_dir))
        sys.exit()
    # check orbit directory
    if not os.path.isdir(orbit_dir):
        print('{} not exists.'.format(orbit_dir))
        sys.exit()
    # check slc directory
    if not os.path.isdir(slc_dir):
        os.mkdir(slc_dir)
    # check iw number
    for i in iw_num:
        if not i in [1, 2, 3]:
            print('IW{} not exists.'.format(i))
            sys.exit()
    # check del_flag
    if del_flag not in ['t', 'f']:
        print("Error del_falg, it must be in ['t', 'f]")
        sys.exit()


def unzip_file(zip_file, log_file):
    safe_dir = zip_file.replace('.zip', '.SAFE')
    zip_file_dir = os.path.dirname(zip_file)
    if os.path.isdir(safe_dir):
        shutil.rmtree(safe_dir)
    call_str = 'unzip ' + zip_file + ' -d ' + zip_file_dir + ' > ' + log_file
    print('\nunzip {}......'.format(os.path.basename(zip_file)))
    os.system(call_str)
    print('done.\n')


def generate_slc(safe_dir, slc_path, iw_num, log_file):
    s1_date = get_s1_date(os.path.basename(safe_dir))

    measurement_dir = safe_dir + '/measurement'
    annotation_dir = safe_dir + '/annotation'
    calibration_dir = safe_dir + '/annotation/calibration'

    slc_tab = slc_path + '/' + s1_date + '_slc_tab'
    if os.path.isfile(slc_tab):
        os.remove(slc_tab)

    for i in iw_num:
        i = str(i)
        slc = slc_path + '/' + s1_date + '.iw' + i + '.slc'
        slc_par = slc_path + '/' + s1_date + '.iw' + i + '.slc.par'
        tops_par = slc_path + '/' + s1_date + '.iw' + i + '.slc.tops_par'

        call_str = 'echo ' + slc + ' ' + slc_par + ' ' + tops_par + ' > ' + slc_tab
        os.system(call_str)

        MEASUREMENT = glob.glob(measurement_dir + '/*iw' + i + '*vv*tiff')
        ANNOTATION = glob.glob(annotation_dir + '/*iw' + i + '*vv*xml')
        CALIBRATION = glob.glob(calibration_dir + '/calibration*' + 'iw' + i +
                                '*vv*')
        NOISE = glob.glob(calibration_dir + '/noise*' + 'iw' + i + '*vv*')

        if not NOISE:
            call_str = 'par_S1_SLC ' + MEASUREMENT[0] + ' ' + ANNOTATION[
                0] + ' ' + CALIBRATION[
                    0] + ' - ' + slc_par + ' ' + slc + ' ' + tops_par + ' >> ' + log_file
        else:
            call_str = 'par_S1_SLC ' + MEASUREMENT[0] + ' ' + ANNOTATION[
                0] + ' ' + CALIBRATION[0] + ' ' + NOISE[
                    0] + ' ' + slc_par + ' ' + slc + ' ' + tops_par + ' >> ' + log_file
        print(
            'generate SLC image and parameter files for iw{}......'.format(i))
        os.system(call_str)
        print('done.\n')
    # delete safe directory and slc_tab
    shutil.rmtree(safe_dir)
    os.remove(slc_tab)


def orbit_correction(orbit_dir, slc_path, zip_file, log_file):
    orbit_file_name = get_orbit_file_name(zip_file, orbit_dir)
    s1_date = get_s1_date(zip_file)
    if orbit_file_name:
        orbit_file_path = os.path.join(orbit_dir, orbit_file_name)
    else:
        print('cannot find precisce orbit for {}.'.format(s1_date))
        orbit_file_path = None
    # orbit correction
    slc_pars = glob.glob(slc_path + '/*.iw*.slc.par')
    for slc_par in slc_pars:
        if orbit_file_path:
            call_str = 'S1_OPOD_vec.vec' + ' ' + slc_par + ' ' + orbit_file_path + ' >> ' + log_file
            iw = re.findall(r'iw\d{1}', os.path.basename(slc_par))[0]
            print('orbit correction for {}......'.format(iw))
            os.system(call_str)
            print('done.\n')


def generate_amp(slc_path, rlks, alks, log_file):
    slcs = glob.glob(slc_path + '/*.iw*.slc')
    for slc in slcs:
        slc_par = slc + '.par'
        bmp = slc + '.bmp'
        width = read_gamma_par(slc_par, 'range_samples:')
        call_str = 'rasSLC ' + slc + ' ' + width + ' 1 0 ' + str(
            rlks) + ' ' + str(
                alks) + ' 1. .35 1 0 0 ' + bmp + ' >> ' + log_file
        iw = re.findall(r'iw\d{1}', os.path.basename(slc_par))[0]
        print('generate amplitude file for {}......'.format(iw))
        os.system(call_str)
        print('done.\n')


def run_all(zip_file, slc_path, orbit_dir, iw_num, rlks, alks, del_flag):
    s1_date = get_s1_date(zip_file)
    # log file
    log_file = os.path.join(slc_path, s1_date + '.log')
    # unzip
    unzip_file(zip_file, log_file)
    # generate slc
    safe_dir = zip_file.replace('.zip', '.SAFE')
    generate_slc(safe_dir, slc_path, iw_num, log_file)
    # orbit correction
    orbit_correction(orbit_dir, slc_path, zip_file, log_file)
    # generate amplitude file for quickview
    generate_amp(slc_path, rlks, alks, log_file)
    # delete zip data
    if del_flag == 't':
        os.remove(zip_file)


def main():
    # parse args
    inps = cmdLineParse()
    # get inputs
    zip_dir = os.path.abspath(inps.s1_zip_dir)
    orbit_dir = os.path.abspath(inps.orbit_dir)
    slc_dir = os.path.abspath(inps.slc_dir)
    iw_num = inps.iw_num
    rlks = inps.rlks
    alks = inps.alks
    del_flag = inps.del_flag.lower()
    # check inputs
    check_inputs(zip_dir, orbit_dir, slc_dir, iw_num, del_flag)
    # get all zips
    zip_files = glob.glob(zip_dir + '/S1*_IW_SLC*.zip')
    # get all dates
    dates = get_all_s1_date(zip_files)
    num = 1
    for date in dates:
        # get zipfiles
        same_date_zips = glob.glob(zip_dir + '/S1*' + date + '*.zip')
        same_date_zips = sorted(same_date_zips, key=lambda i: i[26:32])
        if len(same_date_zips) == 1:
            zip_file = same_date_zips[0]
            slc_path = os.path.join(slc_dir, date)
            if not os.path.isdir(slc_path):
                os.mkdir(slc_path)
            run_all(zip_file, slc_path, orbit_dir, iw_num, rlks, alks,
                    del_flag)
            print("[{}] {} zip2slc for {} is done {}\n".format(num, '>' * 10, date, '<' * 10))
            num += 1
        else:
            for i in range(len(same_date_zips)):
                zip_file = same_date_zips[i]
                slc_path = os.path.join(slc_dir, date + '-' + str(i + 1))
                if not os.path.isdir(slc_path):
                    os.mkdir(slc_path)
                run_all(zip_file, slc_path, orbit_dir, iw_num, rlks, alks,
                        del_flag)
                print("[{}] {} zip2slc for {} is done {}\n".format(num, '>' * 10, date, '<' * 10))
                num += 1


if __name__ == "__main__":
    main()
