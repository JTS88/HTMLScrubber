import argparse

from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument('infile')

if __name__ == '__main__':
    args = parser.parse_args()

    with open(args.infile, 'r', encoding='utf-8') as fp:
        bsoup = BeautifulSoup(markup=fp, features='html.parser')

    just_text = bsoup.get_text()

    print(just_text)

    with open('bsoup.txt', 'w', encoding='utf-8') as of:
        of.write(just_text)
