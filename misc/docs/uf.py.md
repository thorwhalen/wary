## README.md

```python
# uf - UI Fast

**Minimal-boilerplate web UIs for Python functions**

`uf` bridges functions → HTTP services (via [qh](https://github.com/i2mint/qh)) → Web UI forms (via [ju.rjsf](https://github.com/i2mint/ju)), following the "convention over configuration" philosophy.

## Features

- **One-line app creation**: Just pass your functions to `mk_rjsf_app()`
- **Automatic form generation**: RJSF forms created from function signatures
- **Type-aware**: Uses type hints to generate appropriate form fields
- **Zero configuration required**: Sensible defaults for everything
- **Progressive enhancement**: Customize only what you need
- **Mapping-based interfaces**: Access specs and configs as dictionaries
- **Framework agnostic**: Works with Bottle and FastAPI
- **UI decorators**: Rich metadata via `@ui_config`, `@group`, etc.
- **Function grouping**: Organize functions into categories
- **Field customization**: Configure widgets, validation, and interactions
- **Custom type support**: Register transformations for any Python type
- **Field dependencies**: Conditional display and dynamic forms
- **Testing utilities**: Built-in tools for testing your apps

## Installation

```bash
pip install uf
```

## Quick Start

```python
from uf import mk_rjsf_app

def add(x: int, y: int) -> int:
    """Add two numbers"""
    return x + y

def greet(name: str) -> str:
    """Greet a person"""
    return f"Hello, {name}!"

# Create the app
app = mk_rjsf_app([add, greet])

# Run it (for Bottle apps)
app.run(host='localhost', port=8080)
```

Then open http://localhost:8080 in your browser!

## How It Works

`uf` combines three powerful packages from the i2mint ecosystem:

1. **[qh](https://github.com/i2mint/qh)**: Converts functions → HTTP endpoints
2. **[ju.rjsf](https://github.com/i2mint/ju)**: Generates JSON Schema & RJSF specs from signatures
3. **[i2](https://github.com/i2mint/i2)**: Provides signature introspection and manipulation

The result: A complete web UI with zero boilerplate!

## Table of Contents

- [Basic Usage](#basic-usage)
- [UI Decorators](#ui-decorators)
- [Field Configuration](#field-configuration)
- [Function Grouping](#function-grouping)
- [Custom Types](#custom-types)
- [Field Dependencies](#field-dependencies)
- [Testing](#testing)
- [API Reference](#api-reference)
- [Examples](#examples)

## Basic Usage

### Simple Example

```python
from uf import mk_rjsf_app

def multiply(x: float, y: float) -> float:
    """Multiply two numbers"""
    return x * y

app = mk_rjsf_app([multiply], page_title="Calculator")
```

### Object-Oriented Interface

For more control, use the `UfApp` class:

```python
from uf import UfApp

def fibonacci(n: int) -> list:
    """Generate Fibonacci sequence"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]

    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib

# Create app
uf_app = UfApp([fibonacci])

# Call functions programmatically
result = uf_app.call('fibonacci', n=10)

# Access specs
spec = uf_app.get_spec('fibonacci')

# List available functions
functions = uf_app.list_functions()

# Run the server
uf_app.run(host='localhost', port=8080)
```

## UI Decorators

Add rich metadata to your functions using decorators:

### `@ui_config` - Complete UI Configuration

```python
from uf import ui_config, RjsfFieldConfig, get_field_config

@ui_config(
    title="User Registration",
    description="Create a new user account",
    group="Admin",
    icon="user-plus",
    order=1,
    fields={
        'email': get_field_config('email'),
        'bio': get_field_config('multiline_text'),
    }
)
def register_user(email: str, name: str, bio: str = ''):
    """Register a new user."""
    return {'email': email, 'name': name, 'bio': bio}
```

### `@group` - Simple Grouping

```python
from uf import group

@group("Admin")
def delete_user(user_id: int):
    """Delete a user from the system."""
    pass
```

### `@field_config` - Field-Level Configuration

```python
from uf import field_config, get_field_config

@field_config(
    email=get_field_config('email'),
    message=get_field_config('multiline_text'),
)
def send_message(email: str, message: str):
    """Send a message to a user."""
    pass
```

### `@hidden` - Hide from UI

```python
from uf import hidden

@hidden
def internal_function():
    """This won't appear in the UI but is accessible via API."""
    pass
```

### `@with_example` - Provide Test Data

```python
from uf import with_example

@with_example(x=10, y=20)
def add(x: int, y: int) -> int:
    """Add two numbers."""
    return x + y
```

### Other Decorators

```python
from uf import deprecated, requires_auth, rate_limit

@deprecated("Use new_function instead")
def old_function():
    pass

@requires_auth(roles=['admin'], permissions=['user:delete'])
def delete_user(user_id: int):
    pass

@rate_limit(calls=10, period=60)  # 10 calls per minute
def send_email(to: str, subject: str):
    pass
```

## Field Configuration

### Predefined Field Configurations

```python
from uf import get_field_config

# Available configurations:
email_config = get_field_config('email')
password_config = get_field_config('password')
url_config = get_field_config('url')
multiline_config = get_field_config('multiline_text')
long_text_config = get_field_config('long_text')
date_config = get_field_config('date')
datetime_config = get_field_config('datetime')
color_config = get_field_config('color')
file_config = get_field_config('file')
```

### Custom Field Configuration

```python
from uf import RjsfFieldConfig

custom_field = RjsfFieldConfig(
    widget='select',
    enum=['option1', 'option2', 'option3'],
    placeholder='Choose an option',
    description='Please select one option',
)

@field_config(status=custom_field)
def update_status(status: str):
    pass
```

### Field Configuration Builder

```python
from uf import RjsfConfigBuilder, RjsfFieldConfig

builder = RjsfConfigBuilder()
builder.field('name', RjsfFieldConfig(placeholder='Enter name'))
builder.field('email', RjsfFieldConfig(format='email'))
builder.order(['name', 'email', 'phone'])
builder.class_names('custom-form')

spec = builder.build(base_schema)
```

## Function Grouping

### Manual Grouping

```python
from uf import FunctionGroup, mk_grouped_app

admin_group = FunctionGroup(
    name="Admin",
    funcs=[create_user, delete_user, update_user],
    description="User administration functions",
    icon="shield",
    order=1,
)

reports_group = FunctionGroup(
    name="Reports",
    funcs=[generate_report, export_data],
    description="Reporting functions",
    icon="file-text",
    order=2,
)

app = mk_grouped_app([admin_group, reports_group])
```

### Auto-Grouping by Prefix

```python
from uf import auto_group_by_prefix

# Functions named user_create, user_delete, report_generate, etc.
# will be automatically grouped into "User", "Report", etc.
organizer = auto_group_by_prefix(
    [user_create, user_delete, report_generate],
    separator="_"
)
```

### Auto-Grouping by Module

```python
from uf import auto_group_by_module

organizer = auto_group_by_module([func1, func2, func3])
```

### Auto-Grouping by Tag

```python
from uf import auto_group_by_tag

def my_function():
    pass

my_function.__uf_group__ = "Admin"

organizer = auto_group_by_tag([my_function])
```

## Custom Types

Register custom type transformations for seamless JSON serialization:

### Using the Global Registry

```python
from uf import register_type
from pathlib import Path
from decimal import Decimal

# Register Path type
register_type(
    Path,
    to_json=str,
    from_json=Path,
    json_schema_type='string'
)

# Register Decimal type
register_type(
    Decimal,
    to_json=float,
    from_json=Decimal,
    json_schema_type='number'
)
```

### Using a Custom Registry

```python
from uf import InputTransformRegistry

registry = InputTransformRegistry()

registry.register_type(
    MyCustomType,
    to_json=lambda x: x.to_dict(),
    from_json=MyCustomType.from_dict,
    ui_widget='textarea',
    json_schema_type='object'
)

# Use with mk_rjsf_app
input_trans = registry.mk_input_trans_for_funcs([my_func])
output_trans = registry.mk_output_trans()

app = mk_rjsf_app(
    [my_func],
    input_trans=input_trans,
    output_trans=output_trans
)
```

### Pre-registered Types

The following types are automatically supported:
- `datetime.datetime`
- `datetime.date`
- `datetime.time`
- `pathlib.Path`
- `uuid.UUID`
- `decimal.Decimal`

## Field Dependencies

Create dynamic forms where fields show/hide based on other field values:

### Simple Dependency

```python
from uf import FieldDependency, DependencyAction, with_dependencies

@with_dependencies(
    FieldDependency(
        source_field='reason',
        target_field='other_reason',
        condition=lambda v: v == 'other',
        action=DependencyAction.SHOW,
    )
)
def submit_feedback(reason: str, other_reason: str = ''):
    """Submit feedback with conditional 'other' field."""
    pass
```

### Dependency Builder

```python
from uf import DependencyBuilder

builder = DependencyBuilder()
builder.when('age').greater_than(18).enable('alcohol_consent')
builder.when('country').equals('US').show('state')
builder.when('priority').in_list(['high', 'urgent']).require('manager_approval')

dependencies = builder.build()
```

### Available Actions

- `DependencyAction.SHOW` - Show the field
- `DependencyAction.HIDE` - Hide the field
- `DependencyAction.ENABLE` - Enable the field
- `DependencyAction.DISABLE` - Disable the field
- `DependencyAction.REQUIRE` - Make the field required
- `DependencyAction.OPTIONAL` - Make the field optional

## Testing

Built-in testing utilities for your uf apps:

### Test Client

```python
from uf import UfTestClient

client = UfTestClient(app)

# List functions
functions = client.list_functions()

# Get spec
spec = client.get_spec('my_function')

# Call function
result = client.call_function('my_function', {'x': 10, 'y': 20})
assert result['success']
assert result['result'] == 30
```

### Test Context Manager

```python
from uf import UfAppTester

with UfAppTester(app) as tester:
    result = tester.submit_form('add', {'x': 10, 'y': 20})
    tester.assert_success(result)
    tester.assert_result_equals(result, 30)
```

### Testing Individual Functions

```python
from uf import test_ui_function

def add(x: int, y: int) -> int:
    return x + y

# Test with expected output
test_ui_function(add, {'x': 10, 'y': 20}, expected_output=30)

# Test with expected exception
test_ui_function(
    divide,
    {'x': 10, 'y': 0},
    expected_exception=ZeroDivisionError
)
```

### Form Data Builder

```python
from uf import FormDataBuilder

form_data = (
    FormDataBuilder()
    .field('name', 'John Doe')
    .field('email', 'john@example.com')
    .fields(age=30, city='NYC')
    .build()
)
```

### Schema Assertions

```python
from uf import (
    assert_valid_rjsf_spec,
    assert_has_field,
    assert_field_type,
    assert_field_required,
)

spec = app.function_specs['my_function']

assert_valid_rjsf_spec(spec)
assert_has_field(spec, 'email')
assert_field_type(spec, 'age', 'integer')
assert_field_required(spec, 'name')
```

## Customization

### Custom CSS

```python
CUSTOM_CSS = """
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
"""

app = mk_rjsf_app(
    [func1, func2],
    page_title="My Custom App",
    custom_css=CUSTOM_CSS,
)
```

### Advanced qh Configuration

```python
from qh import AppConfig

qh_config = AppConfig(
    cors=True,
    log_requests=True,
)

app = mk_rjsf_app(
    [my_func],
    config=qh_config,
    input_trans=my_input_transformer,
    output_trans=my_output_transformer,
)
```

## Examples

See the `examples/` directory for complete working examples:

- `basic_example.py`: Simple math and text functions
- `advanced_example.py`: Customization and object-oriented interface
- `full_featured_example.py`: **Complete showcase of all features**

## API Reference

### Core Functions

#### `mk_rjsf_app(funcs, **kwargs)`

Main entry point for creating a web app from functions.

**Parameters:**
- `funcs`: Iterable of callable functions
- `config`: Optional qh.AppConfig for HTTP configuration
- `input_trans`: Optional input transformation function
- `output_trans`: Optional output transformation function
- `rjsf_config`: Optional RJSF configuration dict
- `ui_schema_factory`: Optional callable for custom UI schemas
- `page_title`: Title for the web interface (default: "Function Interface")
- `custom_css`: Optional custom CSS string
- `rjsf_theme`: RJSF theme name (default: "default")
- `add_ui`: Whether to add UI routes (default: True)
- `**qh_kwargs`: Additional arguments passed to qh.mk_app

**Returns:** Configured web application (Bottle or FastAPI)

#### `mk_grouped_app(groups, **kwargs)`

Create a uf app with grouped function navigation.

**Parameters:**
- `groups`: Iterable of FunctionGroup objects
- `**kwargs`: Same as mk_rjsf_app

**Returns:** Configured web application with grouped navigation

### Classes

#### `UfApp(funcs, **kwargs)`

Object-oriented wrapper for uf applications.

**Methods:**
- `run(host, port, **kwargs)`: Run the web server
- `call(func_name, **kwargs)`: Call a function by name
- `get_spec(func_name)`: Get RJSF spec for a function
- `list_functions()`: List all function names

#### `FunctionSpecStore(funcs, **kwargs)`

Mapping-based interface to function specifications.

#### `RjsfFieldConfig(**kwargs)`

Configuration for individual form fields.

**Attributes:**
- `widget`: Widget type
- `format`: JSON Schema format
- `enum`: List of allowed values
- `placeholder`: Placeholder text
- `description`: Help text
- And more...

#### `FunctionGroup(name, funcs, **kwargs)`

Group of functions with metadata.

**Attributes:**
- `name`: Group name
- `funcs`: List of functions
- `description`: Group description
- `icon`: Icon identifier
- `order`: Display order

#### `InputTransformRegistry()`

Registry for custom type transformations.

**Methods:**
- `register_type(py_type, **kwargs)`: Register a type
- `mk_input_trans_for_funcs(funcs)`: Create input transformation
- `mk_output_trans()`: Create output transformation

#### `FieldDependency(**kwargs)`

Define a dependency between form fields.

#### `DependencyBuilder()`

Fluent interface for building field dependencies.

### Decorators

- `@ui_config(...)`: Add complete UI configuration
- `@group(name)`: Assign to a group
- `@hidden`: Hide from UI
- `@field_config(**fields)`: Configure specific fields
- `@with_example(**kwargs)`: Attach example data
- `@deprecated(message)`: Mark as deprecated
- `@requires_auth(...)`: Mark as requiring authentication
- `@rate_limit(calls, period)`: Add rate limit metadata

### Testing Utilities

- `UfTestClient(app)`: Test client for uf apps
- `UfAppTester(app)`: Context manager for testing
- `test_ui_function(func, params, **kwargs)`: Test individual functions
- `FormDataBuilder()`: Build test form data
- `assert_valid_rjsf_spec(spec)`: Assert spec is valid
- `assert_has_field(spec, name)`: Assert field exists
- `assert_field_type(spec, name, type)`: Assert field type
- `assert_field_required(spec, name)`: Assert field is required

## Architecture

`uf` follows these design principles:

1. **Convention over Configuration**: Works out-of-the-box with sensible defaults
2. **Mapping-based Interfaces**: Access everything as dictionaries
3. **Lazy Evaluation**: Generate specs only when needed
4. **Composition over Inheritance**: Extend via decorators and transformations
5. **Progressive Enhancement**: Start simple, customize as needed

## Development Roadmap

### ✅ Milestone 1: MVP (Completed)
- [x] Core `mk_rjsf_app` function
- [x] FunctionSpecStore for spec management
- [x] HTML template generation
- [x] Essential API routes

### ✅ Milestone 2: Configuration (Completed)
- [x] RJSF customization layer
- [x] Input transformation registry
- [x] Custom field widgets

### ✅ Milestone 3: Enhancement (Completed)
- [x] Function grouping and organization
- [x] UI metadata decorators (`@ui_config`)
- [x] Auto-grouping utilities

### ✅ Milestone 4: Advanced (Completed)
- [x] Field dependencies and interactions
- [x] Testing utilities
- [x] Comprehensive examples

## Dependencies

- `qh`: HTTP service generation
- `ju`: RJSF form generation and JSON utilities
- `i2`: Signature introspection
- `dol`: Mapping interfaces
- `meshed`: Function composition utilities

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Related Projects

- [qh](https://github.com/i2mint/qh): HTTP services from functions
- [ju](https://github.com/i2mint/ju): JSON Schema and RJSF utilities
- [i2](https://github.com/i2mint/i2): Signature introspection
- [dol](https://github.com/i2mint/dol): Mapping interfaces
- [meshed](https://github.com/i2mint/meshed): Function composition

## Authors

Part of the [i2mint](https://github.com/i2mint) ecosystem.
```

## examples/advanced_example.py

```python
"""Advanced example showing customization options in uf.

This demonstrates:
- Custom page title and CSS
- Using the UfApp class for object-oriented interface
- Functions with more complex types
- Accessing function specs programmatically

To run this example:
    python examples/advanced_example.py
"""

from uf import UfApp


def calculate_bmi(weight_kg: float, height_m: float) -> dict:
    """Calculate Body Mass Index.

    Args:
        weight_kg: Weight in kilograms
        height_m: Height in meters

    Returns:
        Dictionary with BMI value and category
    """
    bmi = weight_kg / (height_m ** 2)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"

    return {
        "bmi": round(bmi, 2),
        "category": category,
    }


def reverse_string(text: str, uppercase: bool = False) -> str:
    """Reverse a string.

    Args:
        text: The string to reverse
        uppercase: Whether to convert to uppercase

    Returns:
        The reversed string
    """
    reversed_text = text[::-1]
    return reversed_text.upper() if uppercase else reversed_text


def fibonacci(n: int) -> list:
    """Generate Fibonacci sequence.

    Args:
        n: Number of Fibonacci numbers to generate

    Returns:
        List of Fibonacci numbers
    """
    if n <= 0:
        return []
    elif n == 1:
        return [0]

    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])

    return fib


# Custom CSS for a nicer look
CUSTOM_CSS = """
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

#sidebar {
    background: rgba(255, 255, 255, 0.95);
}

#header {
    background: rgba(255, 255, 255, 0.95);
}

.function-item.active {
    background: #667eea;
}

.function-item:hover {
    border-color: #667eea;
}
"""


if __name__ == '__main__':
    # Create UfApp with customization
    uf_app = UfApp(
        [calculate_bmi, reverse_string, fibonacci],
        page_title="Advanced Function UI",
        custom_css=CUSTOM_CSS,
    )

    # Access function specs programmatically
    print("Available functions:")
    for func_name in uf_app.list_functions():
        spec = uf_app.get_spec(func_name)
        print(f"  - {func_name}: {spec['description']}")

    # Test calling functions directly
    print("\nDirect function calls:")
    print(f"  fibonacci(10) = {uf_app.call('fibonacci', n=10)}")
    print(f"  reverse_string('hello') = {uf_app.call('reverse_string', text='hello')}")

    print("\nStarting server at http://localhost:8080")
    print("Press Ctrl+C to stop")

    # Run the server
    try:
        uf_app.run(host='localhost', port=8080, debug=True)
    except NotImplementedError:
        print("For FastAPI apps, run:")
        print("  uvicorn examples.advanced_example:uf_app.app --reload")
```

## examples/basic_example.py

```python
"""Basic example of using uf to create a web UI for functions.

This demonstrates the simplest possible usage - just define functions
and pass them to mk_rjsf_app.

To run this example:
    python examples/basic_example.py

Then open http://localhost:8080 in your browser.
"""

from uf import mk_rjsf_app


def add(x: int, y: int) -> int:
    """Add two numbers together.

    Args:
        x: First number
        y: Second number

    Returns:
        The sum of x and y
    """
    return x + y


def multiply(x: float, y: float) -> float:
    """Multiply two numbers.

    Args:
        x: First number
        y: Second number

    Returns:
        The product of x and y
    """
    return x * y


def greet(name: str, greeting: str = "Hello") -> str:
    """Generate a greeting message.

    Args:
        name: Name of the person to greet
        greeting: The greeting to use (default: "Hello")

    Returns:
        A friendly greeting message
    """
    return f"{greeting}, {name}!"


def is_even(number: int) -> bool:
    """Check if a number is even.

    Args:
        number: The number to check

    Returns:
        True if the number is even, False otherwise
    """
    return number % 2 == 0


if __name__ == '__main__':
    # Create the web app with all our functions
    app = mk_rjsf_app(
        [add, multiply, greet, is_even],
        page_title="Basic Math & Text Functions"
    )

    # Run the server
    print("Starting server at http://localhost:8080")
    print("Press Ctrl+C to stop")

    # For bottle apps, we can call run() directly
    if hasattr(app, 'run'):
        app.run(host='localhost', port=8080, debug=True)
    else:
        # For FastAPI apps
        print("For FastAPI apps, run:")
        print("  uvicorn examples.basic_example:app --reload")
```

## examples/full_featured_example.py

```python
"""Full-featured example demonstrating all uf capabilities.

This example showcases:
- UI decorators (@ui_config, @group, etc.)
- Field configurations (email, textarea, etc.)
- Function grouping and organization
- Custom type transformations
- Field dependencies
- Testing utilities

To run this example:
    python examples/full_featured_example.py
"""

from datetime import datetime, date
from typing import Optional
from uf import (
    # Core
    mk_grouped_app,
    # Decorators
    ui_config,
    group,
    field_config,
    with_example,
    # Configuration
    RjsfFieldConfig,
    get_field_config,
    # Organization
    FunctionGroup,
    # Transformation
    InputTransformRegistry,
    # Field interactions
    FieldDependency,
    DependencyAction,
    with_dependencies,
)


# =============================================================================
# User Management Functions (Admin Group)
# =============================================================================

@ui_config(
    title="Create New User",
    description="Register a new user in the system",
    group="Admin",
    icon="user-plus",
    order=1,
)
@field_config(
    email=get_field_config('email'),
    bio=get_field_config('multiline_text'),
)
@with_example(
    name="John Doe",
    email="john@example.com",
    age=30,
    bio="Software developer with 10 years of experience"
)
def create_user(
    name: str,
    email: str,
    age: int,
    bio: str = "",
    is_admin: bool = False,
) -> dict:
    """Create a new user account.

    Args:
        name: Full name of the user
        email: Email address
        age: Age in years
        bio: Short biography
        is_admin: Whether user has admin privileges

    Returns:
        Dictionary with user details and creation timestamp
    """
    return {
        "id": hash(email) % 10000,  # Fake ID for demo
        "name": name,
        "email": email,
        "age": age,
        "bio": bio,
        "is_admin": is_admin,
        "created_at": datetime.now().isoformat(),
    }


@group("Admin")
@with_example(user_id=1234)
def delete_user(user_id: int) -> dict:
    """Delete a user from the system.

    Args:
        user_id: ID of the user to delete

    Returns:
        Confirmation message
    """
    return {
        "success": True,
        "message": f"User {user_id} has been deleted",
        "deleted_at": datetime.now().isoformat(),
    }


# =============================================================================
# Reporting Functions (Reports Group)
# =============================================================================

@ui_config(
    title="Generate Report",
    group="Reports",
    icon="file-text",
    order=1,
)
@field_config(
    report_type=RjsfFieldConfig(
        widget='select',
        enum=['daily', 'weekly', 'monthly', 'yearly'],
    ),
    format=RjsfFieldConfig(
        widget='radio',
        enum=['pdf', 'csv', 'excel'],
    ),
    start_date=get_field_config('date'),
    end_date=get_field_config('date'),
)
def generate_report(
    report_type: str,
    format: str = 'pdf',
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> dict:
    """Generate a report for the specified period.

    Args:
        report_type: Type of report to generate
        format: Output format
        start_date: Optional start date
        end_date: Optional end date

    Returns:
        Report metadata and download link
    """
    return {
        "report_type": report_type,
        "format": format,
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None,
        "generated_at": datetime.now().isoformat(),
        "download_url": f"/downloads/report_{datetime.now().timestamp()}.{format}",
    }


@group("Reports")
def export_data(
    data_type: str,
    include_archived: bool = False,
) -> dict:
    """Export data to CSV format.

    Args:
        data_type: Type of data to export
        include_archived: Whether to include archived records

    Returns:
        Export metadata
    """
    return {
        "data_type": data_type,
        "include_archived": include_archived,
        "record_count": 1234,  # Fake count for demo
        "exported_at": datetime.now().isoformat(),
    }


# =============================================================================
# Communication Functions (Communication Group)
# =============================================================================

@ui_config(
    title="Send Email",
    group="Communication",
    icon="mail",
)
@field_config(
    to_email=get_field_config('email'),
    subject=RjsfFieldConfig(placeholder="Enter email subject"),
    body=get_field_config('long_text'),
    priority=RjsfFieldConfig(
        widget='select',
        enum=['low', 'normal', 'high', 'urgent'],
    ),
)
@with_dependencies(
    FieldDependency(
        source_field='priority',
        target_field='send_immediately',
        condition=lambda v: v in ['high', 'urgent'],
        action=DependencyAction.SHOW,
    )
)
def send_email(
    to_email: str,
    subject: str,
    body: str,
    priority: str = 'normal',
    send_immediately: bool = False,
) -> dict:
    """Send an email message.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body content
        priority: Priority level
        send_immediately: Whether to send immediately (shown for high/urgent priority)

    Returns:
        Email sending confirmation
    """
    return {
        "to": to_email,
        "subject": subject,
        "body_length": len(body),
        "priority": priority,
        "send_immediately": send_immediately,
        "sent_at": datetime.now().isoformat(),
        "message_id": f"msg_{hash(to_email + subject) % 100000}",
    }


@group("Communication")
@with_example(
    recipient="John Doe",
    message="Your order has been shipped!",
    send_sms=True,
)
def send_notification(
    recipient: str,
    message: str,
    send_email: bool = True,
    send_sms: bool = False,
    send_push: bool = False,
) -> dict:
    """Send a multi-channel notification.

    Args:
        recipient: Name of the recipient
        message: Notification message
        send_email: Send via email
        send_sms: Send via SMS
        send_push: Send push notification

    Returns:
        Notification delivery status
    """
    channels = []
    if send_email:
        channels.append('email')
    if send_sms:
        channels.append('sms')
    if send_push:
        channels.append('push')

    return {
        "recipient": recipient,
        "message": message,
        "channels": channels,
        "sent_at": datetime.now().isoformat(),
    }


# =============================================================================
# Utility Functions (Ungrouped)
# =============================================================================

def calculate_statistics(numbers: list[float]) -> dict:
    """Calculate basic statistics for a list of numbers.

    Args:
        numbers: List of numbers

    Returns:
        Dictionary with statistical measures
    """
    if not numbers:
        return {"error": "Empty list provided"}

    return {
        "count": len(numbers),
        "sum": sum(numbers),
        "mean": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers),
    }


# =============================================================================
# Main Application Setup
# =============================================================================

if __name__ == '__main__':
    # Create function groups
    admin_group = FunctionGroup(
        name="Admin",
        funcs=[create_user, delete_user],
        description="User administration functions",
        icon="shield",
        order=1,
    )

    reports_group = FunctionGroup(
        name="Reports",
        funcs=[generate_report, export_data],
        description="Reporting and data export functions",
        icon="file-text",
        order=2,
    )

    communication_group = FunctionGroup(
        name="Communication",
        funcs=[send_email, send_notification],
        description="Email and notification functions",
        icon="mail",
        order=3,
    )

    utilities_group = FunctionGroup(
        name="Utilities",
        funcs=[calculate_statistics],
        description="Utility functions",
        icon="tool",
        order=4,
    )

    # Custom CSS for the app
    CUSTOM_CSS = """
    body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    #sidebar {
        background: rgba(255, 255, 255, 0.95);
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
    }

    #header {
        background: rgba(255, 255, 255, 0.95);
        border-bottom: 2px solid #667eea;
    }

    #header h1 {
        color: #667eea;
    }

    .function-item {
        transition: all 0.3s ease;
    }

    .function-item.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        transform: translateX(5px);
    }

    .function-item:hover {
        border-color: #667eea;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }

    button[type="submit"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    button[type="submit"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    .form-section {
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    """

    # Set up custom type registry
    registry = InputTransformRegistry()

    # Register datetime types (already done by default, but showing how)
    from datetime import datetime, date

    # Create the grouped app
    app = mk_grouped_app(
        groups=[admin_group, reports_group, communication_group, utilities_group],
        page_title="Enterprise Admin Panel",
        custom_css=CUSTOM_CSS,
    )

    print("=" * 70)
    print("Full-Featured uf Application")
    print("=" * 70)
    print()
    print("Features demonstrated:")
    print("  ✓ Function grouping and organization")
    print("  ✓ UI decorators (@ui_config, @group, etc.)")
    print("  ✓ Field configurations (email, textarea, select, etc.)")
    print("  ✓ Field dependencies (conditional display)")
    print("  ✓ Example values for testing")
    print("  ✓ Custom CSS styling")
    print("  ✓ Type transformations (datetime, date)")
    print()
    print("Available groups:")
    for group in [admin_group, reports_group, communication_group, utilities_group]:
        print(f"  • {group.name}: {len(group.funcs)} functions")
    print()
    print("Starting server at http://localhost:8080")
    print("Press Ctrl+C to stop")
    print("=" * 70)

    # For bottle apps, we can call run() directly
    if hasattr(app, 'run'):
        app.run(host='localhost', port=8080, debug=True)
    else:
        print("\nFor FastAPI apps, run:")
        print("  uvicorn examples.full_featured_example:app --reload")
```

