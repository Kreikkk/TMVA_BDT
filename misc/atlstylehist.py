import os
import sys
import time
import uproot

import atlasplots as aplt
import ROOT as root
import numpy as np
import pandas as pd

from config import *
from tools import extract



def setup_layout(bg_hist, signal_hist):
	
	bg_hist.SetStats(False)
	signal_hist.SetStats(False)
	bg_hist.SetLineWidth(2)	
	bg_hist.SetLineColor(2)
	bg_hist.SetFillColor(2)
	bg_hist.SetFillStyle(3004)

	bg_hist.GetXaxis().CenterTitle()
	bg_hist.GetYaxis().SetTitle("Fraction of events")
	bg_hist.GetYaxis().CenterTitle()
	bg_hist.GetXaxis().SetTitleOffset(1.2)
	bg_hist.SetMinimum(0)

	signal_hist.SetLineWidth(2)
	signal_hist.SetLineColor(4)
	signal_hist.SetFillColorAlpha(4, 0.2)

	signal_hist.GetXaxis().CenterTitle()
	signal_hist.GetYaxis().SetTitle("Fraction of events")
	signal_hist.GetYaxis().CenterTitle()
	signal_hist.GetXaxis().SetTitleOffset(1.2)
	signal_hist.SetMinimum(0)

	# legend=root.TLegend(0.70, 0.77, 0.9, 0.9)
	legend=root.TLegend(0.67, 0.77, 0.87, 0.9)
	legend.AddEntry(signal_hist,"Signal","f")
	legend.AddEntry(bg_hist,"Background","f")

	latex = root.TLatex()
	latex.SetNDC()
	latex.SetTextSize(0.035)

	return bg_hist, signal_hist, legend, latex


def plot(filtered_signal_data, filtered_bg_data):
	print("Вхождения(фон):", len(filtered_bg_data["mJJ"]))
	print("Вхождения(сигнал):", len(filtered_signal_data["mJJ"]))
	print("Веса(фон):", np.sum(filtered_bg_data["weightModified"]))
	print("Веса(сигнал):", np.sum(filtered_signal_data["weightModified"]))

	
	filename_counter = 0
	for key in filtered_signal_data.keys()[:-2]:
		bg_column = filtered_bg_data[key]
		signal_column = filtered_signal_data[key]
		xmax = np.max([np.max(bg_column), np.max(signal_column)])
		xmin = np.min([np.min(bg_column), np.min(signal_column)])

		if xmin > 0:
			xmin = 0

		bins1, bins2 = DEF_BINS, DEF_BINS

		if key == "nJets":
			bins1, bins2 = 9, 9
		elif key == "metPt":
			bins1, bins2 = 75, 75
		elif key == "leadJetPt":
			bins1, bins2 = 60, 60
			

		bg_hist = root.TH1F("", "", bins1, xmin, xmax)
		bg_hist.GetXaxis().SetTitle(TITLES[key])

		signal_hist = root.TH1F("", "", bins2, xmin, xmax)
		signal_hist.GetXaxis().SetTitle(TITLES[key])

		bg_hist, signal_hist, legend, latex = setup_layout(bg_hist, signal_hist)


		for bg_value, weight in zip(bg_column, filtered_bg_data["weightModified"]):
			bg_hist.Fill(bg_value, weight)
		for signl_value, weight in zip(signal_column, filtered_signal_data["weightModified"]):
			signal_hist.Fill(signl_value, weight)

		aplt.set_atlas_style()
		fig, ax = aplt.subplots(1, 1, name="fig1", figsize=(800, 600))
		######################################
		ax.plot(signal_hist, MARGINS[key])
		ax.plot(bg_hist, MARGINS[key])
		######################################
		ax.add_margins(top=0.16)
		ax.set_xlabel(TITLES[key])
		ax.set_ylabel("Fraction of events")

		# aplt.atlas_label(text="Internal", loc="upper left")
		ax.text(0.2, 0.92, "#sqrt{s} = 13 TeV, 139 fb^{-1}", size=27, align=13)
		ax.text(0.205, 0.865, "Z_{#gamma} inc. region", size=27, align=13)

		legend = root.TLegend(0.65, 0.8, 0.95, 0.92)
		legend.SetFillColorAlpha(0, 0)
		legend.AddEntry(signal_hist, "Signal", "F")
		legend.AddEntry(bg_hist, "Background", "F")
		legend.Draw()

		# time.sleep(0.5)
		# fig.savefig("histogramms/{}.pdf".format(key))
		# time.sleep(0.5)
		input()


if __name__ == "__main__":
	plot(*extract())
