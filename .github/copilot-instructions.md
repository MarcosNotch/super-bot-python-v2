# GitHub Copilot Instructions - MoneyRails Agent

## General Guidelines

**IMPORTANT**: NO crear archivos de tests ni README.md después de cada implementación a menos que se solicite explícitamente.

## Project Type

FastAPI Python project with LangGraph agents for cripto trading

## Python & FastAPI Best Practices

### 1. Project Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── agents/         # LangGraph agents
│   ├── config/         # Configuration
│   ├── controller/     # API endpoints (routes + schemas)
│   ├── services/       # Business logic
│   └── models/         # Database models (if needed)
├── main.py             # FastAPI app entry point
├── pyproject.toml      # Dependencies
└── .env                # Environment variables
```

### 2. Controller/Router Organization

**ALWAYS** separate concerns in controllers:
- `schemas.py` - Pydantic models (request/response)
- `routes.py` - Endpoint definitions and logic
- `__init__.py` - Export router only

```python
# ✅ GOOD - controller/__init__.py
from .routes import router
__all__ = ["router"]

# ❌ BAD - Don't put everything in __init__.py
```

### 3. Pydantic Models (Schemas)

```python
# ✅ GOOD - Use Field with descriptions
from pydantic import BaseModel, Field
from typing import Optional

class UserRequest(BaseModel):
    name: str = Field(..., min_length=1, description="User name")
    age: Optional[int] = Field(None, ge=0, le=150)
    
    model_config = {
        "json_schema_extra": {
            "examples": [{"name": "John", "age": 30}]
        }
    }

# ❌ BAD - No validation or descriptions
class UserRequest(BaseModel):
    name: str
    age: int
```

### 4. Route Handlers

```python
# ✅ GOOD - Async, typed, documented
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(request: UserRequest) -> UserResponse:
    """
    Create a new user.
    
    Args:
        request: User creation data
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If user already exists
    """
    # Implementation
    pass

# ❌ BAD - No types, no docs, blocking
@router.post("/create")
def create_user(request):
    pass
```

### 5. Error Handling

```python
# ✅ GOOD - Use HTTPException with proper status codes
from fastapi import HTTPException, status

if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )

# ❌ BAD - Return errors as success responses
return {"error": "User not found"}
```

### 6. Dependency Injection

```python
# ✅ GOOD - Use dependencies for common logic
from fastapi import Depends, Header, HTTPException

async def verify_token(authorization: str = Header(...)) -> str:
    if not is_valid_token(authorization):
        raise HTTPException(status_code=401, detail="Invalid token")
    return authorization

@router.get("/protected")
async def protected_route(token: str = Depends(verify_token)):
    pass

# ❌ BAD - Repeat validation in every endpoint
@router.get("/protected")
async def protected_route(authorization: str = Header(...)):
    if not is_valid_token(authorization):
        raise HTTPException(status_code=401)
```

### 7. Configuration Management

```python
# ✅ GOOD - Use Pydantic Settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MoneyRails"
    openai_api_key: str
    database_url: str
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }

settings = Settings()

# ❌ BAD - Direct os.getenv everywhere
import os
api_key = os.getenv("OPENAI_API_KEY")
```

### 8. Async/Await Best Practices

```python
# ✅ GOOD - Use async for I/O operations
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await db.fetch_user(user_id)
    return user

# ❌ BAD - Blocking synchronous calls
@router.get("/users/{user_id}")
def get_user(user_id: int):
    user = db.fetch_user_sync(user_id)  # Blocks event loop
    return user
```

### 9. Response Models

```python
# ✅ GOOD - Explicit response models
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    
    model_config = {"from_attributes": True}

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int) -> UserResponse:
    return await db.get_user(user_id)

# ❌ BAD - Return dicts without validation
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"id": 1, "name": "John"}
```

### 9.1. LangGraph Nodes - State Consistency

```python
# ✅ GOOD - Always return the same state type that is received
def my_node(state: MyAgentState) -> MyAgentState:
    """
    Process the state and return the updated state.
    
    Args:
        state: Current agent state
        
    Returns:
        MyAgentState: Updated state (same type as input)
    """
    # Modify the state
    state["field"] = "new_value"
    
    # Always return the state object, not a dict subset
    return state