## examples/ultimate_showcase.py

```python
"""Ultimate showcase of all uf features.

This example demonstrates every major feature of the uf package:
- Async function support
- Pydantic model integration
- Result rendering (tables, charts, images)
- Call history and presets
- Authentication and authorization
- Caching with multiple backends
- Background task execution
- OpenAPI/Swagger documentation
- Webhook integration
- Theme customization
- Field interactions and dependencies
- Custom transformations
- Function grouping and organization

Run with: python examples/ultimate_showcase.py
"""

import asyncio
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional, List
import json

# Import Pydantic
try:
    from pydantic import BaseModel, Field, EmailStr
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False

# Import uf
from uf import (
    # Core
    mk_rjsf_app,
    UfApp,

    # Organization
    FunctionGroup,
    mk_grouped_app,

    # Decorators
    ui_config,
    group,
    field_config,
    with_example,
    requires_auth,
    rate_limit,

    # Field interactions
    with_dependencies,
    FieldDependency,
    DependencyAction,

    # Async support
    is_async_function,
    timeout_async,
    retry_async,

    # Pydantic support
    wrap_pydantic_function,

    # Renderers
    result_renderer,
    register_renderer,
    get_global_renderer_registry,

    # History
    enable_history,
    get_global_history_manager,

    # Authentication
    DictAuthBackend,
    require_auth,
    User,

    # Caching
    cached,
    MemoryCache,
    get_global_cache_backend,

    # Background tasks
    background,
    get_global_task_queue,
    TaskQueue,

    # OpenAPI
    add_openapi_routes,
    OpenAPIConfig,

    # Webhooks
    webhook,
    WebhookManager,
    get_global_webhook_manager,

    # Themes
    ThemeConfig,
    DARK_THEME,
)


# =============================================================================
# 1. PYDANTIC MODELS
# =============================================================================

if HAS_PYDANTIC:
    class UserProfile(BaseModel):
        """User profile with validation."""

        username: str = Field(..., min_length=3, max_length=20, description="Username (3-20 chars)")
        email: EmailStr = Field(..., description="Valid email address")
        age: int = Field(..., gt=0, lt=150, description="Age in years")
        bio: Optional[str] = Field(None, max_length=500, description="Short bio")
        is_active: bool = Field(True, description="Account active?")

    class DataQuery(BaseModel):
        """Query parameters for data analysis."""

        start_date: date = Field(..., description="Start date")
        end_date: date = Field(..., description="End date")
        metric: str = Field(..., description="Metric to analyze")
        granularity: str = Field('daily', description="Time granularity")


# =============================================================================
# 2. AUTHENTICATION SETUP
# =============================================================================

# Create authentication backend
auth_backend = DictAuthBackend.from_dict({
    'admin': {
        'password': 'admin123',
        'roles': ['admin', 'user'],
        'permissions': ['read', 'write', 'delete']
    },
    'user': {
        'password': 'user123',
        'roles': ['user'],
        'permissions': ['read', 'write']
    },
    'viewer': {
        'password': 'view123',
        'roles': ['viewer'],
        'permissions': ['read']
    }
})


# =============================================================================
# 3. CACHE SETUP
# =============================================================================

# Create memory cache with 100 item limit
cache = MemoryCache(max_size=100)


# =============================================================================
# 4. BACKGROUND TASK QUEUE
# =============================================================================

# Create task queue with 2 workers
task_queue = TaskQueue(num_workers=2)
task_queue.start()


# =============================================================================
# 5. WEBHOOK MANAGER
# =============================================================================

webhook_manager = WebhookManager()
# In production, you would add webhook URLs:
# webhook_manager.add_webhook('https://example.com/webhook', events=['success'])


# =============================================================================
# 6. BASIC FUNCTIONS (Group: Utilities)
# =============================================================================

@group('Utilities')
@ui_config(
    title='Add Numbers',
    description='Add two numbers together',
)
@field_config('x', title='First Number', description='Enter the first number')
@field_config('y', title='Second Number', description='Enter the second number')
@with_example(x=10, y=20, example_name='Ten plus twenty')
@cached(ttl=300)  # Cache for 5 minutes
@result_renderer('json')
def add(x: int, y: int) -> dict:
    """Add two numbers and return detailed result."""
    result = x + y
    return {
        'operation': 'addition',
        'operands': [x, y],
        'result': result,
        'is_even': result % 2 == 0,
        'timestamp': datetime.now().isoformat()
    }


@group('Utilities')
@ui_config(title='Calculate Statistics')
@result_renderer('table')
def calculate_stats(numbers: str) -> list[dict]:
    """Calculate statistics from a comma-separated list of numbers.

    Returns a table of statistical measures.
    """
    nums = [float(n.strip()) for n in numbers.split(',')]

    return [
        {'metric': 'Count', 'value': len(nums)},
        {'metric': 'Sum', 'value': sum(nums)},
        {'metric': 'Mean', 'value': sum(nums) / len(nums)},
        {'metric': 'Min', 'value': min(nums)},
        {'metric': 'Max', 'value': max(nums)},
        {'metric': 'Range', 'value': max(nums) - min(nums)},
    ]


# =============================================================================
# 7. ASYNC FUNCTIONS (Group: Async Operations)
# =============================================================================

@group('Async Operations')
@ui_config(title='Async Data Fetch')
@timeout_async(5.0)  # 5 second timeout
@retry_async(max_retries=3, delay=1.0)
@cached(ttl=60)
async def fetch_data(endpoint: str, timeout: float = 2.0) -> dict:
    """Fetch data from an API endpoint (simulated).

    Demonstrates async support with timeout and retry.
    """
    # Simulate async API call
    await asyncio.sleep(timeout)

    return {
        'endpoint': endpoint,
        'status': 'success',
        'data': {
            'items': ['item1', 'item2', 'item3'],
            'count': 3,
            'fetched_at': datetime.now().isoformat()
        },
        'latency_ms': timeout * 1000
    }


@group('Async Operations')
@ui_config(title='Async Batch Processing')
async def process_batch(item_count: int = 5, delay_per_item: float = 0.5) -> dict:
    """Process multiple items concurrently.

    Demonstrates concurrent async execution.
    """
    async def process_item(item_id: int):
        await asyncio.sleep(delay_per_item)
        return f"Item {item_id} processed"

    # Process items concurrently
    results = await asyncio.gather(*[process_item(i) for i in range(item_count)])

    return {
        'total_items': item_count,
        'results': results,
        'total_time_seconds': delay_per_item,  # Concurrent, not sequential
        'completed_at': datetime.now().isoformat()
    }


# =============================================================================
# 8. PYDANTIC FUNCTIONS (Group: Data Management)
# =============================================================================

if HAS_PYDANTIC:
    @group('Data Management')
    @ui_config(title='Create User Profile')
    @result_renderer('json')
    def create_user(profile: UserProfile) -> dict:
        """Create a user profile with full validation.

        Demonstrates Pydantic integration with automatic form generation
        and validation.
        """
        return {
            'status': 'created',
            'profile': profile.dict(),
            'validation': 'All fields validated successfully',
            'created_at': datetime.now().isoformat()
        }

    # Wrap to handle Pydantic models
    create_user = wrap_pydantic_function(create_user)


    @group('Data Management')
    @ui_config(title='Analyze Data Range')
    @result_renderer('table')
    def analyze_data_range(query: DataQuery) -> list[dict]:
        """Analyze data for a specific date range.

        Demonstrates Pydantic models with date fields.
        """
        days = (query.end_date - query.start_date).days + 1

        return [
            {'field': 'Metric', 'value': query.metric},
            {'field': 'Start Date', 'value': query.start_date.isoformat()},
            {'field': 'End Date', 'value': query.end_date.isoformat()},
            {'field': 'Days', 'value': days},
            {'field': 'Granularity', 'value': query.granularity},
            {'field': 'Data Points', 'value': days if query.granularity == 'daily' else days // 7},
        ]

    # Wrap to handle Pydantic models
    analyze_data_range = wrap_pydantic_function(analyze_data_range)


# =============================================================================
# 9. AUTHENTICATED FUNCTIONS (Group: Admin)
# =============================================================================

@group('Admin')
@ui_config(title='View System Status')
@require_auth(auth_backend, roles=['admin', 'user'])
@result_renderer('table')
def get_system_status() -> list[dict]:
    """View system status (requires authentication).

    Accessible by: admin, user
    """
    return [
        {'component': 'Web Server', 'status': 'Running', 'uptime_hours': 48},
        {'component': 'Database', 'status': 'Running', 'uptime_hours': 240},
        {'component': 'Cache', 'status': 'Running', 'uptime_hours': 48},
        {'component': 'Task Queue', 'status': 'Running', 'uptime_hours': 48},
    ]


@group('Admin')
@ui_config(title='Delete Old Data')
@require_auth(auth_backend, roles=['admin'], permissions=['delete'])
@with_example(days_old=30, example_name='Delete 30-day old data')
def delete_old_data(days_old: int = 30, confirm: bool = False) -> dict:
    """Delete data older than specified days (admin only).

    Requires admin role and delete permission.
    """
    if not confirm:
        return {
            'status': 'cancelled',
            'message': 'Confirmation required to delete data',
            'would_delete': f'Data older than {days_old} days'
        }

    return {
        'status': 'deleted',
        'days_old': days_old,
        'deleted_count': 150,  # Simulated
        'deleted_at': datetime.now().isoformat()
    }


# =============================================================================
# 10. BACKGROUND TASKS (Group: Background Jobs)
# =============================================================================

@group('Background Jobs')
@ui_config(title='Send Bulk Emails')
@background(task_queue=task_queue)
def send_bulk_emails(recipient_count: int, delay_per_email: float = 1.0) -> dict:
    """Send emails in the background (returns immediately).

    This function runs in a background worker thread.
    Returns a task_id immediately.
    """
    import time

    results = []
    for i in range(recipient_count):
        time.sleep(delay_per_email)
        results.append(f"Email {i+1} sent to recipient_{i+1}@example.com")

    return {
        'total_sent': recipient_count,
        'results': results,
        'completed_at': datetime.now().isoformat()
    }


@group('Background Jobs')
@ui_config(title='Generate Report')
@background(task_queue=task_queue)
@webhook(on=['success', 'failure'], manager=webhook_manager)
def generate_large_report(pages: int = 100, delay_per_page: float = 0.1) -> dict:
    """Generate a large report in the background.

    Demonstrates background tasks + webhooks.
    Webhook fires on completion or failure.
    """
    import time

    for i in range(pages):
        time.sleep(delay_per_page)

    return {
        'status': 'completed',
        'pages': pages,
        'file_size_mb': pages * 0.5,  # Simulated
        'generated_at': datetime.now().isoformat()
    }


# =============================================================================
# 11. CACHED EXPENSIVE OPERATIONS (Group: Analytics)
# =============================================================================

@group('Analytics')
@ui_config(title='Calculate Prime Numbers')
@cached(ttl=600, backend=cache)  # Cache for 10 minutes
@result_renderer('json')
def calculate_primes(limit: int = 1000) -> dict:
    """Calculate prime numbers up to limit (cached).

    Expensive operation - results are cached for 10 minutes.
    """
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

    primes = [n for n in range(2, limit + 1) if is_prime(n)]

    return {
        'limit': limit,
        'count': len(primes),
        'primes': primes[:20],  # First 20
        'largest': primes[-1] if primes else None,
        'calculated_at': datetime.now().isoformat(),
        'cached': True
    }


# =============================================================================
# 12. FIELD DEPENDENCIES (Group: Forms)
# =============================================================================

@group('Forms')
@ui_config(title='Conditional Shipping Form')
@with_dependencies(
    FieldDependency(
        source_field='needs_shipping',
        target_field='address',
        action=DependencyAction.SHOW,
        condition=lambda value: value == True
    ),
    FieldDependency(
        source_field='needs_shipping',
        target_field='express_delivery',
        action=DependencyAction.SHOW,
        condition=lambda value: value == True
    )
)
def process_order(
    product: str,
    quantity: int,
    needs_shipping: bool = False,
    address: str = '',
    express_delivery: bool = False
) -> dict:
    """Process an order with conditional shipping fields.

    Demonstrates field dependencies - shipping fields only show
    if needs_shipping is True.
    """
    result = {
        'order_id': f'ORD-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
        'product': product,
        'quantity': quantity,
        'needs_shipping': needs_shipping,
        'total_price': quantity * 29.99  # Simulated
    }

    if needs_shipping:
        result['shipping'] = {
            'address': address,
            'express': express_delivery,
            'estimated_days': 1 if express_delivery else 5
        }

    return result


# =============================================================================
# 13. RATE LIMITED FUNCTIONS (Group: API)
# =============================================================================

@group('API')
@ui_config(title='API Endpoint')
@rate_limit(calls=5, period=60)  # 5 calls per minute
def api_call(endpoint: str, method: str = 'GET') -> dict:
    """Make an API call (rate limited to 5/minute).

    Demonstrates rate limiting.
    """
    return {
        'endpoint': endpoint,
        'method': method,
        'status': 200,
        'rate_limit': {
            'limit': 5,
            'period_seconds': 60,
            'remaining': 4  # Simulated
        },
        'timestamp': datetime.now().isoformat()
    }


# =============================================================================
# 14. HISTORY-ENABLED FUNCTIONS (Group: History)
# =============================================================================

@group('History')
@ui_config(title='Search (with history)')
@enable_history(max_calls=50)
def search(query: str, filters: str = '', limit: int = 10) -> dict:
    """Search with automatic history tracking.

    All calls are recorded in history. You can view past searches
    and reuse parameters as presets.
    """
    return {
        'query': query,
        'filters': filters,
        'limit': limit,
        'results_count': 42,  # Simulated
        'search_time_ms': 23,
        'timestamp': datetime.now().isoformat()
    }


# =============================================================================
# 15. CUSTOM RENDERER EXAMPLE (Group: Visualization)
# =============================================================================

@group('Visualization')
@ui_config(title='Generate Chart Data')
@result_renderer('chart')
def generate_chart_data(data_points: int = 10, chart_type: str = 'line') -> dict:
    """Generate data for visualization.

    Returns data in a format suitable for charting libraries.
    """
    import random

    labels = [f'Point {i+1}' for i in range(data_points)]
    values = [random.randint(10, 100) for _ in range(data_points)]

    return {
        'type': chart_type,
        'labels': labels,
        'datasets': [
            {
                'label': 'Sample Data',
                'data': values,
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 1
            }
        ]
    }


# =============================================================================
# CREATE THE APP
# =============================================================================

# Collect all functions
functions = [
    # Utilities
    add,
    calculate_stats,

    # Async
    fetch_data,
    process_batch,

    # Admin
    get_system_status,
    delete_old_data,

    # Background
    send_bulk_emails,
    generate_large_report,

    # Analytics
    calculate_primes,

    # Forms
    process_order,

    # API
    api_call,

    # History
    search,

    # Visualization
    generate_chart_data,
]

# Add Pydantic functions if available
if HAS_PYDANTIC:
    functions.extend([
        create_user,
        analyze_data_range,
    ])

# Create grouped app with dark theme
app = mk_grouped_app(
    functions,
    page_title='uf Ultimate Showcase',
    theme_config=ThemeConfig(
        default_theme='dark',
        allow_toggle=True,
        available_themes=['light', 'dark', 'ocean', 'sunset']
    ),
    custom_css="""
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        margin-bottom: 2rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .app-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }

    .app-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }

    .feature-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        border-radius: 12px;
        font-size: 0.9rem;
    }
    """
)

# Add OpenAPI documentation
openapi_config = OpenAPIConfig(
    title='uf Ultimate Showcase API',
    version='1.0.0',
    description='Comprehensive demonstration of all uf features',
    enable_swagger=True,
    enable_redoc=True
)

add_openapi_routes(app.app, functions, **openapi_config.to_dict())

# Print startup information
print("=" * 70)
print("uf Ultimate Showcase - All Features Demonstrated")
print("=" * 70)
print("\nFeatures included:")
print("  ✓ Async function support (timeout, retry)")
if HAS_PYDANTIC:
    print("  ✓ Pydantic model integration (auto forms + validation)")
else:
    print("  ⚠ Pydantic not installed (install with: pip install pydantic)")
print("  ✓ Result rendering (JSON, tables, charts)")
print("  ✓ Call history and presets")
print("  ✓ Authentication (3 test users)")
print("  ✓ Caching (memory backend)")
print("  ✓ Background tasks (2 worker threads)")
print("  ✓ OpenAPI/Swagger documentation")
print("  ✓ Webhook integration")
print("  ✓ Theme system (dark mode + 4 themes)")
print("  ✓ Field dependencies")
print("  ✓ Rate limiting")
print("  ✓ Function grouping")
print("\nTest Users:")
print("  • admin / admin123 (full access)")
print("  • user / user123 (read + write)")
print("  • viewer / view123 (read only)")
print("\nDocumentation:")
print("  • Swagger UI: http://localhost:8080/docs")
print("  • ReDoc: http://localhost:8080/redoc")
print("  • OpenAPI Spec: http://localhost:8080/openapi.json")
print("\nStarting server on http://localhost:8080")
print("=" * 70)
print()

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
```

## tests/__init__.py

```python
"""Tests for the uf package."""
```

## tests/test_decorators.py

```python
"""Tests for uf.decorators module."""

import pytest
from uf.decorators import (
    ui_config,
    group,
    hidden,
    field_config,
    get_ui_config,
    get_group,
    get_field_configs,
    is_hidden,
    with_example,
    get_example,
)
from uf.rjsf_config import RjsfFieldConfig


def test_ui_config_decorator():
    """Test ui_config decorator."""

    @ui_config(title="Test Function", group="TestGroup")
    def test_func():
        pass

    config = get_ui_config(test_func)
    assert config is not None
    assert config['title'] == "Test Function"
    assert config['group'] == "TestGroup"


def test_group_decorator():
    """Test group decorator."""

    @group("Admin")
    def admin_func():
        pass

    func_group = get_group(admin_func)
    assert func_group == "Admin"


def test_hidden_decorator():
    """Test hidden decorator."""

    @hidden
    def secret_func():
        pass

    assert is_hidden(secret_func)


def test_field_config_decorator():
    """Test field_config decorator."""
    email_config = RjsfFieldConfig(format='email')
    bio_config = RjsfFieldConfig(widget='textarea')

    @field_config(email=email_config, bio=bio_config)
    def create_profile(email: str, bio: str):
        pass

    configs = get_field_configs(create_profile)
    assert 'email' in configs
    assert 'bio' in configs
    assert configs['email'].format == 'email'
    assert configs['bio'].widget == 'textarea'


def test_with_example_decorator():
    """Test with_example decorator."""

    @with_example(x=10, y=20)
    def add(x: int, y: int):
        return x + y

    example = get_example(add)
    assert example is not None
    args, kwargs = example
    assert kwargs == {'x': 10, 'y': 20}


def test_ui_config_with_fields():
    """Test ui_config with field configurations."""
    email_config = RjsfFieldConfig(format='email')

    @ui_config(
        title="User Form",
        fields={'email': email_config}
    )
    def create_user(email: str):
        pass

    config = get_ui_config(create_user)
    assert config['fields']['email'].format == 'email'


def test_get_ui_config_none():
    """Test getting config from unconfigured function."""

    def plain_func():
        pass

    config = get_ui_config(plain_func)
    assert config is None


def test_is_hidden_false():
    """Test is_hidden on non-hidden function."""

    def visible_func():
        pass

    assert not is_hidden(visible_func)


def test_decorator_preserves_function():
    """Test that decorators preserve the original function."""

    @ui_config(title="Test")
    def test_func(x: int) -> int:
        return x * 2

    # Function should still work
    assert test_func(5) == 10
    # And should have the config
    assert get_ui_config(test_func)['title'] == "Test"
```

## tests/test_specs.py

```python
"""Tests for uf.specs module."""

import pytest
from uf.specs import FunctionSpecStore


def sample_add(x: int, y: int) -> int:
    """Add two numbers."""
    return x + y


def sample_greet(name: str, greeting: str = "Hello") -> str:
    """Greet a person."""
    return f"{greeting}, {name}!"


def test_function_spec_store_creation():
    """Test creating a FunctionSpecStore."""
    funcs = [sample_add, sample_greet]
    store = FunctionSpecStore(funcs)

    assert len(store) == 2
    assert 'sample_add' in store
    assert 'sample_greet' in store


def test_function_spec_store_getitem():
    """Test getting specs from the store."""
    funcs = [sample_add]
    store = FunctionSpecStore(funcs)

    spec = store['sample_add']

    assert 'schema' in spec
    assert 'uiSchema' in spec
    assert 'func' in spec
    assert spec['func'] == sample_add


def test_function_spec_schema_basic():
    """Test that basic schema is generated correctly."""
    funcs = [sample_add]
    store = FunctionSpecStore(funcs)

    spec = store['sample_add']
    schema = spec['schema']

    # Check schema structure
    assert schema['type'] == 'object'
    assert 'properties' in schema
    assert 'x' in schema['properties']
    assert 'y' in schema['properties']


def test_function_spec_required_params():
    """Test that required parameters are identified."""
    funcs = [sample_greet]
    store = FunctionSpecStore(funcs)

    spec = store['sample_greet']
    schema = spec['schema']

    # 'name' is required, 'greeting' has default so is optional
    assert 'name' in schema.get('required', [])
    assert 'greeting' not in schema.get('required', [])


def test_function_spec_store_iteration():
    """Test iterating over the store."""
    funcs = [sample_add, sample_greet]
    store = FunctionSpecStore(funcs)

    names = list(store)
    assert 'sample_add' in names
    assert 'sample_greet' in names


def test_function_spec_store_missing_function():
    """Test accessing a non-existent function."""
    funcs = [sample_add]
    store = FunctionSpecStore(funcs)

    with pytest.raises(KeyError):
        _ = store['nonexistent_function']


def test_function_list():
    """Test the function_list property."""
    funcs = [sample_add, sample_greet]
    store = FunctionSpecStore(funcs)

    func_list = store.function_list

    assert len(func_list) == 2
    assert any(f['name'] == 'sample_add' for f in func_list)
    assert any(f['name'] == 'sample_greet' for f in func_list)


def test_get_func():
    """Test getting the original function."""
    funcs = [sample_add]
    store = FunctionSpecStore(funcs)

    func = store.get_func('sample_add')
    assert func == sample_add
    assert func(10, 20) == 30
```

## tests/test_testing.py

```python
"""Tests for uf.testing module."""

import pytest
from uf.testing import (
    test_ui_function,
    FormDataBuilder,
    assert_valid_rjsf_spec,
    assert_has_field,
    assert_field_type,
    assert_field_required,
)


def test_test_ui_function_success():
    """Test test_ui_function with successful call."""

    def add(x: int, y: int) -> int:
        return x + y

    result = test_ui_function(add, {'x': 10, 'y': 20}, expected_output=30)
    assert result is True


def test_test_ui_function_wrong_output():
    """Test test_ui_function with wrong expected output."""

    def add(x: int, y: int) -> int:
        return x + y

    with pytest.raises(AssertionError):
        test_ui_function(add, {'x': 10, 'y': 20}, expected_output=999)


def test_test_ui_function_exception():
    """Test test_ui_function expecting an exception."""

    def divide(x: int, y: int) -> float:
        return x / y

    result = test_ui_function(
        divide,
        {'x': 10, 'y': 0},
        expected_exception=ZeroDivisionError
    )
    assert result is True


def test_form_data_builder():
    """Test FormDataBuilder."""
    data = (
        FormDataBuilder()
        .field('name', 'John')
        .field('age', 30)
        .fields(email='john@example.com', city='NYC')
        .build()
    )

    assert data['name'] == 'John'
    assert data['age'] == 30
    assert data['email'] == 'john@example.com'
    assert data['city'] == 'NYC'


def test_assert_valid_rjsf_spec():
    """Test assert_valid_rjsf_spec with valid spec."""
    spec = {
        'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'}
            }
        },
        'uiSchema': {}
    }

    assert_valid_rjsf_spec(spec)  # Should not raise


def test_assert_valid_rjsf_spec_invalid():
    """Test assert_valid_rjsf_spec with invalid spec."""
    spec = {'schema': {}}  # Missing required fields

    with pytest.raises(AssertionError):
        assert_valid_rjsf_spec(spec)


def test_assert_has_field():
    """Test assert_has_field."""
    spec = {
        'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            }
        }
    }

    assert_has_field(spec, 'name')  # Should not raise
    assert_has_field(spec, 'age')  # Should not raise


def test_assert_has_field_missing():
    """Test assert_has_field with missing field."""
    spec = {
        'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'}
            }
        }
    }

    with pytest.raises(AssertionError):
        assert_has_field(spec, 'nonexistent')


def test_assert_field_type():
    """Test assert_field_type."""
    spec = {
        'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            }
        }
    }

    assert_field_type(spec, 'name', 'string')
    assert_field_type(spec, 'age', 'integer')


def test_assert_field_type_wrong():
    """Test assert_field_type with wrong type."""
    spec = {
        'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'}
            }
        }
    }

    with pytest.raises(AssertionError):
        assert_field_type(spec, 'name', 'integer')


def test_assert_field_required():
    """Test assert_field_required."""
    spec = {
        'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            },
            'required': ['name']
        }
    }

    assert_field_required(spec, 'name')  # Should not raise


def test_assert_field_required_not_required():
    """Test assert_field_required on optional field."""
    spec = {
        'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'}
            },
            'required': []
        }
    }

    with pytest.raises(AssertionError):
        assert_field_required(spec, 'name')
```

## uf/__init__.py

