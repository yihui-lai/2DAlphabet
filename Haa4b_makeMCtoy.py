## From https://github.com/bouchamaouihichem/2DAlphabet/blob/master/Haa4b_makeMCtoy.py

import os
import sys
import glob
import shutil
import json
import ROOT as R
import numpy as np

R.gROOT.SetBatch(True)

VERBOSE  = False
VVERBOSE = False
VVVERBOSE = False
DELETE_OLD = True  ## Remove old files
TEST = False  ## Append '_test' to outputs
CAT = str(sys.argv[1])  ## gg0lIncl/Hi/Lo, VBFjjIncl/Hi/Lo, LepHi/Lo
CATL = CAT  ## Modified category name
NTOYS    = int(sys.argv[2])
TOYSOURCE = str(sys.argv[3]) ## MC, Data, DataAndMC, None
SMOOTH_CUT = 2.0  ## Largest allowed fluctation in smoothed background (in standard deviations)
MHREG   = 'pnet'
MAREG   = '34a'
MASSESA = ['12']+[str(mA*5) for mA in range(3,13)]
SIGINJ = {}
for mA in MASSESA:  ## Signal to inject, in 1/1000ths
    if   int(mA) <= 20: SIGINJ[mA] = [20]  ## [5, 10, 20, 50]
    elif int(mA) <= 40: SIGINJ[mA] = [50]  ## [10, 20, 50, 100]
    else:               SIGINJ[mA] = [100] ## [10, 20, 50, 100, 200]
YEAR = '2018'
DATE = '2025_06_03'
eos_from_config = [eos for eos in (open('config/user.config','r')).readlines() if eos.startswith('EOS_DIR=')]
EOS_DIR = eos_from_config[0].replace('EOS_DIR=','').replace('\n','')
PLOT_DIR_IN = EOS_DIR+'/plots/'+YEAR+'/'+DATE+'/'+CAT
PLOT_DIR = PLOT_DIR_IN+('_test' if TEST else '')
JSON_DIR = 'jsons/toys/'+YEAR+'/'+DATE+'/'+CAT+('_test' if TEST else '')
DMs = ['Data','MC']
PFs = ['Pass','Fail']

## Set toy options
doToysMC   = (TOYSOURCE == 'MC' or TOYSOURCE == 'DataAndMC')
doToysData = (TOYSOURCE == 'Data' or TOYSOURCE == 'DataAndMC')
if not (doToysMC or doToysData or TOYSOURCE == 'None'):
    print('\n\nHaa4b_makeMCtoy.py bad option! TOYSOURCE = %s. Quitting.\n')
    sys.exit()
## Check for output directory
if not os.path.exists(PLOT_DIR_IN):
    print('\n\nHaa4b_makeMCtoy.py error! '+PLOT_DIR_IN+' does not exist. Run merge_file_script_mctoy.py first.\n')
    sys.exit()
## Make sub-directories for output toy ROOT and JSON files
if not os.path.exists(PLOT_DIR+'/toys'):
    os.system('mkdir -p '+PLOT_DIR+'/toys')
if not os.path.exists(JSON_DIR):
    os.system('mkdir -p '+JSON_DIR)
if not os.path.exists(EOS_DIR+'/'+JSON_DIR):
    os.system('mkdir -p '+EOS_DIR+'/'+JSON_DIR)

###################
## Helper functions
###################

## Get effective per-event weight for MC histogram given per-bin uncertainties
def get_eff_weight(hist):
    nX = hist.GetNbinsX()
    nY = hist.GetNbinsY()
    sum_sq_E = 0
    for iX in range(1,nX+1):
        for iY in range(1,nY+1):
            sum_sq_E += pow(hist.GetBinError(iX,iY), 2)
    eff_wgt = max(sum_sq_E, 1) / max(hist.Integral(), 1)
    if VERBOSE: print('\nget_eff_weight: %dx%d %s has integral %.1f, sum err^2 = %.1f, effective weight %.3f' % 
                      (nX, nY, hist.GetName(), hist.Integral(), sum_sq_E, eff_wgt))
    return eff_wgt
## End function: get_eff_weight(hist)


## Scale histogram to reference histogram yield
def scale_to_ref(hist, ref_hist):
    SF = ref_hist.Integral() / hist.Integral()
    print('Scaling %s by %.3f to match %s (%.1f to %.1f)' % (hist.GetName(), SF, ref_hist.GetName(),
                                                             hist.Integral(), ref_hist.Integral()))
    hist.Scale(SF)
    return hist
## End function: scale_to_ref(hist, ref_hist)


## Reset per-bin uncertainties based on a reference histogram
def reset_bin_errors(hist_in, hist_ref, eff_wgt=None):
    nX = hist_in.GetNbinsX()
    nY = hist_in.GetNbinsY()
    if not eff_wgt: eff_wgt = get_eff_weight(hist_ref)
    for iX in range(1, nX+1):
        for iY in range(1, nY+1):
            ## Reset negative bins to 0
            if hist_in.GetBinContent(iX,iY) < 0.0:
                hist_in.SetBinContent(iX,iY, 0.0)
            val_in  = hist_in.GetBinContent(iX,iY)
            val_ref = hist_ref.GetBinContent(iX,iY)
            err_in  = hist_in.GetBinError(iX,iY)
            err_ref = hist_ref.GetBinError(iX,iY)
            ## Estimate per-bin error as sqrt(N)*wgt, where N is effective MC statistics, and we set N >= 1
            err_in_est = np.sqrt(max(1.0, val_in/eff_wgt))*eff_wgt
            err_ref_est = np.sqrt(max(1.0, val_ref/eff_wgt))*eff_wgt
            err_in_scale = max(val_in, eff_wgt) / max(val_ref, eff_wgt)
            hist_in.SetBinError(iX,iY, max(err_in, max(err_in_est, err_ref_est*err_in_scale)))
            if VVVERBOSE and err_in_est > err_in*1.5 and val_in > eff_wgt:
                print('%s %d,%d = %.3f +/- %.3f, but effective weight %.3f; setting error to %.3f' %
                      (hist_in.GetName(), iX, iY, val_in, err_in, eff_wgt, err_in_est))
        ## End loop: for iY in range(1, nY+1)
    ## End loop: for iX in range(1, nX+1)
    return hist_in
