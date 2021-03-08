import os
import sys
import uproot

import ROOT as root
import numpy as np
import pandas as pd

from config import *
from tools import extract


def setup_layout(canvas, bg_hist, signal_hist):
	canvas.SetTicks(1, 1)
	
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

	return canvas, bg_hist, signal_hist, legend, latex


def plot(filtered_signal_data, filtered_bg_data):
	print("Вхождения(фон):", len(filtered_bg_data["mJJ"]))
	print("Вхождения(сигнал):", len(filtered_signal_data["mJJ"]))
	print("Веса(фон):", np.sum(filtered_bg_data["weightModified"]))
	print("Веса(сигнал):", np.sum(filtered_signal_data["weightModified"]))

	titles = {"mJJ": "m_{jj}[GeV]", "deltaYJJ": "#DeltaY(j_{1},j_{2})", "metPt": "E^{miss}_{T}[GeV]",
			  "ptBalance": "p_{T}- balance", "subleadJetEta": "#eta(j_{2})", "leadJetPt": "p_{T}(j_{1})[GeV]",
			  "photonEta": "#eta(#gamma)", "ptBalanceRed": "p_{T}- balance(reduced)", "nJets": "N_{jets}",
			  "sinDeltaPhiJJOver2": "sin(|#Delta#varphi(j_{1},j_{2})|)",
			  "deltaYJPh":"#DeltaY(j_{1},#gamma)", "weightModified": "weightModified", "nLeptons": "nLeptons", "phCentrality": "phCentrality"}
	filename_counter = 0
	for key in filtered_signal_data.keys()[:-1]:
		bg_column = filtered_bg_data[key]
		signal_column = filtered_signal_data[key]

		xmax = np.max([np.max(bg_column), np.max(signal_column)])
		xmin = np.min([np.min(bg_column), np.min(signal_column)])

		if xmin > 0:
			xmin = 0

		bins1, bins2 = DEF_BINS, DEF_BINS

		if key == "nJets":
			bins1 = int(np.max(bg_column))
			bins2 = int(np.max(signal_column))

		canvas = root.TCanvas("canvas", "CANVAS", 1920, 1080)


		bg_hist = root.TH1F("", "", bins1, xmin, xmax)
		bg_hist.GetXaxis().SetTitle(titles[key])

		signal_hist = root.TH1F("", "", bins1, xmin, xmax)
		signal_hist.GetXaxis().SetTitle(titles[key])

		
		canvas, bg_hist, signal_hist, legend, latex = setup_layout(canvas, bg_hist, signal_hist)

		if key == "mJJ":
			signal_hist.GetXaxis().SetRangeUser(0, 4000)
			bg_hist.GetXaxis().SetRangeUser(0, 4000)
		elif key == "metPt":
			signal_hist.GetXaxis().SetRangeUser(100, 1000)
			bg_hist.GetXaxis().SetRangeUser(100, 1000)
		elif key == "ptBalance":
			signal_hist.GetXaxis().SetRangeUser(0, 0.2)
			bg_hist.GetXaxis().SetRangeUser(0, 0.2)
		elif key == "leadJetPt":
			signal_hist.GetXaxis().SetRangeUser(0, 800)
			bg_hist.GetXaxis().SetRangeUser(0, 800)

		for bg_value, weight in zip(bg_column, filtered_bg_data["weightModified"]):
			bg_hist.Fill(bg_value, weight)
		for signl_value, weight in zip(signal_column, filtered_signal_data["weightModified"]):
			signal_hist.Fill(signl_value, weight)

		if FILTER == 1:
			text = "Z_{#gamma} region"
			filename = "zgamma"

			if key in ("mJJ", "deltaYJJ", "metPt", "subleadJetEta", "leadJetPt", "deltaYJPh", "ptBalanceRed", "sinDeltaPhiJJOver2"):
				bg_hist.DrawNormalized("HIST")
				signal_hist.DrawNormalized("same HIST")
			else:
				signal_hist.DrawNormalized("HIST")
				bg_hist.DrawNormalized("same HIST")	
		elif FILTER == 2:
			text = "Signal region"
			filename = "signal"

			if key in ("mJJ", "deltaYJJ", "metPt", "photonEta", "sinDeltaPhiJJOver2", "deltaYJPh"):
				bg_hist.DrawNormalized("HIST")
				signal_hist.DrawNormalized("same HIST")
			else:
				signal_hist.DrawNormalized("HIST")
				bg_hist.DrawNormalized("same HIST")
		else:
			text = "total"
			filename = "total"

			signal_hist.DrawNormalized("HIST")
			bg_hist.DrawNormalized("same HIST")

		legend.Draw()
		# latex.DrawLatex(0.7, 0.73, text)
		latex.DrawLatex(0.67, 0.73, text)
		canvas.Update()


		if SAVEPNG:
			try:
				os.mkdir(filename)
			except FileExistsError:
				pass
			canvas.Print("./{}/{}{}.png".format(filename, filename_counter, key))
			filename_counter += 1
		if SHOWHIST:
			t = input()

		del bg_hist
		del signal_hist
		del canvas


if __name__ == "__main__":
	plot(*extract())
