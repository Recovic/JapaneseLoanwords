# coding: utf-8
# 语言模型

import codecs
import nltk
import pickle
import math
from nltk.classify import MaxentClassifier
from nltk.classify import SklearnClassifier
from sklearn.linear_model import LogisticRegression
model = open('model/candidate_e2j.dump', 'rb')
cand = pickle.load(model)
model.close()

b = 3
beamsize = 50
selsize = 10
#nltk.config_megam('D:/Workspace/megam_0.92/megam.opt')

kuset = set()
kuset2 = set()

def init():
	with codecs.open('data/kata_romaji.txt', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split('\t')
			kuset.add(pair[0])
			kuset2.add(pair[0])
	with codecs.open('data/kata_romaji_double.txt', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split('\t')
			kuset.add(pair[0])



def save_model(clas):
	save_classifier = open("model/translation_e2j.dump", "wb")
	pickle.dump(clas, save_classifier)
	save_classifier.close()

def load_model():
	classifier_f = open("model/translation_e2j.dump", "rb")
	clas = pickle.load(classifier_f)
	classifier_f.close()
	return clas



def splitku(kus):
	i = 0
	n = len(kus)
	ret = []

	while i < n:
		m = min(4, n - i)
		found = False
		for k in range(m, 0, -1):
			u = kus[i:i + k]
			if u in kuset:
				found = True
				i += k
				ret.append(u)
				break
		if not found:
			return []

	return ret


def splitku2(kus):
	i = 0
	n = len(kus)
	ret = []

	while i < n:
		m = min(4, n - i)
		found = False
		for k in range(m, 0, -1):
			u = kus[i:i + k]
			if u in kuset2:
				found = True
				i += k
				ret.append(u)
				break
		if not found:
			return []

	return ret


def G(e):
	if e in "aeiou":
		return '0'
	elif e in "hy":
		return '1'
	else:
		return '2'


def m_train():
	train = []
	with codecs.open('data/train_chunked_double.data', mode='r', encoding='UTF-8') as file:
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
			ku = splitku(kus)

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

	try:
		clas = SklearnClassifier(LogisticRegression(solver='lbfgs', n_jobs=6, max_iter=500)).train(train)
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


		for j in range(len(seqs)):
			seq, prob = seqs[j]
			if seq:
				x['k-1'] = seq[-1]
			else:
				x['k-1'] = ''
			pdist = clas.prob_classify(x)
			#samples = pdist.samples()
			if eu[i] in cand:
				for sam in cand[eu[i]]:
					candidate = [seq + sam, prob - math.log(pdist.prob(sam))]
					all.append(candidate)
			else:
				return []

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
	clas = m_train()
	#m_test(clas)
