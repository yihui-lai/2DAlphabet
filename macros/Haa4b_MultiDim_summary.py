## From https://github.com/bouchamaouihichem/2DAlphabet/blob/master/Haa4b_fitsummary.py

import os
import sys
import numpy as np
import ROOT as R

R.gROOT.SetBatch(True)
import glob
R.gStyle.SetOptStat(0)  ## Don't display stat boxes

VERBOSE = False
YEAR    = '2018'
DATE    = '2025_06_03'
DMC     = 'Data'  ## Data or MC
SIGINJ  = ''
#SIGINJ  = '*_mA_*_sigBr_*'
doSigInj = ('_sigBr_' in SIGINJ)
CATS    = ['HadXLo']
MASSESA = ['12']+[str(iMA*5) for iMA in range(3,13)]
#MASSESA = ['12']
FITS    = ['1x1C']
MIN_PTS = 100  ## Minimum number of points the scan should contain

eos_from_config = [eos for eos in (open('config/user.config','r')).readlines() if eos.startswith('EOS_DIR=')]
loc_from_config = [loc for loc in (open('config/user.config','r')).readlines() if loc.startswith('LOC_DIR=')]
EOS_DIR = eos_from_config[0].replace('EOS_DIR=','').replace('\n','')
LOC_DIR = loc_from_config[0].replace('LOC_DIR=','').replace('\n','')
IN_DIR  = EOS_DIR+'/ToyStudies/'+YEAR+'/'+DATE
RND_DIR = LOC_DIR+'/output/%stoys/Mergecards/%s%srounded' % (DMC, DMC, DMC)
OUT_DIR = LOC_DIR+'/figures/MultiDimFit'

if not os.path.exists(OUT_DIR):
    os.mkdir(OUT_DIR)

def solve_parab(pts,xs,ys):
    x1,x2,x3 = pts[0][xs],pts[1][xs],pts[2][xs]
    y1,y2,y3 = pts[0][ys],pts[1][ys],pts[2][ys]
    denom = (x1-x2)*(x1-x3)*(x2-x3)
    A     = (x3*(y2-y1) + x2*(y1-y3) + x1*(y3-y2)) / denom
    B     = (x3*x3*(y1-y2) + x2*x2*(y3-y1) + x1*x1*(y2-y3)) / denom
    C     = (x2*x3*(x2-x3)*y1+x3*x1*(x3-x1)*y2+x1*x2*(x1-x2)*y3) / denom
    return [A,B,C]

def get_parab_min(ABC):
    A = ABC[0]
    B = ABC[1]
    C = ABC[2]
    x_min = -B/(2*A)
    y_min = A*pow(x_min,2) + B*x_min + C
    return [x_min, y_min]


