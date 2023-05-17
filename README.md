# HTMLScrubber
An HTML scrubber that extracts the text content of the page and removes the HTML tags.
This scrubber is targeted at NLP usage by maintaining as much of the text formatting as possible.
You can always use regex to remove everything bettwen the tag charaters `<>` or BeautifulSoup which does a good job but doesn't handle some things well, like table data.

Some paragraph parsers look for two consecutive newlines to determine paragraph boundaries.  The HTMLScrubber will ensure that text marked with paragraph tags `<p></p>` Have empty lines above and below.
Table headings and data will also be laid out closer to what the browser would display.

## Usage
There are two static convenience functions, one to read an input string and one to read from a file.

`clean_str = HTMLScrubber.scrub(<HTML string>)`

`clean_str = HTMLScrubber.scrub_from_file(<filename>)`

If you plan to process a bunch of files, it's better to create an instance of the scrubber and call `get_text()` or `get_from_file()` instead.

### Constuction
There are a few options available to control the output.

`HTMLScrubber(pp_newlines=2, table_data_delimiter='\t', include_href=False, include_href_title=False)`

`pp_newlines` controls how many newline characters to insert before an after a paragraph.  The default is 2 newlines.

`table_data_delimiter` specifies what string to insert between table heading or table data columns.  The default is a tab.

`include_href` and `include_href_title` are used when an anchor (HTML link) is found.  Normally most HTML strippers would discard the link entirely (except for the display text).  If both are True (the default) an anchor like this:

`<a href="https://en.wikipedia.org/wiki/Category:Articles_with_Curlie_links" title="Category:Articles with Curlie links">Articles with Curlie links</a>`

will be output this:

`[anchor to https://en.wikipedia.org/wiki/Category:Articles_with_Curlie_links - Category:Articles with Curlie links]Articles with Curlie links`

if include_href is False, the output will look like this:

`[anchor to Category:Articles with Curlie links]Articles with Curlie links`

if both include_href and include_href_title are False, this is the output:

`Articles with Curlie links`
