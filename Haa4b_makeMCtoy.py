import ROOT
import os
import numpy as np

ROOT.gROOT.SetBatch(True)

base_pth=None
category = "VBF_Hi"
#category = "VBF_Lo"
#category = "gg0lIncl"
#category = "Leptonic_Hi"
#category = "Leptonic_Lo"

if category == "Leptonic_Hi" or category == "Leptonic_Lo" or category == "gg0lIncl":
    base_pth="./raw_inputs/"
elif category == "VBF_Hi" or category == "VBF_Lo":
    base_pth="./plots/"

if category == "VBF_Hi":
    output_hist_name = "plots/2DAlphabetfiles_VBF_inputs/VBFHi_Xto4bv2"
    input_ws = ROOT.TFile.Open("raw_inputs/taggerv2_wp40Andwp60/fits_VBFjjHi_Xto4bv2_Htoaato4b_mH_pnet_mA_15to55_WP40_2018/base.root")
    rafile_XXHi=[
        'plots/2DAlphabetfiles_VBF_inputs/VBFHi_Xto4bv2/VBFjjHi_Xto4bv2_MC_2018.root:VBFjjHi_Xto4bv2_Data_2018_pnet_WP40_Pass_Nom:VBFjjHi_Xto4bv2_Data_2018_pnet_WP40_Fail_Nom',
    ]
    rafile = rafile_XXHi
    outprocess = "VBFjjHi_Xto4bv2_BKGsmooth1_2018_pnet_WP40_"
elif category == "VBF_Lo":
    output_hist_name = "plots/2DAlphabetfiles_VBF_inputs/VBFLo_Xto4bv2"
    input_ws = ROOT.TFile.Open("raw_inputs/taggerv2_wp40Andwp60/fits_VBFjjLo_Xto4bv2_Htoaato4b_mH_pnet_mA_15to55_WP40_2018/base.root")
    rafile_XXLo=[
        'plots/2DAlphabetfiles_VBF_inputs/VBFLo_Xto4bv2/VBFjjLo_Xto4bv2_MC_2018.root:VBFjjLo_Xto4bv2_Data_2018_pnet_WP40_Pass_Nom:VBFjjLo_Xto4bv2_Data_2018_pnet_WP40_Fail_Nom',
    ]
    rafile = rafile_XXLo
    outprocess = "VBFjjLo_Xto4bv2_BKGsmooth1_2018_pnet_WP40_"
elif category == "gg0lIncl":
    output_hist_name = "plots/HtoAA_2DAlphabet_merge_inputs_gg0lIncl/2025_04_04_mAa/"
    input_ws = ROOT.TFile.Open("raw_inputs/20250403_Pseudodata/fits_gg0lIncl_Htoaato4b_mH_pnet_vs_massA34a_mA_15to55_WP40_2018/base.root")
    rafile_bkg=[
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_QCD_BGen_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_QCD_Incl_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_QCD_bEnr_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_ST_s_0l_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_ST_s_1l_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_STbar_tW_12l_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_STbar_tW_Incl_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_STbar_t_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_STop_tW_12l_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_STop_tW_Incl_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_STop_t_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_TT0l_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_TT1l_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_TT2l_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_WWW_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_WWZ_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_WW_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_WZZ_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_WZ_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_Wlv_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_Wqq_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_ZZZ_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_ZZ_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_Zll_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_Zqq_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_Zvv_2018.root',
        base_pth+'/20250403_Pseudodata/2DAlphabet_inputFiles_pseudodata_0/gg0lIncl/gg0lIncl_ggH_2018.root',
    ]
    rafile = rafile_bkg
    outprocess = "gg0lIncl_BKGsmooth1_2018_pnet_vs_massA34a_WP40_"
