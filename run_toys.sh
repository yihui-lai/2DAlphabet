## Run single-toy jobs
## Can run up to 10 or so on a single lxplus node, on a few
## nodes at the same time, without the admins getting mad :)
## Would be good to set this up to run on condor / batch

TOYMIN=-1
TOYMAX=-1
FIT="1x1C"
source config/user.config  ## Loads USER, LOC_DIR, and EOS_DIR

echo "Just to be sure, you want to output to:"
echo ${EOS_DIR}

## Run run_toy.sh for all categories
#for iCat in LepLo LepHi LepIncl LepComb gg0lLo gg0lHi gg0lIncl gg0lComb VBFjjLo VBFjjHi VBFjjIncl VBFjjComb VjjLo VjjHi VjjIncl VjjComb tt0l HadWP40Comb HadWP60Comb LepHadComb; do
#for iCat in LepLoA LepHiA LepCombA LepLoB LepHiB LepCombB LepLoC LepHiC LepCombC LepLoD LepHiD LepCombD LepLoE LepHiE LepCombE LepLoF LepHiF LepCombF LepLoG LepHiG LepCombG LepLoH LepHiH LepCombH; do
#for iCat in LepLo LepHi gg0lLo gg0lHi VBFjjLo VBFjjHi VjjLo VjjHi tt0l; do
#for iCat in gg0lLo gg0lHi gg0lIncl gg0lComb gg0lInclV VBFjjLo VBFjjHi VBFjjIncl VBFjjComb VjjLo VjjHi VjjIncl VjjComb tt0l; do
for iToy in $(seq ${TOYMIN} ${TOYMAX}); do
    for iMA in 12 15 20 25 30 35 40 45 50 55 60; do
	for iDMC in MC; do
	    for iCat in LepHiT; do
		for SINJ in "false" "true"; do
	    	    echo "./run_toy.sh ${iToy} ${iDMC} ${iCat} ${iMA} ${FIT} ${SINJ}"
	    	./run_toy.sh ${iToy} ${iDMC} ${iCat} ${iMA} ${FIT} ${SINJ}
	    done
	done
    done
done
