# coding: utf-8
# 生成eu候选

import codecs
import pickle

mintime = 5
select_size = 15
times_base = 1000

kuset = set()
kuset0 = set()
import translation_model as trans
from combine import split_en

#beamsize = 50


def read_dict(filename):
	dic = {}
	with codecs.open(filename, encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n').strip('\r')
			pair = line.split(' ')
			dic[pair[0]] = int(pair[1])
	return dic


endic = read_dict('data/endict.txt')


def read_data(filename, dic, double):
	with codecs.open(filename, encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split(',')
			e = pair[0]
			z = pair[1]
			j = pair[2]

			if e in endic:
				times = (endic[e] / times_base) + 1
				if double:
					ku = trans.splitku(j, mode='double')
				else:
					ku = trans.splitku(j, mode='single')

				eu = split_en(e, z)

				if len(ku) == len(eu):
					for i in range(len(ku)):
						if ku[i] in dic:
							if eu[i] in dic[ku[i]]:
								dic[ku[i]][eu[i]] += times
							else:
								dic[ku[i]][eu[i]] = times
						else:
							dic[ku[i]] = {}
							dic[ku[i]][eu[i]] = times

	return dic

# 筛选eu：排除以下几种
# 1. 含多组辅音的
# 2. 含元音且结尾为非r,l,y,w的辅音的
vowel_weak = "aiueolryw"
vowel_strong = "aeiou"
def legal(eu):
	found = False
	for ch in eu:
		if ch in vowel_strong:
			found = True
		if found and ch not in vowel_weak:
			return False
	return True

if __name__ == '__main__':
	trans.init()

	dic = {}
	dic = read_data('data/train_chunked_double.data', dic, double=True)
	dic = read_data('data/train_chunked_single.data', dic, double=False)

	for key in dic:
		lst = []
		for k in dic[key]:
			if legal(k):
				v = dic[key][k]
				if v > mintime:
					lst.append((k, v))
		lst = sorted(lst, key=lambda tup: tup[1], reverse=True)
		lst = lst[:select_size]
		nlst = []
		for tup in lst:
			nlst.append(tup[0])
		dic[key] = nlst

	# with codecs.open("data/candidate.data", mode="w", encoding='UTF-8') as file:
	# 	for key in dic:
	# 		file.write(key)
	# 		for v in dic[key]:
	# 			file.write(',' + v)
	# 		file.write('\n')

	with open("model/candidate.dump", "wb") as save:
		pickle.dump(dic, save)