elif category == "Leptonic_Hi":
    output_hist_name = "plots/HtoAA_2DAlphabet_merge_inputs_XXHi/2025_04_04_mAa"
    input_ws = ROOT.TFile.Open(base_pth+"/Leptonic_2D_Limits_040125/fits_XXHi_Htoaato4b_mH_pnet_mA_15to55_WP60_2018/base.root")
    rafile_XXHi=[
        base_pth+'2D_1L_030625_mAa/WP60/WlvHi_Data_2018.root',
        base_pth+'2D_1L_030625_mAa/WP60/ttbblv_Data_2018.root',
        base_pth+'2D_2LZ_030625_mAa/WP60/Zll_Data_2018.root',
        base_pth+'2D_2Ltt_030625_mAa/WP60/ttbll_Data_2018.root',
    ]
    rafile_XXHi_bkg=[
        base_pth+'2D_1L_030625_mAa/WP60/WlvHi_TT1l_2018.root',
        base_pth+'2D_1L_030625_mAa/WP60/WlvHi_Wlv_2018.root',
        base_pth+'2D_1L_030625_mAa/WP60/ttbblv_TT1l_2018.root',
        base_pth+'2D_1L_030625_mAa/WP60/ttbblv_Wlv_2018.root',
        base_pth+'2D_2LZ_030625_mAa/WP60/Zll_TT2l_2018.root',
        base_pth+'2D_2LZ_030625_mAa/WP60/Zll_ZZ_2018.root',
        base_pth+'2D_2LZ_030625_mAa/WP60/Zll_Zll_2018.root',
        base_pth+'2D_2Ltt_030625_mAa/WP60/ttbll_TT2l_2018.root',
    ]
    rafile = rafile_XXHi_bkg
    outprocess = "XXHi_BKGsmooth1_2018_pnet_WP60_"
elif category == "Leptonic_Lo":
    output_hist_name = "plots/HtoAA_2DAlphabet_merge_inputs_XXLo/2025_04_04_mAa"
    input_ws = ROOT.TFile.Open(base_pth+"/Leptonic_2D_Limits_040125/fits_XXLo_Htoaato4b_mH_pnet_mA_15to55_WP60_2018/base.root")
    rafile_XXLo=[
      base_pth+'2D_1L_030625_mAa/WP60/WlvLo_Data_2018.root',
      base_pth+'2D_1L_030625_mAa/WP60/ttblv_Data_2018.root',
    ]
    rafile_XXLo_bkg=[
      base_pth+'2D_1L_030625_mAa/WP60/WlvLo_TT1l_2018.root',
      base_pth+'2D_1L_030625_mAa/WP60/WlvLo_Wlv_2018.root',
      base_pth+'2D_1L_030625_mAa/WP60/ttblv_TT1l_2018.root',
      base_pth+'2D_1L_030625_mAa/WP60/ttblv_Wlv_2018.root',
    ]
    rafile = rafile_XXLo_bkg
    outprocess = "XXLo_BKGsmooth1_2018_pnet_WP60_"

os.system("mkdir -p plots/")

