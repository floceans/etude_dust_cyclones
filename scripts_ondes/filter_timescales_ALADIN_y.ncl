; Author : P. Peyrille
; Lanczos filter applied on (time,lat,lon) parameter 
; run with command line : 
; ncl cvar=\"${cvar}\" lfilter=\"2-10\" filter_timescales.ncl  > output 2>&1 
; cvar=variable name in input file , otherwise just write it below. 
; lfilter = 2_10 selects 2 to 10 days filter. See options in the program (2-10,2-15,15-90,90-365,>365)
;
; Inputs: 
; --------
; cvar(time,lat,lon)= parameter to be filtered (vorticity, olr, V wind, precipitation)
; filename :  is supposed to be cvar+"_anom_1979-2021.nc". Should contain a long time period to filter desired scales => change if necessary
; cdir : data directory => change if necessary
;
; Outputs:
; -------
; cfout=cvar+"_anom_BP-2-10_1979-2021.nc" , same parameter name as input filename
; 
begin

; User Input:
; cvar =                     ; if needed
cdir="/cnrm/mosca/USERS/gevaudanm/NO_SAVE/ALADIN/CAM20/output/CAM20-ERA5_test"+EXP+"/"                    ; data directory
cfile=cvar+fname+"day_"+yini+"0101-"+yend+"1231.nc"      ; file name (1 file to be filtered)

dt=1.                        ; sampling per day (here daily data assumed)
;
 print(cvar)
 print(lfilter)
 f=addfile(cdir+cfile,"r")
 x=f->$cvar$
 time=f->time
 lat=f->lat
 lon=f->lon
 bounds_lat = f->bounds_lat
 bounds_lon = f->bounds_lon
 if (cvar.ne."pr") then
  plev = f->plev
 end if
 if (lfilter.eq."2-90") then
  ihp     = 2                             ; band pass
  sigma   = 1.0                           ; Lanczos sigma
  nWgt    = 201                           ; loose 100 each end                            
  fca     = dt/90.                       ; start freq
  fcb     = dt/2.                       ; last  freq
  cfout=cvar+"_anom_BP-2-90"+fname+"day_"+yini+"0101-"+yend+"1231.nc"

 else if  (lfilter.eq."90-365") then
  ihp     = 2                             ; band pass
  sigma   = 1.0                           ; Lanczos sigma
  nWgt    = 201                           ; loose 100 each end                            
  fca     = dt/365.                       ; start freq
  fcb     = dt/90.                       ; last  freq
  cfout=cvar+"_anom_BP-91-365"+fname+"day_"+yini+"0101-"+yend+"1231.nc"
 
 else if (lfilter.eq."365") then
  ihp     = 0                             ; low pass
  sigma   = 1.0                           ; Lanczos sigma
  nWgt    = 201                           ; loose 100 each end
  fca     = dt/366.                       ; start freq
  fcb     = -999.
  cfout=cvar+"_anom_LP-365"+fname+"day_"+yini+"0101-"+yend+"1231.nc"

 else if  (lfilter.eq."2-15") then
  ihp     = 2                             ; band pass
  sigma   = 1.0                           ; Lanczos sigma
  nWgt    = 201                           ; loose 100 each end                            
  fca     = dt/15.                       ; start freq
  fcb     = dt/2.                       ; last  freq
  cfout=cvar+"_anom_BP-2-15"+fname+"day_"+yini+"0101-"+yend+"1231.nc"

 else if  (lfilter.eq."15-90") then
  ihp     = 2                             ; band pass
  sigma   = 1.0                           ; Lanczos sigma
  nWgt    = 201                           ; loose 100 each end                            
  fca     = dt/90.                       ; start freq
  fcb     = dt/15.                       ; last  freq
  cfout=cvar+"_anom_BP-15-90"+fname+"day_"+yini+"0101-"+yend+"1231.nc"

 else if  (lfilter.eq."2-10") then
  ihp     = 2                             ; band pass
  sigma   = 1.0                           ; Lanczos sigma
  nWgt    = 201                           ; loose 100 each end                            
  fca     = dt/10.                       ; start freq
  fcb     = dt/2.                       ; last  freq
  cfout=cvar+"_anom_BP-2-10"+fname+"day_"+yini+"0101-"+yend+"1231.nc"

 end if

 end if
 end if
 end if 
 end if 
 end if 





;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Filtering weights and Filtering
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

wgt     = filwgts_lanczos (nWgt, ihp, fca, fcb, sigma )
printVarSummary(wgt)

printVarSummary(x)
xBPF    = wgt_runave_n_Wrap ( x, wgt, 0 ,0)      ; 20-70
printVarSummary(xBPF)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Create netcdf file
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
nlat=dimsizes(lat(:,0))
nlon=dimsizes(lon(0,:))
nvertex = 4
axis_nbounds = 2

setfileoption("nc","Format","NetCDF4Classic")
system("rm -f "+cfout)

f1 = addfile(cdir+cfout ,"c")  ; open output netCDF file
setfileoption(f1,"DefineMode",True)
dimNames = (/"time", "y", "x", "nvertex", "axis_nbounds", "lev"/)  
dimSizes = (/ -1   ,  nlat,  nlon,  nvertex,  axis_nbounds, 1 /) 
dimUnlim = (/ True , False, False, False, False, False /)   
filedimdef(f1,dimNames,dimSizes,dimUnlim)
filevardef(f1, "time" ,typeof(time),(/"time"/)) 
filevardef(f1, "lat"  ,typeof(lat),(/"y","x"/))                          
filevardef(f1, "lon"  ,typeof(lon),(/"y","x"/))
filevardef(f1,"bounds_lat","double",(/"y","x","nvertex"/))
filevardef(f1,"bounds_lon","double",(/"y","x","nvertex"/))
if (cvar.ne."pr") then
 filevardef(f1, "plev" ,typeof(plev), (/"lev"/))                          
end if
filevardef(f1, cvar    ,typeof(xBPF)  ,getvardims(xBPF))    
 ;
filevarattdef(f1,cvar,xBPF)                           ; copy T attributes
filevarattdef(f1,"time" ,time)                    ; copy time attributes
filevarattdef(f1,"lat"  ,lat)                     ; copy lat attributes
filevarattdef(f1,"lon"  ,lon)                     ; copy lon attributes
 
setfileoption(f1,"DefineMode",False)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;fout=addfile(cfout,"c")
;fout->olr_anom=xBPF
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; output in netcdf file
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
f1->$cvar$=(/xBPF/)
f1->time=(/time/)
f1->lat=(/lat/)
f1->lon=(/lon/)

end
