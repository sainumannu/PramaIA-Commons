# Come Implementare Nuovi Nodi in PramaIA

**Guida completa per l'implementazione corretta di nuovi processori di nodi**

## 🎯 Panoramica

I nodi in PramaIA seguono un'architettura Registry-based dove:
- Il **database** contiene solo i **metadati** dei workflow (struttura, configurazione)
- Il **NodeRegistry** contiene le **implementazioni** effettive dei processori
- I workflow vengono eseguiti attraverso il registry, NON modificando il database

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

### 1. Creare il Processore

Creare un nuovo processore che eredita da `BaseNodeProcessor`:

```python
# backend/engine/processors/my_processors.py
from backend.engine.node_registry import BaseNodeProcessor
from backend.engine.execution_context import ExecutionContext
from typing import Dict, Any

class MyCustomProcessor(BaseNodeProcessor):
    """Descrizione del processore."""
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        """Logica di elaborazione del nodo."""
        input_data = context.get_input_for_node(node.node_id)
        
        # Elaborazione...
        result = {
            "processed_data": "...",
            "status": "success"
        }
        
        return result
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida la configurazione del nodo."""
        # Controlla parametri richiesti
        return "required_param" in config
```

### 2. Registrare nel NodeRegistry

Aggiungere il processore al registry in `backend/engine/node_registry.py`:

```python
# Nel metodo _register_default_processors()

def _register_default_processors(self):
    # ... altri import ...
    
    # Import del nuovo processore
    from backend.engine.processors.my_processors import MyCustomProcessor
    
    # ... altre registrazioni ...
    
    # Registrazione del nuovo processore
    self.register_processor("my_custom_node", MyCustomProcessor())
```

### 3. Aggiornare il Modulo __init__.py

Assicurarsi che il processore sia esportato correttamente:

```python
# backend/engine/processors/__init__.py

from .my_processors import MyCustomProcessor

# Aggiungere a __all__
__all__ = [
    # ... altri processori ...
    'MyCustomProcessor',
]
```

### 4. Usare nei Workflow JSON

Nei file JSON dei workflow, riferirsi al processore con il nome registrato:

```json
{
  "node_id": "node_001",
  "name": "My Custom Node",
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