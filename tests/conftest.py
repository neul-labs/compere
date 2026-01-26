"""
Pytest configuration and fixtures for all tests.
"""

import os
import sys

import pytest

# Add the compere package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment before any tests run."""
    # Import and initialize the app (creates database tables)
    from compere.main import app  # noqa: F401
    from compere.modules.database import Base, engine

    # Ensure tables are created
    Base.metadata.create_all(bind=engine)

    yield

    # Don't drop tables at end - let other tests run


def clear_config_cache():
    """Clear the config cache to allow fresh environment reads."""
    import compere.modules.config as config_module

    config_module.get_config.cache_clear()
    config_module._config = None


@pytest.fixture
def with_fresh_config():
    """Fixture for tests that need to test config with different env vars.

    Use this fixture to clear the config cache, run your test with patched
    environment variables, then restore the cache.
    """
    from compere.modules.database import Base, engine

    # Clear for fresh read
    clear_config_cache()

    yield

    # Restore by clearing cache and re-initializing
    clear_config_cache()

    # Re-create tables in case they were lost
    Base.metadata.create_all(bind=engine)