## End function: reset_bin_errors(hist_in, hist_ref, eff_wgt=None)


## Round bin values, rebinning until rounded integral approximates original integral
def round_bins(h_float, h_round):
    if h_float.GetNbinsX() != h_round.GetNbinsX() or h_float.GetNbinsY() != h_round.GetNbinsY():
        print('\nh_float and h_round have different binning!!! Quitting.\n')
        sys.exit()
    nX = h_float.GetNbinsX()
    nY = h_float.GetNbinsY()

    ## First just round all bins
    h_round.Scale(0)
    for iX in range(1, nX+1):
        for iY in range(1, nY+1):
            h_round.SetBinContent(iX, iY, np.round(h_float.GetBinContent(iX,iY)))
    ## Now subtract rounded histogram from original floating point histogram
    h_remain = h_float.Clone("h_remain")
    h_remain.Add(h_round, -1)

    ## Iteratively rebin, distributing the remainder until it is < 1% of total
    frac_err = h_remain.Integral() / h_float.Integral()
    rebin = 2
    while(abs(frac_err) > 0.01 and abs(h_remain.Integral()) > 1.5 and rebin <= np.floor(nX/2.0) and rebin <= np.floor(nY/2.0)):
        if VERBOSE or (not '_sigBr_' in h_float.GetName()):
            print('\n%s off by factor of %.3f (%.1f events), will rebin by %d' % (h_round.GetName(), -1*frac_err, -1*h_remain.Integral(), rebin))
        ## Loop over "rebinned" bins
        for jX in range(1, int(np.ceil(1.0*nX/rebin))+1):
            for jY in range(1, int(np.ceil(1.0*nY/rebin))+1):
                ## Get center-weighted coordinate from original bins
                cwX = 0
                cwY = 0
                yld = 0
                wgt = 0
                for iiX in range((jX-1)*rebin+1, min(jX*rebin, nX)+1):
                    for iiY in range((jY-1)*rebin+1, min(jY*rebin, nY)+1):
                        iYld = h_remain.GetBinContent(iiX,iiY)
                        yld += iYld
                        wgt += (0.5+iYld)
                        cwX += (0.5+iYld)*h_remain.GetXaxis().GetBinCenter(iiX)
                        cwY += (0.5+iYld)*h_remain.GetYaxis().GetBinCenter(iiY)
                ## If at least +/-0.5 total events, assign 1 event to weighted center
                if abs(yld) > 0.5:
                    diff = 1 if yld > 0 else -1
                    if wgt <= 0:
                        print('\n\nRebinned %s bin %d,%d with factor %d has wgt = %.9f!!! Quitting.' % (h_flot.GetName(), jX, jY, rebin, wgt))
                        sys.exit()
                    cX = h_remain.GetXaxis().FindBin(cwX / wgt)
                    cY = h_remain.GetYaxis().FindBin(cwY / wgt)
                    ## If subtracting from a 0 bin, find nearby non-0 bin
                    if diff < 0 and h_round.GetBinContent(cX,cY) == 0:
                        dist = pow(nX,2) + pow(nY,2)
                        cXp,cYp = -1,-1
                        for iiiX in range((jX-1)*rebin+1, min(jX*rebin, nX)+1):
                            for iiiY in range((jY-1)*rebin+1, min(jY*rebin, nY)+1):
                                if h_round.GetBinContent(iiiX,iiiY) > 0 and pow(cX-iiiX,2) + pow(cY-iiiY,2) < dist:
                                    dist = pow(cX-iiiX,2) + pow(cY-iiiY,2)
                                    cXp = iiiX
                                    cYp = iiiY
                        if cXp > 0 and cYp > 0:
                            cX = cXp
                            cY = cYp
                    ## Don't subtract from 0 bins
                    if diff > 0 or h_round.GetBinContent(cX,cY) > 0:
                        if VERBOSE:
                            print('  * Changing bin %d,%d by %d' % (cX, cY, diff))
                            print('    Averaged over (%d,%d)x(%d,%d)' % ((jX-1)*rebin+1, min(jX*rebin, nX), (jY-1)*rebin+1, min(jY*rebin, nY)))
                        h_round.SetBinContent(cX,cY, h_round.GetBinContent(cX,cY)+diff)
                        h_remain.SetBinContent(cX,cY, h_remain.GetBinContent(cX,cY)-diff)
                ## End conditional: if abs(yld) > 0.5
            ## End loop: for jY in range(1, int(np.ceil(1.0*nX/rebin))+1)
        ## End loop: for jY in range(1, int(np.ceil(1.0*nX/rebin))+1)
        frac_err = h_remain.Integral() / h_float.Integral()
        rebin += 1
    ## End conditional: while(abs(frac_err) > 0.01)

    ## Finally set rounded bin errors
    for iX in range(1, nX+1):
        for iY in range(1, nY+1):
            h_round.SetBinError(iX, iY, np.sqrt(h_round.GetBinContent(iX,iY)))

    del h_remain
    return h_round