# ❌ BAD - Return dict instead of state type
def my_node(state: MyAgentState) -> Dict[str, Any]:
    return {"field": "value"}  # Wrong! Return state, not dict

# ❌ BAD - Return subset of state
def my_node(state: MyAgentState) -> MyAgentState:
    return {"field": "value"}  # Wrong! Return full state

# ✅ GOOD - Update state and return it
def my_node(state: MyAgentState) -> MyAgentState:
    state["errorMessages"] = "Error message"
    return state
```

**Important Rules for LangGraph Nodes:**
1. **Always return the same type** that you receive (`MyAgentState -> MyAgentState`)
2. **Modify the state object** directly, don't create a new dict
3. **Return the full state**, not a subset
4. **Use TypedDict** for state definitions
5. **Update fields** by assignment: `state["field"] = value`

### 10. File Naming Conventions

```
✅ GOOD:
- user_routes.py
- chat_schemas.py
- transfer_service.py

❌ BAD:
- UserRoutes.py
- ChatSchemas.py
- TransferService.py
```

### 11. Import Organization

```python
# ✅ GOOD - Organized imports
# Standard library
import os
from typing import Optional, List

# Third-party
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Local
from app.services.user_service import UserService
from app.config.settings import settings

# ❌ BAD - Random order
from app.services.user_service import UserService
import os
from pydantic import BaseModel
from fastapi import APIRouter
```

### 12. Type Hints

```python
# ✅ GOOD - Always use type hints
from typing import List, Optional, Dict, Any

async def get_users(limit: int = 10) -> List[UserResponse]:
    users: List[User] = await db.fetch_users(limit)
    return [UserResponse.model_validate(u) for u in users]

# ❌ BAD - No type hints
async def get_users(limit=10):
    users = await db.fetch_users(limit)
    return users
```

### 13. Environment Variables

```python
# ✅ GOOD - Centralized config
# config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    debug: bool = False
    
    model_config = {"env_file": ".env"}

# ❌ BAD - Scattered os.getenv
api_key = os.getenv("OPENAI_API_KEY")
```

### 14. CORS Configuration

```python
# ✅ GOOD - Proper CORS setup
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ❌ BAD - Allow all origins in production
allow_origins=["*"]
```

### 15. Logging

```python
# ✅ GOOD - Use logging module
import logging

logger = logging.getLogger(__name__)

@router.post("/transfer")
async def transfer(request: TransferRequest):
    logger.info(f"Processing transfer: {request.amount}")
    try:
        result = await process_transfer(request)
        logger.info(f"Transfer completed: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Transfer failed: {str(e)}", exc_info=True)
        raise

# ❌ BAD - Use print statements
print("Processing transfer...")
```

## LangGraph Best Practices

### 1. Agent Structure

```python
# ✅ GOOD - Clear state and nodes
from typing import TypedDict
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    message: str
    amount: Optional[float]
    recipient: Optional[str]

def process_message(state: AgentState) -> AgentState:
    # Process logic
    return state

# Build graph
graph = StateGraph(AgentState)
graph.add_node("process", process_message)
```

### 2. Node Functions

```python
# ✅ GOOD - Pure functions with clear inputs/outputs
def extract_amount(state: AgentState) -> AgentState:
    """Extract transfer amount from message."""
    # Implementation
    return {**state, "amount": extracted_amount}

# ❌ BAD - Side effects and unclear state
def extract_amount(state):
    global amount
    amount = extract(state["message"])
    return state
