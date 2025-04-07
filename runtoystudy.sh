# step1, create folder for raw files 
mkdir raw_inputs

# -- Leptonic --
cp -r /afs/cern.ch/user/h/hboucham/public/2D_Alphabet_Outputs/2D_Limits_040125 raw_inputs/Leptonic_2D_Limits_040125
cp -r /afs/cern.ch/user/h/hboucham/public/2D_Alphabet_Inputs/2D_*030625_mAa raw_inputs/
mkdir -p plots/HtoAA_2DAlphabet_merge_inputs_XXLo/2025_04_04_mAa/
mkdir -p plots/HtoAA_2DAlphabet_merge_inputs_XXHi/2025_04_04_mAa/
# run merge_file_script_mctoy.py to get input files for leptonic channel
# set CAT_OUT = 'XXHi'
python3 merge_file_script_mctoy.py
# modify CAT_OUT and run again 
# set CAT_OUT = 'XXLo'
python3 merge_file_script_mctoy.py
# now we have the raw input files in plots/HtoAA_2DAlphabet_merge_inputs_XX*/2025_04_04_mAa
# run Haa4b_makeMCtoy.py to make MC sum
# set category = "Leptonic_Hi"
python3 Haa4b_makeMCtoy.py
# set #category = "Leptonic_Lo"
# change category and run again 
python3 Haa4b_makeMCtoy.py
# -- Finished, we have all raw input files --

# -- VBF --
cp -r /afs/cern.ch/user/m/moanwar/public/forYihui/taggerv2_wp40Andwp60 raw_inputs/
cp -r /afs/cern.ch/user/m/moanwar/public/forYihui/2DAlphabetfiles_VBF_inputs plots/
mv plots/2DAlphabetfiles_VBF_inputs/VBFHi_Xto4bv2/VBFjjHi_Xto4bv2_Data_2018.root plots/2DAlphabetfiles_VBF_inputs/VBFHi_Xto4bv2/VBFjjHi_Xto4bv2_MC_2018.root
mv plots/2DAlphabetfiles_VBF_inputs/VBFHi_Xto4bv2/VBFjjHi_Xto4bv2_Data_2018_backup.root plots/2DAlphabetfiles_VBF_inputs/VBFHi_Xto4bv2/VBFjjHi_Xto4bv2_Data_2018.root
mv plots/2DAlphabetfiles_VBF_inputs/VBFLo_Xto4bv2/VBFjjLo_Xto4bv2_Data_2018.root plots/2DAlphabetfiles_VBF_inputs/VBFLo_Xto4bv2/VBFjjLo_Xto4bv2_MC_2018.root
mv plots/2DAlphabetfiles_VBF_inputs/VBFLo_Xto4bv2/VBFjjLo_Xto4bv2_Data_2018_backup.root plots/2DAlphabetfiles_VBF_inputs/VBFLo_Xto4bv2/VBFjjLo_Xto4bv2_Data_2018.root
# change category and run Haa4b_makeMCtoy.py to make toy MC and also compare MC with data 
# set category = "VBF_Hi"
python3 Haa4b_makeMCtoy.py
# change category and run Haa4b_makeMCtoy.py to make toy MC and also compare MC with data
# set category = "VBF_Lo"
python3 Haa4b_makeMCtoy.py
# -- Finished, we have all raw input files --

# -- ggH --
cp -r /eos/cms/store/user/ssawant/htoaa/2DAlphabet_datacards/20250403_Pseudodata raw_inputs/
mkdir -p plots/HtoAA_2DAlphabet_merge_inputs_gg0lIncl/2025_04_04_mAa/
mv raw_inputs/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_Data_2018.root raw_inputs/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_MC_2018.root
mv raw_inputs/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_Data_2018_backup.root raw_inputs/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_Data_2018.root
# run merge_file_script_mctoy.py to get input files for ggH channel
mkdir -p plots/HtoAA_2DAlphabet_merge_inputs_gg0lIncl/2025_04_04_mAa/
# set CAT_OUT = 'gg0lIncl'
python3 merge_file_script_mctoy.py
# change category and run Haa4b_makeMCtoy.py to make toy MC and also compare MC with data
# set category = "gg0lIncl"
python3 Haa4b_makeMCtoy.py
# -- Finished, we have all raw input files --
# -- Finished step1



# step 2, run htoaato4b.py to make datacards
for i in $(seq 0 1 2) # N toys
do 
echo $i
python3 htoaato4b_mctoy.py $i
mv fits_XXLo_Htoaato4b_mH_pnet_mA_15to55_WP60_2018 mctoysjson/fits_XXLo_Htoaato4b_mH_pnet_mA_15to55_WP60_2018_toy$i
# modify htoaato4b_mctoy.py and run this loop again for different categories
#mv fits_XXHi_Htoaato4b_mH_pnet_mA_15to55_WP60_2018 mctoysjson/fits_XXHi_Htoaato4b_mH_pnet_mA_15to55_WP60_2018_toy$i
#mv fits_gg0lIncl_Htoaato4b_mH_pnet_vs_massA34a_mA_15to55_WP40_2018 mctoysjson/fits_gg0lIncl_Htoaato4b_mH_pnet_vs_massA34a_mA_15to55_WP40_2018_toy$i
#mv fits_VBFjjHi_Xto4bv2_Htoaato4b_mH_pnet_mA_15to55_WP40_2018 mctoysjson/fits_VBFjjHi_Xto4bv2_Htoaato4b_mH_pnet_mA_15to55_WP40_2018_toy$i
#mv fits_VBFjjLo_Xto4bv2_Htoaato4b_mH_pnet_mA_15to55_WP40_2018 mctoysjson/fits_VBFjjLo_Xto4bv2_Htoaato4b_mH_pnet_mA_15to55_WP40_2018_toy$i
done


# step3, run Mergecards.sh to combine cards 
source Mergecards.sh

# step4, make summary plots
python3 Haa4b_limitsummary.py
python3 Haa4b_fitsummary.py


