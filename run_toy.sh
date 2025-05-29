## Run limits, bias, and goodness-of-fit for a single toy

iToy=$1            ## Toy index
TOYSOURCE=$2       ## Data or MC
MASSES=(15 30 55)  ## Needs to match hard-coded settings in htoaato4b_mctoy.py
NTOYGOF=10         ## Number of toys 2DAlphabet will run for goodness-of-fit test
YEAR="2018"
#FITS=("0x0" "0x0smr" "1d1C" "1x1C")  ## Needs to be a subset of FITLIST in htoaato4b_mctoy.py
FITS=("0x0" "1x1C")  ## Needs to be a subset of FITLIST in htoaato4b_mctoy.py
SIGINJ=""  ## Empty string for no signal injection
#SIGINJ="_mA_15_sigBr_005"  ## "_mA_XX_sigBr_YYY" (include leading "_")

## Output EOS directory to move ROOT files (avoid disk quota issues)
EOS_OUT_DIR="/eos/cms/store/user/abrinke1/HiggsToAA/2DAlphabet/ToyStudies/2025_05_27/"
echo "Just to be sure, you want to output to:"
echo ${EOS_OUT_DIR}

sToy="toy${iToy}"
## Toy "-1" corresponds to MCrounded or Data
if [ "${iToy}" == "-1" ]; then
    sToy="MCrounded"
    if [[ ${TOYSOURCE} == "Data" ]]; then
	sToy="Data"
    fi
fi

INDIR="output/mctoys"
OUTDIR="output/Mergecards/mc${sToy}"
if [[ ${TOYSOURCE} == "Data" ]]; then
    INDIR="output/datatoys"
    OUTDIR="${INDIR}/Mergecards/data${sToy}"
fi
if [ ! -d ${OUTDIR} ]; then
    mkdir -p ${OUTDIR}
fi

# Start the timer
START_TIME=$SECONDS


