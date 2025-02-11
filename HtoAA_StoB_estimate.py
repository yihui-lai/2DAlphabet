#!/usr/bin/env python

################################################################################################
################################################################################################
########### Author: Andrew Brinkerhoff                                               ###########
########### Purpose: Estimate S/B of different 2D Alphabet Categories                ###########
########### Input: 2D plots used to run 2D Alphabet                                  ###########
########### Output: S/10; B; S/B; S/sqrt(B+err), limit (conservative)                ###########
################################################################################################
################################################################################################

import os
import sys
import math
import ROOT as R
from array import array

R.gROOT.SetBatch(True)  ## Don't display histograms or canvases when drawn
R.gStyle.SetOptStat(0)  ## Don't display stat boxes

## Will finalize this dictionary once all categories are defined
config = {
    "VERBOSE": False,
    "YEAR": '2018',
    "MASSH": 'mass',
    "MASSWIN": [100, 140],
    "MASSESA": ['15', '30', '55'],
    "BKGS": [],
    "categories": {
        "gg0lHi": {
            "IN_DIR": '/eos/cms/store/user/ssawant/htoaa/analysis/20240627_gg0l_1/2018/2DAlphabet_inputFiles/gg0lHi/',
            "SIGS": ['ggHtoaato4b'],
            "CATS": ['gg0lHi'],
            "WP_CUTS": ['WP40', 'WP60', 'WP80']
        },
        "gg0lLo": {
            "IN_DIR": '/eos/cms/store/user/ssawant/htoaa/analysis/20240627_gg0l_1/2018/2DAlphabet_inputFiles/gg0lLo/',
            "SIGS": ['ggHtoaato4b'],
            "CATS": ['gg0lLo'],
            "WP_CUTS": ['WP40', 'WP60', 'WP80']
        },
        "VBFjjHi": {
            "IN_DIR": '/afs/cern.ch/work/m/moanwar/public/hto2ato4b/2DAlphabetfiles_VBFjjHi/',
            "SIGS": ['VBFHtoaato4b', 'ggHtoaato4b'],
            "CATS": ['VBFjjHi'],
            "WP_CUTS": ['WP40', 'WP60']
        },
        "ttbTbjjLo": {
            "IN_DIR": '/eos/cms/store/user/ssawant/htoaa/analysis/20240723_tt0lbTbjj/2018/2DAlphabet_inputFiles/ttbTbjjLo/',
            "SIGS": ['ttHtoaato4b'],
            "CATS": ['ttbTbjjLo'],
            "WP_CUTS": ['WP40', 'WP60', 'WP80']
        },
        "ttbll": {
            "IN_DIR": '/afs/cern.ch/user/h/hboucham/public/2D_2Ltt_012925_v2/',  ## Double lepton
            "SIGS": ['ttHtoaato4b'],
            "CATS": ['ttbll'],
            "WP_CUTS": ['WP60']
        },
        "Zll": {
            "IN_DIR": '/afs/cern.ch/user/h/hboucham/public/2D_2LZ_012925_v2/',
            "SIGS": ['ZHtoaato4b'],
            "CATS": ['Zll'],
            "WP_CUTS": ['WP60']
        },
        "Wlv": {
            "IN_DIR": '/afs/cern.ch/user/h/hboucham/public/2D_1L_012925_v2/',  ## Double lepton
            "SIGS": ['WHtoaato4b'],
            "CATS": ['WlvHi', 'WlvLo'],
            "WP_CUTS": ['WP60']
        },
        "ttblv": {
            "IN_DIR": '/afs/cern.ch/user/h/hboucham/public/2D_1L_012925_v2/',  ## Double lepton
            "SIGS": ['ttHtoaato4b'],
            "CATS": ['ttblv', 'ttbblv'],
            "WP_CUTS": ['WP60']
        },
        "Vjj": {
            "IN_DIR": '/eos/cms/store/user/ssawant/htoaa/analysis/20240626_Vjj/2018/2DAlphabet_inputFiles/Vjj/',
            "SIGS": ['WHtoaato4b', 'ZHtoaato4b'],
            "CATS": ['Vjj'],
            "WP_CUTS": ['WP40', 'WP60']
        },
        "ZvvLo": {
            "IN_DIR": '/eos/cms/store/user/ssawant/htoaa/analysis/20240626_Zvv_METDataset_2/2018/2DAlphabet_inputFiles/ZvvLo/',
            "SIGS": ['ZHtoaato4b'],
            "CATS": ['ZvvLo'],
            "WP_CUTS": ['WP40', 'WP60']
        },
        "ZvvHi": {
            "IN_DIR": '/eos/cms/store/user/ssawant/htoaa/analysis/20240626_Zvv_METDataset_2/2018/2DAlphabet_inputFiles/ZvvHi/',
            "SIGS": ['ZHtoaato4b'],
            "CATS": ['ZvvHi'],
            "WP_CUTS": ['WP40', 'WP60']
        }
    },
}

