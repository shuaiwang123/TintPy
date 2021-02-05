#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#################################################################################
# Generating DEM used in interferometry both for GAMMA and SARSCAPE processor   #
# Copyright (c) 2020, Lei Yuan                                                  #
#################################################################################
from osgeo import gdal
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from skimage import io
import argparse
import os
import sys


def load_data(tif, band=1):
    ds = gdal.Open(tif, gdal.GA_ReadOnly)
    # Data array
    data = ds.GetRasterBand(band).ReadAsArray()
    # Map extent
    trans = ds.GetGeoTransform()
    xsize = ds.RasterXSize
    ysize = ds.RasterYSize
    extent = [
        trans[0], trans[0] + xsize * trans[1], trans[3] + ysize * trans[5],
        trans[3]
    ]
    extent = [round(e) for e in extent]
    ds = None
    size = [xsize, ysize, trans[1], trans[5]]
    return data, extent, size


def plot_data(data, extent, name, cmap='rainbow'):
    plt.figure()
    ax = plt.gca()
    im = ax.imshow(data, extent=extent, cmap='rainbow')
    # create an axes on the right side of ax. The width of cax will be 5%
    # of ax and the padding between cax and ax will be fixed at 0.05 inch.
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.05)
    plt.colorbar(im, cax=cax)
    plt.savefig(name,
                bbox_inches='tight',
                dpi=300)
    # plt.show()


def mosaic_tifs(tifs, out_tif):
    # delete out_tif
    if os.path.exists(out_tif):
        os.remove(out_tif)
    try:
        gdal.Warp(out_tif, tifs)
    except Exception as e:
        print(e)


def write_gamma_par(FILE, Corner_LON, Corner_LAT, X_STEP, Y_STEP, WIDTH,
                    LENGTH, DATA_FORMAT):
    Proj = 'EQA'
    f = open(FILE, 'w')
    f.write("Gamma DIFF&GEO DEM/MAP parameter file\n")
    f.write("title:\t%s\n" % FILE.split('.')[0])
    f.write("DEM_projection:     %s\n" % Proj)  # Projection should be checked.
    f.write("data_format:        %s\n" %
            DATA_FORMAT)  # INTEGER*2 OR REAL*4 should be modified
    f.write("DEM_hgt_offset:          0.00000\n")
    f.write("DEM_scale:               1.00000\n")
    f.write("width:                %s\n" % WIDTH)
    f.write("nlines:               %s\n" % LENGTH)
    f.write("corner_lat:   %s  decimal degrees\n" % Corner_LAT)
    f.write("corner_lon:   %s  decimal degrees\n" % Corner_LON)
    f.write("post_lat:   %s  decimal degrees\n" % -abs(Y_STEP))
    f.write("post_lon:   %s  decimal degrees\n" % abs(X_STEP))
    f.write("\n")
    f.write("ellipsoid_name: WGS 84\n")
    f.write("ellipsoid_ra:        6378137.000   m\n")
    f.write("ellipsoid_reciprocal_flattening:  298.2572236\n")
    f.write("\n")
    f.write("datum_name: WGS 1984\n")
    f.write("datum_shift_dx:              0.000   m\n")
    f.write("datum_shift_dy:              0.000   m\n")
    f.write("datum_shift_dz:              0.000   m\n")
    f.write("datum_scale_m:         0.00000e+00\n")
    f.write("datum_rotation_alpha:  0.00000e+00   arc-sec\n")
    f.write("datum_rotation_beta:   0.00000e+00   arc-sec\n")
    f.write("datum_rotation_gamma:  0.00000e+00   arc-sec\n")
    f.write("datum_country_list Global Definition, WGS84, World\n")
    f.write("\n")
    f.close()


