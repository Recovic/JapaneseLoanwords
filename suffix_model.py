# coding: utf-8
# 后缀模型：用来预测词尾是否为元音

import codecs
import pickle
from nltk.classify import SklearnClassifier
from sklearn.linear_model import LogisticRegression

times_base = 5000

class Suffix:
	def __init__(self):
		self.clas = SklearnClassifier(LogisticRegression(solver='lbfgs', n_jobs=-1, max_iter=100))

	def train(self):
		train_data = []
		word_set = set()


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

		with codecs.open('data/endict.txt', encoding='UTF-8') as file:
			for line in file.readlines():
				line = line.strip('\n')
				line = line.strip('\r')
				pair = line.split(' ')
				word = pair[0]
				if word in word_set:
					times = int(pair[1])
					w = '    ' + word
					x = {}
					if w[-1] in "aeiou":
						w = w[:-1]
						y = '0'
					else:
						y = '1'
					for i in range(-1, -5, -1):
						x[str(i)] = w[i]
					train_data.extend([(x, y)] * (int(times / times_base) + 1))

		print('File loaded.')
		self.clas.train(train_data)
		with open("model/suffix.dump", "wb") as save:
			pickle.dump(self.clas, save)


	def load_model(self):
		with open('model/suffix.dump', 'rb') as file:
			self.clas = pickle.load(file)
		return self

	def predict(self, word):
		word = '    ' + word
		if word[-1] in "aeiou":
			word = word[:-1]
			y = '0'
		else:
			y = '1'
		x = {}
		for i in range(-1, -5, -1):
			x[str(i)] = word[i]
		pdist = self.clas.prob_classify(x)
		return pdist.prob(y)


if __name__ == '__main__':
	suf = Suffix()
	suf.train()
