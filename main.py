# coding: utf-8

import e2j_final
import j2e_final
import fastText.FastText
import math
import codecs

selsize = 10

kuset_single = set()
kuset_double = set()
kuset_n = set()

minCount = 1000


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
with codecs.open('classify/kata_romaji_n.txt', encoding='UTF-8') as file:
	for line in file.readlines():
		line = line.strip('\n')
		line = line.strip('\r')
		pair = line.split('\t')
		kuset_n.add(pair[0])

# mode: single, double, all, n
# mode 'all' splits into list of tuple
def splitku(kus, mode='double'):
	i = 0
	n = len(kus)
	ret = []
	double = False
	all = False
	if mode == 'n':
		kuset_double.update(kuset_n)
		mode = 'double'
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


def isLetter(ch):
	if (ch >= 'a' and ch <= 'z') or (ch == ' '):
		return True
	else:
		return False


def isKata(ch):
	if ch >= '\u30a0' and ch <= '\u30ff':
		return True
	else:
		return False

if __name__ == '__main__':
	model = fastText.load_model('classify/train.model')
	while True:
		s = input('输入英文或日文片假名：')
		if not s:
			break

		flag = 0 # 1:en, 2:ja, -1:illegal
		for ch in s:
			if isLetter(ch):
				if flag != 0 and flag != 1:
					flag = -1
					break
				else:
					flag = 1
			elif isKata(ch):
				if flag != 0 and flag != 2:
					flag = -1
					break
				else:
					flag = 2
			else:
				flag = -1
				break

		if flag == -1:
			print('输入非法，请重新输入。')
		elif flag == 1:
			seqs = e2j_final.predict(s)
			for i in range(min(selsize, len(seqs))):
				print(seqs[i][0] + ' ' + str(math.e ** float(-seqs[i][1])))
		elif flag == 2:
			kus = splitku(s)
			st = ''
			for ku in kus:
				st += ku + ' '
			ans = model.predict(st, k=8)

			for i in range(len(ans[0])):
				if ans[0][i] == '__label__外':
					print('该词为外来语的概率为：' + str(ans[1][i]))
					break

			seqs = j2e_final.predict(s)
			for i in range(min(selsize, len(seqs))):
				print(seqs[i][0] + ' ' + str(math.e ** float(-seqs[i][1])))