def compare_2D_histograms(data_obs1, data_obs2, mH_default, mA_default, name):
    # Create a RooArgList containing both mH and mA variables
    var_list = ROOT.RooArgList(mH_default, mA_default)

    # Initialize histograms
    nbins_mH = mH_default.getBins()
    nbins_mA = mA_default.getBins()

    hist_data_obs1 = ROOT.TH2F("hist_data_obs1", "Data Distribution (data_obs1)", nbins_mH, mH_default.getMin(), mH_default.getMax(), nbins_mA, mA_default.getMin(), mA_default.getMax())
    hist_data_obs2 = ROOT.TH2F("hist_data_obs2", "MC Distribution (data_obs2)", nbins_mH, mH_default.getMin(), mH_default.getMax(), nbins_mA, mA_default.getMin(), mA_default.getMax())

    # Loop through data_obs1 and data_obs2 to fill the histograms
    Total_events_data = 0
    Total_events_MC = 0

    for i in range(data_obs1.numEntries()):
        var_set = data_obs1.get(i)
        weight = data_obs1.weight()
        mH_val = var_set.getRealValue(f"mH_{MHRegion}_default")  # Extract mH value
        mA_val = var_set.getRealValue("mA_default")  # Extract mA value
        binx = hist_data_obs1.GetXaxis().FindBin(mH_val)
        biny = hist_data_obs1.GetYaxis().FindBin(mA_val)
        hist_data_obs1.Fill(mH_val, mA_val, weight)  # Fill data_obs1 histogram with weight
        Total_events_data += weight

    for i in range(data_obs2.numEntries()):
        var_set = data_obs2.get(i)
        weight = data_obs2.weight()
        mH_val = var_set.getRealValue(f"mH_{MHRegion}_default")  # Extract mH value
        mA_val = var_set.getRealValue("mA_default")  # Extract mA value
        binx = hist_data_obs2.GetXaxis().FindBin(mH_val)
        biny = hist_data_obs2.GetYaxis().FindBin(mA_val)
        hist_data_obs2.Fill(mH_val, mA_val, weight)  # Fill data_obs2 histogram with weight
        Total_events_MC += weight

    print(f"Total events in data_obs1: {Total_events_data}")
    print(f"Total events in data_obs2: {Total_events_MC}")

    # Create a canvas to display the plots
    canvas = ROOT.TCanvas("c1", "Comparison of Data and MC", 800, 600)

    # Plot 1: data_obs1 distribution (2D)
    canvas.Clear()
    hist_data_obs1.SetTitle("Data Distribution (data_obs1)")
    hist_data_obs1.GetXaxis().SetTitle("mH")
    hist_data_obs1.GetYaxis().SetTitle("mA")
    hist_data_obs1.Draw("surf1")  # "surf1" for 2D color plot
    canvas.SaveAs(f"plots/{name}_data_obs1_2D_distribution.png")
    canvas.SaveAs(f"plots/{name}_data_obs1_2D_distribution.C")

    # Plot 2: data_obs2 distribution (2D)
    canvas.Clear()
    for ismooth in range(1):
        hist_ratio = hist_data_obs2.Clone("hist_ratio")
        if ismooth!=0:
            hist_ratio.Smooth(ismooth)
        hist_ratio.SetTitle("MC Distribution (data_obs2)")
        hist_ratio.GetXaxis().SetTitle("mH")
        hist_ratio.GetYaxis().SetTitle("mA")
        hist_ratio.Draw("surf1")  # "surf1" for 2D color plot
        canvas.SaveAs(f"plots/{name}_data_obs2_2D_distribution_smooth{ismooth}.png")
        canvas.SaveAs(f"plots/{name}_data_obs2_2D_distribution_smooth{ismooth}.C")

    # Plot 3: Ratio plot (data_obs1 / data_obs2) for each bin in 2D
    canvas.Clear()
    for ismooth in range(1):
        hist_ratio = hist_data_obs2.Clone("hist_ratio")
        if ismooth!=0:
            hist_ratio.Smooth(ismooth)
        hist_ratio.Divide(hist_data_obs1)
        hist_ratio.SetTitle("Data/MC Ratio (data_obs1/data_obs2)")
        hist_ratio.GetXaxis().SetTitle("mH")
        hist_ratio.GetYaxis().SetTitle("mA")
        hist_ratio.Draw("surf1")  # "surf1" for 2D color plot
        canvas.SaveAs(f"plots/{name}_data_obs1_vs_data_obs2_ratio_2D_smooth{ismooth}.png")
        canvas.SaveAs(f"plots/{name}_data_obs1_vs_data_obs2_ratio_2D_smooth{ismooth}.C")


