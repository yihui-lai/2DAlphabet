## Based on example.py
## Modified for boosted Higgs to aa to 4b search
## 2D fit to mass of Higgs (AK8 jet) and mass of "a" boson (ParticleNet regression)
## Mass-decorrelated Hto4b ParticleNet tagger used to define pass/fail regions
## Both gluon fusion (ggH) and associated production modes used
## - Andrew Brinkerhoff (abrinke1), May 2024, Baylor University

from time import time
from TwoDAlphabet import plot
from TwoDAlphabet.twoDalphabet import MakeCard, TwoDAlphabet
from TwoDAlphabet.alphawrap import BinnedDistribution, ParametricFunction
from TwoDAlphabet.helpers import make_env_tarball
import os
import sys
import math

VERBOSE = True
NTOY    = 100       ## Number of toys for goodness-of-fit (GoF) test
CAT     = 'XXHi'    ## Event selection category, e.g. gg0l, VBFjj, Wlv, Zll, Zvv, ...
#CAT     = 'XXLo'    ## Event selection category, e.g. gg0l, VBFjj, Wlv, Zll, Zvv, ...
#CAT     = 'gg0lIncl'
#CAT     = 'VBFjjLo_Xto4bv2'
CAT     = 'VBFjjHi_Xto4bv2'



CATL    = CAT       ## Selection category with lepton "l" instead of mu "m" or ele "e"
MASSH   = 'pnet'    ## Higgs mass regression (mass, msoft, pnet)
MASSESA = ['15','30','55']  ## Masses of "a" boson
MASSA   = ('%sto%s' % (MASSESA[0], MASSESA[-1]) if len(MASSESA) > 1 else MASSESA[0])
WP      = 'WP60'    ## Hto4b efficiency working point
YEAR    = '2018'    ## Data year
UseMCToy = True
toys=0
## Polynomial fit: "x" for 2D with cross terms, "d" without cross terms
## Prefix "e" for exponential, suffix "C" for centered at 0 or "M" for mass ratio
# FITLIST = ['0x0','1x0','0x1','1x1','1x2','2x1','2x2','1d1','2d1','1d2','2d2',
#            'e0x0','e1x0','e0x1','e1x1','e1x2','e2x1','e2x2','e2d1','e1d2','e2d2']
SS_DIR = '/eos/cms/store/user/ssawant/htoaa/analysis/'
HB_DIR = '/afs/cern.ch/user/h/hboucham/public/'
MD_DIR = '/afs/cern.ch/user/m/moanwar/public/'
AB_DIR = '/afs/cern.ch/work/a/abrinke1/public/HiggsToAA/coffea/eventloop/plots/'
YH_DIR = '/afs/cern.ch/work/y/yilai/Haa4b/datacards/CMSSW_11_3_4/src/2DAlphabet/plots/'

if CAT == 'gg0l' or CAT == 'gg0lIncl' or CAT == 'gg0lHi' or CAT == 'gg0lLo':
    # PATH    = SS_DIR+'20240530_ggH0l_for2DAlphabet/2018/2DAlphabet_inputFiles'
    PATH    = 'plots/HtoAA_2DAlphabet_merge_inputs_gg0lIncl/2025_04_04_mAa/'
    SIGS    = ['ggH', 'WH','ttH','ZH', 'VBFH']
    FIT     =  '2d2C'  ## Reasonable GoF for both WP40 and WP60
    FITLIST = ['2d2C']
    NOMTF   = 0.1
    MASSH   = 'pnet_vs_massA34a'    ## Higgs mass regression (mass, msoft, pnet)
    WP      = 'WP40'    ## Hto4b efficiency working point
if CAT == 'VBFjj':
    PATH    = MD_DIR+'forAndrew/2DAlphabetfiles'
    SIGS    = ['VBFH']
    FIT     =  '2d2C'
    FITLIST = ['2d2C']
    NOMTF   = 0.10    ## Nominal fail-to-pass transfer factor (10%)
if CAT == 'VBFjjLo_Xto4bv2':
    PATH    = 'plots/2DAlphabetfiles_VBF_inputs/VBFLo_Xto4bv2/'
    SIGS    = ['VBFH']
    FIT     =  '2d2C'  ## Reasonable GoF for both WP40 and WP60
    FITLIST = ['2d2C']
    WP      = 'WP40'    ## Hto4b efficiency working point
    NOMTF   = (0.1 if WP == 'WP40' else 0.6)
if CAT == 'VBFjjHi_Xto4bv2':
    PATH    = 'plots/2DAlphabetfiles_VBF_inputs/VBFHi_Xto4bv2/'
    SIGS    = ['VBFH']
    FIT     =  '2d2C'  ## Reasonable GoF for both WP40 and WP60
    FITLIST = ['2d2C']
    WP      = 'WP40'    ## Hto4b efficiency working point
    NOMTF   = (0.1 if WP == 'WP40' else 0.6)