```

## Code Style

- Use `snake_case` for functions and variables
- Use `PascalCase` for classes
- Use `UPPER_CASE` for constants
- Maximum line length: 100 characters
- Use f-strings for string formatting
- Use list/dict comprehensions when readable

## Documentation Rules

- **DO NOT** create test files unless explicitly requested
- **DO NOT** create README.md files unless explicitly requested
- **DO** add docstrings to functions and classes
- **DO** add inline comments for complex logic

## Code Review Checklist

Before completing a task, ensure:
- ✅ Proper file organization (schemas, routes, services separated)
- ✅ Type hints on all functions
- ✅ Pydantic models use Field with descriptions
- ✅ Async/await used for I/O operations
- ✅ HTTPException used for errors
- ✅ No tests or READMEs created (unless requested)
- ✅ Clean imports (organized by category)
- ✅ Proper error handling
- ✅ Docstrings on public functions

## What NOT to Do

❌ Don't put everything in `__init__.py`
❌ Don't create test files automatically
❌ Don't create README files automatically
❌ Don't use print() for logging
❌ Don't return errors as 200 responses
❌ Don't use blocking I/O in async functions
❌ Don't hardcode configuration values
❌ Don't ignore type hints
❌ Don't use `import *`
❌ Don't mix business logic in route handlers

## Performance & Scalability Best Practices

### 1. HTTP Clients y Connection Pooling (httpx)

- **DO** usar un `httpx.AsyncClient` compartido (singleton) con **connection pooling** para llamadas HTTP frecuentes.
- **DO** configurar `limits`, `timeout` y `http2=True` en los clientes HTTP que se usen en producción.
- **DON'T** crear un nuevo `httpx.AsyncClient` en cada request ni usar `httpx.get(...)` directo en endpoints críticos.

```python
# ✅ GOOD - Cliente HTTP singleton con pooling
import httpx

limits = httpx.Limits(
    max_keepalive_connections=20,
    max_connections=50,
    keepalive_expiry=30.0,
)

client = httpx.AsyncClient(
    timeout=10.0,
    limits=limits,
    http2=True,
    follow_redirects=True,
)

async def get_transfers(...) -> TransfersResponse:
    response = await client.get("https://api.example.com/transfers")
    response.raise_for_status()
    ...

# ❌ BAD - Crear cliente por request (sin pooling)
import httpx

async def get_transfers(...):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/transfers")
        ...
```

**Reglas para Copilot:**
- Cuando sugieras un nuevo cliente HTTP, **prefiere** definirlo en `app/clients/` o `app/services/` y exponer una instancia global reutilizable.
- No sugieras `httpx.AsyncClient()` dentro de endpoints, middlewares o funciones que se llamen por request.

### 2. Singletons para Recursos Costosos (LLM, Graphs, HTTP Clients)

- **DO** crear una única instancia (singleton) para:
  - Clientes HTTP (por ejemplo, `TransfersHandlerClient`).
  - Clientes de LLM / OpenAI.
  - Grafos de LangGraph y servicios principales (por ejemplo, `ChatService`).
- **DON'T** reinstanciar estos recursos en cada llamada de API.

```python
# ✅ GOOD - Servicio y cliente singleton
# app/services/chat_service.py
chat_service = ChatService()  # Singleton

# app/clients/transfers_client.py
transfers_client = TransfersHandlerClient()  # Singleton

# app/utils/openai_client.py
from functools import lru_cache
from langchain_openai import ChatOpenAI

@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(...)
```

```python
# ❌ BAD - Crear servicios/grafos/LLM en cada request
from app.services.chat_service import ChatService
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI

@router.post("/chat")
async def chat(request: ChatRequest):
    service = ChatService()          # Se crea en cada request
    graph = StateGraph(...)          # Grafo recompilado en cada request
    llm = ChatOpenAI(...)            # LLM nuevo en cada request
    ...
```

**Reglas para Copilot:**
- Evita patrones `service = ServiceClass()` dentro de handlers FastAPI; sugiere reutilizar instancias definidas a nivel de módulo.
- No sugieras crear o compilar grafos de LangGraph dentro de endpoints; asume que los grafos se construyen una vez y se reutilizan.

### 3. OpenAI / LLM Client – Timeouts y Retries

- **DO** configurar timeouts explícitos (`request_timeout`), `max_retries` y parámetros de modelo para acelerar y estabilizar respuestas.
- **DO** centralizar la construcción del cliente de LLM en `app/utils/openai_client.py` o similar.
- **DON'T** crear instancias de `ChatOpenAI` ad‑hoc con valores por defecto y sin timeouts.

```python
# ✅ GOOD - Cliente OpenAI con timeouts y retries controlados
from functools import lru_cache
from langchain_openai import ChatOpenAI
from app.config.config import settings

@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
        request_timeout=15.0,  # Fail fast
        max_retries=1,         # Un solo retry
        model_kwargs={
            "top_p": 0.95,
        },
    )
```

```python
# ❌ BAD - Cliente OpenAI sin timeouts ni reutilización
from langchain_openai import ChatOpenAI

