import unittest
import asyncio
import os
import json
import shutil
from unittest.mock import MagicMock, patch

# Import modules to test
# Note: We might need to adjust imports if bot_main has global execution code
import killfeed
import security

# Mocking bot_main dependencies before importing it
# This is tricky because bot_main might run code on import.
# We will test independent modules first.

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.rate_limiter = security.RateLimiter(max_calls=2, period=1)

    def test_rate_limiter(self):
        user_id = 123
        self.assertTrue(self.rate_limiter.is_allowed(user_id))
        self.assertTrue(self.rate_limiter.is_allowed(user_id))
        self.assertFalse(self.rate_limiter.is_allowed(user_id))
        
    def test_backup_manager(self):
        bm = security.BackupManager(backup_dir="test_backups")
        # Create a dummy file
        with open("test_file.txt", "w") as f:
            f.write("test")
        
        self.assertTrue(bm.backup_file("test_file.txt"))
        self.assertTrue(os.path.exists("test_backups"))
        
        # Cleanup
        if os.path.exists("test_file.txt"): os.remove("test_file.txt")
        if os.path.exists("test_backups"): shutil.rmtree("test_backups")

class TestKillfeed(unittest.TestCase):
    def test_parse_log_line_kill(self):
        line = '2025-11-24 12:00:00 INFO Player "Killer" (123) killed by Player "Victim" (456) with M4A1 <100,0,100>'
        
        # We need to mock the DB functions to avoid writing to real DB
        killfeed.load_db = MagicMock(return_value={})
        killfeed.save_db = MagicMock()
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        embed = loop.run_until_complete(killfeed.parse_log_line(line))
        
        self.assertIsNotNone(embed)
        self.assertEqual(embed.color.value, 15105570) # Orange
        description = embed.description
        self.assertIn("Killer", description)
        self.assertIn("Victim", description)
        self.assertIn("M4A1", description)
        loop.close()

    def test_parse_log_line_death(self):
        line = '2025-11-24 12:00:00 INFO Player "Victim" (456) died'
        
        killfeed.load_db = MagicMock(return_value={})
        killfeed.save_db = MagicMock()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        embed = loop.run_until_complete(killfeed.parse_log_line(line))
        
        self.assertIsNotNone(embed)
        self.assertEqual(embed.color.value, 15158332) # Red
        self.assertIn("Victim", embed.description)
        loop.close()

if __name__ == '__main__':
    unittest.main()