if CAT == 'Vjj':
    # PATH    = SS_DIR+'20240530_VHHadronicMode_for2DAlphabet_1/2018/2DAlphabet_inputFiles'
    PATH    = SS_DIR+'20240626_Vjj/2018/2DAlphabet_inputFiles/Vjj'
    SIGS    = ['WH','ZH']
    FIT     =  '1d1C'
    FITLIST = ['1d1C']
    NOMTF   = (0.15 if WP == 'WP40' else 0.22)
if CAT == 'Wlv' or CAT == 'Wmv' or CAT == 'Wev':
    PATH    = HB_DIR+'2D_Wlv_052824/%s' % WP
    CATL    = 'Wlv'
    SIGS    = ['WH']
    FIT     =  '1x1C'
    FITLIST = ['1x1C']
    NOMTF   = 0.12    ## Nominal fail-to-pass transfer factor (12%)
if CAT == 'WlvLo' or CAT == 'ttblv':
    PATH    = HB_DIR+'2D_062324/%s' % WP
    SIGS    = ['WH'] if CAT.startswith('Wlv') else ['ttH']
    FIT     =  '1x1C'
    FITLIST = ['1x1C']
    NOMTF   = 0.10    ## Nominal fail-to-pass transfer factor (8-12%)
if CAT == 'Zvv' or CAT == 'ZvvHi' or CAT == 'ZvvLo':
    # PATH    = SS_DIR+'20240529_ZH_4b2nu_for2DAlphabet/2018/2DAlphabet_inputFiles'
    PATH    = SS_DIR+'20240626_Zvv_METDataset_2/2018/2DAlphabet_inputFiles/'+CAT
    SIGS    = ['ZH']
    FIT     =  '1d1C'
    FITLIST = ['1d1C']
    NOMTF   = 0.17
if CAT == 'Zll' or CAT == 'Zmm' or CAT == 'Zee':
    PATH    = HB_DIR+'2D_Alphabet_root_052424/%s' % WP
    CATL    = 'Zll'
    SIGS    = ['ZH']
    FIT     =  '0x0'  ## Default for Z to ll: flat transfer factor
    FITLIST = ['0x0']
    NOMTF   = 0.18    ## Nominal fail-to-pass transfer factor (18%)
if CAT == 'LepHi' or CAT == 'XXHi':  ## WlvHi + ttbblv + ttbll + ttbbll + Zll + ZvvHi
    PATH    = YH_DIR+'HtoAA_2DAlphabet_merge_inputs_'+CAT+'/2025_04_04_mAa'
    SIGS    = ['WH','ttH','ZH']
    FIT     =  '1d1C'
    FITLIST = ['1d1C']
    NOMTF   = 0.11
if CAT == 'XXLo':  ## WlvLo + ttblv + ZvvLo
    PATH    = YH_DIR+'HtoAA_2DAlphabet_merge_inputs_'+CAT+'/2025_04_04_mAa'
    SIGS    = ['WH','ttH']
    FIT     =  '1x1C'
    FITLIST = ['1x1C']
    NOMTF   = 0.11


'''--------------------------Helper functions---------------------------'''
def _sig_names():
    '''Set up list of signal names for multiple Higgs production modes, mass(a) values'''
    signames = []
    for sig in SIGS:
        for massA in MASSESA:
            signames.append('%s_%stoaato4b_mA_%s_%s' % (CAT, sig, massA, YEAR))
    return signames

def _select_signal(row, args):
    '''Used by the Ledger.select() method to create a subset of a Ledger.
    This function provides the logic to determine which entries/rows of the Ledger
    to keep for the subset. The first argument should always be the row to process.
    The arguments that follow will be the other arguments of Ledger.select().
    This function should ALWAYS return a bool that signals whether to keep (True)
    or drop (False) the row.

    To check if entries in the Ledger pass, we can access a given row's 
    column value via attributes which are named after the columns (ex. row.process
    gets the "process" column). One can also access them as keys (ex. row["process"]).

    In this example, we want to select for signals that have a specific string
    in their name ("process"). Thus, the first element of `args` contains the string
    we want to find.

    We also want to pick a transfer factor (TF) to use so the second element of `args`
    contains a string to specify the Background_args[1] process we want to use.

    Args:
        row (pandas.Series): The row to evaluate.
        args (list): Arguments to pass in for the evaluation.
    Returns:
        Bool: True if keeping the row, False if dropping.
    '''
    if VERBOSE > 1: print('_select_signal: type = %s, process = %s,' % (row.process_type, row.process)
                          +'signame = %s, order = %s' % (args[0], args[1]))
    signame    = args[0]
    poly_order = args[1]
    if row.process_type == 'SIGNAL':
        if signame in row.process:
            return True
        else:
            return False
    elif 'Background_' in row.process:
        if row.process == CAT+'Background_'+poly_order:
            return True
        else:
            return False
    else:
        return True

