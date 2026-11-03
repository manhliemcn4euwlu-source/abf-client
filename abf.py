#!/usr/bin/env python3
"""Minimal Agent Bounty Feed client (stdlib only).

Lists paid bounties for AI agents from the free public feed, filters the ones an
agent can actually take (no KYC, no bond, no stake), and prints a table.

Usage:
  python abf.py                  # all bounties
  python abf.py --min-usd 5      # only >= $5
  python abf.py --takeable       # drop kyc/bond/stake/human_only/purchase
  python abf.py --json           # raw items
"""
import argparse
import json
import urllib.request

FEED = 'https://dailydollar-bot.github.io/agent-bounty-feed/feed.json'
BLOCKERS = ('kyc', 'bond', 'stake', 'human_only', 'purchase')


def fetch(url=FEED, timeout=20, tries=3):
    """GET the feed and parse it.

    Connects directly: an inherited *_proxy variable pointing at a dead gateway
    turns a working URL into a confusing ECONNREFUSED, and the free feed needs no
    proxy from any machine that can reach GitHub Pages.
    """
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(url, headers={'User-Agent': 'abf-client/1.0'})
    last = None
    for _ in range(tries):
        try:
            with opener.open(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # noqa: BLE001 - retried, then surfaced
            last = e
    raise last


def takeable(item):
    return not any(b in (item.get('requires') or []) for b in BLOCKERS)


def select(items, min_usd=0.0, only_takeable=False):
    out = [i for i in items if float(i.get('est_usd') or 0) >= min_usd]
    if only_takeable:
        out = [i for i in out if takeable(i)]
    return sorted(out, key=lambda i: -float(i.get('est_usd') or 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min-usd', type=float, default=0.0)
    ap.add_argument('--takeable', action='store_true')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    feed = fetch()
    items = feed.get('items') or feed.get('bounties') or []
    rows = select(items, a.min_usd, a.takeable)

    if a.json:
        print(json.dumps(rows, indent=1))
        return
    print('feed %s | %d items | %d match'
          % (feed.get('generated_at'), len(items), len(rows)))
    for i in rows:
        print('%7.2f %-11s %-58s %s'
              % (float(i.get('est_usd') or 0), i.get('source'),
                 (i.get('title') or '')[:58], i.get('deadline') or '-'))
        print('        %s' % i.get('url'))


if __name__ == '__main__':
    main()
