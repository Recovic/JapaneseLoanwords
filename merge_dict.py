# coding: utf-8

import codecs
import random

alpha = 0.95   # train data 比例

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


def merge():
	ans = {}

	with codecs.open('data/dictionary_filter.txt', mode='r', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split(',')
			en = pair[0].lower()
			en = ''.join(list(filter(isLetter, en)))
			ja = ''.join(list(filter(isKata, pair[1])))
			ans[en] = ja

	with codecs.open('data/dictionary_cmudict.txt', mode='r', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split(',')
			en = pair[0].lower()
			en = ''.join(list(filter(isLetter, en)))
			ja = ''.join(list(filter(isKata, pair[1])))
			if en not in ans:
				ans[en] = ja

	with codecs.open('data/dictionary_merge.txt', mode='w', encoding='UTF-8') as file:
		for key in ans:
			file.write(key + ',' + ans[key] + '\n')


def separate():
	train = codecs.open('data/train.data', mode='w', encoding='UTF-8')
	test = codecs.open('data/test.data', mode='w', encoding='UTF-8')

	with codecs.open('data/dictionary_merge.txt', mode='r', encoding='UTF-8') as file:
		for line in file.readlines():
			if random.random() < alpha:
				line = line.replace(' ', '')
				train.write(line)
			else:
				if ' ' not in line:
					test.write(line)

	train.close()
	test.close()

if __name__ == '__main__':
	merge()
	separate()
