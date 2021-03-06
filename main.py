import uproot
import ROOT as root
import itertools

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
	xPlot, yPlotSgn, yPlotBg = array("d"), array("d"), array("d")

	for x, ySgn, yBg in zip(plot_set[0], plot_set[1][0], plot_set[1][1]):
		xPlot.append(x)
		yPlotSgn.append(ySgn)
		yPlotBg.append(yBg)

	NDots = len(xPlot)

	canvas = root.TCanvas("canvas", "CANVAS", 800, 800)

	curve1 = root.TGraph(NDots, xPlot, yPlotSgn)	
	curve1.SetLineColor(4)
	curve1.SetLineWidth(3)
	curve1.GetXaxis().SetTitle(var)
	curve1.GetYaxis().SetTitle('Efficiency')
	curve1.SetTitle("")

	curve2 = root.TGraph(NDots, xPlot, yPlotBg)
	curve2.SetLineColor(2)
	curve2.SetLineWidth(3)
	curve2.GetXaxis().SetTitle(var)
	curve2.GetYaxis().SetTitle('Efficiency')
	curve2.SetTitle("")

	ymax = round(max(max(yPlotSgn), max(yPlotBg)) + 0.1, 1)
	ymin = round(min(min(yPlotSgn), min(yPlotBg)) - 0.1, 1)
	if ymin < 0:
		ymin = 0.

	curve1.GetYaxis().SetRangeUser(ymin, ymax)
	curve2.GetYaxis().SetRangeUser(ymin, ymax)

	curve1.Draw()
	curve2.Draw("SAME")


	legend=root.TLegend(0.73, 0.84, 0.9, 0.9)
	legend.AddEntry(curve1,"Signal")
	legend.AddEntry(curve2,"Background")
	legend.Draw()

	canvas.SetGrid()
	canvas.Update()

	canvas.Print("eff_{}.png".format(var))

	if not IGNORE_GRAPH_SHOW:
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
	xPlot, yPlot = array("d"), array("d")
	for x, y in zip(plot_set[0], plot_set[1]):
		xPlot.append(x)
		yPlot.append(y)

	NDots = len(xPlot)

	canvas = root.TCanvas("canvas", "CANVAS", 800, 800)

	curve = root.TGraph(NDots, xPlot, yPlot)
	curve.SetLineColor(1)
	curve.SetLineWidth(4)
	curve.SetMarkerColor(1)
	curve.SetMarkerStyle(3)
	curve.SetMarkerSize(0)
	curve.SetTitle("")
	curve.GetXaxis().SetTitle(var)
	curve.GetYaxis().SetTitle('Significance')
	curve.Draw()

	threshold = str(round(metadata[0], 3))
	peak = str(round(metadata[1], 3))
	S = str(round(metadata[2]))
	B = str(round(metadata[3]))

	text1 = "For {} signal and {} background".format(S, B)
	text2 = "events the maximum {} is".format("#frac{S}{#sqrt{S+B}}")
	text3 = "{} when cutting at {}".format(peak, threshold)
	latex = root.TLatex()
	latex.SetNDC()
	latex.SetTextSize(0.02)
	offset = 0
	latex.DrawLatex(0.61, 0.22+offset, text1)
	latex.DrawLatex(0.61, 0.19+offset, text2)
	latex.DrawLatex(0.61, 0.15+offset, text3)

	canvas.SetGrid()
	canvas.Update()

	canvas.Print("./sign_{}.png".format(var))

	if not IGNORE_GRAPH_SHOW:
		input()


def error(signal_events, bg_events):
	S = np.sum(signal_events)
	B = np.sum(bg_events)

	SErr = np.sum(signal_events**2)**0.5
	BErr = np.sum(bg_events**2)**0.5

	SPart = (S + B)**(-0.5) - 0.5*S*((S + B)**(-1.5))
	BPart = -0.5*S*((S + B)**(-1.5))

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

		print(error(signal_events, bg_events))
		print("-"*50)





