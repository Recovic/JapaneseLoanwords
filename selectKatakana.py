# coding: UTF-8
# 从语料库中选择片假名词汇
# 逐字确认，保留连续的片假名序列

import codecs

def isKata(ch):
	if ch >= '\u30a0' and ch <= '\u30ff':
		return True
	else:
		return False

ans = {}
with codecs.open('corpus/jawiki.xml', encoding='UTF-8') as file:
	while True:
		line = file.readline()
		if not line:
			break

		#line = line.strip('\n')
		flag = False
		w = ''

		for ch in line:
			if flag:
				if isKata(ch):
					w += ch
				else:
					flag = False
					if len(w) > 1:
						if w in ans:
							ans[w] += 1
						else:
							ans[w] = 1
					w = ''
			else:
				if isKata(ch):
					w += ch
					flag = True


with codecs.open('data/jadict.txt', mode='w', encoding='UTF-8') as file:
	for w in ans:
		if ans[w] > 1:
			file.write(w + ' ' + str(ans[w]) + '\n')