## End function: round_bins(h_float, h_round)


## Compute distance-weighted average of nearby bins, with or without the bin itself
def compute_avg_occ_and_err(hist, dBin, iX, iY, incl_bin, dist_wgt):
    nX = hist.GetNbinsX()
    nY = hist.GetNbinsY()
    iXlo = max(1,iX-dBin)
    iXhi = min(nX,iX+dBin)
    iYlo = max(1,iY-dBin)
    iYhi = min(nY,iY+dBin)
    sum_occ,sum_err,sum_area = 0,0,0
    for iiX in range(iXlo,iXhi+1):
        for iiY in range(iYlo,iYhi+1):
            if iiX != iX or iiY != iY or incl_bin:
                dist_sq = (max(pow(iX-iiX,2) + pow(iY-iiY,2), 0.5) if dist_wgt else 1.0)
                sum_area += (1.0 / dist_sq)
                sum_occ  += hist.GetBinContent(iiX,iiY) / dist_sq
                sum_err  += pow(hist.GetBinError(iiX,iiY), 2) / dist_sq

    return [sum_occ / sum_area, np.sqrt(sum_err) / sum_area]
## End function: compute_avg_occ_and_err(hist, dBin, iX, iY, incl_bin, dist_wgt)


## Compute average difference of bins to average of bins, weighting by distance to iX,iY
def compute_avg_diff(hist, dBin, iX, iY, incl_bin, dist_wgt, avg):
    nX = hist.GetNbinsX()
    nY = hist.GetNbinsY()
    iXlo = max(1,iX-dBin)
    iXhi = min(nX,iX+dBin)
    iYlo = max(1,iY-dBin)
    iYhi = min(nY,iY+dBin)
    sum_sq_diff,sum_area = 0,0
    for iiX in range(iXlo,iXhi+1):
        for iiY in range(iYlo,iYhi+1):
            if iiX != iX or iiY != iY or incl_bin:
                dist_sq = (max(pow(iX-iiX,2) + pow(iY-iiY,2), 0.5) if dist_wgt else 1.0)
                sum_area += (1.0 / dist_sq)
                sum_sq_diff += pow(hist.GetBinContent(iiX,iiY) - avg, 2) / dist_sq
    return np.sqrt(sum_sq_diff / sum_area)
## End function: compute_avg_diff(hist, dBin, iX, iY, incl_bin, dist_wgt, avg)


## Compute maximum bin "pull" w.r.t. nearby bins, to decide whether further smoothing is needed
def compute_max_pull(hist, dBin, eff_wgt=None):
    nX = hist.GetNbinsX()
    nY = hist.GetNbinsY()
    max_pull,mX,mY,mAvg,mArea = 0,0,0,0,0
    if not eff_wgt: eff_wgt = get_eff_weight(hist)
    for iX in range(1,nX+1):
        for iY in range(1,nY+1):
            ## Ignore "corner cases", which don't get smoothed
            if min(iX-1, nX-iX) + min(iY-1, nY-iY) <= 1:
                continue
            val = hist.GetBinContent(iX,iY)
            iXlo = max(1,iX-dBin)
            iXhi = min(nX,iX+dBin)
            iYlo = max(1,iY-dBin)
            iYhi = min(nY,iY+dBin)
            ## Compute average occupancy as minimum of 1 MC event in area around bin, weighted by distance
            avg = compute_avg_occ_and_err(hist, dBin, iX, iY, False, True)[0]
            avg = max(avg, (eff_wgt / pow(1+2*dBin, 2)))
            ## Estimate pull in standard deviations, with average difference weighted by distance
            ## Minimum "sigma" is 10% of sqrt of max bin occupancy
            sigma = compute_avg_diff(hist, dBin, iX, iY, False, True, avg)
            sigma = max(sigma, 0.1*np.sqrt(hist.GetMaximum()))
            pull = (val - avg) / sigma
            if abs(pull) > max_pull:
                max_pull = abs(pull)
                mX = iX
                mY = iY
                mAvg = avg
                mArea = (iXhi-iXlo+1)*(iYhi-iYlo+1)

    print('\ncompute_max_pull: %s bin %d,%d has yield %.3f vs. %.3f avg from %d nearby bins (pull = %.1f)' %
          (hist.GetName(), mX, mY, hist.GetBinContent(mX,mY), mAvg, mArea, max_pull))
    if VVERBOSE:
        for iiX in range(max(1,mX-dBin), min(nX,mX+dBin)+1):
            for iiY in range(max(1,mY-dBin), min(nY,mY+dBin)+1):
                print('  - %d,%d = %.4f+/-%.4f' % (iiX, iiY, hist.GetBinContent(iiX,iiY), hist.GetBinError(iiX,iiY)))
    return max_pull
## End function: compute_max_pull(hist, dBin, eff_wgt=None)


