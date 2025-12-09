"""
Tests for the CLI module.
"""

import os
import sys
from unittest.mock import patch

import pytest
from click.testing import CliRunner

# Add the compere package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from compere.cli import main


class TestCLI:
    """Test CLI commands"""

    def test_cli_help(self):
        """Test CLI help output"""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Compere CLI" in result.output
        assert "--host" in result.output
        assert "--port" in result.output
        assert "--reload" in result.output

    def test_cli_default_options(self):
        """Test CLI with default options"""
        runner = CliRunner()
        with patch("compere.cli.uvicorn.run") as mock_run:
            result = runner.invoke(main, [])
            assert result.exit_code == 0
            mock_run.assert_called_once_with("compere.main:app", host="127.0.0.1", port=8090, reload=False)

    def test_cli_custom_host(self):
        """Test CLI with custom host"""
        runner = CliRunner()
        with patch("compere.cli.uvicorn.run") as mock_run:
            result = runner.invoke(main, ["--host", "0.0.0.0"])
            assert result.exit_code == 0
            mock_run.assert_called_once_with("compere.main:app", host="0.0.0.0", port=8090, reload=False)

    def test_cli_custom_port(self):
        """Test CLI with custom port"""
        runner = CliRunner()
        with patch("compere.cli.uvicorn.run") as mock_run:
            result = runner.invoke(main, ["--port", "9000"])
            assert result.exit_code == 0
            mock_run.assert_called_once_with("compere.main:app", host="127.0.0.1", port=9000, reload=False)

    def test_cli_reload_flag(self):
        """Test CLI with reload flag"""
        runner = CliRunner()
        with patch("compere.cli.uvicorn.run") as mock_run:
            result = runner.invoke(main, ["--reload"])
            assert result.exit_code == 0
            mock_run.assert_called_once_with("compere.main:app", host="127.0.0.1", port=8090, reload=True)

    def test_cli_all_options(self):
        """Test CLI with all options"""
        runner = CliRunner()
        with patch("compere.cli.uvicorn.run") as mock_run:
            result = runner.invoke(main, ["--host", "0.0.0.0", "--port", "8000", "--reload"])
            assert result.exit_code == 0
            mock_run.assert_called_once_with("compere.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
