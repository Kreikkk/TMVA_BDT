import uproot

import numpy as np
import pandas as pd
import ROOT as root

from array import array

from config import *
from tools import extract, error
from hists import setup_layout


def build_reader():
	reader = root.TMVA.Reader("reader")

	var_mJJ 				= array('f',[0])
	var_deltaYJJ 			= array('f',[0])
	var_metPt 				= array('f',[0])
	var_ptBalance 			= array('f',[0])
	var_subleadJetEta 		= array('f',[0])
	var_leadJetPt 			= array('f',[0])
	var_photonEta 			= array('f',[0])
	var_ptBalanceRed 		= array('f',[0])
	var_nJets 				= array('f',[0])
	var_sinDeltaPhiJJOver2 	= array('f',[0])
	var_deltaYJPh 			= array('f',[0])

	reader.AddVariable("mJJ",				var_mJJ)
	reader.AddVariable("deltaYJJ",			var_deltaYJJ)
	reader.AddVariable("metPt",				var_metPt)
	reader.AddVariable("ptBalance",			var_ptBalance)
	reader.AddVariable("subleadJetEta",		var_subleadJetEta)
	reader.AddVariable("leadJetPt",			var_leadJetPt)
	reader.AddVariable("photonEta",			var_photonEta)
	reader.AddVariable("ptBalanceRed",		var_ptBalanceRed)
	reader.AddVariable("nJets",				var_nJets)
	reader.AddVariable("sinDeltaPhiJJOver2",var_sinDeltaPhiJJOver2)
	reader.AddVariable("deltaYJPh",			var_deltaYJPh)

	reader.BookMVA(METHODNAME, WEIGHTSPATH)

	SDataframe, BDataframe = extract()
	SDataframe["BDToutput"] = 0.0
	BDataframe["BDToutput"] = 0.0

	output = []
	for i, row in SDataframe.iterrows():
		var_mJJ[0]					= row["mJJ"]
		var_deltaYJJ[0]				= row["deltaYJJ"]
		var_metPt[0]				= row["metPt"]
		var_ptBalance[0]			= row["ptBalance"]
		var_subleadJetEta[0]		= row["subleadJetEta"]
		var_leadJetPt[0]			= row["leadJetPt"]
		var_photonEta[0]			= row["photonEta"]
		var_ptBalanceRed[0]			= row["ptBalanceRed"]
		var_nJets[0]				= row["nJets"]
		var_sinDeltaPhiJJOver2[0]	= row["sinDeltaPhiJJOver2"]
		var_deltaYJPh[0]			= row["deltaYJPh"]

		output.append(reader.EvaluateMVA("BDTgrad"))
	SDataframe["BDToutput"] = output

	output = []
	for i, row in BDataframe.iterrows():
		var_mJJ[0]					= row["mJJ"]
		var_deltaYJJ[0]				= row["deltaYJJ"]
		var_metPt[0]				= row["metPt"]
		var_ptBalance[0]			= row["ptBalance"]
		var_subleadJetEta[0]		= row["subleadJetEta"]
		var_leadJetPt[0]			= row["leadJetPt"]
		var_photonEta[0]			= row["photonEta"]
		var_ptBalanceRed[0]			= row["ptBalanceRed"]
		var_nJets[0]				= row["nJets"]
		var_sinDeltaPhiJJOver2[0]	= row["sinDeltaPhiJJOver2"]
		var_deltaYJPh[0]			= row["deltaYJPh"]

		output.append(reader.EvaluateMVA("BDTgrad"))
	BDataframe["BDToutput"] = output


	# import matplotlib.pyplot as plt

	# fig, ax = plt.subplots()
	# ax.hist(SDataframe["BDToutput"], weights=SDataframe["weightModified"], bins=50, color="blue", alpha=0.5, label="signal")
	# ax.hist(BDataframe["BDToutput"], weights=BDataframe["weightModified"], bins=50, color="red", alpha=0.5, label="background")
	# ax.legend()
	# ax.set_xlabel("BDToutput")
	# ax.set_ylabel("N of events")
	# plt.show()

	canvas = root.TCanvas("canvas", "CANVAS", 800, 600)
	SHist = root.TH1F("", "", 50, -1, 1)
	BHist = root.TH1F("", "", 50, -1, 1)

	canvas.SetTicks(1, 1)
	
	BHist.SetStats(False)
	SHist.SetStats(False)
	BHist.SetLineWidth(2)	
	BHist.SetLineColor(2)
	BHist.SetFillColor(2)
	BHist.SetFillStyle(3004)

	BHist.GetXaxis().CenterTitle()
	BHist.GetYaxis().SetTitle("Fraction of events")
	BHist.GetYaxis().CenterTitle()
	BHist.GetXaxis().SetTitleOffset(1.2)
	BHist.SetMinimum(0)

	SHist.SetLineWidth(2)
	SHist.SetLineColor(4)
	SHist.SetFillColorAlpha(4, 0.2)

	SHist.GetXaxis().CenterTitle()
	SHist.GetXaxis().SetTitle("BDTgrad output")
	SHist.GetYaxis().SetTitle("Fraction of events")
	SHist.GetYaxis().CenterTitle()
	SHist.GetXaxis().SetTitleOffset(1.2)
	SHist.SetMinimum(0)	

	legend=root.TLegend(0.67, 0.77, 0.87, 0.9)
	legend.AddEntry(SHist,"Signal","f")
	legend.AddEntry(BHist,"Background","f")
	for out, weight in zip(SDataframe["BDToutput"], SDataframe["weightModified"]):
		SHist.Fill(out, weight)
	for out, weight in zip(BDataframe["BDToutput"], BDataframe["weightModified"]):
		BHist.Fill(out, weight)

	SHist.DrawNormalized("HIST E1")
	BHist.DrawNormalized("same HIST E1")

	legend.Draw()
	canvas.Update()
	input()

	return make_selections(SDataframe, BDataframe)


