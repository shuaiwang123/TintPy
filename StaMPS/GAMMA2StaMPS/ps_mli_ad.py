#!/usr/bin/env python3
#####################################################################################
# prepare necessary files(multilooked) processed by GAMMA for StaMPS PS processing  #
# Copyright (c) 2020, Lei Yuan                                                      #
#####################################################################################

# Expected directory structure:
#
# PS:
#   rslc/*.rslc
#   rslc/*.rslc.par
#   diff0/*.diff
#   diff0/*.base
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

EXAMPLE = """Example:
  ./ps_mli_ad.py ./stacking ./
"""


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description=
        'Prepare necessary files(multilooked) processed by GAMMA for StaMPS PS processing.',
        epilog=EXAMPLE,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('stacking_dir', help='path of stacking directory')
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


def gen_lon_lat(stacking_dir, supermaster, sm_dir, geo_dir):
    # get files
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


def modify_par(par_in, par_out):
    with open(par_in, 'r') as f:
        par_content = f.read()
        par_content = par_content.replace('FLOAT', 'FCOMPLEX')
    with open(par_out, 'w+') as f:
        f.write(par_content)


def prep_rslc_and_diff0_dir(stacking_dir, insar_dir):
    # mkdir
    rslc_dir = os.path.join(insar_dir, 'rslc')
    if not os.path.isdir(rslc_dir):
        os.mkdir(rslc_dir)
    diff0_dir = os.path.join(insar_dir, 'diff0')
    if not os.path.isdir(diff0_dir):
        os.mkdir(diff0_dir)
    # get width
    diff_par = glob.glob(os.path.join(stacking_dir, '*', '*.diff.par'))[0]
    width = read_gamma_par(diff_par, 'range_samples')
    # get ifg_pairs
    files = os.listdir(stacking_dir)
    ifg_pairs = sorted([i for i in files if re.match(r'^\d{8}[-_]\d{8}$', i)])
    for ifg in ifg_pairs:
        ifg_out = ifg.replace('-', '_')
        ifg_in_dir = os.path.join(stacking_dir, ifg)
        # prep .diff
        diff = glob.glob(os.path.join(ifg_in_dir, '*.diff.int'))[0]
        diff_dst = os.path.join(diff0_dir, ifg_out + '.diff')
        print(diff_dst)
        shutil.copy(diff, diff_dst)
        # prep .base
        baseline = glob.glob(os.path.join(ifg_in_dir, '*.base'))[0]
        baseline_dst = os.path.join(diff0_dir, ifg_out + '.base')
        print(baseline_dst)
        shutil.copy(baseline, baseline_dst)
        # prep .rslc and .rslc.par
        # real_to_cpx
        # supermaster rslc and rslc.par
        mli1 = glob.glob(os.path.join(ifg_in_dir, '*.pwr1'))[0]
        mli1_dst = os.path.join(rslc_dir, ifg[0:8] + '.rslc')
        if not os.path.isfile(mli1_dst):
            call_str = f"real_to_cpx {mli1} - {mli1_dst} {width} 0"
            os.system(call_str)
            # get content of mli.par and modify it
            mli1_par = glob.glob(os.path.join(ifg_in_dir, '*pwr1.par'))[0]
            mli1_par_dst = mli1_dst + '.par'
            modify_par(mli1_par, mli1_par_dst)
        # slaves rslc and rslc.par
        mli2 = glob.glob(os.path.join(ifg_in_dir, '*.pwr2'))[0]
        mli2_dst = os.path.join(rslc_dir, ifg[9:17] + '.rslc')
        call_str = f"real_to_cpx {mli2} - {mli2_dst} {width} 0"
        os.system(call_str)
        # get content of mli.par and modify it
        mli2_par = glob.glob(os.path.join(ifg_in_dir, '*pwr2.par'))[0]
        mli2_par_dst = mli2_dst + '.par'
        modify_par(mli2_par, mli2_par_dst)


def prep_geo_dir(stacking_dir, supermaster, sm_dir, insar_dir):
    bar_msg = '------------------------------------------------------'
    # mkdir
    geo_dir = os.path.join(insar_dir, 'geo')
    if not os.path.isdir(geo_dir):
        os.mkdir(geo_dir)
    # prep geo/*dem.rdc
    dem_rdc = glob.glob(os.path.join(sm_dir, '*.rdc_hgt'))[0]
    dem_rdc_dst = os.path.join(geo_dir, supermaster + '.dem.rdc')
    print(bar_msg + 'prep geo/*dem.rdc' + bar_msg)
    print(dem_rdc_dst + '\n')
    shutil.copy(dem_rdc, dem_rdc_dst)
    # prep geo/*diff_par
    diff_par = glob.glob(os.path.join(sm_dir, '*.diff.par'))[0]
    diff_par_dst = os.path.join(geo_dir, supermaster + '.diff_par')
    print(diff_par_dst + '\n')
    shutil.copy(diff_par, diff_par_dst)
    # prep geo/YYYYMMDD.lon (master) geo/YYYYMMDD.lat (master)
    print(bar_msg + 'prep geo/*.lon *.lat' + bar_msg)
    gen_lon_lat(stacking_dir, supermaster, sm_dir, geo_dir)
    print('\n')


def prep_dem_dir(stacking_dir, supermaster, sm_dir, insar_dir):
    # mkdir
    dem_dir = os.path.join(insar_dir, 'dem')
    if not os.path.isdir(dem_dir):
        os.mkdir(dem_dir)
    # dem/*_seg.par
    seg_par = os.path.join(sm_dir, 'dem_seg.par')
    seg_par_dst = os.path.join(dem_dir, supermaster + '_seg.par')
    shutil.copy(seg_par, seg_par_dst)


def prep_files(stacking_dir, output_dir):
    # get supermaster and sm_dir
    files = os.listdir(stacking_dir)
    ifg_pairs = sorted([i for i in files if re.match(r'^\d{8}[-_]\d{8}$', i)])
    supermaster = ifg_pairs[0][0:8]
    sm_dir = os.path.join(stacking_dir, ifg_pairs[0])
    # mkdir
    insar_dir = os.path.join(output_dir, 'INSAR_' + supermaster)
    if not os.path.isdir(insar_dir):
        os.mkdir(insar_dir)
    # rslc and diff0
    prep_rslc_and_diff0_dir(stacking_dir, insar_dir)
    # geo
    prep_geo_dir(stacking_dir, supermaster, sm_dir, insar_dir)
    # dem
    prep_dem_dir(stacking_dir, supermaster, sm_dir, insar_dir)
    print(
        '\nAll done, you can run command mt_prep_gamma in terminal, enjoy it.')


def run():
    # get inputs
    inps = cmdline_parser()
    stacking_dir = inps.stacking_dir
    stacking_dir = os.path.abspath(stacking_dir)
    output_dir = inps.output_dir
    output_dir = os.path.abspath(output_dir)
    # run
    prep_files(stacking_dir, output_dir)


if __name__ == "__main__":
    run()