def write_saracape_par(FILE, extent, size):
    hdr = open(FILE + '_dem.hdr', 'w')
    hdr.write("ENVI\n")
    hdr.write("description = {\n")
    hdr.write("ANCILLARY INFO = DEM.\n")
    hdr.write("File generated with SARscape  5.2.1 }\n")
    hdr.write("\n")
    hdr.write(f"samples                   = {size[0]}\n")
    hdr.write(f"lines                     = {size[1]}\n")
    hdr.write("bands                     = 1\n")
    hdr.write("headeroffset              = 0\n")
    hdr.write("file type                 = ENVI Standard\n")
    hdr.write("data type                 = 2\n")
    hdr.write("sensor type               = Unknown\n")
    hdr.write("interleave                = bsq\n")
    hdr.write("byte order                = 0\n")
    hdr.write(
        "map info = {Geographic Lat/Lon, 1, 1, %s, %s, %s, %s, WGS-84, \n" %
        (extent[0], extent[3], abs(size[2]), abs(size[3])))
    hdr.write("units=Degrees}\n")
    hdr.write("x start                   = 1\n")
    hdr.write("y start                   = 1\n")
    hdr.close()

    sml = open(FILE + '_dem.sml', 'w')
    sml.write('<?xml version="1.0" ?>\n')
    sml.write(
        '<HEADER_INFO xmlns="http://www.sarmap.ch/xml/SARscapeHeaderSchema"\n')
    sml.write('    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n')
    sml.write(
        '    xsi:schemaLocation="http://www.sarmap.ch/xml/SARscapeHeaderSchema\n'
    )
    sml.write(
        '    http://www.sarmap.ch/xml/SARscapeHeaderSchema/SARscapeHeaderSchema_version_1.0.xsd">\n'
    )
    sml.write('<RegistrationCoordinates>\n')
    sml.write(f'    <LatNorthing>{extent[3]}</LatNorthing>\n')
    sml.write(f'    <LonEasting>{extent[0]}</LonEasting>\n')
    sml.write(
        f'    <PixelSpacingLatNorth>{-abs(size[3])}</PixelSpacingLatNorth>\n')
    sml.write(
        f'    <PixelSpacingLonEast>{abs(size[2])}</PixelSpacingLonEast>\n')
    sml.write('    <Units>DEGREES</Units>\n')
    sml.write('</RegistrationCoordinates>\n')
    sml.write('<RasterInfo>\n')
    sml.write('    <HeaderOffset>0</HeaderOffset>\n')
    sml.write('    <RowPrefix>0</RowPrefix>\n')
    sml.write('    <RowSuffix>0</RowSuffix>\n')
    sml.write('    <FooterLen>0</FooterLen>\n')
    sml.write('    <CellType>SHORT</CellType>\n')
    sml.write('    <DataUnits>DEM</DataUnits>\n')
    sml.write('    <NullCellValue>-32768</NullCellValue>\n')
    sml.write(f'    <NrOfPixelsPerLine>{size[1]}</NrOfPixelsPerLine>\n')
    sml.write(f'    <NrOfLinesPerImage>{size[0]}</NrOfLinesPerImage>\n')
    sml.write('    <GeocodedImage>OK</GeocodedImage>\n')
    sml.write('    <BytesOrder>LSBF</BytesOrder>\n')
    sml.write('    <OtherInfo>\n')
    sml.write(
        '        <MatrixString NumberOfRows = "1" NumberOfColumns = "2">\n')
    sml.write('            <MatrixRowString ID = "0">\n')
    sml.write('            <ValueString ID = "0">SOFTWARE</ValueString>\n')
    sml.write(
        '            <ValueString ID = "1">SARscape ENVI  5.1.0 Sep  8 2014  W64</ValueString>\n'
    )
    sml.write('            </MatrixRowString>\n')
    sml.write('        </MatrixString>\n')
    sml.write('    </OtherInfo>\n')
    sml.write('</RasterInfo>\n')
    sml.write('<CartographicSystem>\n')
    sml.write('    <State>GEO-GLOBAL</State>\n')
    sml.write('    <Hemisphere></Hemisphere>\n')
    sml.write('    <Projection>GEO</Projection>\n')
    sml.write('    <Zone></Zone>\n')
    sml.write('    <Ellipsoid>WGS84</Ellipsoid>\n')
    sml.write('    <DatumShift></DatumShift>\n')
    sml.write('</CartographicSystem>\n')
    sml.write('<DEMCoordinates>\n')
    sml.write(
        f'    <EastingCoordinateBegin>{extent[0]}</EastingCoordinateBegin>\n')
    sml.write(
        f'    <EastingCoordinateEnd>{extent[1]}</EastingCoordinateEnd>\n')
    sml.write(f'    <EastingGridSize>{abs(size[3])}</EastingGridSize>\n')
    sml.write(
        f'    <NorthingCoordinateBegin>{extent[2]}</NorthingCoordinateBegin>\n'
    )
    sml.write(
        f'    <NorthingCoordinateEnd>{extent[3]}</NorthingCoordinateEnd>\n')
    sml.write(f'    <NorthingGridSize>{abs(size[2])}</NorthingGridSize>\n')
    sml.write('</DEMCoordinates>\n')
    sml.write('</HEADER_INFO>\n')
    sml.close()


