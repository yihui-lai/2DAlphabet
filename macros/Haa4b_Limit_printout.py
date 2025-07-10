import os
import sys
import numpy as np
import ROOT as R

R.gROOT.SetBatch(True)
import glob
R.gStyle.SetOptStat(0)  ## Don't display stat boxes

OUT_DIR = './figures'
VERBOSE = False
SIGINJ = ''
MIN_QUANT = 5  ## Minimum number of quantileExpected points per file (6 if observed)

if not os.path.exists(OUT_DIR):
    os.mkdir(OUT_DIR)

## Store limit for each quantile for each categorization r/NLL/pull and "2 sigma" r/NLL/pull with uncertainties
lim_keys = [('limit',float), ('quant',float), ('cat',np.dtype('U15')), ('mA',np.dtype('U2'))]
limits = np.array([], dtype=lim_keys)  ## Asymptotic limits

## File pattern for limit output
for mA in ['12']+[str(5*iMA) for iMA in range(3,13)]:
#for mA in ['15','30','55']:
    #for mod in ['','A','B','C','D','E','F']:
    for DMC in ['MC','Data']:
        in_dir = 'output/%stoys/Mergecards/%s%srounded' % (DMC, DMC, DMC)
        for cat in ['LepLo']:
            for fit in ['0x0']:
                algo = 'AsymptoticLimits'
                base = 'higgsCombine.test'+algo
                suff = algo+'.mH120.root'
                #file_pattern = '%s/%s.%s%s.mA_%s.%s%s.MCrounded.%s' % (in_dir, base, cat, mod, mA, fit, SIGINJ, suff)
                file_pattern = '%s/%s.%s.mA_%s.%s%s.%s%srounded.%s' % (in_dir, base, cat, mA, fit, SIGINJ, DMC, DMC, suff)
                in_files = glob.glob(file_pattern)
                if not '_sigBr_' in SIGINJ:
                    in_files = [inf for inf in in_files if not ('mA_%s_sigBr_' % mA) in inf] 
                print('\nFound %d files matching pattern:' % len(in_files))
                print(file_pattern)
                assert(len(in_files) == 1)

                fName = in_files[0]
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

                iEntry = 0
                for entry in in_tree:
                    iEntry += 1
                    limit = np.array([(100*entry.limit, 100*entry.quantileExpected, str(cat+'_'+DMC), str(mA))], dtype=lim_keys)
                    limits = np.append(limits, limit)
                ## End loop: for entry in in_tree
                
                if iEntry < MIN_QUANT:
                    print('\nERROR!!! File %s has only %d entries!' % (in_files[0], iEntry))
                    print(fName)
                    continue

                in_file.Close()

            ## End loop: for fit in [
        ## End loop: for cat in [
    ## End loop: for mod in [
## End loop: for mA in [


## Print outputs
for iL in range(len(limits)):
    lim = limits[iL]
    if lim['quant'] != 50:
        continue
    assert(abs(limits[iL-2]['quant'] - 2.5) < 0.1)
    assert(abs(limits[iL-1]['quant'] - 16) < 0.1)
    assert(abs(limits[iL+1]['quant'] - 84) < 0.1)
    assert(abs(limits[iL+2]['quant'] - 97.5) < 0.1)
    #assert(abs(limits[iL+3]['quant'] - -100) < 0.1)
    #for jL in [iL-2, iL-1, iL+1, iL+2, iL+3]:
    for jL in [iL-2, iL-1, iL+1, iL+2]:
        assert(limits[jL]['cat'] == lim['cat'])
        assert(limits[jL]['mA']  == lim['mA'])
    print('mA = %s %s median expected limit = %.2f%%' % (lim['mA'], lim['cat'], lim['limit']))
    # if limits[iL+3]['limit'] < limits[iL-2]['limit'] or limits[iL+3]['limit'] > limits[iL+2]['limit']:
    #     print('  * WARNING!!! Observed limit %.2f%% outside 95% CL expected!!! (%.2f%% - %.2f%%)' % (limits[iL+3]['limit'], limits[iL-2]['limit'], limits[iL+2]['limit']))
    # elif limits[iL+3]['limit'] < limits[iL-2]['limit'] or limits[iL+3]['limit'] > limits[iL+2]['limit']:
    #     print('  * Notable: Observed limit %.2f%% outside 68% CL expected. (%.2f%% - %.2f%%)' % (limits[iL+3]['limit'], limits[iL-1]['limit'], limits[iL+1]['limit']))
