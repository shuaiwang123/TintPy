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
    parser = argparse.ArgumentParser(
        description='Prepare files for MintPy time series processing.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)

    parser.add_argument('stacking_dir', help='directory path of stacking.')
    parser.add_argument(
        'mintpy_dir', help='directory path for MintPy time series processing.')
    parser.add_argument('unw_extension',
                        help='filename extension of unwrapped file.')
    parser.add_argument('rlks', help='range looks.', type=int)
    inps = parser.parse_args()

    return inps


EXAMPLE = """Example:
  ./gamma2mintpy.py /ly/stacking /ly/mintpy diff.int.sm.unw 20
  ./gamma2mintpy.py /ly/stacking /ly/mintpy diff.int.sm.sub.unw 20
  ./gamma2mintpy.py /ly/stacking /ly/mintpy diff.int.gacos.sm.sub.unw 20
"""

TEMPLATE = """mintpy.load.processor      = gamma
mintpy.load.unwFile        = ./interferograms/*/diff_*rlks.unw
mintpy.load.corFile        = ./interferograms/*/filt_*rlks.cor
mintpy.load.connCompFile   = None
mintpy.load.intFile        = None

mintpy.load.demFile        = ./geom_master/sim_*.rdc.dem
mintpy.load.lookupYFile    = ./geom_master/sim_*.UTM_TO_RDC
mintpy.load.lookupXFile    = ./geom_master/sim_*.UTM_TO_RDC
mintpy.load.incAngleFile   = None
mintpy.load.azAngleFile    = None
mintpy.load.shadowMaskFile = None
mintpy.load.waterMaskFile  = None
"""


def check_data(stacking_dir, ifg_pairs, extension):
    no_num = 0
    for ifg in ifg_pairs:
        file = glob.glob(os.path.join(stacking_dir, ifg_pairs,
                                      '*' + extension))
        if not file:
            no_num += 1
            print("cannot find {} file for {}".format(extension, ifg))
    if no_num >= 0:
        sys.exit()


def main():
    inps = cmd_line_parser()
    # get inputs
    mintpy_dir = inps.mintpy_dir
    stacking_dir = inps.stacking_dir
    mintpy_dir = os.path.abspath(mintpy_dir)
    stacking_dir = os.path.abspath(stacking_dir)
    unw_extension = inps.unw_extension
    rlks = str(inps.rlks)

    if not os.path.isdir(mintpy_dir):
        os.mkdir(mintpy_dir)
    if not os.path.isdir(stacking_dir):
        print("{} not exists.".format(stacking_dir))
        sys.exit()

    # directory for mintpy
    geom_master_dir = os.path.join(mintpy_dir, 'geom_master')
    interferograms_dir = os.path.join(mintpy_dir, 'interferograms')
    if not os.path.isdir(geom_master_dir):
        os.mkdir(geom_master_dir)
    if not os.path.isdir(interferograms_dir):
        os.mkdir(interferograms_dir)

    ifg_pairs = [
        i for i in os.listdir(stacking_dir) if re.match(r'\d{8}_\d{8}', i)
    ]
    if len(ifg_pairs) < 1:
        print('no ifg_pair in {}.'.format(stacking_dir))
        sys.exit()

    # check unw
    check_data(stacking_dir, ifg_pairs, unw_extension)
    # check .off
    check_data(stacking_dir, ifg_pairs, '.off')
    # check .pwr1.par
    check_data(stacking_dir, ifg_pairs, '.pwr1.par')
    # check .pwr2.par
    check_data(stacking_dir, ifg_pairs, '.pwr2.par')
    # check .diff.sm.cc
    check_data(stacking_dir, ifg_pairs, '.diff.sm.cc')

    # flag for copying files into geom_master_dir
    flag = True

    for ifg in ifg_pairs:
        ifg_dir = os.path.join(stacking_dir, ifg)
        dst_ifg_dir = os.path.join(interferograms_dir, ifg)

        if not os.path.isdir(dst_ifg_dir):
            os.mkdir(dst_ifg_dir)

        ifg_in = ifg.replace('_', '-')
        # just copy once
        if flag:
            UTM_TO_RDC_path = os.path.join(ifg_dir, 'lookup_fine')
            dst_UTM_TO_RDC = 'sim_' + ifg[0:8] + '_' + rlks + 'rlks.UTM_TO_RDC'
            dst_UTM_TO_RDC_path = os.path.join(geom_master_dir, dst_UTM_TO_RDC)

            diff_par = ifg_in + '.diff.par'
            diff_par_path = os.path.join(ifg_dir, diff_par)
            dst_diff_par = 'sim_' + ifg[0:8] + '_' + rlks + 'rlks.diff_par'
            dst_diff_par_path = os.path.join(geom_master_dir, dst_diff_par)

            rdc_dem = ifg_in + '.rdc_hgt'
            rdc_dem_path = os.path.join(ifg_dir, rdc_dem)
            dst_rdc_dem = 'sim_' + ifg[0:8] + '_' + rlks + 'rlks.rdc.dem'
            dst_rdc_dem_path = os.path.join(geom_master_dir, dst_rdc_dem)

            utm_dem_path = os.path.join(ifg_dir, 'dem_seg')
            dst_utm_dem = 'sim_' + ifg[0:8] + '_' + rlks + 'rlks.utm.dem'
            dst_utm_dem_path = os.path.join(geom_master_dir, dst_utm_dem)

            utm_dem_par_path = utm_dem_path + '.par'
            dst_utm_dem_par = dst_utm_dem + '.par'
            dst_utm_dem_par_path = os.path.join(geom_master_dir,
                                                dst_utm_dem_par)

            exist1 = os.path.isfile(UTM_TO_RDC_path)
            exist2 = os.path.isfile(diff_par_path)
            exist3 = os.path.isfile(rdc_dem_path)
            exist4 = os.path.isfile(utm_dem_path)
            exist5 = os.path.isfile(utm_dem_par_path)

            if exist1 and exist2 and exist3 and exist4 and exist5:
                shutil.copy(UTM_TO_RDC_path, dst_UTM_TO_RDC_path)
                shutil.copy(diff_par_path, dst_diff_par_path)
                shutil.copy(rdc_dem_path, dst_rdc_dem_path)
                shutil.copy(utm_dem_path, dst_utm_dem_path)
                shutil.copy(utm_dem_par_path, dst_utm_dem_par_path)
                flag = False

        off = ifg_in + '.off'
        off_path = os.path.join(ifg_dir, off)
        dst_off = ifg + '_' + rlks + 'rlks.off'
        dst_off_path = os.path.join(dst_ifg_dir, dst_off)
        shutil.copy(off_path, dst_off_path)

        m_amp_par = ifg[0:8] + '.pwr1.par'
        m_amp_par_path = os.path.join(ifg_dir, m_amp_par)
        dst_m_amp_par = ifg[0:8] + '_' + rlks + 'rlks.amp.par'
        dst_m_amp_par_path = os.path.join(dst_ifg_dir, dst_m_amp_par)
        shutil.copy(m_amp_par_path, dst_m_amp_par_path)

        s_amp_par = ifg[-8:] + '.pwr2.par'
        s_amp_par_path = os.path.join(ifg_dir, s_amp_par)
        dst_s_amp_par = ifg[-8:] + '_' + rlks + 'rlks.amp.par'
        dst_s_amp_par_path = os.path.join(dst_ifg_dir, dst_s_amp_par)
        shutil.copy(s_amp_par_path, dst_s_amp_par_path)
        # copy cor in rdc
        cor = ifg_in + '.diff.sm.cc'
        cor_path = os.path.join(ifg_dir, cor)
        dst_cor = 'filt_' + ifg.replace('-', '_') + '_' + rlks + 'rlks.cor'
        dst_cor_path = os.path.join(dst_ifg_dir, dst_cor)
        shutil.copy(cor_path, dst_cor_path)
        # copy unw in rdc
        unw = ifg_in + '.' + unw_extension
        unw_path = os.path.join(ifg_dir, unw)
        dst_unw = 'diff_' + ifg.replace('-', '_') + '_' + rlks + 'rlks.unw'
        dst_unw_path = os.path.join(dst_ifg_dir, dst_unw)
        shutil.copy(unw_path, dst_unw_path)

    if flag:
        print(
            'cannot find lookup_fine diff.par rdc_hgt dem_seg dem_seg.par in one directory.'
        )
    if not flag:
        print('\nAll done, enjoy it, here is the template for load_data:')
        print(TEMPLATE)


if __name__ == "__main__":
    main()
