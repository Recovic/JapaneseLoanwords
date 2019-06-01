# coding: utf-8
# 日译英模型整合

import math
import codecs
import pickle
import chunk_model
import translation_model as trans
from m_ngram import NGram
from suffix_model import Suffix
from translation_model import b
beamsize = 50
selsize = 10
next_cand_size = 3


trans.init()
model = open('model/candidate.dump', 'rb')
cand = pickle.load(model)
model.close()

ngram = NGram().load_model()
chunk = chunk_model.load_model()
translation = trans.load_model()
suffix = Suffix().load_model()

# input: string, string, char
# [eu_left][eu][eu_next] is part of the word
# output: pdist
def trans_classify(eu_left, eu, eu_next, lku):
	x = {}
	x['eu'] = eu
	for bi in range(1, b + 1):
		try:
			x[str(-bi)] = eu_left[-bi]
			x['g' + str(-bi)] = trans.G(eu_left[-bi])
		except:
			x[str(-bi)] = ''
			x['g' + str(-bi)] = ''
	x['+1'] = eu_next
	x['g+1'] = trans.G(eu_next)
	x['k-1'] = lku
	pdist = translation.prob_classify(x)
	return pdist


def calculate_prob(eu, seq, all, ku, nku, lku):
	e, next, z, score = seq
	if (not next) or (next == eu[0]):

		# prob of n-gram
		tmp = '   ' + e + eu
		ok = True
		count = 0
		tsc = 0.0
		for j in range(len(e), len(e) + len(eu)):
			# print(tmp[j:j+4])
			t = ngram.predict(tmp[j:j + 4])
			# print(t)
			if t == 0:
				ok = False
				break
			tsc -= math.log(t)
			count += 1

		if not ok:
			return all

		if count > 0:
			sc1 = tsc  # / count
		else:
			return all

		# find max prob of translation model
		nscore = []
		nset = set()
		if nku:
			tmp = [nku[0]]
			if len(nku) > 1:
				tmp.append(nku[0] + nku[1])
			for u in tmp:
				if u in cand:
					for neu in cand[u]:
						if neu[0] not in nset:
							pdist = trans_classify(e, eu, neu[0], lku)
							nscore.append((neu[0], -math.log(pdist.prob(ku))))
							nset.add(neu[0])
			if not nscore:
				return all
			nscore = sorted(nscore, key=lambda tup: tup[1])
			nscore = nscore[:next_cand_size]

		else:  # 最后一个ku
			next = ''
			pdist = trans_classify(e, eu, '', lku)
			nscore.append(('', -math.log(pdist.prob(ku))))

		for v in range(len(nscore)):
			next, sc2 = nscore[v]

			# prob of chunk model
			te = e + eu + next
			tz = z + '0' * (len(eu) - 1) + '1' * len(next)
			tsc = 0.0
			count = 0
			for j in range(len(z), len(tz)):
				x = chunk_model.gen_x(te, tz, j)
				pdist = chunk.prob_classify(x)
				tsc -= math.log(pdist.prob(tz[j]))
				count += 1
			if count > 0:
				sc3 = tsc  # / count
			else:
				return all
			all.append([e + eu, next, tz, (score + sc1 + sc2 + sc3)])
	return all


def merge_duplicated(lst):
	dic = {}
	for u in lst:
		key = u[0]
		if key in dic:
			dic[key] = -math.log(math.e ** (-dic[key]) + math.e ** (-float(u[3])))
		else:
			dic[key] = float(u[3])

	# 应用后缀模型
	for key in list(dic.keys()):
		if key and key[-1] in "aeiou":
			word = key[:-1]
			logprob = dic[key] - math.log(suffix.predict(word))
			#logprob2 = dic[key] - math.log(1 - suffix.predict(word))
			if word in dic:
				dic[word] = -math.log(math.e ** (-dic[word]) + math.e ** (-float(logprob)))
			else:
				dic[word] = logprob
			#dic[key] = logprob2

	ret = []
	for key in dic:
		ret.append((key, dic[key]))
	return ret


def predict(ja):
	seqs = [['', '', '', 0.0]] # e, next, z, score
	#next = ''  # 根据令翻译模型概率最大的 e[end(i)+1] 取值，来确定下一格的开头字母
	kus = trans.splitku(ja, 'all')
	for k in range(len(kus)):
		kut = kus[k]
		all = list()
		nku = None
		if k < len(kus) - 1:
			nku = kus[k + 1]
		lku = ''
		if k > 0:
			lku = kus[k - 1][-1]

		if len(kut) == 1:
			ku = kut[0]
			for i in range(len(seqs)):
				seq = seqs[i]
				for eu in cand[ku]:
					all = calculate_prob(eu, seq, all, ku, nku, lku)
		else:
			seqs2 = seqs[:]
			ku = kut[0] + kut[1]
			for i in range(len(seqs)):
				seq = seqs[i]
				for eu in cand[ku]:
					all = calculate_prob(eu, seq, all, ku, nku, lku)
			all2 = list()
			ku = kut[0]
			for i in range(len(seqs2)):
				seq = seqs2[i]
				for eu in cand[ku]:
					all2 = calculate_prob(eu, seq, all2, ku, (kut[1],), lku)
			ordered = sorted(all2, key=lambda tup: tup[3])
			seqs2 = ordered[:beamsize]
			all2 = list()
			for i in range(len(seqs2)):
				seq = seqs2[i]
				for eu in cand[ku]:
					all2 = calculate_prob(eu, seq, all2, kut[1], nku, kut[0])
			all += all2

		ordered = sorted(all, key=lambda tup: tup[3])
		seqs = ordered[:beamsize]

	seqs = merge_duplicated(seqs)
	seqs = sorted(seqs, key=lambda tup: tup[1])
	return seqs


def test2():
	count_ok = 0
	count_all = 0
	ofile = codecs.open('data/test_chunked3.data', encoding='UTF-8', mode='w')
	with codecs.open('data/test_chunked.data', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split(',')
			seqs = predict(pair[2])
			for i in range(len(seqs)):
				e = seqs[i][0]
				if (e == pair[0]) or (e[:-1] == pair[0]):
					count_ok += 1
					ofile.write(line + '\n')
					if count_ok > 50:
						return
					break
			count_all += 1
	print(count_ok / count_all)


def test():
	count_ok = 0
	count_last = 0
	count_all = 0
	rfile = codecs.open('log_right.txt', encoding='UTF-8', mode='w')
	rfile.write('ja\ten\n')
	wfile = codecs.open('log_wrong.txt', encoding='utf-8', mode='w')
	rfile.write('ja\ten\tpredict\n')
	with codecs.open('data/test_chunked2.data', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split(',')
			seqs = predict(pair[2])
			last = False
			found = False
			first = ''
			for i in range(len(seqs)):
				e = seqs[i][0]
				if i == 0:
					first = e
				if e == pair[0] or e[:-1] == pair[0]:
					count_ok += 1
					rfile.write(pair[2] + '\t' + pair[0] + '\n')
					found = True
					break
			if not found:
				wfile.write(pair[2] + '\t' + pair[0] + '\t' + first + '\n')
			if last:
				count_last += 1
			count_all += 1

	print(count_ok)
	print(count_last)
	print(count_all)
	rfile.close()
	wfile.close()

if __name__ == '__main__':
	test()
	# while True:
	# 	s = input('Input katakana:')
	# 	seqs = predict(s)
	# 	for i in range(min(selsize, len(seqs))):
	# 		print(seqs[i][0] + ' ' + str(math.e ** float(-seqs[i][1])))