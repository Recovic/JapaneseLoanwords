# coding: utf-8
# 使用 Levenshtein Distance 对齐字符串

import numpy
import codecs
alpha = 0.5    # 特殊匹配规则权重
rule = {}

def equal(ch1, ch2):
	if ch1.lower() == ch2.lower():
		return True
	else:
		return False

def init():
	with codecs.open('data/levdis_ex.txt', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split(' ')
			if pair[0] in rule:
				rule[pair[0]].append(pair[1])
			else:
				rule[pair[0]] = [ pair[1] ]


# 最长后缀匹配特殊规则
def match(sub1, sub2):
	for i in range(max(0, len(sub1) - 3), len(sub1)):
		if sub1[i:] in rule:
			l = rule[sub1[i:]]
			for j in range(max(0, len(sub2) - 3), len(sub2)):
				if sub2[j:] in l:
					return (len(sub1) - i, len(sub2) - j)
	return (-1, -1)

def getDisMatrix(word1, word2):
	d = numpy.zeros([len(word1) + 1, len(word2) + 1])
	for i in range(0, len(word1) + 1):
		d[i][0] = i
	for i in range(0, len(word2) + 1):
		d[0][i] = i

	for i in range(1, len(word1) + 1):
		for j in range(1, len(word2) + 1):
			if equal( word1[i - 1] , word2[j - 1]):
				d[i][j] = d[i - 1][j - 1]
			else:
				(a, b) = match(word1[:i], word2[:j])
				if a != -1:
					d[i][j] = d[i-a][j-b] + alpha
				else:
					d[i][j] = min(d[i - 1][j], d[i][j - 1], d[i - 1][j - 1]) + 1

	return d


def getPath(word1, word2, dis):
	lst = []
	i = len(word1)
	j = len(word2)
	lst.append((i, j))
	while (i > 0 or j > 0):
		ch1 = ''
		ch2 = ''
		if i > 0:
			ch1 = word1[i - 1]
		if j > 0:
			ch2 = word2[j - 1]
		(a, b) = match(word1[:i], word2[:j])
		if equal(ch1 , ch2):
			i -= 1
			j -= 1
			lst.append((i, j))
		elif a != -1:
			i -= a
			j -= b
			lst.append((i, j))
		else:
			cur = dis[i][j]

			# 修改
			if (i > 0 and j > 0):
				leftup = dis[i - 1][j - 1]
				if leftup + 1 == cur:
					i -= 1
					j -= 1
					lst.append((i, j))
					continue

			# 删除
			if i > 0:
				up = dis[i - 1][j]
				if up + 1 == cur:
					i -= 1
					lst.append((i, j))
					continue

			# 插入
			if j > 0:
				left = dis[i][j - 1]
				if left + 1 == cur:
					j -= 1
					lst.append((i, j))
					continue

	return lst

def align_p(word1, word2, path):
	size = len(path)
	cur = path[0]
	nw1 = ''
	nw2 = ''
	for i in range(1, size):
		next = path[i]
		im = cur[0] - next[0]
		jm = cur[1] - next[1]
		ci = cur[0]
		cj = cur[1]

		if (im == 0) and (jm == 1):
			nw1 = '_' + nw1
			nw2 = word2[cj - 1] + nw2
		elif (im == 1) and (jm == 0):
			nw1 = word1[ci - 1] + nw1
			nw2 = '_' + nw2
		else:
			if im > jm:
				nw1 = word1[ci-im:ci] + nw1
				nw2 = word2[cj-jm:cj] + '_'*(im-jm) + nw2
			else:
				nw1 = word1[ci - im:ci] + '_'*(jm-im) + nw1
				nw2 = word2[cj - jm:cj] + nw2
		cur = next

	return (nw1, nw2)

def align(w1, w2):
	d = getDisMatrix(w1, w2)
	p = getPath(w1, w2, d)
	a, b = align_p(w1, w2, p)
	return (a, b)

if __name__ == '__main__':
	init()

	w1 = 'urbanrenewal'
	w2 = 'aabanrinyuaru'
	d = getDisMatrix(w1, w2)
	# print(d)
	p = getPath(w1, w2, d)
	a, b = align_p(w1, w2, p)

	print(p)
	print(a)
	print(b)

