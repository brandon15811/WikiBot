#!/usr/bin/env python
# -*- coding: utf8 -*-
import time
import getopt

from collections import defaultdict

import requests
import feedparser

_ignored_namespaces = ('User:', 'Talk:', 'User talk:')


def _clean_li(li):
    return ' '.join(li.text_content().encode('ascii', 'ignore').split())


def main(argv):
    try:
        opts, args = getopt.gnu_getopt(argv[1:], '', [
            'notifico=',
            'frequency=',
            'name='
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

    last_checked = defaultdict(int)

    while True:
        for wiki in args:
            d = feedparser.parse(wiki)
            time_last_checked = time.time()
            for entry in d.entries:
                # We don't care about certain namespaces.
                if entry.title.strip().startswith(_ignored_namespaces):
                    continue

                # See if this change has occured since the last time
                # we checked this page.
                updated = time.mktime(entry.updated_parsed)
                if last_checked[wiki] != 0 and updated > last_checked[wiki]:
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

            last_checked[wiki] = time_last_checked

        time.sleep(frequency)


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
