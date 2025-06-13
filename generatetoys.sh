#!/bin/bash

#################################################################
# Generate toys from ROOT file inputs prepared by preptoyinput.sh
#################################################################

YEAR="2018"
DATE="2025_06_03"
OUTDIR="raw_inputs/${YEAR}/${DATE}"

# Adjust number of toys
NTOYS=100 # Minimum of 2. 2500 takes about 15 minutes per category (bkg-only + 11 signal injections)

# Do you want to generate toys from MC or Data or both?
#TOYSOURCE='MC'
#TOYSOURCE='Data'
TOYSOURCE='DataAndMC'

# # Are using 2D Alphabet output? (Option from Hichem not currently enabled - AWB 2025.05.16)
# WORKSPACE='2Dworkspace' # YES
# #WORKSPACE='No2Dworkspace' # NO

# Start the timer
START_TIME=$SECONDS

# Categories for which to generate toys
declare -a CATS=('LepLo' 'LepHi' 'LepIncl' 'gg0lLo' 'gg0lHi' 'ggIncl' 'VjjLo' 'VjjHi' 'VjjIncl' 'tt0l')
#declare -a CATS=('LepHiA' 'LepHiB' 'LepHiC' 'LepHiD' 'LepHiE' 'LepHiF' 'LepHiG' 'LepHiH' 'LepLoA' 'LepLoB' 'LepLoC' 'LepLoD' 'LepLoE' 'LepLoF' 'LepLoG' 'LepLoH')

## Generate toys for each category
for CAT in "${CATS[@]}"; do
    echo " > Making toys for $CAT category .. "
    python3 Haa4b_makeMCtoy.py $CAT $NTOYS $TOYSOURCE
    # Calculate elapsed time 
    ELAPSED=$((SECONDS - START_TIME))
    hours=$((ELAPSED / 3600))
    minutes=$(((ELAPSED % 3600) / 60))
    seconds=$((ELAPSED % 60))
    echo "Completed $CAT, runtime so far: $hours hour(s), $minutes minute(s), $seconds second(s)"
    echo ""
done

echo "Total runtime: $hours hour(s), $minutes minute(s), $seconds second(s)"