def make_dem(processor, tif, out_name, extent, size):
    dem_data = io.imread(tif)
    if processor.upper() == 'GAMMA':
        Byteorder = 'big'
        if dem_data.dtype == 'float32':
            DATA_FORMAT = 'REAL*4'
        else:
            DATA_FORMAT = 'INTEGER*2'

        if not sys.byteorder == Byteorder:
            dem_data.byteswap(True)
        dem_data.tofile(out_name + '.dem')
        write_gamma_par(out_name + '.dem.par', extent[0], extent[3], size[2],
                        size[3], size[0], size[1], DATA_FORMAT)

    if processor.upper() == 'SARSCAPE' or processor.upper() == 'ENVI':
        dem_data.tofile(out_name + '_dem')
        write_saracape_par(out_name, extent, size)


EXAMPLE = '''Example:
  python3 make_dem.py -p sarscape -t 1.tif -o dem
  python3 make_dem.py -p gamma -t 1.tif 2.tif -o dem
  python3 make_dem.py -p gamma -t D:\\1.tif D:\\2.tif -o D:\\dem
'''


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description=
        'Generating DEM used in interferometry both for GAMMA and SARSCAPE processor.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)
    parser.add_argument('-p',
                        dest='processor',
                        required=True,
                        type=str,
                        help='interferometry processor [ gamma or sarscape ]')
    parser.add_argument('-t',
                        dest='tifs',
                        required=True,
                        type=str,
                        nargs='+',
                        help='tif(hgt) files for generating DEM')
    parser.add_argument('-o',
                        dest='out',
                        type=str,
                        required=True,
                        help='output name of the generated DEM')
    return parser


def main():
    # get inputs
    parser = cmdline_parser()
    args = parser.parse_args()
    tifs = args.tifs
    processor = args.processor
    # check processor
    if processor.upper() not in ['GAMMA', 'ENVI', 'SARSCAPE']:
        print(
            "Error processor, please reset it. ['GAMMA', 'ENVI', 'SARSCAPE']")
        sys.exit()
    # check tif files
    not_exist = []
    for tif in tifs:
        if not os.path.exists(tif):
            not_exist.append(tif)
    if not_exist:
        for i in not_exist:
            print(f"'{i}' doesn't exist, please check it.")
        sys.exit()
    # check output name of the generated DEM
    dir_name = os.path.dirname(args.out)
    if dir_name:
        if not os.path.exists(dir_name):
            print(f"'{dir_name}' doesn't exist, please check it.")
    dem_name = os.path.basename(args.out)
    # process tif (mosaic read plot)
    if len(tifs) > 1:
        # mosaic tif
        print('Mosaic tifs.')
        mosaiced_tif = dem_name + '.tif'
        mosaic_tifs(tifs, mosaiced_tif)
        if os.path.exists(mosaiced_tif):
            # read tif
            print('Read tif.')
            data, extent, size = load_data(mosaiced_tif)
            # make dem
            print(f"Make {processor} dem.")
            make_dem(processor, mosaiced_tif, args.out, extent, size)
            # plot tif
            print('Plot tif.')
            plot_data(data, extent, dem_name + '.png')
            data = None
            print('Done.')
    else:
        # read tif
        print('Read tif.')
        data, extent, size = load_data(tifs[0])
        print(f"Make {processor} dem.")
        # make dem for one hgt file
        if tifs[0].endswith('.hgt'):
            out_tif = tifs[0] + '.tif'
            gdal.Translate(out_tif, tifs[0])
            make_dem(processor, out_tif, args.out, extent, size)
        else:
            # make dem for one tif file
            make_dem(processor, tifs[0], args.out, extent, size)
        # plot tif
        print('Plot tif.')
        plot_data(data, extent, dem_name + '.png')
        data = None
        print('Done.')


if __name__ == "__main__":
    main()
