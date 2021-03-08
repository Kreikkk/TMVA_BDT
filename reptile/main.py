from dataloader import extract
from reptile.Networks import MLP
from reptile.Core.Core import core

import matplotlib.pyplot as plt
import time
import pandas as pd

SDataframe, BDataframe = extract()

SDataset, BDataset = core.array(SDataframe, dtype=core.float64), core.array(BDataframe, dtype=core.float64)

SLen, BLen = len(SDataset), len(BDataset)
# STrainLen = round(0.0001*SLen)
# BTrainLen = round(0.0001*BLen)
STrainLen = 1
BTrainLen = 1

STestDataframe = SDataframe.iloc[STrainLen:].copy()
BTestDataframe = BDataframe.iloc[BTrainLen:].copy()
# print(STestDataframe)

STrainset, BTrainset = SDataset[:STrainLen], BDataset[:BTrainLen]
STestset, BTestset = SDataset[STrainLen:], BDataset[BTrainLen:]

STrainlabels = core.array([[1] for _ in range(len(STrainset))])
BTrainlabels = core.array([[0] for _ in range(len(BTrainset))])

STestlabels = core.array([[1] for _ in range(len(STestset))])
BTestlabels = core.array([[0] for _ in range(len(BTestset))])

train_dataset = core.vstack((STrainset, BTrainset))[:,:-3]
train_labels = core.vstack((STrainlabels, BTrainlabels))

test_dataset = core.vstack((STestset, BTestset))[:,:-3]
test_labels = core.vstack((STestlabels, BTestlabels))


def normalize(ds):
	for col_id in range(len(ds[0])):
		col = ds[:, col_id]
		mn, mx = min(col), max(col)
		ds[:, col_id] = (col - mn)/(mx - mn)

normalize(train_dataset)
normalize(test_dataset)

# net = MLP()\
# 		.input(11)\
# 		.layer(21)\
# 		.layer(21)\
# 		.layer(1)\

# t = time.time()
# net.fit(
# 	train_dataset,
# 	train_labels,
# 	batch_size=5,
# 	learning_const=0.02,
# 	epochs=400,
# 	print_error=False,)
# print(f"Total time: {time.time() - t}")

# net.dumps("new_upd_model.json")

net = MLP()

net.loads(file_path="new_model.json")


answers = net.feed(test_dataset)
answers = answers.reshape((1,len(answers)))[0]
print(len(answers))
print(len(STestDataframe.values))
print(len(BTestDataframe.values))
STestlen = len(STestDataframe.values)

STestDataframe["output"] = answers[:STestlen]
BTestDataframe["output"] = answers[STestlen:]


SWeights = core.array(STestDataframe["weightModified"])
BWeights = core.array(BTestDataframe["weightModified"])

plt.hist(answers[:STestlen], weights=SWeights/core.sum(SWeights), color="blue", alpha=0.75, bins=50, density=False)
plt.hist(answers[STestlen:], weights=BWeights/core.sum(BWeights), color="red", alpha=0.75, bins=50, density=False)
plt.show()

Ss, Bs = [], []
Xs = core.linspace(min(answers), max(answers), 1000)
for cursor in Xs:
	S = sum(STestDataframe[STestDataframe["output"] >= cursor]["weightModified"])
	B = sum(BTestDataframe[BTestDataframe["output"] >= cursor]["weightModified"])

	Ss.append(S)
	Bs.append(B)

Ss, Bs = core.array(Ss), core.array(Bs)
SignVal = Ss/(Ss + Bs)**0.5
print(core.max(SignVal))

plt.plot(Xs, SignVal)
plt.grid()
plt.show()