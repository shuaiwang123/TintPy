%% ???sarscape??PS?????????PS???shp????????????PS????¦Ã????????????¦Á??????
clear all;clc;close all;
a=shaperead('C:\thorly\Files\landslide\1_PS_processing\geocoding\1_PS_60_0.shp');
num=length(a);
s=struct2cell(a);
s(1,:)=[];
s1=cell2mat(s);
b=zeros(num,5);
xuhao=(1:num)';
b=[xuhao s1(1,:)' s1(2,:)' s1(4,:)' s1(3,:)'];
%b(:,2)=b(:,2)-0.000657+0.000237;  %??????????
b(:,2)=b(:,2)-0.000366;  %??????????
% c=find(b(:,2)>=85.9444&b(:,2)<=86.0296&b(:,3)>=27.9253&b(:,3)<=28.0334);
%c2=find(b(:,2)>=86.0296&b(:,2)<=86.0676&b(:,3)>=27.9253&b(:,3)<=28.0334);
% %c=find(b(:,2)>=85.9444&b(:,2)<=86.0676&b(:,3)>=27.9253&b(:,3)<=28.0334);
% mean=b(c,:);
mean=b;
%mean(:,3)=mean(:,3)-(-23.35);  %?¦Ï???1.8mm/y
fid=fopen('vel60.txt','wt');
fprintf(fid,'%d\t%f\t%f\t%f\t%f\n',mean');
fclose(fid);
%% ?????????????¦Á?????????txt??????????¦Á?????????
clear all
clc;
close all;
a=shaperead('C:\thorly\Files\landslide\1_PS_processing\geocoding\1_PS_60_0.shp');
s=struct2cell(a);
s(1,:)=[];
s1=cell2mat(s);
[r,l]=size(s1);
xuhao=(1:l)';
n=r-20+1;%???????
def=zeros(l,4);
for i=1:n
    def=[xuhao s1(1,:)' s1(2,:)' s1(19+i,:)'];
end
%  def(:,2)=def(:,2)+(1.5/3600);
%  cc=find(def(:,2)>=85.9444&def(:,2)<=86.0676&def(:,3)>=27.9253&def(:,3)<=28.0334);
%  defo=def(cc,:);
%  eval(['save ' num2str(i) '.txt def -ASCII']);
%% ???????¦Ã?????PS????????????????
clear all
clc
close all;
a=shaperead('C:\thorly\Files\landslide\1_PS_processing\geocoding\1_PS_70_0.shp');
num=length(a);
s=struct2cell(a);
s(1,:)=[];
s1=cell2mat(s);
[r,l]=size(s1);

%b=zeros(num,5);
xuhao=(1:num)';
b=[xuhao s1(1,:)' s1(2,:)' s1(4,:)' s1(3,:)'];
%b(:,2)=b(:,2)-0.000657+0.000237;  %??????????
%b(:,2)=b(:,2)-0.000366;  %??????????
c=find(b(:,2)>=102.863295&b(:,2)<=102.876878&b(:,3)>=29.994062&b(:,3)<=30.000900);
%c2=find(b(:,2)>=86.0296&b(:,2)<=86.0676&b(:,3)>=27.9253&b(:,3)<=28.0334);
% %c=find(b(:,2)>=85.9444&b(:,2)<=86.0676&b(:,3)>=27.9253&b(:,3)<=28.0334);
mean=b(c,:);
%mean=b;
%mean(:,3)=mean(:,3)-(-23.35);  %?¦Ï???1.8mm/y
save k25_PS_50_0.txt mean -ascii;
%% ???????¦Á?
point=[2641 2640];
s=size(point);
j=s(2); 
n=r-20+1;   % ???????
A=zeros(j,n);
for i=1:j
    x=point(i);
    for ii=1:n
        A(i,1)=x;
        A(i,ii+1)=s1(ii+19,x);
    end
end

figure;
for i=1:j
    plot(A(i,2:end));
    hold on;
end
grid on;
