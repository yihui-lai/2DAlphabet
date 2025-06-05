#! /usr/bin/env python
## Modified from https://github.com/bouchamaouihichem/2DAlphabet/blob/dev25_0501/merge_file_script_mctoy.py

## Script to estimate S/B ratio for various categories
## Updated to merge sub-categories into 2DAlphabet fit categories
import os
import sys
import shutil
import math
import ROOT as R
from array import array

R.gROOT.SetBatch(True)  ## Don't display histograms or canvases when drawn
R.gStyle.SetOptStat(0)  ## Don't display stat boxes

## User configuration
VERBOSE  = False
YEAR     = '2018'
MASSESH  = ['mass', 'msoft', 'pnet']
MASSESA  = ['15', '30', '55']
WP_CUTS  = ['WP40', 'WP60', 'WP80']
MA_reg   = '34a'
DATE     = '2025_01_01'

CATS_IN = {}
CAT_OUT = sys.argv[1]  ## gg0lIncl, LepHi, LepLo
IN_DIR = 'raw_inputs/'
INCL = 'Incl'

print('\nRunning merge_file_script_mctoy.py for %s' % CAT_OUT)
if CAT_OUT == 'gg0lIncl':
    MASSESH  = ['pnet']
    WP_CUTS  = ['WP60','WP40']
    MA_reg = '34a'
    DATE   = '2025_05_02'
    CAT_INS = ['gg0lLo','gg0lHi']
    INCL = ''  ## Replace "Incl" with blank in directory / file / histogram names
    for cat in CAT_INS:
        CATS_IN[cat] = {}
        CATS_IN[cat]['sigs'] = [pr+'Htoaato4b' for pr in ['gg','VBF','W','Z','tt']]
        CATS_IN[cat]['bkgs'] = ['MC','QCD_BGen','QCD_bEnr','QCD_Incl','Zqq','Wqq','TT0l','TT1l','ggH']
    CATS_IN['gg0lHi']['dir'] = IN_DIR+'2D_in_gg0l_'+DATE+'/gg0lHi/'
    CATS_IN['gg0lLo']['dir'] = IN_DIR+'2D_in_gg0l_'+DATE+'/gg0lLo/'

elif CAT_OUT == 'VBFjjIncl':
    MASSESH  = ['pnet']
    WP_CUTS  = ['WP40']
    MA_reg = '34a'
    DATE   = '2025_04_06'
    CAT_INS = ['VBFjjLo','VBFjjHi']
    INCL = ''  ## Replace "Incl" with blank in directory / file / histogram names
    for cat in CAT_INS:
        CATS_IN[cat] = {}
        CATS_IN[cat]['sigs'] = ['VBFHtoaato4b']
        CATS_IN[cat]['bkgs'] = ['MC']
    print('\nError!!! VBFjj should have all signal available, not just one production mode.')
    CATS_IN['VBFjjHi']['dir'] = IN_DIR+'2D_in_VBFjj_'+DATE+'/VBFjjHi/'
    CATS_IN['VBFjjLo']['dir'] = IN_DIR+'2D_in_VBFjj_'+DATE+'/VBFjjLo/'

elif CAT_OUT == 'LepIncl':
    MASSESH  = ['pnet']
    WP_CUTS  = ['WP60']
    MA_reg = 'a'
    DATE   = '2025_03_06'
    CAT_INS = ['WlvHi', 'ttbblv', 'ttbll', 'Zll', 'WlvLo', 'ttblv']
    for cat in CAT_INS:
        CATS_IN[cat] = {}
        #CATS_IN[cat]['sigs']  = [pr+'Htoaato4b' for pr in ['W','Z','tt']]
    print('\nError!!! All leptonic categories should have all WH/ZH/ttH signal available, not just one production mode.')
    CATS_IN['WlvHi']['dir']   = IN_DIR+'2D_in_Wlv_ttlv_'+DATE+'/'
    CATS_IN['ttbblv']['dir']  = IN_DIR+'2D_in_Wlv_ttlv_'+DATE+'/'
    CATS_IN['ttbll']['dir']   = IN_DIR+'2D_in_ttll_'+DATE+'/'
    CATS_IN['Zll']['dir']     = IN_DIR+'2D_in_Zll_'+DATE+'/'
    CATS_IN['WlvHi']['sigs']  = ['WHtoaato4b']
    CATS_IN['ttbblv']['sigs'] = ['ttHtoaato4b']
    CATS_IN['ttbll']['sigs']  = ['ttHtoaato4b']
    CATS_IN['Zll']['sigs']    = ['ZHtoaato4b']
    #CATS_IN['ZvvHi']['sigs']  = ['ZHtoaato4b']
    CATS_IN['WlvHi']['bkgs']  = ['Wlv','TT1l']
    CATS_IN['ttbblv']['bkgs'] = ['Wlv','TT1l']
    CATS_IN['ttbll']['bkgs']  = ['TT2l']
    CATS_IN['Zll']['bkgs']    = ['Zll','ZZ','TT2l']
    CATS_IN['WlvLo']['dir']  = IN_DIR+'2D_in_Wlv_ttlv_'+DATE+'/'
    CATS_IN['ttblv']['dir']  = IN_DIR+'2D_in_Wlv_ttlv_'+DATE+'/'
    #CATS_IN['ZvvLo']['dir']   = IN_DIR+'2D_in_ZvvLo_'+DATE+'/'
    CATS_IN['WlvLo']['sigs'] = ['WHtoaato4b']
    CATS_IN['ttblv']['sigs'] = ['ttHtoaato4b']
    #CATS_IN['ZvvLo']['sigs'] = ['ZHtoaato4b']
    CATS_IN['WlvLo']['bkgs'] = ['Wlv','TT1l']
    CATS_IN['ttblv']['bkgs'] = ['Wlv','TT1l']

