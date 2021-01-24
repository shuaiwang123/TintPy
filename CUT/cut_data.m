function [] = cut_data( vel_in, lonlat, vel_out )
%cut data using longitude and latitued

data=load(vel_in);
lon=data(:,1);
lat=data(:,2);
vel=data(:,3);

lon_lat=load(lonlat);
t_lon=lon_lat(:,1);
t_lat=lon_lat(:,2);

BWout=inpolygon(lon,lat,t_lon,t_lat);
numOfZero=find(BWout==0);

lon(numOfZero)=NaN;
lat(numOfZero)=NaN;

outInfo=[lon(:) lat(:) vel(:)];
numNotNaN= ~isnan(outInfo(:,2));
outInfo=outInfo(numNotNaN,:);

fid=fopen(vel_out,'wt');
fprintf(fid,'%f\t%f\t%f\n',outInfo');
fclose(fid);

clear t_lon;clear t_lat;clear lon;clear lat;clear vel;clear data;

end