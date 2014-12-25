#!/usr/bin/python
#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup


class ParseHtml():

    def parse(self, path):
        soup = BeautifulSoup(open(path))
        string_href = {}
        for a in soup.find_all("a"):
            print a.parent.parent.name

def test():
    html = ParseHtml()
    path = '/Users/jacsice/Desktop/bookmarks2.html'
    html.parse(path)

if __name__ == '__main__':
    test()