elif CAT_OUT.startswith('LepHi'):
    MASSESH  = ['pnet']
    WP_CUTS  = ['WP60']
    MA_reg = 'a'
    DATE   = '2025_03_06'
    CAT_INS = ['WlvHi', 'ttbblv', 'ttbll', 'Zll'] #, 'ZvvHi']
    for cat in CAT_INS:
        CATS_IN[cat] = {}
        #CATS_IN[cat]['sigs']  = [pr+'Htoaato4b' for pr in ['W','Z','tt']]
    print('\nError!!! All leptonic categories should have all WH/ZH/ttH signal available, not just one production mode.')
    CATS_IN['WlvHi']['dir']   = IN_DIR+'2D_in_Wlv_ttlv_'+DATE+'/'
    CATS_IN['ttbblv']['dir']  = IN_DIR+'2D_in_Wlv_ttlv_'+DATE+'/'
    CATS_IN['ttbll']['dir']   = IN_DIR+'2D_in_ttll_'+DATE+'/'
    CATS_IN['Zll']['dir']     = IN_DIR+'2D_in_Zll_'+DATE+'/'
    CATS_IN['WlvHi']['sigs']  = ['WHtoaato4b']
    CATS_IN['ttbblv']['sigs'] = ['ttHtoaato4b']
    CATS_IN['ttbll']['sigs']  = ['ttHtoaato4b']
    CATS_IN['Zll']['sigs']    = ['ZHtoaato4b']
    #CATS_IN['ZvvHi']['sigs']  = ['ZHtoaato4b']
    CATS_IN['WlvHi']['bkgs']  = ['Wlv','TT1l']
    CATS_IN['ttbblv']['bkgs'] = ['Wlv','TT1l']
    CATS_IN['ttbll']['bkgs']  = ['TT2l']
    CATS_IN['Zll']['bkgs']    = ['Zll','ZZ','TT2l']
    if CAT_OUT == 'LepHiA':
        CAT_INS.append('WlvLo')
        CATS_IN['WlvLo'] = {}
        CATS_IN['WlvLo']['dir']  = IN_DIR+'2D_in_Wlv_ttlv_'+DATE+'/'
        CATS_IN['WlvLo']['sigs'] = ['WHtoaato4b']
        CATS_IN['WlvLo']['bkgs'] = ['Wlv','TT1l']
    if CAT_OUT == 'LepHiB':
        CAT_INS.append('ttblv')
        CATS_IN['ttblv'] = {}
        CATS_IN['ttblv']['dir']  = IN_DIR+'2D_in_Wlv_ttlv_'+DATE+'/'
        CATS_IN['ttblv']['sigs'] = ['ttHtoaato4b']
        CATS_IN['ttblv']['bkgs'] = ['Wlv','TT1l']
    if CAT_OUT == 'LepHiC':
        CAT_INS.remove('WlvHi')
    if CAT_OUT == 'LepHiD':
        CAT_INS.remove('ttbblv')
    if CAT_OUT == 'LepHiE':
        CAT_INS.remove('ttbll')
    if CAT_OUT == 'LepHiF':
        CAT_INS.remove('Zll')
    for cat in list(CATS_IN.keys()):
        if not cat in CAT_INS:
            del CATS_IN[cat]

