#!/usr/bin/env python3
#######################################################################################
# prepare necessary files(multilooked) processed by GAMMA for StaMPS SBAS processing  #
# Copyright (c) 2020, Lei Yuan                                                        #
#######################################################################################

# Expected directory structure:
#
# SB:
#   SMALL_BASELINES/YYYYMMDD_YYYYMMDD/*.diff
#   SMALL_BASELINES/YYYYMMDD_YYYYMMDD/*.cc
#   SMALL_BASELINES/YYYYMMDD_YYYYMMDD/*.base
#   SLC/*.mli  (single master)
#   SLC/*.mli.par  (single master)
#   rslc/*.mli (single master slaves)
#   geo/*dem.rdc (1 file)
#   geo/*.lon (1 file)
#   geo/*.lat (1 file)

import os
import argparse
import glob
import shutil
import re

EXAMPLE = """Example:
  ./perp_sbas_mli.py ./stacking 20200202 ./
"""


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description=
        'Prepare necessary files(multilooked) processed by GAMMA for StaMPS SBAS processing.',
        epilog=EXAMPLE,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('stacking_dir', help='path of stacking directory')
    parser.add_argument('supermaster', help='supermaster for coregistration')
    parser.add_argument('output_dir',
                        help='parent directory of INSAR_supermaster')

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
    diff_par = glob.glob(os.path.join(sm_dir, '*.diff.par'))[0]
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
    cmd = "gmt grd2xyz geo.grd -ZTLf > geo.raw"
    os.system(cmd)
    # set lons to 4-byte floats
    cmd = "swap_bytes geo.raw geolon.raw 4"
    os.system(cmd)
    # geocode
    cmd = f"geocode {lt_fine} geolon.raw {width_dem} {supermaster + '.lon'} {width} {length} 2 0"
    os.system(cmd)

    # latitude file
    cmd = f"gmt grdmath -R{lon}/{lon1}/{lat1}/{lat} -I{width_dem}+/{length_dem}+ Y = geo.grd"
    os.system(cmd)
    # take lats
    cmd = "gmt grd2xyz geo.grd -ZTLf > geo.raw"
    os.system(cmd)
    # set lats to 4-byte floats
    cmd = "swap_bytes geo.raw geolat.raw 4"
    os.system(cmd)
    # geocode
    cmd = f"geocode {lt_fine} geolat.raw {width_dem} {supermaster + '.lat'} {width} {length} 2 0"
    os.system(cmd)

    # cleaning
    cmd = "rm -rf geo.raw geolon.raw geolat.raw geo.grd gmt.history"
    os.system(cmd)


def prep_files(stacking_dir, supermaster, output_dir):
    bar_msg = '------------------------------------------------------'
    # create directories
    insar_dir = os.path.join(output_dir, 'INSAR_' + supermaster)
    if not os.path.isdir(insar_dir):
        os.mkdir(insar_dir)
    sb_dir = os.path.join(insar_dir, 'SMALL_BASELINES')
    if not os.path.isdir(sb_dir):
        os.mkdir(sb_dir)
    geo_dir = os.path.join(insar_dir, 'geo')
    if not os.path.isdir(geo_dir):
        os.mkdir(geo_dir)
    slc_dir = os.path.join(insar_dir, 'SLC')
    if not os.path.isdir(slc_dir):
        os.mkdir(slc_dir)
    rslc_dir = os.path.join(insar_dir, 'rslc')
    if not os.path.isdir(rslc_dir):
        os.mkdir(rslc_dir)

    sm_dir = glob.glob(os.path.join(stacking_dir, '*' + supermaster + '*'))[0]
    # prep slc/*.mli slc/*.mli.par  (single master)
    mli = glob.glob(os.path.join(sm_dir, '*.pwr1'))[0]
    mli_par = glob.glob(os.path.join(sm_dir, '*.pwr1.par'))[0]
    mli_dst = os.path.join(slc_dir, supermaster + '.mli')
    mli_par_dst = mli_dst + '.par'
    print(bar_msg + 'prep slc/*.mli slc/*.mli.par  (single master)' + bar_msg)
    print(mli_dst)
    shutil.copy(mli, mli_dst)
    print(mli_par_dst)
    shutil.copy(mli_par, mli_par_dst)
    print('\n')

    # prep geo/*dem.rdc
    dem_rdc = glob.glob(os.path.join(sm_dir, '*.rdc_hgt'))[0]
    dem_rdc_dst = os.path.join(geo_dir, supermaster + '.dem.rdc')
    print(bar_msg + 'prep geo/*dem.rdc' + bar_msg)
    print(dem_rdc_dst + '\n')
    shutil.copy(dem_rdc, dem_rdc_dst)

    # prep geo/YYYYMMDD.lon (master) geo/YYYYMMDD.lat (master)
    print(bar_msg + 'prep geo/*.lon *.lat' + bar_msg)
    gen_lon_lat(stacking_dir, supermaster, geo_dir)
    print('\n')

    # get ifg_pairs
    files = os.listdir(stacking_dir)
    ifg_pairs = [i for i in files if re.match(r'^\d{8}[-_]\d{8}$', i)]
    print(bar_msg + 'prep .diff .base .rlsc .rslc.par' + bar_msg)
    # prep .diff .base .cc .mli(single master slaves)
    for ifg in ifg_pairs:
        # create directory
        ifg_out = ifg.replace('-', '_')
        ifg_in_dir = os.path.join(stacking_dir, ifg)
        ifg_out_dir = os.path.join(sb_dir, ifg_out)
        if not os.path.isdir(ifg_out_dir):
            os.mkdir(ifg_out_dir)
        # .diff
        diff = glob.glob(os.path.join(ifg_in_dir, '*.diff.int'))[0]
        diff_dst = os.path.join(ifg_out_dir, ifg_out + '.diff')
        print(diff_dst)
        shutil.copy(diff, diff_dst)
        # .base
        baseline = glob.glob(os.path.join(ifg_in_dir, '*.base'))[0]
        baseline_dst = os.path.join(ifg_out_dir, ifg_out + '.base')
        print(baseline_dst)
        shutil.copy(baseline, baseline_dst)
        # .cc
        cc = glob.glob(os.path.join(ifg_in_dir, '*.corr'))[0]
        cc_dst = os.path.join(ifg_out_dir, ifg_out + '.cc')
        print(cc_dst)
        shutil.copy(cc, cc_dst)
        # .mli
        mli1 = glob.glob(os.path.join(ifg_in_dir, '*.pwr1'))[0]
        mli1_dst = os.path.join(rslc_dir, ifg[0:8] + '.mli')
        mli2 = glob.glob(os.path.join(ifg_in_dir, '*.pwr2'))[0]
        mli2_dst = os.path.join(rslc_dir, ifg[9:17] + '.mli')
        if not os.path.isfile(mli1_dst):
            print(mli1_dst)
            shutil.copy(mli1, mli1_dst)
        if not os.path.isfile(mli2_dst):
            print(mli2_dst)
            shutil.copy(mli2, mli2_dst)
    print('\nAll done, you can run command mt_ml_select_gamma in matlab, enjoy it.')


def run():
    # get inputs
    inps = cmdline_parser()
    stacking_dir = inps.stacking_dir
    stacking_dir = os.path.abspath(stacking_dir)
    supermaster = inps.supermaster
    output_dir = inps.output_dir
    output_dir = os.path.abspath(output_dir)
    # run
    prep_files(stacking_dir, supermaster, output_dir)


if __name__ == "__main__":
    run()
