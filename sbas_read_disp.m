clc;clear all;close all;
%% ��ȡ�ۻ��α�
dispname=struct2cell(dir('*_disp_geo'));
[k,len]=size(dispname);
% �Զ���disp_geo.hdr�ļ��ж�ȡ����
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
disp=[disp(:,1:3) C disp(:,4:end)];       % ���յõ����ۻ��α����ݣ���š����ȡ�γ�ȡ�ÿ��Ӱ����ۻ��α䣩
save disp;
%% ����ƽ������ͼ
dat0=freadbk('SI_vel_geo',line,'float32');
figure,imagesc(dat0);colorbar;colormap;axis image;
numout0=find(~isnan(dat0));
scout0=[numout0 lon(numout0) lat(numout0) dat0(numout0)];
save 'vel_geo.txt' scout0 -ascii;
%% �����ۻ��α�ͼ
dat1=freadbk(dispname{1,len},line,'float32');                                % ��ȡ���һ��ʱ����α�ͼ
figure,imagesc(dat1);colorbar;colormap;axis image;
numout1=find(~isnan(dat1));
scout1=[lon(numout1) lat(numout1) dat1(numout1)];
save 'last_disp_geo.txt' scout1 -ascii;
%% ���ݵ�Ż�ȡ�ۼ��α�
a=1;                          % ���ȡ��ĸ���
[m,n]=size(disp);
D=zeros(a,n);
for i=1:a
    x=input('�������к�:');
    A=find(disp(:,1)==x);
    D(i,:)=disp(A,:);
end
%% ��ȡӰ�����ڣ�ʹ��Excel��ͼʱ������ת��Ϊ���ڸ�ʽ��
dispname=struct2cell(dir('*_disp_geo'));
[~,len]=size(dispname);
for i=1:len
    text=strsplit(dispname{1,i},'_');
    tmp=str2double(text{1,2});
    date(i)=tmp;
end
%% ����޳�ƽ������ͼ�еĵ�
clear all;clc;close all;
a=load('vel_geo.txt');
% num=length(a);
% a(:,1)=a(:,1)-0.000258;  % ����ƫ���޸�
% ȥ��NaNֵ
% c=find(~isnan(a(:,1)));
% b=[a(c,1:2) a(c,4)];
% b=a(c,1:3);
% �ü�
% c=find(a(:,2)>=103.669664&a(:,2)<=103.684189&a(:,3)>=30.274171&a(:,3)<30.281289);
% c=find(a(:,2)>=103.67&a(:,2)<=103.68&a(:,3)>=30.27&a(:,3)<30.28);
% c=find(a(:,2)>=102.362804&a(:,2)<=102.405109&a(:,3)>=29.929177&a(:,3)<29.962863);

% mean=a(c,:);
% mean_down=mean;

mean=a;
% ��ָ������������޵�
a=-100000;b=100000;                                    % ָ���������Ҷ˵�
n=4;                                                                 % ָ���������ı���
c_in=find(mean(:,4)>=a&mean(:,4)<=b);      % ���������ڵĵ�
c_out=find(mean(:,4)<a|mean(:,4)>b);           % ����������ĵ�
c_in_num=length(c_in);                                  % ��ȡ�����ڵĵ�ĸ���
R=1+fix(rand(1,round(c_in_num/n))*c_in_num);   % ������[1,c_in_num]�ڲ���1/n��c_in_num�������
R_num=length(R);          % ��ȡ�����ĸ���
R=R';
% ���ݲ������������ԭʼ�����ڵĵ��ز���
c_down=zeros(R_num,1);
for q=1:R_num
    p=R(q,1);                           % ���ζ�ȡ�����
    c_down(q,1)=c_in(p,1);     % ��ȡ�������Ӧ�ĵ��ԭʼ���
end
c_all=[c_out;c_down];
mean_down=mean(c_all,:);
fid=fopen('xsc_T.txt','wt');     % ��Ҫʹ��save�����ļ���ArcGIS�ָ�������ʱ����������
fprintf(fid,'%d\t%f\t%f\t%f\n',mean_down');
fclose(fid);