elif CAT_OUT.startswith('LepLo'):
    MASSESH  = ['pnet']
    WP_CUTS  = ['WP60']
    MA_reg = 'a'
    DATE   = '2025_03_06'
    CAT_INS = ['WlvLo', 'ttblv'] #, 'ZvvLo']
    CATS_IN = {}
    for cat in CAT_INS:
        CATS_IN[cat] = {}
        #CATS_IN[cat]['sigs'] = [pr+'Htoaato4b' for pr in ['W','Z','tt']]
    print('\nError!!! All leptonic categories should have all signal available, not just one production mode.')
    CATS_IN['WlvLo']['dir']  = IN_DIR+'2D_in_Wlv_ttlv_'+DATE+'/'
    CATS_IN['ttblv']['dir']  = IN_DIR+'2D_in_Wlv_ttlv_'+DATE+'/'
    #CATS_IN['ZvvLo']['dir']   = IN_DIR+'2D_in_ZvvLo_'+DATE+'/'
    CATS_IN['WlvLo']['sigs'] = ['WHtoaato4b']
    CATS_IN['ttblv']['sigs'] = ['ttHtoaato4b']
    #CATS_IN['ZvvLo']['sigs'] = ['ZHtoaato4b']
    CATS_IN['WlvLo']['bkgs'] = ['Wlv','TT1l']
    CATS_IN['ttblv']['bkgs'] = ['Wlv','TT1l']
    if CAT_OUT == 'LepLoA':
        CAT_INS.remove('WlvLo')
    if CAT_OUT == 'LepLoB':
        CAT_INS.remove('ttblv')
    if CAT_OUT == 'LepLoC':
        CAT_INS.append('WlvHi')
        CATS_IN['WlvHi'] = {}
        CATS_IN['WlvHi']['dir']   = IN_DIR+'2D_in_Wlv_ttlv_'+DATE+'/'
        CATS_IN['WlvHi']['sigs']  = ['WHtoaato4b']
        CATS_IN['WlvHi']['bkgs']  = ['Wlv','TT1l']
    if CAT_OUT == 'LepLoD':
        CAT_INS.append('ttbblv')
        CATS_IN['ttbblv'] = {}
        CATS_IN['ttbblv']['dir']  = IN_DIR+'2D_in_Wlv_ttlv_'+DATE+'/'
        CATS_IN['ttbblv']['sigs'] = ['ttHtoaato4b']
        CATS_IN['ttbblv']['bkgs'] = ['Wlv','TT1l']
    if CAT_OUT == 'LepLoE':
        CAT_INS.append('ttbll')
        CATS_IN['ttbll'] = {}
        CATS_IN['ttbll']['dir']   = IN_DIR+'2D_in_ttll_'+DATE+'/'
        CATS_IN['ttbll']['sigs']  = ['ttHtoaato4b']
        CATS_IN['ttbll']['bkgs']  = ['TT2l']
    if CAT_OUT == 'LepLoF':
        CAT_INS.append('Zll')
        CATS_IN['Zll'] = {}
        CATS_IN['Zll']['dir']     = IN_DIR+'2D_in_Zll_'+DATE+'/'
        CATS_IN['Zll']['sigs']    = ['ZHtoaato4b']
        CATS_IN['Zll']['bkgs']    = ['Zll','ZZ','TT2l']
    for cat in list(CATS_IN.keys()):
        if not cat in CAT_INS:
            del CATS_IN[cat]


else:
    print('\nERROR!!! Specify valid CAT_OUT in merge_file_script_mctoy.py! (%s is invalid.)\n' % CAT_OUT)
    sys.exit()

## For use as input to Haa4b_makeMCtoy.py
OUT_DIR = IN_DIR+'2D_in_merged_'+CAT_OUT.replace('Incl',INCL)+'/'
## For use as input to htoaato4b_mctoy.py
OUT_DIRS = {}
for cat in [CAT_OUT]+CAT_INS:
    OUT_DIRS[cat] = 'plots/'+cat+'/'


