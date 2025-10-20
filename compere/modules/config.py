"""
Configuration and environment validation module
"""
import os
import sys
import logging
from typing import Dict, Any

def validate_environment() -> Dict[str, Any]:
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
    if python_version < (3, 8):
        errors.append(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")

    # Check required dependencies
    try:
        import fastapi
        import sqlalchemy
        import numpy
        import sklearn
        config["dependencies_ok"] = True
    except ImportError as e:
        errors.append(f"Missing required dependency: {e}")
        config["dependencies_ok"] = False

    # Rate limiting configuration
    config["rate_limit_enabled"] = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
    config["rate_limit_requests"] = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    config["rate_limit_window"] = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    # Authentication configuration
    config["auth_enabled"] = os.getenv("AUTH_ENABLED", "false").lower() == "true"
    config["secret_key"] = os.getenv("SECRET_KEY")

    if config["auth_enabled"] and not config["secret_key"]:
        errors.append("SECRET_KEY is required when AUTH_ENABLED=true")

    # Compile results
    config["validation_errors"] = errors
    config["validation_warnings"] = warnings
    config["validation_passed"] = len(errors) == 0

    return config

def setup_logging(config: Dict[str, Any]) -> None:
    """Setup logging configuration"""
    log_level = getattr(logging, config.get("log_level", "INFO"))

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
        ]
    )

    # Add file handler for production
    if config.get("environment") == "production":
        file_handler = logging.FileHandler("compere.log")
        file_handler.setLevel(log_level)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)

def get_config() -> Dict[str, Any]:
    """Get validated configuration"""
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
    return config