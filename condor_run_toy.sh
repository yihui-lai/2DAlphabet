## Run limits, bias, and goodness-of-fit for a single toy

iToy=$1            ## Toy index
TOYSOURCE=$2       ## Data or MC
xCat=$3            ## Category to run
MASSES=(12 20 35 50 60)  ## Needs to match hard-coded settings in htoaato4b_mctoy.py
NTOYGOF=100        ## Number of toys 2DAlphabet will run for goodness-of-fit test
YEAR="2018"
DATE="2025_06_03"
MHREG="pnet"
MAREG="34a"
#FITS=("0x0" "0x0smr" "1d1C" "1x1C")  ## Needs to be a subset of FITLIST in htoaato4b_mctoy.py
#FITS=("0x0" "1x1C")  ## Needs to be a subset of FITLIST in htoaato4b_mctoy.py
FITS=("1d1C")
SIGINJ=""  ## Empty string for no signal injection
#SIGINJ="_mA_15_sigBr_005"  ## "_mA_XX_sigBr_YYY" (include leading "_")

## Output EOS directory to move ROOT files (avoid disk quota issues)
EOS_OUT_DIR="/eos/cms/store/user/abrinke1/HiggsToAA/2DAlphabet/ToyStudies/${YEAR}/${DATE}/"
echo "Just to be sure, you want to output to:"
echo ${EOS_OUT_DIR}
if [ ! -d ${EOS_OUT_DIR} ]; then
    mkdir -p ${EOS_OUT_DIR}
fi

sToy="toy${iToy}"
## Toy "-1" corresponds to MCrounded or Datarounded, "-2" corresponds to Data
if [ "${iToy}" == "-1" ]; then
    sToy="MCrounded"
    if [[ ${TOYSOURCE} == "Data" ]]; then
	sToy="Datarounded"
    fi
fi
if [[ "${iToy}" == "-2" && ${TOYSOURCE} == "Data" ]]; then
    sToy="Data"
fi
dmToy="${TOYSOURCE}${sToy}"

INDIR="output/MCtoys"
OUTDIR="output/Mergecards/MC${sToy}"
if [[ ${TOYSOURCE} == "Data" ]]; then
    INDIR="output/Datatoys"
    OUTDIR="${INDIR}/Mergecards/Data${sToy}"
fi
if [ ! -d ${OUTDIR} ]; then
    mkdir -p ${OUTDIR}
fi

# Start the timer
START_TIME=$SECONDS