def _load_rpf(poly_order):
    if UseMCToy:
        twoD_for_rpf = TwoDAlphabet('fits_%s_Htoaato4b_mH_%s_mA_%s_%s_%s' % (CAT, MASSH, MASSA, WP, YEAR),
                                'mctoysjson/%s_Htoaato4b_mctoy%s.json' % (CATL, str(toys)), loadPrevious=True,
                                findreplace={'path':PATH, 'SIGNAME':_sig_names(),
                                             'HIST':'$process_%s_%s_$region_Nom' % (MASSH, WP)})
    else:
        twoD_for_rpf = TwoDAlphabet('fits_%s_Htoaato4b_mH_%s_mA_%s_%s_%s' % (CAT, MASSH, MASSA, WP, YEAR),
                                '%s_Htoaato4b.json' % CATL, loadPrevious=True,
                                findreplace={'path':PATH, 'SIGNAME':_sig_names(),
                                             'HIST':'$process_%s_%s_$region_Nom' % (MASSH, WP)})
    params_to_set = twoD_for_rpf.GetParamsOnMatch('rpf.*'+poly_order, 'mA_all_area', 'b')
    return {k:v['val'] for k,v in params_to_set.items()}

def _load_rpf_as_SR(poly_order):
    params_to_set = {}
    for k,v in _load_rpf(poly_order).items():
        params_to_set[k.replace('CR','SR')] = v
    return params_to_set

def _generate_constraints(fit_poly):
    out = {}
    for j in reversed(range(99)):
        if '@'+str(j) in fit_poly:
            nparams = j+1
            break
    for i in range(nparams):
        if i == 0:
            out[i] = {"MIN":-100.0, "MAX":100.0, "NOM":NOMTF, "ERROR":NOMTF}
        else:
            out[i] = {"MIN":-100.0, "MAX":100.0, "NOM":0.00, "ERROR":1.0},
    return out

def _generate_poly(fit_name, verb=False):
    fit_poly = ''
    n_params = -1
    if   '0x0' in fit_name: fit_poly = '@0'
    elif '1x0' in fit_name: fit_poly = '@0*(1+@1*x)'
    elif '0x1' in fit_name: fit_poly = '@0*(1+@1*y)'
    elif '1x1' in fit_name: fit_poly = '@0*((1+@1*x)*(1+@2*y)+@3*x*y)'
    elif '2x1' in fit_name: fit_poly = '@0*((1+@1*x+@4*x*x)*(1+@2*y)+@3*x*y+@5*x*x*y)'
    elif '1x2' in fit_name: fit_poly = '@0*((1+@1*x)*(1+@2*y+@4*y*y)+@3*x*y+@5*x*y*y)'
    elif '2x2' in fit_name: fit_poly = '@0*((1+@1*x+@4*x*x)*(1+@2*y+@5*y*y)+@3*x*y+@6*x*x*y+@7*x*y*y+@8*x*x*y*y)'
    elif '1d1' in fit_name: fit_poly = '@0*((1+@1*x)*(1+@2*y))'
    elif '2d1' in fit_name: fit_poly = '@0*((1+@1*x+@3*x*x)*(1+@2*y))'
    elif '1d2' in fit_name: fit_poly = '@0*((1+@1*x)*(1+@2*y+@3*y*y))'
    elif '2d2' in fit_name: fit_poly = '@0*((1+@1*x+@3*x*x)*(1+@2*y+@4*y*y))'
    else:
        print('\n\n*** ERROR! %s not in the list! Quitting. ***' % fit_name)
        print(FITLIST)
        sys.exit()
    if verb: print('\nUsing fit function %s: %s' % (fit_name, fit_poly))
    ## Variable replacements: "C" = central, "M" = mass ratio
    ## "M" gives m(a)/m(H) for m(a) = [10,62], m(H) = [60,220]
    fit_len = len(fit_name)
    if fit_name.startswith('e'): fit_len -= 1
    if fit_len > 3:
        if fit_name.endswith('C'):
            if verb: print('  * Replacing "x" with "x-0.5" in fit function')
            fit_poly = fit_poly.replace('x','(x-0.5)')
            if fit_len == 4:
                if verb: print('  * Replacing "y" with "y-0.5" in fit function')
                fit_poly = fit_poly.replace('y','(y-0.5)')
            elif fit_name[3] == 'M' or (fit_name.startswith('e') and fit_name[4] == 'M'):
                if verb: print('  * Replacing "y" with "((y+(10/52)-0.5)/(x+(60/160)))" in fit function')
                fit_poly = fit_poly.replace('y','((y+(10/52)-0.5)/(x+(60/160)))')
            else:
                print('\n\n*** ERROR! Invalid fit function %s! Quitting. ***' % fit_name)
                sys.exit()
        elif fit_len == 4 and fit_name.endswith('M'):
            if verb: print('  * Replacing "y" with "((y+(10/52))/(x+(60/160)))" in fit function')
            fit_poly = fit_poly.replace('y','((y+(10/52))/(x+(60/160)))')
        else:
            if verb: print('\n\n*** ERROR! Invalid fit function %s! Quitting. ***' % fit_name)
            sys.exit()
    if fit_name.startswith('e'):
            if verb: print('  * Starting fit function with exponential')
            fit_poly = 'exp(-2.32+'+fit_poly+')'
    if verb: print('Final form: %s\n' % (fit_poly))
    return fit_poly

