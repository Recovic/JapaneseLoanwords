# Transliterator for loanwords in Japanese

As globalization going on, the influence of English continues to permeate other languages, and Japanese is a classic example. For new concepts, modern Japanese usually transliterate these words, and they are known as loanwords. This repository provides a two-way automatic transliteration method between Japanese and English to translate new words that are not in the dictionary. The English-to-Japanese transliteration section divides English words into units and translates each unit into Japanese, and then combines them. The same letters that appear in different English words usually have to be converted into different Japanese, so both English and Japanese context information must be considered to calculate the rationality of the conversion. The Japanese-to-English transliteration is completed by calculating the probability of the English unit candidate, and the target English context information is used to calculate the probability of Japanese-to-English conversion. 

---

新しい概念に対して、現代日本語では音訳を採用して、外国語から外来語を導入します。このリポジトリは、辞書にない新しい外来語を翻訳するため、日本語と英語の間の双方向自動音訳ツールを提供します。英日の部分では、英単語を単位に分割し、単位ごと日本語に翻訳して、そしてそれらを組み合わせます。異なる英単語で現れる同じアルファベットは通常異なる日本語に変換するため、英語と日本語の文脈情報を同時に考慮して、変換の正確度を計算する必要があります。日英部分では、アルファベット候補に対する確率計算が完了することにより、ターゲット英語の文脈情報を用いて日英変換の確率を計算する。
