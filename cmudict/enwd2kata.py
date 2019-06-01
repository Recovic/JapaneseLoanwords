# coding: UTF-8
# 按照对照表生成备选日语发音

import codecs
import math

legalEnd = ['a', 'i', 'u', 'e', 'o', 'n']
beamsize = 100
selectsize = 50

mincount = 10    # 日语词库 最低词频
minkatalen = 3     # 最短词长
MINPROB = 0.1   # 元素概率阈值
MAXLEN = 6       # 前缀最大长度

dic_k2j = {}

# 读取英语发音-日语发音对照表，返回dic(string, list((string, float)))
def readEn2Ja(filename):
	dic = {}
	with codecs.open(filename, encoding='UTF-8') as file:
		en = ''
		for line in file.readlines():
			line = line.strip('\n')
			pair = line.split('\t')

			pair[0] = pair[0].strip()
			if pair[0]:
				en = pair[0]
				dic[en] = []

			prob = float(pair[2])
			if prob > MINPROB:
				ja = pair[1].replace(' ', '')
				dic[en].append((ja, prob))
	return dic


# 读取日语罗马音-片假名对照表，返回dict(string, string)
def readKa2Ja(filename):
	dic = {}
	with codecs.open(filename, encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			pair = line.split('\t')
			kata = pair[0]
			roma = pair[1]

			dic[roma] = kata
	with codecs.open('../data/kata_romaji2.txt', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			pair = line.split('\t')
			kata = pair[0]
			roma = pair[1]

			dic[roma] = kata
	return dic


# 读取日语词库
def readCorpus(filename):
	ret = set()
	with codecs.open(filename, encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			pair = line.split(' ')

			if int(pair[1]) > mincount:
				ret.add(pair[0])

	return ret

# 尝试使用最长前缀匹配算法将罗马音串转换为片假名串，若无法转换则返回空字符串
def japh2kata(ja):
	i = 0
	n = len(ja)
	ret = ''

	while i < n:
		m = min(MAXLEN, n - i)
		found = False
		for k in range(m, 0, -1):
			u = ja[i:i+k]
			if u in dic_k2j:
				found = True
				i += k
				ret += dic_k2j[u]
				break
		if not found:
			return ''

	return ret

def isNum(ch):
	if ch >= '0' and ch <= '9':
		return True
	else:
		return False


if __name__ == '__main__':
	ans = {}
	dic_k2j = readKa2Ja('../data/kata_romaji.txt')

	dic1 = readEn2Ja('enph2japh.txt')
	wordSet = readCorpus('../data/jadict.txt')

	with codecs.open('../data/dictionary_cmudict.txt', mode='w', encoding='UTF-8') as outfile:
		with codecs.open('cmudict-0.7b.txt', encoding='UTF-8') as file:
			for line in file.readlines():

				line = line.strip('\n')
				pair = line.split('  ')

				# 去除多种发音词汇的尾标
				spell = pair[0]
				if len(spell) >= 3 and spell[-1] == ')' and spell[-3] == '(':
					spell = spell[:-3]
				enph = pair[1].split(' ')
				japhMatrix = []
				japhAns = {}

				length = len(enph)

				ok = True

				for i in range(length):
					tone = enph[i]
					# 去除重音信息
					if isNum(tone[-1]):
						tone = tone[:-1]

					# 去除以辅音结尾的发音
					japhUnit = dic1[tone]  # list of (string, float)
					if i == length - 1:
						tmp = []
						for unit in japhUnit:
							if unit[0][-1] in legalEnd:
								tmp.append(unit)
						japhUnit = tmp

					if not japhUnit:
						ok = False
						break

					japhMatrix.append(japhUnit)

				if not ok:
					continue

				# 使用 beam search 进行遍历
				seqs = [[list(), 0.0]]
				for row in japhMatrix:
					all = list()
					for i in range(len(seqs)):
						seq, prob = seqs[i]
						for j in range(len(row)):
							candidate = [seq + [row[j][0]], prob - math.log(row[j][1])]
							all.append(candidate)
					ordered = sorted(all, key=lambda tup:tup[1])
					seqs = ordered[:beamsize]

				for i in range(min(len(seqs), selectsize)):
					seq, prob = seqs[i]
					s = ''.join(seq)
					kata = japh2kata(s)
					if (len(kata) >= minkatalen) and (kata in wordSet):
						outfile.write(spell + ',' + kata + '\n')
						break
