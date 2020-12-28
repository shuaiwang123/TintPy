#!/usr/bin/env python3
###########################################################
# Co-register all of SLCs to a reference SLC using GAMMA  #
# Copyright (c) 2020, Lei Yuan                            #
###########################################################

import os
import re
import argparse
import shutil
import glob
import sys

EXAMPLE = """Example:
  ./coreg_to_one2.py /ly/slc /ly/rslc /ly/dem '2'
  ./coreg_to_one2.py /ly/slc /ly/rslc /ly/dem '1 2' --rlks 8 --alks 2 --ref_slc 20201111
"""


def cmd_line_parser():
    parser = argparse.ArgumentParser(description='Co-register all of the Sentinel-1 TOPS SLCs to a reference SLC.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=EXAMPLE)

    parser.add_argument('slc_dir', help='directory path of SLCs')
    parser.add_argument('rslc_dir', help='directory path of RSLCs')
    parser.add_argument('dem_dir', help='directory path of .dem and .dem.par')
    parser.add_argument('iw_num', type=str, help='IW num for co-registration')
    parser.add_argument('--rlks',
                        help='range looks (defaults: 20)',
                        default=20,
                        type=int)
    parser.add_argument('--alks',
                        help='azimuth looks (defaults: 5)',
                        default=5,
                        type=int)
    parser.add_argument('--ref_slc',
                        help='reference SLC (default: the first slc)',
                        default='0')
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


def gen_bmp(slc, slc_par, rlks, alks):
    width = read_gamma_par(slc_par, 'range_samples')
    bmp = slc + '.bmp'
    call_str = f"rasSLC {slc} {width} 1 0 {rlks} {alks} 1. .35 1 0 0 {bmp}"
    os.system(call_str)


def main():
    inps = cmd_line_parser()
    slc_dir = inps.slc_dir
    rslc_dir = inps.rslc_dir
    dem_dir = inps.dem_dir
    iw_num = inps.iw_num
    iw_num = iw_num.split()
    rlks = inps.rlks
    alks = inps.alks
    ref_slc = inps.ref_slc

    # check slc_dir
    slc_dir = os.path.abspath(slc_dir)
    if not os.path.isdir(slc_dir):
        print("{} not exists.".format(slc_dir))
        sys.exit(1)

    # check rslc_dir
    rslc_dir = os.path.abspath(rslc_dir)
    if not os.path.isdir(rslc_dir):
        os.mkdir(rslc_dir)

    # check dem
    dem_dir = os.path.abspath(dem_dir)
    if not os.path.isdir(dem_dir):
        print("{} not exists.".format(dem_dir))
    else:
        dem = glob.glob(dem_dir + '/*.dem')
        dem_par = glob.glob(dem_dir + '/*.dem.par')
        if not (dem and dem_par):
            print('dem or dem.par not exist.')
        else:
            dem = dem[0]
            dem_par = dem_par[0]

    # check iw_num
    for i in iw_num:
        if i not in ['1', '2', '3']:
            print('Error IW.')
            sys.exit(1)

    # get all date
    tmp_files = os.listdir(slc_dir)
    all_date = sorted([i for i in tmp_files if re.findall(r'^\d{8}$', i)])
    if len(all_date) < 2:
        print('not enough SLCs.')
        sys.exit(1)

    # check ref_slc
    if ref_slc == '0':
        ref_slc = all_date[0]
    else:
        if re.findall(r'^\d{8}$', ref_slc):
            if not ref_slc in all_date:
                print('no slc for {}.'.format(ref_slc))
                sys.exit(1)
        else:
            print('error date for ref_slc.')
            sys.exit(1)

    m_date = ref_slc
    m_slc_dir = os.path.join(slc_dir, m_date)
    m_slc = os.path.join(m_slc_dir, m_date + '.slc')
    m_slc_par = m_slc + '.par'
    m_mli = os.path.join(m_slc_dir, f"{m_date}.mli")
    m_mli_par = m_mli + '.par'

    call_str = f"multi_look {m_slc} {m_slc_par} {m_mli} {m_mli_par} {rlks} {alks}"
    os.system(call_str)

    utm_dem = os.path.join(m_slc_dir, 'dem_seg')
    utm_dem_par = utm_dem + '.par'
    utm2rdc = os.path.join(m_slc_dir, 'lookup_table')
    sim_sar_utm = os.path.join(m_slc_dir, f"{m_date}.sim_sar")
    u = os.path.join(m_slc_dir, 'u')
    v = os.path.join(m_slc_dir, 'v')
    inc = os.path.join(m_slc_dir, 'inc')
    psi = os.path.join(m_slc_dir, 'psi')
    pix = os.path.join(m_slc_dir, 'pix')
    ls_map = os.path.join(m_slc_dir, 'ls_map')

    call_str = f"gc_map {m_mli_par} - {dem_par} {dem} {utm_dem_par} {utm_dem} {utm2rdc} 1 1 {sim_sar_utm} {u} {v} {inc} {psi} {pix} {ls_map} 8 1"
    os.system(call_str)

    pix_sigma0 = os.path.join(m_slc_dir, "pix_sigma0")
    pix_gamma0 = os.path.join(m_slc_dir, "pix_gamma0")

    call_str = f"pixel_area {m_mli_par} {utm_dem_par} {utm_dem} {utm2rdc} {ls_map} {inc} {pix_sigma0} {pix_gamma0}"
    os.system(call_str)

    pix_gamma0_bmp = pix_gamma0 + '.bmp'
    width_mli = read_gamma_par(m_mli_par, 'range_samples')

    call_str = f"raspwr {pix_gamma0} {width_mli} - - - - - - - {pix_gamma0_bmp}"
    os.system(call_str)

    diff_par = os.path.join(m_slc_dir, f"{m_date}.diff_par")

    call_str = f"create_diff_par {m_mli_par} - {diff_par} 1 0"
    os.system(call_str)

    offs = os.path.join(m_slc_dir, f"{m_date}.offs")
    snr = os.path.join(m_slc_dir, f"{m_date}.snr")
    offsets = os.path.join(m_slc_dir, ".offsets")

    call_str = f"offset_pwrm {pix_sigma0} {m_mli} {diff_par} {offs} {snr} 64 64 {offsets} 2 100 100 5.0"
    os.system(call_str)

    coffs = os.path.join(m_slc_dir, "coffs")
    coffsets = os.path.join(m_slc_dir, "coffsets")

    call_str = f"offset_fitm {offs} {snr} {diff_par} {coffs} {coffsets} 5.0 1"
    os.system(call_str)

    width_utm_dem = read_gamma_par(utm_dem_par, 'width')
    utm_to_rdc = os.path.join(m_slc_dir, "lookup_table_fine")

    call_str = f"gc_map_fine {utm2rdc} {width_utm_dem} {diff_par} {utm_to_rdc} 1"
    os.system(call_str)

    geo_m_mli = os.path.join(m_slc_dir, f"geo_{m_date}.mli")

    call_str = f"geocode_back {m_mli} {width_mli} {utm_to_rdc} {geo_m_mli} {width_utm_dem} - 2 0"
    os.system(call_str)

    geo_m_mli_bmp = geo_m_mli + '.bmp'

    call_str = f"raspwr {geo_m_mli} {width_utm_dem} 1 0 1 1 1. .35 1 {geo_m_mli_bmp}"
    os.system(call_str)

    rdc_dem = os.path.join(m_slc_dir, f"{m_date}.hgt")

    length_mli = read_gamma_par(m_mli_par, 'azimuth_lines')
    call_str = f"geocode {utm_to_rdc} {utm_dem} {width_utm_dem} {rdc_dem} {width_mli} {length_mli} 2 0"
    os.system(call_str)

    rdc_dem_bmp = rdc_dem + '.bmp'
    call_str = f"rashgt {rdc_dem} {m_mli} {width_mli} 1 1 0 1 1 160.0 1. .35 1 {rdc_dem_bmp}"
    os.system(call_str)

    s_dates = all_date
    s_dates.remove(m_date)

    # copy reference slc to rsl_dir
    m_rslc_dir = os.path.join(rslc_dir, m_date)
    if not os.path.isdir(m_rslc_dir):
        os.mkdir(m_rslc_dir)
    m_rslc = os.path.join(m_rslc_dir, m_date + '.slc')
    m_rslc_par = m_rslc + '.par'
    if not os.path.isfile(m_rslc):
        shutil.copy(m_slc, m_rslc_dir)
    if not os.path.isfile(m_rslc_par):
        shutil.copy(m_slc_par, m_rslc_dir)

    for s_date in s_dates:
        s_slc_dir = os.path.join(slc_dir, s_date)
        s_slc = os.path.join(s_slc_dir, s_date + '.slc')
        s_slc_par = s_slc + '.par'
        s_rslc_dir = os.path.join(rslc_dir, s_date)

        if not os.path.isdir(s_rslc_dir):
            os.mkdir(s_rslc_dir)
        s_mli = os.path.join(s_rslc_dir, f"{s_date}.mli")
        s_mli_par = s_mli + '.par'

        call_str = f"multi_look {s_slc} {s_slc_par} {s_mli} {s_mli_par} {rlks} {alks}"
        os.system(call_str)

        lt = os.path.join(s_rslc_dir, f"{s_date}.lt")

        call_str = f"rdc_trans {m_mli_par} {rdc_dem} {s_mli_par} {lt}"
        os.system(call_str)

        if len(iw_num) == 1:
            s_iw_slc = os.path.join(s_slc_dir,
                                    f"{s_date}.iw{iw_num[0] * 2}.slc")
            s_iw_slc_par = s_iw_slc + '.par'
            s_iw_slc_tops_par = s_iw_slc + '.tops_par'

            m_iw_slc = os.path.join(m_slc_dir,
                                    f"{m_date}.iw{iw_num[0] * 2}.slc")
            m_iw_slc_par = m_iw_slc + '.par'
            m_iw_slc_tops_par = m_iw_slc + '.tops_par'

            s_iw_rslc = os.path.join(s_rslc_dir,
                                     f"{s_date}.iw{iw_num[0] * 2}.slc")
            s_iw_rslc_par = s_iw_rslc + '.par'
            s_iw_rslc_tops_par = s_iw_rslc + '.tops_par'

            os.chdir(s_rslc_dir)

            call_str = f"echo {s_iw_slc} {s_iw_slc_par} {s_iw_slc_tops_par} > SLC2_tab"
            os.system(call_str)
            call_str = f"echo {m_iw_slc} {m_iw_slc_par} {m_iw_slc_tops_par} > SLC1_tab"
            os.system(call_str)
            call_str = f"echo {s_iw_rslc} {s_iw_rslc_par} {s_iw_rslc_tops_par} > RSLC2_tab"
            os.system(call_str)

        if len(iw_num) == 2:
            s_iw_slc1 = os.path.join(s_slc_dir,
                                     f"{s_date}.iw{iw_num[0] * 2}.slc")
            s_iw_slc_par1 = s_iw_slc1 + '.par'
            s_iw_slc_tops_par1 = s_iw_slc1 + '.tops_par'
            s_iw_slc2 = os.path.join(s_slc_dir,
                                     f"{s_date}.iw{iw_num[1] * 2}.slc")
            s_iw_slc_par2 = s_iw_slc2 + '.par'
            s_iw_slc_tops_par2 = s_iw_slc2 + '.tops_par'

            m_iw_slc1 = os.path.join(m_slc_dir,
                                     f"{m_date}.iw{iw_num[0] * 2}.slc")
            m_iw_slc_par1 = m_iw_slc1 + '.par'
            m_iw_slc_tops_par1 = m_iw_slc1 + '.tops_par'
            m_iw_slc2 = os.path.join(m_slc_dir,
                                     f"{m_date}.iw{iw_num[1] * 2}.slc")
            m_iw_slc_par2 = m_iw_slc2 + '.par'
            m_iw_slc_tops_par2 = m_iw_slc2 + '.tops_par'

            s_iw_rslc1 = os.path.join(s_rslc_dir,
                                      f"{s_date}.iw{iw_num[0] * 2}.slc")
            s_iw_rslc_par1 = s_iw_rslc1 + '.par'
            s_iw_rslc_tops_par1 = s_iw_rslc1 + '.tops_par'
            s_iw_rslc2 = os.path.join(s_rslc_dir,
                                      f"{s_date}.iw{iw_num[1] * 2}.slc")
            s_iw_rslc_par2 = s_iw_rslc2 + '.par'
            s_iw_rslc_tops_par2 = s_iw_rslc2 + '.tops_par'

            os.chdir(s_rslc_dir)

            call_str = f"echo {s_iw_slc1} {s_iw_slc_par1} {s_iw_slc_tops_par1} > SLC2_tab"
            os.system(call_str)
            call_str = f"echo {s_iw_slc2} {s_iw_slc_par2} {s_iw_slc_tops_par2} >> SLC2_tab"
            os.system(call_str)
            call_str = f"echo {m_iw_slc1} {m_iw_slc_par1} {m_iw_slc_tops_par1} > SLC1_tab"
            os.system(call_str)
            call_str = f"echo {m_iw_slc2} {m_iw_slc_par2} {m_iw_slc_tops_par2} >> SLC1_tab"
            os.system(call_str)
            call_str = f"echo {s_iw_rslc1} {s_iw_rslc_par1} {s_iw_rslc_tops_par1} > RSLC2_tab"
            os.system(call_str)
            call_str = f"echo {s_iw_rslc2} {s_iw_rslc_par2} {s_iw_rslc_tops_par2} >> RSLC2_tab"
            os.system(call_str)

        if len(iw_num) == 3:
            s_iw_slc1 = os.path.join(s_slc_dir,
                                     f"{s_date}.iw{iw_num[0] * 2}.slc")
            s_iw_slc_par1 = s_iw_slc1 + '.par'
            s_iw_slc_tops_par1 = s_iw_slc1 + '.tops_par'
            s_iw_slc2 = os.path.join(s_slc_dir,
                                     f"{s_date}.iw{iw_num[1] * 2}.slc")
            s_iw_slc_par2 = s_iw_slc2 + '.par'
            s_iw_slc_tops_par2 = s_iw_slc2 + '.tops_par'
            s_iw_slc3 = os.path.join(s_slc_dir,
                                     f"{s_date}.iw{iw_num[2] * 2}.slc")
            s_iw_slc_par3 = s_iw_slc3 + '.par'
            s_iw_slc_tops_par3 = s_iw_slc3 + '.tops_par'

            m_iw_slc1 = os.path.join(m_slc_dir,
                                     f"{m_date}.iw{iw_num[0] * 2}.slc")
            m_iw_slc_par1 = m_iw_slc1 + '.par'
            m_iw_slc_tops_par1 = m_iw_slc1 + '.tops_par'
            m_iw_slc2 = os.path.join(m_slc_dir,
                                     f"{m_date}.iw{iw_num[1] * 2}.slc")
            m_iw_slc_par2 = m_iw_slc2 + '.par'
            m_iw_slc_tops_par2 = m_iw_slc2 + '.tops_par'
            m_iw_slc3 = os.path.join(m_slc_dir,
                                     f"{m_date}.iw{iw_num[2] * 2}.slc")
            m_iw_slc_par3 = m_iw_slc3 + '.par'
            m_iw_slc_tops_par3 = m_iw_slc3 + '.tops_par'

            s_iw_rslc1 = os.path.join(s_rslc_dir,
                                      f"{s_date}.iw{iw_num[0] * 2}.slc")
            s_iw_rslc_par1 = s_iw_rslc1 + '.par'
            s_iw_rslc_tops_par1 = s_iw_rslc1 + '.tops_par'
            s_iw_rslc2 = os.path.join(s_rslc_dir,
                                      f"{s_date}.iw{iw_num[1] * 2}.slc")
            s_iw_rslc_par2 = s_iw_rslc2 + '.par'
            s_iw_rslc_tops_par2 = s_iw_rslc2 + '.tops_par'
            s_iw_rslc3 = os.path.join(s_rslc_dir,
                                      f"{s_date}.iw{iw_num[2] * 2}.slc")
            s_iw_rslc_par3 = s_iw_rslc3 + '.par'
            s_iw_rslc_tops_par3 = s_iw_rslc3 + '.tops_par'

            os.chdir(s_rslc_dir)

            call_str = f"echo {s_iw_slc1} {s_iw_slc_par1} {s_iw_slc_tops_par1} > SLC2_tab"
            os.system(call_str)
            call_str = f"echo {s_iw_slc2} {s_iw_slc_par2} {s_iw_slc_tops_par2} >> SLC2_tab"
            os.system(call_str)
            call_str = f"echo {s_iw_slc3} {s_iw_slc_par3} {s_iw_slc_tops_par3} >> SLC2_tab"
            os.system(call_str)
            call_str = f"echo {m_iw_slc1} {m_iw_slc_par1} {m_iw_slc_tops_par1} > SLC1_tab"
            os.system(call_str)
            call_str = f"echo {m_iw_slc2} {m_iw_slc_par2} {m_iw_slc_tops_par2} >> SLC1_tab"
            os.system(call_str)
            call_str = f"echo {m_iw_slc3} {m_iw_slc_par3} {m_iw_slc_tops_par3} >> SLC1_tab"
            os.system(call_str)
            call_str = f"echo {s_iw_rslc1} {s_iw_rslc_par1} {s_iw_rslc_tops_par1} > RSLC2_tab"
            os.system(call_str)
            call_str = f"echo {s_iw_rslc2} {s_iw_rslc_par2} {s_iw_rslc_tops_par2} >> RSLC2_tab"
            os.system(call_str)
            call_str = f"echo {s_iw_rslc3} {s_iw_rslc_par3} {s_iw_rslc_tops_par3} >> RSLC2_tab"
            os.system(call_str)

        s_rslc = os.path.join(s_rslc_dir, f"{s_date}.rslc")
        s_rslc_par = s_rslc + ".par"
        call_str = f"SLC_interp_lt_S1_TOPS SLC2_tab {s_slc_par} SLC1_tab {m_slc_par} {lt} {m_mli_par} {s_mli_par} - RSLC2_tab {s_rslc} {s_rslc_par}"
        os.system(call_str)
        
        s_rmli = os.path.join(s_rslc_dir, f"{s_date}.rslc.mli")
        s_rmli_par = s_rmli + ".par"
        call_str = f"multi_look {s_rslc} {s_rslc_par} {s_rmli} {s_rmli_par} {rlks} {alks}"
        os.system(call_str)

        s_rmli_bmp = s_rmli + ".bmp"
        call_str = f"raspwr {s_rmli} {width_mli} - - - - - - - {s_rmli_bmp}"
        os.system(call_str)

        off_file = os.path.join(s_rslc_dir, f"{m_date}-{s_date}.off")
        call_str = f"create_offset {m_slc_par} {s_slc_par} {off_file} 1 {rlks} {alks} 0"
        os.system(call_str)

        offs_file = os.path.join(s_rslc_dir, f"{m_date}-{s_date}.offs")
        snr_file = os.path.join(s_rslc_dir, f"{m_date}-{s_date}.snr")
        call_str = f"offset_pwr {m_slc} {s_rslc} {m_slc_par} {s_rslc_par} {off_file} {offs_file} {snr_file} 256 64 - 1 100 100 15.0 4 0 0"
        os.system(call_str)

        call_str = f"offset_fit {offs_file} {snr_file} {off_file}  - - 0.5 1 0"
        os.system(call_str)

        call_str = f"SLC_interp_lt_S1_TOPS SLC2_tab {s_slc_par} SLC1_tab {m_slc_par} {lt} {m_mli_par} {s_mli_par} {off_file} RSLC2_tab {s_rslc} {s_rslc_par}"
        os.system(call_str)

        off1_file = os.path.join(s_rslc_dir, f"{m_date}-{s_date}.off1")
        call_str = f"create_offset {m_slc_par} {s_slc_par} {off1_file} 1 {rlks} {alks} 0"
        os.system(call_str)

        offs1_file = os.path.join(s_rslc_dir, f"{m_date}-{s_date}.offs1")
        snr1_file = os.path.join(s_rslc_dir, f"{m_date}-{s_date}.snr1")
        coreg_file = os.path.join(s_rslc_dir, f"{m_date}-{s_date}.coreg")
        call_str = f"offset_pwr {m_slc} {s_rslc} {m_slc_par} {s_rslc_par} {off1_file} {offs1_file} {snr1_file} 256 64 {coreg_file} 1 200 200 16.0 4 0 0"
        os.system(call_str)

        call_str = f"offset_fit {offs1_file} {snr1_file} {off1_file}  - - 0.5 1 0"
        os.system(call_str)

        off_total_file = os.path.join(s_rslc_dir, f"{m_date}-{s_date}.off.total")
        call_str = f"offset_add {off_file} {off1_file} {off_total_file}"
        os.system(call_str)

        call_str = f"SLC_interp_lt_S1_TOPS SLC2_tab {s_slc_par} SLC1_tab {m_slc_par} {lt} {m_mli_par} {s_mli_par} {off_total_file} RSLC2_tab {s_rslc} {s_rslc_par}"
        os.system(call_str)

        sim_unw0 = os.path.join(s_rslc_dir, f"{m_date}-{s_date}.sim_unw0")
        call_str = f"phase_sim_orb {m_slc_par} {s_slc_par} {off_total_file} {rdc_dem} {sim_unw0} {m_slc_par} - - 1 1"
        os.system(call_str)

        diff0 = os.path.join(s_rslc_dir, f"{m_date}-{s_date}.diff0")
        call_str = f"SLC_diff_intf {m_slc} {s_rslc} {m_slc_par} {s_rslc_par} {off_total_file} {sim_unw0} {diff0} {rlks} {alks} 0 0 0.25 1 1"
        os.system(call_str)

        diff0_bmp = diff0 + '.bmp'
        call_str = f"rasmph {diff0} {width_mli} 1 0 1 1 1. .35 1 {diff0_bmp}"
        os.system(call_str)

        off_corrected = os.path.join(s_rslc_dir, f"{m_date}-{s_date}.off.corrected")
        call_str = f"S1_coreg_overlap SLC1_tab RSLC2_tab {m_date}-{s_date} {off_total_file} {off_corrected} 0.8 0.01 0.8 1"
        os.system(call_str)

        call_str = f"SLC_interp_lt_S1_TOPS SLC2_tab {s_slc_par} SLC1_tab {m_slc_par} {lt} {m_mli_par} {s_mli_par} {off_corrected} RSLC2_tab {s_rslc} {s_rslc_par}"
        os.system(call_str)

        off_corrected2 = os.path.join(s_rslc_dir, f"{m_date}-{s_date}.off.corrected2")
        call_str = f"S1_coreg_overlap SLC1_tab RSLC2_tab {m_date}-{s_date} {off_corrected} {off_corrected2} 0.8 0.01 0.8 1"
        os.system(call_str)

        call_str = f"SLC_interp_lt_S1_TOPS SLC2_tab {s_slc_par} SLC1_tab {m_slc_par} {lt} {m_mli_par} {s_mli_par} {off_corrected2} RSLC2_tab {s_rslc} {s_rslc_par}"
        os.system(call_str)

        sim_unw = os.path.join(s_rslc_dir, f"{m_date}-{s_date}.sim_unw")
        call_str = f"phase_sim_orb {m_slc_par} {s_slc_par} {off_corrected2} {rdc_dem} {sim_unw} {m_slc_par} - - 1 1"
        os.system(call_str)

        diff = os.path.join(s_rslc_dir, f"{m_date}-{s_date}.diff")
        call_str = f"SLC_diff_intf {m_slc} {s_rslc} {m_slc_par} {s_rslc_par} {off_corrected2} {sim_unw} {diff} {rlks} {alks} 0 0 0.25 1 1"
        os.system(call_str)

        diff_bmp = diff + '.bmp'
        call_str = f"rasmph {diff} {width_mli} 1 0 1 1 1. .35 1 {diff_bmp}"
        os.system(call_str)

        # delete files
        save_files = []
        save_files.append(s_date + '.rslc')
        save_files.append(s_date + '.rslc.par')
        save_files.append(m_date + '-' + s_date + '.diff.bmp')

        for f in os.listdir(s_rslc_dir):
            if f not in save_files:
                path = os.path.join(s_rslc_dir, f)
                os.remove(path)

        os.rename(s_date + '.rslc', s_date + '.slc')
        os.rename(s_date + '.rslc.par', s_date + '.slc.par')

    # generate bmp for rslc
    rslc_files = glob.glob(rslc_dir + '/*/*.slc')
    for f in rslc_files:
        gen_bmp(f, f + '.par', rlks, alks)

    print('\nall done, enjoy it.\n')


if __name__ == "__main__":
    main()