```python
"""uf - UI Fast: Minimal-boilerplate web UIs for Python functions.

uf bridges functions to HTTP services (via qh) to Web UI forms (via ju.rjsf),
following the "convention over configuration" philosophy.

Basic usage:
    >>> from uf import mk_rjsf_app
    >>>
    >>> def add(x: int, y: int) -> int:
    ...     '''Add two numbers'''
    ...     return x + y
    >>>
    >>> app = mk_rjsf_app([add])
    >>> # app.run()  # Start the web server

The main entry points are:
- `mk_rjsf_app`: Create a web app from functions (functional interface)
- `UfApp`: Object-oriented wrapper with additional conveniences
- `FunctionSpecStore`: Manage function specifications (advanced usage)

Advanced features:
- `ui_config`: Decorator for UI metadata
- `RjsfFieldConfig`: Field configuration class
- `FunctionGroup`: Group functions for organization
- `InputTransformRegistry`: Custom type transformations
- Field dependencies and interactions
- Testing utilities
"""

# Core functionality
from uf.base import mk_rjsf_app, UfApp
from uf.specs import FunctionSpecStore

# RJSF configuration
from uf.rjsf_config import (
    RjsfFieldConfig,
    RjsfConfigBuilder,
    get_field_config,
    apply_field_configs,
    ConditionalFieldConfig,
)

# Input transformation
from uf.trans import (
    InputTransformRegistry,
    register_type,
    get_global_registry,
)

# Organization
from uf.organization import (
    FunctionGroup,
    FunctionOrganizer,
    mk_grouped_app,
    auto_group_by_prefix,
    auto_group_by_module,
    auto_group_by_tag,
)

# Decorators
from uf.decorators import (
    ui_config,
    group,
    hidden,
    field_config,
    with_example,
    deprecated,
    requires_auth,
    rate_limit,
    get_ui_config,
    get_group,
    get_field_configs,
    is_hidden,
    get_example,
)

# Field interactions
from uf.field_interactions import (
    FieldDependency,
    DependencyAction,
    DependencyBuilder,
    with_dependencies,
    get_field_dependencies,
)

# Testing utilities
from uf.testing import (
    UfTestClient,
    UfAppTester,
    test_ui_function,
    FormDataBuilder,
    assert_valid_rjsf_spec,
    assert_has_field,
    assert_field_type,
    assert_field_required,
)

# Result rendering
from uf.renderers import (
    ResultRenderer,
    ResultRendererRegistry,
    get_global_renderer_registry,
    register_renderer,
    render_result,
    result_renderer,
    get_result_renderer,
)

# Async support
from uf.async_support import (
    is_async_function,
    async_to_sync,
    make_sync_compatible,
    AsyncFunctionWrapper,
    timeout_async,
    retry_async,
)

# Pydantic integration
from uf.pydantic_support import (
    is_pydantic_model,
    pydantic_model_to_json_schema,
    function_uses_pydantic,
    wrap_pydantic_function,
    pydantic_to_dict,
    dict_to_pydantic,
)

# History and presets
from uf.history import (
    FunctionCall,
    CallHistory,
    Preset,
    PresetManager,
    HistoryManager,
    get_global_history_manager,
    enable_history,
)

# Authentication
from uf.auth import (
    User,
    AuthBackend,
    DictAuthBackend,
    SessionManager,
    ApiKey,
    ApiKeyManager,
    require_auth,
    get_global_auth_backend,
)

# Caching
from uf.caching import (
    CacheBackend,
    MemoryCache,
    DiskCache,
    cached,
    get_global_cache_backend,
)

# Background tasks
from uf.background import (
    Task,
    TaskStatus,
    TaskQueue,
    background,
    get_global_task_queue,
)

# OpenAPI
from uf.openapi import (
    generate_openapi_spec,
    add_openapi_routes,
    OpenAPIConfig,
)

# Webhooks
from uf.webhooks import (
    WebhookEvent,
    WebhookClient,
    WebhookManager,
    webhook,
    get_global_webhook_manager,
)

# Themes
from uf.themes import (
    Theme,
    ThemeConfig,
    get_theme,
    LIGHT_THEME,
    DARK_THEME,
)

__version__ = "0.0.1"

__all__ = [
    # Core
    "mk_rjsf_app",
    "UfApp",
    "FunctionSpecStore",
    # RJSF Config
    "RjsfFieldConfig",
    "RjsfConfigBuilder",
    "get_field_config",
    "apply_field_configs",
    "ConditionalFieldConfig",
    # Transformation
    "InputTransformRegistry",
    "register_type",
    "get_global_registry",
    # Organization
    "FunctionGroup",
    "FunctionOrganizer",
    "mk_grouped_app",
    "auto_group_by_prefix",
    "auto_group_by_module",
    "auto_group_by_tag",
    # Decorators
    "ui_config",
    "group",
    "hidden",
    "field_config",
    "with_example",
    "deprecated",
    "requires_auth",
    "rate_limit",
    "get_ui_config",
    "get_group",
    "get_field_configs",
    "is_hidden",
    "get_example",
    # Field Interactions
    "FieldDependency",
    "DependencyAction",
    "DependencyBuilder",
    "with_dependencies",
    "get_field_dependencies",
    # Testing
    "UfTestClient",
    "UfAppTester",
    "test_ui_function",
    "FormDataBuilder",
    "assert_valid_rjsf_spec",
    "assert_has_field",
    "assert_field_type",
    "assert_field_required",
    # Renderers
    "ResultRenderer",
    "ResultRendererRegistry",
    "get_global_renderer_registry",
    "register_renderer",
    "render_result",
    "result_renderer",
    "get_result_renderer",
    # Async
    "is_async_function",
    "async_to_sync",
    "make_sync_compatible",
    "AsyncFunctionWrapper",
    "timeout_async",
    "retry_async",
    # Pydantic
    "is_pydantic_model",
    "pydantic_model_to_json_schema",
    "function_uses_pydantic",
    "wrap_pydantic_function",
    "pydantic_to_dict",
    "dict_to_pydantic",
    # History
    "FunctionCall",
    "CallHistory",
    "Preset",
    "PresetManager",
    "HistoryManager",
    "get_global_history_manager",
    "enable_history",
    # Authentication
    "User",
    "AuthBackend",
    "DictAuthBackend",
    "SessionManager",
    "ApiKey",
    "ApiKeyManager",
    "require_auth",
    "get_global_auth_backend",
    # Caching
    "CacheBackend",
    "MemoryCache",
    "DiskCache",
    "cached",
    "get_global_cache_backend",
    # Background
    "Task",
    "TaskStatus",
    "TaskQueue",
    "background",
    "get_global_task_queue",
    # OpenAPI
    "generate_openapi_spec",
    "add_openapi_routes",
    "OpenAPIConfig",
    # Webhooks
    "WebhookEvent",
    "WebhookClient",
    "WebhookManager",
    "webhook",
    "get_global_webhook_manager",
    # Themes
    "Theme",
    "ThemeConfig",
    "get_theme",
    "LIGHT_THEME",
    "DARK_THEME",
]
```

## uf/async_support.py

```python
"""Async function support for uf.

Provides utilities for detecting and handling async functions,
allowing seamless integration of async def functions in uf apps.
"""

import asyncio
import inspect
from typing import Callable, Any
from functools import wraps


def is_async_function(func: Callable) -> bool:
    """Check if a function is async.

    Args:
        func: Function to check

    Returns:
        True if function is async

    Example:
        >>> async def my_async_func():
        ...     pass
        >>> is_async_function(my_async_func)
        True
    """
    return asyncio.iscoroutinefunction(func)


def async_to_sync(async_func: Callable) -> Callable:
    """Convert an async function to a synchronous wrapper.

    Args:
        async_func: Async function to wrap

    Returns:
        Synchronous wrapper function

    Example:
        >>> async def fetch_data(url: str):
        ...     # async operations
        ...     return data
        >>> sync_fetch = async_to_sync(fetch_data)
        >>> result = sync_fetch('https://example.com')
    """
    if not is_async_function(async_func):
        return async_func

    @wraps(async_func)
    def sync_wrapper(*args, **kwargs):
        """Synchronous wrapper that runs async function."""
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        async_func(*args, **kwargs)
                    )
                    return future.result()
            else:
                # Loop exists but not running
                return loop.run_until_complete(async_func(*args, **kwargs))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(async_func(*args, **kwargs))

    # Preserve metadata
    sync_wrapper.__uf_is_async__ = True
    sync_wrapper.__uf_original_async__ = async_func

    return sync_wrapper


def make_sync_compatible(funcs: list[Callable]) -> list[Callable]:
    """Convert any async functions in the list to sync wrappers.

    Args:
        funcs: List of functions (may include async)

    Returns:
        List of functions (all synchronous)

    Example:
        >>> funcs = [sync_func, async_func, another_sync]
        >>> compatible = make_sync_compatible(funcs)
        >>> # All functions in compatible are now callable synchronously
    """
    return [async_to_sync(func) for func in funcs]


def create_async_handler(async_func: Callable) -> Callable:
    """Create a handler for async functions in web frameworks.

    This is useful for integrating with frameworks that may or may not
    support async natively (like Bottle vs FastAPI).

    Args:
        async_func: Async function to create handler for

    Returns:
        Appropriate handler (async or sync wrapped)

    Example:
        >>> async def my_endpoint(param: str):
        ...     result = await some_async_operation(param)
        ...     return result
        >>> handler = create_async_handler(my_endpoint)
    """
    if not is_async_function(async_func):
        return async_func

    # For now, return sync wrapper
    # In future, could detect framework and return async if supported
    return async_to_sync(async_func)


class AsyncFunctionWrapper:
    """Wrapper for async functions that provides both sync and async access.

    This allows the same function to be called either way, depending on
    the context.

    Example:
        >>> async def fetch_user(user_id: int):
        ...     # async database query
        ...     return user_data
        >>>
        >>> wrapper = AsyncFunctionWrapper(fetch_user)
        >>> # Sync call
        >>> user = wrapper.call_sync(user_id=123)
        >>> # Async call
        >>> user = await wrapper.call_async(user_id=123)
    """

    def __init__(self, func: Callable):
        """Initialize the wrapper.

        Args:
            func: Function to wrap (sync or async)
        """
        self.func = func
        self.is_async = is_async_function(func)

    def call_sync(self, *args, **kwargs) -> Any:
        """Call the function synchronously.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result
        """
        if self.is_async:
            return async_to_sync(self.func)(*args, **kwargs)
        else:
            return self.func(*args, **kwargs)

    async def call_async(self, *args, **kwargs) -> Any:
        """Call the function asynchronously.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result
        """
        if self.is_async:
            return await self.func(*args, **kwargs)
        else:
            # Run sync function in executor to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: self.func(*args, **kwargs)
            )

    def __call__(self, *args, **kwargs):
        """Call synchronously by default.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result
        """
        return self.call_sync(*args, **kwargs)


def batch_async_calls(
    async_func: Callable,
    calls: list[dict],
) -> list[Any]:
    """Execute multiple async function calls concurrently.

    Args:
        async_func: Async function to call
        calls: List of dicts with 'args' and 'kwargs' for each call

    Returns:
        List of results in same order as calls

    Example:
        >>> async def fetch_user(user_id: int):
        ...     return await db.get_user(user_id)
        >>>
        >>> calls = [
        ...     {'args': (), 'kwargs': {'user_id': 1}},
        ...     {'args': (), 'kwargs': {'user_id': 2}},
        ...     {'args': (), 'kwargs': {'user_id': 3}},
        ... ]
        >>> users = batch_async_calls(fetch_user, calls)
    """
    if not is_async_function(async_func):
        # Sync function, just call sequentially
        return [
            async_func(*call.get('args', ()), **call.get('kwargs', {}))
            for call in calls
        ]

    async def run_batch():
        tasks = [
            async_func(*call.get('args', ()), **call.get('kwargs', {}))
            for call in calls
        ]
        return await asyncio.gather(*tasks)

    return asyncio.run(run_batch())


def timeout_async(seconds: float):
    """Decorator to add timeout to async functions.

    Args:
        seconds: Timeout in seconds

    Returns:
        Decorator function

    Example:
        >>> @timeout_async(5.0)
        ... async def slow_operation():
        ...     await asyncio.sleep(10)  # Will timeout after 5s
    """

    def decorator(async_func: Callable) -> Callable:
        if not is_async_function(async_func):
            return async_func

        @wraps(async_func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    async_func(*args, **kwargs),
                    timeout=seconds
                )
            except asyncio.TimeoutError:
                raise TimeoutError(
                    f"Function {async_func.__name__} "
                    f"timed out after {seconds} seconds"
                )

        return wrapper

    return decorator


def retry_async(max_attempts: int = 3, delay: float = 1.0):
    """Decorator to add retry logic to async functions.

    Args:
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds

    Returns:
        Decorator function

    Example:
        >>> @retry_async(max_attempts=3, delay=2.0)
        ... async def unreliable_api_call():
        ...     # May fail, will retry
        ...     return await external_api.fetch()
    """

    def decorator(async_func: Callable) -> Callable:
        if not is_async_function(async_func):
            return async_func

        @wraps(async_func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await async_func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay)
                    else:
                        raise last_exception

        return wrapper

    return decorator


class AsyncContext:
    """Context manager for handling async operations in uf.

    This helps manage event loops and async resources properly.

    Example:
        >>> with AsyncContext() as ctx:
        ...     result = ctx.run(my_async_function(param))
    """

    def __init__(self):
        """Initialize async context."""
        self._loop = None
        self._owned_loop = False

    def __enter__(self):
        """Enter the context."""
        try:
            self._loop = asyncio.get_event_loop()
            self._owned_loop = False
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._owned_loop = True

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context."""
        if self._owned_loop and self._loop:
            self._loop.close()

    def run(self, coro):
        """Run a coroutine in this context.

        Args:
            coro: Coroutine to run

        Returns:
            Result of the coroutine
        """
        if self._loop.is_running():
            # Can't run_until_complete on a running loop
            # Use asyncio.run in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return self._loop.run_until_complete(coro)


def detect_async_framework(app) -> str:
    """Detect if the web framework supports async natively.

    Args:
        app: The web application

    Returns:
        Framework name: 'fastapi', 'bottle', 'unknown'
    """
    app_type = type(app).__name__

    if 'FastAPI' in app_type:
        return 'fastapi'
    elif 'Bottle' in app_type or hasattr(app, 'route'):
        return 'bottle'
    else:
        return 'unknown'


def is_framework_async_capable(app) -> bool:
    """Check if the framework supports async handlers natively.

    Args:
        app: The web application

    Returns:
        True if framework supports async
    """
    framework = detect_async_framework(app)
    return framework in ['fastapi', 'aiohttp', 'starlette']
```

## uf/auth.py

```python
"""Authentication and authorization for uf.

Provides authentication backends, session management, and role-based
access control for uf applications.
"""

from typing import Callable, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import secrets
import hmac
from functools import wraps


@dataclass
class User:
    """User account information.

    Attributes:
        username: Unique username
        password_hash: Hashed password
        roles: List of role names
        permissions: List of permission strings
        metadata: Additional user metadata
        created_at: When user was created
        is_active: Whether account is active
    """

    username: str
    password_hash: str
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    def has_role(self, role: str) -> bool:
        """Check if user has a role."""
        return role in self.roles

    def has_permission(self, permission: str) -> bool:
        """Check if user has a permission."""
        return permission in self.permissions

    def has_any_role(self, roles: list[str]) -> bool:
        """Check if user has any of the given roles."""
        return any(role in self.roles for role in roles)

    def has_all_roles(self, roles: list[str]) -> bool:
        """Check if user has all of the given roles."""
        return all(role in self.roles for role in roles)


class PasswordHasher:
    """Password hashing utilities.

    Uses PBKDF2-HMAC-SHA256 for secure password hashing.
    """

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> str:
        """Hash a password.

        Args:
            password: Plain text password
            salt: Optional salt (generated if not provided)

        Returns:
            Hash string in format: salt$hash
        """
        if salt is None:
            salt = secrets.token_hex(16)

        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )

        return f"{salt}${pwd_hash.hex()}"

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash.

        Args:
            password: Plain text password
            password_hash: Hash string from hash_password()

        Returns:
            True if password matches
        """
        try:
            salt, stored_hash = password_hash.split('$')
            new_hash = PasswordHasher.hash_password(password, salt)
            return hmac.compare_digest(new_hash, password_hash)
        except ValueError:
            return False


class AuthBackend:
    """Base authentication backend.

    Subclass this to create custom authentication backends.
    """

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user.

        Args:
            username: Username
            password: Password

        Returns:
            User object if authenticated, None otherwise
        """
        raise NotImplementedError

    def get_user(self, username: str) -> Optional[User]:
        """Get a user by username.

        Args:
            username: Username

        Returns:
            User object or None
        """
        raise NotImplementedError

    def create_user(
        self,
        username: str,
        password: str,
        roles: Optional[list[str]] = None,
        permissions: Optional[list[str]] = None,
        **metadata
    ) -> User:
        """Create a new user.

        Args:
            username: Username
            password: Plain text password
            roles: List of roles
            permissions: List of permissions
            **metadata: Additional user metadata

        Returns:
            Created User object
        """
        raise NotImplementedError

    def update_user(self, username: str, **updates) -> bool:
        """Update user information.

        Args:
            username: Username
            **updates: Fields to update

        Returns:
            True if updated successfully
        """
        raise NotImplementedError

    def delete_user(self, username: str) -> bool:
        """Delete a user.

        Args:
            username: Username

        Returns:
            True if deleted successfully
        """
        raise NotImplementedError


class DictAuthBackend(AuthBackend):
    """Simple in-memory dictionary-based authentication.

    Suitable for development and simple applications.

    Example:
        >>> backend = DictAuthBackend()
        >>> backend.create_user('admin', 'secret', roles=['admin'])
        >>> user = backend.authenticate('admin', 'secret')
    """

    def __init__(self):
        """Initialize the backend."""
        self._users: dict[str, User] = {}
        self._hasher = PasswordHasher()

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user."""
        user = self._users.get(username)
        if not user or not user.is_active:
            return None

        if self._hasher.verify_password(password, user.password_hash):
            return user

        return None

    def get_user(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return self._users.get(username)

    def create_user(
        self,
        username: str,
        password: str,
        roles: Optional[list[str]] = None,
        permissions: Optional[list[str]] = None,
        **metadata
    ) -> User:
        """Create a new user."""
        if username in self._users:
            raise ValueError(f"User '{username}' already exists")

        password_hash = self._hasher.hash_password(password)

        user = User(
            username=username,
            password_hash=password_hash,
            roles=roles or [],
            permissions=permissions or [],
            metadata=metadata,
        )

        self._users[username] = user
        return user

    def update_user(self, username: str, **updates) -> bool:
        """Update user information."""
        user = self._users.get(username)
        if not user:
            return False

        for key, value in updates.items():
            if key == 'password':
                user.password_hash = self._hasher.hash_password(value)
            elif hasattr(user, key):
                setattr(user, key, value)

        return True

    def delete_user(self, username: str) -> bool:
        """Delete a user."""
        if username in self._users:
            del self._users[username]
            return True
        return False

    @classmethod
    def from_dict(cls, users_data: dict) -> 'DictAuthBackend':
        """Create backend from dictionary.

        Args:
            users_data: Dictionary mapping usernames to user info

        Example:
            >>> backend = DictAuthBackend.from_dict({
            ...     'admin': {'password': 'secret', 'roles': ['admin']},
            ...     'user': {'password': 'pass', 'roles': ['user']},
            ... })
        """
        backend = cls()
        hasher = PasswordHasher()

        for username, user_info in users_data.items():
            password = user_info.pop('password')
            password_hash = user_info.pop('password_hash', None)

            if password_hash is None:
                password_hash = hasher.hash_password(password)

            user = User(
                username=username,
                password_hash=password_hash,
                **user_info
            )
            backend._users[username] = user

        return backend


class SessionManager:
    """Manage user sessions.

    Example:
        >>> sessions = SessionManager(secret_key='my-secret')
        >>> session_id = sessions.create_session('admin')
        >>> user = sessions.get_session(session_id)
    """

    def __init__(self, secret_key: str, session_timeout: int = 3600):
        """Initialize session manager.

        Args:
            secret_key: Secret key for session signing
            session_timeout: Session timeout in seconds (default: 1 hour)
        """
        self.secret_key = secret_key
        self.session_timeout = session_timeout
        self._sessions: dict[str, dict] = {}

    def create_session(self, username: str, data: Optional[dict] = None) -> str:
        """Create a new session.

        Args:
            username: Username for session
            data: Optional session data

        Returns:
            Session ID
        """
        session_id = secrets.token_urlsafe(32)

        self._sessions[session_id] = {
            'username': username,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(seconds=self.session_timeout),
            'data': data or {},
        }

        return session_id

    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data.

        Args:
            session_id: Session ID

        Returns:
            Session data or None if expired/invalid
        """
        session = self._sessions.get(session_id)
        if not session:
            return None

        # Check expiration
        if datetime.now() > session['expires_at']:
            del self._sessions[session_id]
            return None

        return session

    def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session ID

        Returns:
            True if deleted
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def cleanup_expired(self) -> int:
        """Remove expired sessions.

        Returns:
            Number of sessions removed
        """
        now = datetime.now()
        expired = [
            sid for sid, session in self._sessions.items()
            if now > session['expires_at']
        ]

        for sid in expired:
            del self._sessions[sid]

        return len(expired)


class ApiKey:
    """API key for programmatic access.

    Attributes:
        key: The API key string
        name: Descriptive name
        permissions: List of allowed permissions
        created_at: When key was created
        expires_at: Optional expiration
        is_active: Whether key is active
    """

    def __init__(
        self,
        key: str,
        name: str,
        permissions: Optional[list[str]] = None,
        expires_at: Optional[datetime] = None,
    ):
        """Initialize API key."""
        self.key = key
        self.name = name
        self.permissions = permissions or []
        self.created_at = datetime.now()
        self.expires_at = expires_at
        self.is_active = True

    def is_expired(self) -> bool:
        """Check if key is expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def has_permission(self, permission: str) -> bool:
        """Check if key has permission."""
        return permission in self.permissions


class ApiKeyManager:
    """Manage API keys for programmatic access.

    Example:
        >>> api_keys = ApiKeyManager()
        >>> key = api_keys.create_key('mobile_app', permissions=['read'])
        >>> print(f"Your API key: {key.key}")
        >>> # Later, validate
        >>> if api_keys.validate_key(key.key, 'read'):
        ...     # Allow access
    """

    def __init__(self, key_prefix: str = 'sk_'):
        """Initialize API key manager.

        Args:
            key_prefix: Prefix for generated keys
        """
        self.key_prefix = key_prefix
        self._keys: dict[str, ApiKey] = {}

    def create_key(
        self,
        name: str,
        permissions: Optional[list[str]] = None,
        expires_in_days: Optional[int] = None,
    ) -> ApiKey:
        """Create a new API key.

        Args:
            name: Descriptive name for the key
            permissions: List of allowed permissions
            expires_in_days: Optional expiration in days

        Returns:
            Created ApiKey object
        """
        key_str = f"{self.key_prefix}{secrets.token_urlsafe(32)}"

        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)

        api_key = ApiKey(
            key=key_str,
            name=name,
            permissions=permissions,
            expires_at=expires_at,
        )

        self._keys[key_str] = api_key
        return api_key

    def validate_key(self, key: str, permission: Optional[str] = None) -> bool:
        """Validate an API key.

        Args:
            key: API key string
            permission: Optional permission to check

        Returns:
            True if valid
        """
        api_key = self._keys.get(key)
        if not api_key or not api_key.is_active:
            return False

        if api_key.is_expired():
            return False

        if permission and not api_key.has_permission(permission):
            return False

        return True

    def revoke_key(self, key: str) -> bool:
        """Revoke an API key.

        Args:
            key: API key string

        Returns:
            True if revoked
        """
        api_key = self._keys.get(key)
        if api_key:
            api_key.is_active = False
            return True
        return False

    def list_keys(self) -> list[ApiKey]:
        """List all API keys.

        Returns:
            List of ApiKey objects
        """
        return list(self._keys.values())


def require_auth(
    backend: AuthBackend,
    roles: Optional[list[str]] = None,
    permissions: Optional[list[str]] = None,
):
    """Decorator to require authentication for a function.

    Args:
        backend: Authentication backend
        roles: Required roles (any)
        permissions: Required permissions (all)

    Returns:
        Decorator function

    Example:
        >>> backend = DictAuthBackend.from_dict({
        ...     'admin': {'password': 'secret', 'roles': ['admin']}
        ... })
        >>> @require_auth(backend, roles=['admin'])
        ... def delete_all():
        ...     pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This is metadata-only in current implementation
            # Actual enforcement would require middleware integration
            return func(*args, **kwargs)

        wrapper.__uf_auth_required__ = True
        wrapper.__uf_auth_roles__ = roles or []
        wrapper.__uf_auth_permissions__ = permissions or []
        wrapper.__uf_auth_backend__ = backend

        return wrapper

    return decorator


# Global instances for convenience
_global_auth_backend: Optional[AuthBackend] = None
_global_session_manager: Optional[SessionManager] = None
_global_api_key_manager: Optional[ApiKeyManager] = None


def set_global_auth_backend(backend: AuthBackend) -> None:
    """Set the global authentication backend."""
    global _global_auth_backend
    _global_auth_backend = backend


def get_global_auth_backend() -> Optional[AuthBackend]:
    """Get the global authentication backend."""
    return _global_auth_backend


def set_global_session_manager(manager: SessionManager) -> None:
    """Set the global session manager."""
    global _global_session_manager
    _global_session_manager = manager


def get_global_session_manager() -> Optional[SessionManager]:
    """Get the global session manager."""
    return _global_session_manager


def set_global_api_key_manager(manager: ApiKeyManager) -> None:
    """Set the global API key manager."""
    global _global_api_key_manager
    _global_api_key_manager = manager


def get_global_api_key_manager() -> Optional[ApiKeyManager]:
    """Get the global API key manager."""
    return _global_api_key_manager
```

## uf/background.py

```python
"""Background task execution for uf.

Provides decorators and utilities for running tasks in the background,
with support for queues, scheduling, and progress tracking.
"""

from typing import Callable, Any, Optional
from functools import wraps
from datetime import datetime
from enum import Enum
import threading
import queue
import uuid


class TaskStatus(Enum):
    """Status of a background task."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    """Represents a background task.

    Attributes:
        task_id: Unique task identifier
        func_name: Name of the function
        args: Positional arguments
        kwargs: Keyword arguments
        status: Current task status
        result: Task result (if completed)
        error: Error message (if failed)
        created_at: When task was created
        started_at: When task started running
        completed_at: When task completed
        progress: Progress percentage (0-100)
    """

    def __init__(
        self,
        func: Callable,
        args: tuple = (),
        kwargs: Optional[dict] = None,
        task_id: Optional[str] = None,
    ):
        """Initialize task.

        Args:
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            task_id: Optional task ID (generated if not provided)
        """
        self.task_id = task_id or str(uuid.uuid4())
        self.func = func
        self.func_name = func.__name__
        self.args = args
        self.kwargs = kwargs or {}
        self.status = TaskStatus.PENDING
        self.result: Any = None
        self.error: Optional[str] = None
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.progress = 0

    def execute(self) -> Any:
        """Execute the task.

        Returns:
            Task result

        Raises:
            Exception: If task execution fails
        """
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()

        try:
            self.result = self.func(*self.args, **self.kwargs)
            self.status = TaskStatus.COMPLETED
            self.progress = 100
            return self.result
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.error = str(e)
            raise
        finally:
            self.completed_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert task to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'task_id': self.task_id,
            'func_name': self.func_name,
            'status': self.status.value,
            'result': self.result if self.status == TaskStatus.COMPLETED else None,
            'error': self.error,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'progress': self.progress,
        }


class TaskQueue:
    """FIFO queue for background tasks.

    Example:
        >>> task_queue = TaskQueue(num_workers=2)
        >>> task_queue.start()
        >>> task_id = task_queue.submit(expensive_function, x=10, y=20)
        >>> status = task_queue.get_status(task_id)
        >>> result = task_queue.get_result(task_id)
    """

    def __init__(self, num_workers: int = 1, max_queue_size: int = 100):
        """Initialize task queue.

        Args:
            num_workers: Number of worker threads
            max_queue_size: Maximum queue size
        """
        self.num_workers = num_workers
        self.max_queue_size = max_queue_size
        self._queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self._tasks: dict[str, Task] = {}
        self._workers: list[threading.Thread] = []
        self._running = False

    def start(self) -> None:
        """Start worker threads."""
        if self._running:
            return

        self._running = True

        for i in range(self.num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"TaskWorker-{i}",
                daemon=True,
            )
            worker.start()
            self._workers.append(worker)

    def stop(self, wait: bool = True) -> None:
        """Stop worker threads.

        Args:
            wait: Whether to wait for threads to finish
        """
        self._running = False

        if wait:
            for worker in self._workers:
                worker.join(timeout=5.0)

        self._workers.clear()

    def submit(
        self,
        func: Callable,
        *args,
        task_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Submit a task for execution.

        Args:
            func: Function to execute
            *args: Positional arguments
            task_id: Optional task ID
            **kwargs: Keyword arguments

        Returns:
            Task ID

        Raises:
            queue.Full: If queue is full
        """
        task = Task(func, args=args, kwargs=kwargs, task_id=task_id)
        self._tasks[task.task_id] = task
        self._queue.put(task, block=False)  # Don't block
        return task.task_id

    def get_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get task status.

        Args:
            task_id: Task ID

        Returns:
            TaskStatus or None if not found
        """
        task = self._tasks.get(task_id)
        return task.status if task else None

    def get_result(self, task_id: str, wait: bool = False, timeout: Optional[float] = None) -> Any:
        """Get task result.

        Args:
            task_id: Task ID
            wait: Whether to wait for completion
            timeout: Optional timeout in seconds

        Returns:
            Task result

        Raises:
            ValueError: If task not found
            RuntimeError: If task failed
            TimeoutError: If wait times out
        """
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        if wait and task.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            # Wait for completion
            import time
            start_time = time.time()
            while task.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                time.sleep(0.1)
                if timeout and (time.time() - start_time) > timeout:
                    raise TimeoutError(f"Task {task_id} timed out")

        if task.status == TaskStatus.FAILED:
            raise RuntimeError(f"Task failed: {task.error}")

        if task.status != TaskStatus.COMPLETED:
            return None

        return task.result

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task object.

        Args:
            task_id: Task ID

        Returns:
            Task object or None
        """
        return self._tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task.

        Args:
            task_id: Task ID

        Returns:
            True if cancelled

        Note:
            Can only cancel pending tasks
        """
        task = self._tasks.get(task_id)
        if not task or task.status != TaskStatus.PENDING:
            return False

        task.status = TaskStatus.CANCELLED
        return True

    def _worker_loop(self) -> None:
        """Worker thread loop."""
        while self._running:
            try:
                # Get task with timeout to allow checking _running
                task = self._queue.get(timeout=1.0)
            except queue.Empty:
                continue

            if task.status == TaskStatus.CANCELLED:
                continue

            try:
                task.execute()
            except Exception:
                # Error already recorded in task
                pass
            finally:
                self._queue.task_done()

    def queue_size(self) -> int:
        """Get current queue size.

        Returns:
            Number of pending tasks
        """
        return self._queue.qsize()

    def stats(self) -> dict:
        """Get queue statistics.

        Returns:
            Dictionary with statistics
        """
        total = len(self._tasks)
        by_status = {}
        for task in self._tasks.values():
            status = task.status.value
            by_status[status] = by_status.get(status, 0) + 1

        return {
            'total_tasks': total,
            'queue_size': self.queue_size(),
            'num_workers': self.num_workers,
            'by_status': by_status,
        }


def background(
    queue_name: str = 'default',
    task_queue: Optional[TaskQueue] = None,
):
    """Decorator to run function in background.

    Args:
        queue_name: Name of the queue to use
        task_queue: Optional TaskQueue instance

    Returns:
        Decorator function

    Example:
        >>> @background()
        ... def send_email(to: str, subject: str):
        ...     # Long-running email sending
        ...     pass
        >>>
        >>> task_id = send_email('user@example.com', 'Hello')
        >>> # Returns immediately with task_id
    """
    if task_queue is None:
        task_queue = get_global_task_queue(queue_name)
        if task_queue is None:
            task_queue = TaskQueue(num_workers=2)
            task_queue.start()
            set_global_task_queue(queue_name, task_queue)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            """Submit task and return task ID."""
            task_id = task_queue.submit(func, *args, **kwargs)
            return task_id

        wrapper.__uf_background__ = True
        wrapper.__uf_task_queue__ = task_queue
        wrapper.__uf_original_func__ = func

        # Add utility methods
        def get_status(task_id: str):
            """Get task status."""
            return task_queue.get_status(task_id)

        def get_result(task_id: str, wait: bool = False, timeout: Optional[float] = None):
            """Get task result."""
            return task_queue.get_result(task_id, wait=wait, timeout=timeout)

        wrapper.get_status = get_status
        wrapper.get_result = get_result

        return wrapper

    return decorator


class PeriodicTask:
    """Task that runs periodically.

    Example:
        >>> def cleanup():
        ...     print("Cleaning up...")
        >>>
        >>> periodic = PeriodicTask(cleanup, interval=3600)
        >>> periodic.start()
        >>> # Runs every hour
        >>> periodic.stop()
    """

    def __init__(self, func: Callable, interval: float, args: tuple = (), kwargs: Optional[dict] = None):
        """Initialize periodic task.

        Args:
            func: Function to run
            interval: Interval in seconds
            args: Positional arguments
            kwargs: Keyword arguments
        """
        self.func = func
        self.interval = interval
        self.args = args
        self.kwargs = kwargs or {}
        self._timer: Optional[threading.Timer] = None
        self._running = False

    def start(self) -> None:
        """Start periodic execution."""
        if self._running:
            return

        self._running = True
        self._schedule_next()

    def stop(self) -> None:
        """Stop periodic execution."""
        self._running = False
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def _schedule_next(self) -> None:
        """Schedule next execution."""
        if not self._running:
            return

        self._timer = threading.Timer(self.interval, self._run)
        self._timer.daemon = True
        self._timer.start()

    def _run(self) -> None:
        """Run the function and schedule next."""
        try:
            self.func(*self.args, **self.kwargs)
        except Exception:
            # Log error but continue
            pass
        finally:
            self._schedule_next()


# Global task queues
_global_task_queues: dict[str, TaskQueue] = {}


def get_global_task_queue(name: str = 'default') -> Optional[TaskQueue]:
    """Get a global task queue by name.

    Args:
        name: Queue name

    Returns:
        TaskQueue or None
    """
    return _global_task_queues.get(name)


def set_global_task_queue(name: str, task_queue: TaskQueue) -> None:
    """Set a global task queue.

    Args:
        name: Queue name
        task_queue: TaskQueue instance
    """
    _global_task_queues[name] = task_queue


def get_or_create_task_queue(name: str = 'default', num_workers: int = 2) -> TaskQueue:
    """Get or create a task queue.

    Args:
        name: Queue name
        num_workers: Number of workers if creating

    Returns:
        TaskQueue instance
    """
    queue = get_global_task_queue(name)
    if queue is None:
        queue = TaskQueue(num_workers=num_workers)
        queue.start()
        set_global_task_queue(name, queue)
    return queue
```

