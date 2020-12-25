#!/usr/bin/env python3
##################################
# Get the coverage of SLC        #
# Copyright (c) 2020, Lei Yuan   #
##################################

import argparse
import os
import glob
import sys

EXAMPLE = """Example:
./slc_area.py /ly/slc/20201229 /ly/slc/dem /ly/slc/area
./slc_area.py /ly/slc/20201229 /ly/slc/dem /ly/slc/area --rlks 28 --alks 7
"""


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description="Get the coverage of SLC.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)
    parser.add_argument('slc_dir',
                        help='directory path of slc used to geocode.',
                        type=str)
    parser.add_argument('dem_dir',
                        help='directory path of dem (*.dem and *.dem.par).',
                        type=str)
    parser.add_argument('out_dir',
                        help='directory path of saving output data.',
                        type=str)
    parser.add_argument('--rlks',
                        help='range looks (defaults: 20).',
                        type=int,
                        default=20)
    parser.add_argument('--alks',
                        help='azimuth looks (defaults: 5).',
                        type=int,
                        default=5)

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


def main():
    # get inps
    inps = cmdline_parser()
    slc_dir = inps.slc_dir
    slc_dir = os.path.abspath(slc_dir)
    dem_dir = inps.dem_dir
    dem_dir = os.path.abspath(dem_dir)
    out_dir = inps.out_dir
    out_dir = os.path.abspath(out_dir)
    rlks = inps.rlks
    alks = inps.alks
    # check slc_dir
    slc = glob.glob(
        os.path.join(slc_dir, '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].slc'))
    slc_par = glob.glob(
        os.path.join(slc_dir,
                     '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].slc.par'))
    if slc and slc_par:
        pass
    else:
        print('cannot find *.slc or *.slc.par in {}'.format(slc_dir))
        sys.exit(1)
    slc = slc[0]
    slc_par = slc_par[0]
    # get date
    slc_name = os.path.basename(slc)
    slc_date = slc_name[0:8]
    # check dem_dir
    dem = glob.glob(os.path.join(dem_dir, '*.dem'))
    dem_par = glob.glob(os.path.join(dem_dir, '*.dem.par'))
    if dem and dem_par:
        pass
    else:
        print('cannot find *.dem or *.dem.par in {}'.format(dem_dir))
        sys.exit(1)
    dem = dem[0]
    dem_par = dem_par[0]
    # check out_dir
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    # check rlks alks
    if rlks < 1:
        print('rlks must bigger than 0.')
        sys.exit(1)
    if alks < 1:
        print('alks must bigger than 0.')
        sys.exit(1)
    # geocode slc
    m_mli = os.path.join(out_dir, f"{slc_date}.mli")
    m_mli_par = m_mli + '.par'
    call_str = f"multi_look {slc} {slc_par} {m_mli} {m_mli_par} {rlks} {alks}"
    os.system(call_str)

    utm_dem = os.path.join(out_dir, 'dem_seg')
    utm_dem_par = utm_dem + '.par'
    utm2rdc = os.path.join(out_dir, 'lookup_table')
    sim_sar_utm = os.path.join(out_dir, f"{slc_date}.sim_sar")
    u = os.path.join(out_dir, 'u')
    v = os.path.join(out_dir, 'v')
    inc = os.path.join(out_dir, 'inc')
    psi = os.path.join(out_dir, 'psi')
    pix = os.path.join(out_dir, 'pix')
    ls_map = os.path.join(out_dir, 'ls_map')
    call_str = f"gc_map {m_mli_par} - {dem_par} {dem} {utm_dem_par} {utm_dem} {utm2rdc} 1 1 {sim_sar_utm} {u} {v} {inc} {psi} {pix} {ls_map} 8 1"
    os.system(call_str)

    pix_sigma0 = os.path.join(out_dir, "pix_sigma0")
    pix_gamma0 = os.path.join(out_dir, "pix_gamma0")
    call_str = f"pixel_area {m_mli_par} {utm_dem_par} {utm_dem} {utm2rdc} {ls_map} {inc} {pix_sigma0} {pix_gamma0}"
    os.system(call_str)

    pix_gamma0_bmp = pix_gamma0 + '.bmp'
    width_mli = read_gamma_par(m_mli_par, 'range_samples')
    call_str = f"raspwr {pix_gamma0} {width_mli} - - - - - - - {pix_gamma0_bmp}"
    os.system(call_str)

    diff_par = os.path.join(out_dir, f"{slc_date}.diff_par")
    call_str = f"create_diff_par {m_mli_par} - {diff_par} 1 0"
    os.system(call_str)

    offs = os.path.join(out_dir, f"{slc_date}.offs")
    snr = os.path.join(out_dir, f"{slc_date}.snr")
    offsets = os.path.join(out_dir, ".offsets")
    call_str = f"offset_pwrm {pix_sigma0} {m_mli} {diff_par} {offs} {snr} 64 64 {offsets} 2 100 100 5.0"
    os.system(call_str)

    coffs = os.path.join(out_dir, "coffs")
    coffsets = os.path.join(out_dir, "coffsets")
    call_str = f"offset_fitm {offs} {snr} {diff_par} {coffs} {coffsets} 5.0 1"
    os.system(call_str)

    width_utm_dem = read_gamma_par(utm_dem_par, 'width')
    utm_to_rdc = os.path.join(out_dir, "lookup_table_fine")
    call_str = f"gc_map_fine {utm2rdc} {width_utm_dem} {diff_par} {utm_to_rdc} 1"
    os.system(call_str)

    geo_m_mli = os.path.join(out_dir, f"geo_{slc_date}.mli")
    call_str = f"geocode_back {m_mli} {width_mli} {utm_to_rdc} {geo_m_mli} {width_utm_dem} - 2 0"
    os.system(call_str)

    geo_m_mli_bmp = geo_m_mli + '.bmp'
    call_str = f"raspwr {geo_m_mli} {width_utm_dem} 1 0 1 1 1. .35 1 {geo_m_mli_bmp}"
    os.system(call_str)

    mli_kml = geo_m_mli + '.kml'
    call_str = f"kml_map {geo_m_mli_bmp} {utm_dem_par} {mli_kml}"
    os.system(call_str)


if __name__ == "__main__":
    main()
