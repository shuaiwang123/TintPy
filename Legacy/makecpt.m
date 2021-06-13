close all
clear all
clc

% data=load('JapanE.dat');
% mind=min(data(:,3));
% maxd=max(data(:,3));

mind=-2;
maxd=2;

% color=load('out1.clr');
color=textread('out.clr', '' , 'headerlines', 1);

[row,col]=size(color);
for i=1:row
    shu(i,1)=color(i,1)/100*(maxd-mind)+mind;
    shu(i,2:4)=color(i,2:4);
end
for i=1:row-1
    fcolr(i,1:4)=shu(i,1:4);
    fcolr(i,5:8)=shu(i+1,1:4);
end
fid=fopen('out.cpt','wt');
[row,col]=size(fcolr);
str=' ';
for i=1:row
    for j=1:col
        if j==1||j==5
            fprintf(fid,'%6.2f',fcolr(i,j));
            fprintf(fid,str);
        else
            fprintf(fid,'%6.0f',fcolr(i,j));
            fprintf(fid,str);
        end
    end
    
    fprintf(fid,'\n');
end
fclose(fid);