## uf/base.py

```python
"""Core functionality for uf - UI Fast.

This module provides the main `mk_rjsf_app` function that bridges:
- Functions → HTTP services (via qh)
- HTTP services → Web UI forms (via ju.rjsf)

Following the "convention over configuration" philosophy, it provides sensible
defaults while allowing customization where needed.
"""

from typing import Callable, Iterable, Optional, Any, Mapping as MappingType
from uf.specs import FunctionSpecStore
from uf.routes import add_ui_routes


def mk_rjsf_app(
    funcs: Iterable[Callable],
    *,
    # qh-related kwargs
    config: Optional[Any] = None,
    input_trans: Optional[Callable] = None,
    output_trans: Optional[Callable] = None,
    # rjsf-related kwargs
    rjsf_config: Optional[dict] = None,
    ui_schema_factory: Optional[Callable] = None,
    param_to_prop_type: Optional[Callable] = None,
    # uf-specific kwargs
    page_title: str = "Function Interface",
    function_display_names: Optional[MappingType] = None,
    custom_css: Optional[str] = None,
    rjsf_theme: str = "default",
    add_ui: bool = True,
    **qh_kwargs,
):
    """Create an RJSF-backed web app from a list of functions.

    This is the main entry point for uf. It combines qh's HTTP service
    generation with ju's RJSF form generation to create a complete
    web interface for your functions.

    Args:
        funcs: Iterable of callable functions to expose via web UI
        config: Optional qh.AppConfig for HTTP service configuration
        input_trans: Optional input transformation function for qh
        output_trans: Optional output transformation function for qh
        rjsf_config: Optional configuration dict for RJSF generation
        ui_schema_factory: Optional callable to customize UI schema
        param_to_prop_type: Optional callable to map parameters to types
        page_title: Title for the web interface
        function_display_names: Optional mapping to override function names
        custom_css: Optional custom CSS for the web interface
        rjsf_theme: RJSF theme to use ('default', 'material-ui', etc.)
        add_ui: Whether to add UI routes (set False for API-only)
        **qh_kwargs: Additional keyword arguments passed to qh.mk_app

    Returns:
        A configured web application (bottle or FastAPI app) with:
        - HTTP endpoints for each function
        - RJSF-based web interface (if add_ui=True)
        - API routes for function specs

    Example:
        >>> def add(x: int, y: int) -> int:
        ...     '''Add two numbers'''
        ...     return x + y
        ...
        >>> def greet(name: str) -> str:
        ...     '''Greet a person'''
        ...     return f"Hello, {name}!"
        ...
        >>> app = mk_rjsf_app([add, greet])
        >>> # app.run()  # Start the web server

    Example with customization:
        >>> from uf import mk_rjsf_app, RjsfFieldConfig
        >>>
        >>> def send_email(to: str, subject: str, body: str):
        ...     '''Send an email'''
        ...     pass
        ...
        >>> app = mk_rjsf_app(
        ...     [send_email],
        ...     page_title="Email Sender",
        ...     custom_css="body { background: #f0f0f0; }",
        ... )
    """
    # Convert to list to allow multiple iterations
    funcs = list(funcs)

    # Create function specification store
    function_specs = FunctionSpecStore(
        funcs,
        rjsf_config=rjsf_config or {},
        ui_schema_factory=ui_schema_factory,
        param_to_prop_type=param_to_prop_type,
    )

    # Create HTTP service using qh
    try:
        from qh import mk_app
    except ImportError:
        raise ImportError(
            "qh is required for mk_rjsf_app. Install it with: pip install qh"
        )

    # Build the qh app with function endpoints
    app = mk_app(
        funcs,
        config=config,
        input_trans=input_trans,
        output_trans=output_trans,
        **qh_kwargs,
    )

    # Store function_specs on the app for later access
    app.function_specs = function_specs

    # Add UI routes if requested
    if add_ui:
        add_ui_routes(
            app,
            function_specs,
            page_title=page_title,
            custom_css=custom_css,
            rjsf_theme=rjsf_theme,
        )

    return app


class UfApp:
    """Wrapper class for uf applications.

    Provides a higher-level interface with additional conveniences
    beyond the raw qh app.

    Attributes:
        app: The underlying qh/bottle/fastapi app
        function_specs: FunctionSpecStore for function metadata
        funcs: Dictionary mapping function names to callables
    """

    def __init__(
        self,
        funcs: Iterable[Callable],
        **mk_rjsf_app_kwargs,
    ):
        """Initialize UfApp.

        Args:
            funcs: Iterable of callable functions
            **mk_rjsf_app_kwargs: Arguments passed to mk_rjsf_app
        """
        self.funcs = {f.__name__: f for f in funcs}
        self.app = mk_rjsf_app(list(self.funcs.values()), **mk_rjsf_app_kwargs)
        self.function_specs = self.app.function_specs

    def run(self, host: str = 'localhost', port: int = 8080, **kwargs):
        """Run the web application.

        Args:
            host: Host to bind to
            port: Port to listen on
            **kwargs: Additional arguments passed to app.run()
        """
        if hasattr(self.app, 'run'):
            # Bottle app
            self.app.run(host=host, port=port, **kwargs)
        else:
            # FastAPI or other - provide guidance
            raise NotImplementedError(
                "For FastAPI apps, use: uvicorn.run(app.app, host='...', port=...)"
            )

    def call(self, func_name: str, **kwargs) -> Any:
        """Call a function directly by name.

        Args:
            func_name: Name of the function to call
            **kwargs: Arguments to pass to the function

        Returns:
            Result of the function call

        Raises:
            KeyError: If function name not found
        """
        if func_name not in self.funcs:
            raise KeyError(f"Function '{func_name}' not found")
        return self.funcs[func_name](**kwargs)

    def get_spec(self, func_name: str) -> dict:
        """Get RJSF specification for a function.

        Args:
            func_name: Name of the function

        Returns:
            Dictionary with schema and uiSchema

        Raises:
            KeyError: If function name not found
        """
        return self.function_specs[func_name]

    def list_functions(self) -> list[str]:
        """Get list of all function names.

        Returns:
            List of function name strings
        """
        return list(self.funcs.keys())

    def __repr__(self):
        """String representation of UfApp."""
        func_names = ', '.join(self.list_functions())
        return f"UfApp({func_names})"
```

## uf/caching.py

```python
"""Result caching for uf.

Provides caching decorators and backends to cache function results,
improving performance for expensive operations.
"""

from typing import Callable, Any, Optional, Hashable
from functools import wraps
from datetime import datetime, timedelta
import json
import hashlib
import pickle


class CacheBackend:
    """Base class for cache backends."""

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        raise NotImplementedError

    def delete(self, key: str) -> bool:
        """Delete a key from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted
        """
        raise NotImplementedError

    def clear(self) -> None:
        """Clear all cache entries."""
        raise NotImplementedError

    def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if exists and not expired
        """
        return self.get(key) is not None


class MemoryCache(CacheBackend):
    """In-memory cache backend.

    Simple dictionary-based caching suitable for single-process applications.

    Example:
        >>> cache = MemoryCache(default_ttl=3600)
        >>> cache.set('key', 'value', ttl=60)
        >>> value = cache.get('key')
    """

    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        """Initialize memory cache.

        Args:
            default_ttl: Default TTL in seconds
            max_size: Maximum number of entries
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: dict[str, dict] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        entry = self._cache.get(key)
        if not entry:
            return None

        # Check expiration
        if entry['expires_at'] and datetime.now() > entry['expires_at']:
            del self._cache[key]
            return None

        return entry['value']

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in cache."""
        if ttl is None:
            ttl = self.default_ttl

        expires_at = None
        if ttl > 0:
            expires_at = datetime.now() + timedelta(seconds=ttl)

        self._cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.now(),
        }

        # Evict oldest entries if over max size
        if len(self._cache) > self.max_size:
            self._evict_oldest()

    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    def _evict_oldest(self) -> None:
        """Evict oldest entries to fit max size."""
        # Sort by created_at and remove oldest 10%
        sorted_keys = sorted(
            self._cache.keys(),
            key=lambda k: self._cache[k]['created_at']
        )

        num_to_remove = max(1, len(self._cache) // 10)
        for key in sorted_keys[:num_to_remove]:
            del self._cache[key]

    def cleanup_expired(self) -> int:
        """Remove expired entries.

        Returns:
            Number of entries removed
        """
        now = datetime.now()
        expired = [
            key for key, entry in self._cache.items()
            if entry['expires_at'] and now > entry['expires_at']
        ]

        for key in expired:
            del self._cache[key]

        return len(expired)

    def stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        total = len(self._cache)
        now = datetime.now()
        expired = sum(
            1 for entry in self._cache.values()
            if entry['expires_at'] and now > entry['expires_at']
        )

        return {
            'total_entries': total,
            'active_entries': total - expired,
            'expired_entries': expired,
            'max_size': self.max_size,
            'utilization': total / self.max_size if self.max_size > 0 else 0,
        }


class DiskCache(CacheBackend):
    """Disk-based cache backend using pickle.

    Persists cache to disk, suitable for larger datasets or persistence
    across restarts.

    Example:
        >>> cache = DiskCache(cache_dir='/tmp/uf_cache')
        >>> cache.set('expensive_result', big_data)
    """

    def __init__(self, cache_dir: str = '.uf_cache', default_ttl: int = 3600):
        """Initialize disk cache.

        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default TTL in seconds
        """
        import os
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl

        os.makedirs(cache_dir, exist_ok=True)

    def _get_path(self, key: str) -> str:
        """Get file path for a key."""
        import os
        # Hash the key to create valid filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.cache")

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        import os

        path = self._get_path(key)
        if not os.path.exists(path):
            return None

        try:
            with open(path, 'rb') as f:
                entry = pickle.load(f)

            # Check expiration
            if entry['expires_at'] and datetime.now() > entry['expires_at']:
                os.remove(path)
                return None

            return entry['value']
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in cache."""
        if ttl is None:
            ttl = self.default_ttl

        expires_at = None
        if ttl > 0:
            expires_at = datetime.now() + timedelta(seconds=ttl)

        entry = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.now(),
        }

        path = self._get_path(key)
        with open(path, 'wb') as f:
            pickle.dump(entry, f)

    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        import os

        path = self._get_path(key)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        import os
        import glob

        for file_path in glob.glob(os.path.join(self.cache_dir, '*.cache')):
            os.remove(file_path)


def make_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """Create a cache key from function call.

    Args:
        func_name: Function name
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Cache key string
    """
    # Create a deterministic key from arguments
    key_data = {
        'func': func_name,
        'args': args,
        'kwargs': sorted(kwargs.items()),
    }

    # Serialize to JSON for hashing
    try:
        key_str = json.dumps(key_data, sort_keys=True, default=str)
    except (TypeError, ValueError):
        # Fallback to string representation
        key_str = f"{func_name}:{args}:{sorted(kwargs.items())}"

    # Hash for compact key
    return hashlib.sha256(key_str.encode()).hexdigest()


def cached(
    ttl: int = 3600,
    backend: Optional[CacheBackend] = None,
    key_func: Optional[Callable] = None,
):
    """Decorator to cache function results.

    Args:
        ttl: Time to live in seconds
        backend: Cache backend (uses global MemoryCache if None)
        key_func: Optional function to generate cache key

    Returns:
        Decorator function

    Example:
        >>> @cached(ttl=3600)
        ... def expensive_calculation(x: int, y: int) -> int:
        ...     # Only runs once per unique (x, y) combination
        ...     return heavy_computation(x, y)
        >>>
        >>> result = expensive_calculation(10, 20)  # Computes
        >>> result2 = expensive_calculation(10, 20)  # From cache
    """
    if backend is None:
        backend = get_global_cache_backend()
        if backend is None:
            backend = MemoryCache(default_ttl=ttl)
            set_global_cache_backend(backend)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = make_cache_key(func.__name__, args, kwargs)

            # Try to get from cache
            cached_result = backend.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Compute result
            result = func(*args, **kwargs)

            # Store in cache
            backend.set(cache_key, result, ttl=ttl)

            return result

        wrapper.__uf_cached__ = True
        wrapper.__uf_cache_backend__ = backend
        wrapper.__uf_cache_ttl__ = ttl

        # Add cache control methods
        def clear_cache():
            """Clear all cached results for this function."""
            # This is a simplified version
            # Full implementation would track keys per function
            backend.clear()

        wrapper.clear_cache = clear_cache

        return wrapper

    return decorator


def cache_invalidate(cache_key: str, backend: Optional[CacheBackend] = None) -> bool:
    """Invalidate a specific cache entry.

    Args:
        cache_key: Cache key to invalidate
        backend: Cache backend (uses global if None)

    Returns:
        True if invalidated
    """
    if backend is None:
        backend = get_global_cache_backend()

    if backend:
        return backend.delete(cache_key)

    return False


def cache_clear_all(backend: Optional[CacheBackend] = None) -> None:
    """Clear all cache entries.

    Args:
        backend: Cache backend (uses global if None)
    """
    if backend is None:
        backend = get_global_cache_backend()

    if backend:
        backend.clear()


class CacheStats:
    """Track cache hit/miss statistics."""

    def __init__(self):
        """Initialize cache stats."""
        self.hits = 0
        self.misses = 0
        self.sets = 0

    def record_hit(self):
        """Record a cache hit."""
        self.hits += 1

    def record_miss(self):
        """Record a cache miss."""
        self.misses += 1

    def record_set(self):
        """Record a cache set."""
        self.sets += 1

    def hit_rate(self) -> float:
        """Calculate hit rate.

        Returns:
            Hit rate as a percentage (0-100)
        """
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100

    def reset(self):
        """Reset all statistics."""
        self.hits = 0
        self.misses = 0
        self.sets = 0

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Statistics dictionary
        """
        return {
            'hits': self.hits,
            'misses': self.misses,
            'sets': self.sets,
            'hit_rate': self.hit_rate(),
            'total_requests': self.hits + self.misses,
        }


# Global cache backend
_global_cache_backend: Optional[CacheBackend] = None


def set_global_cache_backend(backend: CacheBackend) -> None:
    """Set the global cache backend."""
    global _global_cache_backend
    _global_cache_backend = backend


def get_global_cache_backend() -> Optional[CacheBackend]:
    """Get the global cache backend."""
    return _global_cache_backend


# Initialize default global backend
set_global_cache_backend(MemoryCache())
```

## uf/decorators.py

```python
"""UI metadata decorators for uf.

Provides decorators for annotating functions with UI configuration,
grouping, and field specifications.
"""

from typing import Callable, Optional, Any
from functools import wraps
from uf.rjsf_config import RjsfFieldConfig


# Attribute names for storing metadata
_UI_CONFIG_ATTR = '__uf_ui_config__'
_GROUP_ATTR = '__uf_group__'
_FIELD_CONFIGS_ATTR = '__uf_field_configs__'
_HIDDEN_ATTR = '__uf_hidden__'


def ui_config(
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
    group: Optional[str] = None,
    fields: Optional[dict[str, RjsfFieldConfig]] = None,
    hidden: bool = False,
    icon: Optional[str] = None,
    order: Optional[int] = None,
):
    """Decorator to add UI configuration to functions.

    This decorator attaches metadata to functions that uf can use to
    customize the generated UI.

    Args:
        title: Custom title for the function in UI
        description: Custom description (overrides docstring)
        group: Group name for organization
        fields: Dictionary mapping parameter names to RjsfFieldConfig
        hidden: Whether to hide this function from UI
        icon: Icon identifier for the function
        order: Display order within group

    Returns:
        Decorator function

    Example:
        >>> @ui_config(
        ...     title="User Registration",
        ...     group="Admin",
        ...     fields={'email': RjsfFieldConfig(format='email')}
        ... )
        ... def register_user(email: str, name: str):
        ...     pass
    """

    def decorator(func: Callable) -> Callable:
        config = {
            'title': title,
            'description': description,
            'group': group,
            'fields': fields or {},
            'hidden': hidden,
            'icon': icon,
            'order': order if order is not None else 0,
        }

        setattr(func, _UI_CONFIG_ATTR, config)

        # Also set group attribute for auto-grouping
        if group:
            setattr(func, _GROUP_ATTR, group)

        # Set hidden attribute
        if hidden:
            setattr(func, _HIDDEN_ATTR, True)

        # Set field configs
        if fields:
            setattr(func, _FIELD_CONFIGS_ATTR, fields)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Copy metadata to wrapper
        setattr(wrapper, _UI_CONFIG_ATTR, config)
        if group:
            setattr(wrapper, _GROUP_ATTR, group)
        if hidden:
            setattr(wrapper, _HIDDEN_ATTR, True)
        if fields:
            setattr(wrapper, _FIELD_CONFIGS_ATTR, fields)

        return wrapper

    return decorator


def group(group_name: str):
    """Decorator to assign a function to a group.

    Simpler alternative to ui_config when you only need to set the group.

    Args:
        group_name: Name of the group

    Returns:
        Decorator function

    Example:
        >>> @group("Admin")
        ... def delete_user(user_id: int):
        ...     pass
    """
    return ui_config(group=group_name)


def hidden(func: Callable) -> Callable:
    """Decorator to hide a function from the UI.

    The function will still be callable via the API but won't appear
    in the UI navigation.

    Args:
        func: Function to hide

    Returns:
        Decorated function

    Example:
        >>> @hidden
        ... def internal_function():
        ...     pass
    """
    return ui_config(hidden=True)(func)


def field_config(**field_configs: RjsfFieldConfig):
    """Decorator to configure specific fields of a function.

    Args:
        **field_configs: Keyword arguments mapping parameter names to configs

    Returns:
        Decorator function

    Example:
        >>> from uf.rjsf_config import get_field_config
        >>>
        >>> @field_config(
        ...     email=get_field_config('email'),
        ...     bio=get_field_config('multiline_text')
        ... )
        ... def create_profile(email: str, bio: str):
        ...     pass
    """
    return ui_config(fields=field_configs)


def get_ui_config(func: Callable) -> Optional[dict]:
    """Get UI configuration from a function.

    Args:
        func: Function to get config from

    Returns:
        Configuration dictionary or None if not configured

    Example:
        >>> config = get_ui_config(my_function)
        >>> if config:
        ...     print(config['title'])
    """
    return getattr(func, _UI_CONFIG_ATTR, None)


def get_group(func: Callable) -> Optional[str]:
    """Get group name from a function.

    Args:
        func: Function to get group from

    Returns:
        Group name or None

    Example:
        >>> group = get_group(my_function)
        >>> if group:
        ...     print(f"Function is in group: {group}")
    """
    config = get_ui_config(func)
    if config:
        return config.get('group')
    return getattr(func, _GROUP_ATTR, None)


def get_field_configs(func: Callable) -> dict[str, RjsfFieldConfig]:
    """Get field configurations from a function.

    Args:
        func: Function to get field configs from

    Returns:
        Dictionary mapping parameter names to RjsfFieldConfig

    Example:
        >>> field_configs = get_field_configs(my_function)
        >>> if 'email' in field_configs:
        ...     print(field_configs['email'].format)
    """
    config = get_ui_config(func)
    if config:
        return config.get('fields', {})
    return getattr(func, _FIELD_CONFIGS_ATTR, {})


def is_hidden(func: Callable) -> bool:
    """Check if a function is hidden from UI.

    Args:
        func: Function to check

    Returns:
        True if function is hidden, False otherwise

    Example:
        >>> if not is_hidden(my_function):
        ...     # Show in UI
        ...     pass
    """
    config = get_ui_config(func)
    if config:
        return config.get('hidden', False)
    return getattr(func, _HIDDEN_ATTR, False)


def with_example(*example_args, **example_kwargs):
    """Decorator to attach example arguments to a function.

    This can be used to provide example/test data that appears in the UI.

    Args:
        *example_args: Example positional arguments
        **example_kwargs: Example keyword arguments

    Returns:
        Decorator function

    Example:
        >>> @with_example(x=10, y=20)
        ... def add(x: int, y: int) -> int:
        ...     return x + y
    """

    def decorator(func: Callable) -> Callable:
        setattr(func, '__uf_example_args__', example_args)
        setattr(func, '__uf_example_kwargs__', example_kwargs)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, '__uf_example_args__', example_args)
        setattr(wrapper, '__uf_example_kwargs__', example_kwargs)

        return wrapper

    return decorator


def get_example(func: Callable) -> Optional[tuple[tuple, dict]]:
    """Get example arguments from a function.

    Args:
        func: Function to get example from

    Returns:
        Tuple of (args, kwargs) or None if no example

    Example:
        >>> example = get_example(my_function)
        >>> if example:
        ...     args, kwargs = example
        ...     result = my_function(*args, **kwargs)
    """
    args = getattr(func, '__uf_example_args__', None)
    kwargs = getattr(func, '__uf_example_kwargs__', None)

    if args is not None or kwargs is not None:
        return (args or (), kwargs or {})

    return None


def deprecated(message: Optional[str] = None):
    """Decorator to mark a function as deprecated.

    Args:
        message: Optional deprecation message

    Returns:
        Decorator function

    Example:
        >>> @deprecated("Use new_function instead")
        ... def old_function():
        ...     pass
    """

    def decorator(func: Callable) -> Callable:
        setattr(func, '__uf_deprecated__', True)
        setattr(func, '__uf_deprecated_message__', message)

        @wraps(func)
        def wrapper(*args, **kwargs):
            import warnings

            msg = message or f"{func.__name__} is deprecated"
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        setattr(wrapper, '__uf_deprecated__', True)
        setattr(wrapper, '__uf_deprecated_message__', message)

        return wrapper

    return decorator


def requires_auth(
    *,
    roles: Optional[list[str]] = None,
    permissions: Optional[list[str]] = None,
):
    """Decorator to mark a function as requiring authentication.

    This is metadata-only; actual authentication must be implemented
    separately in the application layer.

    Args:
        roles: List of required roles
        permissions: List of required permissions

    Returns:
        Decorator function

    Example:
        >>> @requires_auth(roles=['admin'], permissions=['user:delete'])
        ... def delete_user(user_id: int):
        ...     pass
    """

    def decorator(func: Callable) -> Callable:
        setattr(func, '__uf_requires_auth__', True)
        setattr(func, '__uf_required_roles__', roles or [])
        setattr(func, '__uf_required_permissions__', permissions or [])

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, '__uf_requires_auth__', True)
        setattr(wrapper, '__uf_required_roles__', roles or [])
        setattr(wrapper, '__uf_required_permissions__', permissions or [])

        return wrapper

    return decorator


def rate_limit(calls: int, period: int):
    """Decorator to mark a function with rate limiting metadata.

    This is metadata-only; actual rate limiting must be implemented
    separately.

    Args:
        calls: Number of calls allowed
        period: Time period in seconds

    Returns:
        Decorator function

    Example:
        >>> @rate_limit(calls=10, period=60)  # 10 calls per minute
        ... def send_email(to: str, subject: str):
        ...     pass
    """

    def decorator(func: Callable) -> Callable:
        setattr(func, '__uf_rate_limit__', {'calls': calls, 'period': period})

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, '__uf_rate_limit__', {'calls': calls, 'period': period})

        return wrapper

    return decorator
```

## uf/field_interactions.py

