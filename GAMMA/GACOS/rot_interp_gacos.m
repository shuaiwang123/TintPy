function [] = rot_interp_gacos(m_gacos_ztd, s_gacos_ztd, dem_seg_par, m_gacos_phs, s_gacos_phs)
    function [] = rot_interp(gacos_ztd, dem_seg_par ,gacos_phs)
        % resampled gacos aps data to required grid
        % read dem_seg.par
        fid=fopen(dem_seg_par,'r');
        parms = textscan(fid,'%s','headerlines', 6);
        fclose(fid);
        line=str2double(parms{1,1}{4,1});
        sample=str2double(parms{1,1}{2,1});
        left_lon=str2double(parms{1,1}{10,1});
        left_lat=str2double(parms{1,1}{6,1});
        cha=str2double(parms{1,1}{18,1});
        % generate grid
        A=left_lon:cha:left_lon+(sample-1)*cha;
        B=left_lat:-cha:left_lat-(line-1)*cha;
        [lon2,lat2]=meshgrid(A,B);
        % ztd2phase
        rscfile=[gacos_ztd,'.rsc'];
        fid=fopen(rscfile,'r');
        parms=textscan(fid, '%s');
        fclose(fid);
        wid=str2double(parms{1,1}{2,1});
        len=str2double(parms{1,1}{4,1});
        left_lon=str2double(parms{1,1}{14,1});
        left_lat=str2double(parms{1,1}{16,1});
        xstep=str2double(parms{1,1}{18,1});
        cha=xstep;
        A=left_lon:cha:left_lon+(wid-1)*cha;
        B=left_lat:-cha:left_lat-(len-1)*cha;
        [lon,lat]=meshgrid(A,B);
        if(max(max(lon2))>max(max(lon)) || max(max(lat2))>max(max(lat)) || min(min(lon2))<min(min(lat)) || min(min(lat2))<min(min(lat)))
            disp('cut_image: the input image is smaller than the output!');
            return;
        else
            fid=fopen(gacos_ztd,'rb');
            [ztd, ~]=fread(fid,[wid, len],'float');
            fclose(fid);
            % figure,imagesc(ztd);colorbar;colormap;
            ztd=rot90(flip(ztd),3);
            % figure,imagesc(ztd);colorbar;colormap;
            wavelength=0.055165;
            ztd_pha=-4*pi*ztd./wavelength;
            % figure,imagesc(ztd_pha);colorbar;colormap;
            inter_ztd_pha=interp2(lon,lat,ztd_pha,lon2,lat2,'cubic');
            % figure,imagesc(inter_ztd_pha);colorbar;colormap;
            if exist(gacos_phs, 'file'):
                delete(gacos_phs)
            end
            fwritebkbig(inter_ztd_pha,gacos_phs,'float32');
            clear lon;clear lat;clear ztd;clear ztd_pha;clear inter_ztd_pha;
        end
        
    end
% rotate and inpterpolate gacos
rot_interp(m_gacos_ztd, dem_seg_par, m_gacos_phs);
rot_interp(s_gacos_ztd, dem_seg_par, s_gacos_phs);

end
