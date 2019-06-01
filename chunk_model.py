# coding: utf-8
# 分块模型

import codecs
import nltk
import pickle
import math
from nltk.classify import MaxentClassifier
from nltk.classify import SklearnClassifier
from sklearn.linear_model import LogisticRegression

c = 3
beamsize = 500
selsize = 10
#nltk.config_megam('./megam.opt')

def save_model(clas):
	save_classifier = open("model/chunk.dump", "wb")
	pickle.dump(clas, save_classifier)
	save_classifier.close()

def load_model():
	classifier_f = open("model/chunk.dump", "rb")
	clas = pickle.load(classifier_f)
	classifier_f.close()
	return clas

def gen_x(e, z, j):
	x = {}
	# z[j-c-1 : j-1]
	for k in range(1, c + 2):
		key = 'z' + str(-k)
		if j - k >= 0:
			x[key] = z[j - k]
		else:
			x[key] = ''

	# e[j-c : j+c+1]
	for k in range(-c, c + 2):
		key = 'e' + str(k)
		if j + k >= 0 and j + k < len(e):
			x[key] = e[j + k]
		else:
			x[key] = ''
	return x

def m_train():
	train = []
	with codecs.open('data/train_chunked_double.data', mode='r', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split(',')

			e = pair[0]
			z = pair[1]

			for j in range(len(z)):
				x = gen_x(e, z, j)
				y = z[j]
				train.append((x, y))

	try:
		clas = SklearnClassifier(LogisticRegression(solver='lbfgs', n_jobs=-1, max_iter=200)).train(train)
		save_model(clas)
		return clas

	except Exception as e:
		print('Error: %r' % e)
		return None


def predict(clas, en):
	# 使用 beam search 进行遍历
	seqs = [['', 0.0]]
	for j in range(len(en) - 1):
		all = list()
		for i in range(len(seqs)):
			seq, prob = seqs[i]
			x = gen_x(en, seq, j)
			pdist = clas.prob_classify(x)
			# 0
			candidate = [seq + '0', prob - math.log(pdist.prob('0'))]
			all.append(candidate)
			# 1
			candidate = [seq + '1', prob - math.log(pdist.prob('1'))]
			all.append(candidate)

		ordered = sorted(all, key=lambda tup: tup[1])
		seqs = ordered[:beamsize]
	return seqs


def m_test(clas):
	count_ok = 0
	count_all = 0
	with codecs.open('data/test_chunked.data', mode='r', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split(',')

			e = pair[0]
			z = pair[1]

			seqs = predict(clas, e)
			for i in range(selsize):
				a, b = seqs[i]
				if a == z:
					count_ok += 1
					break
			count_all += 1
	print(count_ok / count_all)


if __name__ == '__main__':
	clas = m_train()
	#m_test(clas)


