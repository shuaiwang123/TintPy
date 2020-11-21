#!/usr/bin/env python3
#######################################################
# Prepare preprocessed files using GAMMA for MintPy   #
# Copyright (c) 2020, Lei Yuan                        #
#######################################################

import os
import re
import argparse
import shutil
import glob
import sys


def cmd_line_parser():
    parser = argparse.ArgumentParser(description='Prepare files for MintPy time series processing.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     usage=EXAMPLE)

    parser.add_argument(
        'mintpy_dir', help='directory path for MintPy time series processing.')
    parser.add_argument('stacking_dir', help='directory path of stacking.')
    parser.add_argument('--rlks',
                        help='range looks for generating bmp',
                        type=int,
                        default=20)
    parser.add_argument('--alks',
                        help='azimuth looks for generating bmp',
                        type=int,
                        default=5)
    inps = parser.parse_args()

    return inps


EXAMPLE = """
  ./prep_files.py /ly/mintpy /ly/stacking
  ./prep_files.py /ly/mintpy /ly/stacking --rlks 8 --alks 2
"""


def copy_file(src, dst):
    if os.path.isfile(src):
        print('copy {} into {}'.format(src, dst))
        shutil.copy(src, dst)
    else:
        print("\n{} not exists.\n".format(src))


def main():
    inps = cmd_line_parser()
    # get inputs
    mintpy_dir = inps.mintpy_dir
    stacking_dir = inps.stacking_dir
    mintpy_dir = os.path.abspath(mintpy_dir)
    stacking_dir = os.path.abspath(stacking_dir)
    rlks = str(inps.rlks)
    alks = str(inps.alks)

    if not os.path.isdir(mintpy_dir):
        os.mkdir(mintpy_dir)
    if not os.path.isdir(stacking_dir):
        print("{} not exists.".format(stacking_dir))
        sys.exit(1)

    # dir for mintpy
    geom_master_dir = os.path.join(mintpy_dir, 'geom_master')
    interferograms_dir = os.path.join(mintpy_dir, 'interferograms')
    if not os.path.isdir(geom_master_dir):
        os.mkdir(geom_master_dir)
    if not os.path.isdir(interferograms_dir):
        os.mkdir(interferograms_dir)

    tmp_files = os.listdir(stacking_dir)
    ifg_pairs = [i for i in tmp_files if re.match(r'\d{8}-\d{8}', i)]
    if len(ifg_pairs) < 1:
        print('no ifg_pair in {}.'.format(stacking_dir))
        sys.exit(1)

    # flag for copying files into geom_master_dir
    flag = True

    for ifg in ifg_pairs:
        ifg_dir = os.path.join(stacking_dir, ifg)
        dst_ifg_dir = os.path.join(interferograms_dir, ifg)

        if not os.path.isdir(dst_ifg_dir):
            os.mkdir(dst_ifg_dir)

        if flag:
            # just copy once
            UTM_TO_RDC_path = os.path.join(ifg_dir, 'lookup_fine')
            dst_UTM_TO_RDC = 'sim_' + ifg[0:8] + '_' + rlks + 'rlks.UTM_TO_RDC'
            dst_UTM_TO_RDC_path = os.path.join(geom_master_dir, dst_UTM_TO_RDC)
            copy_file(UTM_TO_RDC_path, dst_UTM_TO_RDC_path)

            diff_par = ifg + '.diff.par'
            diff_par_path = os.path.join(ifg_dir, diff_par)
            dst_diff_par = 'sim_' + ifg[0:8] + '_' + rlks + 'rlks.diff_par'
            dst_diff_par_path = os.path.join(geom_master_dir, dst_diff_par)
            copy_file(diff_par_path, dst_diff_par_path)

            rdc_dem = ifg + '.rdc_hgt'
            rdc_dem_path = os.path.join(ifg_dir, rdc_dem)
            dst_rdc_dem = 'sim_' + ifg[0:8] + '_' + rlks + 'rlks.rdc.dem'
            dst_rdc_dem_path = os.path.join(geom_master_dir, dst_rdc_dem)
            copy_file(rdc_dem_path, dst_rdc_dem_path)

            utm_dem_path = os.path.join(ifg_dir, 'dem_seg')
            dst_utm_dem = 'sim_' + ifg[0:8] + '_' + rlks + 'rlks.utm.dem'
            dst_utm_dem_path = os.path.join(geom_master_dir, dst_utm_dem)
            copy_file(utm_dem_path, dst_utm_dem_path)

            utm_dem_par_path = utm_dem_path + '.par'
            dst_utm_dem_par = dst_utm_dem + '.par'
            dst_utm_dem_par_path = os.path.join(geom_master_dir,
                                                dst_utm_dem_par)
            copy_file(utm_dem_par_path, dst_utm_dem_par_path)

            flag = False

        off = ifg + '.off'
        off_path = os.path.join(ifg_dir, off)
        dst_off = ifg.replace('-', '_') + '_' + rlks + 'rlks.off'
        dst_off_path = os.path.join(dst_ifg_dir, dst_off)
        copy_file(off_path, dst_off_path)

        m_amp_par = ifg[0:8] + '.pwr1.par'
        m_amp_par_path = os.path.join(ifg_dir, m_amp_par)
        dst_m_amp_par = ifg[0:8] + '_' + rlks + 'rlks.amp.par'
        dst_m_amp_par_path = os.path.join(dst_ifg_dir, dst_m_amp_par)
        copy_file(m_amp_par_path, dst_m_amp_par_path)

        s_amp_par = ifg[-8:] + '.pwr2.par'
        s_amp_par_path = os.path.join(ifg_dir, s_amp_par)
        dst_s_amp_par = ifg[-8:] + '_' + rlks + 'rlks.amp.par'
        dst_s_amp_par_path = os.path.join(dst_ifg_dir, dst_s_amp_par)
        copy_file(s_amp_par_path, dst_s_amp_par_path)
        # copy cor in rdc
        cor = ifg + '.diff.sm.cc'
        cor_path = os.path.join(ifg_dir, cor)
        dst_cor = 'filt_' + ifg.replace('-', '_') + '_' + rlks + 'rlks.cor'
        dst_cor_path = os.path.join(dst_ifg_dir, dst_cor)
        copy_file(cor_path, dst_cor_path)
        # copy unw in rdc
        unw = ifg + '.diff.int.sm.unw'
        unw_path = os.path.join(ifg_dir, unw)
        dst_unw = 'diff_' + ifg.replace('-', '_') + '_' + rlks + 'rlks.unw'
        dst_unw_path = os.path.join(dst_ifg_dir, dst_unw)
        copy_file(unw_path, dst_unw_path)

    print('\nall done.')
    sys.exit(1)


# mintpy.load.processor      = gamma
# mintpy.load.unwFile        = ./interferograms/*/diff_*rlks.unw
# mintpy.load.corFile        = ./interferograms/*/filt_*rlks.cor
# mintpy.load.connCompFile   = None
# mintpy.load.intFile        = None

# mintpy.load.demFile        = ./geom_master/sim_*.rdc.dem
# mintpy.load.lookupYFile    = ./geom_master/sim_*.UTM_TO_RDC
# mintpy.load.lookupXFile    = ./geom_master/sim_*.UTM_TO_RDC
# mintpy.load.incAngleFile   = None
# mintpy.load.azAngleFile    = None
# mintpy.load.shadowMaskFile = None
# mintpy.load.waterMaskFile  = None

if __name__ == "__main__":
    main()
