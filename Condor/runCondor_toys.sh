#!/bin/bash

## From https://github.com/bouchamaouihichem/2DAlphabet/blob/2DToys_0518/Condor/runCondor_toys.sh

# Number of Toys
Nmin=-1
Nmax=100
## Fit transfer function
FIT="2s2C"
# Condor log directory
LOG_DIR="log"
OUT_DIR="out"
ERR_DIR="err"

# Template files
SH_TEMPLATE="2D_toy_template.sh"
SUB_TEMPLATE="2D_toy_template.sub"

# Check if both templates exist
if [[ ! -f $SH_TEMPLATE ]]; then
  echo "Error: $SH_TEMPLATE not found!"
  exit 1
fi

if [[ ! -f $SUB_TEMPLATE ]]; then
  echo "Error: $SUB_TEMPLATE not found!"
  exit 1
fi

# Emptying Condor log, out, and err directories
# echo " > Make new $LOG_DIR, $OUT_DIR, and $ERR_DIR directories .. "
# if [ -d "$LOG_DIR" ]; then
#    rm -rf "$LOG_DIR"
# fi
mkdir "$LOG_DIR"
# if [ -d "$OUT_DIR" ]; then
#    rm -rf "$OUT_DIR"
# fi
mkdir "$OUT_DIR"
# if [ -d "$ERR_DIR" ]; then
#    rm -rf "$ERR_DIR"
# fi
mkdir "$ERR_DIR"

# echo "Deleting .sub/.sh file of previous condor submission"
# rm 2D_toy_job_*.sh
# rm 2D_toy_job_*.sub

# Loop over toy jobs from Nmin up to Nmax
for ((ii=Nmin; ii<Nmax; ii++)); do
    # Loop over categories
    #for iCat in LepLo LepHi gg0lLo gg0lHi VBFjjLo VBFjjHi VjjLo VjjHi tt0l LepComb gg0lComb VBFjjComb VjjComb HadWP40Comb HadWP60Comb LepHadComb; do
    for iCat in gg0lV; do
	# Loop over Data and MC
	for iDM in Data MC; do
	    for iMA in 12; do
	    #for iMA in 15 20 25 30 35 40 45 50 55 60; do
		for SINJ in "false" "true"; do
		    SH_OUT="2D_toy_job_${iCat}_${iDM}_${ii}_${iMA}_${FIT}_${SINJ}.sh"
		    SUB_OUT="2D_toy_job_${iCat}_${iDM}_${ii}_${iMA}_${FIT}_${SINJ}.sub"

		    # Create .sh file, replacing NTOY with the index, DMC with Data or MC, and CAT with the category
		    sed "s/CAT/${iCat}/g"  "$SH_TEMPLATE" > "tmp1.sh"
		    sed "s/DMC/${iDM}/g"   "tmp1.sh" > "tmp2.sh"
		    sed "s/NTOY/${ii}/g"   "tmp2.sh" > "tmp3.sh"
		    sed "s/MASSA/${iMA}/g" "tmp3.sh" > "tmp4.sh"
		    sed "s/FIT/${FIT}/g"   "tmp4.sh" > "tmp5.sh"
		    sed "s/SINJ/${SINJ}/g" "tmp5.sh" > "$SH_OUT"
		    chmod +x "$SH_OUT"

		    # Create .sub file, replacing reference to original .sh with the modified .sh name
		    sed "s/2D_toy_template.sh/${SH_OUT}/g" "$SUB_TEMPLATE" > "$SUB_OUT"

		    #echo "Created $SH_OUT and $SUB_OUT"
  
		    #echo "Submitting jobs for Cat ${iCat} ${iDM} Toy ${ii}"
		    condor_submit 2D_toy_job_${iCat}_${iDM}_${ii}_${iMA}_${FIT}_${SINJ}.sub
		done
	    done
	done
    done
done
