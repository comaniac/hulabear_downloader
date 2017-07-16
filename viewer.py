# -*- coding: utf8 -*-
from os import listdir, system
from os.path import isfile, basename, splitext
from getch import getch
import re
import sys
import argparse

arg_parser = argparse.ArgumentParser(description='download_folder')
arg_parser.add_argument('-b', help='the board folder with raw_data articles')
args = arg_parser.parse_args()

def show_article_list(data, start, end, cursor):
    system('clear')
    for i in xrange(start, end):
        if i - start == cursor:
            sys.stdout.write('> ')
        else:
            sys.stdout.write('  ')
        sys.stdout.write(str(i) + '\t' + data[i] + '\n')
    sys.stdout.write(str(end - 1) + ' / ' + str(len(data) - 1) + '\n')

def show_article(data, index):
    system('clear')
    file_name = args.b + str(index) + '   ' + data[index] + '.txt'
    f = open(file_name, 'r')
    article = f.read()

    # identify pages
    pages = [0]
    for i in  re.finditer("<<hulabear_page_splitter>>", article):
        pages.append(i.start())

    curr_page = 0
    while True:
        page_start = pages[curr_page]
        page_end = pages[curr_page + 1]
        sys.stdout.write(article[page_start:page_end] + '\n')
        sys.stdout.flush()
        cmd = get_user_command("(n)ext page, (p)revious page, b(a)ck: ")
        if cmd == 'n':
            if curr_page != len(pages): # not end of article
                curr_page += 1
        elif cmd == 'p':
            if curr_page > 0:
                curr_page -= 1
        elif cmd == 'a':
            return

def get_user_command(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()
    cmd = getch()
    sys.stdout.write('\n')
    return cmd

# get articles
articles = [f for f in listdir(args.b) if f.find('.txt') != -1]

# build article list
num_article = len(articles)
article_list = []
for i in xrange(num_article + 1):
    article_list.append('')

for a in articles:
    idx_and_title = re.search("(\d+)   (.*)", splitext(a)[0])
    if idx_and_title == None:
        continue
    idx = idx_and_title.group(1)
    title = idx_and_title.group(2)
    article_list[int(idx)] = title

# display
cursor = 0
curr_start = 1
article_per_page = 10
last_cmd = ''
while True:
    curr_end = min(curr_start + article_per_page, num_article)
    show_article_list(article_list, curr_start, curr_end, cursor)
    cmd = get_user_command('(n)ext page, (p)revious page (q)uit: ')

    # stage 1: quit cheking
    if cmd == 'q':
        break

    # stage 2: open article
    if cmd == 'd':
        show_article(article_list, curr_start + cursor)

    # stage 2: move cursor
    if cmd == 'w':
        if cursor > 0:
            cursor -= 1
        else:
            cmd = 'p'
            cursor = article_per_page - 1
    elif cmd == 's':
        if cursor < article_per_page - 1:
            cursor += 1
        else:
            cmd = 'n'
            cursor = 0

    # stage 3: change page
    if cmd == 'n' and curr_end != num_article:
        curr_start += article_per_page
    elif cmd == 'p' and curr_start > 0:
        curr_start = max(curr_start - article_per_page, 1)

