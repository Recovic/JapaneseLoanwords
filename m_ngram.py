# coding: utf-8
# 使用 N-Grams 训练语言模型, N=4

import codecs
import pickle
import string
from nltk.classify import SklearnClassifier
from sklearn.linear_model import LogisticRegression

N = 4
times_base = 5000
mincount = 1000

def add(dic, elem, time=1):
	if elem in dic:
		dic[elem] += time
	else:
		dic[elem] = time

class NGram:
	def __init__(self):
		self.dic3 = {}
		self.dic4 = {}
		self.clas = None

	def load_from_text(self, filename):
		with codecs.open(filename, encoding='UTF-8') as file:
			while True:
				line = file.readline()
				if not line:
					break

				line = line.strip('\n')
				line = line.strip('\r')
				line = line.lower()
				line = line.replace('\'', '')

				# 去掉标点符号
				ng = string.punctuation + string.digits
				for c in line:
					if c in ng:
						line = line.replace(c, ' ')

				words = line.split(' ')
				for w in words:
					if w:
						w = '   ' + w
						for i in range(3, len(w)):
							w3 = w[i-3:i]
							w4 = w[i-3:i+1]
							add(self.dic3, w3)
							add(self.dic4, w4)

	def load_from_dict(self, filename):
		with codecs.open(filename, encoding='UTF-8') as file:
			for line in file.readlines():
				line = line.strip('\n')
				line = line.strip('\r')
				pair = line.split(' ')
				word = pair[0]
				time = int(pair[1])
				w = ' ' * (N - 1) + word
				if time > mincount:
					for i in range(0, len(w) - (N - 1)):
						add(self.dic3, w[i: i+N-1], time)
						add(self.dic4, w[i: i+N], time)


	def train(self, filename, train_data_only=False):
		train_data = []
		word_set = set()
		if train_data_only:
			with codecs.open('data/train_chunked_double.data', mode='r', encoding='UTF-8') as file:
				for line in file.readlines():
					line = line.strip('\n').strip('\r')
					line = line.split(',')
					word_set.add(line[0])
			with codecs.open('cmudict/cmudict-0.7b.txt', mode='r', encoding='UTF-8') as file:
				for line in file.readlines():
					line = line.strip('\n').strip('\r')
					pair = line.split('  ')
					word_set.add(pair[0].lower())

		with codecs.open(filename, encoding='UTF-8') as file:
			for line in file.readlines():
				line = line.strip('\n')
				line = line.strip('\r')
				pair = line.split(' ')
				word = pair[0]
				if (not train_data_only) or (word in word_set):
					time = int(pair[1])
					w = ' ' * (N - 1) + word
					for i in range(0, len(w) - (N - 1)):
						x = {}
						for j in range(N - 1):
							x[str(j)] = w[i + j]

						y = w[i + N - 1]
						train_data.extend([(x, y)] * (int(time / times_base) + 1))

		print('File loaded.')
		clas = SklearnClassifier(LogisticRegression(solver='lbfgs', n_jobs=-1, max_iter=100)).train(train_data)
		with open("model/ngram.dump", "wb") as save:
			pickle.dump(clas, save)

	def load_from_list(self, filename):
		with codecs.open(filename, encoding='UTF-8') as file:
			while True:
				line = file.readline()
				if not line:
					break
				line = line.strip('\n')
				line = line.strip('\r')
				pair = line.split(' ')
				add(self.dic3, pair[0])
				elem = pair[0] + pair[1]
				add(self.dic4, elem)


	def save_model(self):
		save3 = open("model/dic3.dump", "wb")
		pickle.dump(self.dic3, save3)
		save3.close()
		save4 = open("model/dic4.dump", "wb")
		pickle.dump(self.dic4, save4)
		save4.close()

	def load_model_old(self):
		save3 = open("model/dic3.dump", "rb")
		self.dic3 = pickle.load(save3)
		save3.close()
		save4 = open("model/dic4.dump", "rb")
		self.dic4 = pickle.load(save4)
		save4.close()

	def load_model(self):
		with open('model/ngram.dump', 'rb') as file:
			self.clas = pickle.load(file)
		return self

	def predict_old(self, string):
		s3 = string[:3]
		if string in self.dic4 and s3 in self.dic3:
			return self.dic4[string] / self.dic3[s3]
		else:
			return 0.0

	def predict(self, string):
		x = {}
		for i in range(N-1):
			x[str(i)] = string[i]
		y = string[N-1]
		pdist = self.clas.prob_classify(x)
		return pdist.prob(y)


if __name__ == '__main__':
	ngram = NGram()
	ngram.train('data/endict.txt', True)
	# ngram.load_model()
	# while True:
	# 	s = input("input:")
	# 	print(ngram.predict(s))