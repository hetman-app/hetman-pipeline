# Framework Integrations

Hetman Pipeline provides seamless integration with popular web frameworks, making it easy to validate request data in your API endpoints.

---

## Falcon Integration

Hetman Pipeline includes built-in support for the [Falcon](https://falcon.readthedocs.io/) web framework, supporting both WSGI and ASGI applications.

### Installation

```bash
pip install hetman-pipeline[falcon]
```

---

## The `process_request` Decorator

The `process_request` decorator validates incoming request data and injects validated values directly into your responder methods.

### Basic Usage

```python
from falcon import App
from pipeline.integration.falcon import process_request
from pipeline import Pipe

class UserResource:
    @process_request(
        email={
            "type": str,
            "conditions": {Pipe.Condition.MaxLength: 64},
            "matches": {Pipe.Match.Format.Email: None}
        },
        age={
            "type": int,
            "conditions": {
                Pipe.Condition.MinNumber: 18,
                Pipe.Condition.MaxNumber: 120
            }
        }
    )
    def on_post(self, req, resp, email, age):
        # email and age are already validated and injected
        resp.media = {
            "message": "User created successfully",
            "email": email,
            "age": age
        }

# Create Falcon app
app = App()
app.add_route('/users', UserResource())
```

---

## How It Works

1. **Request Data Extraction**: The decorator automatically extracts data from:

    - Query parameters (for GET requests): This is slightly more complex because all query values are passed as strings. We attempt to JSON-deserialize every value so that each query parameter is parsed as JSON.
    - Request body (for POST, PUT, PATCH, etc.): We use the .get_media() method to retrieve the payload.

2. **Validation**: Data is validated using the pipeline configuration

3. **Error Handling**: If validation fails:

    - Response status is set to `422 Unprocessable Content`
    - Response body contains validation errors
    - Responder method is **not** executed

4. **Injection**: If validation succeeds:
    - Validated data is injected as keyword arguments
    - Responder method executes normally

---

## Complete Example: User Registration API

```python
from falcon import App, Request, Response

from pipeline import Pipe
from pipeline.integration.falcon import process_request


class RegistrationResource:
    @process_request(
        username={
            "type": str,
            "conditions":
                {
                    Pipe.Condition.MinLength: 3,
                    Pipe.Condition.MaxLength: 20
                },
            "matches": {
                Pipe.Match.Text.Alphanumeric: None
            },
            "transform": {
                Pipe.Transform.Lowercase: None
            }
        },
        email={
            "type": str,
            "conditions": {
                Pipe.Condition.MaxLength: 64
            },
            "matches": {
                Pipe.Match.Format.Email: None
            },
            "transform": {
                Pipe.Transform.Lowercase: None
            }
        },
        password={
            "type": str,
            "matches":
                {
                    Pipe.Match.Format.Password:
                        Pipe.Match.Format.Password.STRICT
                }
        },
        age={
            "type": int,
            "conditions":
                {
                    Pipe.Condition.MinNumber: 18,
                    Pipe.Condition.MaxNumber: 120
                },
            "optional": True
        }
    )
    def on_post(
        self,
        req: Request,
        resp: Response,
        username: str,
        email: str,
        password: str,
        age: int | None = None
    ):
        # All parameters are validated and transformed
        # username and email are lowercased
        # password meets strict requirements
        # age is optional and validated if present

        # Your business logic here
        user_id = create_user_in_database(username, email, password, age)

        resp.media = {
            "success": True,
            "user_id": user_id,
            "username": username,
            "email": email,
            "age": age
        }

        resp.status = 201

# Create app
app = App()
app.add_route('/register', RegistrationResource())
```

### Valid Request

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "JohnDoe",
    "email": "John@Example.com",
    "password": "SecurePass123!",
    "age": 25
  }'
```

**Response (201 Created):**

```json
{
	"success": true,
	"user_id": 12345,
	"username": "johndoe",
	"email": "john@example.com",
	"age": 25
}
```

### Invalid Request

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ab",
    "email": "invalid-email",
    "password": "weak"
  }'
```

**Response (422 Unprocessable Content):**

```json
{
	"username": [
		{
			"id": "min_length",
			"msg": "Too short. Minimum length is 3 characters.",
			"value": "ab"
		}
	],
	"email": [
		{
			"id": "email",
			"msg": "Invalid email address format (e.g., 'user@example.com').",
			"value": "invalid-email"
		}
	],
	"password": [
		{
			"id": "password",
			"msg": "Password too weak. Required: 6-64 characters, at least 1 uppercase, 1 lowercase, 1 digit, and 1 special character.",
			"value": "weak"
		}
	]
}
```

---

## GET Request Validation

The decorator also works with GET requests, validating query parameters:

```python
from falcon import App
from pipeline.integration.falcon import process_request
from pipeline import Pipe

class SearchResource:
    @process_request(
        query={
            "type": str,
            "conditions": {
                Pipe.Condition.MinLength: 3,
                Pipe.Condition.MaxLength: 100
            }
        },
        page={
            "type": int,
            "conditions": {
                Pipe.Condition.MinNumber: 1,
                Pipe.Condition.MaxNumber: 1000
            },
            "optional": True
        },
        limit={
            "type": int,
            "conditions": {
                Pipe.Condition.MinNumber: 1,
                Pipe.Condition.MaxNumber: 100
            },
            "optional": True
        }
    )
    def on_get(self, req, resp, query, page=1, limit=10):
        # Perform search with validated parameters
        results = search_database(query, page, limit)

        resp.media = {
            "query": query,
            "page": page,
            "limit": limit,
            "results": results
        }

app = App()
app.add_route('/search', SearchResource())
```

