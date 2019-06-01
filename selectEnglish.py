# coding: utf-8
# 从语料库中统计英文词库

import codecs
import string

def isLetter(ch):
	if ch >= 'a' and ch <= 'z':
		return True
	else:
		return False

def select():
	ans = {}
	with codecs.open('corpus/enwiki.xml', encoding='UTF-8') as file:
		while True:
			line = file.readline()
			if not line:
				break

			line = line.strip('\n')
			line = line.strip('\r')
			line = line.lower()
			line = line.replace('\'', '')
			line = line.replace('-', '')

			# 去掉标点符号
			ng = string.punctuation + string.digits
			for c in line:
				if c in ng:
					line = line.replace(c, ' ')

			words = line.split(' ')
			for w in words:
				if w and isLetter(w[0]):
					w = ''.join(list(filter(isLetter, w)))
					if w in ans:
						ans[w] += 1
					else:
						ans[w] = 1


	with codecs.open('data/endict.txt', mode='w', encoding='UTF-8') as file:
		for w in ans:
			if ans[w] >= 5:
				file.write(w + ' ' + str(ans[w]) + '\n')



if __name__ == '__main__':
	select()