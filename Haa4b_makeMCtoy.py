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
CATEGORY = str(sys.argv[1])  ## gg0lIncl/Hi/Lo, VBFjjIncl/Hi/Lo, LepHi/Lo
NTOYS    = int(sys.argv[2])
TOYSOURCE = str(sys.argv[3]) ## MC, Data, DataAndMC, None
SMOOTH_CUT = 3.0  ## Largest allowed fluctation in smoothed background (in standard deviations)
MASSESA = ['15','30','55']
SIGINJ = {'15':[5, 10, 20, 50],
          '30':[10, 20, 50, 100],
          '55':[10, 20, 50, 100, 200]}  ## Signal to inject, in 1/1000ths
YEAR = '2018'
PLOT_DIR = 'plots/'+CATEGORY+'/toys'
JSON_DIR = 'jsons/toys/'+CATEGORY

## Set toy options
doToysMC   = (TOYSOURCE == 'MC' or TOYSOURCE == 'DataAndMC')
doToysData = (TOYSOURCE == 'Data' or TOYSOURCE == 'DataAndMC')
if not (doToysMC or doToysData or TOYSOURCE == 'None'):
    print('\n\nHaa4b_makeMCtoy.py bad option! TOYSOURCE = %s. Quitting.\n')
    sys.exit()
## Check for output directory
if not os.path.exists('plots/'+CATEGORY):
    print('\n\n\nHaa4b_makeMCtoy.py error! plots/'+CATEGORY+' does not exist. Run merge_file_script_mctoy.py first.\n')
    sys.exit()
## Make sub-directories for output toy ROOT and JSON files
if not os.path.exists(PLOT_DIR):
    os.mkdir(PLOT_DIR)
