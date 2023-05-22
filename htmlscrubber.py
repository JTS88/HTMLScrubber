import logging
import re
from html.parser import HTMLParser

logger = logging.getLogger(__name__)


class HTMLScrubber(HTMLParser):
    def __init__(self, pp_newlines=2, table_data_delimiter='\t', include_href=False, include_href_title=False):
        """
        Initialize the HTML scrubber and the HTML parser
        :param pp_newlines: The number of newline characters that surround a paragraph
        :param table_data_delimiter: The delimiter that will be inserted between table headings and table data
        :param include_href: Include the url (href=) for an anchor tag if True
        :param include_href_title: Include the title (title=) for an anchor tag if true
        """
        super().__init__()
        self.pp_newlines = pp_newlines
        self.table_data_delimiter = table_data_delimiter
        self.include_href = include_href
        self.include_href_title = include_href_title

        self.anchor_start = '[anchor to '
        self.anchor_end = ']'

        # the accumulated text data from parsing the page
        self.accumulated_text = []

        self.pre_nest = 0
        self.code_nest = 0

        # regex for the heading tags h1 - h6
        self.heading_regex = re.compile('h[1-6]')

        self.in_script = False
        self.in_style = False
        self.table_row_first_column = False

    def reset(self):
        super().reset()
        self.accumulated_text = []
        self.pre_nest = 0
        self.code_nest = 0

    def get_text(self, html_text: str) -> str:
        """
        Extract the text from the HTML string passed in
        :param html_text: The HTML string to parse
        :return: The extracted text
        """
        self.reset()
        self.feed(html_text)
        self.close()

        return ''.join(self.accumulated_text)

    def get_from_file(self, filename: str) -> str:
        """
        Read the HTML content from the passed in filename and extract the text
        :param filename: The name of the file containing the HTML text
        :return: The extracted text
        """
        try:
            with open(filename, 'r', encoding='utf-8') as fp:
                file_str = fp.read()
                return self.get_text(file_str)
        except Exception as e:
            logger.error(f'Error reading {filename}, error is {str(e)}')
            return None

    @staticmethod
    def scrub(html_text: str) -> str:
        """
        A convenience function that creates an HTMLScrubber instance and extracts the passed in text
        :param html_text: The HTML string to parse
        :return: The extracted text
        """
        hs = HTMLScrubber()
        return hs.get_text(html_text)

    @staticmethod
    def scrub_from_file(filename: str) -> str:
        """
        A convenience function that creates an HTMLScrubber instance and extracts the passed in text
        :param filename: The name of the file containing the HTML text
        :return: The extracted text
        """
        hs = HTMLScrubber()
        return hs.get_from_file(filename)

    def get_attr(self, attr_name, attr_list):
        """
        Find the named attribute in the list of attributes and return its value
        :param attr_name: The name of the attribute to find
        :param attr_list: The list of attributes to search.  Each attribute is a tuple of name and value.
        :return: The value for attr_name or an empty string if not found
        """
        for attr in attr_list:
            if attr[0] == attr_name:
                return attr[1]

        return ''

    def add_anchor(self, attrs):
        """
        Adds the anchor data including the href url and title if the user asked for them
        :param attrs:  The attributes for the anchor
        :return: None
        """
        if self.include_href:
            href_str = self.get_attr('href', attrs)
        else:
            href_str = ''

        if self.include_href_title:
            title_str = self.get_attr('title', attrs)
            if title_str:
                title_str = '{}{}'.format(' - ' if href_str else '', title_str)
        else:
            title_str = ''

        if href_str or title_str:
            self.accumulated_text.append(f'{self.anchor_start}{href_str}{title_str}{self.anchor_end}')

    def prev_newline(self):
        """
        Determines if the previous entry in the accumulated text ended with a newline
        :return: True if the previous line ended with a newline or False if it does not
        """
        if len(self.accumulated_text) > 0:
            return self.accumulated_text[-1].endswith('\n')
        else:
            # no accumulated text
            return False

    def handle_starttag(self, tag, attrs):
        """
        Callback used by HTMLParser for the start of an HTML tag
        :param tag: The HTML tag
        :param attrs: Attributes associated with the tag
        :return: None
        """
        logger.debug('Encountered a start tag:', tag)
        if tag == 'a':
            logger.info('Starting anchor')
            self.add_anchor(attrs)
        elif tag == 'br':
            self.accumulated_text.append('\n')
        elif tag == 'button':
            # buttons will have blank lines above and below
            self.accumulated_text.append('\n' * (1 if self.prev_newline() else 2))
        elif tag == 'code':
            self.code_nest += 1
        elif tag == 'ol' or tag == 'ul':
            # beginning of a list, start it on a new line
            if not self.prev_newline():
                self.accumulated_text.append('\n')
        elif tag == 'p' or self.heading_regex.match(tag):
            # start of paragraph or a heading, make sure there are enough newlines
            num_newlines = self.pp_newlines if not self.prev_newline() else self.pp_newlines - 1
            if num_newlines > 0:
                self.accumulated_text.append('\n' * num_newlines)
        elif tag == 'pre':
            self.pre_nest += 1
        elif tag == 'script':
            self.in_script = True
        elif tag == 'style':
            self.in_style = True
        elif tag == 'table':
            if not self.prev_newline():
                # start a table on a new line
                self.accumulated_text.append('\n')
        elif tag == 'tr':
            # starting a new row
            self.table_row_first_column = True
        elif tag == 'td' or tag == 'th':
            if self.table_row_first_column:
                self.table_row_first_column = False
            else:
                # insert a delimiter between table columns
                self.accumulated_text.append(self.table_data_delimiter)
        else:
            logger.info('Unhandled start tag: ', tag)

    def handle_endtag(self, tag):
        """
        Callback used by HTMLParser for the end of an HTML tag
        :param tag: The HTML tag
        :return: None
        """
        logger.debug('Encountered an end tag:', tag)
        if tag == 'br':
            # this is a tag like <br />, just ignore it
            pass
        elif tag == 'button':
            # buttons will have blank lines above and below
            self.accumulated_text.append('\n\n')
        elif tag == 'code':
            self.code_nest -= 1
        elif tag == 'li':
            logger.info('End of list item')
            self.accumulated_text.append('\n')
        elif tag == 'p' or self.heading_regex.match(tag):
            # end of a paragraph or heading, insert the specified number of newlines
            self.accumulated_text.append('\n' * self.pp_newlines)
        elif tag == 'pre':
            self.pre_nest -= 1
        elif tag == 'script':
            self.in_script = False
        elif tag == 'style':
            self.in_style = False
        elif tag == 'title':
            self.accumulated_text.append('\n')
        elif tag == 'tr':
            logger.info('End of table row')
            self.accumulated_text.append('\n')
        else:
            logger.info('Unhandled end tag: ', tag)

    def handle_data(self, data):
        """
        Callback used by the HTML parser for string data
        :param data: The string data
        :return: None
        """

        # skip empty data strings
        if data.isspace():
            return

        # skip over script or style blocks
        if not self.in_script and not self.in_style:
            if data == '&amp;' or data == '&#38;':
                self.accumulated_text.append('&')
            elif data == '&gt;' or data == '&#62;':
                self.accumulated_text.append('>')
            elif data == '&lt;' or data == '&#60;':
                self.accumulated_text.append('<')
            elif data == '&nbsp;' or data == '&#160;':
                self.accumulated_text.append(' ')
            else:
                logger.info('Encountered some data:', data)
                self.accumulated_text.append(data)

                # if we are in a <pre> section, add a newline
                if self.pre_nest > 0:
                    self.accumulated_text.append('\n')
        else:
            logger.info('Skipping script or style data:', data)