## For bins with high uncertainty, use local regional average to compute expectation
def get_bin_expectation(hist, iX, iY, eff_wgt=1.0):
    val = hist.GetBinContent(iX,iY)
    err = hist.GetBinError(iX,iY)
    if (val > err):
        return [val, err]
    if VERBOSE and (VVERBOSE or val > eff_wgt) and (err > val):
        print('\nget_bin_expectation: %s bin %d,%d = %.3f +/- %.3f' %
              (hist.GetName(), iX, iY, val, err))
    ## Maximum average over 5x5, or up to 4 bins away (for corners)
    dBin = 0
    area = 1
    val_old = val
    while(err > val and area < 25 and dBin < 4):
        dBin += 1
        area = (min(iX+dBin, hist.GetNbinsX()) - max(iX-dBin, 1) + 1)*(min(iY+dBin, hist.GetNbinsY()) - max(iY-dBin, 1) + 1)
        occ_and_err = compute_avg_occ_and_err(hist, dBin, iX, iY, True, True)
        val = occ_and_err[0]
        err = occ_and_err[1]
        if VERBOSE and (VVERBOSE or val_old > eff_wgt): print('  - Avg %d bins, now %.3f +/- %.3f' % (area, val, err))
    ## End conditional: while(err > val and area < 25)
    return [val, err]
## End function: get_bin_expectation(hist, iX, iY, eff_wgt)


## Function to generate toys
def toys_generator(hist, nToy, output_dir, root_cmd, h_sigs={}, PF=None):
    if VERBOSE: print('\ntoys_generator: Throwing %d toys from %s' % (nToy, hist.GetName()))
    str_repl = None
    for substr in ['_MCsmooth1_','_MCsmooth2_','_Datasmooth1_','_Datasmooth2_']:
        if substr in hist.GetName():
            str_repl = substr
            break
    if str_repl == None:
        print('\n\nWhy are you throwing toys from non-smoothed MC or Data?!? Quitting.\n')
        sys.exit()
    
    ## Create histogram to save average of toys and their variance squared
    avg_toy_hist = hist.Clone(hist.GetName().replace(str_repl, str_repl+'%dtoyAvg_' % nToy))
    avg_toy_hist.Scale(0)
    avg_toy_varSq = avg_toy_hist.Clone(avg_toy_hist.GetName().replace('toyAvg','toyVarSq'))
    avg_toy_hist_sig = {}
    for mA in h_sigs.keys():
        for sInj in SIGINJ[mA]:
            key = 'mA_%s_sigBr_%03d' % (mA, sInj)
            avg_toy_hist_sig[key] = avg_toy_hist.Clone(avg_toy_hist.GetName().replace('toyAvg', 'toyAvg_%s' % key))

    ## Loop and generate the toys
    for iT in range(nToy):
        filename = hist.GetName().split('_'+WP)[0].replace(str_repl, str_repl+'toy%d_' % iT)
        ## Create new ROOT file (root_cmd = "RECREATE"), or add to existing ("UPDATE")
        output_file = R.TFile(output_dir+"/"+filename+".root", root_cmd)
        out_file_sig = {}
        for key in avg_toy_hist_sig.keys():
            out_file_sig[key] = R.TFile(output_file.GetName().replace('toy%d' % iT, 'toy%d_%s' % (iT, key)), root_cmd)
        if iT == 0:
            print('Writing %s toy #%d to %s' % (PF, iT, output_dir+"/"+filename+".root"))
        if (iT % int(np.sqrt(nToy))) == 0:
            print('  - Starting toy %d/%d' % (iT, nToy))
        toy_hist = hist.Clone(hist.GetName().replace(str_repl, str_repl+'toy%d_' % iT))
        toy_hist_sig = {}
        for key in avg_toy_hist_sig.keys():
            toy_hist_sig[key] = toy_hist.Clone(toy_hist.GetName().replace('toy%d' % iT, 'toy%d_%s' % (iT, key)))
        for iX in range(1, hist.GetNbinsX()+1):
            for iY in range(1, hist.GetNbinsY()+1):
                expected = hist.GetBinContent(iX,iY)
                #print('Histogram %s bin (%d,%d) = (%.1f,%.1f) has expected %.3f' % (hist.GetName(), iX, iY, hist.GetXaxis().GetBinCenter(iX), hist.GetYaxis().GetBinCenter(iY), expected))
                fluctuated = np.random.poisson(expected)
                toy_hist.SetBinContent(iX,iY,fluctuated)
                toy_hist.SetBinError(iX,iY,np.sqrt(fluctuated))
                for key in toy_hist_sig.keys():
                    mA = key[3:5]
                    sBr = int(key[-3:])*0.001
                    assert (mA in MASSESA and int(key[-3:]) in SIGINJ[mA]), 'Haa4b_makeMCtoy.py: mA = %s, sBr = %d' % (mA, sBr)
                    exp_sig = expected + h_sigs[mA][PF].GetBinContent(iX,iY)*sBr
                    fluc_sig = np.random.poisson(exp_sig)
                    toy_hist_sig[key].SetBinContent(iX,iY,fluc_sig)
                    toy_hist_sig[key].SetBinError(iX,iY,np.sqrt(fluc_sig))
        avg_toy_hist.Add(toy_hist)
        for key in toy_hist_sig.keys():
            avg_toy_hist_sig[key].Add(toy_hist_sig[key])
        output_file.cd()
        toy_hist.Write()
        output_file.Write()
        output_file.Close()
        for key in toy_hist_sig.keys():
            out_file_sig[key].cd()
            toy_hist_sig[key].Write()
            out_file_sig[key].Write()
            out_file_sig[key].Close()
        del toy_hist
        del toy_hist_sig
    ## End loop: for iT in range(nToy)
    avg_toy_hist.Scale(1.0/nToy)
    for key in avg_toy_hist_sig.keys():
        avg_toy_hist_sig[key].Scale(1.0/nToy)

    ## Store variance of toys w.r.t. average
    for jT in range(nToy):
        filename = hist.GetName().split('_'+WP)[0].replace(str_repl, str_repl+'toy%d_' % jT)
        ## Reopen ROOT file with toy
        output_file = R.TFile(output_dir+"/"+filename+".root", "OPEN")
        toy_hist = output_file.Get(hist.GetName().replace(str_repl, str_repl+'toy%d_' % jT))
        ## Get the difference squared
        toy_hist.Add(avg_toy_hist, -1)
        toy_hist.Multiply(toy_hist)
        avg_toy_varSq.Add(toy_hist)
        output_file.Close()
    ## End loop: for jT in range(nToy)
    avg_toy_varSq.Scale(1.0/nToy)

    ## Set error bars of average to variance
    for iX in range(1,avg_toy_hist.GetNbinsX()+1):
        for iY in range(1,avg_toy_hist.GetNbinsY()+1):
            avg_toy_hist.SetBinError(iX,iY,np.sqrt(avg_toy_varSq.GetBinContent(iX,iY)))
            for key in avg_toy_hist_sig.keys():
                ## Estimate signal-injected uncertainty as sqrt(err^2 + avg(sig+bkg) - avg(bkg))
                avg_toy_hist_sig[key].SetBinError(iX,iY,np.sqrt(max(0, avg_toy_varSq.GetBinContent(iX,iY) +
                                                                    avg_toy_hist_sig[key].GetBinContent(iX,iY) -
                                                                    avg_toy_hist.GetBinContent(iX,iY))))

    avg_toy_hist_sig['bkg'] = avg_toy_hist
    avg_toy_hist_sig['bkgVar'] = avg_toy_varSq
    return avg_toy_hist_sig
