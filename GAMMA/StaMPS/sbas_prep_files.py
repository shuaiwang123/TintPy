#!/usr/bin/env python3
################################################################################
# prepare necessary files processde by GAMMA for StaMPS SBAS processing        #
# Copyright (c) 2020, Lei Yuan                                                 #
################################################################################

# Expected directory structure:
#   SMALL_BASELINES/YYYYMMDD_YYYYMMDD/YYYYMMDD.rslc (master)
#   SMALL_BASELINES/YYYYMMDD_YYYYMMDD/YYYYMMDD.rslc (slave)
#   SMALL_BASELINES/YYYYMMDD_YYYYMMDD/*.rslc.par
#   SMALL_BASELINES/YYYYMMDD_YYYYMMDD/*.diff
#   SMALL_BASELINES/YYYYMMDD_YYYYMMDD/*.base
#   geo/*dem.rdc
#   geo/*diff_par
#   geo/YYYYMMDD.lon (master)
#   geo/YYYYMMDD.lat (master)
#   dem/*_seg.par

import os
import argparse
import glob
import shutil
import re

USAGE = """
  # for singlelooked interferogram
  sbas_prep_files.py ./rslc ./stacking 20200202 ./ 
  # for multilooked interferogram
  sbas_prep_files.py ./rslc ./stacking 20200202 ./  --ml_flag True
"""


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description=
        'Prepare necessary files processde by GAMMA for StaMPS SBAS processing.',
        usage=USAGE,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('rslc_dir', help='path of rslc directory')
    parser.add_argument('stacking_dir', help='path of stacking directory')
    parser.add_argument('supermaster', help='supermaster for coregistration')
    parser.add_argument('output_dir',
                        help='parent directory of INSAR_supermaster')
    parser.add_argument(
        '--ml_flag',
        help='flag of multilook interferotram (default: False)',
        default=False,
        type=bool)

    inps = parser.parse_args()
    return inps


def read_gamma_par(par_file, keyword):
    value = ''
    with open(par_file, 'r') as f:
        for l in f.readlines():
            if l.count(keyword) == 1:
                tmp = l.split(':')
                value = tmp[1].strip()
    return value


def gen_lon_lat(stacking_dir, supermaster, geo_dir):
    # get files
    sm_dir = glob.glob(os.path.join(stacking_dir, '*' + supermaster + '*'))[0]
    print(sm_dir)
    dem_par = os.path.join(sm_dir, 'dem_seg.par')
    lt_fine = os.path.join(sm_dir, 'lookup_fine')
    diff_par = os.path.join(sm_dir, os.path.split(sm_dir)[-1] + '.diff.par')
    # width of interferogram
    width = read_gamma_par(diff_par, 'range_samp_1')
    # length of inerferogram
    length = read_gamma_par(diff_par, 'az_samp_1')
    # Extract geocoding information to generate the lon and lat matrices
    lat = float(read_gamma_par(dem_par, 'corner_lat').split()[0])
    lon = float(read_gamma_par(dem_par, 'corner_lon').split()[0])
    lat_step = float(read_gamma_par(dem_par, 'post_lat').split()[0])
    lon_step = float(read_gamma_par(dem_par, 'post_lon').split()[0])
    length_dem = int(read_gamma_par(dem_par, 'nlines'))
    width_dem = int(read_gamma_par(dem_par, 'width'))
    lat1 = lat + lat_step * (length_dem - 1)
    lat1 = round(float(lat1), 6)
    lon1 = lon + lon_step * (width_dem - 1)
    lon1 = round(float(lon1), 6)
    # change path of running
    os.chdir(geo_dir)
    # longitude file
    cmd = f"gmt grdmath -R{lon}/{lon1}/{lat1}/{lat} -I{width_dem}+/{length_dem}+ X = geo.grd"
    os.system(cmd)
    # take lons
    cmd = f"gmt grd2xyz geo.grd -ZTLf > geo.raw"
    os.system(cmd)
    # set lons to 4-byte floats
    cmd = f"swap_bytes geo.raw geolon.raw 4"
    os.system(cmd)
    # geocode
    cmd = f"geocode {lt_fine} geolon.raw {width_dem} {supermaster + '.lon'} {width} {length} 2 0"
    os.system(cmd)

    # latitude file
    cmd = f"gmt grdmath -R{lon}/{lon1}/{lat1}/{lat} -I{width_dem}+/{length_dem}+ Y = geo.grd"
    os.system(cmd)
    # take lats
    cmd = f"gmt grd2xyz geo.grd -ZTLf > geo.raw"
    os.system(cmd)
    # set lats to 4-byte floats
    cmd = f"swap_bytes geo.raw geolat.raw 4"
    os.system(cmd)
    # geocode
    cmd = f"geocode {lt_fine} geolat.raw {width_dem} {supermaster + '.lat'} {width} {length} 2 0"
    os.system(cmd)

    # cleaning
    cmd = f"rm -rf geo.raw geolon.raw geolat.raw geo.grd gmt.history"
    os.system(cmd)


