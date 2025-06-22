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
PRINTONLY = False
YEAR     = '2018'
HADSIGS  = ['ggH', 'VBFH', 'WH', 'ZH', 'ttH']
LEPSIGS  = ['WH', 'ZH', 'ttH']
MASSESA  = ['12']+[str(mA*5) for mA in range(3,13)]
MHREGS   = ['mass', 'msoft', 'pnet']
MAREGS   = ['34a', '34d', '4a']
WP_CUTS  = ['WP60']  ## Default for most categories
DATE     = '2025_06_03'
eos_from_config = [eos for eos in (open('config/user.config','r')).readlines() if eos.startswith('EOS_DIR=')]
EOS_DIR = eos_from_config[0].replace('EOS_DIR=','').replace('\n','')

CATS_IN = {}
CAT_OUT = sys.argv[1]  ## gg0lIncl, LepHi, LepLo, etc.
CAT_INS = [CAT_OUT]
IN_DIR = 'raw_inputs/%s/%s/' % (YEAR, DATE)

IS_HAD,IS_LEP = False,False
for pref in ['gg0l','VBFjj','Vjj','tt0l']:
    if CAT_OUT.startswith(pref):
        IS_HAD = True
for pref in ['Lep','Zll','Wlv','ttb','Zvv']:
    if CAT_OUT.startswith(pref):
        IS_LEP = True
assert (IS_HAD or IS_LEP), 'CAT_OUT %s not valid!!! Quitting.' % CAT_OUT

print('\nRunning merge_file_script_mctoy.py for %s' % CAT_OUT)
if IS_HAD:
    if CAT_OUT.startswith('gg0l') or CAT_OUT.startswith('VBFjj'):
        WP_CUTS  = ['WP40', 'WP60']  ## Use WP60 to model WP40
    if CAT_OUT.endswith('Incl'):
        CAT_INS = [CAT_OUT.replace('Incl','')+sub for sub in ['Lo','Hi']]
    for cat in CAT_INS:
        CATS_IN[cat] = {}
        CATS_IN[cat]['sigs'] = [sig+'toaato4b' for sig in HADSIGS]
        CATS_IN[cat]['bkgs'] = ['QCD_BGen','QCD_bEnr','QCD_Incl','Wqq','Zqq','TT0l','TT1l','MC']  ## Put 'MC' at the end!!!
        if CAT_OUT.startswith('VBFjj'):
            CATS_IN[cat]['bkgs'] = CATS_IN[cat]['bkgs'][0:-1]  ## Does not already have summed MC
        CATS_IN[cat]['dir']  = IN_DIR+cat
        if cat.startswith('VBFjj'):
            CATS_IN[cat]['dir']  = IN_DIR+'VBFjj'

