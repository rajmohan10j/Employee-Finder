import unittest
import json
from pathlib import Path
from app import app, excel_mgr

class CandidateAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_01_stats_endpoint(self):
        res = self.app.get('/api/stats')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('total_candidates', data)
        self.assertGreaterEqual(data['total_candidates'], 0)
        print(f"Stats check passed: {data['total_candidates']} total candidates found.")

    def test_02_candidates_list(self):
        res = self.app.get('/api/candidates')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['candidates']), 0)
        print(f"Candidates list check passed: loaded {len(data['candidates'])} items.")

    def test_03_search_query(self):
        res = self.app.get('/api/candidates?query=test')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['candidates']), 0)
        print(f"Search query check passed: returned {len(data['candidates'])} results.")

    def test_04_reviewers_endpoint(self):
        res = self.app.get('/api/reviewers')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertGreater(len(data['reviewers']), 0)
        print(f"Reviewers check passed: {len(data['reviewers'])} reviewers found.")

    def test_05_network_info(self):
        res = self.app.get('/api/network_info')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIn('primary_url', data)
        print(f"Network info check passed: Primary URL is {data['primary_url']}.")

if __name__ == '__main__':
    unittest.main()
