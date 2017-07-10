# -*- coding: utf8 -*-
import re
import ConfigParser


class Formatter:
    def __init__(self):
        self._current_line = 0
        self._config = ConfigParser.ConfigParser()
        self._config.read("config.ini")
        self._page_splitter = self._config.get("data", "page_splitter")

    def normalize(self, data):
        return self.reformat(self.decolor(data))

    def decolor(self, data):
        data = re.sub(r"\[([0-9]*;*)*m|\[m", "", data)
        return data

    def reformat(self, data):
        self._current_line = 4
        data = data.replace("[;H\x1B[2J", "")  # article header
        data = re.sub(r"(\n)*\x1B\[[0-9]*;1H(?P<content>.*)\x1B\[K", self._extract_content, data)  # control code
        data = re.sub(r"\[(?P<line>[0-9]+);1H", self._line_no_to_breakers, data)  # mapping line number to new lines
        data = re.sub(r"\n[^\n]*<<hulabear_page_splitter>>", "\n  "+self._page_splitter+"\n", data)  # page footer
        match = re.split(r"Origin:.*<hulabear.twbbs.org>", data) # split into article and comments
        if match and len(match) == 2:
            data = match[0] + u"Origin:  呼啦貝爾  <hulabear.twbbs.org>".encode("Big5") + \
                   re.sub(r"([\s|\x1B]*\n)", "\n", match[1])
        return data

    def parse_article_title(self, article):
        article = re.sub(r"\x1B", " ", article)
        match = re.search(ur"\xbc\xd0\xc3D(?P<title>.*)\n", article) # \xbc\xd0\xc3D = big5 encoding for 標題
        return match.group("title").rstrip()

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