## End function: _generate_poly(fit_name)

def _get_rpf_options():
    _rpf_options = {}
    for fName in FITLIST:
        if VERBOSE: print('Inside _get_rpf_options, running _generate_poly(%s)' % fName)
        fit_poly = _generate_poly(fName)
        _rpf_options[fName] = { 'form': fit_poly,
                                'constraints': _generate_constraints(fit_poly) }
        if VERBOSE: print(_rpf_options[fName])
    return _rpf_options

'''---------------Primary functions---------------------------'''
def test_make(SRorCR):
    if VERBOSE: print('\nInside test_make(%s)' % SRorCR)
    '''Constructs the workspace for either the CR or SR.
    Args: SRorCR (str): 'SR' or 'CR'.
    '''
    assert SRorCR in ['SR','CR']

    # Create the twoD object which starts by reading the JSON config and input arguments to
    # grab input simulation and data histograms, rebin them if needed, and save them all
    # in one place (organized_hists.root). The modified JSON config (with find-replaces applied, etc)
    # is also saved as runConfig.json. This means, if you want to share your analysis with
    # someone, they can grab everything they need from this one spot - no need to have access to
    # the original files! (Note though that you'd have to change the config to point to organized_hists.root).

    # TwoDAlphabet class defined in TwoDAlphabet/twoDalphabet.py
    # First argument is the "tag", i.e. output directory name, in this case including the
    # Higgs production mode (CAT), AK8 mass algo (MASSH), and signal "a" boson mass (MASSA)
    # Second argument is JSON config file, third argument says we're starting from scratch
    # findreplace adds lines to GLOBAL part of JSON (_addFindReplace in TwoDAlphabet/config.py)
    # in this case a specific signal model (production mode and "a" boson mass)
    # 'SIGNAME' also gets used as the $process in _batch_replace
    if UseMCToy:
        twoD = TwoDAlphabet('fits_%s_Htoaato4b_mH_%s_mA_%s_%s_%s' % (CAT, MASSH, MASSA, WP, YEAR),
                        'mctoysjson/%s_Htoaato4b_mctoy%s.json' % (CATL, str(toys)), loadPrevious=False, verbose=VERBOSE,
                        findreplace={'path':PATH, 'SIGNAME':_sig_names(),
                                     'HIST':'$process_%s_%s_$region_Nom' % (MASSH, WP)})
    else:
        twoD = TwoDAlphabet('fits_%s_Htoaato4b_mH_%s_mA_%s_%s_%s' % (CAT, MASSH, MASSA, WP, YEAR),
                        '%s_Htoaato4b.json' % CATL, loadPrevious=False, verbose=VERBOSE,
                        findreplace={'path':PATH, 'SIGNAME':_sig_names(),
                                     'HIST':'$process_%s_%s_$region_Nom' % (MASSH, WP)})
    if VERBOSE: print('Completed first TwoDAlphabet with loadPrevious=False')
    # Initial "QCD" template simply equals data - all MC backgrounds
    # Is this really what we want for the "Pass" region as well? - AWB 2024.05.21
    qcd_hists = twoD.InitQCDHists(VERBOSE)

    # This loop will only run once since the only regions are pass or fail
    for ps, fl in [['Pass', 'Fail'] for r in twoD.ledger.GetRegions() if r == 'Pass']:
        if VERBOSE: print('ps = %s, fl = %s' % (ps, fl))
        # Gets the Binning object and meta information (`_unused`) that we don't care about.
        # The Binning object is needed for constructing the Alphabet objects.
        # If one wanted to be very robust, they could get the binning for `ps` and `fl`
        # separately and check that the binning is consistent between the two.
        binning_f, _unused = twoD.GetBinningFor(fl, VERBOSE)
        if VERBOSE: print(binning_f)

        # Next we construct the Alphabet objects which all inherit from the Generic2D class.
        # This class constructs and stores RooAbsArg objects (RooRealVar, RooFormulaVar, etc)
        # which represent each bin in the space.

        # First we make a BinnedDistribution which is a collection of RooRealVars built from a starting
        # histogram (`qcd_hists[fl]`). These can be set to be "constant" but, if not, they become free floating
        # parameters in the fit. Bins <= 0 are forced to 1e-9 ("forcePositive" in TwoDAlphabet/alphawrap.py).
        # If bin and at least 7 of 8 "neighbors" are 0, bin value is fixed to constant 0.
        # Otherwise set to max(bin value, 5) with pre-fit uncertainty of 1e-6 to 1e6. Revisit? - AWB 2024.05.21
        fail_name = CAT+'Background_'+fl
        qcd_f = BinnedDistribution(
                    fail_name, qcd_hists[fl],
                    binning_f, constant=False,
                    forcePositive=True, verbose=VERBOSE
                )

        # We add it to `twoD` so its included when making the RooWorkspace and ledger.
        # We specify the name of the process, the region it lives in, and the object itself.
        # The process is assumed to be a background and colored yellow but this can be changed
        # with optional arguments.
        twoD.AddAlphaObj(CAT+'Background', fl, qcd_f)

        # As global variables, we've defined some different transfer function (TF) options.
        # We only want to include one of these at the time of fitting but we want to construct
        # them all right now so we can pick and choose later.
        rpf_options = _get_rpf_options()
        for opt_name in rpf_options.keys():
            # We have two regions determined by a TF, "pass" and "fail" with the "pass"
            # being a parametric scaling of the "fail". The functional form and the
            # dictionary of constraints is defined in _rpf_options so we just plug
            # these in, being careful to name the objects uniquely (this affects
            # the naming of the RooFormulaVars created, which need to be unique).

            # The ParametricFunction class is the same as the BinnedDistribution except
            # the bins are RooFormulaVars constructed from the input formula with the
            # "x" and "y" taken as the centers of each bin.
            # The constraints option takes as input a dictionary with keys that control
            # the minimum, maximum, and error (initial step) of each parameter. It can
            # also be used to specify if the parameter should be unconstrainted (flatParam)
            # or Gaussian constrained (param <mu> <sigma>).
            # By default bin values are forced to be >= 1e-9 for any parameter values (forcePositive)
            # Does this lead to any non-linear behavior? How does it affect uncertainties? - AWB 2024.05.021
            if VERBOSE: print('  * For opt_name = %s, booking qcd_rpfL ParametricFunction' % opt_name)
            opt_fit = rpf_options[opt_name]
            qcd_rpf = ParametricFunction(
                       (fail_name.replace('Fail','rpfL')).replace('fail','rpfL')+'_'+opt_name,
                       binning_f, opt_fit['form'],
                       constraints=opt_fit['constraints'], forcePositive=True
                   )
            
            # Of course, what we actually need is these TFs multiplied by something else:
            #     qcd_p = qcd_f*rpf
            # The Multiply method will make a new set of RooFormulaVars defined by multiplying the RooAbsArgs
            # of each object together. Other methods exist for adding and dividing, where Add() can take an
            # optional factor so that subtraction is possible.
            qcd_p = qcd_f.Multiply(fail_name.replace('Fail','Pass')+'_'+opt_name, qcd_rpf)

            # Now add the final models to the `twoD` object for tracking
            # Note that we have unique process names so they are identifiable
            # but we give them different titles so that they look pretty in
            # the final plot legends. First two args are just strings (process and region).
            twoD.AddAlphaObj(CAT+'Background_'+opt_name, ps, qcd_p, title=CAT+'Background')

    # Save() will save the RooWorkspace and the ledgers and other associated pieces
    # so the twoD object can be reconstructed later. If this line doesn't run or
    # if something in the above needs to change, everything will need to be re-run to this point.
    twoD.Save()
    if VERBOSE: print('\nFinished test_make(%s)!' % SRorCR)