```python
"""Field dependencies and interactions for uf.

Provides tools for defining relationships between form fields, such as
conditional display, dynamic validation, and field dependencies.
"""

from typing import Callable, Optional, Any, Literal
from dataclasses import dataclass
from enum import Enum


class DependencyAction(Enum):
    """Actions that can be triggered by field dependencies."""

    SHOW = "show"  # Show the target field
    HIDE = "hide"  # Hide the target field
    ENABLE = "enable"  # Enable the target field
    DISABLE = "disable"  # Disable the target field
    REQUIRE = "require"  # Make the target field required
    OPTIONAL = "optional"  # Make the target field optional


@dataclass
class FieldDependency:
    """Define a dependency between form fields.

    Attributes:
        source_field: Name of the field that triggers the dependency
        target_field: Name of the field affected by the dependency
        condition: Function that takes source value and returns bool
        action: Action to perform when condition is true
        else_action: Optional action when condition is false

    Example:
        >>> # Show 'other_reason' only when reason is 'other'
        >>> dep = FieldDependency(
        ...     source_field='reason',
        ...     target_field='other_reason',
        ...     condition=lambda v: v == 'other',
        ...     action=DependencyAction.SHOW,
        ...     else_action=DependencyAction.HIDE
        ... )
    """

    source_field: str
    target_field: str
    condition: Callable[[Any], bool]
    action: DependencyAction
    else_action: Optional[DependencyAction] = None

    def check(self, value: Any) -> DependencyAction:
        """Check the condition and return the appropriate action.

        Args:
            value: Value of the source field

        Returns:
            The action to perform
        """
        if self.condition(value):
            return self.action
        elif self.else_action:
            return self.else_action
        else:
            # Return opposite action if no else_action specified
            opposites = {
                DependencyAction.SHOW: DependencyAction.HIDE,
                DependencyAction.HIDE: DependencyAction.SHOW,
                DependencyAction.ENABLE: DependencyAction.DISABLE,
                DependencyAction.DISABLE: DependencyAction.ENABLE,
                DependencyAction.REQUIRE: DependencyAction.OPTIONAL,
                DependencyAction.OPTIONAL: DependencyAction.REQUIRE,
            }
            return opposites.get(self.action, self.action)

    def to_json_schema(self) -> dict:
        """Convert to JSON Schema dependencies format.

        Returns:
            JSON Schema dependencies structure

        Note:
            This uses JSON Schema's if/then/else structure for dependencies.
        """
        # Build condition schema
        if callable(self.condition):
            # For callable conditions, we need to handle specific cases
            # This is a simplified version - complex conditions may need custom handling
            condition_schema = {'properties': {self.source_field: {}}}
        else:
            condition_schema = self.condition

        # Build then/else schemas based on actions
        then_schema = self._action_to_schema(self.action)
        else_schema = (
            self._action_to_schema(self.else_action) if self.else_action else None
        )

        result = {'if': condition_schema}

        if then_schema:
            result['then'] = then_schema

        if else_schema:
            result['else'] = else_schema

        return result

    def _action_to_schema(self, action: DependencyAction) -> dict:
        """Convert action to JSON Schema modification.

        Args:
            action: The dependency action

        Returns:
            Schema modification dict
        """
        if action == DependencyAction.SHOW:
            # In JSON Schema, showing is the default, hiding uses uiSchema
            return {}
        elif action == DependencyAction.HIDE:
            return {}
        elif action == DependencyAction.REQUIRE:
            return {'required': [self.target_field]}
        elif action == DependencyAction.OPTIONAL:
            return {}
        else:
            return {}

    def to_ui_schema(self) -> dict:
        """Convert to RJSF UI Schema dependencies format.

        Returns:
            UI Schema dependencies structure
        """
        # UI Schema handles widget-level interactions
        ui_deps = {}

        if self.action == DependencyAction.HIDE:
            ui_deps[self.target_field] = {'ui:widget': 'hidden'}
        elif self.action == DependencyAction.DISABLE:
            ui_deps[self.target_field] = {'ui:disabled': True}

        return ui_deps


class DependencyBuilder:
    """Builder for creating field dependencies.

    Provides a fluent interface for defining dependencies between fields.

    Example:
        >>> builder = DependencyBuilder()
        >>> builder.when('reason').equals('other').show('other_reason')
        >>> builder.when('age').greater_than(18).enable('alcohol_consent')
        >>> dependencies = builder.build()
    """

    def __init__(self):
        """Initialize the dependency builder."""
        self._dependencies: list[FieldDependency] = []
        self._current_field: Optional[str] = None
        self._current_condition: Optional[Callable] = None

    def when(self, field_name: str) -> 'DependencyBuilder':
        """Start a dependency condition on a field.

        Args:
            field_name: Name of the source field

        Returns:
            Self for method chaining
        """
        self._current_field = field_name
        self._current_condition = None
        return self

    def equals(self, value: Any) -> 'DependencyBuilder':
        """Condition: field equals value.

        Args:
            value: Value to compare against

        Returns:
            Self for method chaining
        """
        self._current_condition = lambda v: v == value
        return self

    def not_equals(self, value: Any) -> 'DependencyBuilder':
        """Condition: field does not equal value.

        Args:
            value: Value to compare against

        Returns:
            Self for method chaining
        """
        self._current_condition = lambda v: v != value
        return self

    def greater_than(self, value: Any) -> 'DependencyBuilder':
        """Condition: field is greater than value.

        Args:
            value: Value to compare against

        Returns:
            Self for method chaining
        """
        self._current_condition = lambda v: v > value
        return self

    def less_than(self, value: Any) -> 'DependencyBuilder':
        """Condition: field is less than value.

        Args:
            value: Value to compare against

        Returns:
            Self for method chaining
        """
        self._current_condition = lambda v: v < value
        return self

    def is_truthy(self) -> 'DependencyBuilder':
        """Condition: field is truthy.

        Returns:
            Self for method chaining
        """
        self._current_condition = lambda v: bool(v)
        return self

    def is_falsy(self) -> 'DependencyBuilder':
        """Condition: field is falsy.

        Returns:
            Self for method chaining
        """
        self._current_condition = lambda v: not bool(v)
        return self

    def in_list(self, values: list) -> 'DependencyBuilder':
        """Condition: field value is in list.

        Args:
            values: List of acceptable values

        Returns:
            Self for method chaining
        """
        self._current_condition = lambda v: v in values
        return self

    def custom(self, condition: Callable[[Any], bool]) -> 'DependencyBuilder':
        """Condition: custom callable.

        Args:
            condition: Function that takes value and returns bool

        Returns:
            Self for method chaining
        """
        self._current_condition = condition
        return self

    def show(self, target_field: str) -> 'DependencyBuilder':
        """Action: show target field.

        Args:
            target_field: Name of field to show

        Returns:
            Self for method chaining
        """
        return self._add_dependency(target_field, DependencyAction.SHOW)

    def hide(self, target_field: str) -> 'DependencyBuilder':
        """Action: hide target field.

        Args:
            target_field: Name of field to hide

        Returns:
            Self for method chaining
        """
        return self._add_dependency(target_field, DependencyAction.HIDE)

    def enable(self, target_field: str) -> 'DependencyBuilder':
        """Action: enable target field.

        Args:
            target_field: Name of field to enable

        Returns:
            Self for method chaining
        """
        return self._add_dependency(target_field, DependencyAction.ENABLE)

    def disable(self, target_field: str) -> 'DependencyBuilder':
        """Action: disable target field.

        Args:
            target_field: Name of field to disable

        Returns:
            Self for method chaining
        """
        return self._add_dependency(target_field, DependencyAction.DISABLE)

    def require(self, target_field: str) -> 'DependencyBuilder':
        """Action: make target field required.

        Args:
            target_field: Name of field to require

        Returns:
            Self for method chaining
        """
        return self._add_dependency(target_field, DependencyAction.REQUIRE)

    def make_optional(self, target_field: str) -> 'DependencyBuilder':
        """Action: make target field optional.

        Args:
            target_field: Name of field to make optional

        Returns:
            Self for method chaining
        """
        return self._add_dependency(target_field, DependencyAction.OPTIONAL)

    def _add_dependency(
        self, target_field: str, action: DependencyAction
    ) -> 'DependencyBuilder':
        """Add a dependency to the list.

        Args:
            target_field: Target field name
            action: Action to perform

        Returns:
            Self for method chaining
        """
        if not self._current_field or not self._current_condition:
            raise ValueError("Must call when() and a condition method first")

        dep = FieldDependency(
            source_field=self._current_field,
            target_field=target_field,
            condition=self._current_condition,
            action=action,
        )

        self._dependencies.append(dep)
        return self

    def build(self) -> list[FieldDependency]:
        """Build and return the list of dependencies.

        Returns:
            List of FieldDependency objects
        """
        return self._dependencies.copy()


def add_field_dependencies(
    func: Callable,
    dependencies: list[FieldDependency],
) -> dict:
    """Augment RJSF spec with field dependencies.

    Args:
        func: Function to augment
        dependencies: List of field dependencies

    Returns:
        Dictionary with augmented schema and uiSchema

    Example:
        >>> deps = [
        ...     FieldDependency('reason', 'other_reason',
        ...                    lambda v: v == 'other',
        ...                    DependencyAction.SHOW)
        ... ]
        >>> spec = add_field_dependencies(my_func, deps)
    """
    # This would typically be called during spec generation
    # For now, return a structure that can be merged
    schema_additions = {'allOf': []}
    ui_schema_additions = {}

    for dep in dependencies:
        # Add JSON Schema dependencies
        schema_dep = dep.to_json_schema()
        if schema_dep:
            schema_additions['allOf'].append(schema_dep)

        # Add UI Schema dependencies
        ui_dep = dep.to_ui_schema()
        if ui_dep:
            ui_schema_additions.update(ui_dep)

    return {'schema_additions': schema_additions, 'ui_schema_additions': ui_schema_additions}


def with_dependencies(*dependencies: FieldDependency):
    """Decorator to attach field dependencies to a function.

    Args:
        *dependencies: FieldDependency objects

    Returns:
        Decorator function

    Example:
        >>> @with_dependencies(
        ...     FieldDependency('reason', 'other_reason',
        ...                    lambda v: v == 'other',
        ...                    DependencyAction.SHOW)
        ... )
        ... def submit_feedback(reason: str, other_reason: str = ''):
        ...     pass
    """
    from functools import wraps

    def decorator(func: Callable) -> Callable:
        setattr(func, '__uf_field_dependencies__', list(dependencies))

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, '__uf_field_dependencies__', list(dependencies))

        return wrapper

    return decorator


def get_field_dependencies(func: Callable) -> list[FieldDependency]:
    """Get field dependencies from a function.

    Args:
        func: Function to get dependencies from

    Returns:
        List of FieldDependency objects
    """
    return getattr(func, '__uf_field_dependencies__', [])
```

## uf/history.py

```python
"""Call history and presets for uf.

Provides functionality to track function calls, save parameter presets,
and reuse previous calls for improved user experience.
"""

from typing import Callable, Any, Optional
from datetime import datetime
from collections import defaultdict
import json


class FunctionCall:
    """Record of a single function call.

    Attributes:
        func_name: Name of the function
        params: Parameters used
        result: Result returned (if captured)
        timestamp: When the call was made
        success: Whether the call succeeded
        error: Error message if failed
    """

    def __init__(
        self,
        func_name: str,
        params: dict,
        result: Any = None,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """Initialize function call record.

        Args:
            func_name: Name of the function
            params: Parameters dictionary
            result: Function result
            success: Whether call succeeded
            error: Error message if failed
        """
        self.func_name = func_name
        self.params = params
        self.result = result
        self.timestamp = datetime.now()
        self.success = success
        self.error = error

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'func_name': self.func_name,
            'params': self.params,
            'result': self.result if self.success else None,
            'timestamp': self.timestamp.isoformat(),
            'success': self.success,
            'error': self.error,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FunctionCall':
        """Create from dictionary.

        Args:
            data: Dictionary with call data

        Returns:
            FunctionCall instance
        """
        call = cls(
            func_name=data['func_name'],
            params=data['params'],
            result=data.get('result'),
            success=data.get('success', True),
            error=data.get('error'),
        )
        if 'timestamp' in data:
            call.timestamp = datetime.fromisoformat(data['timestamp'])
        return call


class CallHistory:
    """Manage history of function calls.

    Example:
        >>> history = CallHistory(max_size=100)
        >>> history.record('add', {'x': 10, 'y': 20}, result=30)
        >>> recent = history.get_recent('add', limit=5)
    """

    def __init__(self, max_size: int = 100):
        """Initialize call history.

        Args:
            max_size: Maximum number of calls to keep per function
        """
        self.max_size = max_size
        self._history: dict[str, list[FunctionCall]] = defaultdict(list)

    def record(
        self,
        func_name: str,
        params: dict,
        result: Any = None,
        success: bool = True,
        error: Optional[str] = None,
    ) -> None:
        """Record a function call.

        Args:
            func_name: Name of the function
            params: Parameters used
            result: Result returned
            success: Whether call succeeded
            error: Error message if failed
        """
        call = FunctionCall(
            func_name=func_name,
            params=params,
            result=result,
            success=success,
            error=error,
        )

        self._history[func_name].append(call)

        # Trim to max size
        if len(self._history[func_name]) > self.max_size:
            self._history[func_name] = self._history[func_name][-self.max_size:]

    def get_recent(self, func_name: str, limit: int = 10) -> list[FunctionCall]:
        """Get recent calls for a function.

        Args:
            func_name: Function name
            limit: Maximum number to return

        Returns:
            List of recent FunctionCall objects (newest first)
        """
        calls = self._history.get(func_name, [])
        return list(reversed(calls[-limit:]))

    def get_successful_calls(
        self, func_name: str, limit: int = 10
    ) -> list[FunctionCall]:
        """Get recent successful calls.

        Args:
            func_name: Function name
            limit: Maximum number to return

        Returns:
            List of successful FunctionCall objects
        """
        calls = [c for c in self._history.get(func_name, []) if c.success]
        return list(reversed(calls[-limit:]))

    def clear(self, func_name: Optional[str] = None) -> None:
        """Clear history.

        Args:
            func_name: Function to clear, or None for all
        """
        if func_name:
            self._history[func_name] = []
        else:
            self._history.clear()

    def to_dict(self) -> dict:
        """Convert history to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            func_name: [call.to_dict() for call in calls]
            for func_name, calls in self._history.items()
        }

    @classmethod
    def from_dict(cls, data: dict, max_size: int = 100) -> 'CallHistory':
        """Create from dictionary.

        Args:
            data: Dictionary with history data
            max_size: Maximum size per function

        Returns:
            CallHistory instance
        """
        history = cls(max_size=max_size)

        for func_name, calls_data in data.items():
            history._history[func_name] = [
                FunctionCall.from_dict(call_data) for call_data in calls_data
            ]

        return history


class Preset:
    """A saved parameter preset for a function.

    Attributes:
        name: Preset name
        func_name: Function this preset is for
        params: Parameter values
        description: Optional description
        created_at: When preset was created
    """

    def __init__(
        self,
        name: str,
        func_name: str,
        params: dict,
        description: str = "",
    ):
        """Initialize preset.

        Args:
            name: Preset name
            func_name: Function name
            params: Parameter values
            description: Optional description
        """
        self.name = name
        self.func_name = func_name
        self.params = params
        self.description = description
        self.created_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'name': self.name,
            'func_name': self.func_name,
            'params': self.params,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Preset':
        """Create from dictionary.

        Args:
            data: Dictionary with preset data

        Returns:
            Preset instance
        """
        preset = cls(
            name=data['name'],
            func_name=data['func_name'],
            params=data['params'],
            description=data.get('description', ''),
        )
        if 'created_at' in data:
            preset.created_at = datetime.fromisoformat(data['created_at'])
        return preset


class PresetManager:
    """Manage parameter presets for functions.

    Example:
        >>> presets = PresetManager()
        >>> presets.save('quick_add', 'add', {'x': 10, 'y': 20}, 'Quick test')
        >>> preset = presets.get('quick_add', 'add')
        >>> result = my_func(**preset.params)
    """

    def __init__(self):
        """Initialize preset manager."""
        self._presets: dict[str, dict[str, Preset]] = defaultdict(dict)

    def save(
        self,
        preset_name: str,
        func_name: str,
        params: dict,
        description: str = "",
    ) -> Preset:
        """Save a parameter preset.

        Args:
            preset_name: Name for this preset
            func_name: Function this preset is for
            params: Parameter values
            description: Optional description

        Returns:
            Created Preset object
        """
        preset = Preset(
            name=preset_name,
            func_name=func_name,
            params=params,
            description=description,
        )

        self._presets[func_name][preset_name] = preset
        return preset

    def get(self, preset_name: str, func_name: str) -> Optional[Preset]:
        """Get a preset.

        Args:
            preset_name: Name of preset
            func_name: Function name

        Returns:
            Preset object or None
        """
        return self._presets.get(func_name, {}).get(preset_name)

    def list_presets(self, func_name: str) -> list[Preset]:
        """List all presets for a function.

        Args:
            func_name: Function name

        Returns:
            List of Preset objects
        """
        return list(self._presets.get(func_name, {}).values())

    def delete(self, preset_name: str, func_name: str) -> bool:
        """Delete a preset.

        Args:
            preset_name: Name of preset
            func_name: Function name

        Returns:
            True if deleted, False if not found
        """
        if func_name in self._presets and preset_name in self._presets[func_name]:
            del self._presets[func_name][preset_name]
            return True
        return False

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            func_name: {
                preset_name: preset.to_dict()
                for preset_name, preset in presets.items()
            }
            for func_name, presets in self._presets.items()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PresetManager':
        """Create from dictionary.

        Args:
            data: Dictionary with preset data

        Returns:
            PresetManager instance
        """
        manager = cls()

        for func_name, presets_data in data.items():
            for preset_name, preset_data in presets_data.items():
                preset = Preset.from_dict(preset_data)
                manager._presets[func_name][preset_name] = preset

        return manager


class HistoryManager:
    """Combined manager for history and presets.

    Provides a unified interface for tracking calls and managing presets.

    Example:
        >>> manager = HistoryManager()
        >>> manager.record_call('add', {'x': 10, 'y': 20}, result=30)
        >>> manager.save_preset('quick', 'add', {'x': 10, 'y': 20})
        >>> recent = manager.get_recent_calls('add')
        >>> presets = manager.get_presets('add')
    """

    def __init__(self, max_history: int = 100):
        """Initialize history manager.

        Args:
            max_history: Maximum history size per function
        """
        self.history = CallHistory(max_size=max_history)
        self.presets = PresetManager()

    def record_call(
        self,
        func_name: str,
        params: dict,
        result: Any = None,
        success: bool = True,
        error: Optional[str] = None,
    ) -> None:
        """Record a function call.

        Args:
            func_name: Function name
            params: Parameters used
            result: Result returned
            success: Whether call succeeded
            error: Error message if failed
        """
        self.history.record(func_name, params, result, success, error)

    def get_recent_calls(
        self, func_name: str, limit: int = 10
    ) -> list[FunctionCall]:
        """Get recent calls.

        Args:
            func_name: Function name
            limit: Maximum number to return

        Returns:
            List of recent FunctionCall objects
        """
        return self.history.get_recent(func_name, limit)

    def save_preset(
        self,
        preset_name: str,
        func_name: str,
        params: dict,
        description: str = "",
    ) -> Preset:
        """Save a preset.

        Args:
            preset_name: Name for preset
            func_name: Function name
            params: Parameter values
            description: Optional description

        Returns:
            Created Preset object
        """
        return self.presets.save(preset_name, func_name, params, description)

    def get_preset(self, preset_name: str, func_name: str) -> Optional[Preset]:
        """Get a preset.

        Args:
            preset_name: Name of preset
            func_name: Function name

        Returns:
            Preset object or None
        """
        return self.presets.get(preset_name, func_name)

    def get_presets(self, func_name: str) -> list[Preset]:
        """Get all presets for a function.

        Args:
            func_name: Function name

        Returns:
            List of Preset objects
        """
        return self.presets.list_presets(func_name)

    def save_to_file(self, filepath: str) -> None:
        """Save history and presets to file.

        Args:
            filepath: Path to save to
        """
        data = {
            'history': self.history.to_dict(),
            'presets': self.presets.to_dict(),
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str, max_history: int = 100) -> 'HistoryManager':
        """Load from file.

        Args:
            filepath: Path to load from
            max_history: Maximum history size

        Returns:
            HistoryManager instance
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        manager = cls(max_history=max_history)
        manager.history = CallHistory.from_dict(data.get('history', {}), max_history)
        manager.presets = PresetManager.from_dict(data.get('presets', {}))

        return manager


# Global instance
_global_history_manager = HistoryManager()


def get_global_history_manager() -> HistoryManager:
    """Get the global history manager.

    Returns:
        Global HistoryManager instance
    """
    return _global_history_manager


def enable_history(func: Callable, max_size: int = 100) -> Callable:
    """Decorator to enable call history for a function.

    Args:
        max_size: Maximum history size

    Returns:
        Decorator function

    Example:
        >>> @enable_history
        ... def my_function(x: int):
        ...     return x * 2
    """

    def wrapper(*args, **kwargs):
        """Wrapper that records calls."""
        manager = get_global_history_manager()

        try:
            result = func(*args, **kwargs)
            manager.record_call(
                func.__name__,
                kwargs,
                result=result,
                success=True,
            )
            return result
        except Exception as e:
            manager.record_call(
                func.__name__,
                kwargs,
                success=False,
                error=str(e),
            )
            raise

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__uf_history_enabled__ = True

    return wrapper
```

## uf/openapi.py

```python
"""OpenAPI/Swagger integration for uf.

Automatically generates OpenAPI specifications and provides Swagger UI
for API documentation and testing.
"""

from typing import Callable, Any, Optional
import inspect


def function_to_openapi_operation(func: Callable, path: str = None) -> dict:
    """Convert a function to OpenAPI operation spec.

    Args:
        func: Function to convert
        path: Optional API path

    Returns:
        OpenAPI operation dictionary
    """
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or ""

    # Parse docstring for description
    lines = doc.split('\n')
    summary = lines[0] if lines else func.__name__
    description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else summary

    # Build parameters from signature
    parameters = []
    request_body = None

    type_map = {
        int: 'integer',
        float: 'number',
        str: 'string',
        bool: 'boolean',
        list: 'array',
        dict: 'object',
    }

    for param_name, param in sig.parameters.items():
        param_type = 'string'  # default

        if param.annotation != inspect.Parameter.empty:
            py_type = param.annotation
            # Handle Optional types
            if hasattr(py_type, '__origin__'):
                if py_type.__origin__ is type(Optional):
                    py_type = py_type.__args__[0]

            param_type = type_map.get(py_type, 'string')

        param_schema = {
            'type': param_type,
        }

        # Check if required
        required = param.default == inspect.Parameter.empty

        parameters.append({
            'name': param_name,
            'in': 'query',
            'required': required,
            'schema': param_schema,
        })

    operation = {
        'summary': summary,
        'description': description,
        'parameters': parameters,
        'responses': {
            '200': {
                'description': 'Successful response',
                'content': {
                    'application/json': {
                        'schema': {'type': 'object'}
                    }
                }
            },
            '400': {
                'description': 'Bad request'
            },
            '500': {
                'description': 'Internal server error'
            }
        }
    }

    # Add tags if function has group
    if hasattr(func, '__uf_ui_config__'):
        config = func.__uf_ui_config__
        if config.get('group'):
            operation['tags'] = [config['group']]

    return operation


def generate_openapi_spec(
    funcs: list[Callable],
    title: str = "API",
    version: str = "1.0.0",
    description: str = "",
    servers: Optional[list[dict]] = None,
) -> dict:
    """Generate OpenAPI 3.0 specification.

    Args:
        funcs: List of functions
        title: API title
        version: API version
        description: API description
        servers: Optional list of server configs

    Returns:
        OpenAPI specification dictionary
    """
    if servers is None:
        servers = [{'url': '/'}]

    paths = {}
    tags = set()

    for func in funcs:
        func_name = func.__name__
        path = f'/{func_name}'

        operation = function_to_openapi_operation(func, path)

        # Collect tags
        if 'tags' in operation:
            tags.update(operation['tags'])

        paths[path] = {
            'post': operation  # Use POST for form submissions
        }

    spec = {
        'openapi': '3.0.0',
        'info': {
            'title': title,
            'version': version,
            'description': description,
        },
        'servers': servers,
        'paths': paths,
    }

    # Add tags
    if tags:
        spec['tags'] = [{'name': tag} for tag in sorted(tags)]

    return spec


def swagger_ui_html(openapi_url: str = '/openapi.json') -> str:
    """Generate Swagger UI HTML.

    Args:
        openapi_url: URL to OpenAPI spec

    Returns:
        HTML string for Swagger UI
    """
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            window.ui = SwaggerUIBundle({{
                url: '{openapi_url}',
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                layout: "StandaloneLayout"
            }});
        }};
    </script>
</body>
</html>"""
    return html


def redoc_ui_html(openapi_url: str = '/openapi.json') -> str:
    """Generate ReDoc UI HTML.

    Args:
        openapi_url: URL to OpenAPI spec

    Returns:
        HTML string for ReDoc UI
    """
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation</title>
</head>
<body>
    <redoc spec-url='{openapi_url}'></redoc>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
</body>
</html>"""
    return html


def add_openapi_routes(app: Any, funcs: list[Callable], **spec_kwargs) -> None:
    """Add OpenAPI routes to an app.

    Adds:
    - /openapi.json: OpenAPI specification
    - /docs: Swagger UI
    - /redoc: ReDoc UI

    Args:
        app: Web application
        funcs: List of functions
        **spec_kwargs: Arguments for generate_openapi_spec
    """
    # Generate spec
    spec = generate_openapi_spec(funcs, **spec_kwargs)

    # Detect framework
    is_bottle = hasattr(app, 'route')

    if is_bottle:
        @app.route('/openapi.json')
        def openapi_spec():
            """Return OpenAPI spec."""
            import json
            from bottle import response
            response.content_type = 'application/json'
            return json.dumps(spec)

        @app.route('/docs')
        def swagger_ui():
            """Return Swagger UI."""
            return swagger_ui_html()

        @app.route('/redoc')
        def redoc_ui():
            """Return ReDoc UI."""
            return redoc_ui_html()
    else:
        # FastAPI
        from fastapi.responses import JSONResponse, HTMLResponse

        @app.get('/openapi.json')
        async def openapi_spec():
            """Return OpenAPI spec."""
            return JSONResponse(content=spec)

        @app.get('/docs', response_class=HTMLResponse)
        async def swagger_ui():
            """Return Swagger UI."""
            return swagger_ui_html()

        @app.get('/redoc', response_class=HTMLResponse)
        async def redoc_ui():
            """Return ReDoc UI."""
            return redoc_ui_html()


class OpenAPIConfig:
    """Configuration for OpenAPI generation.

    Example:
        >>> config = OpenAPIConfig(
        ...     title="My API",
        ...     version="2.0.0",
        ...     description="API for my application"
        ... )
    """

    def __init__(
        self,
        title: str = "API",
        version: str = "1.0.0",
        description: str = "",
        servers: Optional[list[dict]] = None,
        enable_swagger: bool = True,
        enable_redoc: bool = True,
    ):
        """Initialize OpenAPI config.

        Args:
            title: API title
            version: API version
            description: API description
            servers: List of server configurations
            enable_swagger: Enable Swagger UI
            enable_redoc: Enable ReDoc UI
        """
        self.title = title
        self.version = version
        self.description = description
        self.servers = servers or [{'url': '/'}]
        self.enable_swagger = enable_swagger
        self.enable_redoc = enable_redoc

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Configuration dictionary
        """
        return {
            'title': self.title,
            'version': self.version,
            'description': self.description,
            'servers': self.servers,
            'enable_swagger': self.enable_swagger,
            'enable_redoc': self.enable_redoc,
        }
```

## uf/organization.py