elif IS_LEP:
    if CAT_OUT.startswith('Lep'):
        CAT_INS = []
        for pref in ['LepLo','LepIncl']:
            if CAT_OUT.startswith(pref):
                CAT_INS = CAT_INS+['ZvvLo','WlvLo','ttblv']
                break
        for pref in ['LepHi','LepIncl']:
            if CAT_OUT.startswith(pref):
                CAT_INS = CAT_INS+['ZvvHi','Zll','WlvHi','ttbblv','ttbll']
                break
        ## Check modifications to lepontic categorization
        if CAT_OUT == 'LepLoA': CAT_INS.remove('WlvLo')
        if CAT_OUT == 'LepHiA': CAT_INS.append('WlvLo')
        if CAT_OUT == 'LepLoB': CAT_INS.remove('ttblv')
        if CAT_OUT == 'LepHiB': CAT_INS.append('ttblv')
        if CAT_OUT == 'LepLoC': CAT_INS.append('WlvHi')
        if CAT_OUT == 'LepHiC': CAT_INS.remove('WlvHi')
        if CAT_OUT == 'LepLoD': CAT_INS.append('ttbblv')
        if CAT_OUT == 'LepHiD': CAT_INS.remove('ttbblv')
        if CAT_OUT == 'LepLoE': CAT_INS.append('ttbll')
        if CAT_OUT == 'LepHiE': CAT_INS.remove('ttbll')
        if CAT_OUT == 'LepLoF': CAT_INS.append('Zll')
        if CAT_OUT == 'LepHiF': CAT_INS.remove('Zll')
        if CAT_OUT == 'LepLoG': CAT_INS.append('ZvvHi')
        if CAT_OUT == 'LepHiG': CAT_INS.remove('ZvvHi')
        if CAT_OUT == 'LepLoH': CAT_INS.remove('ZvvLo')
        if CAT_OUT == 'LepHiH': CAT_INS.append('ZvvLo')
    ## End conditional: if CAT_OUT.startswith('Lep')
    elif CAT_OUT.endswith('Incl'):
        CAT_INS = [CAT_OUT.replace('Incl','')+sub for sub in ['Lo','Hi']]
    for cat in CAT_INS:
        CATS_IN[cat] = {}
        CATS_IN[cat]['sigs'] = [sig+'toaato4b' for sig in LEPSIGS]
        CATS_IN[cat]['dir']  = IN_DIR+cat
        if cat.startswith('Zll') or cat.startswith('ttbll'):
            CATS_IN[cat]['bkgs'] = ['Zll','ZZ','TT2l','STop_tW_12l','STbar_tW_12l','MC']  ## Put 'MC' at the end!
        elif cat.startswith('Wlv') or (cat.startswith('tt') and cat.endswith('lv')):
            CATS_IN[cat]['bkgs'] = ['Zll','ZZ','Wlv','TT1l','TT2l','ST_s_1l','STop_t','STbar_t','STop_tW_12l','STbar_tW_12l','MC']
        elif cat.startswith('Zvv'):
            CATS_IN[cat]['bkgs'] = ['QCD_BGen','QCD_bEnr','QCD_Incl','Wqq','Zqq','TT0l','TT1l','Zll','Wlv','ST_s_1l','STop_t','STbar_t','STop_tW_12l','STbar_tW_12l','WW','WZ','ZZ','MC']
        else:
            assert False, 'Category %s not a valid leptonic category!!! Quitting.' % cat
## End conditional: elif IS_LEP
else:
    assert False, '\nERROR!!! Specify valid CAT_OUT in merge_file_script_mctoy.py! (%s is invalid.)\n' % CAT_OUT


## For use as input to Haa4b_makeMCtoy.py
OUT_DIR = IN_DIR+'2D_in_merged_'+CAT_OUT+'/'
## For use as input to htoaato4b_mctoy.py
OUT_DIRS = {}
for cat in [CAT_OUT]+CAT_INS:
    OUT_DIRS[cat] = EOS_DIR+'/plots/'+YEAR+'/'+DATE+'/'+cat+'/'


