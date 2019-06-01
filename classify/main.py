# coding: utf-8

import fastText.FastText
from fastText import train_supervised

def print_results(N, p, r):
	print("N\t" + str(N))
	print("P@{}\t{:.3f}".format(1, p))
	print("R@{}\t{:.3f}".format(1, r))


if __name__ == '__main__':
	# model = train_supervised(
	# 	'train.data', epoch=25, lr=1.0, wordNgrams=3, verbose=2, minCount=1
	# )
	#
	# model.save_model('train.model')
	# print_results(*model.test('test.data'))

	model = fastText.load_model('train.model')
	print(model.predict('ア メ リ カ', k=8))