# step 1, merge bkg MC
BKGMCTotal_pass = None  # Use None instead of an empty string
BKGMCTotal_fail = None
file_raw_list={}
for raf in rafile:
    print(f"add {raf}")
    pass_name = None
    fail_name = None
    name = None
    filepath = None
    if ":" in raf:
        pass_name = raf.split(":")[1]
        fail_name = raf.split(":")[2]
        filepath = raf.split(":")[0]
        name = raf.split("/")[-1].split(":")[0].replace(".root", "")
    else:
        name = raf.split("/")[-1].replace(".root", "")
        pass_name = f"{name}_pnet_WP60_Pass_Nom"
        fail_name = f"{name}_pnet_WP60_Fail_Nom"
        filepath = raf
        if category == "gg0lIncl":
            pass_name = f"{name}_pnet_vs_massA34d_WP40_Pass_Nom"
            fail_name = f"{name}_pnet_vs_massA34d_WP40_Fail_Nom"
    file_raw_list[raf] = ROOT.TFile.Open(filepath)
    hist2_pass = file_raw_list[raf].Get(pass_name)
    hist2_fail = file_raw_list[raf].Get(fail_name)
    if hist2_pass and hist2_fail:  # Ensure histograms exist
        if BKGMCTotal_pass is None:  # Correct initialization check
            BKGMCTotal_pass = hist2_pass.Clone(f"{outprocess}Pass_Nom")
            BKGMCTotal_fail = hist2_fail.Clone(f"{outprocess}Fail_Nom")
        else:
            BKGMCTotal_pass.Add(hist2_pass)  # No need to Clone again
            BKGMCTotal_fail.Add(hist2_fail)
    else:
        print(f"Warning: Histogram not found in file {raf}")
BKGMCTotal_pass_Smooth1 = None
BKGMCTotal_fail_Smooth1 = None
if BKGMCTotal_pass!=None and BKGMCTotal_fail!=None:
    BKGMCTotal_pass_Smooth1=BKGMCTotal_pass.Clone(f"{outprocess}Pass_Nom")
    BKGMCTotal_fail_Smooth1=BKGMCTotal_fail.Clone(f"{outprocess}Fail_Nom")
    BKGMCTotal_pass_Smooth1.Smooth(1)
    BKGMCTotal_fail_Smooth1.Smooth(1)
for i in range(1, BKGMCTotal_pass_Smooth1.GetNbinsX() + 1):
    for j in range(1, BKGMCTotal_pass_Smooth1.GetNbinsY() + 1):
        if BKGMCTotal_pass_Smooth1.GetBinContent(i,j)<0:
            if(abs(BKGMCTotal_pass_Smooth1.GetBinError(i,j))/abs(BKGMCTotal_pass_Smooth1.GetBinContent(i,j))>0.5):
                BKGMCTotal_pass_Smooth1.SetBinContent(i,j, 0)
            else:
                print(BKGMCTotal_pass_Smooth1.GetBinContent(i,j), BKGMCTotal_pass_Smooth1.GetBinError(i,j))
                exit()
        if BKGMCTotal_fail_Smooth1.GetBinContent(i,j)<0:
            if(abs(BKGMCTotal_fail_Smooth1.GetBinError(i,j))/abs(BKGMCTotal_fail_Smooth1.GetBinContent(i,j))>0.5):
                BKGMCTotal_fail_Smooth1.SetBinContent(i,j, 0)
            else:
                print(BKGMCTotal_fail_Smooth1.GetBinContent(i,j), BKGMCTotal_fail_Smooth1.GetBinError(i,j))
                exit()
        BKGMCTotal_pass_Smooth1.SetBinError(i, j, np.sqrt(BKGMCTotal_pass_Smooth1.GetBinContent(i,j)))
        BKGMCTotal_fail_Smooth1.SetBinError(i, j, np.sqrt(BKGMCTotal_fail_Smooth1.GetBinContent(i,j)))


