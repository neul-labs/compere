"""
Configuration and environment validation module
"""

import logging
import os
import sys
from functools import lru_cache
from typing import Any

# Module-level cached config
_config: dict[str, Any] | None = None


def validate_environment() -> dict[str, Any]:
    """Validate environment variables and dependencies"""
    config = {}
    errors = []
    warnings = []

    # Database configuration
    database_url = os.getenv("DATABASE_URL", "sqlite:///./compere.db")
    config["database_url"] = database_url

    # Validate database URL format
    if not database_url.startswith(("sqlite://", "postgresql://", "mysql://")):
        errors.append(f"Invalid DATABASE_URL format: {database_url}")

    # ELO K-factor validation
    try:
        k_factor = float(os.getenv("ELO_K_FACTOR", "32.0"))
        if k_factor <= 0:
            errors.append("ELO_K_FACTOR must be positive")
        elif k_factor > 100:
            warnings.append(f"ELO_K_FACTOR ({k_factor}) is unusually high")
        config["elo_k_factor"] = k_factor
    except ValueError:
        errors.append("ELO_K_FACTOR must be a valid number")

    # Environment type
    env = os.getenv("ENVIRONMENT", "development")
    config["environment"] = env
    if env not in ["development", "staging", "production"]:
        warnings.append(f"Unknown ENVIRONMENT: {env}")

    # Log level
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    config["log_level"] = log_level
    if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        warnings.append(f"Invalid LOG_LEVEL: {log_level}, defaulting to INFO")
        config["log_level"] = "INFO"

    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 11):
        errors.append(f"Python 3.11+ required, found {python_version.major}.{python_version.minor}")

    # Check required dependencies
    try:
        from importlib.util import find_spec

        required_deps = ["fastapi", "sqlalchemy", "numpy", "sklearn"]
        missing = [dep for dep in required_deps if find_spec(dep) is None]
        if missing:
            errors.append(f"Missing required dependencies: {', '.join(missing)}")
            config["dependencies_ok"] = False
        else:
            config["dependencies_ok"] = True
    except Exception as e:
        errors.append(f"Error checking dependencies: {e}")
        config["dependencies_ok"] = False

    # Rate limiting configuration
    config["rate_limit_enabled"] = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
    config["rate_limit_requests"] = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    config["rate_limit_window"] = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    # Elo rating configuration
    config["elo_initial_rating"] = float(os.getenv("ELO_INITIAL_RATING", "1500.0"))

    # UCB/MAB configuration
    config["ucb_exploration_constant"] = float(os.getenv("UCB_EXPLORATION_CONSTANT", "1.414"))  # sqrt(2)
    config["ucb_unexplored_weight"] = float(os.getenv("UCB_UNEXPLORED_WEIGHT", "1000.0"))

    # Pairing weights (should sum to 1.0)
    config["pairing_ucb_weight"] = float(os.getenv("PAIRING_UCB_WEIGHT", "0.3"))
    config["pairing_similarity_weight"] = float(os.getenv("PAIRING_SIMILARITY_WEIGHT", "0.4"))
    config["pairing_random_weight"] = float(os.getenv("PAIRING_RANDOM_WEIGHT", "0.3"))

    # Rating similarity threshold for pairing bonus
    config["pairing_rating_threshold"] = float(os.getenv("PAIRING_RATING_THRESHOLD", "200.0"))

    # Recent comparison exclusion
    config["recent_comparison_limit"] = int(os.getenv("RECENT_COMPARISON_LIMIT", "5"))

    # Authentication configuration
    config["auth_enabled"] = os.getenv("AUTH_ENABLED", "false").lower() == "true"
    config["secret_key"] = os.getenv("SECRET_KEY")
    config["access_token_expire_minutes"] = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    if config["auth_enabled"] and not config["secret_key"]:
        errors.append("SECRET_KEY is required when AUTH_ENABLED=true")

    # CORS configuration
    cors_origins_str = os.getenv("CORS_ORIGINS", "")
    if cors_origins_str:
        config["cors_origins"] = [o.strip() for o in cors_origins_str.split(",") if o.strip()]
    elif env == "development":
        config["cors_origins"] = ["*"]
    else:
        # In production, CORS must be explicitly configured
        config["cors_origins"] = []

    # Logging middleware
    config["log_requests"] = os.getenv("LOG_REQUESTS", "true").lower() == "true"

    # Compile results
    config["validation_errors"] = errors
    config["validation_warnings"] = warnings
    config["validation_passed"] = len(errors) == 0

    return config


