import numpy as np
import ROOT as root

from config import *


def main():
	fout = root.TFile("output.root", "RECREATE")
	factory = root.TMVA.Factory("TMVAClassification", fout,
                            ":".join([    "!V",
                                          "!Silent",
                                          "Color",
                                          "DrawProgressBar",
                                          "Transformations=I;D;P;G,D",
                                          "AnalysisType=Classification"]))

	dataloader = root.TMVA.DataLoader("dataloader")

	SFile = root.TFile("source/"+SFILENAME)
	STree = SFile.Get(TREENAME)
	dataloader.AddSignalTree(STree)

	BFile1 = root.TFile("source/"+"ZgQCD.root")
	BFile2 = root.TFile("source/"+"ttgamma.root")
	BFile3 = root.TFile("source/"+"SinglePhoton.root")
	BFile4 = root.TFile("source/"+"WenuDataDriven.root")
	BFile5 = root.TFile("source/"+"Wgam.root")
	BFile6 = root.TFile("source/"+"WgamEWK.root")
	BFile7 = root.TFile("source/"+"Zllgam.root")
	BFile8 = root.TFile("source/"+"ZnunuFromQcd.root")

	BTree1 = BFile1.Get(TREENAME)
	BTree2 = BFile2.Get(TREENAME)
	BTree3 = BFile3.Get(TREENAME)
	BTree4 = BFile4.Get(TREENAME)
	BTree5 = BFile5.Get(TREENAME)
	BTree6 = BFile6.Get(TREENAME)
	BTree7 = BFile7.Get(TREENAME)
	BTree8 = BFile8.Get(TREENAME)

	dataloader.AddBackgroundTree(BTree1)
	dataloader.AddBackgroundTree(BTree2)
	dataloader.AddBackgroundTree(BTree3)
	dataloader.AddBackgroundTree(BTree4)
	dataloader.AddBackgroundTree(BTree5)
	dataloader.AddBackgroundTree(BTree6)
	dataloader.AddBackgroundTree(BTree7)
	dataloader.AddBackgroundTree(BTree8)

	dataloader.AddVariable("mJJ","F")
	dataloader.AddVariable("deltaYJJ","F")
	dataloader.AddVariable("metPt","F")
	dataloader.AddVariable("ptBalance","F")
	dataloader.AddVariable("subleadJetEta","F")
	dataloader.AddVariable("leadJetPt","F")
	dataloader.AddVariable("photonEta","F")
	dataloader.AddVariable("ptBalanceRed","F")
	dataloader.AddVariable("nJets","F")
	dataloader.AddVariable("sinDeltaPhiJJOver2","F")
	dataloader.AddVariable("deltaYJPh","F")

	dataloader.AddSpectator("weightModified", "F")

	cut = root.TCut("(nJets > 1)&&(nLeptons == 0)")

	dataloader.PrepareTrainingAndTestTree(cut, ":".join(["nTrain_Signal=0",
														 "nTrain_Background=0",
														 "SplitMode=Random",
														 "NormMode=NumEvents",
														 "!V"]))

	method = factory.BookMethod(dataloader, root.TMVA.Types.kBDT, "BDTG",
                            ":".join([ "!H",
                                       "!V",
                                       "NTrees=850",
                                       "nEventsMin=150",
                                       "MaxDepth=3",
                                       "BoostType=Grad",
                                       "AdaBoostBeta=0.5",
                                       "SeparationType=GiniIndex",
                                       "nCuts=20",
                                       "PruneMethod=NoPruning",
                                       ]))

	factory.TrainAllMethods()
	factory.TestAllMethods()
	factory.EvaluateAllMethods()
	fout.Close()

	root.TMVA.TMVAGui("output.root")
	root.gApplication.Run()


if __name__ == "__main__":
	root.TMVA.Tools.Instance()
	main()