## End function: toys_generator(hist, nToy, output_dir, root_cmd, h_sigs={}, PF=None)



####################
## Main body of code
####################

print("Running Haa4b_makeMCtoy.py for the following category:", CAT)

## "Super-category" defines hadronic directory / file names
superCat = CAT
for supr in ['gg0l','VBFjj','Vjj','tt0l']:
    if CAT.startswith(supr) and CAT != 'gg0lV':
        superCat = supr+'Incl'
## Most categories used WP60; only gg0l and VBFjj use WP40
WP = 'WP60'
if CAT.startswith('gg0l') or CAT.startswith('VBFjj'):
    WP = 'WP40'
if CAT == 'VVBFjj':
    WP = 'WP4060'

## Different categories use different sets of background samples
samps = ['Data']
sigs = None
if CAT.startswith('Had') or CAT.startswith('gg0l') or ('VBFjj' in CAT) or CAT.startswith('Vjj') or CAT.startswith('tt0l'):
    ## Background MC already summed ('MC') for all categories except VBFjj, which has manual summing ('SumMC')
    samps.append('SumMC' if (('VBFjj' in CAT) or (CAT == 'gg0lV')) else 'MC')
    sigs = ['ggH','VBFH','WH','ZH','ttH','SumH']
    for sig in sigs:
        for mA in MASSESA:
            samps.append(sig+'toaato4b_mA_'+str(mA))

elif CAT.startswith('Lep'):
    if CAT.startswith('LepHi') or CAT.startswith('LepLo'):
        CATL = CAT[0:5]  ## i.e. LepHi or LepLo, without A, B, C ... modification
    elif CAT == 'LepIncl':
        CATL = CAT
    else:
        assert False, '\nInvalid CAT = %s!!! Quitting.' % CAT
    ## Use manual summing ('SumMC') instead of original sum ('MC') in order to drop QCD from Zvv background model
    samps.append('SumMC')
    sigs = ['WH','ZH','ttH','SumH']
    for sig in sigs:
        for mA in MASSESA:
            samps.append(sig+'toaato4b_mA_'+str(mA))

else:
    assert False, '\nInvalid category %s!!! Quitting.' % CAT

print('\nIn Haa4b_makeMCtoy.py, looking for the following samples:')
print(samps)

base_pth_in = '%s/raw_inputs/%s/%s/2D_in_merged_%s/' % (EOS_DIR, YEAR, DATE, superCat)

# step 1, merge bkg MC, set bin errors based on effective yields
h_orig,h_sig = {},{}
for DM in DMs:
    h_orig[DM] = {}
    for PF in PFs: h_orig[DM][PF] = None
for mA in MASSESA:
    h_sig[mA] = {}
    for PF in PFs: h_sig[mA][PF] = None

## Loop over samples to get pass / fail histograms
print(samps)

