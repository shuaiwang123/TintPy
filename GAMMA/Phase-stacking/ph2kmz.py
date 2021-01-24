#!/usr/bin/env python3
##############################################################
# Display wrapped phase derived by Stacking in Google Earth  #
# Copyright (c) 2020, Lei Yuan                               #
##############################################################

import os
import argparse
import sys
import zipfile

EXAMPLE = """Example:
  ./ph2kmz.py ph_rate lookup_fine dem_seg.par 20201111-20201123.cc 20201111.pwr 20201111-20201123.diff.par res
  ./ph2kmz.py ph_rate lookup_fine dem_seg.par 20201111-20201123.cc 20201111.pwr 20201111-20201123.diff.par res --c 5 -t 0.3
  ./ph2kmz.py ph_rate lookup_fine dem_seg.par 20201111-20201123.cc 20201111.pwr 20201111-20201123.diff.par res --c 3 4 5 -t 0.3
"""


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description=
        'Display wrapped phase derived by Stacking in Google Earth.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)

    parser.add_argument('ph_rate',
                        type=str,
                        help='path of radar coordinate phase rate.')
    parser.add_argument('lookup', type=str, help='path of lookup_fine.')
    parser.add_argument('dem_seg_par', type=str, help='path of dem_seg.par.')
    parser.add_argument('cc',
                        type=str,
                        help='path of radar coordinate coherence file.')
    parser.add_argument('pwr',
                        type=str,
                        help='path of radar coordinate pwr file.')
    parser.add_argument('diff_par', type=str, help='path of *.diff.par.')
    parser.add_argument('out_dir', type=str, help='path of output directory.')

    parser.add_argument('--c',
                        dest='cycles',
                        type=float,
                        nargs='+',
                        help='data value per color cycle (default: 3.14).',
                        default=(3.14))
    parser.add_argument(
        '--t',
        dest='threshold',
        type=float,
        help='display coherence threshold (default: 0.0, display all).',
        default=0.0)

    inps = parser.parse_args()

    return inps


def read_gamma_par(par_file, keyword):
    value = ''
    with open(par_file, 'r') as f:
        for l in f.readlines():
            if l.count(keyword) == 1:
                tmp = l.split()
                value = tmp[1].strip()
    return value


def geocode(infile, lookup_file, outfile, width_rdr, width_geo, lines_geo):
    call_str = f"geocode_back {infile} {width_rdr} {lookup_file} {outfile} {width_geo} {lines_geo} 1 0"
    if not os.path.isfile(outfile):
        os.system(call_str)


def check_file(file):
    if not os.path.isfile(file):
        print("cannot find {}".format(file))
        sys.exit()


def main():
    # get inps
    inps = cmdline_parser()
    ph_rate = os.path.abspath(inps.ph_rate)
    lookup = os.path.abspath(inps.lookup)
    cc = os.path.abspath(inps.cc)
    pwr = os.path.abspath(inps.pwr)
    dem_seg_par = os.path.abspath(inps.dem_seg_par)
    diff_par = os.path.abspath(inps.diff_par)
    out_dir = os.path.abspath(inps.out_dir)
    cycles = inps.cycles
    threshold = inps.threshold

    # check file
    check_file(ph_rate)
    check_file(lookup)
    check_file(cc)
    check_file(pwr)
    check_file(dem_seg_par)
    check_file(diff_par)

    # check out_dir
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    # read gamma paramaters
    width_rdr = read_gamma_par(diff_par, 'range_samp_1')
    width = read_gamma_par(dem_seg_par, 'width')
    nlines = read_gamma_par(dem_seg_par, 'nlines')

    # geocoding of data
    ph_rate_name = os.path.basename(ph_rate)
    geo_ph_rate = os.path.join(out_dir, 'geo_' + ph_rate_name)
    geocode(ph_rate, lookup, geo_ph_rate, width_rdr, width, nlines)

    pwr_name = os.path.basename(pwr)
    geo_pwr = os.path.join(out_dir, 'geo_' + pwr_name)
    geocode(pwr, lookup, geo_pwr, width_rdr, width, nlines)

    cc_name = os.path.basename(cc)
    geo_cc = os.path.join(out_dir, 'geo_' + cc_name)
    geocode(cc, lookup, geo_cc, width_rdr, width, nlines)

    for cycle in cycles:
        # generate raster graphics image of phase + intensity data
        bmp = geo_ph_rate + '_' + str(cycle) + '.bmp'
        call_str = f"rasdt_pwr24 {geo_ph_rate} {geo_pwr} {width} 1 1 0 1 1 {cycle} 1. .35 1 {bmp} {geo_cc} 1 {threshold}"
        os.system(call_str)
        # create kml XML file with link to image
        geo_ph_rate_name = os.path.basename(geo_ph_rate)
        kml_name = geo_ph_rate_name + '_' + str(cycle) + '.kml'
        bmp_name = os.path.basename(bmp)
        os.chdir(out_dir)
        call_str = f"kml_map {bmp_name} {dem_seg_par} {kml_name}"
        os.system(call_str)
        # unzip bmp and kml
        kmz_name =  geo_ph_rate_name + '_' + str(cycle) + '.kmz'
        with zipfile.ZipFile(kmz_name, 'w') as f:
            f.write(kml_name)
            os.remove(kml_name)
            f.write(bmp_name)
            os.remove(bmp_name)

    print('All done, enjoy it!')

if __name__ == "__main__":
    main()