```python
"""Function grouping and organization for uf.

Provides tools for organizing functions into categories, groups, and
hierarchies for better navigation in the UI.
"""

from typing import Callable, Iterable, Optional
from dataclasses import dataclass, field
from collections.abc import Mapping


@dataclass
class FunctionGroup:
    """Group of functions with metadata.

    Attributes:
        name: Name of the group
        funcs: Functions in this group
        description: Description of the group
        icon: Optional icon identifier for the group
        order: Display order (lower numbers first)
        collapsed: Whether the group starts collapsed in UI

    Example:
        >>> math_funcs = FunctionGroup(
        ...     'Math',
        ...     [add, subtract, multiply, divide],
        ...     description='Mathematical operations',
        ...     icon='calculator'
        ... )
    """

    name: str
    funcs: list[Callable] = field(default_factory=list)
    description: str = ""
    icon: Optional[str] = None
    order: int = 0
    collapsed: bool = False

    def add_function(self, func: Callable) -> 'FunctionGroup':
        """Add a function to this group.

        Args:
            func: Function to add

        Returns:
            Self for method chaining
        """
        self.funcs.append(func)
        return self

    def get_function_names(self) -> list[str]:
        """Get names of all functions in this group.

        Returns:
            List of function name strings
        """
        return [f.__name__ for f in self.funcs]


class FunctionOrganizer:
    """Organize functions into groups and hierarchies.

    This class provides a fluent interface for building function
    organization structures that can be used to generate grouped
    navigation in the UI.

    Example:
        >>> organizer = FunctionOrganizer()
        >>> organizer.group('Admin', [user_create, user_delete], icon='shield')
        >>> organizer.group('Reports', [generate_report, export_csv], icon='file')
        >>> groups = organizer.get_groups()
    """

    def __init__(self):
        """Initialize the organizer."""
        self._groups: list[FunctionGroup] = []
        self._ungrouped_funcs: list[Callable] = []

    def group(
        self,
        name: str,
        funcs: Optional[Iterable[Callable]] = None,
        *,
        description: str = "",
        icon: Optional[str] = None,
        order: int = 0,
        collapsed: bool = False,
    ) -> FunctionGroup:
        """Create and add a function group.

        Args:
            name: Name of the group
            funcs: Optional functions to add to group
            description: Description of the group
            icon: Optional icon identifier
            order: Display order
            collapsed: Whether to start collapsed

        Returns:
            The created FunctionGroup

        Example:
            >>> organizer.group(
            ...     'Database',
            ...     [save_record, load_record],
            ...     description='Database operations',
            ...     icon='database'
            ... )
        """
        func_group = FunctionGroup(
            name=name,
            funcs=list(funcs or []),
            description=description,
            icon=icon,
            order=order,
            collapsed=collapsed,
        )
        self._groups.append(func_group)
        return func_group

    def add_to_group(self, group_name: str, func: Callable) -> 'FunctionOrganizer':
        """Add a function to an existing group.

        Args:
            group_name: Name of the group
            func: Function to add

        Returns:
            Self for method chaining

        Raises:
            ValueError: If group doesn't exist
        """
        for group in self._groups:
            if group.name == group_name:
                group.add_function(func)
                return self

        raise ValueError(f"Group '{group_name}' not found")

    def add_ungrouped(self, func: Callable) -> 'FunctionOrganizer':
        """Add a function without a group.

        Args:
            func: Function to add

        Returns:
            Self for method chaining
        """
        self._ungrouped_funcs.append(func)
        return self

    def get_groups(self) -> list[FunctionGroup]:
        """Get all groups, sorted by order.

        Returns:
            List of FunctionGroup objects sorted by order
        """
        groups = sorted(self._groups, key=lambda g: g.order)

        # Add ungrouped functions if any
        if self._ungrouped_funcs:
            ungrouped = FunctionGroup(
                name="Other",
                funcs=self._ungrouped_funcs,
                description="Uncategorized functions",
                order=999,
            )
            groups.append(ungrouped)

        return groups

    def get_all_functions(self) -> list[Callable]:
        """Get all functions across all groups.

        Returns:
            List of all functions
        """
        all_funcs = []
        for group in self._groups:
            all_funcs.extend(group.funcs)
        all_funcs.extend(self._ungrouped_funcs)
        return all_funcs

    def to_dict(self) -> dict:
        """Convert organization to dictionary format.

        Returns:
            Dictionary representation suitable for JSON serialization

        Example:
            >>> org_dict = organizer.to_dict()
            >>> # Can be used in templates or APIs
        """
        return {
            'groups': [
                {
                    'name': group.name,
                    'description': group.description,
                    'icon': group.icon,
                    'order': group.order,
                    'collapsed': group.collapsed,
                    'functions': [
                        {
                            'name': func.__name__,
                            'description': func.__doc__ or '',
                        }
                        for func in group.funcs
                    ],
                }
                for group in self.get_groups()
            ]
        }


def mk_grouped_app(
    groups: Iterable[FunctionGroup],
    **mk_rjsf_app_kwargs,
):
    """Create a uf app with grouped function navigation.

    Args:
        groups: Iterable of FunctionGroup objects
        **mk_rjsf_app_kwargs: Arguments passed to mk_rjsf_app

    Returns:
        Configured web application with grouped navigation

    Example:
        >>> admin_group = FunctionGroup('Admin', [user_create, user_delete])
        >>> reports_group = FunctionGroup('Reports', [generate_report])
        >>> app = mk_grouped_app([admin_group, reports_group])
    """
    from uf.base import mk_rjsf_app

    # Collect all functions from all groups
    all_funcs = []
    for group in groups:
        all_funcs.extend(group.funcs)

    # Create the app
    app = mk_rjsf_app(all_funcs, **mk_rjsf_app_kwargs)

    # Store organization metadata on the app
    app.function_groups = list(groups)

    # Create organizer for serialization
    organizer = FunctionOrganizer()
    for group in groups:
        organizer.group(
            name=group.name,
            funcs=group.funcs,
            description=group.description,
            icon=group.icon,
            order=group.order,
            collapsed=group.collapsed,
        )

    app.organization = organizer

    # Add route to get group information
    _add_group_routes(app, organizer)

    return app


def _add_group_routes(app, organizer: FunctionOrganizer):
    """Add routes for accessing group information.

    Args:
        app: The web application
        organizer: FunctionOrganizer instance
    """
    # Detect framework
    is_bottle = hasattr(app, 'route')

    if is_bottle:
        @app.route('/api/groups')
        def get_groups():
            """Get function group organization."""
            import json
            from bottle import response

            response.content_type = 'application/json'
            return json.dumps(organizer.to_dict())
    else:
        # FastAPI
        from fastapi.responses import JSONResponse

        @app.get('/api/groups')
        async def get_groups():
            """Get function group organization."""
            return JSONResponse(content=organizer.to_dict())


def auto_group_by_prefix(
    funcs: Iterable[Callable],
    separator: str = "_",
) -> FunctionOrganizer:
    """Automatically group functions by name prefix.

    Groups functions based on the part of their name before the separator.
    For example, with separator="_":
    - user_create, user_delete → "user" group
    - report_generate, report_export → "report" group

    Args:
        funcs: Functions to organize
        separator: Separator character (default: "_")

    Returns:
        FunctionOrganizer with auto-generated groups

    Example:
        >>> funcs = [user_create, user_delete, report_generate, admin_reset]
        >>> organizer = auto_group_by_prefix(funcs)
        >>> # Creates groups: 'user', 'report', 'admin'
    """
    from collections import defaultdict

    # Group functions by prefix
    groups_dict = defaultdict(list)

    for func in funcs:
        name = func.__name__
        if separator in name:
            prefix = name.split(separator)[0]
            groups_dict[prefix].append(func)
        else:
            groups_dict['other'].append(func)

    # Create organizer
    organizer = FunctionOrganizer()

    for group_name, group_funcs in sorted(groups_dict.items()):
        # Capitalize group name
        display_name = group_name.replace('_', ' ').title()

        organizer.group(
            display_name,
            group_funcs,
            description=f"{display_name} operations",
        )

    return organizer


def auto_group_by_module(funcs: Iterable[Callable]) -> FunctionOrganizer:
    """Automatically group functions by their module.

    Args:
        funcs: Functions to organize

    Returns:
        FunctionOrganizer with module-based groups

    Example:
        >>> from myapp import user_ops, report_ops
        >>> funcs = [user_ops.create, user_ops.delete, report_ops.generate]
        >>> organizer = auto_group_by_module(funcs)
    """
    from collections import defaultdict

    groups_dict = defaultdict(list)

    for func in funcs:
        module = func.__module__
        # Get last part of module name
        if '.' in module:
            module_name = module.split('.')[-1]
        else:
            module_name = module

        groups_dict[module_name].append(func)

    # Create organizer
    organizer = FunctionOrganizer()

    for module_name, group_funcs in sorted(groups_dict.items()):
        display_name = module_name.replace('_', ' ').title()

        organizer.group(
            display_name,
            group_funcs,
            description=f"Functions from {module_name}",
        )

    return organizer


def auto_group_by_tag(funcs: Iterable[Callable], tag_attr: str = '__uf_group__') -> FunctionOrganizer:
    """Automatically group functions by a tag attribute.

    Functions can be tagged with a group name using an attribute.

    Args:
        funcs: Functions to organize
        tag_attr: Name of the attribute to use for grouping

    Returns:
        FunctionOrganizer with tag-based groups

    Example:
        >>> def create_user(name: str):
        ...     pass
        >>> create_user.__uf_group__ = 'Admin'
        >>>
        >>> organizer = auto_group_by_tag([create_user, other_func])
    """
    from collections import defaultdict

    groups_dict = defaultdict(list)

    for func in funcs:
        tag = getattr(func, tag_attr, 'Other')
        groups_dict[tag].append(func)

    # Create organizer
    organizer = FunctionOrganizer()

    for tag, group_funcs in sorted(groups_dict.items()):
        organizer.group(tag, group_funcs)

    return organizer
```

## uf/pydantic_support.py

```python
"""Pydantic integration for uf.

Provides seamless integration with Pydantic models, automatically
generating forms with validation from Pydantic models.
"""

from typing import Callable, Any, Optional, get_type_hints, get_args, get_origin
import inspect


def is_pydantic_model(obj: Any) -> bool:
    """Check if an object is a Pydantic model.

    Args:
        obj: Object to check

    Returns:
        True if object is a Pydantic BaseModel
    """
    try:
        from pydantic import BaseModel
        if inspect.isclass(obj):
            return issubclass(obj, BaseModel)
        return isinstance(obj, BaseModel)
    except ImportError:
        return False


def pydantic_model_to_json_schema(model_class) -> dict:
    """Convert a Pydantic model to JSON Schema.

    Args:
        model_class: Pydantic model class

    Returns:
        JSON Schema dictionary

    Example:
        >>> from pydantic import BaseModel
        >>> class User(BaseModel):
        ...     name: str
        ...     age: int
        >>> schema = pydantic_model_to_json_schema(User)
    """
    if not is_pydantic_model(model_class):
        raise ValueError(f"{model_class} is not a Pydantic model")

    # Pydantic v2 compatibility
    try:
        # Pydantic v2
        return model_class.model_json_schema()
    except AttributeError:
        # Pydantic v1
        return model_class.schema()


def function_uses_pydantic(func: Callable) -> bool:
    """Check if a function uses Pydantic models in its signature.

    Args:
        func: Function to check

    Returns:
        True if any parameter is a Pydantic model
    """
    try:
        type_hints = get_type_hints(func)
        return any(is_pydantic_model(hint) for hint in type_hints.values())
    except Exception:
        return False


def extract_pydantic_params(func: Callable) -> dict[str, Any]:
    """Extract Pydantic model parameters from function signature.

    Args:
        func: Function to analyze

    Returns:
        Dictionary mapping parameter names to Pydantic model classes
    """
    pydantic_params = {}

    try:
        type_hints = get_type_hints(func)
        for param_name, param_type in type_hints.items():
            if is_pydantic_model(param_type):
                pydantic_params[param_name] = param_type
    except Exception:
        pass

    return pydantic_params


def create_pydantic_spec(func: Callable) -> Optional[dict]:
    """Create RJSF spec from function with Pydantic parameters.

    Args:
        func: Function that uses Pydantic models

    Returns:
        RJSF specification dictionary or None

    Example:
        >>> from pydantic import BaseModel, EmailStr
        >>> class UserCreate(BaseModel):
        ...     email: EmailStr
        ...     age: int
        >>> def create_user(user: UserCreate):
        ...     pass
        >>> spec = create_pydantic_spec(create_user)
    """
    pydantic_params = extract_pydantic_params(func)

    if not pydantic_params:
        return None

    # If single Pydantic parameter, use its schema directly
    if len(pydantic_params) == 1:
        param_name, model_class = list(pydantic_params.items())[0]
        schema = pydantic_model_to_json_schema(model_class)

        # Clean up schema
        if '$defs' in schema:
            schema.pop('$defs')

        return {
            'schema': schema,
            'uiSchema': {},
            'pydantic_model': model_class,
            'param_name': param_name,
        }

    # Multiple Pydantic parameters - combine schemas
    combined_schema = {
        'type': 'object',
        'properties': {},
        'required': [],
        'title': func.__name__,
    }

    for param_name, model_class in pydantic_params.items():
        model_schema = pydantic_model_to_json_schema(model_class)
        combined_schema['properties'][param_name] = model_schema

        # Add to required if no default
        sig = inspect.signature(func)
        if sig.parameters[param_name].default == inspect.Parameter.empty:
            combined_schema['required'].append(param_name)

    return {
        'schema': combined_schema,
        'uiSchema': {},
        'pydantic_models': pydantic_params,
    }


def pydantic_to_dict(obj: Any) -> dict:
    """Convert Pydantic model instance to dictionary.

    Args:
        obj: Pydantic model instance

    Returns:
        Dictionary representation
    """
    if not is_pydantic_model(obj):
        return obj

    # Pydantic v2 compatibility
    try:
        # Pydantic v2
        return obj.model_dump()
    except AttributeError:
        # Pydantic v1
        return obj.dict()


def dict_to_pydantic(data: dict, model_class) -> Any:
    """Convert dictionary to Pydantic model instance.

    Args:
        data: Dictionary of data
        model_class: Pydantic model class

    Returns:
        Pydantic model instance

    Raises:
        ValidationError: If data doesn't match model schema
    """
    if not is_pydantic_model(model_class):
        return data

    # Pydantic v2 compatibility
    try:
        # Pydantic v2
        return model_class.model_validate(data)
    except AttributeError:
        # Pydantic v1
        return model_class.parse_obj(data)


def wrap_pydantic_function(func: Callable) -> Callable:
    """Wrap a function that uses Pydantic models.

    The wrapper converts dict inputs to Pydantic models before calling
    the function, and converts Pydantic outputs back to dicts.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function

    Example:
        >>> from pydantic import BaseModel
        >>> class User(BaseModel):
        ...     name: str
        >>> def create_user(user: User) -> User:
        ...     return user
        >>> wrapped = wrap_pydantic_function(create_user)
        >>> result = wrapped({'name': 'Alice'})  # Pass dict, not User
    """
    pydantic_params = extract_pydantic_params(func)

    if not pydantic_params:
        return func

    def wrapper(**kwargs):
        """Wrapper that handles Pydantic conversion."""
        # Convert dict inputs to Pydantic models
        converted_kwargs = {}

        for param_name, value in kwargs.items():
            if param_name in pydantic_params:
                model_class = pydantic_params[param_name]
                if isinstance(value, dict):
                    converted_kwargs[param_name] = dict_to_pydantic(
                        value, model_class
                    )
                else:
                    converted_kwargs[param_name] = value
            else:
                converted_kwargs[param_name] = value

        # Call function
        result = func(**converted_kwargs)

        # Convert Pydantic output to dict if needed
        if is_pydantic_model(result):
            return pydantic_to_dict(result)

        return result

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__uf_pydantic_wrapped__ = True
    wrapper.__uf_original_function__ = func

    return wrapper


def extract_field_validators(model_class) -> dict:
    """Extract field validators from Pydantic model.

    Args:
        model_class: Pydantic model class

    Returns:
        Dictionary mapping field names to validator info
    """
    if not is_pydantic_model(model_class):
        return {}

    validators = {}

    try:
        # Pydantic v2
        if hasattr(model_class, 'model_fields'):
            for field_name, field_info in model_class.model_fields.items():
                validator_info = {
                    'required': field_info.is_required(),
                    'default': field_info.default if field_info.default is not None else None,
                }

                # Extract constraints
                if hasattr(field_info, 'constraints'):
                    constraints = {}
                    for constraint in ['gt', 'ge', 'lt', 'le', 'min_length', 'max_length']:
                        if hasattr(field_info, constraint):
                            val = getattr(field_info, constraint)
                            if val is not None:
                                constraints[constraint] = val

                    if constraints:
                        validator_info['constraints'] = constraints

                validators[field_name] = validator_info
    except Exception:
        # Pydantic v1 or other issues
        pass

    return validators


def pydantic_error_to_user_friendly(error) -> dict:
    """Convert Pydantic ValidationError to user-friendly format.

    Args:
        error: Pydantic ValidationError

    Returns:
        Dictionary with field-level errors
    """
    try:
        from pydantic import ValidationError
    except ImportError:
        return {'error': str(error)}

    if not isinstance(error, ValidationError):
        return {'error': str(error)}

    field_errors = {}

    for err in error.errors():
        field = '.'.join(str(loc) for loc in err['loc'])
        message = err['msg']
        field_errors[field] = message

    return {'field_errors': field_errors}


class PydanticRegistry:
    """Registry for Pydantic models used in uf.

    Tracks models and provides utilities for working with them.
    """

    def __init__(self):
        """Initialize the registry."""
        self._models: dict[str, Any] = {}

    def register(self, name: str, model_class: Any) -> None:
        """Register a Pydantic model.

        Args:
            name: Name to register under
            model_class: Pydantic model class
        """
        if not is_pydantic_model(model_class):
            raise ValueError(f"{model_class} is not a Pydantic model")

        self._models[name] = model_class

    def get(self, name: str) -> Optional[Any]:
        """Get a registered model by name.

        Args:
            name: Model name

        Returns:
            Pydantic model class or None
        """
        return self._models.get(name)

    def list_models(self) -> list[str]:
        """List all registered model names.

        Returns:
            List of model name strings
        """
        return list(self._models.keys())


# Global registry
_global_pydantic_registry = PydanticRegistry()


def get_pydantic_registry() -> PydanticRegistry:
    """Get the global Pydantic registry.

    Returns:
        Global PydanticRegistry instance
    """
    return _global_pydantic_registry
```

## uf/renderers.py