def setup_logging(config: dict[str, Any]) -> None:
    """Setup logging configuration"""
    log_level = getattr(logging, config.get("log_level", "INFO"))

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
        ],
    )

    # Add file handler for production
    if config.get("environment") == "production":
        file_handler = logging.FileHandler("compere.log")
        file_handler.setLevel(log_level)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)


@lru_cache(maxsize=1)
def get_config() -> dict[str, Any]:
    """Get validated configuration (cached singleton)"""
    global _config
    if _config is not None:
        return _config

    config = validate_environment()

    if not config["validation_passed"]:
        print("Environment validation failed:")
        for error in config["validation_errors"]:
            print(f"  ERROR: {error}")
        sys.exit(1)

    if config["validation_warnings"]:
        print("Environment warnings:")
        for warning in config["validation_warnings"]:
            print(f"  WARNING: {warning}")

    setup_logging(config)
    _config = config
    return config


# Type-safe accessor functions for centralized config access
def get_database_url() -> str:
    """Get database URL from configuration."""
    return get_config()["database_url"]


def get_elo_k_factor() -> float:
    """Get Elo K-factor from configuration."""
    return get_config()["elo_k_factor"]


def get_elo_initial_rating() -> float:
    """Get initial Elo rating from configuration."""
    return get_config()["elo_initial_rating"]


def get_secret_key() -> str | None:
    """Get JWT secret key from configuration."""
    return get_config().get("secret_key")


def is_auth_enabled() -> bool:
    """Check if authentication is enabled."""
    return get_config().get("auth_enabled", False)


def get_cors_origins() -> list[str]:
    """Get CORS allowed origins from configuration."""
    return get_config().get("cors_origins", [])


def get_environment() -> str:
    """Get environment type (development/staging/production)."""
    return get_config().get("environment", "development")


def is_development() -> bool:
    """Check if running in development mode."""
    return get_environment() == "development"


def get_rate_limit_config() -> tuple[bool, int, int]:
    """Get rate limit configuration (enabled, requests, window)."""
    config = get_config()
    return (
        config.get("rate_limit_enabled", False),
        config.get("rate_limit_requests", 100),
        config.get("rate_limit_window", 60),
    )


def is_log_requests_enabled() -> bool:
    """Check if request logging is enabled."""
    return get_config().get("log_requests", True)


def get_ucb_config() -> dict[str, float]:
    """Get UCB/MAB configuration values."""
    config = get_config()
    return {
        "exploration_constant": config.get("ucb_exploration_constant", 1.414),
        "unexplored_weight": config.get("ucb_unexplored_weight", 1000.0),
    }


def get_pairing_config() -> dict[str, float | int]:
    """Get entity pairing configuration values."""
    config = get_config()
    return {
        "ucb_weight": config.get("pairing_ucb_weight", 0.3),
        "similarity_weight": config.get("pairing_similarity_weight", 0.4),
        "random_weight": config.get("pairing_random_weight", 0.3),
        "rating_threshold": config.get("pairing_rating_threshold", 200.0),
        "recent_comparison_limit": config.get("recent_comparison_limit", 5),
    }


def get_access_token_expire_minutes() -> int:
    """Get access token expiration time in minutes."""
    return get_config().get("access_token_expire_minutes", 30)
