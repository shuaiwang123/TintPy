## phase-stacking
`stacking diff_tab 1150 ph_rate sig_ph_rate sig_ph 100 100 - - - 1`

## view result
`disdt_pwr24 geo_ph_rate 20170120-20170219.utm.pwr 3462 1 1 0 5 1 .35`

## geocode data
`geocode_back ph_rate 1150 lookup_fine geo_ph_rate 3846 3573 1 0`
`geocode_back 20170303-20170327.pwr1 1150 lookup_fine geo_20170303-20170327.pwr1 3846 3573 1 0`
`geocode_back 20170303-20170327.diff.sm.cc 1150 lookup_fine geo_20170303-20170327.diff.sm.cc 3846 3573 1 0`

## make kmz
`rasdt_pwr24 geo_ph_rate geo_20170303-20170327.pwr1 3846 1 1 0 1 1 5 1. .35 1 mabian5.bmp geo_20170303-20170327.diff.sm.cc 1 0`
`kml_map mabian5.bmp dem_seg.par mabian5.kml`