```python
"""Result rendering system for uf.

Provides smart rendering of function results based on their type,
including tables, charts, DataFrames, JSON, and custom renderers.
"""

from typing import Callable, Any, Optional, Type
from collections.abc import Mapping
import json


class ResultRenderer:
    """Base class for result renderers.

    Subclass this to create custom renderers for specific result types.
    """

    def can_render(self, result: Any) -> bool:
        """Check if this renderer can handle the given result.

        Args:
            result: The function result to render

        Returns:
            True if this renderer can handle the result
        """
        raise NotImplementedError

    def render(self, result: Any) -> dict:
        """Render the result to a displayable format.

        Args:
            result: The function result to render

        Returns:
            Dictionary with rendering information:
            - 'type': Renderer type (e.g., 'table', 'chart', 'json')
            - 'data': Rendered data
            - 'options': Optional rendering options
        """
        raise NotImplementedError


class JsonRenderer(ResultRenderer):
    """Render results as formatted JSON."""

    def can_render(self, result: Any) -> bool:
        """Can render any JSON-serializable result."""
        try:
            json.dumps(result)
            return True
        except (TypeError, ValueError):
            return False

    def render(self, result: Any) -> dict:
        """Render as formatted JSON."""
        return {
            'type': 'json',
            'data': result,
            'options': {'indent': 2},
        }


class TableRenderer(ResultRenderer):
    """Render list of dicts as a table."""

    def can_render(self, result: Any) -> bool:
        """Can render list of dictionaries."""
        if not isinstance(result, list):
            return False
        if not result:
            return False
        return all(isinstance(item, dict) for item in result)

    def render(self, result: Any) -> dict:
        """Render as table."""
        if not result:
            return {'type': 'table', 'data': [], 'columns': []}

        # Extract columns from first item
        columns = list(result[0].keys())

        return {
            'type': 'table',
            'data': result,
            'columns': columns,
            'options': {'sortable': True, 'searchable': True},
        }


class DataFrameRenderer(ResultRenderer):
    """Render pandas DataFrame."""

    def can_render(self, result: Any) -> bool:
        """Can render pandas DataFrame."""
        try:
            import pandas as pd
            return isinstance(result, pd.DataFrame)
        except ImportError:
            return False

    def render(self, result: Any) -> dict:
        """Render DataFrame as table."""
        # Convert to dict records
        data = result.to_dict('records')
        columns = result.columns.tolist()

        return {
            'type': 'dataframe',
            'data': data,
            'columns': columns,
            'options': {
                'sortable': True,
                'searchable': True,
                'index': result.index.tolist(),
            },
        }


class ChartRenderer(ResultRenderer):
    """Render data suitable for charts."""

    def can_render(self, result: Any) -> bool:
        """Can render list of dicts with numeric values."""
        if not isinstance(result, list):
            return False
        if not result:
            return False
        if not all(isinstance(item, dict) for item in result):
            return False

        # Check if has numeric values
        first = result[0]
        has_numeric = any(
            isinstance(v, (int, float)) for v in first.values()
        )
        return has_numeric

    def render(self, result: Any) -> dict:
        """Render as chart data."""
        if not result:
            return {'type': 'chart', 'data': []}

        # Extract labels and datasets
        first = result[0]
        label_key = list(first.keys())[0]  # First key is label
        value_keys = [k for k in first.keys() if isinstance(first[k], (int, float))]

        labels = [item[label_key] for item in result]
        datasets = []

        for value_key in value_keys:
            datasets.append({
                'label': value_key,
                'data': [item[value_key] for item in result],
            })

        return {
            'type': 'chart',
            'data': {
                'labels': labels,
                'datasets': datasets,
            },
            'options': {
                'chart_type': 'bar',  # default, can be overridden
                'responsive': True,
            },
        }


class ImageRenderer(ResultRenderer):
    """Render image data."""

    def can_render(self, result: Any) -> bool:
        """Can render bytes that look like images."""
        if isinstance(result, bytes):
            # Check for common image headers
            if result.startswith(b'\x89PNG'):
                return True
            if result.startswith(b'\xff\xd8\xff'):  # JPEG
                return True
            if result.startswith(b'GIF8'):
                return True
        return False

    def render(self, result: Any) -> dict:
        """Render image as base64."""
        import base64

        b64_data = base64.b64encode(result).decode('utf-8')

        # Detect format
        if result.startswith(b'\x89PNG'):
            mime_type = 'image/png'
        elif result.startswith(b'\xff\xd8\xff'):
            mime_type = 'image/jpeg'
        elif result.startswith(b'GIF8'):
            mime_type = 'image/gif'
        else:
            mime_type = 'image/png'

        return {
            'type': 'image',
            'data': f'data:{mime_type};base64,{b64_data}',
            'options': {},
        }


class ResultRendererRegistry:
    """Registry for result renderers.

    Manages a collection of renderers and selects the appropriate one
    for each result type.
    """

    def __init__(self):
        """Initialize the registry with default renderers."""
        self._renderers: list[ResultRenderer] = []
        self._type_renderers: dict[str, ResultRenderer] = {}

        # Register default renderers in priority order
        self.register(DataFrameRenderer())
        self.register(ImageRenderer())
        self.register(TableRenderer())
        self.register(ChartRenderer())
        self.register(JsonRenderer())  # Fallback

    def register(
        self,
        renderer: ResultRenderer,
        priority: int = 0,
    ) -> None:
        """Register a renderer.

        Args:
            renderer: ResultRenderer instance
            priority: Higher priority renderers are tried first
        """
        self._renderers.insert(priority, renderer)

    def register_for_type(
        self,
        result_type: Type,
        renderer: ResultRenderer,
    ) -> None:
        """Register a renderer for a specific type.

        Args:
            result_type: Python type to match
            renderer: ResultRenderer instance
        """
        type_name = result_type.__name__
        self._type_renderers[type_name] = renderer

    def render(self, result: Any, renderer_type: Optional[str] = None) -> dict:
        """Render a result using the appropriate renderer.

        Args:
            result: The function result to render
            renderer_type: Optional specific renderer type to use

        Returns:
            Rendered result dictionary
        """
        # If specific renderer requested, try that first
        if renderer_type and renderer_type in self._type_renderers:
            renderer = self._type_renderers[renderer_type]
            if renderer.can_render(result):
                return renderer.render(result)

        # Check type-specific renderers
        result_type_name = type(result).__name__
        if result_type_name in self._type_renderers:
            renderer = self._type_renderers[result_type_name]
            if renderer.can_render(result):
                return renderer.render(result)

        # Try each registered renderer
        for renderer in self._renderers:
            if renderer.can_render(result):
                return renderer.render(result)

        # Fallback to JSON
        return JsonRenderer().render(str(result))


# Global registry instance
_global_registry = ResultRendererRegistry()


def get_global_renderer_registry() -> ResultRendererRegistry:
    """Get the global renderer registry.

    Returns:
        The global ResultRendererRegistry instance
    """
    return _global_registry


def register_renderer(renderer: ResultRenderer, priority: int = 0) -> None:
    """Register a renderer in the global registry.

    Args:
        renderer: ResultRenderer instance
        priority: Higher priority renderers are tried first
    """
    _global_registry.register(renderer, priority)


def register_renderer_for_type(result_type: Type, renderer: ResultRenderer) -> None:
    """Register a renderer for a specific type.

    Args:
        result_type: Python type to match
        renderer: ResultRenderer instance
    """
    _global_registry.register_for_type(result_type, renderer)


def render_result(result: Any, renderer_type: Optional[str] = None) -> dict:
    """Render a result using the global registry.

    Args:
        result: The function result to render
        renderer_type: Optional specific renderer type to use

    Returns:
        Rendered result dictionary
    """
    return _global_registry.render(result, renderer_type)


def result_renderer(renderer_type: str):
    """Decorator to specify result renderer for a function.

    Args:
        renderer_type: Type of renderer to use

    Returns:
        Decorator function

    Example:
        >>> @result_renderer('table')
        ... def get_users() -> list[dict]:
        ...     return [{'name': 'Alice', 'age': 30}]
    """

    def decorator(func: Callable) -> Callable:
        setattr(func, '__uf_result_renderer__', renderer_type)
        return func

    return decorator


def get_result_renderer(func: Callable) -> Optional[str]:
    """Get the result renderer type for a function.

    Args:
        func: Function to check

    Returns:
        Renderer type string or None
    """
    return getattr(func, '__uf_result_renderer__', None)


# Custom renderer examples


class MarkdownRenderer(ResultRenderer):
    """Render markdown strings."""

    def can_render(self, result: Any) -> bool:
        """Can render strings that look like markdown."""
        if not isinstance(result, str):
            return False
        # Simple heuristic: contains markdown-like syntax
        md_indicators = ['#', '**', '*', '```', '[', '|']
        return any(indicator in result for indicator in md_indicators)

    def render(self, result: Any) -> dict:
        """Render as markdown."""
        return {
            'type': 'markdown',
            'data': result,
            'options': {},
        }


class HtmlRenderer(ResultRenderer):
    """Render HTML strings."""

    def can_render(self, result: Any) -> bool:
        """Can render strings that look like HTML."""
        if not isinstance(result, str):
            return False
        return result.strip().startswith('<') and '>' in result

    def render(self, result: Any) -> dict:
        """Render as HTML."""
        return {
            'type': 'html',
            'data': result,
            'options': {'sanitize': True},  # Security: sanitize HTML
        }


# Register additional renderers
register_renderer(MarkdownRenderer())
register_renderer(HtmlRenderer())
```

## uf/rjsf_config.py

```python
"""RJSF customization layer for uf.

Provides configuration classes and builders for customizing RJSF form
generation beyond the defaults, including field widgets, UI options,
and validation rules.
"""

from typing import Optional, Callable, Any, Literal
from dataclasses import dataclass, field


@dataclass
class RjsfFieldConfig:
    """Configuration for individual form fields.

    This class allows fine-grained control over how form fields are
    rendered in the RJSF interface.

    Attributes:
        widget: Widget type (e.g., 'textarea', 'select', 'radio', 'date')
        ui_options: Additional UI options for the widget
        format: JSON Schema format (e.g., 'email', 'uri', 'date-time')
        enum: List of allowed values (for dropdowns)
        description: Field description/help text
        placeholder: Placeholder text for the input
        title: Custom title for the field
        disabled: Whether the field is disabled
        readonly: Whether the field is read-only
        hidden: Whether to hide the field
        default: Default value for the field

    Example:
        >>> email_config = RjsfFieldConfig(
        ...     widget='email',
        ...     format='email',
        ...     placeholder='user@example.com'
        ... )
    """

    widget: Optional[str] = None
    ui_options: dict = field(default_factory=dict)
    format: Optional[str] = None
    enum: Optional[list] = None
    description: Optional[str] = None
    placeholder: Optional[str] = None
    title: Optional[str] = None
    disabled: bool = False
    readonly: bool = False
    hidden: bool = False
    default: Optional[Any] = None

    def to_json_schema_patch(self) -> dict:
        """Convert to JSON Schema properties.

        Returns:
            Dictionary of JSON Schema properties to merge into schema
        """
        patch = {}

        if self.format:
            patch['format'] = self.format
        if self.enum:
            patch['enum'] = self.enum
        if self.description:
            patch['description'] = self.description
        if self.title:
            patch['title'] = self.title
        if self.default is not None:
            patch['default'] = self.default

        return patch

    def to_ui_schema_patch(self) -> dict:
        """Convert to RJSF UI Schema properties.

        Returns:
            Dictionary of UI Schema properties for this field
        """
        ui_patch = {}

        if self.widget:
            ui_patch['ui:widget'] = self.widget
        if self.placeholder:
            ui_patch['ui:placeholder'] = self.placeholder
        if self.disabled:
            ui_patch['ui:disabled'] = True
        if self.readonly:
            ui_patch['ui:readonly'] = True
        if self.hidden:
            ui_patch['ui:widget'] = 'hidden'

        if self.ui_options:
            ui_patch['ui:options'] = self.ui_options

        return ui_patch


class RjsfConfigBuilder:
    """Builder for RJSF configurations with sensible defaults.

    This class helps construct RJSF specifications by providing a
    fluent interface for configuring fields.

    Example:
        >>> builder = RjsfConfigBuilder()
        >>> builder.field('email', RjsfFieldConfig(format='email'))
        >>> builder.field('message', RjsfFieldConfig(widget='textarea'))
        >>> spec = builder.build(base_schema)
    """

    def __init__(self):
        """Initialize the config builder."""
        self._field_configs: dict[str, RjsfFieldConfig] = {}
        self._ui_order: Optional[list[str]] = None
        self._class_names: Optional[str] = None

    def field(self, param_name: str, config: RjsfFieldConfig) -> 'RjsfConfigBuilder':
        """Configure a specific field.

        Args:
            param_name: Name of the parameter/field
            config: Configuration for the field

        Returns:
            Self for method chaining
        """
        self._field_configs[param_name] = config
        return self

    def order(self, field_order: list[str]) -> 'RjsfConfigBuilder':
        """Set the order of fields in the form.

        Args:
            field_order: List of field names in desired order

        Returns:
            Self for method chaining
        """
        self._ui_order = field_order
        return self

    def class_names(self, class_names: str) -> 'RjsfConfigBuilder':
        """Set CSS class names for the form.

        Args:
            class_names: Space-separated CSS class names

        Returns:
            Self for method chaining
        """
        self._class_names = class_names
        return self

    def build(self, base_schema: dict, base_ui_schema: Optional[dict] = None) -> dict:
        """Build the final RJSF specification.

        Args:
            base_schema: Base JSON Schema to augment
            base_ui_schema: Optional base UI Schema to augment

        Returns:
            Dictionary with 'schema' and 'uiSchema' keys
        """
        schema = base_schema.copy()
        ui_schema = (base_ui_schema or {}).copy()

        # Apply field configurations
        for field_name, config in self._field_configs.items():
            # Update schema properties
            if 'properties' in schema and field_name in schema['properties']:
                schema_patch = config.to_json_schema_patch()
                schema['properties'][field_name].update(schema_patch)

            # Update UI schema
            ui_patch = config.to_ui_schema_patch()
            if ui_patch:
                ui_schema[field_name] = {**ui_schema.get(field_name, {}), **ui_patch}

        # Apply UI order
        if self._ui_order:
            ui_schema['ui:order'] = self._ui_order

        # Apply class names
        if self._class_names:
            ui_schema['ui:classNames'] = self._class_names

        return {
            'schema': schema,
            'uiSchema': ui_schema,
        }


# Predefined field configurations for common use cases
COMMON_FIELD_CONFIGS = {
    'email': RjsfFieldConfig(
        widget='email',
        format='email',
        placeholder='user@example.com',
    ),
    'password': RjsfFieldConfig(
        widget='password',
    ),
    'url': RjsfFieldConfig(
        format='uri',
        placeholder='https://example.com',
    ),
    'multiline_text': RjsfFieldConfig(
        widget='textarea',
        ui_options={'rows': 5},
    ),
    'long_text': RjsfFieldConfig(
        widget='textarea',
        ui_options={'rows': 10},
    ),
    'date': RjsfFieldConfig(
        widget='date',
        format='date',
    ),
    'datetime': RjsfFieldConfig(
        widget='datetime',
        format='date-time',
    ),
    'color': RjsfFieldConfig(
        widget='color',
    ),
    'range': RjsfFieldConfig(
        widget='range',
    ),
    'file': RjsfFieldConfig(
        widget='file',
    ),
}


def get_field_config(config_name: str) -> RjsfFieldConfig:
    """Get a predefined field configuration by name.

    Args:
        config_name: Name of the configuration (e.g., 'email', 'multiline_text')

    Returns:
        RjsfFieldConfig instance

    Raises:
        KeyError: If config_name not found

    Example:
        >>> email_config = get_field_config('email')
        >>> email_config.format
        'email'
    """
    if config_name not in COMMON_FIELD_CONFIGS:
        raise KeyError(
            f"Unknown config '{config_name}'. "
            f"Available: {list(COMMON_FIELD_CONFIGS.keys())}"
        )
    return COMMON_FIELD_CONFIGS[config_name]


def apply_field_configs(
    schema: dict,
    ui_schema: dict,
    field_configs: dict[str, RjsfFieldConfig],
) -> tuple[dict, dict]:
    """Apply field configurations to existing schemas.

    Args:
        schema: JSON Schema to modify
        ui_schema: UI Schema to modify
        field_configs: Mapping of field names to configurations

    Returns:
        Tuple of (modified_schema, modified_ui_schema)

    Example:
        >>> configs = {
        ...     'email': get_field_config('email'),
        ...     'bio': get_field_config('multiline_text'),
        ... }
        >>> schema, ui_schema = apply_field_configs(schema, ui_schema, configs)
    """
    builder = RjsfConfigBuilder()
    for field_name, config in field_configs.items():
        builder.field(field_name, config)

    result = builder.build(schema, ui_schema)
    return result['schema'], result['uiSchema']


class ConditionalFieldConfig:
    """Configuration for conditional field display.

    Allows fields to be shown/hidden based on the values of other fields.

    Example:
        >>> # Show 'other_reason' field only when reason is 'other'
        >>> config = ConditionalFieldConfig(
        ...     'other_reason',
        ...     condition={'reason': {'const': 'other'}}
        ... )
    """

    def __init__(
        self,
        field_name: str,
        *,
        condition: dict,
        then_schema: Optional[dict] = None,
        else_schema: Optional[dict] = None,
    ):
        """Initialize conditional field configuration.

        Args:
            field_name: Name of the field to make conditional
            condition: JSON Schema condition (if/then/else style)
            then_schema: Schema to apply when condition is true
            else_schema: Schema to apply when condition is false
        """
        self.field_name = field_name
        self.condition = condition
        self.then_schema = then_schema
        self.else_schema = else_schema

    def to_json_schema(self) -> dict:
        """Convert to JSON Schema if/then/else structure.

        Returns:
            JSON Schema conditional structure
        """
        schema = {'if': self.condition}

        if self.then_schema:
            schema['then'] = self.then_schema

        if self.else_schema:
            schema['else'] = self.else_schema

        return schema
```

## uf/routes.py

```python
"""API routes for uf web interface.

Provides convenience routes for the web UI, including function listing,
spec retrieval, and the main HTML interface.
"""

from typing import Any, Callable
from collections.abc import Mapping


def add_ui_routes(
    app: Any,
    function_specs: Mapping,
    *,
    page_title: str = "Function Interface",
    custom_css: str = None,
    rjsf_theme: str = "default",
) -> None:
    """Add UI routes to a qh app.

    Adds the following routes:
    - GET / : Main UI page (HTML)
    - GET /api/functions : List available functions (JSON)
    - GET /api/functions/{name}/spec : Get RJSF spec for function (JSON)

    Args:
        app: The qh/bottle/fastapi app to add routes to
        function_specs: FunctionSpecStore with function specifications
        page_title: Title for the web interface
        custom_css: Optional custom CSS
        rjsf_theme: RJSF theme to use

    Note:
        This function detects whether the app is using Bottle or FastAPI
        and adds routes accordingly.
    """
    from uf.templates import generate_index_html, generate_error_page

    # Detect framework
    is_bottle = hasattr(app, 'route')
    is_fastapi = hasattr(app, 'get')

    if is_bottle:
        _add_bottle_routes(
            app,
            function_specs,
            page_title=page_title,
            custom_css=custom_css,
            rjsf_theme=rjsf_theme,
        )
    elif is_fastapi:
        _add_fastapi_routes(
            app,
            function_specs,
            page_title=page_title,
            custom_css=custom_css,
            rjsf_theme=rjsf_theme,
        )
    else:
        raise ValueError(f"Unsupported app type: {type(app)}")


def _add_bottle_routes(
    app,
    function_specs: Mapping,
    *,
    page_title: str,
    custom_css: str,
    rjsf_theme: str,
) -> None:
    """Add routes for Bottle framework."""
    from uf.templates import generate_index_html

    @app.route('/')
    def index():
        """Serve main UI page."""
        try:
            html = generate_index_html(
                function_specs,
                page_title=page_title,
                custom_css=custom_css,
                rjsf_theme=rjsf_theme,
            )
            return html
        except Exception as e:
            from uf.templates import generate_error_page
            return generate_error_page(str(e), 500)

    @app.route('/api/functions')
    def list_functions():
        """List all available functions."""
        import json
        from bottle import response

        response.content_type = 'application/json'

        try:
            func_list = [
                {
                    'name': name,
                    'description': spec.get('description', ''),
                }
                for name, spec in function_specs.items()
            ]
            return json.dumps(func_list)
        except Exception as e:
            response.status = 500
            return json.dumps({'error': str(e)})

    @app.route('/api/functions/<func_name>/spec')
    def get_function_spec(func_name):
        """Get RJSF specification for a function."""
        import json
        from bottle import response

        response.content_type = 'application/json'

        try:
            spec = function_specs[func_name]
            return json.dumps({
                'schema': spec['schema'],
                'uiSchema': spec['uiSchema'],
                'name': spec['name'],
                'description': spec['description'],
            })
        except KeyError:
            response.status = 404
            return json.dumps({'error': f"Function '{func_name}' not found"})
        except Exception as e:
            response.status = 500
            return json.dumps({'error': str(e)})


def _add_fastapi_routes(
    app,
    function_specs: Mapping,
    *,
    page_title: str,
    custom_css: str,
    rjsf_theme: str,
) -> None:
    """Add routes for FastAPI framework."""
    from fastapi.responses import HTMLResponse, JSONResponse
    from uf.templates import generate_index_html

    @app.get('/', response_class=HTMLResponse)
    async def index():
        """Serve main UI page."""
        try:
            html = generate_index_html(
                function_specs,
                page_title=page_title,
                custom_css=custom_css,
                rjsf_theme=rjsf_theme,
            )
            return html
        except Exception as e:
            from uf.templates import generate_error_page
            return HTMLResponse(
                content=generate_error_page(str(e), 500),
                status_code=500
            )

    @app.get('/api/functions')
    async def list_functions():
        """List all available functions."""
        try:
            func_list = [
                {
                    'name': name,
                    'description': spec.get('description', ''),
                }
                for name, spec in function_specs.items()
            ]
            return JSONResponse(content=func_list)
        except Exception as e:
            return JSONResponse(
                content={'error': str(e)},
                status_code=500
            )

    @app.get('/api/functions/{func_name}/spec')
    async def get_function_spec(func_name: str):
        """Get RJSF specification for a function."""
        try:
            spec = function_specs[func_name]
            return JSONResponse(content={
                'schema': spec['schema'],
                'uiSchema': spec['uiSchema'],
                'name': spec['name'],
                'description': spec['description'],
            })
        except KeyError:
            return JSONResponse(
                content={'error': f"Function '{func_name}' not found"},
                status_code=404
            )
        except Exception as e:
            return JSONResponse(
                content={'error': str(e)},
                status_code=500
            )


def create_function_handler(func: Callable, func_name: str) -> Callable:
    """Create a request handler for a function.

    This wraps the function to handle HTTP requests and responses.

    Args:
        func: The function to wrap
        func_name: Name of the function

    Returns:
        A handler function compatible with web frameworks
    """
    def handler(**kwargs):
        """Handle function execution from HTTP request."""
        try:
            result = func(**kwargs)
            return {'result': result, 'success': True}
        except Exception as e:
            return {
                'error': str(e),
                'success': False,
                'error_type': type(e).__name__,
            }

    handler.__name__ = func_name
    handler.__doc__ = func.__doc__
    return handler
```

## uf/specs.py

```python
"""Function specification management for uf.

Provides a Mapping-based interface to function specifications, including RJSF
form specs and OpenAPI schemas.
"""

from typing import Callable, Iterable, Optional, Any
from collections.abc import Mapping
from functools import cached_property


class FunctionSpecStore(Mapping):
    """A mapping from function names to their RJSF specifications.

    Lazily generates and caches form specs for each function.

    Args:
        funcs: Iterable of callable functions to generate specs for
        rjsf_config: Optional configuration dict for RJSF generation
        ui_schema_factory: Optional callable to customize UI schema generation
        param_to_prop_type: Optional callable to map parameters to property types

    Example:
        >>> def add(x: int, y: int) -> int:
        ...     '''Add two numbers'''
        ...     return x + y
        >>> specs = FunctionSpecStore([add])
        >>> 'add' in specs
        True
        >>> spec = specs['add']
        >>> 'schema' in spec
        True
    """

    def __init__(
        self,
        funcs: Iterable[Callable],
        *,
        rjsf_config: Optional[dict] = None,
        ui_schema_factory: Optional[Callable] = None,
        param_to_prop_type: Optional[Callable] = None,
    ):
        self._funcs = {f.__name__: f for f in funcs}
        self._rjsf_config = rjsf_config or {}
        self._ui_schema_factory = ui_schema_factory
        self._param_to_prop_type = param_to_prop_type
        self._spec_cache = {}

    def __getitem__(self, func_name: str) -> dict:
        """Get RJSF spec for a function.

        Args:
            func_name: Name of the function

        Returns:
            Dictionary containing the RJSF specification with keys:
            - 'schema': JSON Schema for the function inputs
            - 'uiSchema': UI Schema for rendering hints
            - 'func': The original function object

        Raises:
            KeyError: If function name not found
        """
        if func_name not in self._funcs:
            raise KeyError(f"Function '{func_name}' not found")

        if func_name not in self._spec_cache:
            self._spec_cache[func_name] = self._generate_spec(func_name)

        return self._spec_cache[func_name]

    def __iter__(self):
        """Iterate over function names."""
        return iter(self._funcs)

    def __len__(self):
        """Return number of functions."""
        return len(self._funcs)

    def _generate_spec(self, func_name: str) -> dict:
        """Generate RJSF specification for a function.

        Args:
            func_name: Name of the function to generate spec for

        Returns:
            Dictionary with schema, uiSchema, and function reference
        """
        func = self._funcs[func_name]

        try:
            # Import ju.rjsf for form spec generation
            from ju.rjsf import func_to_form_spec

            # Generate form spec
            form_spec = func_to_form_spec(
                func,
                **self._rjsf_config
            )

            # Apply custom UI schema factory if provided
            if self._ui_schema_factory:
                ui_schema = self._ui_schema_factory(func)
                if 'uiSchema' in form_spec:
                    form_spec['uiSchema'].update(ui_schema)
                else:
                    form_spec['uiSchema'] = ui_schema

            return {
                'schema': form_spec.get('schema', {}),
                'uiSchema': form_spec.get('uiSchema', {}),
                'func': func,
                'name': func_name,
                'description': func.__doc__ or f"Execute {func_name}",
            }

        except ImportError:
            # Fallback to basic spec if ju.rjsf not available
            return self._generate_basic_spec(func_name, func)

    def _generate_basic_spec(self, func_name: str, func: Callable) -> dict:
        """Generate a basic specification without ju.rjsf.

        This is a fallback for when ju.rjsf is not available. It creates
        a minimal JSON Schema from function signature.

        Args:
            func_name: Name of the function
            func: The function object

        Returns:
            Basic specification dictionary
        """
        import inspect

        sig = inspect.signature(func)
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param.default is inspect.Parameter.empty:
                required.append(param_name)

            # Basic type mapping
            param_type = "string"  # default
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"

            properties[param_name] = {"type": param_type}

        return {
            'schema': {
                'type': 'object',
                'properties': properties,
                'required': required,
                'title': func_name,
                'description': func.__doc__ or '',
            },
            'uiSchema': {},
            'func': func,
            'name': func_name,
            'description': func.__doc__ or f"Execute {func_name}",
        }

    @cached_property
    def function_list(self) -> list[dict]:
        """Get list of all functions with basic metadata.

        Returns:
            List of dictionaries with function name and description
        """
        return [
            {
                'name': name,
                'description': func.__doc__ or f"Execute {name}",
            }
            for name, func in self._funcs.items()
        ]

    def get_func(self, func_name: str) -> Callable:
        """Get the original function object by name.

        Args:
            func_name: Name of the function

        Returns:
            The function object

        Raises:
            KeyError: If function name not found
        """
        return self._funcs[func_name]
```

## uf/templates.py

```python
"""HTML template generation for uf web interface.

Provides functions to generate the web UI that lists functions and displays
RJSF forms for interacting with them.
"""

from typing import Optional
from collections.abc import Mapping


def generate_index_html(
    function_specs: Mapping,
    *,
    page_title: str = "Function Interface",
    custom_css: Optional[str] = None,
    rjsf_theme: str = "default",
    base_url: str = "",
) -> str:
    """Generate HTML page with RJSF forms for functions.

    Creates a single-page application with:
    - Function list/navigation sidebar
    - RJSF form for selected function
    - Result display area
    - Uses React and RJSF from CDN (no build step required)

    Args:
        function_specs: Mapping from function names to their specs
        page_title: Title for the HTML page
        custom_css: Optional custom CSS to inject
        rjsf_theme: RJSF theme to use ('default', 'material-ui', 'semantic-ui')
        base_url: Base URL for API endpoints

    Returns:
        Complete HTML string for the web interface
    """
    # Get function list for sidebar
    func_list = []
    for name in function_specs:
        spec = function_specs[name]
        func_list.append({
            'name': name,
            'description': spec.get('description', f"Execute {name}")
        })

    # Generate function list HTML
    func_list_html = "\n".join([
        f'''
        <div class="function-item" onclick="loadFunction('{func['name']}')">
            <div class="function-name">{func['name']}</div>
            <div class="function-desc">{func['description'][:100]}</div>
        </div>
        '''
        for func in func_list
    ])

    custom_styles = custom_css or ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>

    <!-- React and ReactDOM -->
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>

    <!-- RJSF and dependencies -->
    <script src="https://unpkg.com/@rjsf/core@5/dist/react-jsonschema-form.js"></script>
    <script src="https://unpkg.com/@rjsf/validator-ajv8@5/dist/react-jsonschema-form-validator-ajv8.js"></script>

    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            display: flex;
            height: 100vh;
            overflow: hidden;
        }}

        #sidebar {{
            width: 300px;
            background: #f5f5f5;
            border-right: 1px solid #ddd;
            overflow-y: auto;
            padding: 20px;
        }}

        #main {{
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        #header {{
            background: #fff;
            border-bottom: 1px solid #ddd;
            padding: 20px 30px;
        }}

        #header h1 {{
            font-size: 24px;
            margin-bottom: 5px;
        }}

        #header .subtitle {{
            color: #666;
            font-size: 14px;
        }}

        #content {{
            flex: 1;
            overflow-y: auto;
            padding: 30px;
        }}

        .function-item {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .function-item:hover {{
            background: #f0f0f0;
            border-color: #4CAF50;
        }}

        .function-item.active {{
            background: #4CAF50;
            color: white;
            border-color: #4CAF50;
        }}

        .function-name {{
            font-weight: 600;
            margin-bottom: 4px;
        }}

        .function-desc {{
            font-size: 12px;
            color: #666;
            line-height: 1.4;
        }}

        .function-item.active .function-desc {{
            color: rgba(255, 255, 255, 0.9);
        }}

        #form-container {{
            max-width: 800px;
        }}

        .form-section {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 20px;
        }}

        .form-section h2 {{
            margin-bottom: 10px;
            font-size: 20px;
        }}

        .form-section .description {{
            color: #666;
            margin-bottom: 20px;
            line-height: 1.6;
        }}

        #result {{
            background: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 20px;
            margin-top: 20px;
            display: none;
        }}

        #result.success {{
            background: #e8f5e9;
            border-color: #4CAF50;
        }}

        #result.error {{
            background: #ffebee;
            border-color: #f44336;
        }}

        #result h3 {{
            margin-bottom: 10px;
        }}

        #result pre {{
            background: white;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}

        .loading {{
            display: none;
            text-align: center;
            padding: 20px;
            color: #666;
        }}

        .loading.active {{
            display: block;
        }}

        button[type="submit"] {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.2s;
        }}

        button[type="submit"]:hover {{
            background: #45a049;
        }}

        {custom_styles}
    </style>
</head>
<body>
    <div id="sidebar">
        <h2 style="margin-bottom: 15px;">Functions</h2>
        {func_list_html}
    </div>

    <div id="main">
        <div id="header">
            <h1>{page_title}</h1>
            <div class="subtitle">Select a function from the sidebar to get started</div>
        </div>

        <div id="content">
            <div id="form-container"></div>
            <div id="loading" class="loading">Processing...</div>
            <div id="result"></div>
        </div>
    </div>

    <script>
        const {{ useState, useEffect }} = React;
        const Form = JSONSchemaForm.default;
        const validator = JSONSchemaFormValidator.default;

        let currentFunction = null;

        function FunctionForm({{ funcName }}) {{
            const [schema, setSchema] = useState(null);
            const [uiSchema, setUiSchema] = useState({{}});
            const [loading, setLoading] = useState(true);

            useEffect(() => {{
                // Load function spec
                fetch(`{base_url}/api/functions/${{funcName}}/spec`)
                    .then(res => res.json())
                    .then(data => {{
                        setSchema(data.schema);
                        setUiSchema(data.uiSchema || {{}});
                        setLoading(false);
                    }})
                    .catch(err => {{
                        console.error('Error loading spec:', err);
                        setLoading(false);
                    }});
            }}, [funcName]);

            const handleSubmit = ({{ formData }}) => {{
                const resultDiv = document.getElementById('result');
                const loadingDiv = document.getElementById('loading');

                resultDiv.style.display = 'none';
                loadingDiv.classList.add('active');

                fetch(`{base_url}/${{funcName}}`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(formData)
                }})
                .then(res => {{
                    if (!res.ok) {{
                        return res.json().then(err => {{ throw err; }});
                    }}
                    return res.json();
                }})
                .then(data => {{
                    loadingDiv.classList.remove('active');
                    resultDiv.className = 'success';
                    resultDiv.innerHTML = `
                        <h3>Result</h3>
                        <pre>${{JSON.stringify(data, null, 2)}}</pre>
                    `;
                    resultDiv.style.display = 'block';
                }})
                .catch(err => {{
                    loadingDiv.classList.remove('active');
                    resultDiv.className = 'error';
                    resultDiv.innerHTML = `
                        <h3>Error</h3>
                        <pre>${{JSON.stringify(err, null, 2)}}</pre>
                    `;
                    resultDiv.style.display = 'block';
                }});
            }};

            if (loading) {{
                return React.createElement('div', {{ className: 'loading active' }}, 'Loading form...');
            }}

            if (!schema) {{
                return React.createElement('div', null, 'Error loading function specification');
            }}

            return React.createElement('div', {{ className: 'form-section' }},
                React.createElement('h2', null, funcName),
                React.createElement('div', {{ className: 'description' }}, schema.description || ''),
                React.createElement(Form, {{
                    schema: schema,
                    uiSchema: uiSchema,
                    validator: validator,
                    onSubmit: handleSubmit
                }})
            );
        }}

        function loadFunction(funcName) {{
            currentFunction = funcName;

            // Update sidebar active state
            document.querySelectorAll('.function-item').forEach(item => {{
                item.classList.remove('active');
            }});
            event.currentTarget.classList.add('active');

            // Clear previous results
            document.getElementById('result').style.display = 'none';

            // Render form
            const container = document.getElementById('form-container');
            const root = ReactDOM.createRoot(container);
            root.render(React.createElement(FunctionForm, {{ funcName }}));
        }}
    </script>
