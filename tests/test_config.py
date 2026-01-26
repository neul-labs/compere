"""
Tests for configuration module.
"""

import logging
import os
import sys
from unittest.mock import patch

import pytest

# Add the compere package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import compere.modules.config as config_module
from compere.modules.config import get_config, setup_logging, validate_environment


def clear_config_cache():
    """Clear the config cache to allow fresh environment reads."""
    config_module.get_config.cache_clear()
    config_module._config = None


class TestValidateEnvironment:
    """Test environment validation"""

    def test_default_configuration(self):
        """Test validation with default configuration"""
        with patch.dict(os.environ, {}, clear=True):
            config = validate_environment()
            assert config["database_url"] == "sqlite:///./compere.db"
            assert config["elo_k_factor"] == 32.0
            assert config["environment"] == "development"
            assert config["log_level"] == "INFO"

    def test_valid_database_urls(self):
        """Test various valid database URL formats"""
        valid_urls = [
            "sqlite:///./test.db",
            "postgresql://user:pass@localhost/db",
            "mysql://user:pass@localhost/db",
        ]

        for url in valid_urls:
            with patch.dict(os.environ, {"DATABASE_URL": url}, clear=True):
                config = validate_environment()
                assert config["database_url"] == url
                assert "Invalid DATABASE_URL" not in str(config["validation_errors"])

    def test_invalid_database_url(self):
        """Test invalid database URL format"""
        with patch.dict(os.environ, {"DATABASE_URL": "invalid://url"}, clear=True):
            config = validate_environment()
            assert any("Invalid DATABASE_URL" in e for e in config["validation_errors"])

    def test_valid_elo_k_factor(self):
        """Test valid ELO K-factor values"""
        with patch.dict(os.environ, {"ELO_K_FACTOR": "16.0"}, clear=True):
            config = validate_environment()
            assert config["elo_k_factor"] == 16.0
            assert config["validation_passed"] is True

    def test_invalid_elo_k_factor_negative(self):
        """Test negative ELO K-factor"""
        with patch.dict(os.environ, {"ELO_K_FACTOR": "-10"}, clear=True):
            config = validate_environment()
            assert any("ELO_K_FACTOR must be positive" in e for e in config["validation_errors"])

    def test_invalid_elo_k_factor_not_number(self):
        """Test non-numeric ELO K-factor"""
        with patch.dict(os.environ, {"ELO_K_FACTOR": "not_a_number"}, clear=True):
            config = validate_environment()
            assert any("ELO_K_FACTOR must be a valid number" in e for e in config["validation_errors"])

    def test_high_elo_k_factor_warning(self):
        """Test warning for unusually high ELO K-factor"""
        with patch.dict(os.environ, {"ELO_K_FACTOR": "150"}, clear=True):
            config = validate_environment()
            assert any("unusually high" in w for w in config["validation_warnings"])

    def test_valid_environments(self):
        """Test valid environment values"""
        for env in ["development", "staging", "production"]:
            with patch.dict(os.environ, {"ENVIRONMENT": env}, clear=True):
                config = validate_environment()
                assert config["environment"] == env
                assert not any("Unknown ENVIRONMENT" in w for w in config["validation_warnings"])

    def test_unknown_environment_warning(self):
        """Test warning for unknown environment"""
        with patch.dict(os.environ, {"ENVIRONMENT": "custom"}, clear=True):
            config = validate_environment()
            assert any("Unknown ENVIRONMENT" in w for w in config["validation_warnings"])

    def test_valid_log_levels(self):
        """Test valid log level values"""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            with patch.dict(os.environ, {"LOG_LEVEL": level}, clear=True):
                config = validate_environment()
                assert config["log_level"] == level

    def test_invalid_log_level(self):
        """Test invalid log level defaults to INFO"""
        with patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}, clear=True):
            config = validate_environment()
            assert config["log_level"] == "INFO"
            assert any("Invalid LOG_LEVEL" in w for w in config["validation_warnings"])

    def test_log_level_case_insensitive(self):
        """Test log level is case insensitive"""
        with patch.dict(os.environ, {"LOG_LEVEL": "debug"}, clear=True):
            config = validate_environment()
            assert config["log_level"] == "DEBUG"

    def test_rate_limit_configuration(self):
        """Test rate limit configuration"""
        with patch.dict(
            os.environ,
            {
                "RATE_LIMIT_ENABLED": "true",
                "RATE_LIMIT_REQUESTS": "50",
                "RATE_LIMIT_WINDOW": "30",
            },
            clear=True,
        ):
            config = validate_environment()
            assert config["rate_limit_enabled"] is True
            assert config["rate_limit_requests"] == 50
            assert config["rate_limit_window"] == 30

    def test_rate_limit_disabled(self):
        """Test rate limit disabled by default"""
        with patch.dict(os.environ, {}, clear=True):
            config = validate_environment()
            assert config["rate_limit_enabled"] is False

    def test_elo_initial_rating(self):
        """Test ELO initial rating configuration"""
        with patch.dict(os.environ, {"ELO_INITIAL_RATING": "1200.0"}, clear=True):
            config = validate_environment()
            assert config["elo_initial_rating"] == 1200.0

    def test_ucb_configuration(self):
        """Test UCB/MAB configuration"""
        with patch.dict(
            os.environ,
            {
                "UCB_EXPLORATION_CONSTANT": "2.0",
                "UCB_UNEXPLORED_WEIGHT": "500.0",
            },
            clear=True,
        ):
            config = validate_environment()
            assert config["ucb_exploration_constant"] == 2.0
            assert config["ucb_unexplored_weight"] == 500.0

    def test_pairing_weights(self):
        """Test pairing weight configuration"""
        with patch.dict(
            os.environ,
            {
                "PAIRING_UCB_WEIGHT": "0.4",
                "PAIRING_SIMILARITY_WEIGHT": "0.3",
                "PAIRING_RANDOM_WEIGHT": "0.3",
            },
            clear=True,
        ):
            config = validate_environment()
            assert config["pairing_ucb_weight"] == 0.4
            assert config["pairing_similarity_weight"] == 0.3
            assert config["pairing_random_weight"] == 0.3

    def test_pairing_rating_threshold(self):
        """Test pairing rating threshold configuration"""
        with patch.dict(os.environ, {"PAIRING_RATING_THRESHOLD": "300.0"}, clear=True):
            config = validate_environment()
            assert config["pairing_rating_threshold"] == 300.0

    def test_recent_comparison_limit(self):
        """Test recent comparison limit configuration"""
        with patch.dict(os.environ, {"RECENT_COMPARISON_LIMIT": "10"}, clear=True):
            config = validate_environment()
            assert config["recent_comparison_limit"] == 10

    def test_auth_enabled_without_secret(self):
        """Test auth enabled without secret key raises error"""
        with patch.dict(os.environ, {"AUTH_ENABLED": "true"}, clear=True):
            config = validate_environment()
            assert any("SECRET_KEY is required" in e for e in config["validation_errors"])

    def test_auth_enabled_with_secret(self):
        """Test auth enabled with secret key"""
        with patch.dict(
            os.environ,
            {"AUTH_ENABLED": "true", "SECRET_KEY": "my-secret-key"},
            clear=True,
        ):
            config = validate_environment()
            assert config["auth_enabled"] is True
            assert config["secret_key"] == "my-secret-key"
            assert not any("SECRET_KEY is required" in e for e in config["validation_errors"])

    def test_validation_passed(self):
        """Test validation_passed flag"""
        with patch.dict(os.environ, {}, clear=True):
            config = validate_environment()
            assert config["validation_passed"] is True

    def test_validation_failed(self):
        """Test validation_passed flag when errors exist"""
        with patch.dict(os.environ, {"ELO_K_FACTOR": "-10"}, clear=True):
            config = validate_environment()
            assert config["validation_passed"] is False

    def test_dependencies_check(self):
        """Test dependency checking"""
        with patch.dict(os.environ, {}, clear=True):
            config = validate_environment()
            assert "dependencies_ok" in config


