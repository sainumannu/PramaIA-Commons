# Come Implementare Nuovi Nodi in PramaIA

**Guida completa per l'implementazione corretta di nuovi processori di nodi**

## 🏗️ **NUOVA ARCHITETTURA PDK** - Aggiornamento Novembre 2025

**⚠️ IMPORTANTE:** L'architettura è stata completamente ridisegnata!

### 🎯 Separazione Core vs Business

**SERVER (Solo Processori CORE):**
- ✅ I/O Essenziali: `UserInputProcessor`, `FileInputProcessor`, `TextOutputProcessor`
- ✅ LLM Core: `OpenAIProcessor`, `AnthropicProcessor`, `OllamaProcessor`
- ✅ API Core: `HTTPRequestProcessor`, `WebhookProcessor`
- ✅ Data Core: `DataTransformProcessor`, `TextProcessor`, `JSONProcessor`
- ✅ RAG Core: `RAGQueryProcessor`, `RAGGenerationProcessor`

**PDK (Tutti i Processori BUSINESS):**
- 📨 Event Processing: `EventInputProcessor` → PDK Plugin
- 📄 File Processing: `FileParsingProcessor` → PDK Plugin
- 📊 Metadata: `MetadataManagerProcessor` → PDK Plugin
- 📝 Documents: `DocumentProcessorProcessor` → PDK Plugin
- 🔍 Vector Store: `VectorStoreOperationsProcessor` → PDK Plugin
- 📋 Logging: `EventLoggerProcessor` → PDK Plugin

### ⚡ Principi Architetturali

1. **❌ ZERO FALLBACK** - Se PDK down → errore chiaro, non fallback silenziosi
2. **🔌 PDK per Business** - Tutta la business logic è nel PDK
3. **⚡ Server Resiliente** - Funziona per operazioni core anche senza PDK
4. **🚨 Errori Trasparenti** - KeyError esplicito se processore business richiesto dal server

## 🎯 Panoramica

I nodi in PramaIA ora seguono un'architettura **Core + PDK** dove:
- Il **server** contiene solo processori **CORE essenziali**
- Il **PDK** contiene tutti i processori **BUSINESS**
- Il **database** contiene solo i **metadati** dei workflow (struttura, configurazione)
- I workflow vengono eseguiti attraverso il registry appropriato

## 🔄 Come Implementare Nuovi Nodi

### Opzione A: Processore Core (Raro)

**Usa questa opzione SOLO per:**
- Interfacce I/O essenziali
- Funzionalità LLM base
- Operazioni API critiche

**Implementazione:**

## ❌ Errore Comune: Modificare il Database

**SBAGLIATO:** Tentare di aggiornare il campo `node_type` nel database per cambiare l'implementazione.

```sql
-- ❌ NON FARE QUESTO
UPDATE workflow_nodes SET node_type = 'NewProcessor' WHERE node_type = 'OldProcessor';
```

**Perché non funziona:**
- Il database contiene solo riferimenti ai nomi dei processori
- L'implementazione effettiva è nel registry del codice
- Modificare il DB senza aggiornare il registry causa errori "processor not found"

## ✅ Approccio Corretto: Registry Pattern

**Implementazione:**

1. Creare processore in `backend/engine/processors/core_processors.py`:

```python
from backend.engine.node_registry import BaseNodeProcessor
from backend.engine.execution_context import ExecutionContext
from typing import Dict, Any

class MyCoreProcessor(BaseNodeProcessor):
    """Processore core essenziale per funzionalità di base."""
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        """Logica di elaborazione core."""
        input_data = context.get_input_for_node(node.node_id)
        
        # Elaborazione core (I/O, LLM, API base)...
        result = {
            "processed_data": "...",
            "status": "success"
        }
        
        return result
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida configurazione."""
        return True
```

2. Registrare in `backend/engine/processors/__init__.py`:

```python
from .core_processors import MyCoreProcessor

CORE_PROCESSORS = {
    # ... altri processori core ...
    'MyCoreProcessor': MyCoreProcessor,
}
```

