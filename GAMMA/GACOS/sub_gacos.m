function []=sub_gacos(diff_file,m_gacos_file,s_gacos_file,inc_angle,line)
% subtract gacos aps phase from diff_file
% read diff.int
diff_int=freadbkbig(diff_file,line,'cpxfloat32');
figure('visible','off'),imagesc(angle(diff_int));colorbar;colormap(jet);
saveas(gcf,'diff.int','png')
% read master and slave gacos phase
m_gacos=freadbkbig(m_gacos_file,line,'float32');
s_gacos=freadbkbig(s_gacos_file,line,'float32');
figure('visible','off'),imagesc(m_gacos);colorbar;colormap(jet);
saveas(gcf,'m_gacos','png')
figure('visible','off'),imagesc(s_gacos);colorbar;colormap(jet);
saveas(gcf,'s_gacos','png')
% get diff_gacos
m_gacos=m_gacos.*cosd(inc_angle);
s_gacos=s_gacos.*cosd(inc_angle);
diff_gacos=s_gacos-m_gacos;
clear m_gacos;clear s_gacos;
figure('visible','off'),imagesc(diff_gacos);colorbar;colormap(jet);
saveas(gcf,'diff_gacos','png')
% real2cpx
atodata_cpx=complex(cos(diff_gacos),sin(diff_gacos));
figure('visible','off'),imagesc(angle(atodata_cpx));colorbar;colormap(jet);
saveas(gcf,'diff_gacos_cpx','png')
% subtract
diff_correct=diff_int.*(atodata_cpx);
figure('visible','off'),imagesc(angle(diff_correct));colorbar;colormap(jet);
saveas(gcf,'diff_correct','png')
if exist([diff_file '.gacos'], 'file'):
    delete([diff_file '.gacos'])
end
fwritebkbig(diff_correct,[diff_file '.gacos'],'cpxfloat32');

end