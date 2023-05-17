# HTMLScrubber
An HTML scrubber that extracts the text content of the page and removes the HTML tags.
This scrubber is targeted at NLP usage by maintaining as much of the text formatting as possible.
You can always use regex to remove everything bettwen the tag charaters `<>` or BeautifulSoup which does a good job but doesn't handle some things well, like table data.

Some paragraph parsers look for two consecutive newlines to determine paragraph boundaries.  The HTMLScrubber will ensure that text marked with paragraph tags `<p></p>` Have empty lines above and below.
Table headings and data will also be laid out closer to what the browser would display.
