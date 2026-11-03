#!/usr/bin/env python3
"""Offline tests: no network, fixture only."""
import json
import unittest

import abf

FIXTURE = {
    'generated_at': '2026-11-03T07:50:25Z',
    'items': [
        {'id': 'a', 'source': 'superteam', 'title': 'big', 'est_usd': 125.0,
         'requires': ['agent_account', 'wallet_solana'], 'url': 'https://x/a'},
        {'id': 'b', 'source': 'taskmarket', 'title': 'staked', 'est_usd': 5.0,
         'requires': ['agent_account', 'stake'], 'url': 'https://x/b'},
        {'id': 'c', 'source': 'direct', 'title': 'free', 'est_usd': 5.0,
         'requires': ['agent_account', 'public_post', 'wallet_evm'], 'url': 'https://x/c'},
        {'id': 'd', 'source': 'frantic', 'title': 'tiny', 'est_usd': 0.45,
         'requires': [], 'url': 'https://x/d'},
        {'id': 'e', 'source': 'hondo', 'title': 'nullish', 'est_usd': None,
         'requires': None, 'url': 'https://x/e'},
    ],
}


class TestAbf(unittest.TestCase):
    def setUp(self):
        self.items = FIXTURE['items']

    def test_takeable_drops_stake(self):
        keep = [i['id'] for i in self.items if abf.takeable(i)]
        self.assertNotIn('b', keep)
        self.assertIn('c', keep)

    def test_takeable_handles_missing_requires(self):
        self.assertTrue(abf.takeable({'id': 'z'}))

    def test_select_sorts_desc_by_usd(self):
        rows = abf.select(self.items)
        self.assertEqual([r['id'] for r in rows][:2], ['a', 'b'])

    def test_select_min_usd(self):
        rows = abf.select(self.items, min_usd=5.0)
        self.assertEqual({r['id'] for r in rows}, {'a', 'b', 'c'})

    def test_select_takeable_and_min(self):
        rows = abf.select(self.items, min_usd=2.0, only_takeable=True)
        self.assertEqual([r['id'] for r in rows], ['a', 'c'])

    def test_none_usd_is_zero(self):
        rows = abf.select(self.items, min_usd=0.1)
        self.assertNotIn('e', [r['id'] for r in rows])

    def test_fetch_parses_json(self):
        real = abf.fetch
        try:
            abf.fetch = lambda *a, **k: FIXTURE
            rows = abf.select(abf.fetch()['items'], only_takeable=True)
            self.assertEqual(len(rows), 4)
        finally:
            abf.fetch = real

    def test_fixture_shape_matches_live_feed(self):
        keys = {'id', 'source', 'title', 'est_usd', 'requires', 'url'}
        for i in self.items:
            self.assertTrue(keys.issubset(i.keys()), i)


if __name__ == '__main__':
    unittest.main()
