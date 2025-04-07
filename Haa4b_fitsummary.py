import ROOT
import os
import numpy as np

ROOT.gROOT.SetBatch(True)
import glob
ROOT.gStyle.SetOptStat(0)  ## Don't display stat boxes

# File pattern for toy fit diagnostics
for channel in ['leptonic', 'vbf', 'ggh', 'all']:
    for mass in ['30']:
        file_pattern = f"fitDiagnostics.testFitDiagnostics.ma_{mass}.{channel}.toy*.root"
        files = glob.glob(file_pattern)
        hist = ROOT.TH1F("h_rOverErr", "Bias in r (r / rErr);r / rErr;Fits", 20, -5, 5)
        for f in files:
            if not os.path.isfile(f):
                continue
            f_root = ROOT.TFile.Open(f)
            if not f_root or f_root.IsZombie():
                print(f"Skipping unreadable file: {f}")
                continue
        
            tree = f_root.Get("tree_fit_sb")
            if not tree:
                print(f"No tree_fit_sb in file: {f}")
                f_root.Close()
                continue
        
            for entry in tree:
                if entry.fit_status != 0:
                    continue  # skip failed fits
                if entry.rErr != 0:
                    hist.Fill(entry.r / entry.rErr)
        
            f_root.Close()
        
        # Styling and draw
        hist.SetLineColor(ROOT.kBlue + 1)
        hist.SetLineWidth(2)
        # Fit with Gaussian
        fit_result = hist.Fit("gaus", "S")  # "S" to get the fit result object
        fit_func = hist.GetFunction("gaus")
        fit_func.SetLineColor(ROOT.kRed + 1)
        fit_func.SetLineWidth(2)
        fit_func.SetLineStyle(1)
        # Get fit parameters
        fit_mean = fit_result.Parameter(1)
        fit_mean_err = fit_result.Parameter(2)
        print(f"Fitted bias (mean of r/rErr): {fit_mean:.4f} ± {fit_mean_err:.4f}")
        c = ROOT.TCanvas("c", "", 800, 600)
        hist.Draw("hist")
        fit_func.Draw("same")
        hist.GetFunction("gaus").SetLineColor(ROOT.kRed + 1)
        hist.GetFunction("gaus").SetLineWidth(2)
        # Annotate with bias value
        latex = ROOT.TLatex()
        latex.SetNDC()
        latex.SetTextSize(0.04)
        latex.DrawLatex(0.15, 0.85, f"#mu = {fit_mean:.3f}")
        latex2 = ROOT.TLatex()
        latex2.SetNDC()
        latex2.SetTextSize(0.04)
        latex2.DrawLatex(0.15, 0.75, f"#sigma = {fit_mean_err:.3f}")
        legend = ROOT.TLegend(0.6, 0.75, 0.88, 0.88)
        legend.AddEntry(hist, "r / rErr", "l")
        legend.AddEntry(fit_func, "Gaussian Fit", "l")
        legend.Draw()
        
        c.SaveAs(f"bias_r_over_rErr_{channel}_{mass}.png")


