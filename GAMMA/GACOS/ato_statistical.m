function []=ato_statistical(aec_unw_file,unw_file,inc_angle,line,width,range_spacing,azimuth_spacing)
aecimage=freadbkbig(aec_unw_file,line,'float32');
image=freadbkbig(unw_file,line,'float32');
% figure;imagesc(image);colormap jet; colorbar;
wavelength=0.055165;
gacos_imagedisp=-aecimage.*wavelength.*100./(4*pi);
imagedisp=-image.*wavelength.*100./(4*pi);
% figure;imagesc(imagedisp);colormap jet; colorbar;
% obtaining parameters of sampled pixels
ground_range=range_spacing/sind(inc_angle);
sample_size=5000;
lbox=round(sample_size/azimuth_spacing); % window size
rbox=round(sample_size/ground_range);% window size
n=100;  % window number
maxline=line-lbox;
maxrow=width-rbox;
line=randperm(maxline);
width=randperm(maxrow);
randline=line(1:n);
randrow=width(1:n);
for i=1:n
    aecsample=gacos_imagedisp(randline(i):randline(i)+lbox-1,randrow(i):randrow(i)+rbox-1);
    pixelnumber=sum(sum(aecsample~=0));
    rms=sum(aecsample(:))/pixelnumber;
    aecsample(aecsample==0)=rms;
    aecsamplesd(i)=sum(sum((aecsample-rms).^2))/pixelnumber;
    sample=imagedisp(randline(i):randline(i)+lbox-1,randrow(i):randrow(i)+rbox-1);
    pixelnumber=sum(sum(sample~=0));
    rms=sum(sample(:))/pixelnumber;
    sample(sample==0)=rms;
    samplesd(i)=sum(sum((sample-rms).^2))/pixelnumber;
end
A=find(isnan(aecsamplesd));
aecsamplesd(A)=0;
aecsd=mean(aecsamplesd);
B=find(isnan(samplesd));
samplesd(A)=0;
sd=mean(samplesd);
figure('visible','off'),imagesc(gacos_imagedisp);colorbar;colormap(jet);title(aecsd);
saveas(gcf,'disp_gacos','png')
figure('visible','off'),imagesc(imagedisp);colorbar;colormap(jet);title(sd);
saveas(gcf,'disp_orig','png')

end
