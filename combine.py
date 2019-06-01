# coding: utf-8
# 整合模型

import codecs
import math
import pickle
import m_ngram
import chunk_model

min_count = 10
selsize = 10
dicnum = 100000
inf = float('inf')

def split_en(e, z):
	eu = []
	i = 0
	#start[0] = 0
	cur = e[0]
	for j in range(len(z)):
		if z[j] == '1':
			eu.append(cur)
			cur = e[j + 1]
			#end[i] = j
			#start[i + 1] = j + 1
			i += 1
		else:
			cur += e[j + 1]
	if cur:
		eu.append(cur)
		#end[i] = len(e) - 1
	return eu


def add(dic, key, value):
	if key not in dic:
		dic[key] = [value]
	else:
		dic[key].append(value)

def ngram_chunk():
	dic = {}
	ngram = m_ngram.NGram()
	ngram.load_model()
	clas = chunk_model.load_model()

	with codecs.open('data/endict000.txt', mode='r', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split(' ')
			if int(pair[1]) > min_count:
				en = pair[0]

				# N-Gram
				score = 0.0
				cnt = 0

				for i in range(3, len(en)):
					tmp = ngram.predict(en[i-3 : i+1])
					if tmp > 0:
						score -= math.log(tmp)
						cnt += 1
					else:
						score = inf
						break

				if score == inf:
					continue

				if cnt > 0:
					score /= cnt

				# chunk
				seqs = chunk_model.predict(clas, en)
				seqs = seqs[:selsize]
				for i in range(len(seqs)):
					z, s = seqs[i]
					if z:
						key = len(z)
						s /= key
						eu = split_en(en, z)
						if score == 0:
							add(dic, key, [eu, s])
						else:
							add(dic, key, [eu, (s+score)/2])
	for key in dic:
		lst = sorted(dic[key], key=lambda tup: tup[1])
		dic[key] = lst[:dicnum]

	save_classifier = open("model/dict.dump", "wb")
	pickle.dump(dic, save_classifier)
	save_classifier.close()

	return dic


if __name__ == '__main__':
	dic = ngram_chunk()
	print(dic)