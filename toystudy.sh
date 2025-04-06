# step 1, run Haa4b_makeMCtoy.py to make toys
python3 Haa4b_makeMCtoy.py

# step 2, run htoaato4b.py to make datacards
for i in $(seq 0 1 200) # 200 toys
do 
echo $i
python3 htoaato4b_mctoy.py $i
mv fits_XXLo_Htoaato4b_mH_pnet_mA_15to55_WP60_2018 mctoysjson/fits_XXLo_Htoaato4b_mH_pnet_mA_15to55_WP60_2018_toy$i
# modify htoaato4b_mctoy.py and run this loop again for XXHi
#mv fits_XXHi_Htoaato4b_mH_pnet_mA_15to55_WP60_2018 mctoysjson/fits_XXHi_Htoaato4b_mH_pnet_mA_15to55_WP60_2018_toy$i
done

# step3, run Mergecards.sh to combine cards 
source Mergecards.sh

# step4, make summary plots
python3 Haa4b_limitsummary.py
python3 Haa4b_fitsummary.py