**Request:**

```bash
curl "http://localhost:5000/search?query=python&page=2&limit=20"
```

---

## ASGI Support

The decorator automatically detects and supports ASGI applications:

```python
from falcon.asgi import App, Request, Response
from pipeline.integration.falcon import process_request
from pipeline import Pipe

class AsyncUserResource:
    @process_request(
        email={
            "type": str,
            "matches": {Pipe.Match.Format.Email: None}
        }
    )
    async def on_post(self, req: Request, resp: Response, email: str):
        # Async responder with validated email
        user = await create_user_async(email)

        resp.media = {"user_id": user.id, "email": email}

# Create ASGI app
app = App()
app.add_route('/users', AsyncUserResource())
```

---

## Custom Error Handling

By default, validation errors are returned as a dictionary with field names as keys. You can customize this behavior globally using `PipelineFalcon.global_error_handler`.

!!! tip "Recommended Approach"

    For APIs, it's recommended to use a **global error handler** to ensure a consistent error response format across all endpoints.

### Using Global Error Handler

The global error handler should **raise an exception** with your custom error format:

```python
from falcon import HTTPBadRequest
from pipeline.integration.falcon import PipelineFalcon, process_request
from pipeline import Pipe

def custom_error_handler(errors: dict):
    """
    Custom global error handler for all validation errors.

    This function is called when validation fails and should raise
    an HTTPBadRequest exception with a custom error format.

    Args:
        errors: Dictionary of validation errors (field -> error list)

    Raises:
        HTTPBadRequest: With custom error format
    """
    # Transform errors to a custom format
    formatted_errors = []

    for field, error_list in errors.items():
        for error in error_list:
            formatted_errors.append({
                "field": field,
                "code": error.get('id'),
                "message": error.get('msg'),
                "invalid_value": error.get('value')
            })

    # Raise HTTPBadRequest with custom format, you can use any exception you want that is supported by Falcon
    raise HTTPBadRequest(
        title="Validation Failed",
        description={
            "success": False,
            "error_count": len(formatted_errors),
            "errors": formatted_errors
        }
    )

# Set the global error handler (affects all endpoints)
PipelineFalcon.global_error_handler = custom_error_handler

# Now all endpoints will use this error format
class UserResource:
    @process_request(
        email={
            "type": str,
            "matches": {Pipe.Match.Format.Email: None}
        }
    )
    def on_post(self, req, resp, email):
        resp.media = {"email": email}
```

### Alternative: Per-Instance Error Handler

If you need different error handling for specific pipelines, you can pass `handle_errors` to the decorator:

```python
from falcon import HTTPBadRequest
from pipeline.integration.falcon import process_request
from pipeline import Pipe

def strict_error_handler(errors: dict):
    """Strict error handler that includes detailed information"""
    raise HTTPBadRequest(
        title="Strict Validation Error",
        description={
            "message": "Your request contains validation errors",
            "fields_with_errors": list(errors.keys()),
            "details": errors
        }
    )

class StrictResource:
    @process_request(
        email={"type": str, "matches": {Pipe.Match.Format.Email: None}},
        handle_errors=strict_error_handler  # Override global handler
    )
    def on_post(self, req, resp, email):
        resp.media = {"email": email}
```

!!! warning "Error Handler Must Raise Exception"

    The error handler **must raise an exception**. It should **not** return a value. If it doesn't raise an exception, the validation will be considered successful and the responder will execute with potentially invalid data.

---

## Best Practices

!!! tip "Use Optional Fields"

    Mark fields as optional when they're not required:

    ```text
    @process_request(
        required_field={"type": str},
        optional_field={"type": str, "optional": True}
    )
    ```

!!! warning "Error Response Format"

    The default error response is a dictionary with field names as keys and error lists as values. Make sure your API clients can handle this format.

!!! note "Parameter Injection"

    Validated parameters are injected as keyword arguments. Make sure your responder method signature matches the pipeline configuration.

---

## Integration with Other Frameworks

While Hetman Pipeline currently has built-in support for Falcon, you can easily integrate it with other frameworks:

### Flask Example

```python
from flask import Flask, request, jsonify
from pipeline import Pipeline, Pipe

app = Flask("test_app")

@app.route('/users', methods=['POST'])
def create_user():
    # Define pipeline
    user_pipeline = Pipeline(
        email={
            "type": str,
            "matches": {Pipe.Match.Format.Email: None}
        },
        age={
            "type": int,
            "conditions": {Pipe.Condition.MinNumber: 18}
        }
    )

    # Validate request data
    result = user_pipeline.run(data=request.json)

    if result.errors:
        return jsonify(result.errors), 422

    # Use validated data
    return jsonify({
        "email": result.processed_data['email'],
        "age": result.processed_data['age']
    }), 201
```

More integrations will be added in the future but you can easily add your own integration by following the same pattern.

---

## Next Steps

-   Learn about [Pipeline Hooks](hooks.md) for custom processing
-   Explore [Handler Modifiers](modifiers.md) for advanced validation
-   Check [Error Customization](customization.md) for custom error messages
