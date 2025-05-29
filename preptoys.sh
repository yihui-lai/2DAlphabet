#!/bin/bash
## Modified from https://raw.githubusercontent.com/bouchamaouihichem/2DAlphabet/refs/heads/dev25_0501/runToys.sh

#########################################################################
# Updated bash script to run the full MC Toy chain
# Adapted from runtoystudy.sh by Hichem B
#########################################################################

# Start the timer
START_TIME=$SECONDS

# Do you want to re-copy input ROOT files to local area?
FETCH_INPUTS=false # true or false

# Adjust number of toys
NTOYS=400 # Minimum of 2. 2500 takes about 15 minutes per category (bkg-only + 19 signal injections)

# # Are using 2D Alphabet output? (Option from Hichem not currently enabled - AWB 2025.05.16)
# WORKSPACE='2Dworkspace' # YES
# #WORKSPACE='No2Dworkspace' # NO

# Do you want to generate toys from MC or Data or both?
TOYSOURCE='MC'
#TOYSOURCE='Data'
#TOYSOURCE='DataAndMC'

# Categories for which to generate toys
declare -a CATS=('gg0lHi' 'gg0lLo' 'gg0lIncl' 'LepHi' 'LepLo' 'LepIncl' 'VBFjjHi' 'VBFjjLo' 'VBFjjIncl')


## Copy input ROOT files to local area, then merge files
if $FETCH_INPUTS; then

    # Emptying the input directory
    echo " > Make new raw_inputs directory .. "
    if [ -d "raw_inputs" ]; then
	rm -rf "raw_inputs"
    fi
    mkdir "raw_inputs"

    # Copy all 2D plots
    echo " > Copy all input 2D histogram files .. "
    # -- ggH --
    cp -r /eos/cms/store/user/ssawant/htoaa/analysis/20250502_gg0l_FullSyst/2018/2DAlphabet_inputFiles_pseudodata raw_inputs/2D_in_gg0l_2025_05_02
    # -- VBF --
    mkdir raw_inputs/2D_in_VBFjj_2025_04_06
    cp -r /afs/cern.ch/user/m/moanwar/public/forYihui/2DAlphabetfiles_VBF_inputs/VBFLo_Xto4bv2 raw_inputs/2D_in_VBFjj_2025_04_06/VBFjjLo
    cp -r /afs/cern.ch/user/m/moanwar/public/forYihui/2DAlphabetfiles_VBF_inputs/VBFHi_Xto4bv2 raw_inputs/2D_in_VBFjj_2025_04_06/VBFjjHi
    # -- Leptonic --
    cp -r /afs/cern.ch/user/h/hboucham/public/2D_Alphabet_Inputs/2D_2LZ_030625_mAa raw_inputs/2D_in_Zll_2025_03_06
    cp -r /afs/cern.ch/user/h/hboucham/public/2D_Alphabet_Inputs/2D_2Ltt_030625_mAa raw_inputs/2D_in_ttll_2025_03_06
    cp -r /afs/cern.ch/user/h/hboucham/public/2D_Alphabet_Inputs/2D_1L_030625_mAa raw_inputs/2D_in_Wlv_ttlv_2025_03_06

    # Rename some files
    echo " > Rename some confusingly named files ('Data' really means 'MC'!) .. "
    for iCat in gg0lLo gg0lHi gg0lIncl;
    do
	mv raw_inputs/2D_in_gg0l_2025_05_02/${iCat}/${iCat}_Data_2018.root raw_inputs/2D_in_gg0l_2025_05_02/${iCat}/${iCat}_MC_2018.root
	mv raw_inputs/2D_in_gg0l_2025_05_02/${iCat}/${iCat}_Data_2018_backup.root raw_inputs/2D_in_gg0l_2025_05_02/${iCat}/${iCat}_Data_2018.root
    done
    for jCat in Lo Hi;
    do
	mv raw_inputs/2D_in_VBFjj_2025_04_06/VBFjj${jCat}/VBFjj${jCat}_Xto4bv2_Data_2018.root raw_inputs/2D_in_VBFjj_2025_04_06/VBFjj${jCat}/VBFjj${jCat}_Xto4bv2_MC_2018.root
	mv raw_inputs/2D_in_VBFjj_2025_04_06/VBFjj${jCat}/VBFjj${jCat}_Xto4bv2_Data_2018_backup.root raw_inputs/2D_in_VBFjj_2025_04_06/VBFjj${jCat}/VBFjj${jCat}_Xto4bv2_Data_2018.root
    done

    # ## Option from Hichem not currently enabled - AWB 2025.05.16
    # if [[ "${WORKSPACE}" == "2Dworkspace" ]]
    # then
    # 	echo " > Copy all 2DAlphabet output workspace files .. "
    # 	# -- ggH --
    # 	cp -r /eos/cms/store/user/ssawant/htoaa/analysis/20250502_gg0l_FullSyst/2018/2DAlphabet_fits_pseudodata raw_inputs/2D_out_gg0l_2025_05_07
    # 	# -- VBF --
    # 	cp -r /afs/cern.ch/user/m/moanwar/public/forYihui/taggerv2_wp40Andwp60 raw_inputs/2D_out_VBFjj_2025_03_12
    # 	# -- Leptonic --
    # 	cp -r /afs/cern.ch/user/h/hboucham/public/2D_Alphabet_Outputs/2D_Limits_040125 raw_inputs/2D_out_Lep_2025_04_01
    # fi

    # Prepare inputs
    echo " > Merging categories (LepHi, LepLo, gg0lIncl, VBFjjIncl)"
    python3 merge_file_script_mctoy.py LepHi
    python3 merge_file_script_mctoy.py LepLo
    python3 merge_file_script_mctoy.py gg0lIncl
    python3 merge_file_script_mctoy.py VBFjjIncl

fi
## End conditional: if $FETCH_INPUTS


## Generate toys for each category
for CAT in "${CATS[@]}"; do
    echo " > Making toys for $CAT category .. "
    python3 Haa4b_makeMCtoy.py $CAT $NTOYS $TOYSOURCE
done


# Calculate elapsed time 
ELAPSED=$((SECONDS - START_TIME))
hours=$((ELAPSED / 3600))
minutes=$(((ELAPSED % 3600) / 60))
seconds=$((ELAPSED % 60))
echo "Total runtime: $hours hour(s), $minutes minute(s), $seconds second(s)"
