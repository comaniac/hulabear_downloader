# -*- coding: utf8 -*-
import re
import ConfigParser


class Formatter:
    def __init__(self):
        self._current_line = 0
        self._config = ConfigParser.ConfigParser()
        self._config.read("config.ini")
        self._page_splitter = self._config.get("data", "page_splitter")
        self._file_encode = self._config.get("data", "file_encode")

    def normalize(self, data):
        return self.reformat(self.decolor(data))

    def encoding(self, data):
        return (data.decode("Big5", "ignore").
                encode(self._file_encode, "ignore"))

    def decolor(self, data):
        data = re.sub(r"\[([0-9]*;*)*m|\[m", "", data)
        return data

    def reformat(self, data):
        self._current_line = 4
        data = data.replace("[;H\x1B[2J", "")  # article header

        # control code
        data = re.sub(r"(\n)*\x1B\[[0-9]*;1H(?P<content>.*)\x1B\[K", self._extract_content, data)
        data = re.sub(r"\x1B\[K", "", data)

        # mapping line number to new lines
        data = re.sub(r"\[(?P<line>[0-9]+);1H", self._line_no_to_breakers, data)
        data = re.sub(r"<<hulabear_page_splitter>>([\s\x1B])*", "<<hulabear_page_splitter>>\n", data)

        # page footer
        data = re.sub(r"\n[^\n]*<<hulabear_page_splitter>>", "\n  "+self._page_splitter, data)
        match = re.split(r"Origin:.*<hulabear.twbbs.org>", data) # split into article and comments
        if match and len(match) == 2:
            data = match[0] + u"Origin:  呼啦貝爾  <hulabear.twbbs.org>".encode("Big5") + \
                   re.sub(r"([\s|\x1B]*\n)", "\n", match[1])
        return data

    def parse_article_title(self, article):
        article = re.sub(r"\x1B", " ", article)

        # \xbc\xd0\xc3D = big5 encoding for title
        match = re.search(ur"\xbc\xd0\xc3D(?P<title>.*)\n", article)
        if match:
            return match.group("title").rstrip()
        else:
            return ""

    def escape_article_title(self, title):
        return self.encoding(re.sub(r"[\\/:\*\?\"<>\|]", "_", title))

    def _extract_content(self, match):
        if match:
            return match.group("content")

    def _line_no_to_breakers(self, match):
        if match:
            if int(match.group("line")) > self._current_line:  # still in the same page
                breaks = int(match.group("line")) - self._current_line
            else: # a new page
                breaks = int(match.group("line"))
            self._current_line = int(match.group("line"))
            return "\r\n"*breaks + "  "

