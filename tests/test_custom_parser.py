import unittest
from typing import Callable
import sys
import os

# Add the project root to sys.path to ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from zenif.cli.applets.parser import parse
from zenif.cli.applets.parameters import Parameter
from zenif.cli.applets.exceptions import AppletError


class TestCustomParser(unittest.TestCase):
    def setUp(self):
        # Create mock functions with parameters
        self.cmd_with_params = self._create_mock_function()
        self.cmd_with_aliases = self._create_mock_function_with_aliases()
        self.root_function = self._create_mock_root_function()

    def _create_mock_function(self) -> Callable:
        """Create a mock function with positional args, options and flags"""

        def mock_func(path, depth=None, quiet=False, mode=None):
            return {"path": path, "depth": depth, "quiet": quiet, "mode": mode}

        mock_func.__name__ = "mock_func"
        mock_func.__doc__ = "A mock function for testing"
        mock_func._cli_params = {
            "path": Parameter(
                param_name="path", kind="argument", help="Path to search"
            ),
            "depth": Parameter(
                param_name="depth", kind="option", help="Search depth", default=1
            ),
            "quiet": Parameter(
                param_name="quiet", kind="flag", help="Be quiet", default=False
            ),
            "mode": Parameter(
                param_name="mode", kind="option", help="Search mode", default="normal"
            ),
        }
        mock_func._aliases = []
        return mock_func

    def _create_mock_function_with_aliases(self) -> Callable:
        """Create a mock function with aliases for options and flags"""

        def mock_func_aliases(target, verbose=False, format=None):
            return {"target": target, "verbose": verbose, "format": format}

        mock_func_aliases.__name__ = "mock_func_aliases"
        mock_func_aliases.__doc__ = "A mock function with aliases"
        mock_func_aliases._cli_params = {
            "target": Parameter(
                param_name="target", kind="argument", help="Target path"
            ),
            "verbose": Parameter(
                param_name="verbose", kind="flag", help="Be verbose", default=False
            ),
            "format": Parameter(
                param_name="format", kind="option", help="Output format", default="text"
            ),
        }
        mock_func_aliases._cli_aliases = {"verbose": "v", "format": "f"}
        mock_func_aliases._aliases = []
        return mock_func_aliases

    def _create_mock_root_function(self) -> Callable:
        """Create a mock root function"""

        def root_func(branch=None, all=False):
            return {"branch": branch, "all": all}

        root_func.__name__ = "root_func"
        root_func.__doc__ = "A mock root function"
        root_func._cli_params = {
            "branch": Parameter(
                param_name="branch", kind="option", help="Branch name", default="main"
            ),
            "all": Parameter(
                param_name="all", kind="flag", help="Show all branches", default=False
            ),
        }
        root_func._primary_name = "root_func"
        root_func._aliases = []
        return root_func

    def test_positional_arguments(self):
        """Test parsing of positional arguments"""
        args = ["/path/to/dir"]
        result = parse(self.cmd_with_params, args)
        self.assertEqual(result["path"], "/path/to/dir")
        self.assertEqual(result["depth"], 1)  # Default value
        self.assertFalse(result["quiet"])  # Default value

    def test_options_standard_format(self):
        """Test parsing options in --option value format"""
        args = ["/path/to/dir", "--depth", "5", "--mode", "advanced"]
        result = parse(self.cmd_with_params, args)
        self.assertEqual(result["path"], "/path/to/dir")
        self.assertEqual(result["depth"], "5")
        self.assertEqual(result["mode"], "advanced")

    def test_options_equal_format(self):
        """Test parsing options in --option=value format"""
        args = ["/path/to/dir", "--depth=5", "--mode=advanced"]
        result = parse(self.cmd_with_params, args)
        self.assertEqual(result["path"], "/path/to/dir")
        self.assertEqual(result["depth"], "5")
        self.assertEqual(result["mode"], "advanced")

    def test_short_options(self):
        """Test parsing short options based on first letter"""
        args = ["/path/to/dir", "-d", "5", "-m", "advanced"]
        result = parse(self.cmd_with_params, args)
        self.assertEqual(result["depth"], "5")
        self.assertEqual(result["mode"], "advanced")

    def test_short_options_equal_format(self):
        """Test parsing short options in -o=value format"""
        args = ["/path/to/dir", "-d=5", "-m=advanced"]
        result = parse(self.cmd_with_params, args)
        self.assertEqual(result["depth"], "5")
        self.assertEqual(result["mode"], "advanced")

    def test_short_options_joined_numeric(self):
        """Test parsing short options in -o10 format (for numeric values)"""
        args = ["/path/to/dir", "-d5"]
        result = parse(self.cmd_with_params, args)
        self.assertEqual(result["depth"], "5")

    def test_flags(self):
        """Test parsing boolean flags"""
        args = ["/path/to/dir", "--quiet"]
        result = parse(self.cmd_with_params, args)
        self.assertTrue(result["quiet"])

    def test_short_flags(self):
        """Test parsing short boolean flags"""
        args = ["/path/to/dir", "-q"]
        result = parse(self.cmd_with_params, args)
        self.assertTrue(result["quiet"])

    def test_aliases(self):
        """Test parsing options and flags with aliases"""
        args = ["/path/to/file", "-v", "-f", "json"]
        result = parse(self.cmd_with_aliases, args)
        self.assertEqual(result["target"], "/path/to/file")
        self.assertTrue(result["verbose"])
        self.assertEqual(result["format"], "json")

    def test_mixed_args(self):
        """Test parsing a mix of different argument types"""
        args = ["/path/to/dir", "-q", "--depth=5", "-m", "advanced"]
        result = parse(self.cmd_with_params, args)
        self.assertEqual(result["path"], "/path/to/dir")
        self.assertEqual(result["depth"], "5")
        self.assertTrue(result["quiet"])
        self.assertEqual(result["mode"], "advanced")

    def test_root_command(self):
        """Test parsing arguments for a root command"""
        args = ["--branch", "develop", "--all"]
        result = parse(self.root_function, args)
        self.assertEqual(result["branch"], "develop")
        self.assertTrue(result["all"])

    def test_missing_required_argument(self):
        """Test that an error is raised when a required argument is missing"""
        args = []
        with self.assertRaises(AppletError):
            parse(self.cmd_with_params, args)

    def test_unknown_option(self):
        """Test that an error is raised for unknown options"""
        args = ["/path/to/dir", "--unknown", "value"]
        with self.assertRaises(AppletError):
            parse(self.cmd_with_params, args)


if __name__ == "__main__":
    unittest.main()
