import uproot

import numpy as np
import pandas as pd

from config import *


def build_dataframe(tree):

	dataframe = pd.DataFrame({"mJJ":			pd.Series(np.array(tree["mJJ"].array())),
							  "deltaYJJ":		pd.Series(np.array(tree["deltaYJJ"].array())),
							  "metPt":			pd.Series(np.array(tree["metPt"].array())),
							  "ptBalance":		pd.Series(np.array(tree["ptBalance"].array())),
							  "subleadJetEta":	pd.Series(np.array(tree["subleadJetEta"].array())),
							  "leadJetPt":		pd.Series(np.array(tree["leadJetPt"].array())),
							  "photonEta":		pd.Series(np.array(tree["photonEta"].array())),
							  "ptBalanceRed":	pd.Series(np.array(tree["ptBalanceRed"].array())),
							  "nJets":			pd.Series(np.array(tree["nJets"].array())),
							  "sinDeltaPhiJJOver2": pd.Series(np.array(tree["sinDeltaPhiJJOver2"].array())),
							  "deltaYJPh":		pd.Series(np.array(tree["deltaYJPh"].array())),
							  "phCentrality":	pd.Series(np.array(tree["phCentrality"].array())),
							  "weightModified":	pd.Series(np.array(tree["weightModified"].array())),
							  "nLeptons":		pd.Series(np.array(tree["nLeptons"].array())),
							 })

	return dataframe


def selection(dataframe):
	dataframe = dataframe[dataframe["nJets"] > 1]
	dataframe = dataframe[dataframe["nLeptons"] == 0]

	return dataframe


def extract():
	SFile = uproot.open("source/"+SFILENAME)
	STree = SFile[TREENAME]
	SDataframe = build_dataframe(STree)

	BDataframe = pd.DataFrame(columns=["mJJ", "deltaYJJ", "metPt", "ptBalance", "subleadJetEta",
									   "leadJetPt", "photonEta", "ptBalanceRed", "nJets",
									   "sinDeltaPhiJJOver2", "deltaYJPh", "phCentrality", 
									   "weightModified", "nLeptons"])
	for filename in BFILENAMES:
		BFile = uproot.open("source/"+filename)
		BTree = BFile[TREENAME]
		BDataframe = BDataframe.append(build_dataframe(BTree), ignore_index=True)

	SDataframe = selection(SDataframe)
	BDataframe = selection(BDataframe)

	return SDataframe, BDataframe

a, b = extract()

print(a)