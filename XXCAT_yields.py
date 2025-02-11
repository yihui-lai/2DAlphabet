# Script by Hichem Bouchamaoui to print out signal and data yields for merged
# root files (XXHi/XXLo) in a table format for all WP * Pass/Fail * mA

import ROOT
import os
import glob
import sys
from tabulate import tabulate
from collections import defaultdict
import math
import ctypes

# Check if a directory is provided as an argument
if len(sys.argv) < 2:
    print("Usage: python script.py <directory_path>")
    sys.exit(1)

# Get directory from system argument
directory = sys.argv[1]

# Define WPXX and PF categories
wp_list = ["WP40", "WP60", "WP80"]
pf_list = ["Pass", "Fail"]

# Define categories for grouping ROOT files
categories = ["mA_15", "mA_30", "mA_55"]
grouped_results = {cat: {wp: {pf: [0, 0] for pf in pf_list} for wp in wp_list} for cat in categories}

# Get all ROOT files in the directory
root_files = glob.glob(os.path.join(directory, "*.root"))

if not root_files:
    print(f"No ROOT files found in {directory}")
    sys.exit(1)

# Loop over all ROOT files
for root_file in root_files:
    # Identify category based on filename
    category = None
    for cat in categories:
        if cat in root_file:
            category = cat
            break
    if "Data" in root_file:
        category = "Data"

    print(f"\nProcessing file: {root_file}")
    file = ROOT.TFile.Open(root_file, "READ")

    if not file or file.IsZombie():
        print(f"Error opening file: {root_file}")
        continue

    # Initialize results dictionary with WPXX as rows and PF as columns
    results = {wp: {pf: None for pf in pf_list} for wp in wp_list}

    # Loop through all keys in the file
    for key in file.GetListOfKeys():
        obj = key.ReadObj()

        # Check if the object is a 2D histogram (TH2D)
        if isinstance(obj, ROOT.TH2D):
            hist_name = obj.GetName()

            # Exclude histograms containing "pnet" or "msoft"
            if "pnet" in hist_name.lower() or "msoft" in hist_name.lower():
                continue

            # Determine WPXX and PF category
            wp_match = next((wp for wp in wp_list if wp in hist_name), None)
            pf_match = next((pf for pf in pf_list if pf in hist_name), None)

            if wp_match and pf_match:
                error = ctypes.c_double(0)
                #error = float(0.0)  # Use a normal float instead of ROOT.Double
                integral_value = round(obj.IntegralAndError(1, obj.GetNbinsX(), 1,obj.GetNbinsY(), error), 3)
                error = float(error.value)
                integral_error = round(math.sqrt(error), 3)  # Convert to a normal Python float
                #integral_error = math.sqrt(error)  # Convert to a normal Python float

                results[wp_match][pf_match] = f"{integral_value} ± {integral_error}"

                # Sum values into the grouped results (excluding "Data")
                if category and category != "Data":
                    grouped_results[category][wp_match][pf_match][0] += integral_value
                    grouped_results[category][wp_match][pf_match][1] += error  # Sum in quadrature

    # Convert results to table format
    table_data = [[wp] + [results[wp][pf] if results[wp][pf] is not None else "-" for pf in pf_list] for wp in wp_list]

    # Print table
    print(tabulate(table_data, headers=["WPXX"] + pf_list, tablefmt="grid"))

    file.Close()

# Print summary tables for each category (excluding Data)
for category in categories:
    print(f"\nSummed Results for {category}:\n")

    # Compute final errors as sqrt(sum of squares)
    summary_table_data = [
        [wp] + [
            f"{round(grouped_results[category][wp][pf][0], 3)} ± {round(math.sqrt(grouped_results[category][wp][pf][1]), 3)}"
            if grouped_results[category][wp][pf][0] != 0 else "-"
            for pf in pf_list
        ]
        for wp in wp_list
    ]

    print(tabulate(summary_table_data, headers=["WPXX"] + pf_list, tablefmt="grid"))

