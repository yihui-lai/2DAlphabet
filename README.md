# Installation instructions
```
cmssw-el7  ## Emulate SLC7 environment; required before any cmsenv
cmsrel CMSSW_11_3_4
cd CMSSW_11_3_4/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v9.1.0
cd ../../
git clone git@github.com:JHU-Tools/CombineHarvester.git
cd CombineHarvester/
git fetch origin
git checkout CMSSW_11_3_X
cd ../
scramv1 b clean
scramv1 b -j 8
git clone -b git@github.com:bouchamaouihichem/2DAlphabet.git
python3 -m virtualenv twoD-env
source twoD-env/bin/activate
cd 2DAlphabet/
python setup.py develop
mkdir plots
mkdir plots/HtoAA_2DAlphabet_merge_inputs_XXHi/
mkdir plots/HtoAA_2DAlphabet_merge_inputs_XXLo/
```


# Running instructions
```
cd /afs/cern.ch/user/h/hboucham/work/H4B/CMSSW_11_3_4/src/
cmssw-el7 
cmsenv
voms-proxy-init --voms cms
source twoD-env/bin/activate
cd 2DAlphabet
```

merge sub-categories into XXHi/XXLo by editing ```merge_file_script.py```
-  adjust ouput category (e.g: ```CAT_OUT = 'XXHi'``` or ```CAT_OUT = 'XXLo'```)
-  adjust sub-categories input directories (e.g: ```CATS_IN['WlvHi']['dir']   = '/afs/cern.ch/user/h/hboucham/public/2D_Alphabet_Inputs/2D_1L_030625_mA'+MA_reg+'/'```)
-  adjust output directory (e.g: ```DATE     = '2025_03_06_mA'+ MA_reg```)
-  Variation ```merge_file_script_Zvv.py``` includes ZvvHi/Lo as well, but currently not recommended to run this version.
- ```python3 merge_file_script.py```

Run 2D Alphabet after editing ```htoaato4b.py```:
- adjust input file directory (e.g: ```PATH    = AB_DIR+'HtoAA_2DAlphabet_merge_inputs_'+CAT+'/2025_03_06_mAa'```)
- adjust the following parameters: category ```CAT = [XXHi/XXLo]```, Higgs mass ```MASSH = [pnet/mass/msoft]```, working point ```WP = [WP40/WP60/WP80]```, year ```YEAR = [2018/2017/2016]```.
- optional but not recommended unless you know what you're doing: adjust fit ```FIT     =  '1d1C'```, nominal fail-to-pass transfer factor ```NOMTF   = 0.10 ``` and binning and more in the corresponding json files (e.g: ```XXHi_Htoaato4b.json```)
- ```python3 htoaato4b.py```
- 2D alphabet output directory example: ```fits_XX_Htoaato4b_mH_mass_mA_15to55_WP80_2018/```

Other scripts:
- ```XXCAT_yields.py```: returns yield table given merge directory (e.g: ```python3 XXCAT_yields.py plots/HtoAA_2DAlphabet_merge_inputs_XXHi/2025_03_06_mAa/```)
- ```HtoAA_StoB_estimate.py```: After selecting a sub-category ```current = "Zll"```, a working point ```"WP_CUTS": ['WP60'] ``` and updating the input directory ```"IN_DIR": '/afs/cern.ch/user/h/hboucham/public/2D_Alphabet_Inputs/2D_2LZ_021525_CAT34_mA34a_mH/'```, this script returns a sub-category purity and conservative limits using signal and data yields (e.g: ```python3  HtoAA_StoB_estimate.py```)