for samp in samps:
    filepath = base_pth_in+superCat+'_'+samp+'_'+YEAR+'.root'
    print(f"add {filepath}")
    hname_base = CAT+'_'+samp+'_'+YEAR+'_'+MHREG+'_'+MAREG+'_'+WP
    hname = {}
    for PF in PFs: hname[PF] = hname_base+'_'+PF+'_Nom'
    in_file = R.TFile.Open(filepath)

    ## Store signal histograms
    isSignal = False
    for mA in MASSESA:
        if 'Htoaato4b_mA_'+mA in filepath:
            isSignal = True
            ## Write out individual signal component histograms
            out_file_sig = R.TFile('%s/%s_%s_%s_%s_%s.root' % (PLOT_DIR, CAT, samp, YEAR, MHREG, MAREG), 'RECREATE')
            for PF in PFs:
                out_file_sig.cd()
                in_file.Get(hname[PF]).Write()
                if h_sig[mA][PF] == None:
                    h_sig[mA][PF] = in_file.Get(hname[PF])
                    h_sig[mA][PF].SetDirectory(0)
                    for sig in sigs:
                        h_sig[mA][PF].SetName(h_sig[mA][PF].GetName().replace(sig+'toaa','Htoaa'))
                    if VERBOSE: print('  * Creating %s from %s (integral = %.1f)' % (h_sig[mA][PF].GetName(), hname[PF], h_sig[mA][PF].Integral()))
                elif not 'SumH' in hname[PF]:
                    h_sig[mA][PF].Add(in_file.Get(hname[PF]))
                    if VERBOSE: print('  * Adding %s to %s (new integral = %.1f)' % (hname[PF], h_sig[mA][PF].GetName(), h_sig[mA][PF].Integral()))
            ## End loop: for PF in PFs
            out_file_sig.Write()
            out_file_sig.Close()
            del out_file_sig
        ## End conditional: if 'Htoaato4b_mA_'+mA in filepath
    ## End loop: for mA in MASSESA
    if isSignal:
        continue

    h_in = {}
    for PF in PFs: h_in[PF] = in_file.Get(hname[PF])

    ## For WP40 samples (gg0l and VBFjj and VVBFjj), scale background MC WP60 --> WP40
    if (WP == 'WP40' or WP == 'WP4060') and samp != 'Data' and not 'Htoaato4b' in samp:
        for PF in PFs:
            h_in_WP60  = in_file.Get(hname[PF].replace(WP,'WP60'))
            WP40_yield = h_in[PF].Integral()
            h_in[PF].Scale(0)
            h_in[PF].Add(h_in_WP60)
            SF = WP40_yield / h_in_WP60.Integral()
            print('Scaling %s by %.3f from %.1f to %.1f' % (h_in[PF].GetName(), SF, h_in_WP60.Integral(), WP40_yield))
            h_in[PF].Scale(SF)
            del h_in_WP60
        ## End loop: for PF in PFs
    ## End conditional: if (WP == 'WP40' or WP == 'WP4060') and samp != 'Data' and not 'Htoaato4b' in samp

    ## Get the input histograms, sum background MC
    for PF in PFs:
        if samp == 'Data':
            h_orig['Data'][PF] = h_in[PF].Clone(hname[PF])
            h_orig['Data'][PF].SetDirectory(0)
        elif h_orig['MC'][PF] is None:
            h_orig['MC'][PF] = h_in[PF].Clone(hname[PF].replace('_%s_' % samp, '_MC_'))
            h_orig['MC'][PF].SetDirectory(0)
        else:
            h_orig['MC'][PF].Add()
    ## End loop: for PF in PFs
## End loop: for samp in samps

## Scale MC to data
for PF in PFs: h_orig['MC'][PF] = scale_to_ref(h_orig['MC'][PF], h_orig['Data'][PF])

## Set minimum per-bin errors to reflect effective MC event weights
eff_wgt = {}
for DM in DMs: eff_wgt[DM] = {}
for PF in PFs:
    eff_wgt['Data'][PF] = 1.0  ## Effective "weight" of data is 1
    eff_wgt['MC'][PF] = get_eff_weight(h_orig['MC'][PF])
nX = h_orig['MC']['Pass'].GetNbinsX()
nY = h_orig['MC']['Pass'].GetNbinsY()
for PF in PFs:
    h_orig['MC'][PF] = reset_bin_errors(h_orig['MC'][PF], h_orig['MC'][PF], eff_wgt['MC'][PF])
    for DM in DMs:
        if (nX != h_orig[DM][PF].GetNbinsX() or nY != h_orig[DM][PF].GetNbinsY()):
            assert False, '\nERROR!!! %s is %dx%d, %s is not! Quitting.' % (h_orig['MC']['Pass'].GetName(), nX, nY, h_orig[DM][PF].GetName())

## Write h_orig and signal, without smoothing, to ROOT file
out_file_dataMC = R.TFile('%s/%s_%s_%dtoys_Data_MC.root' % (PLOT_DIR, CAT, TOYSOURCE, NTOYS), 'RECREATE')
for PF in PFs:
    for DM in DMs:         h_orig[DM][PF].Write()
    for mA in h_sig.keys(): h_sig[mA][PF].Write()
out_file_dataMC.Write()
out_file_dataMC.Close()

