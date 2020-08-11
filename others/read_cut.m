clear all;
close all;
clc;

%% lineΪ�У�sampleΪ�У�left_lonΪ���ϽǾ��ȣ�left_latΪ���Ͻ�γ�ȣ�chaΪ���
% ������dem_seg.par����鿴
line=4000;
sample=2612;
left_lon=120.0711309;
left_lat=23.3681578;
cha=2.7785496e-04;    % ����Ϊ��ֵ
%% ��������
A=left_lon:cha:left_lon+(sample-1)*cha;
B=left_lat:-cha:left_lat-(line-1)*cha;
[lon,lat]=meshgrid(A,B);

%% ��ȡ���ϵ��ͼ����ʾ
cc=freadbkbig('C:\Users\leiyuan\Desktop\dinsar/20160109-20160214.utm.cc',line,'float32');
figure,imagesc(cc);colormap(jet);colorbar;axis image;

%% ��ȡ�α�ͼ����ʾ
def=freadbkbig('C:\Users\leiyuan\Desktop\dinsar/20160109-20160214.utm.disp',line,'float32');
figure,imagesc(def);colormap(jet);colorbar;axis image;

%% �ü���Ҫ�����򣬵���ѡ�㣬˫���˳�
% [tx,ty]=getpts;
% save 'txx_A.txt' tx -ascii;
% save 'tyy_A.txt' ty -ascii;

% ������Ҫ�������´βü�ʱ������ע�͵��������д���
txx=load('txx_A.txt');
tyy=load('tyy_A.txt');
[srow,spix]=size(def);
[X,Y]=meshgrid(1:srow,1:spix);
X=X';
Y=Y';

% �������ֵ����
BWout = inpolygon(Y,X,txx,tyy);
nump=find(BWout==0);
clear txx;
clear tyy;
cc(nump)=NaN;
def(nump)=NaN;
lon(nump)=NaN;
lat(nump)=NaN;
%% �������ϵ��ͼ����ʾ�����ȡ�γ�ȡ����ϵ����
cc_a=[lon(:) lat(:) cc(:)];
num3=find(~isnan(cc_a(:,3)));
cc_a=cc_a(num3,:);
figure,imagesc(cc);colormap(jet);colorbar;axis image;
save cc_a.txt cc_a -ascii
%% �������ͼ����ʾ�����ȡ�γ�ȡ�����ֵ��
wrap = wrap(-4*pi*def/0.056);          % 0.056����Sentinel-1������5.6cm��
figure;imagesc(wrap);colorbar;colormap(jet);axis image;
ase_wrap = [lon(:) lat(:) wrap(:)];
num1=find(~isnan(ase_wrap(:,3)));
ase_wrap=ase_wrap(num1,:);
save wrap_a.txt ase_wrap -ascii
%% �����α�ͼ����ʾ�����ȡ�γ�ȡ��α�ֵ����λΪm����
figure;imagesc(def);colorbar;colormap(jet);axis image;
ase_def=[lon(:) lat(:) def(:)];   % def(:)*100�ɱ�Ϊcm
num=find(~isnan(ase_def(:,3)));
ase_def=ase_def(num,:);
save disp_a.txt ase_def -ascii
%% ������ͼ����ʾ�����ȡ�γ�ȡ����ֵ��
unwrap=-4*pi*def/0.056;               % �α�ת��λ
figure;imagesc(unwrap);colorbar;colormap(jet);axis image;
ase_unwrap = [lon(:) lat(:) unwrap(:)];
num2=find(~isnan(ase_unwrap(:,3)));
ase_unwrap=ase_unwrap(num2,:);
save unwrap_a.txt ase_unwrap -ascii