def main():

    print('\nInside HtoAA_2DAlphabet_merge_inputs\n')

    print('\n\nWARNING!!! Should run from inside 2DAlphabet/CMSSW_11_3_4/src/2DAlphabet/')
    print('to avoid "list is accessing an object already deleted" error! - AWB 2024.06.24\n')
    print('See https://root-forum.cern.ch/t/error-in-tlist-clear-a-list-is-accessing-an-object-already-deleted-list-name-tlist-when-opening-a-file-created-by-root-6-30-using-root-6-14-09/57588/1')
    

    if not PRINTONLY:
        print('\nDeleting any existing output directories, and creating empty ones:')
        for o_dir in [OUT_DIR]+[OUT_DIRS[cat] for cat in [CAT_OUT]+CAT_INS]:
            print(o_dir)
            if os.path.exists(o_dir):
                shutil.rmtree(o_dir)
            os.makedirs(o_dir)

    h_outs = {}  ## Save summed output histograms
    h_ins  = {}  ## Also save the inputs (keeps naming scheme consistent)
    for cat in CAT_INS:
        if PRINTONLY: print('\n\n******* Category %s *******\n' % cat)
        ## Save quantities for S/B and S/sqrt(B) estimates
        data_pass,data_fail,data_fail_win,sig_pass,sig_pass_win = 0,0,0,0,0

        samps = ['Data']
        if cat.startswith('VBFjj') and YEAR == '2018':
            samps = ['JetHT_Run2018%s' % era for era in ['A','B','C','D']]
        for bkg in CATS_IN[cat]['bkgs']:
            samps.append(bkg)
        samps.append('SumMC')  ## Summed background MC
        for mA in MASSESA:
            for sig in CATS_IN[cat]['sigs']:
                samps.append(sig+'_mA_'+mA)
            samps.append('SumHtoaato4b_mA_'+mA)
        for sampIn in samps:
            samp = sampIn
            if cat.startswith('VBFjj') and sampIn.startswith('JetHT'):
                samp = 'Data'
            for wp in WP_CUTS:
                if cat.startswith('VBFjj'):
                    in_file_str = CATS_IN[cat]['dir']+'/analyze_htoaa_stage1.root'
                elif IS_LEP and not cat.startswith('Zvv'):
                    in_file_str = CATS_IN[cat]['dir']+'/%s/%s_%s_%s.root' % (wp, cat, samp, YEAR)
                else:
                    in_file_str = CATS_IN[cat]['dir']+'/%s_%s_%s.root' % (cat, samp, YEAR)
                in_file = None
                ## SumHtoaato4b and SumMC are constructed on the fly
                if not samp.startswith('Sum'):
                    if VERBOSE or (samp == 'Data' and not PRINTONLY):
                        print('\n*******\nReading from %s' % in_file_str)
                    in_file = R.TFile(in_file_str, 'open')

                for mHr in MHREGS:
                    if PRINTONLY and mHr != 'pnet': continue
                    for mAr in MAREGS:
                        if PRINTONLY and mAr != '34a': continue
                        for pf in ['Pass', 'Fail']:
                            h_in_name_read  = '%s_%s_%s_%s_%s_%s_%s_Nom' % (cat, samp, YEAR, mHr, mAr, wp, pf)
                            h_in_name_write = h_in_name_read
                            if cat.startswith('VBFjj'):
                                ## Translate VBFjj naming convention to standard naming convention. Example:
                                ## hLeadingFatJetPNet_massH_v2b_vs_34massAa_VBFHi_Xto4bv2_SRWP40_Nom
                                mHr1 = 'Mass' if mHr == 'mass' else ('MSoftDrop' if mHr == 'msoft' else ('PNet_massH_v2b' if mHr == 'pnet' else 'Invalid'))
                                mAr1 = '34massAa' if mAr == '34a' else ('34massAd' if mAr == '34d' else ('massAa' if mAr == '4a' else 'Invalid'))
                                cat1 = 'VBFHi' if cat == 'VBFjjHi' else ('VBFLo' if cat == 'VBFjjLo' else 'Invalid')
                                pf1 = 'SR' if pf == 'Pass' else ('SB' if pf == 'Fail' else 'Invalid')
                                nom1 = 'noweight' if sampIn.startswith('JetHT') else 'Nom'
                                h_in_name_read = 'evt/%s/hLeadingFatJet%s_vs_%s_%s_Xto4bv2_%s%s_%s' % (sampIn, mHr1, mAr1, cat1, pf1, wp, nom1)
                            ## End conditional: if cat.startswith('VBFjj')

                            ## Get sums from previously accessed and saved histograms
                            if samp == 'SumMC':
                                xBkg = CATS_IN[cat]['bkgs'][0]  ## First background MC component
                                h_in = h_ins[h_in_name_write.replace('SumMC',xBkg)].Clone('SumMC')
                                for iBkg in CATS_IN[cat]['bkgs'][1:]:
                                    if iBkg != 'MC' and iBkg != 'SumMC':
                                        h_in.Add(h_ins[h_in_name_write.replace('SumMC',iBkg)])
                            elif samp.startswith('SumHtoaato4b'):
                                xSig = CATS_IN[cat]['sigs'][0]  ## First signal component
                                h_in = h_ins[h_in_name_write.replace('SumHtoaato4b',xSig)].Clone('SumHtoaato4b')
                                for iSig in CATS_IN[cat]['sigs'][1:]:
                                    h_in.Add(h_ins[h_in_name_write.replace('SumHtoaato4b',iSig)])
                            else: ## Standard behavior: get histogram from input file
                                if VERBOSE: print('\nGetting histogram %s' % h_in_name_read)
                                h_in = in_file.Get(h_in_name_read)
                                if VERBOSE: print('  * Integral = %.1f' % h_in.Integral())

                            h_out_name = '%s_%s_%s_%s_%s_%s_%s_Nom' % (CAT_OUT, samp, YEAR, mHr, mAr, wp, pf)
                            if not (h_in_name_write in h_ins.keys()):
                                h_ins[h_in_name_write] = h_in.Clone(h_in_name_write)
                                if VERBOSE: print('Cloned %s into %s' % (h_in_name_read, h_ins[h_in_name_write].GetName()))
                            elif cat.startswith('VBFjj') and samp == 'Data':
                                h_ins[h_in_name_write].Add(h_in)
                                if VERBOSE: print('Added %s into %s' % (h_in_name_read, h_ins[h_in_name_write].GetName()))
                            else:
                                assert False, '\nERROR!!! Trying to add %s to existing %s! Quitting.' % (h_in_name_read, h_in_name_write)
                            if VERBOSE: print('  * Integral = %.1f' % h_ins[h_in_name_write].Integral())
                            h_ins[h_in_name_write].SetDirectory(0) ## Save locally
                        
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
                                                                                             h_in_name_read, nXi, nYi))
                                    print('Spanning [%.1f-%.1f] x [%.1f-%.1f] vs. [%.1f-%.1f] x [%.1f-%.1f]' % (xLo, xHo, yLo, yHo,
                                                                                                                xLi, xHi, yLi, yHi))
                                    sys.exit()
                                else:
                                    h_outs[h_out_name].Add(h_in)
                                    if VERBOSE: print('  * Integral = %.1f' % h_outs[h_out_name].Integral())

                            nXi = h_in.GetNbinsX()
                            nYi = h_in.GetNbinsY()
                            iXw = [ii+1 for ii in range(nXi) if h_in.GetXaxis().GetBinLowEdge(ii+1) == 110][0]
                            jXw = [ii for ii in range(nXi) if h_in.GetXaxis().GetBinLowEdge(ii+1) == 140][0]
                            if (wp == 'WP40') or (not 'WP40' in WP_CUTS):
                                if samp == 'Data':
                                    print('Adding to data: %s (%s)' % (samp, h_in_name_read))
                                    if pf == 'Pass':
                                        data_pass += h_in.Integral()
                                    if pf == 'Fail':
                                        data_fail += h_in.Integral()
                                        data_fail_win += h_in.Integral(iXw, jXw, 1, nYi)
                                if 'Htoaato4b' in samp and '_mA_30' in samp and not 'SumH' in samp:
                                    if pf == 'Pass':
                                        print('Adding to sig: %s (%s)' % (samp, h_in_name_read))
                                        sig_pass += h_in.Integral()
                                        sig_pass_win += h_in.Integral(iXw, jXw, 1, nYi)
                            ## End conditional: if (wp == 'WP40') or (not 'WP40' in WP_CUTS)

                            if PRINTONLY and not 'Htoaato4b' in samp and (samp == 'Data' or wp == 'WP60'):
                                print('%s %s %s integral = %.2f' % (wp, pf, samp, h_in.Integral()))
                                if h_in.GetMaximum() > 0.10*h_in.Integral() or samp == 'MC' or samp == 'SumMC':
                                    print('  - Max = %.2f (%.1f%%)' % (h_in.GetMaximum(), 100*h_in.GetMaximum()/h_in.Integral()))
                        ## End loop: for pf in ['Pass', 'Fail']
                    ## End loop: for mAr in MAREGS
                ## End loop: for mHr in MHREGS
                if not samp.startswith('Sum'):
                    in_file.Close()

                if PRINTONLY: continue

                ## Common output ROOT file with all histograms (input to Haa4b_makeMCtoy.py)
                out_file_str = OUT_DIR+('%s_%s_%s.root' % (CAT_OUT, samp, YEAR))
                root_cmd = ('update' if os.path.exists(out_file_str) else 'recreate')
                out_file = R.TFile(out_file_str, root_cmd)
                ## ROOT file with only merged category histograms (input to htoaato4b_mctoy.py)
                out_file_str2 = OUT_DIRS[CAT_OUT]+('%s_%s_%s.root' % (CAT_OUT, samp, YEAR))
                root_cmd2 = ('update' if os.path.exists(out_file_str2) else 'recreate')
                out_file2 = R.TFile(out_file_str2, root_cmd2)
                if cat != CAT_OUT:
                    ## ROOT file with only individual category histograms (input to htoaato4b_mctoy.py)
                    out_file_str3 = OUT_DIRS[cat]+('%s_%s_%s.root' % (cat, samp, YEAR))
                    root_cmd3 = ('update' if os.path.exists(out_file_str3) else 'recreate')
                    out_file3 = R.TFile(out_file_str3, root_cmd3)

                if VERBOSE or 'Data' in out_file_str:
                    print('\n*******\nWriting to %s' % out_file_str)
                    print('(Also to %s)' % out_file_str2)
                    if cat != CAT_OUT:
                        print('(Also to %s)' % out_file_str3)

                for mHr in MHREGS:
                    for mAr in MAREGS:
                        for pf in ['Pass', 'Fail']:
                            ## Write out individual input histograms
                            h_in_name = '%s_%s_%s_%s_%s_%s_%s_Nom' % (cat, samp, YEAR, mHr, mAr, wp, pf)
                            out_file.cd()
                            h_ins[h_in_name].Write()
                            if cat != CAT_OUT:
                                out_file3.cd()
                                h_ins[h_in_name].Write()
                            if VERBOSE: print('Wrote out %s' % h_in_name)
                            if VERBOSE: print('  * Integral = %.1f' % h_ins[h_in_name].Integral())
                            ## Write out summed output histogram (overwrite if needed)
                            h_out_name = '%s_%s_%s_%s_%s_%s_%s_Nom' % (CAT_OUT, samp, YEAR, mHr, mAr, wp, pf)
                            out_file.cd()
                            h_outs[h_out_name].Write('', R.TObject.kOverwrite)
                            out_file2.cd()
                            h_outs[h_out_name].Write('', R.TObject.kOverwrite)
                            if VERBOSE: print('Wrote out %s' % h_out_name)
                            if VERBOSE: print('  * Integral = %.1f' % h_outs[h_out_name].Integral())
                        ## End loop: for pf in ['Pass', 'Fail']
                    ## End loop: for mAr in MAREGS
                ## End loop: for mHr in MHREGS
                out_file.Write()
                out_file.Close()
                out_file2.Write()
                out_file2.Close()
                if cat != CAT_OUT:
                    out_file3.Write()
                    out_file3.Close()
            ## End loop: for wp in WP_CUTS
        ## End loop: for samp in samps

        if data_pass == 0:
            print('Very weird!!! %s data_pass = 0! Setting to 1.' % cat)
            data_pass = 1.0
        data_pass_win = data_fail_win*(data_pass/data_fail)
        print('\n%s Data pass/fail = %d/%d (%.1f%%), est. %.1f in Higgs window (%.1f%%)' % (cat, data_pass, data_fail, 100*data_pass/data_fail, data_pass_win, 100*data_pass_win/data_pass))
        print('30 GeV Signal pass = %.1f, %.1f in window (%.1f%%)' % (sig_pass, sig_pass_win, 100*sig_pass_win/sig_pass))
        print('S/B = %.2f, S/sqrt(B) = %.2f\n' % (sig_pass_win/data_pass_win, sig_pass_win/math.sqrt(data_pass_win)))

    ## End loop: for cat in CAT_INS

    print('\n\nAll done!')
    
## End function: def main()


if __name__ == '__main__':
    main()