# step 2, smooth, set negative bins to 0, and set errors based on effective yields
h_smooth1,h_smooth2 = {},{}
for DM in DMs:
    h_smooth1[DM],h_smooth2[DM] = {},{}
    for PF in PFs:
        if h_orig[DM][PF] == None:
            assert False, "\n\nERROR!!! h_orig[%s][%s] does not exist! Quitting.\n" % (DM, PF)
        h_smooth1[DM][PF] = None
        h_smooth1[DM][PF] = h_orig[DM][PF].Clone(h_orig[DM][PF].GetName().replace('_%s_' % DM,'_%ssmooth1_' % DM))
        ## Smooth until there are no large statistical variations in 3x3 or 5x5 regions (up to 3 times)
        nSmooth = 0
        while((compute_max_pull(h_smooth1[DM][PF], 1, eff_wgt[DM][PF]) > SMOOTH_CUT or
               compute_max_pull(h_smooth1[DM][PF], 2, eff_wgt[DM][PF]) > SMOOTH_CUT) and nSmooth < 3):
            h_smooth1[DM][PF].Smooth(1)
            h_smooth1[DM][PF] = reset_bin_errors(h_smooth1[DM][PF], h_orig[DM][PF], eff_wgt[DM][PF])
            nSmooth += 1
        print('\nSmoothed %s %d times' % (h_smooth1[DM][PF].GetName(), nSmooth))
        h_smooth1[DM][PF] = scale_to_ref(h_smooth1[DM][PF], h_orig['Data'][PF])

        # Additional manual regional averaging for bins with large uncertainty compared to yields
        h_smooth2[DM][PF] = h_smooth1[DM][PF].Clone(h_smooth1[DM][PF].GetName().replace('smooth1','smooth2'))

        # Loop over bins in 2D distribution
        for iX in range(1, nX+1):
            for iY in range(1, nY+1):
                # Set error using un-smoothed bin error or effective weight (whichever is larger)
                bin_wgt = pow(h_orig[DM][PF].GetBinError(iX,iY),2) / max(eff_wgt[DM][PF], h_orig[DM][PF].GetBinContent(iX,iY))
                bin_wgt = max(bin_wgt, eff_wgt[DM][PF])
                bin_err = np.sqrt(max(1.0, h_smooth1[DM][PF].GetBinContent(iX,iY) / bin_wgt))*bin_wgt
                h_smooth1[DM][PF].SetBinError(iX,iY, bin_err)
                exp = get_bin_expectation(h_smooth1[DM][PF], iX, iY, eff_wgt[DM][PF])
                h_smooth2[DM][PF].SetBinContent(iX,iY, exp[0])
                h_smooth2[DM][PF].SetBinError(iX,iY, exp[1])
            ## End loop: for iY in range(1, nY+1)
        ## End loop: for iX in range(1, nX+1)
        h_smooth2[DM][PF] = scale_to_ref(h_smooth2[DM][PF], h_orig['Data'][PF])

    ## End loop: for PF in PFs
## End loop: for DM in DMs


# Also create rounded integer version for "nominal" pseudo-data
h_rounded,h_rounded_sig = {},{}
for DM in DMs:
    h_rounded[DM],h_rounded_sig[DM] = {},{}
    for PF in PFs:
        h_rounded[DM][PF] = h_smooth2[DM][PF].Clone(h_smooth2[DM][PF].GetName().replace('smooth2','rounded'))
        h_rounded[DM][PF] = round_bins(h_smooth2[DM][PF], h_rounded[DM][PF])

        h_rounded_sig[DM][PF] = {}
        for mA in h_sig.keys():
            for sInj in SIGINJ[mA]:
                key = 'mA_%s_sigBr_%03d' % (mA, sInj)
                h_rounded_sig[DM][PF][key] = h_smooth2[DM][PF].Clone(h_smooth2[DM][PF].GetName().replace('smooth2','rounded_'+key))
                h_rounded_sig[DM][PF][key].Add(h_sig[mA][PF], sInj*0.001)
                h_rounded_sig[DM][PF][key] = round_bins(h_rounded_sig[DM][PF][key].Clone(key+'_'+PF+'_tmp'), h_rounded_sig[DM][PF][key])
            ## End loop: for sInj in SIGINJ[mA]
        ## End loop: for mA in h_sig.keys()
    ## End loop: for PF in PFs
## End loop: for DM in DMs

## Write rounded template to its own "toy" file
for DM in DMs:
    out_round_name = h_rounded[DM]['Pass'].GetName().split('_'+WP)[0]
    out_file_round = R.TFile(PLOT_DIR+'/'+out_round_name+'.root', 'RECREATE')
    for PF in PFs: h_rounded[DM][PF].Write()
    out_file_round.Write()
    out_file_round.Close()
    out_file_round_sig = {}
    for key in h_rounded_sig[DM]['Pass'].keys():
        out_file_round_sig[key] = R.TFile(out_file_round.GetName().replace('rounded','rounded_'+key), 'RECREATE')
        for PF in PFs: h_rounded_sig[DM][PF][key].Write()
        out_file_round_sig[key].Write()
        out_file_round_sig[key].Close()
    del out_file_round
    del out_file_round_sig
## End loop: for DM in DMs


## Generate toys, get average toy occupancy and variance
avg_toy = {}
for DM in DMs:
    avg_toy[DM] = {}
    for PF in PFs: avg_toy[DM][PF] = None
for DM in DMs:
    if (DM == 'MC' and not doToysMC) or (DM == 'Data' and not doToysData):
        continue
    if DELETE_OLD:
        print('\nRemoving all files matching '+PLOT_DIR+'/toys/*'+DM+'smooth2_toy*'+MHREG+'_'+MAREG+'*')
        for fl in glob.glob(PLOT_DIR+'/toys/*'+DM+'smooth2_toy*'+MHREG+'_'+MAREG+'*'):
            os.remove(fl)
    for PF in PFs:
        ROOT_cmd = 'RECREATE' if PF == 'Pass' else 'UPDATE'
        avg_toy[DM][PF] = toys_generator(h_smooth2[DM][PF], NTOYS, PLOT_DIR+'/toys', ROOT_cmd, h_sig, PF)
## End loop: for DM in DMs

## Write h_orig and average toy histograms to ROOT file
out_file_dataMC = R.TFile('%s/%s_%s_%dtoys_Data_MC.root' % (PLOT_DIR, CAT, TOYSOURCE, NTOYS), 'UPDATE')
wrt_hists  = [[h_smooth1[DM][PF] for PF in PFs] for DM in DMs]
wrt_hists += [[h_smooth2[DM][PF] for PF in PFs] for DM in DMs]
wrt_hists += [[h_rounded[DM][PF] for PF in PFs] for DM in DMs]

for DM in DMs:
    if (DM == 'MC' and not doToysMC) or (DM == 'Data' and not doToysData):
        continue
    for key in avg_toy[DM]['Pass'].keys():
        wrt_hists += [[avg_toy[DM][PF][key] for PF in PFs]]

