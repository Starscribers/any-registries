import os

import pytest

from any_registries import Registry
from any_registries.exceptions import ItemNotRegistered


@pytest.fixture
def registry():
    """Create a fresh registry for each test."""
    return Registry()


@pytest.fixture
def env_cleanup():
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


def test_register_and_get_simple(registry):
    """Test basic registration and retrieval."""

    @registry.register("test_key")
    def test_function():
        return "test_value"

    retrieved_function = registry.get("test_key")
    assert retrieved_function() == "test_value"


def test_key_getter_function():
    """Test registration using key getter function."""

    def name_key_getter(func):
        return func.__name__

    registry_with_key_getter = Registry(key=name_key_getter)

    @registry_with_key_getter.register()
    def named_function():
        return "named_value"

    retrieved_function = registry_with_key_getter.get("named_function")
    assert retrieved_function() == "named_value"


def test_item_not_registered_exception(registry):
    """Test that ItemNotRegistered is raised for unknown keys."""
    with pytest.raises(
        ItemNotRegistered, match="Item with key 'nonexistent_key' is not registered"
    ):
        registry.get("nonexistent_key")


def test_registry_property(registry):
    """Test the registry property returns the internal dictionary."""

    @registry.register("prop_test")
    def prop_function():
        return "prop_value"

    registry_dict = registry.registry
    assert "prop_test" in registry_dict
    assert registry_dict["prop_test"]() == "prop_value"


def test_class_registration(registry):
    """Test registering classes instead of functions."""

    @registry.register("test_class")
    class TestClass:
        def method(self):
            return "class_method_value"

    retrieved_class = registry.get("test_class")
    instance = retrieved_class()
    assert instance.method() == "class_method_value"


def test_chaining_auto_load():
    """Test that auto_load method returns self for chaining."""
    registry = Registry()
    result = registry.auto_load("pattern1", "pattern2")
    assert result is registry
    assert registry.auto_loads == ["pattern1", "pattern2"]


def test_project_root_environment_variable(env_cleanup):
    """Test that PROJECT_ROOT environment variable is used."""
    os.environ["PROJECT_ROOT"] = "/test/project/root"
    registry = Registry()
    assert registry.base_path == "/test/project/root"


def test_base_dir_environment_variable(env_cleanup):
    """Test that BASE_DIR environment variable is used when PROJECT_ROOT is not set."""
    if "PROJECT_ROOT" in os.environ:
        del os.environ["PROJECT_ROOT"]
    os.environ["BASE_DIR"] = "/test/base/dir"
    registry = Registry()
    assert registry.base_path == "/test/base/dir"


def test_explicit_base_path_overrides_environment(env_cleanup):
    """Test that explicit base_path parameter overrides environment variables."""
    os.environ["PROJECT_ROOT"] = "/test/project/root"
    os.environ["BASE_DIR"] = "/test/base/dir"
    registry = Registry(base_path="/explicit/path")
    assert registry.base_path == "/explicit/path"


def test_registry_empty_initialization():
    """Test registry initialization with default values."""
    registry = Registry()
    assert registry._registry == {}
    assert registry._loaded is False
    assert registry.auto_loads == []
    assert registry.key_getter is None
    assert registry.base_path == os.getcwd()


def test_registry_with_custom_base_path():
    """Test registry initialization with custom base path."""
    custom_path = "/custom/path"
    registry = Registry(base_path=custom_path)
    assert registry.base_path == custom_path


def test_registry_with_auto_loads():
    """Test registry initialization with auto loads."""
    auto_loads = ["pattern1", "pattern2"]
    registry = Registry(auto_loads=auto_loads)
    assert registry.auto_loads == auto_loads


@pytest.mark.parametrize(
    "key,expected",
    [
        ("string_key", "string_key"),
        (123, 123),
        (("tuple", "key"), ("tuple", "key")),
    ],
)
def test_registry_with_different_key_types(key, expected):
    """Test registry with different types of keys."""
    registry = Registry()

    @registry.register(key)
    def test_func():
        return f"value_for_{key}"

    retrieved = registry.get(expected)
    assert retrieved() == f"value_for_{key}"


def test_registry_overwrite_registration(registry):
    """Test that registering with the same key overwrites the previous registration."""

    @registry.register("same_key")
    def first_function():
        return "first_value"

    @registry.register("same_key")
    def second_function():
        return "second_value"

    retrieved = registry.get("same_key")
    assert retrieved() == "second_value"


def test_registry_force_load_idempotent():
    """Test that calling force_load multiple times is safe."""
    registry = Registry()
    assert registry._loaded is False

    registry.force_load()
    assert registry._loaded is True

    # Should remain True after multiple calls
    registry.force_load()
    assert registry._loaded is True
