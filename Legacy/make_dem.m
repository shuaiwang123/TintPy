clear;close all;clc;
% read tif
a1=imread('srtm_57_06.tif');
a2=imread('srtm_56_06.tif');
% mosaic matrix
mosaic=[a2 a1];
% get size
s = size(mosaic);
num=find(mosaic<=-10000);
mosaic(num)=NaN;
%% you must set these parameters
flag=1;        % 0 for gamma, 1 for sarscape
name='test_dem';       % name of dem file
lon_min=95;
lat_min=30;
% spacing=0.0002777778;    % 1s (30m)
spacing=0.000833333333;    % 3s (90m)
%% *****************************you can ignore the following code*****************************
%% for gamma
if flag==0
    disp('write dem for gamma')
    fwritebkbig(mosaic,name,'float32');
    dem=freadbkbig(name,s(1, 1),'float32');
    figure;imagesc(dem);colorbar;colormap;axis image;
end
%% for sarscape
if flag==1
    disp('write dem for sarscape')
    fwritebk(mosaic,name,'short');
    dem=freadbk(name,s(1, 1),'short');
    figure;imagesc(dem);colorbar;colormap;axis image;
end
%% write hdr sml or par
lon_max=lon_min+ceil(spacing*s(1,2));
lat_max=lat_min+ceil(spacing*s(1,1));
% hdr for sarscape
if flag==1
    disp('write hdr file for sarscape')
    hdr=fopen([name '.hdr'],'wt');
    fprintf(hdr,'%s\n','ENVI');
    fprintf(hdr,'%s\n','description = {');
    fprintf(hdr,'%s\n','   ANCILLARY INFO = DEM.');
    fprintf(hdr,'%s\n','   File generated with SARscape  5.2.1 }');
    fprintf(hdr,'%s\n','');
    fprintf(hdr,'%s\n',['samples                   = ' num2str(s(1,2))]);
    fprintf(hdr,'%s\n',['lines                     = ' num2str(s(1,1))]);
    fprintf(hdr,'%s\n','bands                     = 1');
    fprintf(hdr,'%s\n','headeroffset              = 0');
    fprintf(hdr,'%s\n','file type                 = ENVI Standard');
    fprintf(hdr,'%s\n','data type                 = 2');
    fprintf(hdr,'%s\n','sensor type               = Unknown');
    fprintf(hdr,'%s\n','interleave                = bsq');
    fprintf(hdr,'%s\n','byte order                = 0');
    fprintf(hdr,'%s\n',['map info = {Geographic Lat/Lon, 1, 1, ' num2str(lon_min) ', ' num2str(lat_max) ', ' num2str(spacing) ', ' num2str(spacing) ', WGS-84, ']);
    fprintf(hdr,'%s\n',' units=Degrees}');
    fprintf(hdr,'%s\n','x start                   = 1');
    fprintf(hdr,'%s\n','y start                   = 1');
    fclose(hdr);
    % sml for sarscape
    disp('write sml file for sarscape')
    sml=fopen([name '.sml'],'wt');
    fprintf(sml,'%s\n','<?xml version="1.0" ?>');
    fprintf(sml,'%s\n','<HEADER_INFO xmlns="http://www.sarmap.ch/xml/SARscapeHeaderSchema"');
    fprintf(sml,'%s\n','	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"');
    fprintf(sml,'%s\n','	xsi:schemaLocation="http://www.sarmap.ch/xml/SARscapeHeaderSchema');
    fprintf(sml,'%s\n','	http://www.sarmap.ch/xml/SARscapeHeaderSchema/SARscapeHeaderSchema_version_1.0.xsd">');
    fprintf(sml,'%s\n','   <RegistrationCoordinates>');
    fprintf(sml,'%s\n',['      <LatNorthing>' num2str(lat_max) '</LatNorthing>']);
    fprintf(sml,'%s\n',['      <LonEasting>' num2str(lon_min) '</LonEasting>']);
    fprintf(sml,'%s\n',['      <PixelSpacingLatNorth>' num2str(-spacing) '</PixelSpacingLatNorth>']);
    fprintf(sml,'%s\n',['      <PixelSpacingLonEast>' num2str(spacing) '</PixelSpacingLonEast>']);
    fprintf(sml,'%s\n','      <Units>DEGREES</Units>');
    fprintf(sml,'%s\n','   </RegistrationCoordinates>');
    fprintf(sml,'%s\n','   <RasterInfo>');
    fprintf(sml,'%s\n','      <HeaderOffset>0</HeaderOffset>');
    fprintf(sml,'%s\n','      <RowPrefix>0</RowPrefix>');
    fprintf(sml,'%s\n','      <RowSuffix>0</RowSuffix>');
    fprintf(sml,'%s\n','      <FooterLen>0</FooterLen>');
    fprintf(sml,'%s\n','      <CellType>SHORT</CellType>');
    fprintf(sml,'%s\n','      <DataUnits>DEM</DataUnits>');
    fprintf(sml,'%s\n','      <NullCellValue>-32768</NullCellValue>');
    fprintf(sml,'%s\n',['      <NrOfPixelsPerLine>' num2str(s(1,2)) '</NrOfPixelsPerLine>']);
    fprintf(sml,'%s\n',['      <NrOfLinesPerImage>' num2str(s(1,1)) '</NrOfLinesPerImage>']);
    fprintf(sml,'%s\n','      <GeocodedImage>OK</GeocodedImage>');
    fprintf(sml,'%s\n','      <BytesOrder>LSBF</BytesOrder>');
    fprintf(sml,'%s\n','      <OtherInfo>');
    fprintf(sml,'%s\n','         <MatrixString NumberOfRows = "1" NumberOfColumns = "2">');
    fprintf(sml,'%s\n','            <MatrixRowString ID = "0">');
    fprintf(sml,'%s\n','               <ValueString ID = "0">SOFTWARE</ValueString>');
    fprintf(sml,'%s\n','              <ValueString ID = "1">SARscape ENVI  5.1.0 Sep  8 2014  W64</ValueString>');
    fprintf(sml,'%s\n','            </MatrixRowString>');
    fprintf(sml,'%s\n','         </MatrixString>');
    fprintf(sml,'%s\n','      </OtherInfo>');
    fprintf(sml,'%s\n','   </RasterInfo>');
    fprintf(sml,'%s\n','   <CartographicSystem>');
    fprintf(sml,'%s\n','      <State>GEO-GLOBAL</State>');
    fprintf(sml,'%s\n','      <Hemisphere></Hemisphere>');
    fprintf(sml,'%s\n','      <Projection>GEO</Projection>');
    fprintf(sml,'%s\n','      <Zone></Zone>');
    fprintf(sml,'%s\n','      <Ellipsoid>WGS84</Ellipsoid>');
    fprintf(sml,'%s\n','      <DatumShift></DatumShift>');
    fprintf(sml,'%s\n','   </CartographicSystem>');
    fprintf(sml,'%s\n','   <DEMCoordinates>');
    fprintf(sml,'%s\n',['      <EastingCoordinateBegin>' num2str(lon_min) '</EastingCoordinateBegin>']);
    fprintf(sml,'%s\n',['      <EastingCoordinateEnd>' num2str(lon_max) '</EastingCoordinateEnd>']);
    fprintf(sml,'%s\n',['      <EastingGridSize>' num2str(spacing) '</EastingGridSize>']);
    fprintf(sml,'%s\n',['      <NorthingCoordinateBegin>' num2str(lat_min) '</NorthingCoordinateBegin>']);
    fprintf(sml,'%s\n',['      <NorthingCoordinateEnd>' num2str(lat_max) '</NorthingCoordinateEnd>']);
    fprintf(sml,'%s\n',['      <NorthingGridSize>' num2str(spacing) '</NorthingGridSize>']);
    fprintf(sml,'%s\n','   </DEMCoordinates>');
    fprintf(sml,'%s\n','</HEADER_INFO>');
    fclose(sml);
