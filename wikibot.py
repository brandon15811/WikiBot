#!/usr/bin/env python
# -*- coding: utf8 -*-
import time
import getopt

from collections import defaultdict

import requests
import feedparser
import json

_ignored_namespaces = ('User:', 'Talk:', 'User talk:')

def main(argv):
    try:
        opts, args = getopt.gnu_getopt(argv[1:], '', [
            'notifico=',
            'frequency=',
            'name=',
            'category='
        ])
    except getopt.GetoptError as e:
        print(str(e))
        return 1

    notifico = 'http://n.tkte.ch'
    # Try every 60 seconds
    frequency = 60
    name = 'wiki'
    for o, a in opts:
        if o == '--notifico':
            notifico = a.strip()
        elif o == '--frequency':
            frequency = int(a.strip())
        elif o == '--name':
            name = a.strip()
        elif o == '--category':
            category = a.strip()

    last_checked = defaultdict(int)
    first_run = True

    while True:
        for wiki in args:
            d = feedparser.parse(wiki)

            for entry in d.entries:
                # We don't care about certain namespaces.
                if entry.title.strip().startswith(_ignored_namespaces):
                    continue
                try:
                    pages = []

                    categoryjson = requests.get(wiki.split('index.php', 1)[0] +
                    "api.php?action=query&list=categorymembers&" +
                    "cmtitle=Category:" + category +
                    "&cmprop=title&format=json").json['query']['categorymembers']

                    for page in categoryjson:
                        pages.append(page['title'])

                    if not entry.title.strip() in pages:
                        continue
                except NameError:
                    pass

                # See if this change has occured since the last time
                # we checked this page.
                updated = time.mktime(entry.updated_parsed)
                if not first_run and updated > last_checked[wiki]:
                    line = []
                    line.append('[{0}]'.format(name))
                    line.append('Edit by {0} to {1} ->'.format(
                        entry.author,
                        entry.title
                    ))
                    line.append(requests.get(
                        'http://tinyurl.com/api-create.php?url={0}'.format(
                            entry.link
                    )).content)

                    requests.post(notifico, data={
                        'payload': ' '.join(line)
                    })

            last_checked[wiki] = max(
                time.mktime(e.updated_parsed) for e in d.entries
            )

        first_run = False
        time.sleep(frequency)


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
