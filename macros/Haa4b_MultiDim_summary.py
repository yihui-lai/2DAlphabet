## From https://github.com/bouchamaouihichem/2DAlphabet/blob/master/Haa4b_fitsummary.py

import os
import sys
import numpy as np
import ROOT as R

R.gROOT.SetBatch(True)
import glob
R.gStyle.SetOptStat(0)  ## Don't display stat boxes

IN_DIR = '/eos/cms/store/user/abrinke1/HiggsToAA/2DAlphabet/ToyStudies/2025_05_27'
OUT_DIR = './figures'
VERBOSE = False
SIGINJ = ''
MIN_PTS = 100  ## Minimum number of points the scan should contain

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
#for cat in ['gg0lHi','LepHi']:
for cat in ['LepHi']:
    for mA in ['15','30','55']:
    #for mA in ['55']:
        #for fit in ['0x0','0x0smr','1x1C','1x1Csmr','2x2C']:
        #for fit in ['0x0smr','1x1C']:
        #for fit in ['0x0','0x0smr','1d1C']:
        for fit in ['0x0']:
            algo = 'MultiDimFit'
            base = 'higgsCombine.test'+algo
            suff = 'MultiDimFit.mH120.root'
            file_pattern = '%s/%s.%s.mA_%s.%s*%s.toy*.%s' % (IN_DIR, base, cat, mA, fit, SIGINJ, suff)
            in_files = glob.glob(file_pattern)
            if not '_sigBr_' in SIGINJ:
                #in_files = [inf for inf in in_files if not '_sigBr_' in inf] 
                in_files = [inf for inf in in_files if not ('mA_%s_sigBr_' % mA) in inf] 
            print('\nFound %d files matching pattern:' % len(in_files))
            print(file_pattern)

            ## Store best-fit r/NLL/pull and "2 sigma" r/NLL/pull with uncertainties
            fit_keys = [('r',float), ('rErr',float), ('NLL',float), ('NLLerr',float), ('pull',float), ('pullErr',float)]
            bst_pt = np.array([], dtype=fit_keys)  ## Best-fit values
            zro_pt = np.array([], dtype=fit_keys)  ## Values at r = 0
            #tsg_pt = np.array([], dtype=fit_keys)  ## Values at +2 sigma from best-fit
            #lim_pt = np.array([], dtype=fit_keys)  ## Values at 95% CL limit point

            iFile,nFiles,nEntry = 0,0,0
            for fName in in_files:
                iFile += 1
                if (iFile % int(np.sqrt(len(in_files)))) == 1:
                    print('Looking at file #%d / %d' % (iFile, len(in_files)))
                if not os.path.isfile(fName):
                    print('\nWEIRD ERROR! %s does not exist!' % fName)
                    continue
                in_file = R.TFile.Open(fName)
                if not in_file:
                    print('\nWEIRD ERROR! %s cannot be opened!' % fName)
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
                rCut = 0.01 if mA == '15' else (0.02 if mA == '30' else (0.03 if mA == '55' else 0.01))
                if val[0]['r'] > rCut:
                    print('\nERROR!!! File %d, first "r" = %.4f, not near 0. Code assumes scan starts from ~0. Skipping!' % (iFile, val[0]['r']))
                    print(fName)
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

                ## Fill best-fit and r=0 value arrays
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

                #tsg_pt = np.array([], fit_keys)  ## Values at +2 sigma from best-fit
                #lim_pt = np.array([], fit_keys)  ## Values at 95% CL limit point
                nFiles += 1
                in_file.Close()
            ## End loop: for fName in in_files

            print('\nFinished loop for %s %s %s: %d / %d files actually used (%d entries)\n\n' % (cat, mA, fit, nFiles, len(in_files), nEntry))

            injStr = SIGINJ if len(SIGINJ) > 0 else 'bkgOnly'
            h_str = 'h_MultiDim_%s_%s_%s_%s' % (cat, mA, fit, injStr)
            xMax = 0.05 if mA == '15' else (0.2 if mA == '30' else (0.5 if mA == '55' else 0.1))
            h_best_mu  = R.TH1F(h_str+'_best_fit_mu', h_str+'_best_fit_mu', 100, 0, xMax)
            h_zro_pull = R.TH1F(h_str+'_mu_zero_pull', h_str+'_mu_zero_pull', 40, 0, 4.0)

            for i in range(len(bst_pt)):
                h_best_mu.Fill(min(bst_pt[i]['r'], xMax-0.0001))
                h_zro_pull.Fill(min(zro_pt[i]['pull'], 3.999))
            h_best_mu.SetLineColor(R.kBlue)
            h_best_mu.SetLineWidth(2)
            h_zro_pull.SetLineColor(R.kBlue)
            h_zro_pull.SetLineWidth(2)

            ## Plot histograms
            for hst in [h_best_mu, h_zro_pull]:
                # Find median
                p = np.array([0.5])
                q = np.array([0.])
                hst.GetQuantiles(1, q, p)
                med = q[0]
                nZero = hst.GetBinContent(1)
                nHist = hst.Integral()
                del p,q
                print('\n%s median = %.3f (%d/%d = 0)' % (hst.GetName(), med, nZero, nHist))

                can = R.TCanvas(hst.GetName(), hst.GetName(), 800, 600)
                can.cd()
                hst.SetBinContent(1,0)  ## Zero out first bin for visualization
                hst.Draw("hist")

                ## Annotate with median, fraction of fits with mu = 0
                vstr = ''
                if 'best_fit_mu' in hst.GetName():
                    vstr = 'best-fit #mu'
                elif 'mu_zero_pull' in hst.GetName():
                    vstr = '#mu = 0 pull'
                ltx1 = R.TLatex()
                ltx1.SetNDC()
                ltx1.SetTextSize(0.04)
                ltx1.DrawLatex(0.15, 0.85, 'Median %s = %.4f' % (vstr, med))
                ltx2 = R.TLatex()
                ltx2.SetNDC()
                ltx2.SetTextSize(0.04)
                ltx2.DrawLatex(0.15, 0.75, '%d / %d have %s = 0' % (nZero, nHist, vstr))
                leg = R.TLegend(0.6, 0.75, 0.88, 0.88)
                leg.AddEntry(hst, '%s values (> 0)' % vstr, 'l')
                leg.Draw()

                can.SaveAs(OUT_DIR+'/'+hst.GetName()+'.png')
                del leg,ltx2,ltx1,can
            ## End loop: for hst in [h_best_mu, h_zro_pull]

        ## End loop: for fit in [
    ## End loop: for mA in [
## End loop: for cat in [