def test_fit(SRorCR):
    '''Loads a TwoDAlphabet object from an existing project area, selects
    a subset of objects to run over (a specific signal and TF), makes a sub-directory
    to store the information, and runs the fit in that sub-directory. To make clear
    when a directory/area is being specified vs when a signal is being selected,
    I've redundantly prepended the "subtag" argument with "_area".
    '''
    if SRorCR == 'SR':
        print('\n\nWARNING!!! You may be unblinding prematurely!!!\n\n')

    # So that the find-replace in the config doesn't need to be done again if I want
    # the SR (since it would have been performed already by test_make()), I grab
    # the runConfig.json that's already been saved in the created directory.
    working_area = 'fits_%s_Htoaato4b_mH_%s_mA_%s_%s_%s' % (CAT, MASSH, MASSA, WP, YEAR)
    twoD = TwoDAlphabet(working_area, '%s/runConfig.json' % working_area, loadPrevious=True)

    # Access the Ledger and perform a selection on it to create a subset
    # from which to build the card. One can modify the Ledger DataFrames
    # manually to do more sophisticated manipulations but the select()
    # method will not modify the Ledger in-place. It always generates a new Ledger
    # which, by itself, is only stored in memory.

    # Create a subset of the primary ledger using the select() method.
    # The select() method takes as a function as its first argument
    # and any args to pass to that function as the remiaining arguments
    # to select(). See _select_signal for how to construct the function.
    # Construct subsets for all mA values together and for middle mA.
    midMA = MASSESA[math.floor(len(MASSESA) / 2)]
    subsetAll = twoD.ledger.select(_select_signal, 'Htoaato4b_mA_', FIT)
    subsetMid = twoD.ledger.select(_select_signal, '%s_%stoaato4b_mA_%s_%s' % (CAT, SIGS[0], midMA, YEAR), FIT)

    # Make card reads the ledger and creates a Combine card from it.
    # The second argument specifices the sub-directory to save the card in.
    # MakeCard() will also save the corresponding Ledger DataFrames as csvs
    # in the sub-directory for later reference/debugging. By default, MakeCard()
    # will reference the base.root workspace in the first level of the project directory
    # (../ relative to the card). However, one can specify another path if a different
    # workspace is desired. Additionally, a different dataset can be supplied via
    # toyData but this requires supplying almost the full Combine card line and
    # is reserved for quick hacks by those who are familiar with Combine cards.
    twoD.MakeCard(subsetAll, 'mA_all_area')
    twoD.MakeCard(subsetMid, 'mA_%s_area' % midMA)

    # Run the fit! Will run in the area specified by the `subtag` (ie. sub-directory) argument
    # and use the card in that area. Via the cardOrW argument, a different card or workspace can be
    # supplied (passed to the -d option of Combine). 
    twoD.MLfit('mA_all_area', rMin=0, rMax=20, verbosity=0)
    twoD.MLfit('mA_%s_area' % midMA, rMin=0, rMax=20, verbosity=0)

