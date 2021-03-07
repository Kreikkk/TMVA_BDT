import ROOT as root


if __name__ == "__main__":
	root.TMVA.Tools.Instance()
	root.TMVA.TMVAGui("output.root")
	root.gApplication.Run()