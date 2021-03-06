import uproot
import ROOT as root
import itertools

import atlasplots as aplt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config import *
from array import array
from matplotlib.ticker import MultipleLocator
from tools import extract


def assemble_DF(tree):
	frame = 	pd.DataFrame({"mJJ":			pd.Series(tree["mJJ"].array()),
							  "deltaYJJ":		pd.Series(tree["deltaYJJ"].array()),
							  "phCentrality":	pd.Series(tree["phCentrality"].array()),
							  "ptBalance":		pd.Series(tree["ptBalance"].array()),
							  "nJets":			pd.Series(tree["nJets"].array()),
							  "nLeptons":		pd.Series(tree["nLeptons"].array()),
							  "weightModified":	pd.Series(tree["weightModified"].array()),})

	return frame


def readfile():
	signal_file = uproot.open(SIGNALPROCFNM)
	bg_file = uproot.open(BGPROCFNM)

	raw_signal_data = assemble_DF(signal_file[TREENM])
	raw_bg_data = assemble_DF(bg_file[TREENM])

	signal_data = raw_signal_data[raw_signal_data["nLeptons"] == N_LEP]
	signal_data = raw_signal_data[raw_signal_data["nJets"] > 1]

	bg_data = raw_bg_data[raw_bg_data["nLeptons"] == N_LEP]
	bg_data = raw_bg_data[raw_bg_data["nJets"] > 1]

	return signal_data, bg_data


def main(var, dataset):
	data = iterational_filter(var, dataset)
	
	xPlot= data[0]
	yPlot, SRatioPlot, BRatioPlot = data[1]

	maximum = 0
	ind = 0
	for i, item in enumerate(yPlot):
		if item > maximum:
			maximum = item
			ind = i

	threshold = xPlot[ind]
	print("{}\tthreshold: {}".format(var, threshold))
	print("\t\tsignificance: {}".format(maximum))


	S = sum(dataset[0]["weightModified"])
	B = sum(dataset[1]["weightModified"])
	info = (threshold, maximum, S, B)

	if GRAPHING:
		plot_significance((xPlot, yPlot), var, info)
		plot_efficiency((xPlot, (SRatioPlot, BRatioPlot)), var)

	sgn_subset, bg_subset = dataset
	if STG[var]["sign"] == "+":
		dataset = (sgn_subset[sgn_subset[var] > threshold], bg_subset[bg_subset[var] > threshold])
	else:
		dataset = (sgn_subset[sgn_subset[var] < threshold], bg_subset[bg_subset[var] < threshold])

	return dataset


def iterational_filter(var, dataset):
	xPlot, yPlot, SRatioPlot, BRatioPlot = [], [], [], []
	sign_subset, bg_subset = dataset

	minimum = max((min(bg_subset[var]), min(sign_subset[var])))
	maximum = min((max(bg_subset[var]), max(sign_subset[var])))

	initS = sum(sign_subset["weightModified"])
	initB = sum(bg_subset["weightModified"])

	if var == "ptBalance":
		min_ = 0.05
	maximum = STG[var]["max"]

	cursor = minimum
	while cursor < maximum:
		signal = get_response(var, cursor, sign_subset)
		background = get_response(var, cursor, bg_subset)

		S = sum(signal["weightModified"])
		B = sum(background["weightModified"])
		if B+S < 0:
			print("WARNING!, negative B+S={}, event dropped".format(B+S))
			continue

		SRatioPlot.append(S/initS)
		BRatioPlot.append(B/initB)

		xPlot.append(cursor)
		yPlot.append(S/(S+B)**0.5)

		cursor += STG[var]["step"]

	return xPlot, (yPlot, SRatioPlot, BRatioPlot)

