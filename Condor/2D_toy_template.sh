#!/bin/bash

## From https://github.com/bouchamaouihichem/2DAlphabet/blob/2DToys_0518/Condor/2D_toys.sh

cd /afs/cern.ch/work/a/abrinke1/public/HiggsToAA/2DAlphabet/CMSSW_11_3_4/src/
cmsenv
source twoD-env/bin/activate
cd 2DAlphabet
bash condor_run_toy.sh NTOY DMC CAT
