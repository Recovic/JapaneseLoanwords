# coding: utf-8
# 利用字符串对齐算法对数据集进行分块

import levdis
import codecs

MAXLEN = 4

infile = ''
outfile = ''
kadic = {} # kata -> romaji
roset = set()        # single syllable only
roset_all = set()    # single and double syllable

def init():
	levdis.init()
	with codecs.open('data/kata_romaji.txt', mode='r', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split('\t')
			kadic[pair[0]] = pair[1]
			roset.add(pair[1])
	with codecs.open('data/kata_romaji_double.txt', mode='r', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split('\t')
			kadic[pair[0]] = pair[1]
			roset_all.add(pair[1])
	roset_all.update(roset)


def ka2ro(ja):
	i = 0
	n = len(ja)
	ret = ''

	while i < n:
		m = min(MAXLEN, n - i)
		found = False
		for k in range(m, 0, -1):
			u = ja[i:i + k]
			if u in kadic:
				found = True
				i += k
				ret += kadic[u]
				break
		if not found:
			return ''

	return ret



# 将英文按照与日语对齐进行分块
# 输入：罗马音与英文
# 输出：分块数组
# all: True: 考虑双元音
def chunk(en, ka, all=True):
	ro = ka2ro(ka)
	en2, ja2 = levdis.align(en, ro)
	n = len(ja2)
	tmp = [0] * (n-1)

	i = 0
	while i < n:
		m = min(6, n - i)
		for k in range(m, 0, -1):
			u = ja2[i:i + k]
			if '___' in u: # 忽略对齐后相距过远的项
				return []
			v = u.replace('_', '')
			if not v:
				return []
			if all:
				if v in roset_all:
					# for l in range(i+k-1, i-1, -1):
					# 	if ja2[l] == '_' and en2[l] not in 'aeiou':
					# 		i -= 1
					# 	else:
					# 		break

					i += k
					if 0 < i < n:
						tmp[i-1] = 1
					break
			else:
				if v in roset:
					i += k
					if 0 < i < n:
						tmp[i - 1] = 1
					break
		else:
			return []

	j = -1
	l = len(en) - 1
	ans = [0] * l
	for i in range(n-1):
		if en2[i] != '_':
			j += 1
			if j >= l:
				break
			ans[j] = tmp[i]
		elif j >= 0:
			if tmp[i] == 1 or tmp[i-1] == 1:
				ans[j] = 1
	return ans


if __name__ == '__main__':
	init()

	chunk('percent', 'パー')

	outf = codecs.open('data/train_chunked_double.data', mode='w', encoding='UTF-8')
	outf2 = codecs.open('data/train_chunked_single.data', mode='w', encoding='UTF-8')
	with codecs.open('data/train.data', mode='r', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n')
			line = line.strip('\r')
			pair = line.split(',')
			en = pair[0]
			ja = pair[1]
			l1 = chunk(en, ja)
			l2 = chunk(en, ja, all=False)
			if l1:
				s = ''.join(str(i) for i in l1)
				outf.write(en + ',' + s + ',' + ja + '\n')
			if l2:
				s = ''.join(str(i) for i in l2)
				outf2.write(en + ',' + s + ',' + ja + '\n')
	outf.close()
	outf2.close()

	with codecs.open('data/test_chunked.data', mode='w', encoding='UTF-8') as outf:
		with codecs.open('data/test.data', mode='r', encoding='UTF-8') as file:
			for line in file.readlines():
				line = line.strip('\n')
				line = line.strip('\r')
				pair = line.split(',')
				en = pair[0]
				ja = pair[1]
				l = chunk(en, ja)
				if l:
					s = ''.join(str(i) for i in l)
					outf.write(en + ',' + s + ',' + ja + '\n')
