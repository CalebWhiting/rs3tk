"""Test __main__.py module."""

from __future__ import annotations

from unittest.mock import patch


def test_main_forwards_to_cli_main() -> None:
    """Test __main__.py forwards to cli.main()."""
    with patch("rs3tk.cli.main") as mock_main:
        import rs3tk.__main__ as main_module

        main_module.main()
        mock_main.assert_called_once()


class TestMainModule:
    """Test the __main__ module structure."""

    def test_main_module_imports(self) -> None:
        """Test __main__.py imports correctly."""
        from rs3tk.__main__ import main

        assert main is not None
        assert callable(main)

    def test_main_module_has_attributes(self) -> None:
        """Test __main__.py has expected attributes."""
        import rs3tk.__main__ as main_module

        assert hasattr(main_module, "__name__")
        assert main_module.__name__ == "rs3tk.__main__"