def main():

    print('\nInside HtoAA_2DAlphabet_merge_inputs\n')

    print('\n\nWARNING!!! Should run from inside 2DAlphabet/CMSSW_11_3_4/src/2DAlphabet/')
    print('to avoid "list is accessing an object already deleted" error! - AWB 2024.06.24\n')
    print('See https://root-forum.cern.ch/t/error-in-tlist-clear-a-list-is-accessing-an-object-already-deleted-list-name-tlist-when-opening-a-file-created-by-root-6-30-using-root-6-14-09/57588/1')
    

    print('\nDeleting any existing output directories, and creating empty ones:')
    for o_dir in [OUT_DIR]+[OUT_DIRS[cat] for cat in [CAT_OUT]+CAT_INS]:
        print(o_dir)
        if os.path.exists(o_dir):
            shutil.rmtree(o_dir)
        os.mkdir(o_dir)

    h_outs = {}  ## Save summed output histograms
    h_ins  = {}  ## Also save the inputs (keeps naming scheme consistent)
    for cat in CAT_INS:
        samps = ['Data']
        for bkg in CATS_IN[cat]['bkgs']:
            samps.append(bkg)
        for sig in CATS_IN[cat]['sigs']:
            for mA in MASSESA:
                samps.append(sig+'_mA_'+mA)
        for samp in samps:
            for wp in WP_CUTS:
                ## CHANGING THIS IN ORDER TO ACCOMMODATE NON-UNIFORM NAMING CONVENTIONS!!!
                if 'LepHi' in CAT_OUT or 'LepLo' or 'LepIncl' in CAT_OUT:
                    in_file_str = CATS_IN[cat]['dir']+'%s/%s_%s_%s.root' % (wp, cat, samp, YEAR)
                elif 'VBF' in CAT_OUT:
                    in_file_str = CATS_IN[cat]['dir']+'%s_Xto4bv2_%s_%s.root' % (cat, samp, YEAR)
                else:
                    in_file_str = CATS_IN[cat]['dir']+'%s_%s_%s.root' % (cat, samp, YEAR)
                in_file = R.TFile(in_file_str, 'open')
                print('\n*******\nReading from %s' % in_file_str)

                for mH in MASSESH:
                    for pf in ['Pass', 'Fail']:
                        #h_in_name = '%s_%s_%s_%s_%s_%s_Nom' % (cat, samp, YEAR, mH, wp, pf)
                        ## CHANGING THIS IN ORDER TO ACCOMMODATE WEIRD NAMING CONVENTIONS!!!
                        h_in_name = ''
                        if ('gg0l' in cat or 'VBF' in cat):
                            catStr = (cat+'_Xto4bv2' if 'VBF' in cat else cat)
                            sampStr = ('Data' if samp == 'MC' else samp)
                            mHStr = (mH+'_vs_massA'+MA_reg if 'gg0l' in cat else mH)
                            h_in_name = '%s_%s_%s_%s_%s_%s_Nom' % (catStr, sampStr, YEAR, mHStr, wp, pf)
                            print(h_in_name)
                        else:
                            h_in_name = '%s_%s_%s_%s_%s_%s_Nom' % (cat, samp, YEAR, mH, wp, pf)
                        ##################################################################
                        h_in = in_file.Get(h_in_name)
                        if VERBOSE: print('\nGot histogram %s' % h_in_name)
                        if VERBOSE: print('  * Integral = %.1f' % h_in.Integral())

                        h_out_name = '%s_%s_%s_%s_%s_%s_Nom' % (CAT_OUT, samp, YEAR, mH, wp, pf)
                        h_in_name_save = '%s_%s_%s_%s_%s_%s_Nom' % (cat, samp, YEAR, mH, wp, pf)
                        h_ins[h_in_name_save] = h_in.Clone(h_in_name_save)
                        if VERBOSE: print('Cloned %s into %s' % (h_in_name, h_ins[h_in_name_save].GetName()))
                        if VERBOSE: print('  * Integral = %.1f' % h_ins[h_in_name_save].Integral())
                        h_ins[h_in_name_save].SetDirectory(0) ## Save locally
                        
                        if not h_out_name in h_outs.keys():
                            h_outs[h_out_name] = h_in.Clone(h_out_name)
                            if VERBOSE: print('Created %s' % h_out_name)
                            if VERBOSE: print('  * Integral = %.1f' % h_outs[h_out_name].Integral())
                            h_outs[h_out_name].SetDirectory(0) ## Save locally
                        else:
                            if VERBOSE: print('Adding %.1f to %s (with %.1f)' % (h_in.Integral(), h_out_name, \
                                                                                 h_outs[h_out_name].Integral()))
                            nXo = h_outs[h_out_name].GetNbinsX()
                            nYo = h_outs[h_out_name].GetNbinsY()
                            nXi = h_in.GetNbinsX()
                            nYi = h_in.GetNbinsY()
                            xLo = h_outs[h_out_name].GetXaxis().GetBinLowEdge(1)
                            xHo = h_outs[h_out_name].GetXaxis().GetBinLowEdge(nXo+1)
                            yLo = h_outs[h_out_name].GetYaxis().GetBinLowEdge(1)
                            yHo = h_outs[h_out_name].GetYaxis().GetBinLowEdge(nYo+1)
                            xLi = h_in.GetXaxis().GetBinLowEdge(1)
                            xHi = h_in.GetXaxis().GetBinLowEdge(nXi+1)
                            yLi = h_in.GetYaxis().GetBinLowEdge(1)
                            yHi = h_in.GetYaxis().GetBinLowEdge(nYi+1)
                            if (nXo != nXi or nYo != nYi or xLo != xLi or xHo != xHi or yLo != yLi or yHo != yHi):
                                print('\nMAJOR ERROR!!! %s is %d x %d, %s is %d x %d' % (h_out_name, nXo, nYo,
                                                                                         h_in_name, nXi, nYi))
                                print('Spanning [%.1f-%.1f] x [%.1f-%.1f] vs. [%.1f-%.1f] x [%.1f-%.1f]' % (xLo, xHo, yLo, yHo,
                                                                                                            xLi, xHi, yLi, yHi))
                                sys.exit()
                            else:    
                                h_outs[h_out_name].Add(h_in)
                                if VERBOSE: print('  * Integral = %.1f' % h_outs[h_out_name].Integral())

                    ## End loop: for pf in ['Pass', 'Fail']
                ## End loop: for mH in MASSESH
                in_file.Close()

                ## Common output ROOT file with all histograms (input to Haa4b_makeMCtoy.py)
                out_file_str = OUT_DIR+('%s_%s_%s.root' % (CAT_OUT.replace('Incl',INCL), samp, YEAR))
                root_cmd = ('update' if os.path.exists(out_file_str) else 'recreate')
                out_file = R.TFile(out_file_str, root_cmd)
                ## ROOT file with only merged category histograms (input to htoaato4b_mctoy.py)
                out_file_str2 = OUT_DIRS[CAT_OUT]+('%s_%s_%s.root' % (CAT_OUT, samp, YEAR))
                root_cmd2 = ('update' if os.path.exists(out_file_str2) else 'recreate')
                out_file2 = R.TFile(out_file_str2, root_cmd2)
                ## ROOT file with only individual category histograms (input to htoaato4b_mctoy.py)
                out_file_str3 = OUT_DIRS[cat]+('%s_%s_%s.root' % (cat, samp, YEAR))
                root_cmd3 = ('update' if os.path.exists(out_file_str3) else 'recreate')
                out_file3 = R.TFile(out_file_str3, root_cmd3)

                print('\n*******\nWriting to %s' % out_file_str)
                print('(Also to %s and %s' % (out_file_str2, out_file_str3))

                for mH in MASSESH:
                    for pf in ['Pass', 'Fail']:
                        ## Write out individual input histograms
                        h_in_name_save = '%s_%s_%s_%s_%s_%s_Nom' % (cat, samp, YEAR, mH, wp, pf)
                        out_file.cd()
                        h_ins[h_in_name_save].Write()
                        out_file3.cd()
                        h_ins[h_in_name_save].Write()                        
                        if VERBOSE: print('Wrote out %s' % h_in_name_save)
                        if VERBOSE: print('  * Integral = %.1f' % h_ins[h_in_name_save].Integral())
                        ## Write out summed output histogram (overwrite if needed)
                        h_out_name = '%s_%s_%s_%s_%s_%s_Nom' % (CAT_OUT, samp, YEAR, mH, wp, pf)
                        out_file.cd()
                        h_outs[h_out_name].Write('', R.TObject.kOverwrite)
                        out_file2.cd()
                        h_outs[h_out_name].Write('', R.TObject.kOverwrite)
                        if VERBOSE: print('Wrote out %s' % h_out_name)
                        if VERBOSE: print('  * Integral = %.1f' % h_outs[h_out_name].Integral())
                    ## End loop: for pf in ['Pass', 'Fail']
                ## End loop: for mH in MASSESH
                out_file.Write()
                out_file.Close()
                out_file2.Write()
                out_file2.Close()
                out_file3.Write()
                out_file3.Close()
            ## End loop: for wp in WP_CUTS
        ## End loop: for samp in samps
    ## End loop: for cat in CAT_INS
    print('\n\nAll done!')
    
## End function: def main()


if __name__ == '__main__':
    main()

