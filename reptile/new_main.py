from dataloader import extract
from reptile.Networks import MLP
from reptile.Core.Core import core

import matplotlib.pyplot as plt
import time
import pandas as pd



def dataset_gen(train_ratio=0.99, shuffle_seed=1):
	SDataframe, BDataframe = extract()
	SDataframe["label"] = 1
	BDataframe["label"] = 0

	Dataframe = SDataframe.append(BDataframe, ignore_index=True)
	Dataframe = Dataframe.sample(frac=1, random_state=shuffle_seed).reset_index(drop=True)
	Dataframe["response"] = 0
	train_set_size = round(len(Dataframe)*train_ratio)

	TrainDataframe = Dataframe.iloc[:train_set_size].copy()
	TestDataframe  = Dataframe.iloc[train_set_size:].copy()

	return TrainDataframe, TestDataframe


def normalize(dataset):
	for index in range(len(dataset[0])):
		col = dataset[:,index]
		mn, mx = min(col), max(col)
		dataset[:,index] = (col - mn)/(mx - mn)


def train(fname="model"):
	train_df, _  = dataset_gen()
	train_data   = core.array(train_df.iloc[:,:11], dtype="float64")
	train_labels = core.array([[item] for item in train_df["label"]], dtype="float64")
	normalize(train_data)

	net = MLP()\
			.input(11)\
			.layer(21)\
			.layer(11)\
			.layer(1)\

	t = time.time()

	net.fit(
		train_data,
		train_labels,
		batch_size=5,
		learning_const=0.02,
		epochs=500,
		print_error=False,)

	print(f"Total time: {time.time() - t}")

	net.dumps(f"{fname}.json")


def apply(fname="model"):
	net = MLP()
	net.loads(file_path=f"{fname}.json")

	_, test_df = dataset_gen()															
	# test_df, _ = dataset_gen()															
	test_data   = core.array(test_df.iloc[:,:11], dtype="float64")
	test_labels = core.array([[item] for item in test_df["label"]], dtype="float64")
	normalize(test_data)

	answers = net.feed(test_data).reshape((1,len(test_labels)))[0]
	test_df["response"] = answers

	SDataframe = test_df[test_df["label"] == 1]
	BDataframe = test_df[test_df["label"] == 0]

	SWeights = SDataframe["weightModified"]
	BWeights = BDataframe["weightModified"]

	plt.hist(SDataframe["response"], weights=SWeights/core.sum(SWeights), color="blue", bins=50, alpha=0.75)
	plt.hist(BDataframe["response"], weights=BWeights/core.sum(BWeights), color="red", bins=50, alpha=0.75)
	plt.show()

	Ss, Bs = [], []
	Xs = core.linspace(core.min(answers), core.max(answers), 1000)
	for cursor in Xs:
		S = core.sum(SDataframe[SDataframe["response"] >= cursor]["weightModified"])
		B = core.sum(BDataframe[BDataframe["response"] >= cursor]["weightModified"])

		Ss.append(S)
		Bs.append(B)

	Ss = core.array(Ss)
	Bs = core.array(Bs)
	
	SignVal = Ss/(Ss + Bs)**0.5
	print(core.max(SignVal))

	plt.plot(Xs, SignVal)
	plt.grid()
	plt.show()


if __name__ == "__main__":
	train("MLP12_analog_100proc")
	# apply("MLP12_analog")