def test_plot(SRorCR):
    '''Load the twoD object again and run standard plots for a specific subtag.
    Assumes loading the Ledger in this sub-directory but a different one can
    be provided if desired.
    '''
    if SRorCR == 'SR':
        print('\n\nWARNING!!! You may be unblinding prematurely!!!\n\n')
    working_area = 'fits_%s_Htoaato4b_mH_%s_mA_%s_%s_%s' % (CAT, MASSH, MASSA, WP, YEAR)
    twoD = TwoDAlphabet(working_area, '%s/runConfig.json' % working_area, loadPrevious=True)
    midMA = MASSESA[math.floor(len(MASSESA) / 2)]
    subsetMid = twoD.ledger.select(_select_signal, '%s_%stoaato4b_mA_%s_%s' % (CAT, SIGS[0], midMA, YEAR), FIT)
    twoD.StdPlots('mA_%s_area' % midMA, subsetMid)
    ## For some reason PostFit2DShapesFromWorkspace segfaults in mA_all_area - AWB 2024.05.25
    subsetAll = twoD.ledger.select(_select_signal, 'Htoaato4b_mA_', FIT)
    twoD.StdPlots('mA_all_area', subsetAll)

def test_limit(SRorCR):
    '''Perform a blinded limit. To be blinded, the Combine algorithm (via option `--run blind`)
    will create an Asimov toy dataset from the pre-fit model. Since the TF parameters are meaningless
    in our true "pre-fit", we need to load in the parameter values from a different fit so we have
    something reasonable to create the Asimov toy. 
    '''
    # Returns a dictionary of the TF parameters with the names as keys and the post-fit values as dict values.
    params_to_set = _load_rpf_as_SR(FIT) if SRorCR == 'SR' else _load_rpf()
    working_area = 'fits_%s_Htoaato4b_mH_%s_mA_%s_%s_%s' % (CAT, MASSH, MASSA, WP, YEAR)
    twoD = TwoDAlphabet(working_area, '%s/runConfig.json' % working_area, loadPrevious=True)

    # The iterWorkspaceObjs attribute stores the key-value pairs in the JSON config 
    # where the value is a list. This allows for later access like here so the user
    # can loop over the list values without worrying if the config has changed over time
    # (necessitating remembering that it changed and having to hard-code the list here).
    if VERBOSE: print ('Possible signals: %s' % twoD.iterWorkspaceObjs['SIGNAME'])

    ## for signame in twoD.iterWorkspaceObjs['SIGNAME']:
    areaname = None
    for massA in MASSESA:
        signame = 'Htoaato4b_mA_%s_%s' % (massA, YEAR)
        areaname = 'mA_%s_area' % massA
        print ('Performing limit for %s in %s' % (signame, areaname))

        # Make a subset and card as in test_fit()
        subset = twoD.ledger.select(_select_signal, signame, FIT)
        twoD.MakeCard(subset, areaname)
        # Run the blinded limit with our dictionary of TF parameters
        twoD.Limit(
            subtag=areaname,
            blindData=True,
            verbosity=0,
            setParams=params_to_set,
            condor=False
        )

