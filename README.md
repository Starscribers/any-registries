# Any Registries

[![PyPI version](https://badge.fury.io/py/any-registries.svg)](https://badge.fury.io/py/any-registries)
[![Python versions](https://img.shields.io/pypi/pyversions/any-registries.svg)](https://pypi.org/project/any-registries/)

A flexible and powerful registry system for Python applications with auto-loading capabilities. This package provides a generic registry pattern that can be used to register and retrieve any type of object (functions, classes, constants, etc.) with support for automatic module discovery and loading.

## Features

- **Generic Type Support**: Register any type of object (functions, classes, constants)
- **Auto-loading**: Automatically discover and load modules based on glob patterns
- **Multiple Registration Keys**: Register objects with multiple keys simultaneously
- **Key Functions**: Use custom functions to generate registration keys
- **Environment Integration**: Respects `PROJECT_ROOT` and `BASE_DIR` environment variables
- **Lazy Loading**: Optional lazy loading for better performance
- **Type Hints**: Full typing support for better IDE experience

## Installation

```bash
pip install any-registries
```


## Quick Start

### Basic Usage

```python
from any_registries import Registry

# Create a registry
my_registry = Registry()

# Register a function
@my_registry.register("my_function")
def my_function():
    return "Hello, World!"

# Register a class
@my_registry.register("my_class")
class MyClass:
    def __init__(self, name):
        self.name = name

# Retrieve and use registered items
func = my_registry.get("my_function")
print(func())  # Output: Hello, World!

cls = my_registry.get("my_class")
instance = cls("test")
print(instance.name)  # Output: test
```

### Auto-loading Modules

The registry can automatically discover and load modules based on file patterns:

```python
from any_registries import Registry

# Create registry with auto-loading
registry = Registry(base_path="/path/to/your/project")
registry.auto_load("**/handlers/*.py", "**/processors/*.py")

# Or chain the calls
registry = Registry().auto_load("**/handlers/*.py").auto_load("**/processors/*.py")

# Force loading (if lazy loading is disabled)
registry.force_load()
```

### Custom Key Functions

Use a custom function to generate registration keys:

```python
def name_key(obj):
    return obj.__name__

registry = Registry(key=name_key)

@registry.register()  # No key needed, will use function name
def my_named_function():
    return "Named function"

# Retrieve using the function name
func = registry.get("my_named_function")
```

### Environment Variables

The registry respects environment variables for base path discovery:

```python
import os

# Set environment variable
os.environ["PROJECT_ROOT"] = "/my/project/root"

# Registry will use PROJECT_ROOT as base_path
registry = Registry()

# Or use BASE_DIR if PROJECT_ROOT is not set
os.environ["BASE_DIR"] = "/my/base/dir"
registry = Registry()

# Explicit base_path overrides environment variables
registry = Registry(base_path="/explicit/path")
```

## Advanced Usage

### Plugin System Example

Create a simple plugin system:

```python
from any_registries import Registry

# Create a plugin registry
plugins = Registry()

@plugins.register("database")
class DatabasePlugin:
    def connect(self):
        return "Connected to database"

@plugins.register("cache")
class CachePlugin:
    def get(self, key):
        return f"Cache value for {key}"

# Use plugins
db = plugins.get("database")()
print(db.connect())  # Output: Connected to database

cache = plugins.get("cache")()
print(cache.get("user:123"))  # Output: Cache value for user:123
```

### Handler Registry Example

Register and use different handlers:

```python
from any_registries import Registry

# Create handler registry
handlers = Registry()

@handlers.register("json")
def handle_json(data):
    import json
    return json.loads(data)

@handlers.register("csv")
def handle_csv(data):
    import csv
    import io
    return list(csv.reader(io.StringIO(data)))

# Use handlers
json_handler = handlers.get("json")
result = json_handler('{"name": "test"}')
print(result)  # Output: {'name': 'test'}
```

### Factory Pattern Example

Use registry as a factory:

```python
from any_registries import Registry

# Vehicle factory
vehicles = Registry()

@vehicles.register("car")
class Car:
    def __init__(self, model):
        self.model = model

    def start(self):
        return f"{self.model} car started"

@vehicles.register("bike")
class Bike:
    def __init__(self, model):
        self.model = model

    def start(self):
        return f"{self.model} bike started"

# Factory function
def create_vehicle(vehicle_type, model):
    vehicle_class = vehicles.get(vehicle_type)
    return vehicle_class(model)

# Use factory
my_car = create_vehicle("car", "Toyota")
print(my_car.start())  # Output: Toyota car started
```

## API Reference

### Registry Class

```python
class Registry(Generic[TYPE_KEY, TYPE_TARGET]):
    def __init__(
        self,
        base_path: str | None = None,
        auto_loads: list | None = None,
        key: Callable | None = None,
        lazy_load: bool = True,
    ) -> None:
        """
        Initialize a new Registry.

        Args:
            base_path: Base path for module discovery (defaults to environment variables)
            auto_loads: List of glob patterns for auto-loading modules
            key: Function to generate keys from registered objects
            lazy_load: Whether to load modules lazily (default: True)
        """
```

#### Methods

- `get(key)`: Retrieve a registered object by key
- `auto_load(*patterns)`: Add patterns for auto-loading modules
- `force_load()`: Force loading of all auto-load modules
- `registry`: Property to access the internal registry dictionary

### Exceptions

- `ItemNotRegistered`: Raised when trying to retrieve a non-existent key

## Configuration Options

### Lazy Loading

By default, modules are loaded lazily when first accessed. Disable lazy loading:

```python
registry = Registry(lazy_load=False)
```

### Base Path Priority

The registry determines the base path in this order:

1. Explicit `base_path` parameter
2. `PROJECT_ROOT` environment variable
3. `BASE_DIR` environment variable
4. Current working directory (`os.getcwd()`)

## Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e .[dev]

# Run core tests
pytest tests/test_registry.py

# Run tests with coverage
pytest --cov=any_registries
```

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/RIDStarscribers/python-packages.git
cd python-packages/any-registries

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
ruff format src/ tests/
ruff check src/ tests/

# Type checking
mypy src/
```

## Use Cases

- **Plugin Systems**: Register and discover plugins dynamically
- **Handler Registries**: Map keys to handler functions or classes
- **Factory Patterns**: Register classes and create instances by key
- **Command Patterns**: Register command handlers
- **Strategy Patterns**: Register different algorithms or strategies
- **Configuration Management**: Register configuration handlers
- **Data Processing**: Register different data processors or transformers

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure tests pass (`pytest`)
6. Format code (`ruff format` and `ruff check`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 0.2.0
- Initial release
- Basic registry functionality
- Auto-loading support
- Type hints and comprehensive tests
- Python 3.8+ support

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/RIDStarscribers/python-packages/issues) page
2. Create a new issue with detailed information
3. Include Python version and error traceback

## Related Projects

- [Python Design Patterns](https://python-patterns.guide/) - Background on registry and other patterns