def prep_files(stacking_dir, rslc_dir, supermaster, output_dir, ml_flag):
    bar_msg = '------------------------------------------------------'
    # create directoried
    insar_dir = os.path.join(output_dir, 'INSAR_' + supermaster)
    if not os.path.isdir(insar_dir):
        os.mkdir(insar_dir)
    sb_dir = os.path.join(insar_dir, 'SMALL_BASELINES')
    if not os.path.isdir(sb_dir):
        os.mkdir(sb_dir)
    geo_dir = os.path.join(insar_dir, 'geo')
    if not os.path.isdir(geo_dir):
        os.mkdir(geo_dir)
    dem_dir = os.path.join(insar_dir, 'dem')
    if not os.path.isdir(dem_dir):
        os.mkdir(dem_dir)
    # prep dem/*_seg.par
    sm_dir = glob.glob(os.path.join(stacking_dir, '*' + supermaster + '*'))[0]
    dem_par = os.path.join(sm_dir, 'dem_seg.par')
    dem_par_dst = os.path.join(dem_dir, supermaster + '_seg.par')
    print(bar_msg + 'prep dem/*_seg.par' + bar_msg)
    print(dem_par_dst + '\n')
    shutil.copy(dem_par, dem_par_dst)
    # prep geo/*dem.rdc
    dem_rdc = glob.glob(os.path.join(sm_dir, '*.rdc_hgt'))[0]
    dem_rdc_dst = os.path.join(geo_dir, supermaster + '.dem.rdc')
    print(bar_msg + 'prep geo/*dem.rdc' + bar_msg)
    print(dem_rdc_dst + '\n')
    shutil.copy(dem_rdc, dem_rdc_dst)
    # prep geo/*diff_par
    diff_par = glob.glob(os.path.join(sm_dir, '*.diff.par'))[0]
    diff_par_dst = os.path.join(geo_dir, supermaster + '.diff_par')
    print(bar_msg + 'prep geo/*diff_par' + bar_msg)
    print(diff_par_dst + '\n')
    shutil.copy(diff_par, diff_par_dst)
    # prep geo/YYYYMMDD.lon (master) geo/YYYYMMDD.lat (master)
    print(bar_msg + 'prep geo/*.lon *.lat' + bar_msg)
    gen_lon_lat(stacking_dir, supermaster, geo_dir)
    print('\n')
    # get ifg_pairs
    files = os.listdir(stacking_dir)
    ifg_pairs = [i for i in files if re.match('^\d{8}-\d{8}$', i)]
    print(bar_msg + 'prep .diff .base .rlsc .rslc.par' + bar_msg)
    # prep .diff .base .rlsc .rslc.par
    for ifg in ifg_pairs:
        # create directory
        ifg_dir = os.path.join(sb_dir, ifg.replace('-', '_'))
        if not os.path.isdir(ifg_dir):
            os.mkdir(ifg_dir)
        # .diff
        if ml_flag:
            diff = os.path.join(stacking_dir, ifg, ifg + '.diff')
        else:
            diff = os.path.join(stacking_dir, ifg, ifg + '.diff.int')
        diff_dst = os.path.join(ifg_dir, ifg.replace('-', '_') + '.diff')
        print(diff_dst)
        shutil.copy(diff, diff_dst)
        # .base
        baseline = os.path.join(stacking_dir, ifg, ifg + '.base')
        baseline_dst = os.path.join(ifg_dir, ifg.replace('-', '_') + '.base')
        print(baseline_dst)
        shutil.copy(baseline, baseline_dst)
        # master.rslc master.rslc.par
        master, slave = ifg[0:8], ifg[9:17]
        m_rslc = os.path.join(rslc_dir, master, master + '.rslc')
        m_rslc_par = m_rslc + '.par'
        print(os.path.join(ifg_dir, m_rslc + '.rslc'))
        shutil.copy(m_rslc, ifg_dir)
        print(os.path.join(ifg_dir, m_rslc + '.rslc.par'))
        shutil.copy(m_rslc_par, ifg_dir)
        # slave.rslc slave.rslc.par
        s_rslc = os.path.join(stacking_dir, ifg, slave + '.rslc')
        s_rslc_par = s_rslc + '.par'
        print(os.path.join(ifg_dir, s_rslc + '.rslc'))
        shutil.copy(s_rslc, ifg_dir)
        print(os.path.join(ifg_dir, s_rslc + '.rslc.par'))
        shutil.copy(s_rslc_par, ifg_dir)
    print('All done.')


def run():
    # get inputs
    inps = cmdline_parser()
    rslc_dir = inps.rslc_dir
    rslc_dir = os.path.abspath(rslc_dir)
    stacking_dir = inps.stacking_dir
    stacking_dir = os.path.abspath(stacking_dir)
    supermaster = inps.supermaster
    output_dir = inps.output_dir
    output_dir = os.path.abspath(output_dir)
    ml_flag = inps.ml_flag
    # run
    prep_files(stacking_dir, rslc_dir, supermaster, output_dir, ml_flag)


if __name__ == "__main__":
    run()
    # gen_lon_lat('/media/ly/3TB/ALOS550/stacking_ml', '20180103',
    #             '/media/ly/3TB/ALOS550/geo')