## WARNING!!! You have to run *all* the "sub-categories" before running the "Comb" categories
for iCat in $xCat; do

    ## Define WP for each category type
    WP="UNDEF"
    if [[ $iCat == "gg0l"* || $iCat == "VBF"* || $iCat == "HadWP40"* ]]; then
	WP="WP40"
    fi
    if [[ $iCat == "Lep"* || $iCat == "Vjj"* || $iCat == "tt0l"* || $iCat == "HadWP60"* ]]; then
	if [[ $iCat != "LepHadComb" ]]; then
	    WP="WP60"
	fi
    fi

    ## Define component sub-categories for each super-category
    subCats=(${iCat})
    subCatsLep=()
    subCatsHadWP40=()
    subCatsHadWP60=()
    if [[ ${iCat:0:7} == "LepComb" ]]; then
	subCats=(LepHi${iCat:7:7} LepLo${iCat:7:7})
    fi
    if [[ $iCat == "gg0lComb" ]]; then
	subCats=(gg0lHi gg0lLo)
    fi
    if [[ $iCat == "VBFjjComb" ]]; then
	subCats=(VBFjjHi VBFjjLo)
    fi
    if [[ $iCat == "VjjComb" ]]; then
	subCats=(VjjHi VjjLo)
    fi
    if [[ $iCat == "HadWP40Comb" ]]; then
	subCats=(gg0lHi gg0lLo VBFjjHi VBFjjLo)
    fi
    if [[ $iCat == "HadWP60Comb" ]]; then
	subCats=(VjjHi VjjLo tt0l)
    fi
    if [[ $iCat == "LepHadComb" ]]; then
	subCatsHadWP40=(gg0lHi gg0lLo VBFjjHi VBFjjLo)
	subCatsHadWP60=(VjjHi VjjLo tt0l)
	subCatsLep=(LepHi LepLo)
    fi

    ## Make toys for each category
    if [[ $iCat != *"Comb"* ]]; then
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
    		new_card="${INDIR}/fits_${jCat}_Htoaato4b_${MHREG}_${MAREG}_${WP}_${iFit}_${YEAR}_${sToy}${SIGINJ}/mA_${iMA}_area/card.txt"
		if test -f ${new_card}; then
    		    in_cards="${in_cards} ${new_card}"
		else
		    echo "Could not find input card:"
		    echo ${new_card}
		fi
    	    done
    	    if [[ $iCat == "LepHadComb" ]]; then
    		in_cards=""
    		for lCat in "${subCatsLep[@]}"; do
    		    new_card="${in_cards} ${INDIR}/fits_${lCat}_Htoaato4b_${MHREG}_${MAREG}_WP60_${iFit}_${YEAR}_${sToy}/mA_${iMA}_area/card.txt"
		    if test -f ${new_card}; then
    			in_cards="${in_cards} ${new_card}"
		    else
			echo "Could not find input card:"
			echo ${new_card}
		    fi
    		done
    		for hCat40 in "${subCatsHadWP40[@]}"; do
    		    new_card="${INDIR}/fits_${hCat40}_Htoaato4b_${MHREG}_${MAREG}_WP40_${iFit}_${YEAR}_${sToy}/mA_${iMA}_area/card.txt"
		    if test -f ${new_card}; then
    			in_cards="${in_cards} ${new_card}"
		    else
			echo "Could not find input card:"
			echo ${new_card}
		    fi
    		done
    		for hCat60 in "${subCatsHadWP60[@]}"; do
    		    new_card="${INDIR}/fits_${hCat60}_Htoaato4b_${MHREG}_${MAREG}_WP60_${iFit}_${YEAR}_${sToy}/mA_${iMA}_area/card.txt"
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
    	        #combine -M GoodnessOfFit -d ${OUTDIR}/workspace_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.root --algo=saturated --fixedSignalStrength 0 -n .testGoodnessOfFit.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy} --toysFrequentist -t ${NTOYGOF} -s 123456
    	        echo "combine -M GoodnessOfFit -d ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt --algo=saturated --fixedSignalStrength 0 -n .testGoodnessOfFit.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy} --toysFrequentist -t ${NTOYGOF} -s 123456"
    	        combine -M GoodnessOfFit -d ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt --algo=saturated --fixedSignalStrength 0 -n .testGoodnessOfFit.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy} --toysFrequentist -t ${NTOYGOF} -s 123456
	    fi

    	    ## AsymptoticLimits
    	    #combine -M AsymptoticLimits ${OUTDIR}/workspace_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.root ${runOpt} --cminDefaultMinimizerStrategy 0 -n .testAsymptoticLimits.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy}
    	    echo "combine -M AsymptoticLimits ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt ${runOpt} --cminDefaultMinimizerStrategy 2 --cminDefaultMinimizerTolerance=0.0001 -n .testAsymptoticLimits.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy}"
    	    combine -M AsymptoticLimits ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt ${runOpt} --cminDefaultMinimizerStrategy 2 --cminDefaultMinimizerTolerance=0.0001 -n .testAsymptoticLimits.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy}

    	    # # ## FitDiagnostics
    	    # # ##combine -M FitDiagnostics ${OUTDIR}/workspace_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.root ${fitOpt} --setParameters r=0 --cminDefaultMinimizerStrategy 0 --rMin -4 --rMax 4 -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy}
	    # # #combine -M FitDiagnostics ${OUTDIR}/workspace_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.root ${fitOpt} --setParameters r=0 --cminDefaultMinimizerStrategy 0 --rMin -0.3 --rMax 0.3 --robustFit 1 --setRobustFitTolerance 0.02 --profilingMode all --saveShapes --saveWithUncertainties -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy}
	    # # combine -M FitDiagnostics ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt ${fitOpt} --setParameters r=0 --cminDefaultMinimizerStrategy 0 --rMin -0.2 --rMax 0.2 --robustFit 1 --setRobustFitTolerance 0.02 --profilingMode all --saveShapes --saveWithUncertainties -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy}
	    # # # echo "combine -M FitDiagnostics ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt ${fitOpt} --setParameters r=0 --cminDefaultMinimizerStrategy 0 --rMin -0.3 --rMax 0.3 --robustFit 1 --setRobustFitTolerance 0.02 --profilingMode all --saveShapes --saveWithUncertainties -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy}"
	    # # echo "combine -M FitDiagnostics ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt --setParameterRanges r=-0.0,0.40 --robustFit 1 --stepSize 0.01 --setRobustFitTolerance 0.02 --minos all --profilingMode all -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy}"
	    # # combine -M FitDiagnostics ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt --setParameterRanges r=-0.0,0.40 --robustFit 1 --stepSize 0.01 --setRobustFitTolerance 0.02 --minos all --profilingMode all -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy}
	    # echo "combine -M FitDiagnostics ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt --setParameterRanges r=-0.0,0.40 --robustFit 1 --minos all -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy}"
	    # combine -M FitDiagnostics ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt --setParameterRanges r=-0.0,0.40 --robustFit 1 --minos all -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy}

	    SCAN="--setParameterRanges r=-1,1 --points 1"
	    if [[ $iMA == "12" || $iMA == "15" || $iMA == "20" ]]; then
	    	SCAN="--setParameterRanges r=-0.00025,0.10025 --points 201"
	    elif [[ $iMA == "25" || $iMA == "30" || $iMA == "35" || $iMA == "40" ]]; then
	    	SCAN="--setParameterRanges r=-0.0005,0.2005 --points 201"
	    elif [[ $iMA == "45" || $iMA == "50" || $iMA == "55" || $iMA == "60" ]]; then
	    	SCAN="--setParameterRanges r=-0.001,0.401 --points 201"
	    fi
	    
	    ## MultiDimFit
	    echo "combine -M MultiDimFit ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt --algo grid ${SCAN} --floatOtherPOIs=1 --preFitValue=0 --cminDefaultMinimizerStrategy 0 --robustFit 1 -n .testMultiDimFit.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy}"
	    combine -M MultiDimFit ${OUTDIR}/combined_${iCat}_mA_${iMA}_${iFit}${SIGINJ}_${YEAR}.txt --algo grid ${SCAN} --floatOtherPOIs=1 --preFitValue=0 --cminDefaultMinimizerStrategy 0 --robustFit 1 -n .testMultiDimFit.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy}

	    ## Move files to EOS
	    if [ "$iToy" -ge 0 ]; then
	        echo "mv *.test*.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy}*root ${EOS_OUT_DIR}"
	        mv *.test*.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy}*root ${EOS_OUT_DIR}
	    else
    	    echo "     <<<<< All done with mA = ${iMA}"
	        echo "mv *.test*.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy}*root ${OUTDIR}"
	        mv *.test*.${iCat}.mA_${iMA}.${iFit}${SIGINJ}.${dmToy}*root ${OUTDIR}
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