for wrt_hist in wrt_hists:
    if VERBOSE: print('\nIn Haa4b_makeMCtoy_ggH.py, writing %s (and "fail")' % wrt_hist[0].GetName())
    wrt_rebin = {}
    for ii in [0,1]:
        wrt_hist[ii].Write()
        ## Also write rebinned versions and ratios for simpler analysis later
        for rebin in [2,3,4]:
            if ii == 0:
                wrt_rebin[str(rebin)] = [None,None]
            wrt_rebin[str(rebin)][ii] = wrt_hist[ii].Clone(wrt_hist[ii].GetName()+'_rebin%d' % rebin)
            wrt_rebin[str(rebin)][ii].Rebin2D(rebin, rebin)
            wrt_rebin[str(rebin)][ii].Write()
            if ii == 1:
                wrt_hist_ratio = wrt_rebin[str(rebin)][0].Clone(wrt_rebin[str(rebin)][0].GetName().replace('Pass','Ratio'))
                wrt_hist_ratio.Divide(wrt_rebin[str(rebin)][1])
                wrt_hist_ratio.Write()
                del wrt_hist_ratio
        ## End loop: for rebin in range(2,6)
    ## End loop: for ii in [0,1]
    del wrt_rebin
    wrt_hist_ratio = wrt_hist[0].Clone(wrt_hist[0].GetName().replace('Pass','Ratio'))
    wrt_hist_ratio.Divide(wrt_hist[1])
    wrt_hist_ratio.Write()
    del wrt_hist_ratio
## End loop: for wrt_hist in [...]

out_file_dataMC.Write()
out_file_dataMC.Close()
del out_file_dataMC


## Write JSONs for data and rounded data and MC templates
for dset in ['Data','Datarounded','MCrounded']:
    DM = 'Data' if dset.startswith('Data') else 'MC'
    print('\nWriting '+JSON_DIR+'/'+CAT+'_Htoaato4b_'+dset+'.json')
    with open('jsons/%s_Htoaato4b_%s.json' % (CATL, DM), 'r') as jf:
        jsonDM = json.load(jf)  # `data` is now a Python dictionary or list
        jsonDM['PROCESSES']["data_obs"]['ALIAS'] = '%s_%s_%s_%s_%s' % (CAT, dset, YEAR, MHREG, MAREG)
        jsonDM['NAME'] = CAT+'_Htoaato4b'
    with open('%s/%s_Htoaato4b_%s_%s_%s.json' % (JSON_DIR, CAT, dset, MHREG, MAREG),  'w') as jf:
        json.dump(jsonDM, jf, indent=2)
    if not dset.endswith('rounded'):
        continue
    for key in h_rounded_sig[DM]['Pass'].keys():
        jsonDM['PROCESSES']["data_obs"]['ALIAS'] = '%s_%s_%s_%s_%s_%s' % (CAT, dset, key, YEAR, MHREG, MAREG)
        with open('%s/%s_Htoaato4b_%s_%s_%s_%s.json' % (JSON_DIR, CAT, dset, key, MHREG, MAREG), 'w') as jf:
            json.dump(jsonDM, jf, indent=2)

## Write JSONs for toys
for DM in DMs:
    if (DM == 'MC' and not doToysMC) or (DM == 'Data' and not doToysData):
        continue
    print('\nWriting '+str(NTOYS)+' '+DM+' toys to '+EOS_DIR+'/'+JSON_DIR+'/')
    if DELETE_OLD:
        print('First remove files matching '+EOS_DIR+'/'+JSON_DIR+'/*'+DM+'toy*'+MHREG+'_'+MAREG+'*')
        for fl in glob.glob(EOS_DIR+'/'+JSON_DIR+'/*'+DM+'toy*'+MHREG+'_'+MAREG+'*'):
            os.remove(fl)
    for iToy in range(NTOYS):
        ## Use "MC" settings (i.e. unblinded) for toys 0 - 9
        with open('jsons/%s_Htoaato4b_%s.json' % (CATL, DM if iToy > 9 else 'MC'), 'r') as jf:
            jsonDM = json.load(jf)  # `data` is now a Python dictionary or list
        jsonDM['PROCESSES']["data_obs"]['ALIAS'] = '%s_%ssmooth2_toy%d_%s_%s_%s' % (CAT, DM, iToy, YEAR, MHREG, MAREG)
        jsonDM['PROCESSES']["data_obs"]['LOC'] = 'path/toys/FILE:HIST'
        jsonDM['NAME'] = CAT+'_Htoaato4b'
        with open('%s/%s/%s_Htoaato4b_%stoy%d_%s_%s.json' % (EOS_DIR, JSON_DIR, CAT, DM, iToy, MHREG, MAREG), 'w') as jf:
            json.dump(jsonDM, jf, indent=2)
        for key in h_rounded_sig[DM]['Pass'].keys():
            jsonDM['PROCESSES']["data_obs"]['ALIAS'] = '%s_%ssmooth2_toy%d_%s_%s_%s_%s' % (CAT, DM, iToy, key, YEAR, MHREG, MAREG)
            with open('%s/%s/%s_Htoaato4b_%stoy%d_%s_%s_%s.json' % (EOS_DIR, JSON_DIR, CAT, DM, iToy, key, MHREG, MAREG), 'w') as jf:
                json.dump(jsonDM, jf, indent=2)
    ## End loop: for iToy in range(NTOYS)
## End loop: for DM in DMs


print('\n\nALL DONE with Haa4b_makeMCtoy.py!!!\n\n')
