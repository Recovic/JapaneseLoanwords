# coding: utf-8

import codecs
import random
import math

kuset_single = set()
kuset_double = set()
kuset_n = set()

minCount = 1000


with codecs.open('../data/kata_romaji.txt', encoding='UTF-8') as file:
	for line in file.readlines():
		line = line.strip('\n')
		line = line.strip('\r')
		pair = line.split('\t')
		kuset_single.add(pair[0])
with codecs.open('../data/kata_romaji_double.txt', encoding='UTF-8') as file:
	for line in file.readlines():
		line = line.strip('\n')
		line = line.strip('\r')
		pair = line.split('\t')
		kuset_double.add(pair[0])
with codecs.open('kata_romaji_n.txt', encoding='UTF-8') as file:
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

percent = 0.9

if __name__ == '__main__':
	count = 0
	ofile1 = codecs.open('train.data', encoding='utf-8', mode='w')
	ofile2 = codecs.open('test.data', encoding='utf-8', mode='w')
	with codecs.open('../corpus/bccwj.tsv', encoding='utf-8') as file:
		for line in file.readlines():
			count += 1
			if count == 1:
				continue

			line = line.strip('\n').strip('\r')
			pair = line.split('\t')
			jalist = splitku(pair[1], "n")
			#jalist = [pair[1]]
			label = pair[5]
			freq = int(pair[6])
			times = int((freq / float(minCount)) ** 0.7) + 1

			if len(jalist) > 3:
				if random.uniform(0, 1) < percent:
					for i in range(times):
						ofile1.write("__label__" + label)
						for u in jalist:
							ofile1.write(" " + u)
						ofile1.write('\n')
				else:
					ofile2.write("__label__" + label)
					for u in jalist:
						ofile2.write(" " + u)
					ofile2.write('\n')

	ofile1.close()
	ofile2.close()
