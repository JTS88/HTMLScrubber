import argparse
import logging

from htmlscrubber import HTMLScrubber

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('infile')

if __name__ == '__main__':
    args = parser.parse_args()

    with open(args.infile, 'r', encoding='utf-8') as fp:
        html_str = fp.read()

    hs = HTMLScrubber(include_href=True, include_href_title=True)
    clean_str = hs.get_text(html_str)
    print(clean_str)

    with open('scrubber.txt', 'w', encoding='utf-8') as of:
        of.write(clean_str)