### Opzione B: Processore Business (Raccomandato)

**Usa questa opzione per:**
- Elaborazione documenti
- Operazioni vector store
- Parsing file avanzato  
- Business logic specifica
- Integrazioni esterne

**Implementazione PDK:**

1. Creare plugin in `PramaIA-PDK/plugins/my-business-plugin/`:

```json
// plugin.json
{
  "name": "my-business-plugin",
  "version": "1.0.0", 
  "description": "Processore business personalizzato",
  "nodes": [
    {
      "id": "my_business_processor",
      "name": "My Business Processor",
      "description": "Elaborazione business specifica",
      "category": "Business",
      "icon": "🔧",
      "config_schema": {
        "type": "object",
        "properties": {
          "param1": {"type": "string", "default": "value1"}
        }
      }
    }
  ]
}
```

2. Implementare in `nodes/my_business_processor.js`:

```javascript
class MyBusinessProcessor {
    constructor() {
        this.name = 'My Business Processor';
    }

    async execute(input, config, context) {
        const logger = context.logger || console;
        
        logger.info('🔧 Processing business logic...');
        
        // La tua business logic qui
        const result = {
            ...input,
            business_data: "elaborated",
            processed_at: new Date().toISOString()
        };
        
        return result;
    }

    validate(config) {
        return { valid: true };
    }
}

module.exports = MyBusinessProcessor;
```

3. Usare nel server via PDKNodeProcessor:

```python
# Nel workflow
pdk_processor = PDKNodeProcessor(
    plugin_id='my-business-plugin',
    node_id='my_business_processor'
)
```

## 🚨 Cosa NON Fare

### ❌ Non Aggiungere Processori Business al Server
```python
# ❌ SBAGLIATO - Non aggiungere al server
class MyDocumentProcessor(BaseNodeProcessor):  # Business logic nel server
    pass
```

### ❌ Non Creare Fallback Silenziosi
```python  
# ❌ SBAGLIATO - Fallback che nascondono errori
try:
    return pdk_processor.execute()
except:
    return fallback_processor.execute()  # Nasconde problemi PDK
```

### ❌ Non Modificare Database per Cambiare Implementazioni
```sql
-- ❌ SBAGLIATO - Il database contiene solo metadati
UPDATE workflow_nodes SET node_type = 'NewProcessor' WHERE node_type = 'OldProcessor';
```

## ✅ Cosa Fare

### ✅ Errori Chiari e Trasparenti
```python
# ✅ GIUSTO - Errore chiaro se PDK non disponibile
def get_processor(processor_name):
    if processor_name in CORE_PROCESSORS:
        return CORE_PROCESSORS[processor_name] 
    else:
        raise KeyError(
            f"Processore '{processor_name}' NON è un processore core. "
            f"Per processori business usa PDKNodeProcessor e assicurati che PDK sia attivo."
        )
```

### ✅ Separazione Chiara Core vs Business
```python
# ✅ GIUSTO - Core nel server
user_input = UserInputProcessor()  # Sempre disponibile

# ✅ GIUSTO - Business nel PDK  
pdf_parser = PDKNodeProcessor('core-business-processors-plugin', 'file_parsing')
```
  "node_type": "my_custom_node",
  "config": {
    "required_param": "value",
    "optional_param": 42
  },
  "position_x": 100,
  "position_y": 200
}
```

## 🔄 Sostituzione Processori Esistenti

Per sostituire un processore esistente (come fatto con gli stub):

### Metodo 1: Sostituzione Registry (Consigliato)

```python
# Nel node_registry.py
# Invece di:
# self.register_processor("event_input_node", OldStubProcessor())

