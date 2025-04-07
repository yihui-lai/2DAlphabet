import ROOT
import os
import numpy as np

ROOT.gROOT.SetBatch(True)
import glob
ROOT.gStyle.SetOptStat(0)  ## Don't display stat boxes

data_expected_list={
    'leptonic_30':0.0337, 'vbf_30':0.0503, 'ggh_30':0.0327, 'all_30':0.0171
}

for channel in ['leptonic', 'vbf', 'ggh', 'all']:
    for mass in ['30']:
        # Input files
        file_pattern = f"higgsCombine.testAsymptoticLimits.ma_{mass}.{channel}.toy*.AsymptoticLimits.mH120.root"
        data_file = "data.root"
        # Get list of toy files
        files = glob.glob(file_pattern)
        # Create histograms
        h_exp = ROOT.TH1F("h_exp", "Expected and Observed Limits;Limit;Events", 20, 0, 0.1)
        h_obs = ROOT.TH1F("h_obs", "Expected and Observed Limits;Limit;Events", 20, 0, 0.1)
        for f in files:
            if not os.path.isfile(f):
                continue
            root_file = ROOT.TFile.Open(f)
            if not root_file or root_file.IsZombie():
                continue
            tree = root_file.Get("limit")
            if not tree:
                root_file.Close()
                continue
            for entry in tree:
                if abs(entry.quantileExpected - 0.5) < 1e-4:
                    h_exp.Fill(entry.limit)
                elif entry.quantileExpected == -1:
                    h_obs.Fill(entry.limit)
            root_file.Close()
        
        # Get expected limit from data.root
        #data_expected = None
        #if os.path.isfile(data_file):
        #    f_data = ROOT.TFile.Open(data_file)
        #    if f_data and not f_data.IsZombie():
        #        t_data = f_data.Get("limit")
        #        if t_data:
        #            for entry in t_data:
        #                if abs(entry.quantileExpected - 0.5) < 1e-4:
        #                    data_expected = entry.limit
        #                    break
        #        f_data.Close()
        data_expected = data_expected_list[f"{channel}_{mass}"]
        
        # Styling
        h_exp.SetLineColor(ROOT.kBlue + 1)
        h_exp.SetLineWidth(2)
        h_obs.SetLineColor(ROOT.kRed + 1)
        h_obs.SetLineWidth(2)
        
        # Draw
        c = ROOT.TCanvas("c", "", 800, 600)
        h_exp.Draw("hist")
        h_obs.Draw("hist same")
        
        # Add arrow for expected data
        if data_expected is not None:
            arrow = ROOT.TArrow(data_expected, 0, data_expected, h_exp.GetMaximum() * 0.5, 0.02, "|>")
            arrow.SetLineColor(ROOT.kOrange)
            arrow.SetFillColor(ROOT.kOrange)
            arrow.SetLineWidth(2)
            arrow.Draw()
        else:
            print("Could not extract expected value from data.root")
        
        # Add legend
        legend = ROOT.TLegend(0.55, 0.7, 0.88, 0.85)
        legend.AddEntry(h_exp, "Expected (median, toys)", "l")
        legend.AddEntry(h_obs, "Observed (toys)", "l")
        if data_expected is not None:
            legend.AddEntry(arrow, "Expected (median, data)", "l")
        legend.Draw()
        
        c.SaveAs(f"limit_distribution_with_data_arrow_{channel}_{mass}.png")