def main():

    # Specify category you would like to run
    current = "Zll" 
    #current = "ttbll"
    #current = "Wlv"
    #current = "ttblv"

    print('\nInside HtoAA_StoB_est\n')

    scenario = config["categories"][current]
    IN_DIR = scenario["IN_DIR"]
    SIGS = scenario["SIGS"]
    CATS = scenario["CATS"]
    WP_CUTS = scenario["WP_CUTS"]

    samps = ['Data']
    for bkg in config["BKGS"]:
        samps.append(bkg)
    for sig in SIGS:
        for mA in config["MASSESA"]:
            samps.append(f'{sig}_mA_{mA}')

    yields = {}

    for wp in WP_CUTS:
        yields[wp] = {}
        for cat in CATS:
            yields[wp][cat] = {}
            for samp in samps:
                if cat.startswith('W') and samp.startswith('ttHtoaa'): continue
                if cat.startswith('ttb') and samp.startswith('WHtoaa'): continue
                yields[wp][cat][samp] = {}

                if 'hboucham' in IN_DIR:
                    in_file_str = f'{IN_DIR}{wp}/{cat}_{samp}_{config["YEAR"]}.root'
                else:
                    in_file_str = f'{IN_DIR}{cat}_{samp}_{config["YEAR"]}.root'
                in_file = R.TFile(in_file_str, 'open')
                if config["VERBOSE"]: print(f'\nOpened {in_file_str}')

                for pf in ['Pass', 'Fail']:
                    if pf == 'Fail' and 'Htoaato4b' in samp: continue

                    h_name = f'{cat}_{samp}_{config["YEAR"]}_{config["MASSH"]}_{wp}_{pf}_Nom'
                    hist = in_file.Get(h_name)
                    if config["VERBOSE"]: print(f'\nGot histogram {h_name}')
                    if config["VERBOSE"]: print(f'  * Integral = {hist.Integral():.1f}')

                    yields[wp][cat][samp][pf] = {}
                    yields[wp][cat][samp][pf]['mH_in'] = 0

                    nY = hist.GetNbinsY()
                    for iX in range(1, hist.GetNbinsX() + 1):
                        if config["MASSWIN"][0] < hist.GetXaxis().GetBinCenter(iX) < config["MASSWIN"][1]:
                            yields[wp][cat][samp][pf]['mH_in'] += hist.Integral(iX, iX, 1, nY)
                    yields[wp][cat][samp][pf]['mH_out'] = hist.Integral() - yields[wp][cat][samp][pf]['mH_in']

                    if config["VERBOSE"]: 
                        print(f'{wp} {cat} {samp} {pf} total = {hist.Integral():.1f}, mH_in = {yields[wp][cat][samp][pf]["mH_in"]:.1f}, mH_out = {yields[wp][cat][samp][pf]["mH_out"]:.1f}')
                    del hist

                in_file.Close()

            ## End loop: for samp in samps

            nSig = 0
            for sig in SIGS:
                if cat.startswith('W') and sig.startswith('ttHtoaa'): continue
                if cat.startswith('ttb') and sig.startswith('WHtoaa'): continue
                for mA in config["MASSESA"]:
                    nSig += yields[wp][cat][f'{sig}_mA_{mA}']['Pass']['mH_in']
            nSig /= (10.0 * len(config["MASSESA"]))  ## Scale down to 10% branching fraction
            if cat == 'gg0l':
                print('\nWARNING!!! In gg0l from 20240530, signal over-estimated by roughly a factor of 4!')
                print('Scaling signal by 0.25 to compensate. - AWB 2024.06.26')
                nSig *= 0.25

            ## For any 0 yields, set to 0.5 as best guess between 0 and 1
            nBkg  = max(yields[wp][cat]['Data']['Fail']['mH_in'],  0.5)
            nBkg *= max(yields[wp][cat]['Data']['Pass']['mH_out'], 0.5)
            nBkg /= max(yields[wp][cat]['Data']['Fail']['mH_out'], 0.5)

            ## For any 0 yields, set to 1.0, i.e. 100% relative uncertainty
            eBkg  = (1.0 / max(yields[wp][cat]['Data']['Fail']['mH_in'],  1.0))
            eBkg += (1.0 / max(yields[wp][cat]['Data']['Pass']['mH_out'], 1.0))
            eBkg += (1.0 / max(yields[wp][cat]['Data']['Fail']['mH_out'], 1.0))
            eBkg = nBkg * math.sqrt(eBkg)

            print(f'{wp} {cat} S/10 = {nSig:.3f}, B = {nBkg:.2f} +/- {eBkg:.2f}, S/B = {nSig/nBkg:.3f} +/- {(nSig/nBkg)*(eBkg/nBkg):.3f}, S/sqrt(B+err) = {nSig/math.sqrt(nBkg+eBkg):.3f}, limit = {(0.2/nSig) * (1 + math.sqrt(nBkg+eBkg + 1)):.4f}')

        ## End loop: for cat in CATS
    ## End loop: for wp in WP_CUTS

    print('\nAll done!')

## End function: def main()

if __name__ == '__main__':
    main()