end
% par for gamma
if flag==0
    disp('write par file for gamma')
    par=fopen([name '.par'],'wt');
    fprintf(par,'%s\n','Gamma DIFF&GEO DEM/MAP parameter file');
    fprintf(par,'%s\n','title: Xiongben');
    fprintf(par,'%s\n','DEM_projection:     EQA');
    fprintf(par,'%s\n','data_format:        REAL*4');
    fprintf(par,'%s\n','DEM_hgt_offset:          0.00000');
    fprintf(par,'%s\n','DEM_scale:               1.00000');
    fprintf(par,'%s\n',['width:                ' num2str(s(1,2))]);
    fprintf(par,'%s\n',['nlines:               ' num2str(s(1,1))]);
    fprintf(par,'%s\n',['corner_lat:      ' num2str(lat_max) '  decimal degrees']);
    fprintf(par,'%s\n',['corner_lon:      ' num2str(lon_min) ' decimal degrees']);
    fprintf(par,'%s\n',['post_lat:    ' num2str(-spacing) ' decimal degrees']);
    fprintf(par,'%s\n',['post_lon:    ' num2str(spacing) ' decimal degrees']);
    fprintf(par,'%s\n','');
    fprintf(par,'%s\n','ellipsoid_name: WGS 84');
    fprintf(par,'%s\n','ellipsoid_ra:        6378137.000   m');
    fprintf(par,'%s\n','ellipsoid_reciprocal_flattening:  298.2572236');
    fprintf(par,'%s\n','');
    fprintf(par,'%s\n','datum_name: WGS 1984');
    fprintf(par,'%s\n','datum_shift_dx:              0.000   m');
    fprintf(par,'%s\n','datum_shift_dy:              0.000   m');
    fprintf(par,'%s\n','datum_shift_dz:              0.000   m');
    fprintf(par,'%s\n','datum_scale_m:         0.00000e+00');
    fprintf(par,'%s\n','datum_rotation_alpha:  0.00000e+00   arc-sec');
    fprintf(par,'%s\n','datum_rotation_beta:   0.00000e+00   arc-sec');
    fprintf(par,'%s\n','datum_rotation_gamma:  0.00000e+00   arc-sec');
    fprintf(par,'%s\n','datum_country_list Global Definition, WGS84, World');
end