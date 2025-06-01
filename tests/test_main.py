import unittest
from unittest.mock import patch, MagicMock, Mock
import sys
import os

# Mock Ulauncher modules before importing main
ulauncher_mocks = {
    "ulauncher": MagicMock(),
    "ulauncher.api": MagicMock(),
    "ulauncher.api.client": MagicMock(),
    "ulauncher.api.client.EventListener": MagicMock(),
    "ulauncher.api.client.Extension": MagicMock(),
    "ulauncher.api.shared": MagicMock(),
    "ulauncher.api.shared.action": MagicMock(),
    "ulauncher.api.shared.action.ExtensionCustomAction": MagicMock(),
    "ulauncher.api.shared.item": MagicMock(),
    "ulauncher.api.shared.item.ExtensionResultItem": MagicMock(),
    "ulauncher.api.shared.action.RenderResultListAction": MagicMock(),
    "ulauncher.api.shared.action.CopyToClipboardAction": MagicMock(),
    "ulauncher.api.shared.event": MagicMock(),
    "ulauncher.api.shared.action.RunScriptAction": MagicMock(),
}

for module_name, mock_module in ulauncher_mocks.items():
    sys.modules[module_name] = mock_module

# Add the parent directory to path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import (
    run_search,
    _calculate_priority,
    _parse_pacman_output,
    _parse_pamac_output,
)


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

    def test_calculate_priority_no_match(self):
        priority = _calculate_priority("firefox", "extra", "neovim")
        self.assertEqual(priority, 100)  # Just official repo bonus

    def test_calculate_priority_aur_exact_match(self):
        priority = _calculate_priority("neovim", "aur", "neovim")
        self.assertEqual(priority, 1000)  # 1000, no official repo bonus

    @patch("main.subprocess.run")
    def test_parse_pacman_output_success(self, mock_run):
        # Mock successful pacman output
        mock_proc = Mock()
        mock_proc.stdout = "core/neovim 0.8.0-1\n    Vim-based text editor\nextra/vim 9.0.0-1\n    Vi Improved"
        mock_run.return_value = mock_proc

        results = _parse_pacman_output(["pacman", "-Ss", "vim"], "vim")

        self.assertGreater(len(results), 0)
        # Check that results contain tuples with (priority, name, repo, desc)
        for result in results:
            self.assertEqual(len(result), 4)
            self.assertIsInstance(result[0], int)  # priority
            self.assertIsInstance(result[1], str)  # name
            self.assertIsInstance(result[2], str)  # repo
            self.assertIsInstance(result[3], str)  # description

    @patch("main.subprocess.run")
    def test_parse_pacman_output_failure(self, mock_run):
        # Mock subprocess failure
        mock_run.side_effect = Exception("Command failed")

        results = _parse_pacman_output(["pacman", "-Ss", "nonexistent"], "nonexistent")

        self.assertEqual(results, [])

    @patch("main.subprocess.run")
    def test_parse_pamac_output_success(self, mock_run):
        # Mock successful pamac output
        mock_proc = Mock()
        mock_proc.stdout = "neovim 0.8.0-1 (extra)\nvim 9.0.0-1 (extra)"
        mock_run.return_value = mock_proc

        results = _parse_pamac_output(["pamac", "search", "vim"], "vim")

        # Should return list of tuples
        self.assertIsInstance(results, list)

    @patch("main._parse_pacman_output")
    def test_run_search_pacman(self, mock_parse):
        mock_parse.return_value = [(1000, "neovim", "core", "Text editor")]

        results = run_search("pacman", "neovim")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], ("neovim", "core", "Text editor"))
        mock_parse.assert_called_once_with(["pacman", "-Ss", "neovim"], "neovim")

    @patch("main._parse_pamac_output")
    def test_run_search_pamac(self, mock_parse):
        mock_parse.return_value = [(1000, "neovim", "extra", "Text editor")]

        results = run_search("pamac", "neovim")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], ("neovim", "extra", "Text editor"))

    @patch("main._parse_pacman_output")
    def test_run_search_yay_with_aur_fallback(self, mock_parse):
        # First call returns few results, second call returns AUR results
        mock_parse.side_effect = [
            [(1000, "neovim", "core", "Text editor")],  # Official repos
            [(500, "neovim-git", "aur", "Development version")],  # AUR
        ]

        results = run_search("yay", "neovim")

        self.assertEqual(len(results), 2)
        # Should be called twice - once for --repo, once for --aur
        self.assertEqual(mock_parse.call_count, 2)

    def test_run_search_unsupported_backend(self):
        with self.assertRaises(ValueError):
            run_search("unsupported", "test")


class TestUtilityFunctions(unittest.TestCase):
    def test_priority_calculation_edge_cases(self):
        # Test case sensitivity
        priority1 = _calculate_priority("NEOVIM", "core", "neovim")
        priority2 = _calculate_priority("neovim", "core", "NEOVIM")
        self.assertEqual(priority1, priority2)

        # Test empty strings
        priority = _calculate_priority("", "core", "test")
        self.assertEqual(priority, 100)  # Just repo bonus

        # Test special characters
        priority = _calculate_priority("vim-plug", "aur", "vim")
        self.assertGreater(priority, 0)


if __name__ == "__main__":
    unittest.main()