async def handle_request(...):
    llm = ChatOpenAI(api_key="...", model="gpt-4o")  # Sin timeout, sin cache
    ...
```

**Reglas para Copilot:**
- Siempre que propongas usar el LLM, utiliza una función tipo `get_llm()` ya existente en lugar de crear un cliente nuevo.
- Sugiere explícitamente `request_timeout` y `max_retries` cuando se definan nuevos clientes.

### 4. Logging y Middlewares – Minimizar Overhead

- **DO** usar logging estratégico:
  - Menos logs por request.
  - Evitar logs para health checks.
  - INFO/WARNING/ERROR solo para eventos importantes.
- **DON'T** loguear cada detalle de cada request, especialmente en middleware.

```python
# ✅ GOOD - Middleware de logging optimizado
from fastapi import Request
from app.utils.logger import logger

@app.middleware("http")
async def log_requests(request: Request, call_next):
    if request.url.path == "/health":
        return await call_next(request)

    response = await call_next(request)

    if response.status_code >= 400 or request.url.path.startswith("/api"):
        logger.info(f"{request.method} {request.url.path} - {response.status_code}")

    return response
```

```python
# ❌ BAD - Logging excesivo en cada request
@app.middleware("http")
async def log_everything(request: Request, call_next):
    logger.info(f"Request headers: {request.headers}")
    logger.info(f"Request body: {await request.body()}")
    logger.info(f"Client: {request.client}")
    ...
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
```

**Reglas para Copilot:**
- Evita proponer logs detallados en bucles o middlewares que se llamen en cada request.
- Desaconseja logging de cuerpos completos de request/response salvo en debugging puntual controlado por flags.

### 5. Compresión de Responses (GZipMiddleware)

- **DO** usar `GZipMiddleware` con un `minimum_size` razonable (por ejemplo, `1000` bytes) para ahorrar ancho de banda.
- **DON'T** deshabilitar la compresión por defecto ni añadir compresión duplicada manualmente.

```python
# ✅ GOOD - GZip habilitado solo para payloads grandes
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

```python
# ❌ BAD - Sin compresión o compresión manual en cada endpoint
@app.get("/large-response")
async def large_response():
    data = generate_large_payload()
    compressed = gzip.compress(json.dumps(data).encode("utf-8"))  # Compresión manual
    return Response(content=compressed)
```

**Reglas para Copilot:**
- Cuando se sugieran middlewares globales, prioriza incluir `GZipMiddleware` configurado una sola vez en `main.py`.
- No propongas compresión manual en endpoints salvo casos muy específicos.

### 6. Anti‑Patrones de Performance a Evitar

- **HTTP Clients**
  - ❌ No crear `httpx.AsyncClient` por request.
  - ❌ No usar llamados `httpx.get/post/...` directos en endpoints sin pooling.
- **LangGraph**
  - ❌ No recompilar grafos (`StateGraph(...)`, `graph.compile()`) dentro de los handlers.
  - ✅ Compilar grafos una sola vez al iniciar el módulo/servicio.
- **LLM / OpenAI**
  - ❌ No crear nuevos clientes de LLM por request.
  - ✅ Reutilizar `get_llm()` cacheado.
- **Logging**
  - ❌ No loguear todo request/response por defecto.
  - ✅ Limitar el logging a lo relevante para observabilidad.
- **Generales**
  - ❌ No hacer trabajo pesado de inicialización en cada request (carga de modelos, configuración costosa).
  - ✅ Mover inicialización pesada a nivel de módulo o startup del servicio.

### 7. Do / Don't de Performance (Resumen)

**Do:**
1. Reutilizar clientes HTTP y LLM (singleton + pooling + cache).
2. Configurar timeouts y retries explícitos para servicios externos.
3. Compilar grafos de LangGraph una sola vez y reutilizarlos.
4. Usar GZip y parámetros de Uvicorn pensados para producción cuando se muestren ejemplos.
5. Mantener el logging ligero en el camino caliente de requests.

**Don't:**
1. Crear recursos caros (clientes HTTP, LLM, grafos) dentro de endpoints.
2. Apoyarse en defaults de librerías para producción (Uvicorn, OpenAI, httpx).
3. Añadir logging detallado en middlewares o loops críticos.
4. Duplicar lógica de compresión o configuración de clientes.
