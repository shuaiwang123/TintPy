clc;clear all;close all;
%% 读取累积形变
dispname=struct2cell(dir('*_disp_geo'));
[k,len]=size(dispname);
% 自动从disp_geo.hdr文件中读取参数
hdrname=struct2cell(dir('*_disp_geo.hdr'));
fid = fopen(hdrname{1,1});
A = textscan(fid,'%s','headerlines', 7);
fclose(fid);
line=str2double(A{1,1}{6,1});
sample=str2double(A{1,1}{3,1});
left_lon=strsplit(A{1,1}{40,1},',');
left_lon=str2double(left_lon{1,1});
left_lat=strsplit(A{1,1}{41,1},',');
left_lat=str2double(left_lat{1,1});
cha=strsplit(A{1,1}{42,1},',');
cha=str2double(cha{1,1});
A=left_lon:cha:left_lon+(sample-1)*cha;
B=left_lat:-cha:left_lat-(line-1)*cha;
[lon,lat]=meshgrid(A,B);
for i=2:len
    dat=freadbk(dispname{1,i},line,'float32');
    numout=find(~isnan(dat));
    disp{i}=[numout lon(numout) lat(numout) dat(numout)];
end
disp(1)=[];
disp=cell2mat(disp);
inf=[disp(:,1) disp(:,2) disp(:,3)];
disp0=disp(:,4:4:end);
disp=[inf disp0];
[m,~]=size(disp);
C=zeros(m,1);
disp=[disp(:,1:3) C disp(:,4:end)];       % 最终得到的累积形变数据（点号、经度、纬度、每张影像的累积形变）
save disp;
%% 绘制平均速率图
dat0=freadbk('SI_vel_geo',line,'float32');
figure,imagesc(dat0);colorbar;colormap;axis image;
numout0=find(~isnan(dat0));
scout0=[numout0 lon(numout0) lat(numout0) dat0(numout0)];
save 'vel_geo.txt' scout0 -ascii;
%% 绘制累积形变图
dat1=freadbk(dispname{1,len},line,'float32');                                % 读取最后一张时间的形变图
figure,imagesc(dat1);colorbar;colormap;axis image;
numout1=find(~isnan(dat1));
scout1=[lon(numout1) lat(numout1) dat1(numout1)];
save 'last_disp_geo.txt' scout1 -ascii;
%% 根据点号获取累计形变
a=1;                          % 需读取点的个数
[m,n]=size(disp);
D=zeros(a,n);
for i=1:a
    x=input('键入序列号:');
    A=find(disp(:,1)==x);
    D(i,:)=disp(A,:);
end
%% 获取影像日期（使用Excel画图时，将其转换为日期格式）
dispname=struct2cell(dir('*_disp_geo'));
[~,len]=size(dispname);
for i=1:len
    text=strsplit(dispname{1,i},'_');
    tmp=str2double(text{1,2});
    date(i)=tmp;
end
%% 随机剔除平均速率图中的点
clear all;clc;close all;
a=load('vel_geo.txt');
% num=length(a);
% a(:,1)=a(:,1)-0.000258;  % 坐标偏移修复
% 去除NaN值
% c=find(~isnan(a(:,1)));
% b=[a(c,1:2) a(c,4)];
% b=a(c,1:3);
% 裁剪
% c=find(a(:,2)>=103.669664&a(:,2)<=103.684189&a(:,3)>=30.274171&a(:,3)<30.281289);
% c=find(a(:,2)>=103.67&a(:,2)<=103.68&a(:,3)>=30.27&a(:,3)<30.28);
% c=find(a(:,2)>=102.362804&a(:,2)<=102.405109&a(:,3)>=29.929177&a(:,3)<29.962863);

% mean=a(c,:);
% mean_down=mean;

mean=a;
% 在指定区间内随机剔点
a=-100000;b=100000;                                    % 指定区间左右端点
n=4;                                                                 % 指定降采样的倍数
c_in=find(mean(:,4)>=a&mean(:,4)<=b);      % 搜索区间内的点
c_out=find(mean(:,4)<a|mean(:,4)>b);           % 搜索区间外的点
c_in_num=length(c_in);                                  % 读取区间内的点的个数
R=1+fix(rand(1,round(c_in_num/n))*c_in_num);   % 在区间[1,c_in_num]内产生1/n倍c_in_num个随机数
R_num=length(R);          % 读取随机点的个数
R=R';
% 根据产生的随机数对原始区间内的点重采样
c_down=zeros(R_num,1);
for q=1:R_num
    p=R(q,1);                           % 依次读取随机数
    c_down(q,1)=c_in(p,1);     % 读取随机数对应的点的原始序号
end
c_all=[c_out;c_down];
mean_down=mean(c_all,:);
fid=fopen('xsc_T.txt','wt');     % 不要使用save保存文件，ArcGIS分割列数据时，存在问题
fprintf(fid,'%d\t%f\t%f\t%f\n',mean_down');
fclose(fid);