# take dataHIST from workspace
w1 = input_ws.Get("w")
Nevt_allregions={}
for IsPass in ["Pass", "Fail"]:
    Nevt_allregions[IsPass]=0
    for MHRegion in ["LOW", "SIG", "HIGH"]:
        print(f"----> {IsPass}_{MHRegion}")
        data_obs1 = w1.data(f"data_obs_{IsPass}_{MHRegion}")
        #print("Data Events: ", data_obs1.numEntries())
        mH_default = w1.var(f"mH_{MHRegion}_default")
        mA_default = w1.var("mA_default")
        Total_events1=0
        for i in range(data_obs1.numEntries()):
            var_set = data_obs1.get(i)
            weight = data_obs1.weight()
            mH_val = var_set.getRealValue(f"mH_{MHRegion}_default")  # Extract mH value
            mA_val = var_set.getRealValue("mA_default")  # Extract mA value
            Total_events1 += weight
            #print( f"Bin {i}, (mH = {mH_val}, mA = {mA_val}): {weight}")
        Nevt_allregions[IsPass]+=Total_events1
        #print("total: ", Total_events1)
        nbins_mH = mH_default.getBins()  # Default number of bins in mH
        nbins_mA = mA_default.getBins()  # Default number of bins in mA
        low_mH = mH_default.getMin()
        high_mH = mH_default.getMax()
        low_mA = mA_default.getMin()
        high_mA = mA_default.getMax()
        hist_rebinned = ROOT.TH2F("hist_rebinned", "Rebinned Histogram",
                                  nbins_mH, low_mH, high_mH,
                                  nbins_mA, low_mA, high_mA)
        
        BKGMCTotal_tofill = BKGMCTotal_pass_Smooth1
        if IsPass=="Fail":
            BKGMCTotal_tofill = BKGMCTotal_fail_Smooth1
        for i in range(1, BKGMCTotal_tofill.GetNbinsX() + 1):
            for j in range(1, BKGMCTotal_tofill.GetNbinsY() + 1):
                x_center = BKGMCTotal_tofill.GetXaxis().GetBinCenter(i)
                y_center = BKGMCTotal_tofill.GetYaxis().GetBinCenter(j)
                content = BKGMCTotal_tofill.GetBinContent(i, j)
                # Find the new bin index and fill the rebinned histogram
                binx = hist_rebinned.GetXaxis().FindBin(x_center)
                biny = hist_rebinned.GetYaxis().FindBin(y_center)
                content_org = hist_rebinned.GetBinContent(binx, biny)
                #print(x_center, y_center, binx, biny)
                hist_rebinned.SetBinContent(binx, biny, content + content_org)
                hist_rebinned.SetBinError(binx, biny, np.sqrt(content + content_org))
        #hist_rebinned.Scale(Total_events1*1.0/hist_rebinned.Integral())
        print("Remake data_obs")
        data_obs2 = ROOT.RooDataHist(f"data_obs_mc_{IsPass}_{MHRegion}", "Binned dataset from histogram",
                                     ROOT.RooArgList(mH_default, mA_default),
                                     hist_rebinned)
        w1.Import(data_obs2)  # Import data_obs2 into the workspace w1
        Total_events2=0
        for i in range(data_obs2.numEntries()):
            var_set = data_obs2.get(i)
            weight = data_obs2.weight()
            mH_val = var_set.getRealValue(f"mH_{MHRegion}_default")  # Extract mH value
            mA_val = var_set.getRealValue("mA_default")  # Extract mA value
            Total_events2 +=weight
            if weight<0:
                print( f"Bin {i}, (mH = {mH_val}, mA = {mA_val}): {weight}")
                if f"{IsPass}"=="Fail":
                    exit()
        print("total ws, raw hist: ", Total_events2, Total_events1)
        if(abs(Total_events1-Total_events2)/Total_events1 > 0.2) :
            print("----- Something is wrong! -----")
            #exit()
        if f"{IsPass}_{MHRegion}" !="Pass_SIG":
            compare_2D_histograms(data_obs1, data_obs2, mH_default, mA_default, f"{category}_{IsPass}_{MHRegion}")
        del hist_rebinned


BKGMCTotal_pass_Smooth1.Scale( Nevt_allregions["Pass"]*1.0/BKGMCTotal_pass_Smooth1.Integral() )
BKGMCTotal_fail_Smooth1.Scale( Nevt_allregions["Fail"]*1.0/BKGMCTotal_fail_Smooth1.Integral() )

