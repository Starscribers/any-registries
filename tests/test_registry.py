from __future__ import annotations

import os
from typing import Callable

import pytest
from typing_extensions import Self

from any_registries import Registry
from any_registries.exceptions import ItemNotRegistered


@pytest.fixture
def registry() -> Registry:
    """Create a fresh registry for each test."""
    return Registry()


@pytest.fixture
def env_cleanup() -> None:
    """Store and restore environment variables."""
    original_project_root = os.environ.get("PROJECT_ROOT")
    original_base_dir = os.environ.get("BASE_DIR")

    yield

    # Restore original environment variables
    if original_project_root is not None:
        os.environ["PROJECT_ROOT"] = original_project_root
    elif "PROJECT_ROOT" in os.environ:
        del os.environ["PROJECT_ROOT"]

    if original_base_dir is not None:
        os.environ["BASE_DIR"] = original_base_dir
    elif "BASE_DIR" in os.environ:
        del os.environ["BASE_DIR"]


def test_register_and_get_simple(registry: Registry) -> None:
    """Test basic registration and retrieval."""

    @registry.register("test_key")
    def test_function() -> str:
        return "test_value"

    retrieved_function = registry.get("test_key")
    assert retrieved_function() == "test_value"


def test_key_getter_function() -> None:
    """Test registration using key getter function."""

    def name_key_getter(func: Callable) -> str:
        return func.__name__

    registry_with_key_getter: Registry[str, Callable] = Registry(key=name_key_getter)

    @registry_with_key_getter.register()
    def named_function() -> str:
        return "named_value"

    retrieved_function = registry_with_key_getter.get("named_function")
    assert retrieved_function() == "named_value"


def test_item_not_registered_exception(registry: Registry) -> None:
    """Test that ItemNotRegistered is raised for unknown keys."""
    with pytest.raises(
        ItemNotRegistered, match="Item with key 'nonexistent_key' is not registered"
    ):
        registry.get("nonexistent_key")


def test_registry_property(registry: Registry) -> None:
    """Test the registry property returns the internal dictionary."""

    @registry.register("prop_test")
    def prop_function() -> str:
        return "prop_value"

    registry_dict = registry.registry
    assert "prop_test" in registry_dict
    assert registry_dict["prop_test"]() == "prop_value"


def test_class_registration(registry: Registry) -> None:
    """Test registering classes instead of functions."""

    @registry.register("test_class")
    class TestClass:
        def method(self: Self) -> str:
            return "class_method_value"

    retrieved_class = registry.get("test_class")
    instance = retrieved_class()
    assert instance.method() == "class_method_value"


def test_chaining_auto_load() -> None:
    """Test that auto_load method returns self for chaining."""
    registry: Registry[str, type] = Registry()
    result = registry.auto_load("pattern1", "pattern2")
    assert result is registry
    assert registry.auto_loads == ["pattern1", "pattern2"]


def test_project_root_environment_variable(env_cleanup: None) -> None:
    """Test that PROJECT_ROOT environment variable is used."""
    os.environ["PROJECT_ROOT"] = "/test/project/root"
    registry: Registry[str, type] = Registry()
    assert registry.base_path == "/test/project/root"


def test_base_dir_environment_variable(env_cleanup: None) -> None:
    """Test that BASE_DIR environment variable is used when PROJECT_ROOT is not set."""
    if "PROJECT_ROOT" in os.environ:
        del os.environ["PROJECT_ROOT"]
    os.environ["BASE_DIR"] = "/test/base/dir"
    registry: Registry[str, type] = Registry()
    assert registry.base_path == "/test/base/dir"


def test_explicit_base_path_overrides_environment(env_cleanup: None) -> None:
    """Test that explicit base_path parameter overrides environment variables."""
    os.environ["PROJECT_ROOT"] = "/test/project/root"
    os.environ["BASE_DIR"] = "/test/base/dir"
    registry: Registry[str, type] = Registry(base_path="/explicit/path")
    assert registry.base_path == "/explicit/path"


def test_registry_empty_initialization() -> None:
    """Test registry initialization with default values."""
    registry: Registry[str, type] = Registry()
    assert registry._registry == {}
    assert registry._loaded is False
    assert registry.auto_loads == []
    assert registry.key_getter is None
    assert registry.base_path == os.getcwd()


def test_registry_with_custom_base_path() -> None:
    """Test registry initialization with custom base path."""
    custom_path = "/custom/path"
    registry: Registry[str, type] = Registry(base_path=custom_path)
    assert registry.base_path == custom_path


def test_registry_with_auto_loads() -> None:
    """Test registry initialization with auto loads."""
    auto_loads = ["pattern1", "pattern2"]
    registry: Registry[str, type] = Registry(auto_loads=auto_loads)
    assert registry.auto_loads == auto_loads


def test_registry_overwrite_registration(registry: Registry) -> None:
    """Test that registering with the same key overwrites the previous registration."""

    @registry.register("same_key")
    def first_function() -> str:
        return "first_value"

    @registry.register("same_key")
    def second_function() -> str:
        return "second_value"

    retrieved = registry.get("same_key")
    assert retrieved() == "second_value"
