# SuperBotV2 - Crypto Trading API

API de trading automatizado con análisis de mercado usando LangGraph y FastAPI.

## 🚀 Inicio Rápido

### 1. Configurar Variables de Entorno

```bash
cp .env.example .env
# Edita .env con tus credenciales
```

### 2. Instalar Dependencias

```bash
uv sync
```

### 3. Iniciar el Servidor

```bash
# Opción 1: Con uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Opción 2: Ejecutar directamente
python main.py
```

El servidor estará disponible en:
- **API**: http://localhost:8000
- **Docs Interactiva**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 Endpoints

### POST /api/trading/analyze

Ejecuta el análisis completo de trading.

**Request:**
```json
{
  "symbols": ["BTCUSD"],
  "news_limit": 10
}
```

**Response:**
```json
{
  "success": true,
  "symbols": ["BTCUSD"],
  "news_analysis": {
    "sentiment": "positive",
    "context_summary": "...",
    "market_opinion": "..."
  },
  "technical_analysis": {
    "momentum": "bullish",
    "crossover_status": "golden_cross",
    ...
  },
  "fear_greed": {
    "index": 75,
    "classification": "Greed"
  },
  "support_resistance": {
    "nearest_support": 95000.0,
    "distance_to_support": "-1.5%",
    ...
  },
  "strategist_proposal": {
    "direction": "buy",
    "entry_price": 96500.0,
    "stop_loss": 95000.0,
    "take_profit": 98000.0,
    ...
  }
}
```

### Ejemplos de Uso

#### cURL
```bash
curl -X POST "http://localhost:8000/api/trading/analyze" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["BTCUSD"], "news_limit": 10}'
```

#### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/api/trading/analyze",
    json={"symbols": ["BTCUSD"], "news_limit": 10}
)
result = response.json()
print(f"Dirección: {result['strategist_proposal']['direction']}")
```

#### JavaScript
```javascript
fetch('http://localhost:8000/api/trading/analyze', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({symbols: ['BTCUSD'], news_limit: 10})
})
.then(res => res.json())
.then(data => console.log(data));
```

## 🏗️ Arquitectura

### Flujo del Análisis

1. **Análisis Paralelo** (4 nodos simultáneos):
   - Análisis de noticias (sentimiento)
   - Análisis técnico (SMAs 25/200)
   - Fear & Greed Index
   - Soporte y Resistencia

2. **Trading Committee**:
   - Agente 1: El Estratega (propone trade)
   - Agente 2: Abogado del Diablo (próximamente)
   - Agente 3: Juez de Riesgo (próximamente)

### Stack Tecnológico

- **FastAPI** - Framework web async
- **LangGraph** - Orquestación de agentes
- **LangChain + OpenAI** - LLM para análisis
- **SQLAlchemy + MySQL** - Persistencia de datos
- **Pydantic** - Validación de datos

## 📁 Estructura del Proyecto

```
SuperBotV2/
├── app/
│   ├── agent/           # Nodos de LangGraph
│   ├── controller/      # Endpoints FastAPI
│   ├── database/        # Repositorios y modelos
│   ├── graph/           # Configuración del grafo
│   ├── models/          # Modelos Pydantic
│   └── utils/           # Utilidades (LLM, executors)
├── main.py              # Entry point FastAPI
├── pyproject.toml       # Dependencias
└── .env                 # Variables de entorno
```

## 🔧 Configuración

### Variables de Entorno Requeridas

```bash
# Alpaca API
ALPACA_API_KEY=your_key
ALPACA_API_SECRET=your_secret

# Polygon API
INDICATORS_API_KEY=your_key

# OpenAI
OPENAI_API_KEY=your_key

# MySQL
MYSQL_HOST=your_host
MYSQL_USER=admin
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=superbot
```

## ⚡ Performance

- **Tiempo de respuesta**: ~10-15 segundos
- **Ejecución paralela**: 2.5x más rápido
- **Connection pooling**: HTTP y DB optimizados
- **Singleton pattern**: LLM y grafo reutilizados

## 📚 Documentación Adicional

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Ejemplos**: Ver `API_USAGE.py`

## 🚧 Próximas Características

- [ ] Agente 2: Abogado del Diablo
- [ ] Agente 3: Juez de Riesgo
- [ ] Ejecución automática de trades
- [ ] WebSocket para streaming de análisis
- [ ] Dashboard web

## 📝 Notas

- Los análisis pueden tardar 10-15 segundos
- Usar timeout >= 60s en clientes HTTP
- La API maneja errores gracefully
- Logs disponibles en consola del servidor