def make_selections(SDataframe, BDataframe):
	Min = max(min(SDataframe["BDToutput"]), min(BDataframe["BDToutput"]))
	Max = min(max(SDataframe["BDToutput"]), max(BDataframe["BDToutput"]))

	cursor = Min
	plot_data = [[],[]]
	while cursor <= Max:
		S = sum(SDataframe[SDataframe["BDToutput"] > cursor]["weightModified"])
		B = sum(BDataframe[BDataframe["BDToutput"] > cursor]["weightModified"])

		plot_data[0].append(cursor)
		plot_data[1].append(S/(S+B)**0.5)
		cursor += BDTSTEP

	peak = max(enumerate(plot_data[1]), key=lambda x: x[1])
	meta = {"initS": round(sum(SDataframe["weightModified"])),
			"initB": round(sum(BDataframe["weightModified"])),
			"peak": (peak[1], plot_data[0][peak[0]])}
	plot_data.append(meta)
	
	a = SDataframe[SDataframe["BDToutput"] > plot_data[0][peak[0]]]
	b = BDataframe[BDataframe["BDToutput"] > plot_data[0][peak[0]]]
	print(error(np.array(a["weightModified"]), np.array(b["weightModified"])))

	return plot_data


def plot(plot_data):
	canvas = root.TCanvas("canvas", "CANVAS", 800, 800)

	xPlot, yPlot = array("d"), array("d")
	for x, y in zip(plot_data[0], plot_data[1]):
		xPlot.append(x)
		yPlot.append(y)

	curve = root.TGraph(len(xPlot), xPlot, yPlot)
	curve.SetLineColor(1)
	curve.SetLineWidth(4)
	curve.SetMarkerColor(1)
	curve.SetMarkerStyle(3)
	curve.SetMarkerSize(0)
	curve.SetTitle("")
	curve.GetXaxis().SetTitle("Cut value applied on BDTgrad output")
	curve.GetYaxis().SetTitle('Significance')
	curve.GetXaxis().SetRangeUser(-1, 1)
	curve.Draw()

	text1 = "For {} signal and {} background".format(round(plot_data[2]["initS"]),
													 round(plot_data[2]["initB"]))
	text2 = "events the maximum {} is".format("#frac{S}{#sqrt{S+B}}")
	text3 = "{} when cutting at {}".format(round(plot_data[2]["peak"][0], 3),
										   round(plot_data[2]["peak"][1], 3))
	latex = root.TLatex()
	latex.SetNDC()
	latex.SetTextSize(0.02)
	offset = -0.01
	latex.DrawLatex(0.13, 0.22+offset, text1)
	latex.DrawLatex(0.13, 0.19+offset, text2)
	latex.DrawLatex(0.13, 0.15+offset, text3)

	canvas.SetGrid()
	canvas.Update()
	input()


if __name__ == "__main__":
	root.TMVA.Tools.Instance()

	plot_data = build_reader()
	plot(plot_data)