def plot_efficiency(plot_set, var):
	aplt.set_atlas_style()

	xPlot, yPlotSgn, yPlotBg = array("d"), array("d"), array("d")

	temp = plot_set[0]
	if var == "mJJ":
		temp = [x/1000 for x in plot_set[0]]

	for x, ySgn, yBg in zip(temp, plot_set[1][0], plot_set[1][1]):
		xPlot.append(x)
		yPlotSgn.append(ySgn)
		yPlotBg.append(yBg)

	NDots = len(xPlot)

	fig, ax = aplt.subplots(1, 1, name="fig2", figsize=(800, 400))

	curve1 = root.TGraph(NDots, xPlot, yPlotSgn)	
	curve1.SetLineColor(4)
	curve1.SetLineWidth(2)
	curve1.GetXaxis().SetTitle(TITLES[var])
	curve1.GetYaxis().SetTitle('Efficiency')
	curve1.SetTitle("")
	curve1.SetMarkerSize(0)
	
	curve2 = root.TGraph(NDots, xPlot, yPlotBg)
	curve2.SetLineColor(2)
	curve2.SetLineWidth(2)
	curve2.GetXaxis().SetTitle(TITLES[var])
	curve2.GetYaxis().SetTitle('Efficiency')
	curve2.SetTitle("")
	curve2.SetMarkerSize(0)


	if var == "phCentrality":
		curve1.GetXaxis().SetRangeUser(0, 1)
		curve2.GetXaxis().SetRangeUser(0, 1)
	if var == "mJJ":
		curve1.GetXaxis().SetRangeUser(0, 2)
		curve2.GetXaxis().SetRangeUser(0, 2)
	if var == "ptBalance":
		curve1.GetXaxis().SetRangeUser(0, 0.125)
		curve2.GetXaxis().SetRangeUser(0, 0.125)
	if var == "deltaYJJ":
		curve1.GetXaxis().SetRangeUser(0, 4)
		curve2.GetXaxis().SetRangeUser(0, 4)

	ax.plot(curve2)
	ax.plot(curve1, "SAME")



	legend=root.TLegend(0.73, 0.6, 0.9, 0.66)
	legend.AddEntry(curve1,"Signal", "L")
	legend.AddEntry(curve2,"Background", "L")
	legend.SetTextSize(27)

	legend.Draw()


	# canvas.Print("eff_{}.png".format(var))
	input()


def get_response(var, threshold, dataset):
	sign = STG[var]["sign"]

	if sign == "+":
		passed = dataset[dataset[var] > threshold]
	elif sign == "-":
		passed = dataset[dataset[var] < threshold]
	else:
		raise Exception("Inappropriate sign provided")

	return passed


def plot_significance(plot_set, var, metadata):
	aplt.set_atlas_style()

	temp = plot_set[0]
	if var == "mJJ":
		temp = [x/1000 for x in plot_set[0]]

	xPlot, yPlot = array("d"), array("d")
	for x, y in zip(temp, plot_set[1]):
		xPlot.append(x)
		yPlot.append(y)

	NDots = len(xPlot)

	curve = root.TGraph(NDots, xPlot, yPlot)
	curve.SetLineColor(2)
	curve.SetLineWidth(2)
	curve.SetMarkerColor(2)
	curve.SetMarkerSize(0)
	curve.GetXaxis().SetTitle(TITLES[var])
	curve.GetYaxis().SetTitle('Significance')
	curve.GetYaxis().SetRangeUser(*YLIMS[var])
	if var == "phCentrality":
		curve.GetXaxis().SetRangeUser(0, 1)
	if var == "mJJ":
		curve.GetXaxis().SetRangeUser(0, 2)
	if var == "ptBalance":
		curve.GetXaxis().SetRangeUser(0, 0.125)
	if var == "deltaYJJ":
		curve.GetXaxis().SetRangeUser(0, 4)
	# curve.GetYaxis().SetLabelSize(24)
	# curve.GetXaxis().SetLabelSize(24)
	# curve.GetYaxis().SetTickSize(0.1)



	threshold = str(round(metadata[0], 3))
	peak = str(round(metadata[1], 3))
	S = str(round(metadata[2]))
	B = str(round(metadata[3]))

	fig, ax = aplt.subplots(1, 1, name="fig2", figsize=(800, 600))

	ax.plot(curve)

	# ax.set_xlim(YLIMS[var])
	# ax.add_margins(top=0.16)


	ax.set_xlabel("Cut value applied on BDTgrad output")
	ax.set_ylabel("Significance")

	# aplt.atlas_label(text="Internal", loc="upper left")
	ax.text(0.19, 0.92, "#sqrt{s} = 13 TeV, 139 fb^{-1}", size=27, align=13)
	ax.text(0.195, 0.865, "Z_{#gamma} inc. region", size=27, align=13)

	text1 = "For {} signal and {} background".format(S, B)
	text2 = "events the maximum {} is".format("S/#sqrt{S+B}")
	text3 = "{} when cutting at {}".format(peak, threshold)

	offset = 0
	if var in ("phCentrality", "mJJ"):
		offset = 0.35

	ax.text(0.2 + offset, 0.3, text1, size=20, align=13)
	ax.text(0.2 + offset, 0.27, text2, size=20, align=13)
	ax.text(0.2 + offset, 0.22, text3, size=20, align=13)

	if var == "mJJ":
		line = root.TLine(round(metadata[0]/1000, 3), 0, round(metadata[0]/1000, 3), 4)
	else:
		line = root.TLine(round(metadata[0], 3), 0, round(metadata[0], 3), 4)
	line.SetLineStyle(10)
	line.SetLineColor(6)
	ax.plot(line)

	# legend = root.TLegend(0.65, 0.8, 0.95, 0.92)
	legend = root.TLegend(0.7, 0.83, 1.0, 0.95)

	legend.SetFillColorAlpha(0, 0)
	legend.AddEntry(line, "Cut value", "L")
	legend.SetTextSize(27)
	legend.Draw()
	# print(dir(legend))


	fig.canvas.SetGrid()
	# fig.savefig("{}.pdf".format(var))
	# input()