# File pattern for toy fit diagnostics
for cat in CATS:
    for mA in MASSESA:
        for fit in FITS:
            algo = 'MultiDimFit'
            base = 'higgsCombine.test'+algo
            suff = 'MultiDimFit.mH120.root'
            file_pattern = '%s/%s/%s.%s.mA_%s.%s%s.%stoy*.%s' % (IN_DIR, cat, base, cat, mA, fit, SIGINJ, DMC, suff)
            rnd_pattern  = '%s/%s.%s.mA_%s.%s%s.%s%srounded.%s' % (RND_DIR, base, cat, mA, fit, SIGINJ, DMC, DMC, suff)
            in_files  = glob.glob(file_pattern)
            rnd_files = glob.glob(rnd_pattern)
            if doSigInj:
                in_files  = [inf for inf in in_files]
                rnd_files = [rnf for rnf in rnd_files]
            else:
                in_files  = [inf for inf in in_files if not ('mA_%s_sigBr_' % mA) in inf]
                rnd_files = [rnf for rnf in rnd_files if not ('mA_%s_sigBr_' % mA) in rnf]
            print('\nFound %d files matching pattern:' % len(in_files))
            print(file_pattern)
            print('Found %d files matching pattern:' % len(rnd_files))
            print(rnd_pattern)
            assert len(rnd_files) <= 1, '\nFound %d rounded files instead of 1!!! Quitting.\n' % len(rnd_files)
            found_round = (len(rnd_files) == 1)

            ## Store injected signal
            injSig = 0
            if doSigInj:
                injSig = float(in_files[0].split('_sigBr_')[1][0:3])*0.001


            ## Store best-fit r/NLL/pull and "2 sigma" r/NLL/pull with uncertainties
            fit_keys = [('r',float), ('rErr',float), ('NLL',float), ('NLLerr',float), ('pull',float), ('pullErr',float)]
            bst_pt = np.array([], dtype=fit_keys)  ## Best-fit values
            zro_pt = np.array([], dtype=fit_keys)  ## Values at r = 0
            inj_pt = np.array([], dtype=fit_keys)  ## Values at r = injected signal
            #tws_pt = np.array([], dtype=fit_keys)  ## Values at +2 sigma from best-fit
            #lim_pt = np.array([], dtype=fit_keys)  ## Values at 95% CL limit point

            iFile,nFiles,nEntry = 0,0,0
            for fName in rnd_files+in_files:
                iFile += 1
                if (iFile % int(np.sqrt(len(rnd_files+in_files)))) == 1:
                    print('Looking at file #%d / %d' % (iFile, len(rnd_files+in_files)))
                if not os.path.isfile(fName):
                    print('\nWEIRD ERROR! %s does not exist!' % fName)
                    continue
                in_file = None
                try:
                    in_file = R.TFile.Open(fName)
                except:
                    print('\nWEIRD ERROR! %s cannot be opened!' % fName)
                    continue
                if not in_file:
                    print('\nWEIRD ERROR! %s opened but somehow not there!' % fName)
                    continue
                if in_file.IsZombie():
                    print('\nWEIRD ERROR! %s is a zombie!' % fName)
                    continue
                in_tree = in_file.Get("limit")
                if not in_tree:
                    print('\nWEIRD ERROR! No "limit" tree in file %s' % fName)
                    in_file.Close()
                    continue
                val_keys = [('r',float), ('dNLL',float), ('NLL',float), ('pull',float)]
                val = np.array([], val_keys)
                iEntry = 0
                for entry in in_tree:
                    iEntry += 1
                    nEntry += 1
                    val = np.append(val, np.array([(entry.r, entry.deltaNLL, -999., -999.)], dtype=val.dtype))
                ## End loop: for entry in in_tree
                if iEntry < MIN_PTS:
                    print('\nERROR!!! File %d has only %d entries! Skipping.' % (iFile, iEntry))
                    print(fName)
                    continue

                if val[0]['r'] != 0 or val[1]['r'] == 0:
                    val = val[1:]  ## Remove first element (either 'best-fit' or just 'middle r', not consistent)
                rCut = 0.01 if int(mA) < 22 else (0.02 if int(mA) < 42 else (0.03 if int(mA) < 63 else 0.01))
                if val[0]['r'] > rCut:
                    print('\nERROR!!! File %d, first "r" = %.4f, not near 0. Code assumes scan starts from ~0. Skipping!' % (iFile, val[0]['r']))
                    print(fName)
                ## Double check injected signal
                if doSigInj:
                    if float(fName.split('_sigBr_')[1][0:3]) != int(injSig*1000):
                        assert False, '\nFile %s does not match %.1f%% injected signal!' % (fName, injSig*100)
                sort_dNLL = np.sort(val, order='dNLL')
                min_dNLL = sort_dNLL[0]['dNLL']
                sort_dNLL[:]['NLL'] = sort_dNLL[:]['dNLL'] - min_dNLL
                sort_dNLL[:]['pull'] = np.sqrt(2*sort_dNLL[:]['NLL'])

                parab_min = sort_dNLL[0:7]  ## Lowest 7 points in NLL parabola
                min_NLL_pt = [-99.,-99.]  ## Best-fit [r, NLL]
                min_NLL_err = [0,0]  ## Uncertainties on best-fit [r, NLL]
                if parab_min[0]['r'] == 0:
                    min_NLL_pt = [0.0, parab_min[0]['NLL']]
                else:
                    pIdx = [-99,-99,0,-99,-99]  ## 5 points on parabola to infer minimum
                    for iPar in range(1,7):
                        if parab_min[iPar]['r'] < parab_min[0]['r']:
                            if pIdx[1] == -99:
                                pIdx[1] = iPar
                            elif pIdx[0] == -99:
                                pIdx[0] = iPar
                            else: True  ## Already found 2 closer
                        if parab_min[iPar]['r'] > parab_min[0]['r']:
                            if pIdx[3] == -99:
                                pIdx[3] = iPar
                            elif pIdx[4] == -99:
                                pIdx[4] = iPar
                            else: True  ## Already found 2 closer
                    if -99 in pIdx[1:4] and -99 in pIdx[0:3] and -99 in pIdx[2:5]:
                        print('\nERROR! File %d, could not find 2 points close to minimum. Skipping.' % iFile)
                        continue
                    idxs = [1,2,3] if not -99 in pIdx[1:4] else ([2,3,4] if not -99 in pIdx[2:5] else [0,1,2])
                    min_NLL_pt = get_parab_min(solve_parab([parab_min[pIdx[i]] for i in idxs], 'r', 'NLL'))
                    if not -99 in pIdx[1:4] and not -99 in pIdx[1:5]:
                        min_NLL_up = solve_parab([parab_min[pIdx[i]] for i in [1,2,4]], 'r', 'NLL')
                        min_NLL_err += [pow(min_NLL_pt[0]-min_NLL_up[0],2), pow(min_NLL_pt[1]-min_NLL_up[1],2)]
                    if not -99 in pIdx[1:4] and not -99 in pIdx[0:4]:
                        min_NLL_dn = solve_parab([parab_min[pIdx[i]] for i in [0,2,3]], 'r', 'NLL')
                        min_NLL_err += [pow(min_NLL_pt[0]-min_NLL_dn[0],2), pow(min_NLL_pt[1]-min_NLL_dn[1],2)]
                    if min_NLL_err != [0,0]:
                        min_NLL_err = np.sqrt(min_NLL_err) / 2.0
                    else:
                        print('\nWARNING! File %d, could not find 3 points around minimum. No uncertainties.' % iFile)
                    if VERBOSE:
                        print('File %d min r = %.5f+/-%.7f, NLL = %.5f+/-%0.7f' % (iFile, min_NLL_pt[0], min_NLL_err[0], min_NLL_pt[1], min_NLL_err[1]))
                    ## Adjust values based on best-fit r / NLL
                    sort_dNLL[:]['NLL']  = sort_dNLL[:]['NLL'] - min_NLL_pt[1]
                    sort_dNLL[:]['pull'] = np.sqrt(2*sort_dNLL[:]['NLL'])
                ## End conditional: if parab_min[0]['r'] == 0 / else

                ## Create new array sorted by r, starting from the updated dNLL-sorted array
                sort_r = np.sort(sort_dNLL, order='r')
                if sort_r[0]['r'] > rCut:
                    print('\nERROR! Lowest "r" value = %.4f, not ~0. Skipping!' % sort_r[0]['r'])
                    continue
                ## Find point corresponding to injected signal
                iInj = -99
                for iI in range(1, len(sort_r)-1):
                    if sort_r[iI-1]['r'] < injSig and sort_r[iI+1]['r'] > injSig:
                        iInj = iI

                ## Fill best-fit and r=0 and r=inj value arrays
                new_bst_pt = np.array([min_NLL_pt[0], min_NLL_err[0], 0.0, min_NLL_err[1], 0.0, np.sqrt(2*min_NLL_err[1])], dtype=fit_keys)
                bst_pt = np.append(bst_pt, np.array([(min_NLL_pt[0], min_NLL_err[0], 0, min_NLL_err[1], 0, np.sqrt(2*min_NLL_err[1]))], dtype=fit_keys))
                if (sort_r[0]['r'] == 0):
                    zro_pt = np.append(zro_pt, np.array([(0, 0, sort_r[0]['NLL'], 0, np.sqrt(2*sort_r[0]['NLL']), 0)], dtype=fit_keys))
                    if VERBOSE:
                        print('File %d r = 0 has NLL = %.5f (%.3f sigma)' % (iFile, sort_r[0]['NLL'], np.sqrt(2*sort_r[0]['NLL'])))
                else:
                    if VERBOSE:
                        print('File %d extrapolating to r = 0 from following (r,NLL) points:' % iFile)
                        print([[sort_r[i]['r'], sort_r[i]['NLL']] for i in [0,1,2]])
                        print('Yields parabola with the following terms:')
                        print(solve_parab([sort_r[i] for i in [0,1,2]], 'r', 'NLL'))
                    zro_NLL = solve_parab([sort_r[i] for i in [0,1,2]], 'r', 'NLL')[2]  ## "C" from parabolic fit to lowest 3 r values
                    zro_pt = np.append(zro_pt, np.array([(0, 0, zro_NLL, 0, np.sqrt(2*zro_NLL), 0)], dtype=fit_keys))
                if injSig > 0 and iInj >= 0:
                    inj_r   = sort_r[iInj]['r']
                    inj_NLL = sort_r[iInj]['NLL']
                    inj_pull = np.sqrt(2*inj_NLL)*(-1 if inj_r > min_NLL_pt[0] else 1)
                    if abs(inj_r - injSig) > 0.01 or abs(inj_r - injSig) / injSig > 0.20:
                        print('\nFile %d injected signal = %.1f%%, but closest point is %.1f%%. Skipping.' % (nFiles, injSig*100, inj_r*100))
                    else:
                        inj_pt = np.append(inj_pt, np.array([(inj_r, 0, inj_NLL, 0, inj_pull, 0)], dtype=fit_keys))


                #tws_pt = np.array([], fit_keys)  ## Values at +2 sigma from best-fit
                #lim_pt = np.array([], fit_keys)  ## Values at 95% CL limit point
                nFiles += 1
                in_file.Close()
            ## End loop: for fName in rnd_files+in_files

            print('\nFinished loop for %s %s %s: %d / %d files actually used (%d entries)\n\n' % (cat, mA, fit, nFiles, len(rnd_files+in_files), nEntry))

            injStr = 'sigBr_%03d' % (injSig*1000) if doSigInj else 'bkgOnly'
            h_str = 'h_MultiDim_%s_%s_%s_%s_%s' % (cat, mA, fit, injStr, DMC)
            xMax = 0.10 if int(mA) < 22 else (0.2 if int(mA) < 42 else 0.40)
            zpMax = 8.0 if doSigInj else 4.0
            ipMax = 4.0
            h_best_mu  = R.TH1F(h_str+'_best_fit_mu', h_str+'_best_fit_mu', 100, 0, xMax)
            h_zro_pull = R.TH1F(h_str+'_mu_zero_pull', h_str+'_mu_zero_pull', 40, 0, zpMax)
            h_inj_pull = R.TH1F(h_str+'_mu_inj_pull', h_str+'_mu_inj_pull', 80, -1*ipMax, ipMax)

            ## Fill histograms
            best_mu_rnd,zro_pull_rnd,inj_pull_rnd = -99,-99,-99
            for ii in range(max(len(bst_pt), max(len(zro_pt), len(inj_pt)))):
                ## Value from rounded templates should be first entry
                if found_round and ii == 0:
                    best_mu_rnd  = min(bst_pt[ii]['r'], xMax-0.0001)
                    zro_pull_rnd = min(zro_pt[ii]['pull'], zpMax-0.0001)
                    if doSigInj:
                        inj_pull_rnd = min(max(inj_pt[ii]['pull'], -1*(ipMax-0.0001)), ipMax-0.0001)
                else:
                    if ii < len(bst_pt): h_best_mu.Fill(min(bst_pt[ii]['r'], xMax-0.0001))
                    if ii < len(zro_pt): h_zro_pull.Fill(min(zro_pt[ii]['pull'], zpMax-0.0001))
                    if doSigInj and ii < len(inj_pt):
                        h_inj_pull.Fill(min(max(inj_pt[ii]['pull'], -1*(ipMax-0.0001)), ipMax-0.0001))

            ## Plot histograms
            hst_list = [h_best_mu, h_zro_pull]+([h_inj_pull] if doSigInj else [])
            for hst in hst_list:
                # Find median
                p = np.array([0.16,0.50,0.84])
                q = np.array([0.,0.,0.])
                hst.GetQuantiles(3, q, p)
                qdn = q[0]
                qmd = q[1]
                qup = q[2]
                nZero = hst.GetBinContent(1)
                nHist = hst.Integral()
                del p,q
                print('\n%s median = %.3f (%d/%d = 0)' % (hst.GetName(), qmd, nZero, nHist))

                can = R.TCanvas(hst.GetName(), hst.GetName(), 800, 600)
                can.cd()
                if hst.GetBinLowEdge(1) == 0:
                    hst.SetBinContent(1,0)  ## Zero out first bin for visualization
                hst.SetLineColor(R.kBlue)
                hst.SetLineWidth(2)
                hst_max = max([hst.GetBinContent(ii) for ii in range(2, hst.GetNbinsX()+1)])
                hst.GetYaxis().SetRangeUser(0, hst_max*1.5)
                hst.Draw("hist")

                ## Draw arrow representing median
                marr = R.TArrow(qmd, 0, qmd, hst_max, 1.0, '|>')
                marr.SetLineWidth(4)
                marr.SetLineColor(R.kGreen+1)
                marr.SetFillColor(R.kGreen+1)
                marr.Draw("same")

                ## Draw arrow representing values from rounded template
                val_rnd = -99
                if found_round:
                    val_rnd = (best_mu_rnd if 'best_fit_mu' in hst.GetName() else
                               (zro_pull_rnd if 'mu_zero_pull' in hst.GetName() else
                                (inj_pull_rnd if 'mu_inj_pull' in hst.GetName() else -99)))
                    rarr = R.TArrow(val_rnd, 0, val_rnd, hst_max, 1.0, '|>')
                    rarr.SetLineWidth(4)
                    rarr.SetLineColor(R.kRed)
                    rarr.SetFillColor(R.kRed)
                    rarr.Draw("same")

                ## Annotate with median, fraction of fits with mu = 0
                vstr = ''
                if 'best_fit_mu' in hst.GetName():
                    vstr = 'best-fit #mu'
                elif 'mu_zero_pull' in hst.GetName():
                    vstr = '#mu = 0 pull'
                elif 'mu_inj_pull' in hst.GetName():
                    vstr = '#mu = %.1f%% pull' % (injSig*100)
                ltx1 = R.TLatex()
                ltx1.SetNDC()
                ltx1.SetTextSize(0.037)
                ltx1.SetTextColor(R.kGreen+2)
                ltx1.DrawLatex(0.13, 0.85, 'Median %s = %.3f [%.3f,%.3f]' % (vstr, qmd, qdn, qup))
                ltx2 = R.TLatex()
                ltx2.SetNDC()
                ltx2.SetTextSize(0.037)
                ltx2.SetTextColor(R.kBlue)
                if 'mu_inj_pull' in hst.GetName() or (doSigInj and 'mu_zero_pull' in hst.GetName()):
                    ltx2.DrawLatex(0.13, 0.77, '%d entries / %d files' % (nHist, len(in_files)))
                else:
                    ltx2.DrawLatex(0.13, 0.77, '%d / %d have %s = 0' % (nZero, nHist, vstr))
                ltx3 = R.TLatex()
                if found_round:
                    ltx3.SetNDC()
                    ltx3.SetTextSize(0.037)
                    ltx3.SetTextColor(R.kRed)
                    ltx3.DrawLatex(0.13, 0.69, 'Template %s = %.3f' % (vstr, val_rnd))
                leg = R.TLegend(0.58, 0.75, 0.88, 0.88)
                leg.AddEntry(hst, vstr+' values'+(' (> 0)' if not 'mu_inj_pull' in hst.GetName() else ''), 'l')
                leg.Draw()

                can.SaveAs(OUT_DIR+'/'+hst.GetName()+'.png')
                del leg,ltx3,ltx2,ltx1,can
            ## End loop: for hst in [h_best_mu, h_zro_pull]

        ## End loop: for fit in [
    ## End loop: for mA in [
## End loop: for cat in [
