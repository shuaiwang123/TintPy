function []=sub_gacos(diff_file,m_gacos_file,s_gacos_file,inc_angle,line)
diff_int=freadbkbig(diff_file,line,'cpxfloat32');
% figure,imagesc(angle(diff_int));colorbar;colormap(jet);
saveas(gcf,'diff.int','png')
m_gacos=freadbkbig(m_gacos_file,line,'float32');
s_gacos=freadbkbig(s_gacos_file,line,'float32');
% figure,imagesc(m_gacos);colorbar;colormap(jet);
saveas(gcf,'m_gacos','png')
% figure,imagesc(s_gacos);colorbar;colormap(jet);
saveas(gcf,'s_gacos','png')
m_gacos=m_gacos.*cosd(inc_angle);
s_gacos=s_gacos.*cosd(inc_angle);
diff_gacos=s_gacos-m_gacos;
clear m_gacos;clear s_gacos;
% figure,imagesc(diff_gacos);colorbar;colormap(jet);
saveas(gcf,'diff_gacos','png')
% real2cpx
atodata_cpx=complex(cos(diff_gacos),sin(diff_gacos));
% figure,imagesc(angle(atodata_cpx));colorbar;colormap(jet);
saveas(gcf,'diff_gacos_cpx','png')
% correct
diff_correct=diff_int.*(atodata_cpx);
% figure,imagesc(angle(diff_correct));colorbar;colormap(jet);
saveas(gcf,'diff_correct','png')
filename=[diff_file '.gacos'];
fwritebkbig(diff_correct,filename,'cpxfloat32');
diff_int_gacos=freadbkbig(filename,line,'cpxfloat32');
% figure,imagesc(angle(diff_int_gacos));colorbar;colormap(jet);
