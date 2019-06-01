# coding: utf-8
# 生成ku候选

import codecs
import pickle

mintime = 4

kuset = set()
kuset0 = set()
from translation_model_e2j import init
from translation_model_e2j import splitku
from translation_model_e2j import splitku2
from combine import split_en

#beamsize = 50

if __name__ == '__main__':
	init()
	dic = {}
	file = codecs.open('data/train_chunked_double.data', encoding='UTF-8')
	file2 = codecs.open('data/train_chunked_single.data', encoding='UTF-8')
	for line in file.readlines():
		line = line.strip('\n')
		line = line.strip('\r')
		pair = line.split(',')
		e = pair[0]
		z = pair[1]
		j = pair[2]

		ku = splitku(j)
		eu = split_en(e, z)

		if len(ku) == len(eu):
			for i in range(len(ku)):
				if eu[i] in dic:
					if ku[i] in dic[eu[i]]:
						dic[eu[i]][ku[i]] += 1
					else:
						dic[eu[i]][ku[i]] = 1
				else:
					dic[eu[i]] = {}
					dic[eu[i]][ku[i]] = 1

	for line in file2.readlines():
		line = line.strip('\n')
		line = line.strip('\r')
		pair = line.split(',')
		e = pair[0]
		z = pair[1]
		j = pair[2]

		ku = splitku2(j)
		eu = split_en(e, z)

		if len(ku) == len(eu):
			for i in range(len(ku)):
				if eu[i] in dic:
					if ku[i] in dic[eu[i]]:
						dic[eu[i]][ku[i]] += 1
					else:
						dic[eu[i]][ku[i]] = 1
				else:
					dic[eu[i]] = {}
					dic[eu[i]][ku[i]] = 1

	file.close()
	file2.close()

	for key in dic:
		lst = []
		for k in dic[key]:
			v = dic[key][k]
			if v > mintime:
				lst.append(k)
		dic[key] = lst

	print(dic['a'])

	with open("model/candidate_e2j.dump", "wb") as save:
		pickle.dump(dic, save)