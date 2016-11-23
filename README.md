# fpixphase1

## /config_BpI
config files for BpI

## /config_BmO
config files for BmO

## /config_BpO_warm 
config files for BpO warm operation.

## /MakePixelConfigs
Dumper scripts used for calibration result quick check.

(**Source environmental variables first, then run these scripts under this folder only**)

- POHBias

  ```bash
  python dumpAll_pohbias.py <pohbias run number>
  ```
  
- Delay25
  ```bash
  python dumpAll_delay25_byPrt.py <delay25 run number>
  ```

- TBMDelayWithScores

  ```bash
  python dumpAll_tbmdelaywscores2d_withpoints.py <tbm run number>
  ```

- CalDel

  ```bash
  python dumpAll_caldel.py <caldel run number>
  ```
  
- VcThrCalDel
  ```bash
  python dumpAll_vcthrcaldel.py <vcthr run number>
  ```
  
- PixelAlive
  Generate root file first, then 
  
  ```bash
  python dumpAll_pixelalive.py <pixelAlive run number>
  # make plots grouped in a module
  python dumpAll_pixelalive_map.py <pixelAlive run number>
  ```
  
- SCurve
  
  **step1** Generate root file first,
  
  ```bash
  source runscurve.sh <run num> # one fed per process, comment out feds you don't need
  ```
  **step2** then
  
  ```bash
  python dumpAll_scurve_simple.py <scurve run number> # giving 1D summary plot
  python dumpAll_scurve.py <scurve run number> # giving 2D module map
  ```
  
- BB
  
  **Step1**
  
  ```bash
  python bb3Calib.py <bb run number>
  ```
  
  **step2** generate root file,
  
  ```bash
  source runscurve.sh <run num> # one fed per process, comment out feds you don't need
  ```
 
  **steps3** then
  
  ```bash
  python dumpAll_bb3_simple.py <bb run number> # giving 1D summary plot
  python dumpAll_bb3.py <bb run number> # choose the right HC you want to analyze from line#5-8 in write_other_hc_configs.py
  ```
  
(**Other scripts**)

- *count_dead_pixels.py*
  
  Give number of 'dead' pixels whose threshold beyond certain range provided(default is (30,120)) per module
  
  ```bash
  python count_dead_pixels.py <bb run number>
  ```

- *insertTbmAsDefault.py*
  
  Insert TBMDelayWithScores calibration result into `$PIXELCONFIGURATIONBASE/tbm` and ask to set as default
  
  ```bash
  python insertTbmAsDefault.py <tbm run number>
  ```

  Insert picked calibration result from dumpped folder into `$PIXELCONFIGURATIONBASE/tbm` and ask to set as default
  
  ```bash
  python insertTbmAsDefault.py <tbm run#> dump
  ```
  
- *mkDetConfig.py*
  
  Make decconfig file & ask to set as default by given option. Do `python mkDetConfig.py -h` to know how to use it.
  
- *mkCalibWithDet.sh*
  
  Insert config alias by given detconfig alias while others set as default.
  
  ```bash
  source mkCalibWithDet.sh <configAlias> <detconfigAlias> <calibrationName>
  # <calibrationName> could be [POHBias, TBMDelayWithScores, CalDel, VcThrCalDel, PixelAlive, SCurve, BB]
  ```