## WARNING!!! You have to run *all* the "sub-categories" before running the "Comb" categories
#for iCat in LepHi LepLo gg0lHi gg0lLo VBFjjIncl LepComb gg0lComb HadComb LepHadComb; do
for iCat in LepHi gg0lHi; do

    ## Define WP for each category type
    WP="UNDEF"
    if [[ $iCat == "gg0l"* || $iCat == "VBF"* || $iCat == "Had"* ]]; then
	WP="WP40"
    fi
    if [[ $iCat == "Lep"* && $iCat != "LepHadComb" ]]; then
	WP="WP60"
    fi

    ## Define component sub-categories for each super-category
    subCats=(${iCat})
    subCatsLep=()
    subCatsHad=()
    if [[ $iCat == "LepComb" ]]; then
	subCats=(LepHi LepLo)
    fi
    if [[ $iCat == "gg0lComb" ]]; then
	subCats=(gg0lHi gg0lLo)
    fi
    if [[ $iCat == "HadComb" ]]; then
	subCats=(gg0lHi gg0lLo VBFjjIncl)
    fi
    if [[ $iCat == "LepHadComb" ]]; then
	subCatsHad=(gg0lHi gg0lLo VBFjjIncl)
	subCatsLep=(LepHi LepLo)
    fi

    ## Make toys for each category
    if [[ $iCat != *"Comb" ]]; then
    	echo ">>>>>>>>>> Making Toy #${iToy} in category ${iCat} (${WP})"
    	python3 htoaato4b_mctoy.py "${iToy}" "${iCat}" "${TOYSOURCE}" "${SIGINJ:1}"
    	echo ">>>>>>>>>> Made Toy #${iToy} in category ${iCat} (${WP})"
    fi

    ## Merge datacards and run limits for each mA point
    echo ">>>>>>>>>> Merging datacards for Toy #${iToy} in category ${iCat} (${WP})"
    
    for iMA in "${MASSES[@]}"; do
	for iFit in "${FITS[@]}"; do
    	    echo "     <<<<< Now looking at mA = ${iMA}, fit = ${iFit}"

    	    in_cards=""
    	    for jCat in "${subCats[@]}"; do
    		new_card="${INDIR}/fits_${jCat}_Htoaato4b_mH_pnet_mA_${MASSES[0]}to${MASSES[-1]}_${WP}_${iFit}_${YEAR}_${sToy}${SIGINJ}/mA_${iMA}_area/card.txt"
		if test -f ${new_card}; then
    		    in_cards="${in_cards} ${new_card}"
		else
		    echo "Could not find input card:"
		    echo ${new_card}
		fi
    	    done
    	    if [[ $iCat == "LepHadComb" ]]; then
    		in_cards=""
    		for hCat in "${subCatsHad[@]}"; do
    		    new_card="${INDIR}/fits_${hCat}_Htoaato4b_mH_pnet_mA_${MASSES[0]}to${MASSES[-1]}_WP40_${iFit}_${YEAR}_${sToy}/mA_${iMA}_area/card.txt"
		    if test -f ${new_card}; then
    			in_cards="${in_cards} ${new_card}"
		    else
			echo "Could not find input card:"
			echo ${new_card}
		    fi
    		done
    		for lCat in "${subCatsLep[@]}"; do
    		    new_card="${in_cards} ${INDIR}/fits_${lCat}_Htoaato4b_mH_pnet_mA_${MASSES[0]}to${MASSES[-1]}_WP60_${iFit}_${YEAR}_${sToy}/mA_${iMA}_area/card.txt"
		    if test -f ${new_card}; then
    			in_cards="${in_cards} ${new_card}"
		    else
			echo "Could not find input card:"
			echo ${new_card}
		    fi
    		done
    	    fi
    	    echo $in_cards
	    if [ "$in_cards" == "" ]; then
		echo "<<<<< No cards matching mA = ${iMA}, fit = ${iFit}. Skipping!"
		continue
	    fi

    	    ## Combine cards, output to workspace
    	    echo "combineCards.py $in_cards > ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt"
    	    combineCards.py $in_cards > ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt
    	    echo "text2workspace.py --out ${OUTDIR}/workspace_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.root"
    	    text2workspace.py ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt --for-fits --no-wrappers --optimize-simpdf-constraints=cms --X-pack-asympows --use-histsum  --out ${OUTDIR}/workspace_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.root

	    ## Set blinding options
	    runOpt="--run=both"
	    fitOpt=""
	    if [[ ${TOYSOURCE} == "Data" ]]; then
		runOpt="--run=expected"
		fitOpt="-t -1"
	    fi

    	    ## GoodnessOfFit
	    ## Only need to run GoF for one mA point, since signal strength is set to 0
	    if [[ $iMA == ${MASSES[0]} ]]; then
    	        #combine -M GoodnessOfFit -d ${OUTDIR}/workspace_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.root --algo=saturated --fixedSignalStrength 0 -n .testGoodnessOfFit.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy} --toysFrequentist -t ${NTOYGOF} -s 123456
    	        combine -M GoodnessOfFit -d ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt --algo=saturated --fixedSignalStrength 0 -n .testGoodnessOfFit.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy} --toysFrequentist -t ${NTOYGOF} -s 123456
	    fi

    	    ## AsymptoticLimits
    	    #combine -M AsymptoticLimits ${OUTDIR}/workspace_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.root ${runOpt} --cminDefaultMinimizerStrategy 0 -n .testAsymptoticLimits.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy}
    	    echo "combine -M AsymptoticLimits ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt ${runOpt} --cminDefaultMinimizerStrategy 0 -n .testAsymptoticLimits.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy}"
    	    combine -M AsymptoticLimits ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt ${runOpt} --cminDefaultMinimizerStrategy 0 -n .testAsymptoticLimits.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy}

    	    # ## FitDiagnostics
    	    # ##combine -M FitDiagnostics ${OUTDIR}/workspace_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.root ${fitOpt} --setParameters r=0 --cminDefaultMinimizerStrategy 0 --rMin -4 --rMax 4 -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy}
	    # #combine -M FitDiagnostics ${OUTDIR}/workspace_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.root ${fitOpt} --setParameters r=0 --cminDefaultMinimizerStrategy 0 --rMin -0.3 --rMax 0.3 --robustFit 1 --setRobustFitTolerance 0.02 --profilingMode all --saveShapes --saveWithUncertainties -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy}
	    # combine -M FitDiagnostics ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt ${fitOpt} --setParameters r=0 --cminDefaultMinimizerStrategy 0 --rMin -0.2 --rMax 0.2 --robustFit 1 --setRobustFitTolerance 0.02 --profilingMode all --saveShapes --saveWithUncertainties -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy}
	    # # echo "combine -M FitDiagnostics ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt ${fitOpt} --setParameters r=0 --cminDefaultMinimizerStrategy 0 --rMin -0.3 --rMax 0.3 --robustFit 1 --setRobustFitTolerance 0.02 --profilingMode all --saveShapes --saveWithUncertainties -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy}"
	    # echo "combine -M FitDiagnostics ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt --setParameterRanges r=-0.0,0.40 --robustFit 1 --stepSize 0.01 --setRobustFitTolerance 0.02 --minos all --profilingMode all -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy}"
	    # combine -M FitDiagnostics ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt --setParameterRanges r=-0.0,0.40 --robustFit 1 --stepSize 0.01 --setRobustFitTolerance 0.02 --minos all --profilingMode all -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy}
	    echo "combine -M FitDiagnostics ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt --setParameterRanges r=-0.0,0.40 --robustFit 1 --minos all -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy}"
	    combine -M FitDiagnostics ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt --setParameterRanges r=-0.0,0.40 --robustFit 1 --minos all -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy}

	    SCAN="--setParameterRanges r=-1,1 --points 1"
	    if [ "${iMA}" == "15" ]; then
		SCAN="--setParameterRanges r=-0.00025,0.10025 --points 201"
	    elif [ "${iMA}" == "30" ]; then
		SCAN="--setParameterRanges r=-0.0005,0.2005 --points 201"
	    elif [ "${iMA}" == "55" ]; then
		SCAN="--setParameterRanges r=-0.001,0.401 --points 201"
	    fi
	    
	    ## MultiDimFit
	    echo "combine -M MultiDimFit ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt --algo grid ${SCAN} --floatOtherPOIs=1 --preFitValue=0 --cminDefaultMinimizerStrategy 0 --robustFit 1 -n .testMultiDimFit.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy}"
	    combine -M MultiDimFit ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt --algo grid ${SCAN} --floatOtherPOIs=1 --preFitValue=0 --cminDefaultMinimizerStrategy 0 --robustFit 1 -n .testMultiDimFit.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy}

	    ## Move files to EOS
	    if [ "$iToy" -ge 0 ]; then
	        echo "mv *.test*.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy}*root ${EOS_OUT_DIR}"
	        mv *.test*.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy}*root ${EOS_OUT_DIR}
	    else
    	    echo "     <<<<< All done with mA = ${iMA}"
	        echo "mv *.test*.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy}*root ${OUTDIR}"
	        mv *.test*.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${sToy}*root ${OUTDIR}
	    fi

	    # Calculate elapsed time
	    ELAPSED=$((SECONDS - START_TIME))
	    hours=$((ELAPSED / 3600))
	    minutes=$(((ELAPSED % 3600) / 60))
	    seconds=$((ELAPSED % 60))
	    echo "Runtime so far: $hours hour(s), $minutes minute(s), $seconds second(s)"
	done ## End loop: for iFit in "${FITS[@]}"
    done  ## End loop: for iMA in "${MASSES[@]}"
done  ## End loop: for iCat in gg0lHi

echo "TOTAL runtime: $hours hour(s), $minutes minute(s), $seconds second(s)"