if not os.path.exists(JSON_DIR):
    os.system('mkdir -p '+JSON_DIR)

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

    if VERBOSE: print('\ncompute_max_pull: %s bin %d,%d has yield %.3f vs. %.3f avg from %d nearby bins (pull = %.1f)' %
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
def toys_generator(hist, nToy, output_dir, root_cmd, h_sigs={}):
    if VERBOSE: print('\ntoys_generator: Throwing %d toys from %s' % (nToy, hist.GetName()))
    str_repl = None
    for substr in ['_MCsmooth1_','_MCsmooth2_','_Data_']:
        if substr in hist.GetName():
            str_repl = substr
            break
    if str_repl == None:
        print('\n\nWhy are you throwing toys from non-smoothed MC?!? Quitting.\n')
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
        filename = hist.GetName().split("_pnet")[0].replace(str_repl, str_repl+'toy%d_' % iT)
        ## Create new ROOT file (root_cmd = "RECREATE"), or add to existing ("UPDATE")
        output_file = R.TFile(output_dir+"/"+filename+".root", root_cmd)
        out_file_sig = {}
        for key in avg_toy_hist_sig.keys():
            out_file_sig[key] = R.TFile(output_file.GetName().replace('toy%d' % iT, 'toy%d_%s' % (iT, key)), root_cmd)
        if iT == 0:
            print('Writing toy #%d to %s' % (iT, output_dir+"/"+filename+".root"))
        if (iT % 100) == 0:
            print('  - Starting toy %d/%d' % (iT, nToy))
        toy_hist = hist.Clone(hist.GetName().replace(str_repl, str_repl+'toy%d_' % iT))
        toy_hist_sig = {}
        for key in avg_toy_hist_sig.keys():
            toy_hist_sig[key] = toy_hist.Clone(toy_hist.GetName().replace('toy%d' % iT, 'toy%d_%s' % (iT, key)))
        for iX in range(1, hist.GetNbinsX()+1):
            for iY in range(1, hist.GetNbinsY()+1):
                expected = hist.GetBinContent(iX,iY)
                fluctuated = np.random.poisson(expected)
                toy_hist.SetBinContent(iX,iY,fluctuated)
                toy_hist.SetBinError(iX,iY,np.sqrt(fluctuated))
                for key in toy_hist_sig.keys():
                    mA = key[3:5]
                    sBr = int(key[-3:])*0.001
                    assert (mA in MASSESA and int(key[-3:]) in SIGINJ[mA]), 'Haa4b_makeMCtoy.py: mA = %s, sBr = %d' % (mA, sBr)
                    exp_sig = expected + h_sigs[mA].GetBinContent(iX,iY)*sBr
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
        filename = hist.GetName().split("_pnet")[0].replace(str_repl, str_repl+'toy%d_' % jT)
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
## End function: toys_generator(hist, nToy, output_dir, root_cmd, h_sigs={})



####################
## Main body of code
####################

print("Running Haa4b_makeMCtoy.py for the following category:", CATEGORY)

## "Super-category" defines some directory / file names
superCat = CATEGORY
## Most categories used WP60, a couple use WP60
WP = 'WP60'
for supr in ['gg0l','VBFjj']:
    if supr in CATEGORY:
        superCat = supr
        WP = 'WP40'

## Different categories use different sets of background samples
samps = ['Data']
if 'gg0l' in CATEGORY or 'VBFjj' in CATEGORY:
    samps.append('MC')  ## Background MC already summed
    sigs = ['ggH','VBFH','WH','ZH','ttH']
    if 'VBFjj' in CATEGORY:
        print('\nWARNING!!! Only VBFH signal available for VBFjj categories. Need to add others!!!\n')
        sigs = ['VBFH']
    for sig in sigs:
        for mA in MASSESA:
            samps.append(sig+'toaato4b_mA_'+str(mA))

elif 'Lep' in CATEGORY:
    samps = samps+['Wlv','TT1l']
    sigs  = ['WH','ttH']
    if CATEGORY == 'LepHi':
        samps = samps+['Zll','TT2l','ZZ']
        sigs  = sigs+['ZH']
    for sig in sigs:
        for mA in MASSESA:
            samps.append(sig+'toaato4b_mA_'+str(mA))

else:
    print('\nInvalid category %s!!! Quitting.' % CATEGORY)
    sys.exit()

print('\nIn Haa4b_makeMCtoy.py, looking for the following samples:')
print(samps)

base_pth = 'raw_inputs/2D_in_merged_%s/' % superCat


# step 1, merge bkg MC, set bin errors based on effective yields
h_data_pass = None
h_data_fail = None
h_MC_pass = None
h_MC_fail = None
h_sig_pass = {}
h_sig_fail = {}
for mA in MASSESA:
    h_sig_pass[mA] = None
    h_sig_fail[mA] = None

## Loop over samples to get pass / fail histograms
for samp in samps:
    filepath = base_pth+superCat+'_'+samp+'_'+YEAR+'.root'
    print(f"add {filepath}")
    hname = CATEGORY+'_'+samp+'_'+YEAR+'_pnet_'+WP
    pass_name = hname+'_Pass_Nom'
    fail_name = hname+'_Fail_Nom'
    in_file = R.TFile.Open(filepath)

    ## Store signal histograms
    isSignal = False
    for mA in MASSESA:
        if 'Htoaato4b_mA_'+mA in filepath:
            isSignal = True
            if h_sig_pass[mA] == None:
                h_sig_pass[mA] = in_file.Get(pass_name)
                h_sig_fail[mA] = in_file.Get(fail_name)
                h_sig_pass[mA].SetDirectory(0)
                h_sig_fail[mA].SetDirectory(0)
                for sig in ['ggH','VBFH','WH','ZH','ttH']:
                    h_sig_pass[mA].SetName(h_sig_pass[mA].GetName().replace(sig+'toaa','Htoaa'))
                    h_sig_fail[mA].SetName(h_sig_fail[mA].GetName().replace(sig+'toaa','Htoaa'))
                if VERBOSE: print('  * Creating %s from %s (integral = %.1f)' % (h_sig_pass[mA].GetName(), pass_name, h_sig_pass[mA].Integral()))
            else:
                h_sig_pass[mA].Add(in_file.Get(pass_name))
                h_sig_fail[mA].Add(in_file.Get(fail_name))
                if VERBOSE: print('  * Adding %s to %s (new integral = %.1f)' % (pass_name, h_sig_pass[mA].GetName(), h_sig_pass[mA].Integral()))
        ## End conditional: if 'Htoaato4b_mA_'+mA in filepath
    ## End loop: for mA in MASSESA
    if isSignal:
        continue

    h_in_pass = in_file.Get(pass_name)
    h_in_fail = in_file.Get(fail_name)

    ## For gg0l, scale background MC WP60 --> WP40
    if 'gg0l' in CATEGORY and samp != 'Data' and not 'Htoaato4b' in samp:
        h_in_pass_WP60 = in_file.Get(pass_name.replace('WP40','WP60'))
        h_in_fail_WP60 = in_file.Get(fail_name.replace('WP40','WP60'))
        WP40_yield_pass = h_in_pass.Integral()
        WP40_yield_fail = h_in_fail.Integral()
        h_in_pass.Scale(0)
        h_in_fail.Scale(0)
        h_in_pass.Add(h_in_pass_WP60)
        h_in_fail.Add(h_in_fail_WP60)
        pass_SF = WP40_yield_pass / h_in_pass_WP60.Integral()
        fail_SF = WP40_yield_fail / h_in_fail_WP60.Integral()
        print('Scaling %s by %.3f from %.1f to %.1f' % (h_in_pass.GetName(), pass_SF, h_in_pass_WP60.Integral(), WP40_yield_pass))
        print('Scaling %s by %.3f from %.1f to %.1f' % (h_in_fail.GetName(), fail_SF, h_in_fail_WP60.Integral(), WP40_yield_fail))
        h_in_pass.Scale(pass_SF)
        h_in_fail.Scale(fail_SF)
    ## End conditional: if 'gg0l' in CATEGORY and samp != 'Data' and not 'Htoaato4b' in samp

    ## Get the input histograms, sum background MC
    if samp == 'Data':
        h_data_pass = h_in_pass.Clone(pass_name)
        h_data_pass.SetDirectory(0)
        h_data_fail = h_in_fail.Clone(fail_name)
        h_data_fail.SetDirectory(0)
    elif ((h_MC_pass is None) and (h_MC_fail is None)):
        h_MC_pass = h_in_pass.Clone(pass_name.replace('_%s_' % samp, '_MC_'))
        h_MC_pass.SetDirectory(0)
        h_MC_fail = h_in_fail.Clone(fail_name.replace('_%s_' % samp, '_MC_'))
        h_MC_fail.SetDirectory(0)
    else:
        h_MC_pass.Add(h_in_pass)
        h_MC_fail.Add(h_in_fail)
## End loop: for samp in samps

## Scale MC to data
h_MC_pass = scale_to_ref(h_MC_pass, h_data_pass)
h_MC_fail = scale_to_ref(h_MC_fail, h_data_fail)


## Set minimum per-bin errors to reflect effective MC event weights
eff_wgt_pass = get_eff_weight(h_MC_pass)
eff_wgt_fail = get_eff_weight(h_MC_fail)
nX = h_MC_pass.GetNbinsX()
nY = h_MC_pass.GetNbinsY()
if (nX != h_MC_fail.GetNbinsX() or nY != h_MC_fail.GetNbinsY()):
    print('\nERROR!!! %s is %dx%d, %s is not! Quitting.' % (h_MC_pass.GetName(), nX, nY, h_MC_fail.GetName()))
    sys.exit()
h_MC_pass = reset_bin_errors(h_MC_pass, h_MC_pass, eff_wgt_pass)
h_MC_fail = reset_bin_errors(h_MC_fail, h_MC_fail, eff_wgt_fail)


## Write h_MC_pass and h_MC_fail and signal, without smoothing, to ROOT file
out_file_dataMC = R.TFile('plots/%s/%s_%s_%dtoys_Data_MC.root' % (CATEGORY, CATEGORY, TOYSOURCE, NTOYS), 'RECREATE')
h_data_pass.Write()
h_data_fail.Write()
h_MC_pass.Write()
h_MC_fail.Write()
for mA in h_sig_pass.keys():
    h_sig_pass[mA].Write()
    h_sig_fail[mA].Write()
out_file_dataMC.Write()
out_file_dataMC.Close()

# step 2, smooth, set negative bins to 0, and set errors based on effective yields
h_MCsmooth1_pass = None
h_MCsmooth1_fail = None
if h_MC_pass!=None and h_MC_fail!=None:
    h_MCsmooth1_pass=h_MC_pass.Clone(h_MC_pass.GetName().replace('_MC_','_MCsmooth1_'))
    h_MCsmooth1_fail=h_MC_fail.Clone(h_MC_fail.GetName().replace('_MC_','_MCsmooth1_'))
    ## Smooth until there are no large statistical variations in 3x3 or 5x5 regions (up to 2 times)
    nSmooth_pass,nSmooth_fail = 0,0
    while((compute_max_pull(h_MCsmooth1_pass, 1, eff_wgt_pass) > SMOOTH_CUT or
           compute_max_pull(h_MCsmooth1_pass, 2, eff_wgt_pass) > SMOOTH_CUT) and nSmooth_pass < 2):
        h_MCsmooth1_pass.Smooth(1)
        h_MCsmooth1_pass = reset_bin_errors(h_MCsmooth1_pass, h_MC_pass, eff_wgt_pass)
        nSmooth_pass += 1
    while((compute_max_pull(h_MCsmooth1_fail, 1, eff_wgt_fail) > SMOOTH_CUT or
           compute_max_pull(h_MCsmooth1_fail, 2, eff_wgt_fail) > SMOOTH_CUT) and nSmooth_fail < 2):
        h_MCsmooth1_fail.Smooth(1)
        h_MCsmooth1_fail = reset_bin_errors(h_MCsmooth1_fail, h_MC_fail, eff_wgt_fail)
        nSmooth_fail += 1
    print('\nSmoothed %s %d times, %s %d times' % (h_MCsmooth1_pass.GetName(), nSmooth_pass,
                                                   h_MCsmooth1_fail.GetName(), nSmooth_fail))
    h_MCsmooth1_pass = scale_to_ref(h_MCsmooth1_pass, h_data_pass)
    h_MCsmooth1_fail = scale_to_ref(h_MCsmooth1_fail, h_data_fail)
else:
    print('\n\nERROR!!! Either h_MC_pass or h_MC_fail does not exist! Quitting.\n')
    sys.exit()


# Additional manual regional averaging for bins with large uncertainty compared to yields
h_MCsmooth2_pass = h_MCsmooth1_pass.Clone(h_MCsmooth1_pass.GetName().replace('smooth1','smooth2'))
h_MCsmooth2_fail = h_MCsmooth1_fail.Clone(h_MCsmooth1_fail.GetName().replace('smooth1','smooth2'))

# Loop over bins in 2D distribution
for iX in range(1, nX+1):
    for iY in range(1, nY+1):
        # Set negative bins to 0
        if h_MCsmooth1_pass.GetBinContent(iX,iY) < 0:
            h_MCsmooth1_pass.SetBinContent(iX,iY,0)
        if h_MCsmooth1_fail.GetBinContent(iX,iY,0) < 0:
            h_MCsmooth1_fail.SetBinContent(iX,iY, 0)
        # Set error using un-smoothed bin error or effective weight (whichever is larger)
        bin_wgt_pass = pow(h_MC_pass.GetBinError(iX,iY),2) / max(eff_wgt_pass, h_MC_pass.GetBinContent(iX,iY))
        bin_wgt_fail = pow(h_MC_fail.GetBinError(iX,iY),2) / max(eff_wgt_fail, h_MC_fail.GetBinContent(iX,iY))
        bin_wgt_pass = max(bin_wgt_pass, eff_wgt_pass)
        bin_wgt_fail = max(bin_wgt_fail, eff_wgt_fail)
        bin_err_pass = np.sqrt(max(1.0, h_MCsmooth1_pass.GetBinContent(iX,iY)/bin_wgt_pass))*bin_wgt_pass
        bin_err_fail = np.sqrt(max(1.0, h_MCsmooth1_fail.GetBinContent(iX,iY)/bin_wgt_fail))*bin_wgt_fail
        h_MCsmooth1_pass.SetBinError(iX,iY,bin_err_pass)
        h_MCsmooth1_fail.SetBinError(iX,iY,bin_err_fail)
        pass_exp = get_bin_expectation(h_MCsmooth1_pass, iX, iY, eff_wgt_pass)
        fail_exp = get_bin_expectation(h_MCsmooth1_fail, iX, iY, eff_wgt_fail)
        h_MCsmooth2_pass.SetBinContent(iX,iY, pass_exp[0])
        h_MCsmooth2_fail.SetBinContent(iX,iY, fail_exp[0])
        h_MCsmooth2_pass.SetBinError(iX,iY, pass_exp[1])
        h_MCsmooth2_fail.SetBinError(iX,iY, fail_exp[1])
    ## End loop: for iY in range(1, nY+1)
## End loop: for iX in range(1, nX+1)
h_MCsmooth2_pass = scale_to_ref(h_MCsmooth2_pass, h_data_pass)
h_MCsmooth2_fail = scale_to_ref(h_MCsmooth2_fail, h_data_fail)

# Also create rounded integer version for "nominal" pseudo-data
h_MCrounded_pass = h_MCsmooth2_pass.Clone(h_MCsmooth2_pass.GetName().replace('smooth2','rounded'))
h_MCrounded_fail = h_MCsmooth2_fail.Clone(h_MCsmooth2_fail.GetName().replace('smooth2','rounded'))
h_MCrounded_pass = round_bins(h_MCsmooth2_pass, h_MCrounded_pass)
h_MCrounded_fail = round_bins(h_MCsmooth2_fail, h_MCrounded_fail)
h_MCrounded_sig_pass = {}
h_MCrounded_sig_fail = {}
for mA in h_sig_pass.keys():
    for sInj in SIGINJ[mA]:
        key = 'mA_%s_sigBr_%03d' % (mA, sInj)
        h_MCrounded_sig_pass[key] = h_MCsmooth2_pass.Clone(h_MCsmooth2_pass.GetName().replace('smooth2','rounded_'+key))
        h_MCrounded_sig_fail[key] = h_MCsmooth2_fail.Clone(h_MCsmooth2_fail.GetName().replace('smooth2','rounded_'+key))
        h_MCrounded_sig_pass[key].Add(h_sig_pass[mA], sInj*0.01)
        h_MCrounded_sig_fail[key].Add(h_sig_fail[mA], sInj*0.01)
        h_MCrounded_sig_pass[key] = round_bins(h_MCrounded_sig_pass[key].Clone(key+'_pass_tmp'), h_MCrounded_sig_pass[key])
        h_MCrounded_sig_fail[key] = round_bins(h_MCrounded_sig_fail[key].Clone(key+'_fail_tmp'), h_MCrounded_sig_fail[key])

## Write rounded MC to its own "toy" file
out_MCr_name = h_MCrounded_pass.GetName().split("_pnet")[0]
out_fileMCr = R.TFile('plots/'+CATEGORY+'/'+out_MCr_name+'.root', 'RECREATE')
h_MCrounded_pass.Write()
h_MCrounded_fail.Write()
out_fileMCr.Write()
out_fileMCr.Close()
out_fileMCr_sig = {}
for key in h_MCrounded_sig_pass.keys():
    out_fileMCr_sig[key] = R.TFile(out_fileMCr.GetName().replace('rounded','rounded_'+key), 'RECREATE')
    h_MCrounded_sig_pass[key].Write()
    h_MCrounded_sig_fail[key].Write()
    out_fileMCr_sig[key].Write()
    out_fileMCr_sig[key].Close()


## Generate toys, get average toy occupancy and variance
avg_toyMC_pass = None
avg_toyMC_fail = None
avg_toyData_pass = None
avg_toyData_fail = None
if doToysMC:
    print('\nRemoving all files matching plots/'+CATEGORY+'/toys/*MCsmooth2_toy*')
    for fl in glob.glob('plots/'+CATEGORY+'/toys/*MCsmooth2_toy*'):
        os.remove(fl)
    avg_toyMC_pass = toys_generator(h_MCsmooth2_pass, NTOYS, PLOT_DIR, "RECREATE", h_sig_pass)
    avg_toyMC_fail = toys_generator(h_MCsmooth2_fail, NTOYS, PLOT_DIR, "UPDATE", h_sig_fail)
if doToysData:
    print('\nRemoving all files matching plots/'+CATEGORY+'/toys/*Data_toy*')
    for fl in glob.glob('plots/'+CATEGORY+'/toys/*Data_toy*'):
        os.remove(fl)
    avg_toyData_pass = toys_generator(h_data_pass, NTOYS, PLOT_DIR, "RECREATE", h_sig_pass)
    avg_toyData_fail = toys_generator(h_data_fail, NTOYS, PLOT_DIR, "UPDATE", h_sig_fail)


## Write h_MC_pass and h_MC_fail and average toy histograms to ROOT file
out_file_dataMC = R.TFile('plots/%s/%s_%s_%dtoys_Data_MC.root' % (CATEGORY, CATEGORY, TOYSOURCE, NTOYS), 'UPDATE')
wrt_hists = [[h_MCsmooth1_pass, h_MCsmooth1_fail],
             [h_MCsmooth2_pass, h_MCsmooth2_fail],
             [h_MCrounded_pass, h_MCrounded_fail]]
if doToysMC:
    for key in avg_toyMC_pass.keys():
        wrt_hists += [[avg_toyMC_pass[key], avg_toyMC_fail[key]]]
if doToysData:
    for key in avg_toyData_pass.keys():
        wrt_hists += [[avg_toyData_pass[key], avg_toyData_fail[key]]]

for wrt_hist in wrt_hists:
    if VERBOSE: print('\nIn Haa4b_makeMCtoy_ggH.py, writing %s (and "fail")' % wrt_hist[0].GetName())
    wrt_rebin = {}
    for ii in [0,1]:
        wrt_hist[ii].Write()
        ## Also write rebinned versions and ratios for simpler analysis later
        for rebin in range(2,6):
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


## Write JSON for rounded MC template
print('\nWriting '+JSON_DIR+'/'+CATEGORY+'_Htoaato4b_MCrounded.json')
with open('jsons/%s_Htoaato4b_MC.json' % CATEGORY, 'r') as jf:
    jsonMC = json.load(jf)  # `data` is now a Python dictionary or list
jsonMC['PROCESSES']["data_obs"]['ALIAS'] = CATEGORY+'_MCrounded_'+YEAR
with open(JSON_DIR+'/'+CATEGORY+'_Htoaato4b_MCrounded.json', 'w') as jf:
    json.dump(jsonMC, jf, indent=2)
for key in h_MCrounded_sig_pass.keys():
    jsonMC['PROCESSES']["data_obs"]['ALIAS'] = CATEGORY+'_MCrounded_'+key+'_'+YEAR
    with open(JSON_DIR+'/'+CATEGORY+'_Htoaato4b_MCrounded_'+key+'.json', 'w') as jf:
        json.dump(jsonMC, jf, indent=2)
## Write JSON for rounded data
print('Writing '+JSON_DIR+'/'+CATEGORY+'_Htoaato4b_Data.json')
with open('jsons/%s_Htoaato4b_Data.json' % CATEGORY, 'r') as jf:
    jsonData = json.load(jf)  # `data` is now a Python dictionary or list
jsonData['PROCESSES']["data_obs"]['ALIAS'] = CATEGORY+'_Data_'+YEAR
with open(JSON_DIR+'/'+CATEGORY+'_Htoaato4b_Data.json', 'w') as jf:
    json.dump(jsonData, jf, indent=2)


if doToysMC:
    print('\nWriting '+str(NTOYS)+' MC toys to '+JSON_DIR+'/')
    print('First remove files matching '+JSON_DIR+'/*mctoy*')
    for fl in glob.glob(JSON_DIR+'/*mctoy*'):
        os.remove(fl)
    for iToy in range(NTOYS):
        with open('jsons/%s_Htoaato4b_MC.json' % CATEGORY, 'r') as jf:
            jsonMC = json.load(jf)  # `data` is now a Python dictionary or list
        jsonMC['PROCESSES']["data_obs"]['ALIAS'] = CATEGORY+'_MCsmooth2_toy'+str(iToy)+'_'+YEAR
        with open(JSON_DIR+'/'+CATEGORY+'_Htoaato4b_mctoy'+str(iToy)+'.json', 'w') as jf:
            json.dump(jsonMC, jf, indent=2)
        for key in h_MCrounded_sig_pass.keys():
            jsonMC['PROCESSES']["data_obs"]['ALIAS'] = CATEGORY+'_MCsmooth2_toy'+str(iToy)+'_'+key+'_'+YEAR
            with open(JSON_DIR+'/'+CATEGORY+'_Htoaato4b_mctoy'+str(iToy)+'_'+key+'.json', 'w') as jf:
                json.dump(jsonMC, jf, indent=2)

if doToysData:
    print('\nWriting '+str(NTOYS)+' data toys to '+JSON_DIR+'/')
    print('First remove files matching '+JSON_DIR+'/*datatoy*')
    for fl in glob.glob(JSON_DIR+'/*datatoy*'):
        os.remove(fl)
    for jToy in range(NTOYS):
        with open('jsons/%s_Htoaato4b_Data.json' % CATEGORY, 'r') as jf:
            jsonData = json.load(jf)  # `data` is now a Python dictionary or list
        jsonData['PROCESSES']["data_obs"]['ALIAS'] = CATEGORY+'_Data_toy'+str(jToy)+'_'+YEAR
        with open(JSON_DIR+'/'+CATEGORY+'_Htoaato4b_datatoy'+str(jToy)+'.json', 'w') as jf:
            json.dump(jsonData, jf, indent=2)
        for key in h_MCrounded_sig_pass.keys():
            jsonData['PROCESSES']["data_obs"]['ALIAS'] = CATEGORY+'_Data_toy'+str(iToy)+'_'+key+'_'+YEAR
            with open(JSON_DIR+'/'+CATEGORY+'_Htoaato4b_datatoy'+str(iToy)+'_'+key+'.json', 'w') as jf:
                json.dump(jsonData, jf, indent=2)

print('\n\nALL DONE with Haa4b_makeMCtoy.py!!!\n\n')
