#!/bin/bash

export mass_points=(15 30 55)
#export mass_points=(30)
for i in "${mass_points[@]}"
do
for it in $(seq 0 1 200)
do
    export Leptonic_cards="$( ls mctoysjson/*toy${it}/mA_${i}_area/card*txt | sed 's/ / /g' | tr '\n' ' ' | sed 's/ $//' )"
    #export lpetonic_par="XXHiBackground_rpfL_1d1C_par0=0.03648462421250542,XXHiBackground_rpfL_1d1C_par1=-1.5307179756478035,XXHiBackground_rpfL_1d1C_par2=-1.1784577696146243,XXLoBackground_rpfL_1x1C_par0=0.029909966999568383,XXLoBackground_rpfL_1x1C_par1=-2.324602453784678,XXLoBackground_rpfL_1x1C_par2=-1.5337877370469641,XXLoBackground_rpfL_1x1C_par3=-2.456561396995653"
    #export ggH_cards="$( ls ggH/mA_${i}_area/card*txt | sed 's/ / /g' | tr '\n' ' ' | sed 's/ $//' )"
    #export ggH_par="Background_gg0lIncl_rpfL_2d2C_par0=0.06872869914214164,Background_gg0lIncl_rpfL_2d2C_par1=-0.7936949284044204,Background_gg0lIncl_rpfL_2d2C_par2=-0.3412259464945464,Background_gg0lIncl_rpfL_2d2C_par3=-1.6586733958293962,Background_gg0lIncl_rpfL_2d2C_par4=-0.7175766645661952"
    #export VBF_cards="$( ls VBF/fits_VBFjj*A_15to55_WP40_2018/mA_${i}_area/card*.txt | sed 's/ / /g' | tr '\n' ' ' | sed 's/ $//' )"
    #export VBF_par="Background_VBFjjHi_rpfL_2d2C_par0=0.0666451134464694,Background_VBFjjHi_rpfL_2d2C_par1=-0.8027698477344529,Background_VBFjjHi_rpfL_2d2C_par2=-0.35751309893623784,Background_VBFjjHi_rpfL_2d2C_par3=-1.4520435295622747,Background_VBFjjHi_rpfL_2d2C_par4=-1.5873488110214566,Background_VBFjjLo_rpfL_2d2C_par0=0.058783598236516355,Background_VBFjjLo_rpfL_2d2C_par1=-0.8044428687736627,Background_VBFjjLo_rpfL_2d2C_par2=-0.6671966898780965,Background_VBFjjLo_rpfL_2d2C_par3=-0.8123544649013184,Background_VBFjjLo_rpfL_2d2C_par4=0.04976840519145753"
    #echo "====> combineCards.py $Leptonic_cards $ggH_cards $VBF_cards > combined_ma_${i}_all.txt"
    #combineCards.py $Leptonic_cards $ggH_cards $VBF_cards > combined_ma_${i}_all.txt
    #echo "====> combineCards.py $Leptonic_cards > combined_ma_${i}_leptonic.txt"
    combineCards.py $Leptonic_cards > combined_ma_${i}_leptonic_toy${it}.txt
    #echo "====> combineCards.py $VBF_cards > combined_ma_${i}_vbf.txt"
    #combineCards.py $VBF_cards > combined_ma_${i}_vbf.txt
    #echo "====> combineCards.py $ggH_cards > combined_ma_${i}_ggh.txt"
    #combineCards.py $ggH_cards > combined_ma_${i}_ggh.txt
    # text2workspace.py
    text2workspace.py combined_ma_${i}_leptonic_toy${it}.txt --for-fits --no-wrappers --optimize-simpdf-constraints=cms --X-pack-asympows --use-histsum  --out workspace_ma_${i}_leptonic_toy${it}.root
    #text2workspace.py combined_ma_${i}_vbf.txt --for-fits --no-wrappers --optimize-simpdf-constraints=cms --X-pack-asympows --use-histsum  --out workspace_ma_${i}_vbf.root
    #text2workspace.py combined_ma_${i}_ggh.txt --for-fits --no-wrappers --optimize-simpdf-constraints=cms --X-pack-asympows --use-histsum  --out workspace_ma_${i}_ggh.root
    #text2workspace.py combined_ma_${i}_all.txt --for-fits --no-wrappers --optimize-simpdf-constraints=cms --X-pack-asympows --use-histsum  --out workspace_ma_${i}_all.root
    # AsymptoticLimits
    combine -M AsymptoticLimits workspace_ma_${i}_leptonic_toy${it}.root --cminDefaultMinimizerStrategy 0 -n .testAsymptoticLimits.ma_${i}.leptonic.toy${it}
    combine -M FitDiagnostics workspace_ma_${i}_leptonic_toy${it}.root --setParameters r=1 --cminDefaultMinimizerStrategy 0 --rMin -20 --rMax 20 -n .testFitDiagnostics.ma_${i}.leptonic.toy${it}
    #combine -M AsymptoticLimits workspace_ma_${i}_vbf.root --cminDefaultMinimizerStrategy 0 --setParameters ${VBF_par} --run=blind -n .testAsymptoticLimits.ma_${i}.vbf
    #combine -M AsymptoticLimits workspace_ma_${i}_ggh.root --cminDefaultMinimizerStrategy 0 --setParameters ${ggH_par} --run=blind -n .testAsymptoticLimits.ma_${i}.ggh
    #combine -M AsymptoticLimits workspace_ma_${i}_all.root --cminDefaultMinimizerStrategy 0 --setParameters ${lpetonic_par},${ggH_par},${VBF_par} --run=blind -n .testAsymptoticLimits.ma_${i}.all
done
done 