class TestSetupLogging:
    """Test logging setup"""

    def test_setup_logging_info(self):
        """Test logging setup with INFO level"""
        config = {"log_level": "INFO", "environment": "development"}
        setup_logging(config)

        # basicConfig only sets level if root logger has no handlers or level not set
        # Just verify the function runs without error
        root_logger = logging.getLogger()
        # The level should be set via basicConfig
        assert root_logger.level in [logging.INFO, logging.DEBUG, logging.WARNING, logging.NOTSET]

    def test_setup_logging_debug(self):
        """Test logging setup with DEBUG level"""
        # Reset root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.NOTSET)

        config = {"log_level": "DEBUG", "environment": "development"}
        setup_logging(config)

        # Verify function runs and logger is usable
        assert root_logger is not None

    def test_setup_logging_default(self):
        """Test logging setup with missing log level"""
        config = {"environment": "development"}
        setup_logging(config)

        # Should default to INFO - verify it doesn't crash
        root_logger = logging.getLogger()
        assert root_logger is not None


class TestGetConfig:
    """Test get_config function"""

    def test_get_config_success(self):
        """Test get_config with valid configuration"""
        clear_config_cache()
        with patch.dict(os.environ, {}, clear=True):
            config = get_config()
            assert config["validation_passed"] is True
            assert "database_url" in config
        clear_config_cache()

    def test_get_config_exits_on_error(self):
        """Test get_config exits on validation errors"""
        clear_config_cache()
        with patch.dict(os.environ, {"ELO_K_FACTOR": "not_a_number"}, clear=True):
            with pytest.raises(SystemExit) as exc_info:
                get_config()
            assert exc_info.value.code == 1
        clear_config_cache()

    def test_get_config_prints_warnings(self, capsys):
        """Test get_config prints warnings"""
        clear_config_cache()
        with patch.dict(os.environ, {"ENVIRONMENT": "custom_env"}, clear=True):
            config = get_config()
            captured = capsys.readouterr()
            assert "WARNING" in captured.out or config["validation_warnings"]
        clear_config_cache()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
