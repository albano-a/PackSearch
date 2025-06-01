import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import PackageSearchExtension, run_search, _calculate_priority


class TestPackageSearchExtension(unittest.TestCase):
    
    def setUp(self):
        self.extension = PackageSearchExtension()
    
    @patch('main.shutil.which')
    def test_detect_backend_yay(self, mock_which):
        mock_which.side_effect = lambda cmd: cmd == "yay"
        backend = self.extension.detect_backend()
        self.assertEqual(backend, "yay")
    
    @patch('main.shutil.which')
    def test_detect_backend_pacman(self, mock_which):
        mock_which.side_effect = lambda cmd: cmd == "pacman"
        backend = self.extension.detect_backend()
        self.assertEqual(backend, "pacman")
    
    @patch('main.shutil.which')
    def test_detect_backend_none(self, mock_which):
        mock_which.return_value = None
        backend = self.extension.detect_backend()
        self.assertIsNone(backend)


class TestSearchFunctions(unittest.TestCase):
    
    def test_calculate_priority_exact_match(self):
        priority = _calculate_priority("neovim", "core", "neovim")
        self.assertEqual(priority, 1100)  # 1000 + 100 for official repo
    
    def test_calculate_priority_partial_match(self):
        priority = _calculate_priority("neovim-git", "aur", "neovim")
        self.assertEqual(priority, 750)  # 750 for starts with
    
    def test_calculate_priority_contains_match(self):
        priority = _calculate_priority("python-neovim", "extra", "neovim")
        self.assertEqual(priority, 600)  # 500 + 100 for official repo


if __name__ == '__main__':
    unittest.main()