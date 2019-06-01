# coding: utf-8
# 语言模型

import codecs
import nltk
import pickle
import math
from nltk.classify import MaxentClassifier
from nltk.classify import SklearnClassifier
from sklearn.linear_model import LogisticRegression

b = 3
beamsize = 1000
selsize = 10
#nltk.config_megam('D:/Workspace/megam_0.92/megam.opt')

kuset_single = set()
kuset_double = set()

def init():
	with codecs.open('data/kata_romaji.txt', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split('\t')
			kuset_single.add(pair[0])
	with codecs.open('data/kata_romaji_double.txt', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split('\t')
			kuset_double.add(pair[0])



def save_model(clas):
	save_classifier = open("model/translation.dump", "wb")
	pickle.dump(clas, save_classifier)
	save_classifier.close()

def load_model():
	classifier_f = open("model/translation.dump", "rb")
	clas = pickle.load(classifier_f)
	classifier_f.close()
	return clas

# mode: single, double, all
# mode 'all' splits into list of tuple
def splitku(kus, mode='double'):
	i = 0
	n = len(kus)
	ret = []
	double = False
	all = False
	if mode == 'double' or mode == 'all':
		double = True
	if mode == 'all':
		all = True
	while i < n:
		m = min(4, n - i)
		found = False
		for k in range(m, 0, -1):
			u = kus[i:i + k]
			if double and u in kuset_double:
				found = True
				i += k
				if all:
					ret.append((u[:-1], u[-1]))
				else:
					ret.append(u)
				break
			if u in kuset_single:
				found = True
				i += k
				if all:
					ret.append((u,))
				else:
					ret.append(u)
				break
		if not found:
			return []

	return ret


def G(e):
	if not e:
		return ''
	elif e in "aeiou":
		return '0'
	elif e in "hy":
		return '1'
	else:
		return '2'


def read_train_data(filename, double):
	train = []
	with codecs.open(filename, mode='r', encoding='UTF-8') as file:
		count = 0
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split(',')

			e = pair[0]
			z = pair[1]
			kus = pair[2]

			start = {}
			end = {}
			eu = []
			if double:
				ku = splitku(kus, mode='double')
			else:
				ku = splitku(kus, mode='single')

			i = 0
			start[0] = 0
			cur = e[0]
			for j in range(len(z)):
				if z[j] == '1':
					eu.append(cur)
					cur = e[j + 1]
					end[i] = j
					start[i+1] = j+1
					i += 1
				else:
					cur += e[j + 1]
			if cur:
				eu.append(cur)
				end[i] = len(e) - 1

			if len(ku) == len(eu):
				count += 1
			else:
				continue

			for i in range(len(eu)):
				x = {}
				x['eu'] = eu[i]

				for j in range(1, b+1):
					key = start[i] - j
					if key >= 0:
						x[str(-j)] = e[key]
						x['g' + str(-j)] = G(e[key])
					else:
						x[str(-j)] = ''
						x['g' + str(-j)] = ''

				key = end[i] + 1
				if key < len(e):
					x['+1'] = e[key]
					x['g+1'] = G(e[key])
				else:
					x['+1'] = ''
					x['g+1'] = ''

				# 加入假名上文
				if i > 0:
					x['k-1'] = ku[i-1][-1]
				else:
					x['k-1'] = ''

				y = ku[i]
				train.append((x, y))

		print(str(count) + ' lines read.')
	return train

def m_train():
	train = []
	train += read_train_data('data/train_chunked_double.data', double=True)
	train += read_train_data('data/train_chunked_single.data', double=False)

	try:
		clas = SklearnClassifier(LogisticRegression(solver='lbfgs', n_jobs=8, max_iter=500)).train(train)
		save_model(clas)
		return clas

	except Exception as e:
		print('Error: %r' % e)
		return None



def predict(clas, e, z):
	# 使用 beam search 进行遍历
	start = {}
	end = {}
	eu = []

	i = 0
	start[0] = 0
	cur = e[0]
	for j in range(len(z)):
		if z[j] == '1':
			eu.append(cur)
			cur = e[j + 1]
			end[i] = j
			start[i + 1] = j + 1
			i += 1
		else:
			cur += e[j + 1]
	if cur:
		eu.append(cur)
		end[i] = len(e) - 1


	seqs = [['', 0.0]]
	for i in range(len(eu)):
		all = list()

		x = {}
		x['eu'] = eu[i]

		for j in range(1, b + 1):
			key = start[i] - j
			if key >= 0:
				x[str(-j)] = e[key]
			else:
				x[str(-j)] = ''

		key = end[i] + 1
		if key < len(e):
			x['+1'] = e[key]
		else:
			x['+1'] = ''

		pdist = clas.prob_classify(x)

		for j in range(len(seqs)):
			seq, prob = seqs[j]
			samples = pdist.samples()
			for sam in samples:
				candidate = [seq + sam, prob - math.log(pdist.prob(sam))]
				all.append(candidate)

		ordered = sorted(all, key=lambda tup: tup[1])
		seqs = ordered[:beamsize]
	return seqs


def m_test(clas):
	count_ok = 0
	count_all = 0
	with codecs.open('data/test_chunked2.data', mode='r', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split(',')

			e = pair[0]
			z = pair[1]

			seqs = predict(clas, e, z)
			for i in range(selsize):
				a, b = seqs[i]
				if a == pair[2]:
					count_ok += 1
					break
			count_all += 1

	print(count_ok / count_all)

if __name__ == '__main__':
	init()
	m_train()