# Sostituire con:
self.register_processor("event_input_node", NewRealProcessor())
```

**Vantaggi:**
- Nessuna modifica al database necessaria
- I workflow esistenti continuano a funzionare
- Cambio immediato per tutti i workflow

### Metodo 2: Nuovo Nome + Migrazione Graduale

```python
# Registrare entrambi temporaneamente
self.register_processor("event_input_node", OldStubProcessor())      # Legacy
self.register_processor("event_input_node_v2", NewRealProcessor())   # Nuovo
```

Poi aggiornare gradualmente i workflow JSON per usare `event_input_node_v2`.

## 📋 Processo Step-by-Step

### Per Nuovo Processore

1. **Analisi Requisiti**
   - Definire input/output del nodo
   - Identificare parametri configurabili
   - Documentare comportamento atteso

2. **Implementazione**
   - Creare classe processor
   - Implementare `execute()` e `validate_config()`
   - Aggiungere logging appropriato

3. **Registrazione**
   - Scegliere nome univoco per `register_processor()`
   - Aggiungere al registry
   - Aggiornare imports

4. **Testing**
   - Testare processore in isolamento
   - Creare workflow di test
   - Verificare integrazione

5. **Documentazione**
   - Aggiornare registry dei nodi
   - Documentare parametri e comportamento

### Per Sostituzione Processore

1. **Backup**
   - Testare il nuovo processore in isolamento
   - Verificare compatibilità input/output

2. **Sostituzione Graduale**
   - Registrare con nuovo nome temporaneamente
   - Testare su workflow non critici
   - Sostituire definitivamente nel registry

3. **Verifica**
   - Testare tutti i workflow che usano il processore
   - Monitorare log per errori
   - Rollback se necessario

## 🧪 Best Practices

### Naming Convention
```python
# Processori specifici di dominio
"pdf_parser"           # Per parsing PDF
"email_sender"         # Per invio email
"database_query"       # Per query database

# Processori generici
"text_processor"       # Elaborazione testo generico
"data_transformer"     # Trasformazione dati
"api_caller"          # Chiamate API
```

### Error Handling
```python
async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
    try:
        # Logica del processore
        result = await self._process_data(input_data)
        return {"status": "success", "data": result}
        
    except ValidationError as e:
        logger.error(f"Validation error in {node.name}: {e}")
        return {"status": "validation_error", "error": str(e)}
        
    except Exception as e:
        logger.error(f"Unexpected error in {node.name}: {e}")
        return {"status": "error", "error": str(e)}
```

### Configuration Validation
```python
def validate_config(self, config: Dict[str, Any]) -> bool:
    """Valida configurazione con controlli specifici."""
    required_fields = ["input_field", "output_format"]
    
    # Controllo campi obbligatori
    for field in required_fields:
        if field not in config:
            logger.error(f"Missing required config field: {field}")
            return False
    
    # Validazione valori
    if config.get("timeout", 0) < 0:
        logger.error("Timeout must be positive")
        return False
    
    return True
```

## 🔍 Debugging

### Verifica Registry
```python
# Test se un processore è registrato
from backend.engine.node_registry import NodeRegistry
registry = NodeRegistry()
processor = registry.get_processor("my_node_type")
print(f"Processor: {type(processor).__name__ if processor else 'NOT FOUND'}")
```

### Test Processore
```python
# Test isolato del processore
processor = MyCustomProcessor()
test_config = {"required_param": "test"}
is_valid = processor.validate_config(test_config)
print(f"Config valid: {is_valid}")
```

## 📚 Riferimenti

- **BaseNodeProcessor**: `backend/engine/node_registry.py`
- **ExecutionContext**: `backend/engine/execution_context.py`  
- **Registry Processori**: `backend/engine/processors/__init__.py`
- **Esempi Implementazione**: `backend/engine/processors/simple_real_processors.py`

## ⚠️ Punti Critici

1. **Mai modificare il database** per cambiare implementazioni
2. **Sempre testare** la compatibilità input/output
3. **Documentare** tutti i parametri configurabili
4. **Logging appropriato** per debugging
5. **Error handling** robusto per stabilità workflow

---

**Ricorda:** Il database definisce COSA eseguire, il Registry definisce COME eseguirlo.