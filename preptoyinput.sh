#!/bin/bash

########################################################
# Prepare input ROOT files to be used in generatetoys.sh
########################################################

YEAR="2018"
DATE="2025_06_03"
OUTDIR="raw_inputs/${YEAR}/${DATE}"

# Do you want to re-copy input ROOT files to local area?
FETCH_INPUTS=true # true or false; takes ~3 minutes

# Do you want to run merge_file_script_mctoy.py (necessary to generate toys)
MERGE_INPUTS=true # true or false; takes ~13 minutes for standard categories, ~16 for Lep options

# # Are using 2D Alphabet output? (Option from Hichem not currently enabled - AWB 2025.05.16)
# WORKSPACE='2Dworkspace' # YES
# #WORKSPACE='No2Dworkspace' # NO

# Start the timer
START_TIME=$SECONDS

## Copy input ROOT files to local area
if $FETCH_INPUTS; then

    # Emptying the input directory
    echo " > Make new directory ${OUTDIR}"
    if [ -d $OUTDIR ]; then
    	rm -rf $OUTDIR
    fi
    mkdir -p $OUTDIR

    # Copy all 2D plots
    echo " > Copy all input 2D histogram files to raw_inputs ..."
    # -- Hadronic categories from Siddhesh (gg0l, Vjj, tt0l, Zvv) --
    echo "Starting hadronic ..."
    cp -r /eos/cms/store/user/ssawant/htoaa/analysis/20250603_*DatacardsFullSyst/2018/2DAlphabet_inputFiles/* ${OUTDIR}/
    # -- VBF --
    echo "Starting VBF ..."
    mkdir ${OUTDIR}/VBFjj
    cp /afs/cern.ch/user/m/moanwar/public/2DAlphabet_2018_4June/analyze_htoaa_stage1.root ${OUTDIR}/VBFjj/
    # -- Leptonic categories from Hichem (Zll, Wlv, ttlv, ttll) --
    echo "Starting leptonic ..."
    cp -r /afs/cern.ch/user/h/hboucham/public/2D_Alphabet_Inputs/2D18_2LZ_060325  ${OUTDIR}/Zll
    cp -r /afs/cern.ch/user/h/hboucham/public/2D_Alphabet_Inputs/2D18_2Ltt_060325 ${OUTDIR}/ttbll
    for CAT in WlvLo WlvHi ttblv ttbblv; do
	for WP in WP40 WP60 WP80; do
	    mkdir -p ${OUTDIR}/${CAT}/${WP}
	    cp /afs/cern.ch/user/h/hboucham/public/2D_Alphabet_Inputs/2D18_1L_060325/${WP}/${CAT}*root ${OUTDIR}/${CAT}/${WP}/
	done
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

    # Calculate elapsed time 
    ELAPSED=$((SECONDS - START_TIME))
    hours=$((ELAPSED / 3600))
    minutes=$(((ELAPSED % 3600) / 60))
    seconds=$((ELAPSED % 60))
    echo "Time to fetch inputs: $hours hour(s), $minutes minute(s), $seconds second(s)"

fi ## End conditional: if $FETCH_INPUTS


if $MERGE_INPUTS; then
    # Prepare inputs
    echo " > Merging categories (LepHi, LepLo, LepIncl, gg0lIncl, VBFjjIncl, VjjIncl, tt0l)"
    for CAT in LepLo LepHi LepIncl gg0lIncl VBFjjIncl VjjIncl tt0l; do
    	## Producing "Incl" categories also produces Hi/Lo plots
    	echo " > python3 merge_file_script_mctoy.py ${CAT}"
    	python3 merge_file_script_mctoy.py ${CAT}
    done

    # Calculate elapsed time 
    ELAPSED=$((SECONDS - START_TIME))
    hours=$((ELAPSED / 3600))
    minutes=$(((ELAPSED % 3600) / 60))
    seconds=$((ELAPSED % 60))
    echo "Time to merge standard categories: $hours hour(s), $minutes minute(s), $seconds second(s)"

    echo " > Merging modified LepHi and LepLo categories (A - H)"
    for mod in A B C D E F G H; do
    	echo " > python3 merge_file_script_mctoy.py LepLo${mod}"
    	python3 merge_file_script_mctoy.py LepLo${mod}
    	echo " > python3 merge_file_script_mctoy.py LepHi${mod}"
    	python3 merge_file_script_mctoy.py LepHi${mod}
    done
fi  ## End conditional: if $MERGE_INPUTS

# Calculate elapsed time 
ELAPSED=$((SECONDS - START_TIME))
hours=$((ELAPSED / 3600))
minutes=$(((ELAPSED % 3600) / 60))
seconds=$((ELAPSED % 60))
echo "Total runtime: $hours hour(s), $minutes minute(s), $seconds second(s)"
