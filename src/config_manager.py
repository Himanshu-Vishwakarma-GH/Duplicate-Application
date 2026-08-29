"""
Configuration manager for Duplicate Application Manager.
Handles reading, saving, and validating config.json and rules.json.
"""

import json
import os
from typing import Any, Dict, Optional

DEFAULT_CONFIG_PATH = "config/default_config.json"
DEFAULT_RULES_PATH = "config/rules.json"

REQUIRED_CONFIG_FIELDS = [
    "version",
    "scan_directories",
    "excluded_directories",
    "file_extensions",
    "hash_algorithm",
    "large_file_threshold_mb",
    "database_path",
    "log_level",
    "theme",
]

REQUIRED_RULES_FIELDS = [
    "version",
    "categories",
]


class ConfigError(Exception):
    """Custom exception raised when configuration validation or IO fails."""
    pass


def get_default_config() -> Dict[str, Any]:
    """Return the default configuration dictionary."""
    return {
        "version": "1.0.0",
        "scan_directories": [
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            "D:\\Applications",
        ],
        "excluded_directories": [
            "node_modules",
            ".git",
            "__pycache__",
        ],
        "file_extensions": [
            ".exe", ".msi", ".app", ".dmg", ".deb", ".rpm"
        ],
        "hash_algorithm": "sha256",
        "large_file_threshold_mb": 100,
        "database_path": "data/app_manager.db",
        "log_level": "INFO",
        "theme": "dark",
    }


def validate_config(config_data: Dict[str, Any]) -> None:
    """Validate that all required configuration fields exist in config_data."""
    if not isinstance(config_data, dict):
        raise ConfigError("Configuration data must be a JSON object (dict).")
    
    missing_fields = [field for field in REQUIRED_CONFIG_FIELDS if field not in config_data]
    if missing_fields:
        raise ConfigError(f"Configuration is missing required fields: {', '.join(missing_fields)}")


def validate_rules(rules_data: Dict[str, Any]) -> None:
    """Validate that all required rules fields exist in rules_data."""
    if not isinstance(rules_data, dict):
        raise ConfigError("Rules data must be a JSON object (dict).")

    missing_fields = [field for field in REQUIRED_RULES_FIELDS if field not in rules_data]
    if missing_fields:
        raise ConfigError(f"Rules configuration is missing required fields: {', '.join(missing_fields)}")


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    If path is None or file does not exist, attempts DEFAULT_CONFIG_PATH or returns default config.
    Validates required fields before returning.
    """
    target_path = config_path or DEFAULT_CONFIG_PATH
    if not os.path.exists(target_path):
        # Fall back to default config if file is missing
        config = get_default_config()
        validate_config(config)
        return config

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        raise ConfigError(f"Failed to read config from {target_path}: {e}") from e

    validate_config(config)
    return config


def save_config(config_data: Dict[str, Any], config_path: Optional[str] = None) -> None:
    """Validate and save configuration dictionary to JSON file."""
    validate_config(config_data)
    target_path = config_path or DEFAULT_CONFIG_PATH

    parent_dir = os.path.dirname(target_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    try:
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
    except Exception as e:
        raise ConfigError(f"Failed to save config to {target_path}: {e}") from e


def load_rules(rules_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load rules from JSON file.
    Validates required fields before returning.
    """
    target_path = rules_path or DEFAULT_RULES_PATH
    if not os.path.exists(target_path):
        raise ConfigError(f"Rules file not found at {target_path}")

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            rules = json.load(f)
    except Exception as e:
        raise ConfigError(f"Failed to read rules from {target_path}: {e}") from e

    validate_rules(rules)
    return rules


def save_rules(rules_data: Dict[str, Any], rules_path: Optional[str] = None) -> None:
    """Validate and save rules dictionary to JSON file."""
    validate_rules(rules_data)
    target_path = rules_path or DEFAULT_RULES_PATH

    parent_dir = os.path.dirname(target_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    try:
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(rules_data, f, indent=2)
    except Exception as e:
        raise ConfigError(f"Failed to save rules to {target_path}: {e}") from e


class ConfigManager:
    """Class wrapper for managing application configurations and rules."""

    def __init__(self, config_path: Optional[str] = None, rules_path: Optional[str] = None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.rules_path = rules_path or DEFAULT_RULES_PATH
        self.config = load_config(self.config_path)
        self.rules = load_rules(self.rules_path) if os.path.exists(self.rules_path) else {"version": "1.0.0", "categories": []}

    def reload(self) -> None:
        """Reload configuration and rules from files."""
        self.config = load_config(self.config_path)
        if os.path.exists(self.rules_path):
            self.rules = load_rules(self.rules_path)

    def save(self) -> None:
        """Save current configuration and rules to files."""
        save_config(self.config, self.config_path)
        save_rules(self.rules, self.rules_path)