def test_GoF(SRorCR):
    '''Perform a Goodness of Fit test using an existing working area.
    Requires using data so SRorCR is enforced to be 'CR' to avoid accidental unblinding.
    '''
    if SRorCR == 'SR':
        print('\n\nWARNING!!! You may be unblinding prematurely!!!\n\n')

    working_area = 'fits_%s_Htoaato4b_mH_%s_mA_%s_%s_%s' % (CAT, MASSH, MASSA, WP, YEAR)
    twoD = TwoDAlphabet(working_area, '%s/runConfig.json' % working_area, loadPrevious=True)

    # If the card doesn't exist, make it (in the case that test_fit() wasn't run first).
    # Only need to run with one signal model, since we fix signal strength to 0 anyway.
    midMA = MASSESA[math.floor(len(MASSESA) / 2)]
    signame = '%s_%stoaato4b_mA_%s_%s' % (CAT, SIGS[0], midMA, YEAR)
    areaname = 'mA_%s_area' % midMA
    if not os.path.exists(twoD.tag+'/'+areaname+'/card.txt'):
        subset = twoD.ledger.select(_select_signal, signame, FIT)
        twoD.MakeCard(subset, areaname)
    # Run the Goodness of fit test with NTOY toys, r frozen to 0, TF parameters set to prefit.
    # This method always runs the evaluation on data interactively but the toy generation and evaluation
    # can be sent to condor with condor=True and split over several jobs with njobs=<int>.
    # Note that running a GoF test without data is relatively meaningless so by using this method,
    # you must unblind data. If you wish to use a toy dataset instead, you should set that
    # up when making the card.
    twoD.GoodnessOfFit(
        areaname, ntoys=NTOY, freezeSignal=0,
        condor=False, njobs=1
    )

    # Note that no plotting is done here since one needs to wait for the condor jobs to finish first.
    # See test_GoF_plot() for plotting (which will also collect the outputs from the jobs).

def test_SigInj(SRorCR, massA):
    '''Perform a signal injection test'''
    assert SRorCR in ['SR','CR']

    signame = '%s_%stoaato4b_mA_%s_%s' % (CAT, SIGS[0], massA, YEAR)
    areaname = 'mA_%s_area' % massA
    working_area = 'fits_%s_Htoaato4b_mH_%s_mA_%s_%s_%s' % (CAT, MASSH, MASSA, WP, YEAR)
    twoD = TwoDAlphabet(working_area, '%s/runConfig.json' % working_area, loadPrevious=True)

    # If the card doesn't exist, make it (in the case that test_fit() wasn't run first).
    if not os.path.exists(twoD.tag+'/'+areaname+'/card.txt'):
        subset = twoD.ledger.select(_select_signal, signame, FIT)
        twoD.MakeCard(subset, areaname)

    # Perform the signal injection test with r=0 and with NTOY toys split over 10 jobs on condor.
    # Because the data is blinded, we feed in the parameters from a previous fit so that we
    # have a model from which to generate toys.
    twoD.SignalInjection(
        areaname, injectAmount=0,
        ntoys=NTOY,
        blindData=True,
        setParams=_load_rpf_as_SR(FIT),
        condor=False, njobs=1)

def test_GoF_plot(SRorCR):
    '''Plot the GoF in fits_<CAT>_Htoaato4b_mH_<MASSH>_mA_<MASSA>_<WP>_<YEAR>/mA_<MASSA>_area (condor=True indicates that condor jobs need to be unpacked)'''
    midMA = MASSESA[math.floor(len(MASSESA) / 2)]
    plot.plot_gof('fits_%s_Htoaato4b_mH_%s_mA_%s_%s_%s' % (CAT, MASSH, MASSA, WP, YEAR),
                  'mA_%s_area' % midMA, condor=False)

def test_SigInj_plot(SRorCR, massA):
    '''Plot the signal injection test for r=0 injected and stored in fits_<CAT>_Htoaato4b_mH_<MASSH>_mA_<MASSA>_<WP>_<YEAR>/mA_<MASSA>_area
    (condor=True indicates that condor jobs need to be unpacked)'''
    plot.plot_signalInjection('fits_%s_Htoaato4b_mH_%s_mA_%s_%s_%s' % (CAT, MASSH, MASSA, WP, YEAR),
                              'mA_%s_area' % massA, injectedAmount=0, condor=False)

def test_Impacts(SRorCR, massA):
    '''Calculate the nuisance parameter impacts. The parameters corresponding to the unconstrained bins
    of the fail region are ignored. Assumes that a fit has already been performed so that the post-fit
    uncertainties can be used for the scans. However, another card or workspace can be specified as well
    as a dictionary of parameters to set before running (setParams). With blindData=True, a pre-fit Asimov
    toy is generated for the sake of performing the scans. Since we're using the SR, blindData is set to True
    '''
    if SRorCR == 'SR':
        print('\n\nWARNING!!! You may be unblinding prematurely!!!\n\n')
    working_area = 'fits_%s_Htoaato4b_mH_%s_mA_%s_%s_%s' % (CAT, MASSH, MASSA, WP, YEAR)
    twoD = TwoDAlphabet(working_area, '%s/runConfig.json' % working_area, loadPrevious=True)

    # We need to run impacts in the SR for them to make sense but we can't use the data in the SR while blinded.
    # So we need a toy to play with instead.
    subset = twoD.ledger.select(_select_signal, '%s_%stoaato4b_mA_%s_%s' % (CAT, SIGS[0], massA, YEAR), FIT)
    # Make a new area to play in
    twoD.MakeCard(subset, 'mA_%s_impactArea' % massA)

    # Generate the toy
    toy_file_path = twoD.GenerateToys(
        'impactToy', 'mA_%s_impactArea' % massA,
        card='card.txt',
        workspace=None,
        ntoys=1, seed=123456, expectSignal=0,
        setParams=_load_rpf_as_SR(FIT)
    )
    # Run the parameter impacts on the toy with the pre-fit workspace/card
    twoD.Impacts(
        'mA_%s_impactArea' % massA,
        cardOrW='card.txt', blindData=True,
        extra='-t 1 --toysFile %s' % toy_file_path.split('/')[-1]
    )

