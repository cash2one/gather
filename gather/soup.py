#!/usr/bin/python
#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup


class ParseHtml():

    def parse(self, path):
        soup = BeautifulSoup(path)
        href_title = {}
        for a in soup.find_all("a"):
            href_title[a['href']] = a.string

        return href_title


def test():
    html = ParseHtml()
    path = '/Users/jacsice/Desktop/bookmarks2.html'
    html.parse(path)

if __name__ == '__main__':
    test()
