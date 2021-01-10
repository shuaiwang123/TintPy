clear all;
close all;
clc;

disp=load('mudui3_SBAS_T.txt');
num=disp(:,1); 
lon=disp(:,2);
lat=disp(:,3);
def=disp(:,4);

lon_lat=load('T_line.txt');
t_lon=lon_lat(:,1);
t_lat=lon_lat(:,2);

BWout=inpolygon(lon,lat,t_lon,t_lat);
numOfZero=find(BWout==0);

clear t_lon;
clear t_lat;

lon(numOfZero)=NaN;
lat(numOfZero)=NaN;

outInfo=[num(:) lon(:) lat(:) def(:)];
numNotNaN=find(~isnan(outInfo(:,2)));
outInfo=outInfo(numNotNaN,:);
% save mudui21_SBAS_TT.txt outInfo -ascii

fid=fopen('mudui3_SBAS_TT.txt','wt');
fprintf(fid,'%d\t%f\t%f\t%f\n',outInfo');
fclose(fid);