def error(signal_events, bg_events):
	S = np.sum(signal_events)
	B = np.sum(bg_events)

	SErr = np.sum(signal_events**2)**0.5
	BErr = np.sum(bg_events**2)**0.5

	SPart = (S + B)**(-0.5) - 0.5*S*((S + B)**(-1.5))
	BPart = -0.5*S*((S + B)**(-1.5))

	return ((SPart*SErr)**2 + (BPart*BErr)**2)**0.5


def error_ROC(signal_events, bg_events):
	S = np.sum(signal_events)
	B = np.sum(bg_events)

	SErr = np.sum(signal_events**2)**0.5
	BErr = np.sum(bg_events**2)**0.5

	SPart = B/((S + B)**2)
	BPart = S/((S + B)**2)

	return ((SPart*SErr)**2 + (BPart*BErr)**2)**0.5


if __name__ == "__main__":
	print("-"*50)
	counter = 0
	variables = ["phCentrality", "mJJ", "ptBalance", "deltaYJJ"]

	if COMBINATIONS == "ALL":
		for item in list(itertools.permutations(variables)):

			counter += 1
			print("Set: {}".format(counter))
			newset = extract()

			for var in item:
				newset = main(var, newset)

			signal_events = np.array(newset[0]["weightModified"])
			bg_events = np.array(newset[1]["weightModified"])

			print(error(signal_events, bg_events))
			print("-"*50)

	else:
		newset = extract()

		for var in variables:
			newset = main(var, newset)

		signal_events = np.array(newset[0]["weightModified"])
		bg_events = np.array(newset[1]["weightModified"])


		sign_subset, bg_subset = extract()

		initS = sum(sign_subset["weightModified"])
		initB = sum(bg_subset["weightModified"])

		initSErr = sum(sign_subset["weightModified"]**2)**0.5
		initBErr = sum(bg_subset["weightModified"]**2)**0.5
		SErr = sum(signal_events**2)**0.5
		BErr = sum(bg_events**2)**0.5
		S = sum(signal_events)
		B = sum(bg_events)

		SigEffErr = ((SErr/initS)**2 + (S*initSErr/(initS)**2)**2)**0.5
		BgRejErr = ((BErr/initB)**2 + (B*initBErr/(initB)**2)**2)**0.5

		print("SigEff: ", sum(signal_events)/initS, " +- ", SigEffErr)
		print("BgRej: ", 1 - sum(bg_events)/initB, " +- ", BgRejErr)

		print(error(signal_events, bg_events))
		print("-"*50)