def test_generate_for_SR(massA):
    '''NOTE: This is an expert-level manipulation that requires understanding the underlying Combine
    commands. Use and change it only if you understand what each step is doing.
    
    Use the CR fit result to generate and fit a toy in the SR (without looking at SR data).
    There are two ways to do this which will be broken up into toyArea1 and toyArea2.'''
    # Load in the SR TwoDAlphabet object
    working_area = 'fits_%s_Htoaato4b_mH_%s_mA_%s_%s_%s' % (CAT, MASSH, MASSA, WP, YEAR)
    twoD = TwoDAlphabet(working_area, '%s/runConfig.json' % working_area, loadPrevious=True)

    subset = twoD.ledger.select(_select_signal, '%s_%stoaato4b_mA_%s_%s' % (CAT, SIGS[0], massA, YEAR), FIT)
    params_to_set = _load_rpf_as_SR(FIT)

    ###################################
    #-------- Version 1 --------------#
    ###################################
    # We'll make a card for each version to ensure the directory structure is made - they will be identical though to start.
    twoD.MakeCard(subset, 'mA_%s_toyArea1' % massA)

    # Perform a fit as normal but via the `extra` arg, provide some commands
    # directly to combine to generate 1 toy, with seed 123456, and with r=0.
    # Note that --expectSignal 0 will generate with r=0 AND fit with r=0.
    twoD.MLfit(
        subtag='mA_%s_toyArea1' % massA,
        setParams=params_to_set,
        rMin=0,rMax=5,verbosity=0,
        extra='-t 1 -s 123456 --expectSignal 0'
    )
    # Plot!
    twoD.StdPlots('mA_%s_toyArea1' % massA, ledger=subset)

    ###################################
    #-------- Version 2 --------------#
    ###################################
    # We'll make a card for each version to ensure the directory structure is made - they will be identical though to start.
    twoD.MakeCard(subset, 'mA_%s_toyArea2' % massA)
    # First generate a toy by itself. This means we can set r for *just* this step
    # as opposed to Version 1 where r was set for generation and for fitting.
    # Note that this method will generate frequentist toys but always skip the frequentist fit.
    # So if you'd like to generate from a post-fit workspace, you should fit first
    # and then provide a workspace snapshot
    toy_file_path = twoD.GenerateToys(
        'toys', 'mA_%s_toyArea2' % massA,
        card='card.txt', workspace=None, # A card or workspace MUST be defined manually or one of these options should be set to True to use a default.
        ntoys=1, seed=123456, expectSignal=0,
        setParams=params_to_set
    )
    # Perform a fit as normal but via the `extra` arg, tell combine
    # to access our already-generated toy.
    # Note that r is now freely floating in this fit again.
    twoD.MLfit(
        subtag='mA_%s_toyArea2' % massA,
        setParams=params_to_set,
        rMin=0,rMax=5,verbosity=0,
        extra='-t 1 --toysFile=%s' % toy_file_path.split('/')[-1]
    )
    # Plot!
    twoD.StdPlots('mA_%s_toyArea2' % massA, ledger=subset)

if __name__ == '__main__':
    # Provided for convenience is this function which will package
    # the current CMSSW and store it on the user's EOS (assumes FNAL).
    # Only needs to be run once unless you fundamentally change your working environment.
    # make_env_tarball()

    # All functions can in principle be run with 'SR' (signal region)
    # or 'CR' (control region).  Higgs to aa analysis currently has
    # no CRs, but we may in the future. - AWB 2024.05.21
    if len(sys.argv) > 1:
        print("First argument:", sys.argv[1])  # First passed argument
    else:
        if UseMCToy:
            print("toy ?")
            exit()
    toys = int(sys.argv[1])

    test_make('SR')         ## Generate histograms Generic2D objects, including transfer functions
    test_fit('SR')          ## Perform fits to data with models
    #test_plot('SR')         ## Plot data vs. prediction, pre-fit and post-fit
    test_limit('SR')        ## Compute expected asymptotic limits
    #test_GoF('SR')          ## Perform goodness-of-fit (GoF) test with toys
    # midMA = MASSESA[math.floor(len(MASSESA) / 2)]
    # test_SigInj('SR', midMA)       ## Presumably performs some signal injection test (?)
    # test_Impacts('SR', midMA)      ## Test impact of systematic uncertainties (?)
    # # test_generate_for_SR()  ## Absolutely no idea (???)
    # ## If using condor, run after condor jobs finish
    #test_GoF_plot('SR')     ## Plot results of GoF tests
    # test_SigInj_plot('SR', midMA)  ## Plot results of signal injection tests
