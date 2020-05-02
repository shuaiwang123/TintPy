clear all;
close all;
clc;

%% line为行，sample为列，left_lon为左上角经度，left_lat为左上角纬度，cha为间隔
% 可以在dem_seg.par里面查看
line=4000;
sample=2612;
left_lon=120.0711309;
left_lat=23.3681578;
cha=2.7785496e-04;    % 必须为正值
%% 生成坐标
A=left_lon:cha:left_lon+(sample-1)*cha;
B=left_lat:-cha:left_lat-(line-1)*cha;
[lon,lat]=meshgrid(A,B);

%% 读取相干系数图并显示
cc=freadbkbig('C:\Users\leiyuan\Desktop\dinsar/20160109-20160214.utm.cc',line,'float32');
figure,imagesc(cc);colormap(jet);colorbar;axis image;

%% 读取形变图并显示
def=freadbkbig('C:\Users\leiyuan\Desktop\dinsar/20160109-20160214.utm.disp',line,'float32');
figure,imagesc(def);colormap(jet);colorbar;axis image;

%% 裁剪想要的区域，单击选点，双击退出
% [tx,ty]=getpts;
% save 'txx_A.txt' tx -ascii;
% save 'tyy_A.txt' ty -ascii;

% 保存想要的区域，下次裁剪时，可以注释掉上面三行代码
txx=load('txx_A.txt');
tyy=load('tyy_A.txt');
[srow,spix]=size(def);
[X,Y]=meshgrid(1:srow,1:spix);
X=X';
Y=Y';

% 区域外的值置零
BWout = inpolygon(Y,X,txx,tyy);
nump=find(BWout==0);
clear txx;
clear tyy;
cc(nump)=NaN;
def(nump)=NaN;
lon(nump)=NaN;
lat(nump)=NaN;
%% 保存相干系数图并显示（经度、纬度、相干系数）
cc_a=[lon(:) lat(:) cc(:)];
num3=find(~isnan(cc_a(:,3)));
cc_a=cc_a(num3,:);
figure,imagesc(cc);colormap(jet);colorbar;axis image;
save cc_a.txt cc_a -ascii
%% 保存缠绕图并显示（经度、纬度、缠绕值）
wrap = wrap(-4*pi*def/0.056);          % 0.056代表Sentinel-1波长（5.6cm）
figure;imagesc(wrap);colorbar;colormap(jet);axis image;
ase_wrap = [lon(:) lat(:) wrap(:)];
num1=find(~isnan(ase_wrap(:,3)));
ase_wrap=ase_wrap(num1,:);
save wrap_a.txt ase_wrap -ascii
%% 保存形变图并显示（经度、纬度、形变值（单位为m））
figure;imagesc(def);colorbar;colormap(jet);axis image;
ase_def=[lon(:) lat(:) def(:)];   % def(:)*100可变为cm
num=find(~isnan(ase_def(:,3)));
ase_def=ase_def(num,:);
save disp_a.txt ase_def -ascii
%% 保存解缠图并显示（经度、纬度、解缠值）
unwrap=-4*pi*def/0.056;               % 形变转相位
figure;imagesc(unwrap);colorbar;colormap(jet);axis image;
ase_unwrap = [lon(:) lat(:) unwrap(:)];
num2=find(~isnan(ase_unwrap(:,3)));
ase_unwrap=ase_unwrap(num2,:);
save unwrap_a.txt ase_unwrap -ascii