def toys_generator(hist1, hist2, ntoyes, output_filename):
    for i in range(ntoyes):
        print(hist1.GetName())
        filename = hist1.GetName().split("_pnet")[0].replace("smooth1",f"smooth1_toy{i}")
        output_file = ROOT.TFile(output_filename+"/"+filename+".root", "RECREATE")
        toy_hist1 = hist1.Clone(hist1.GetName().replace("smooth1",f"smooth1_toy{i}"))
        for ix in range(1, hist1.GetNbinsX() + 1):
            for iy in range(1, hist1.GetNbinsY() + 1):
                expected = hist1.GetBinContent(ix, iy)
                fluctuated = np.random.poisson(expected)
                toy_hist1.SetBinContent(ix, iy, fluctuated)
        toy_hist1.Write()
        toy_hist2 = hist2.Clone(hist2.GetName().replace("smooth1",f"smooth1_toy{i}"))
        for ix in range(1, hist2.GetNbinsX() + 1):
            for iy in range(1, hist2.GetNbinsY() + 1):
                expected = hist2.GetBinContent(ix, iy)
                fluctuated = np.random.poisson(expected)
                toy_hist2.SetBinContent(ix, iy, fluctuated)
        toy_hist2.Write()
        output_file.Close()

#output_file = ROOT.TFile(output_hist_name, "RECREATE")  # Create a new ROOT file
##w1.Write()  # Write the workspace to the file
#BKGMCTotal_pass_Smooth1.Write()
#BKGMCTotal_fail_Smooth1.Write()
#output_file.Close()  # Close the file

Ntoys=50
toys_generator(BKGMCTotal_pass_Smooth1, BKGMCTotal_fail_Smooth1, Ntoys, output_hist_name)

import json
# Read JSON file
os.system("mkdir -p mctoysjson/")
if category == "Leptonic_Hi":
    for i in range(Ntoys):
        with open('XXHi_Htoaato4b.json', 'r') as f:
            data = json.load(f)  # `data` is now a Python dictionary or list
        data['PROCESSES']["data_obs"]['ALIAS'] = f"XXHi_BKGsmooth1_toy{i}_2018"
        with open(f'mctoysjson/XXHi_Htoaato4b_mctoy{i}.json', 'w') as f:
            json.dump(data, f, indent=4)
elif category == "Leptonic_Lo":
    for i in range(Ntoys):
        with open('XXLo_Htoaato4b.json', 'r') as f:
            data = json.load(f)  # `data` is now a Python dictionary or list
        data['PROCESSES']["data_obs"]['ALIAS'] = f"XXLo_BKGsmooth1_toy{i}_2018"
        with open(f'mctoysjson/XXLo_Htoaato4b_mctoy{i}.json', 'w') as f:
            json.dump(data, f, indent=4)
elif category == "gg0lIncl":
    for i in range(Ntoys):
        with open('gg0lIncl_Htoaato4b.json', 'r') as f:
            data = json.load(f)  # `data` is now a Python dictionary or list
        data['PROCESSES']["data_obs"]['ALIAS'] = f"gg0lIncl_BKGsmooth1_toy{i}_2018"
        with open(f'mctoysjson/gg0lIncl_Htoaato4b_mctoy{i}.json', 'w') as f:
            json.dump(data, f, indent=4)
elif category == "VBF_Hi":
    for i in range(Ntoys):
        with open('VBFjjHi_Htoaato4b.json', 'r') as f:
            data = json.load(f)  # `data` is now a Python dictionary or list
        data['PROCESSES']["data_obs"]['ALIAS'] = f"VBFjjHi_Xto4bv2_BKGsmooth1_toy{i}_2018"
        with open(f'mctoysjson/VBFjjHi_Xto4bv2_Htoaato4b_mctoy{i}.json', 'w') as f:
            json.dump(data, f, indent=4)
elif category == "VBF_Lo":
    for i in range(Ntoys):
        with open('VBFjjLo_Htoaato4b.json', 'r') as f:
            data = json.load(f)  # `data` is now a Python dictionary or list
        data['PROCESSES']["data_obs"]['ALIAS'] = f"VBFjjLo_Xto4bv2_BKGsmooth1_toy{i}_2018"
        with open(f'mctoysjson/VBFjjLo_Xto4bv2_Htoaato4b_mctoy{i}.json', 'w') as f:
            json.dump(data, f, indent=4)
