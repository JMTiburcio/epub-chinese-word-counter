import jieba
from bs4 import BeautifulSoup
from ebooklib import epub
from collections import Counter
import re
import csv

def get_text_from_epub(file_path):
    book = epub.read_epub(file_path)
    text = ''
    for item in book.get_items():
        if isinstance(item, epub.EpubHtml):
            soup = BeautifulSoup(item.get_content().decode('utf-8'), 'html.parser')
            text += soup.get_text()
    return text

def load_cedict(cedict_path):
    with open(cedict_path, 'r', encoding='utf8') as f:
        lines = f.readlines()

    cedict = {}
    for i, line in enumerate(lines):
        if line[0] == '#' or line[0] == '%':  # Ignore comments and special lines
            continue
        parts = line.split(' ')
        trad, simp = parts[0], parts[1]
        pinyin = re.findall('\[(.*?)\]', line)[0]
        definitions = re.findall('/(.*?)/', line)[0] 
        if simp in cedict:
            cedict[simp].append((pinyin, definitions))
        else:
            cedict[simp] = [(pinyin, definitions)]
    return cedict

def translate_and_pinyin(cedict, word):
    if word in cedict:
        entries = cedict[word]
        pinyins = "; ".join([entry[0] for entry in entries])
        definitions = "; ".join([entry[1] for entry in entries])
        return pinyins, definitions
    else:
        print(f"Word not found in cedict: {word}")
        return "Not found", "Not found"

def process_text(text, cedict):
    words = Counter()
    text = re.sub(r'\W+', ' ', text)
    seg_list = jieba.cut(text, cut_all=False)

    for seg in seg_list:
        if re.search('[\u4e00-\u9fff]', seg):
            words[seg] += 1

    print("As 300 palavras mais comuns são: ")
    print([word for word, _ in words.most_common(300)])

    with open('word_count.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Word', 'Pinyin', 'Translation']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')


        writer.writeheader()
        for word, count in words.most_common(300):
            pinyin, translation = translate_and_pinyin(cedict, word)
            if pinyin and translation:
                writer.writerow({'Word': word, 'Pinyin': pinyin, 'Translation': translation})

def main():
    file_path = '/home/tiburcio/Downloads/(黄仁宇作品系列) 黄仁宇 - 中国大历史-三联书店 (2007).epub'
    cedict_path = '/home/tiburcio/Downloads/cedict_ts.u8'
    text = get_text_from_epub(file_path)
    cedict = load_cedict(cedict_path)
    process_text(text, cedict)

if __name__ == '__main__':
    main()