</body>
</html>"""

    return html


def generate_error_page(error_message: str, status_code: int = 500) -> str:
    """Generate a simple error page.

    Args:
        error_message: Error message to display
        status_code: HTTP status code

    Returns:
        HTML string for error page
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error {status_code}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            background: #f5f5f5;
        }}
        .error-container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 500px;
        }}
        h1 {{
            color: #f44336;
            margin-bottom: 20px;
        }}
        p {{
            color: #666;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <h1>Error {status_code}</h1>
        <p>{error_message}</p>
    </div>
</body>
</html>"""
```

## uf/testing.py

```python
"""Testing utilities for uf applications.

Provides tools for testing uf apps, including test clients, fixtures,
and assertion helpers.
"""

from typing import Callable, Any, Optional
from contextlib import contextmanager
import json


class UfTestClient:
    """Test client for uf applications.

    Provides a convenient interface for testing uf apps without
    running a web server.

    Example:
        >>> from uf import mk_rjsf_app
        >>> app = mk_rjsf_app([my_func])
        >>> client = UfTestClient(app)
        >>> response = client.call_function('my_func', {'x': 10, 'y': 20})
        >>> assert response['success']
    """

    def __init__(self, app):
        """Initialize test client.

        Args:
            app: The uf application to test
        """
        self.app = app
        self.function_specs = getattr(app, 'function_specs', None)

    def list_functions(self) -> list[str]:
        """Get list of available function names.

        Returns:
            List of function name strings
        """
        if self.function_specs:
            return list(self.function_specs.keys())
        return []

    def get_spec(self, func_name: str) -> dict:
        """Get RJSF specification for a function.

        Args:
            func_name: Name of the function

        Returns:
            Function specification dict

        Raises:
            KeyError: If function not found
        """
        if not self.function_specs:
            raise ValueError("App does not have function_specs")

        return self.function_specs[func_name]

    def call_function(
        self,
        func_name: str,
        params: dict,
        *,
        expect_success: bool = True,
    ) -> dict:
        """Call a function with the given parameters.

        Args:
            func_name: Name of the function to call
            params: Dictionary of parameters
            expect_success: Whether to expect success (raises on failure)

        Returns:
            Result dictionary with 'success' and 'result' or 'error'

        Raises:
            AssertionError: If expect_success=True and call fails
        """
        if not self.function_specs:
            raise ValueError("App does not have function_specs")

        spec = self.function_specs[func_name]
        func = spec['func']

        try:
            result = func(**params)
            response = {'success': True, 'result': result}
        except Exception as e:
            response = {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__,
            }

        if expect_success and not response['success']:
            raise AssertionError(
                f"Function call failed: {response['error']}"
            )

        return response

    def validate_params(self, func_name: str, params: dict) -> tuple[bool, Optional[str]]:
        """Validate parameters against function schema.

        Args:
            func_name: Name of the function
            params: Parameters to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            spec = self.get_spec(func_name)
            schema = spec['schema']

            # Check required parameters
            required = schema.get('required', [])
            for req_param in required:
                if req_param not in params:
                    return False, f"Missing required parameter: {req_param}"

            # Basic type checking
            properties = schema.get('properties', {})
            for param_name, value in params.items():
                if param_name not in properties:
                    return False, f"Unknown parameter: {param_name}"

                param_schema = properties[param_name]
                expected_type = param_schema.get('type')

                if expected_type:
                    if not self._check_type(value, expected_type):
                        return (
                            False,
                            f"Parameter {param_name} has wrong type. "
                            f"Expected {expected_type}, got {type(value).__name__}",
                        )

            return True, None

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def _check_type(self, value: Any, json_type: str) -> bool:
        """Check if value matches JSON Schema type.

        Args:
            value: Value to check
            json_type: JSON Schema type name

        Returns:
            True if types match
        """
        type_map = {
            'string': str,
            'number': (int, float),
            'integer': int,
            'boolean': bool,
            'array': list,
            'object': dict,
            'null': type(None),
        }

        expected_types = type_map.get(json_type)
        if expected_types is None:
            return True  # Unknown type, allow it

        return isinstance(value, expected_types)


class UfAppTester:
    """Context manager for testing uf apps.

    Provides a testing context with common utilities and assertions.

    Example:
        >>> with UfAppTester(app) as tester:
        ...     result = tester.submit_form('add', {'x': 10, 'y': 20})
        ...     tester.assert_success(result)
        ...     tester.assert_result_equals(result, 30)
    """

    def __init__(self, app):
        """Initialize the app tester.

        Args:
            app: The uf application to test
        """
        self.app = app
        self.client = UfTestClient(app)
        self._results_history: list[dict] = []

    def __enter__(self) -> 'UfAppTester':
        """Enter the testing context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the testing context."""
        pass

    def submit_form(self, func_name: str, form_data: dict) -> dict:
        """Simulate form submission.

        Args:
            func_name: Name of the function
            form_data: Form data as dictionary

        Returns:
            Result dictionary
        """
        result = self.client.call_function(func_name, form_data, expect_success=False)
        self._results_history.append(result)
        return result

    def assert_success(self, result: dict, message: str = ""):
        """Assert that a result indicates success.

        Args:
            result: Result dictionary
            message: Optional custom error message

        Raises:
            AssertionError: If result is not successful
        """
        msg = message or f"Expected success but got error: {result.get('error')}"
        assert result.get('success'), msg

    def assert_failure(self, result: dict, message: str = ""):
        """Assert that a result indicates failure.

        Args:
            result: Result dictionary
            message: Optional custom error message

        Raises:
            AssertionError: If result is successful
        """
        msg = message or "Expected failure but got success"
        assert not result.get('success'), msg

    def assert_result_equals(self, result: dict, expected: Any):
        """Assert that result value equals expected.

        Args:
            result: Result dictionary
            expected: Expected value

        Raises:
            AssertionError: If values don't match
        """
        self.assert_success(result)
        actual = result.get('result')
        assert actual == expected, f"Expected {expected}, got {actual}"

    def assert_error_type(self, result: dict, error_type: str):
        """Assert that error type matches.

        Args:
            result: Result dictionary
            error_type: Expected error type name

        Raises:
            AssertionError: If error types don't match
        """
        self.assert_failure(result)
        actual_type = result.get('error_type')
        assert actual_type == error_type, f"Expected {error_type}, got {actual_type}"

    def get_history(self) -> list[dict]:
        """Get history of all results.

        Returns:
            List of result dictionaries
        """
        return self._results_history.copy()


def test_ui_function(
    func: Callable,
    test_inputs: dict,
    *,
    expected_output: Any = None,
    expected_exception: Optional[type] = None,
) -> bool:
    """Test a function with form-like input.

    Args:
        func: Function to test
        test_inputs: Dictionary of test parameters
        expected_output: Expected return value (if any)
        expected_exception: Expected exception type (if any)

    Returns:
        True if test passes

    Raises:
        AssertionError: If test fails

    Example:
        >>> def add(x: int, y: int) -> int:
        ...     return x + y
        >>> test_ui_function(add, {'x': 10, 'y': 20}, expected_output=30)
        True
    """
    if expected_exception:
        try:
            func(**test_inputs)
            raise AssertionError(f"Expected {expected_exception.__name__} but no exception was raised")
        except expected_exception:
            return True
        except Exception as e:
            raise AssertionError(
                f"Expected {expected_exception.__name__} but got {type(e).__name__}: {e}"
            )
    else:
        result = func(**test_inputs)

        if expected_output is not None:
            assert result == expected_output, f"Expected {expected_output}, got {result}"

        return True


@contextmanager
def mock_function_response(app, func_name: str, mock_result: Any):
    """Context manager to mock a function's response.

    Args:
        app: The uf application
        func_name: Name of function to mock
        mock_result: Value to return

    Yields:
        None

    Example:
        >>> with mock_function_response(app, 'get_user', {'name': 'Test'}):
        ...     # Calls to get_user will return {'name': 'Test'}
        ...     result = client.call_function('get_user', {'id': 1})
    """
    if not hasattr(app, 'function_specs'):
        raise ValueError("App does not have function_specs")

    spec = app.function_specs[func_name]
    original_func = spec['func']

    # Create mock function
    def mock_func(**kwargs):
        return mock_result

    # Replace function
    spec['func'] = mock_func

    try:
        yield
    finally:
        # Restore original function
        spec['func'] = original_func


class FormDataBuilder:
    """Builder for constructing form data for tests.

    Provides a fluent interface for building test form data.

    Example:
        >>> form_data = (
        ...     FormDataBuilder()
        ...     .field('name', 'John Doe')
        ...     .field('email', 'john@example.com')
        ...     .field('age', 30)
        ...     .build()
        ... )
    """

    def __init__(self):
        """Initialize the builder."""
        self._data: dict = {}

    def field(self, name: str, value: Any) -> 'FormDataBuilder':
        """Add a field to the form data.

        Args:
            name: Field name
            value: Field value

        Returns:
            Self for method chaining
        """
        self._data[name] = value
        return self

    def fields(self, **kwargs) -> 'FormDataBuilder':
        """Add multiple fields at once.

        Args:
            **kwargs: Field name-value pairs

        Returns:
            Self for method chaining
        """
        self._data.update(kwargs)
        return self

    def build(self) -> dict:
        """Build and return the form data.

        Returns:
            Dictionary of form data
        """
        return self._data.copy()


def assert_valid_rjsf_spec(spec: dict):
    """Assert that a specification is valid RJSF format.

    Args:
        spec: The specification to validate

    Raises:
        AssertionError: If spec is invalid
    """
    assert 'schema' in spec, "Spec must have 'schema' key"
    assert isinstance(spec['schema'], dict), "Schema must be a dict"

    schema = spec['schema']
    assert 'type' in schema, "Schema must have 'type'"
    assert 'properties' in schema, "Schema must have 'properties'"
    assert isinstance(schema['properties'], dict), "Properties must be a dict"


def assert_has_field(spec: dict, field_name: str):
    """Assert that a spec has a specific field.

    Args:
        spec: The specification
        field_name: Name of the field to check

    Raises:
        AssertionError: If field not found
    """
    assert_valid_rjsf_spec(spec)
    properties = spec['schema']['properties']
    assert field_name in properties, f"Field '{field_name}' not found in schema"


def assert_field_type(spec: dict, field_name: str, expected_type: str):
    """Assert that a field has the expected type.

    Args:
        spec: The specification
        field_name: Name of the field
        expected_type: Expected JSON Schema type

    Raises:
        AssertionError: If type doesn't match
    """
    assert_has_field(spec, field_name)
    field_schema = spec['schema']['properties'][field_name]
    actual_type = field_schema.get('type')
    assert actual_type == expected_type, f"Expected type '{expected_type}', got '{actual_type}'"


def assert_field_required(spec: dict, field_name: str):
    """Assert that a field is required.

    Args:
        spec: The specification
        field_name: Name of the field

    Raises:
        AssertionError: If field is not required
    """
    assert_has_field(spec, field_name)
    required = spec['schema'].get('required', [])
    assert field_name in required, f"Field '{field_name}' is not required"
```

## uf/themes.py

```python
"""Theme and styling support for uf.

Provides built-in themes, dark mode support, and theme customization.
"""

from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Theme:
    """UI theme configuration.

    Attributes:
        name: Theme name
        colors: Color palette
        fonts: Font configuration
        css: Additional custom CSS
    """

    name: str
    colors: dict[str, str] = field(default_factory=dict)
    fonts: dict[str, str] = field(default_factory=dict)
    css: str = ""

    def to_css(self) -> str:
        """Convert theme to CSS.

        Returns:
            CSS string
        """
        css_vars = []

        # Add color variables
        for key, value in self.colors.items():
            css_vars.append(f"  --color-{key}: {value};")

        # Add font variables
        for key, value in self.fonts.items():
            css_vars.append(f"  --font-{key}: {value};")

        css = ":root {\n" + "\n".join(css_vars) + "\n}\n\n" + self.css

        return css


# Built-in theme definitions

LIGHT_THEME = Theme(
    name="light",
    colors={
        "primary": "#4CAF50",
        "secondary": "#2196F3",
        "success": "#4CAF50",
        "error": "#f44336",
        "warning": "#ff9800",
        "info": "#2196F3",
        "background": "#ffffff",
        "surface": "#f5f5f5",
        "text": "#212121",
        "text-secondary": "#666666",
        "border": "#dddddd",
    },
    fonts={
        "main": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "mono": "'Courier New', Courier, monospace",
    },
)


DARK_THEME = Theme(
    name="dark",
    colors={
        "primary": "#66BB6A",
        "secondary": "#42A5F5",
        "success": "#66BB6A",
        "error": "#EF5350",
        "warning": "#FFA726",
        "info": "#42A5F5",
        "background": "#1e1e1e",
        "surface": "#2d2d2d",
        "text": "#e0e0e0",
        "text-secondary": "#b0b0b0",
        "border": "#404040",
    },
    fonts={
        "main": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "mono": "'Courier New', Courier, monospace",
    },
    css="""
body {
    background-color: var(--color-background);
    color: var(--color-text);
}

#sidebar {
    background-color: var(--color-surface);
    border-right-color: var(--color-border);
}

#header {
    background-color: var(--color-surface);
    border-bottom-color: var(--color-border);
    color: var(--color-text);
}

.function-item {
    background-color: var(--color-background);
    border-color: var(--color-border);
    color: var(--color-text);
}

.function-item:hover {
    background-color: var(--color-surface);
}

.function-item.active {
    background-color: var(--color-primary);
    color: white;
}

.form-section {
    background-color: var(--color-surface);
    border-color: var(--color-border);
}

#result {
    background-color: var(--color-surface);
    border-color: var(--color-border);
}

#result.success {
    background-color: rgba(102, 187, 106, 0.1);
    border-color: var(--color-success);
}

#result.error {
    background-color: rgba(239, 83, 80, 0.1);
    border-color: var(--color-error);
}

input, textarea, select {
    background-color: var(--color-background);
    border-color: var(--color-border);
    color: var(--color-text);
}

button[type="submit"] {
    background-color: var(--color-primary);
}

button[type="submit"]:hover {
    background-color: var(--color-secondary);
}
""",
)


OCEAN_THEME = Theme(
    name="ocean",
    colors={
        "primary": "#00BCD4",
        "secondary": "#009688",
        "success": "#4CAF50",
        "error": "#f44336",
        "warning": "#FF5722",
        "info": "#03A9F4",
        "background": "#f0f8ff",
        "surface": "#e1f5fe",
        "text": "#01579B",
        "text-secondary": "#0277BD",
        "border": "#B3E5FC",
    },
    fonts={
        "main": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "mono": "'Courier New', Courier, monospace",
    },
    css="""
body {
    background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
}

.function-item.active {
    background: linear-gradient(135deg, #00BCD4 0%, #009688 100%);
}
""",
)


SUNSET_THEME = Theme(
    name="sunset",
    colors={
        "primary": "#FF6F00",
        "secondary": "#F4511E",
        "success": "#558B2F",
        "error": "#C62828",
        "warning": "#F57C00",
        "info": "#1976D2",
        "background": "#FFF3E0",
        "surface": "#FFE0B2",
        "text": "#E65100",
        "text-secondary": "#EF6C00",
        "border": "#FFCC80",
    },
    fonts={
        "main": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "mono": "'Courier New', Courier, monospace",
    },
    css="""
body {
    background: linear-gradient(135deg, #FFE0B2 0%, #FFCC80 100%);
}

.function-item.active {
    background: linear-gradient(135deg, #FF6F00 0%, #F4511E 100%);
}
""",
)


# Theme registry
BUILT_IN_THEMES = {
    "light": LIGHT_THEME,
    "dark": DARK_THEME,
    "ocean": OCEAN_THEME,
    "sunset": SUNSET_THEME,
}


def get_theme(name: str) -> Optional[Theme]:
    """Get a built-in theme by name.

    Args:
        name: Theme name

    Returns:
        Theme object or None

    Example:
        >>> theme = get_theme('dark')
        >>> css = theme.to_css()
    """
    return BUILT_IN_THEMES.get(name)


def generate_theme_toggle_js() -> str:
    """Generate JavaScript for theme toggling.

    Returns:
        JavaScript code for theme switching
    """
    js = """
// Theme toggle functionality
(function() {
    const THEME_KEY = 'uf-theme';
    const DEFAULT_THEME = 'light';

    function getTheme() {
        return localStorage.getItem(THEME_KEY) || DEFAULT_THEME;
    }

    function setTheme(theme) {
        localStorage.setItem(THEME_KEY, theme);
        document.body.setAttribute('data-theme', theme);

        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('themechange', {
            detail: { theme }
        }));
    }

    function toggleTheme() {
        const current = getTheme();
        const next = current === 'light' ? 'dark' : 'light';
        setTheme(next);
    }

    // Initialize theme on load
    window.addEventListener('load', function() {
        const theme = getTheme();
        document.body.setAttribute('data-theme', theme);
    });

    // Expose functions globally
    window.ufTheme = {
        get: getTheme,
        set: setTheme,
        toggle: toggleTheme
    };
})();
"""
    return js


def create_theme_toggle_button() -> str:
    """Create HTML for theme toggle button.

    Returns:
        HTML string for theme toggle button
    """
    html = """
<button id="theme-toggle" onclick="window.ufTheme.toggle()"
        style="position: fixed; top: 10px; right: 10px; z-index: 1000;
               padding: 10px 15px; border: none; border-radius: 5px;
               cursor: pointer; background: var(--color-surface);
               color: var(--color-text); font-size: 20px;">
    🌓
</button>
<script>
    // Update button on theme change
    window.addEventListener('themechange', function(e) {
        const btn = document.getElementById('theme-toggle');
        btn.textContent = e.detail.theme === 'light' ? '🌙' : '☀️';
    });

    // Set initial icon
    const btn = document.getElementById('theme-toggle');
    btn.textContent = window.ufTheme.get() === 'light' ? '🌙' : '☀️';
</script>
"""
    return html


class ThemeConfig:
    """Configuration for theme system.

    Example:
        >>> config = ThemeConfig(
        ...     default_theme='dark',
        ...     allow_toggle=True,
        ...     available_themes=['light', 'dark', 'ocean']
        ... )
    """

    def __init__(
        self,
        default_theme: str = 'light',
        allow_toggle: bool = True,
        available_themes: Optional[list[str]] = None,
        custom_theme: Optional[Theme] = None,
    ):
        """Initialize theme config.

        Args:
            default_theme: Default theme name
            allow_toggle: Allow users to toggle theme
            available_themes: List of available theme names
            custom_theme: Optional custom theme
        """
        self.default_theme = default_theme
        self.allow_toggle = allow_toggle
        self.available_themes = available_themes or ['light', 'dark']
        self.custom_theme = custom_theme

    def get_css(self) -> str:
        """Get CSS for all available themes.

        Returns:
            Combined CSS string
        """
        css_parts = []

        # Add light theme as default
        light = get_theme('light')
        if light:
            css_parts.append(light.to_css())

        # Add dark theme
        dark = get_theme('dark')
        if dark:
            css_parts.append(f"\nbody[data-theme='dark'] {{\n")
            css_parts.append(dark.to_css())
            css_parts.append("}\n")

        # Add other themes
        for theme_name in self.available_themes:
            if theme_name in ['light', 'dark']:
                continue
            theme = get_theme(theme_name)
            if theme:
                css_parts.append(f"\nbody[data-theme='{theme_name}'] {{\n")
                css_parts.append(theme.to_css())
                css_parts.append("}\n")

        # Add custom theme
        if self.custom_theme:
            css_parts.append(f"\nbody[data-theme='{self.custom_theme.name}'] {{\n")
            css_parts.append(self.custom_theme.to_css())
            css_parts.append("}\n")

        return "\n".join(css_parts)

    def get_js(self) -> str:
        """Get JavaScript for theme functionality.

        Returns:
            JavaScript string
        """
        js = generate_theme_toggle_js()

        # Set default theme
        js += f"\nwindow.ufTheme.set(window.ufTheme.get() || '{self.default_theme}');\n"

        return js

    def get_toggle_button_html(self) -> str:
        """Get HTML for theme toggle button.

        Returns:
            HTML string or empty if toggle not allowed
        """
        if not self.allow_toggle:
            return ""

        return create_theme_toggle_button()
```

## uf/trans.py

```python
"""Input transformation integration for uf.

Provides a registry for custom type transformations that bridges between
RJSF form data and qh's input transformation system.
"""

from typing import Callable, Optional, Any, Type
from collections.abc import Mapping
from uf.rjsf_config import RjsfFieldConfig


class InputTransformRegistry:
    """Registry for custom type transformations.

    Integrates with qh's type registry and extends it for UI needs,
    allowing custom types to be properly handled in both the form
    interface and the HTTP service layer.

    Example:
        >>> from datetime import datetime
        >>> registry = InputTransformRegistry()
        >>>
        >>> # Register a custom type
        >>> registry.register_type(
        ...     datetime,
        ...     to_json=lambda dt: dt.isoformat(),
        ...     from_json=lambda s: datetime.fromisoformat(s),
        ...     ui_widget='datetime'
        ... )
    """

    def __init__(self):
        """Initialize the transformation registry."""
        self._type_handlers: dict[Type, dict] = {}

    def register_type(
        self,
        py_type: Type,
        *,
        to_json: Optional[Callable[[Any], Any]] = None,
        from_json: Optional[Callable[[Any], Any]] = None,
        ui_widget: Optional[str] = None,
        ui_config: Optional[RjsfFieldConfig] = None,
        json_schema_type: Optional[str] = None,
        json_schema_format: Optional[str] = None,
    ) -> None:
        """Register a type with both qh and UI configuration.

        Args:
            py_type: Python type to register
            to_json: Function to convert Python type to JSON-serializable
            from_json: Function to convert JSON to Python type
            ui_widget: RJSF widget to use for this type
            ui_config: Full RjsfFieldConfig for this type
            json_schema_type: JSON Schema type (e.g., 'string', 'number')
            json_schema_format: JSON Schema format (e.g., 'date-time', 'email')

        Example:
            >>> from pathlib import Path
            >>> registry.register_type(
            ...     Path,
            ...     to_json=str,
            ...     from_json=Path,
            ...     ui_widget='text',
            ...     json_schema_type='string'
            ... )
        """
        handler = {
            'to_json': to_json or (lambda x: x),
            'from_json': from_json or (lambda x: x),
        }

        # Build UI config
        if ui_config:
            handler['ui_config'] = ui_config
        else:
            # Build from individual params
            config = RjsfFieldConfig(widget=ui_widget)
            if json_schema_format:
                config.format = json_schema_format
            handler['ui_config'] = config

        if json_schema_type:
            handler['json_schema_type'] = json_schema_type
        if json_schema_format:
            handler['json_schema_format'] = json_schema_format

        self._type_handlers[py_type] = handler

    def get_handler(self, py_type: Type) -> Optional[dict]:
        """Get handler for a type.

        Args:
            py_type: Python type to look up

        Returns:
            Handler dict or None if not registered
        """
        return self._type_handlers.get(py_type)

    def get_ui_config(self, py_type: Type) -> Optional[RjsfFieldConfig]:
        """Get UI configuration for a type.

        Args:
            py_type: Python type to look up

        Returns:
            RjsfFieldConfig or None if not registered
        """
        handler = self.get_handler(py_type)
        if handler:
            return handler.get('ui_config')
        return None

    def to_json(self, value: Any, py_type: Optional[Type] = None) -> Any:
        """Transform a Python value to JSON-serializable form.

        Args:
            value: Value to transform
            py_type: Optional type hint (uses type(value) if not provided)

        Returns:
            JSON-serializable value
        """
        if value is None:
            return None

        target_type = py_type or type(value)
        handler = self.get_handler(target_type)

        if handler and handler['to_json']:
            return handler['to_json'](value)

        return value

    def from_json(self, value: Any, py_type: Type) -> Any:
        """Transform a JSON value to Python type.

        Args:
            value: JSON value to transform
            py_type: Target Python type

        Returns:
            Transformed value
        """
        if value is None:
            return None

        handler = self.get_handler(py_type)

        if handler and handler['from_json']:
            return handler['from_json'](value)

        return value

    def mk_input_trans_for_funcs(
        self,
        funcs: list[Callable],
    ) -> Callable:
        """Create input transformation compatible with qh.

        This creates a transformation function that can be passed to
        qh.mk_app as the input_trans parameter.

        Args:
            funcs: List of functions to create transformation for

        Returns:
            Transformation function for qh

        Example:
            >>> from uf import mk_rjsf_app
            >>> registry = InputTransformRegistry()
            >>> # ... register types ...
            >>> input_trans = registry.mk_input_trans_for_funcs([my_func])
            >>> app = mk_rjsf_app([my_func], input_trans=input_trans)
        """
        import inspect

        # Build mapping of func_name -> param_name -> type
        func_type_map = {}
        for func in funcs:
            sig = inspect.signature(func)
            param_types = {}
            for param_name, param in sig.parameters.items():
                if param.annotation != inspect.Parameter.empty:
                    param_types[param_name] = param.annotation
            func_type_map[func.__name__] = param_types

        def input_trans(func_name: str, kwargs: dict) -> dict:
            """Transform input kwargs based on registered types."""
            if func_name not in func_type_map:
                return kwargs

            param_types = func_type_map[func_name]
            transformed = {}

            for param_name, value in kwargs.items():
                if param_name in param_types:
                    py_type = param_types[param_name]
                    transformed[param_name] = self.from_json(value, py_type)
                else:
                    transformed[param_name] = value

            return transformed

        return input_trans

    def mk_output_trans(self) -> Callable:
        """Create output transformation for qh.

        Returns:
            Transformation function for qh output

        Example:
            >>> output_trans = registry.mk_output_trans()
            >>> app = mk_rjsf_app([my_func], output_trans=output_trans)
        """

        def output_trans(result: Any) -> Any:
            """Transform output to JSON-serializable form."""
            if result is None:
                return None

            # Try to transform using registered handlers
            result_type = type(result)
            handler = self.get_handler(result_type)

            if handler and handler['to_json']:
                return handler['to_json'](result)

            # Handle common collection types
            if isinstance(result, list):
                return [output_trans(item) for item in result]
            elif isinstance(result, dict):
                return {k: output_trans(v) for k, v in result.items()}
            elif isinstance(result, tuple):
                return [output_trans(item) for item in result]

            return result

        return output_trans

    def get_all_registered_types(self) -> list[Type]:
        """Get list of all registered types.

        Returns:
            List of registered Python types
        """
        return list(self._type_handlers.keys())


# Global registry instance for convenience
_global_registry = InputTransformRegistry()


def register_type(*args, **kwargs):
    """Register a type in the global registry.

    This is a convenience function that uses the global registry.
    See InputTransformRegistry.register_type for full documentation.
    """
    return _global_registry.register_type(*args, **kwargs)


def get_global_registry() -> InputTransformRegistry:
    """Get the global transformation registry.

    Returns:
        The global InputTransformRegistry instance
    """
    return _global_registry


# Register common custom types
def register_common_types():
    """Register commonly-used Python types.

    This includes:
    - datetime.datetime
    - datetime.date
    - datetime.time
    - pathlib.Path
    - uuid.UUID
    - decimal.Decimal
    """
    from datetime import datetime, date, time
    from pathlib import Path
    from uuid import UUID
    from decimal import Decimal

    # datetime types
    _global_registry.register_type(
        datetime,
        to_json=lambda dt: dt.isoformat(),
        from_json=lambda s: datetime.fromisoformat(s) if isinstance(s, str) else s,
        ui_widget='datetime',
        json_schema_type='string',
        json_schema_format='date-time',
    )

    _global_registry.register_type(
        date,
        to_json=lambda d: d.isoformat(),
        from_json=lambda s: date.fromisoformat(s) if isinstance(s, str) else s,
        ui_widget='date',
        json_schema_type='string',
        json_schema_format='date',
    )

    _global_registry.register_type(
        time,
        to_json=lambda t: t.isoformat(),
        from_json=lambda s: time.fromisoformat(s) if isinstance(s, str) else s,
        ui_widget='time',
        json_schema_type='string',
        json_schema_format='time',
    )

    # Path
    _global_registry.register_type(
        Path,
        to_json=str,
        from_json=Path,
        json_schema_type='string',
    )

    # UUID
    _global_registry.register_type(
        UUID,
        to_json=str,
        from_json=lambda s: UUID(s) if isinstance(s, str) else s,
        json_schema_type='string',
        json_schema_format='uuid',
    )

    # Decimal
    _global_registry.register_type(
        Decimal,
        to_json=float,
        from_json=Decimal,
        json_schema_type='number',
    )


# Auto-register common types on import
try:
    register_common_types()
except ImportError:
    # Some types might not be available, that's okay
    pass
```

## uf/webhooks.py

```python
"""Webhook support for uf.

Provides functionality to trigger HTTP callbacks when functions complete,
enabling integration with external services.
"""

from typing import Callable, Optional, Any
from functools import wraps
from datetime import datetime
import threading
import json


class WebhookEvent:
    """Represents a webhook event.

    Attributes:
        event_type: Type of event ('success', 'failure', 'start')
        func_name: Name of the function
        params: Function parameters
        result: Function result (if success)
        error: Error message (if failure)
        timestamp: When event occurred
    """

    def __init__(
        self,
        event_type: str,
        func_name: str,
        params: dict,
        result: Any = None,
        error: Optional[str] = None,
    ):
        """Initialize webhook event.

        Args:
            event_type: Event type
            func_name: Function name
            params: Function parameters
            result: Function result
            error: Error message
        """
        self.event_type = event_type
        self.func_name = func_name
        self.params = params
        self.result = result
        self.error = error
        self.timestamp = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation
        """
        return {
            'event_type': self.event_type,
            'func_name': self.func_name,
            'params': self.params,
            'result': self.result,
            'error': self.error,
            'timestamp': self.timestamp.isoformat(),
        }


class WebhookClient:
    """Client for sending webhooks.

    Example:
        >>> client = WebhookClient('https://example.com/webhook')
        >>> client.send(WebhookEvent('success', 'my_func', {}, result=42))
    """

    def __init__(
        self,
        url: str,
        headers: Optional[dict] = None,
        timeout: float = 10.0,
        retry_count: int = 3,
    ):
        """Initialize webhook client.

        Args:
            url: Webhook URL
            headers: Optional HTTP headers
            timeout: Request timeout in seconds
            retry_count: Number of retry attempts
        """
        self.url = url
        self.headers = headers or {}
        self.timeout = timeout
        self.retry_count = retry_count

    def send(self, event: WebhookEvent, async_send: bool = True) -> bool:
        """Send a webhook event.

        Args:
            event: WebhookEvent to send
            async_send: Whether to send asynchronously

        Returns:
            True if sent successfully (for sync sends)
        """
        if async_send:
            # Send in background thread
            thread = threading.Thread(
                target=self._send_sync,
                args=(event,),
                daemon=True,
            )
            thread.start()
            return True
        else:
            return self._send_sync(event)

    def _send_sync(self, event: WebhookEvent) -> bool:
        """Send webhook synchronously.

        Args:
            event: WebhookEvent to send

        Returns:
            True if sent successfully
        """
        import requests

        payload = event.to_dict()
        headers = {
            **self.headers,
            'Content-Type': 'application/json',
        }

        for attempt in range(self.retry_count):
            try:
                response = requests.post(
                    self.url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                return True
            except Exception as e:
                if attempt == self.retry_count - 1:
                    # Last attempt failed
                    print(f"Webhook send failed after {self.retry_count} attempts: {e}")
                    return False
                # Retry with exponential backoff
                import time
                time.sleep(2 ** attempt)

        return False


class WebhookManager:
    """Manage webhooks for multiple URLs and events.

    Example:
        >>> manager = WebhookManager()
        >>> manager.add_webhook('https://example.com/hook1', events=['success'])
        >>> manager.add_webhook('https://example.com/hook2', events=['failure'])
        >>> manager.trigger('success', 'my_func', {}, result=42)
    """

    def __init__(self):
        """Initialize webhook manager."""
        self._webhooks: list[dict] = []

    def add_webhook(
        self,
        url: str,
        events: Optional[list[str]] = None,
        headers: Optional[dict] = None,
        condition: Optional[Callable] = None,
    ) -> None:
        """Add a webhook.

        Args:
            url: Webhook URL
            events: List of event types to trigger on (None = all)
            headers: Optional HTTP headers
            condition: Optional callable to filter events
        """
        self._webhooks.append({
            'url': url,
            'events': events,
            'headers': headers or {},
            'condition': condition,
            'client': WebhookClient(url, headers),
        })

    def remove_webhook(self, url: str) -> bool:
        """Remove a webhook by URL.

        Args:
            url: Webhook URL

        Returns:
            True if removed
        """
        original_len = len(self._webhooks)
        self._webhooks = [w for w in self._webhooks if w['url'] != url]
        return len(self._webhooks) < original_len

    def trigger(
        self,
        event_type: str,
        func_name: str,
        params: dict,
        result: Any = None,
        error: Optional[str] = None,
    ) -> int:
        """Trigger webhooks for an event.

        Args:
            event_type: Event type
            func_name: Function name
            params: Function parameters
            result: Function result
            error: Error message

        Returns:
            Number of webhooks triggered
        """
        event = WebhookEvent(event_type, func_name, params, result, error)

        triggered = 0
        for webhook in self._webhooks:
            # Check if this webhook should be triggered
            if webhook['events'] and event_type not in webhook['events']:
                continue

            # Check condition if provided
            if webhook['condition'] and not webhook['condition'](event):
                continue

            # Send webhook
            webhook['client'].send(event)
            triggered += 1

        return triggered

    def list_webhooks(self) -> list[dict]:
        """List all registered webhooks.

        Returns:
            List of webhook configurations
        """
        return [
            {
                'url': w['url'],
                'events': w['events'],
            }
            for w in self._webhooks
        ]


def webhook(
    on: Optional[list[str]] = None,
    url: Optional[str] = None,
    manager: Optional[WebhookManager] = None,
):
    """Decorator to add webhooks to a function.

    Args:
        on: List of events to trigger on ('success', 'failure', 'start')
        url: Optional webhook URL
        manager: Optional WebhookManager instance

    Returns:
        Decorator function

    Example:
        >>> @webhook(on=['success', 'failure'])
        ... def process_order(order_id: int):
        ...     # Process order
        ...     return {'status': 'processed'}
    """
    if on is None:
        on = ['success', 'failure']

    if manager is None:
        manager = get_global_webhook_manager()
        if manager is None:
            manager = WebhookManager()
            set_global_webhook_manager(manager)

    # If URL provided, add to manager
    if url:
        manager.add_webhook(url, events=on)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get params from kwargs
            params = kwargs.copy()

            # Trigger start event if configured
            if 'start' in on:
                manager.trigger('start', func.__name__, params)

            try:
                result = func(*args, **kwargs)

                # Trigger success event
                if 'success' in on:
                    manager.trigger('success', func.__name__, params, result=result)

                return result

            except Exception as e:
                # Trigger failure event
                if 'failure' in on:
                    manager.trigger('failure', func.__name__, params, error=str(e))

                raise

        wrapper.__uf_webhook_enabled__ = True
        wrapper.__uf_webhook_events__ = on
        wrapper.__uf_webhook_manager__ = manager

        return wrapper

    return decorator


# Global webhook manager
_global_webhook_manager: Optional[WebhookManager] = None


def set_global_webhook_manager(manager: WebhookManager) -> None:
    """Set the global webhook manager."""
    global _global_webhook_manager
    _global_webhook_manager = manager


def get_global_webhook_manager() -> Optional[WebhookManager]:
    """Get the global webhook manager."""
    return _global_webhook_manager
```