# coding: utf-8
# 日译英模型整合

import math
import codecs
import pickle
import chunk_model
import translation_model_e2j
from translation_model_e2j import b
# beamsize = 50
selsize = 10
#next_cand_size = 3

kuset = set()
from translation_model_e2j import splitku

translation_model_e2j.init()
model = open('model/candidate_e2j.dump', 'rb')
cand = pickle.load(model)
model.close()

chunk = chunk_model.load_model()
translation = translation_model_e2j.load_model()


def predict(en):
	ans = {}
	cseqs = chunk_model.predict(chunk, en)
	for i in range(min(selsize, len(cseqs))):
		z, probc = cseqs[i]
		tseqs = translation_model_e2j.predict(translation, en, z)
		for j in range(min(selsize, len(tseqs))):
			k, probt = tseqs[j]
			prob = probc + probt
			if k not in ans:
				ans[k] = prob
			else:
				#ans[k] = min(prob, ans[k])
				ans[k] = -math.log(math.e ** (-prob) + math.e ** (-ans[k]))
	ret = []
	for key in ans:
		ret.append((key, ans[key]))
	ret = sorted(ret, key=lambda tup: tup[1])
	return ret



def test():
	count_ok = 0
	count_all = 0
	ofile = codecs.open('log_e2j.txt', mode='w', encoding='UTF-8')
	ofile.write('original,expected,first\n')
	with codecs.open('data/test_chunked2.data', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split(',')
			seqs = predict(pair[0])
			for i in range(len(seqs)):
				k = seqs[i][0]
				if i == 0 and k != pair[2]:
					ofile.write(pair[0] + ',' + pair[2] + ',' + k + '\n')
				if k == pair[2]:
					count_ok += 1
					break
			count_all += 1
	print(count_ok / count_all)


if __name__ == '__main__':
	test()
	# while True:
	# 	e = input('Input english:')
	# 	seqs = predict(e)
	# 	for i in range(min(selsize, len(seqs))):
	# 		print(seqs[i][0] + ' ' + str(math.e ** float(-seqs[i][1])))