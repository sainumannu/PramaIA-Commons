# Architettura PDK Pura - Guida di Migrazione

**Guida per comprendere e utilizzare la nuova architettura separata**

## 🎯 Panoramica del Cambiamento

**Prima (Monolitico):**
```
PramaIA Server
├── input_processors.py
├── event_input_processor.py      ❌ Business nel server
├── file_parsing_processor.py     ❌ Business nel server  
├── vector_store_processor.py     ❌ Business nel server
├── document_processor.py         ❌ Business nel server
└── llm_processors.py
```

**Ora (PDK Puro):**
```
PramaIA Server (Solo Core)
├── input_processors.py           ✅ I/O Core
├── output_processors.py          ✅ I/O Core
├── llm_processors.py             ✅ LLM Core
├── api_processors.py             ✅ API Core
├── data_processors.py            ✅ Data Core
├── rag_processors.py             ✅ RAG Core
└── pdk_processors.py             ✅ Proxy PDK

PramaIA-PDK (Business Logic)
└── plugins/core-business-processors-plugin/
    ├── nodes/event_input.js       🔌 Business nel PDK
    ├── nodes/file_parsing.js      🔌 Business nel PDK
    ├── nodes/metadata_manager.js  🔌 Business nel PDK
    ├── nodes/document_processor.js 🔌 Business nel PDK
    ├── nodes/vector_store.js      🔌 Business nel PDK
    └── nodes/event_logger.js      🔌 Business nel PDK
```

## ✅ Vantaggi della Nuova Architettura

### 🛡️ Resilienza
- **Server funziona** anche se PDK down per operazioni core (chat, API, I/O base)
- **Errori chiari** invece di fallback confusi
- **Zero dipendenze nascoste** tra server e business logic

### 🚀 Estensibilità  
- **Nuovi processori business** senza modificare server
- **Plugin sistema** per funzionalità avanzate
- **Versioning indipendente** server vs business logic

### 🔍 Debuggabilità
- **Separazione responsabilità** crystal clear
- **Niente fallback silenziosi** che nascondono problemi
- **Log e errori** tracciabili per componente

## 📋 Guida di Migrazione

### Per Sviluppatori

**Prima:**
```python
# Vecchio modo - tutto nel server
from backend.engine.processors import EventInputProcessor
processor = EventInputProcessor()
```

**Ora:**
```python
# Nuovo modo - core nel server, business nel PDK
from backend.engine.processors import PDKNodeProcessor

# Per business logic
business_processor = PDKNodeProcessor(
    plugin_id='core-business-processors-plugin',
    node_id='event_input'
)

# Per operazioni core 
from backend.engine.processors import get_core_processor
core_processor = get_core_processor('UserInputProcessor')
```

### Per Workflow JSON

**Prima:**
```json
{
  "node_type": "EventInputProcessor",
  "name": "Event Input"
}
```

**Ora:**
```json
{
  "node_type": "PDKNodeProcessor",
  "name": "Event Input",
  "config": {
    "plugin_id": "core-business-processors-plugin",
    "node_id": "event_input"
  }
}
```

## 🚨 Gestione Errori

### Comportamento con PDK Down

**Core (funziona sempre):**
```python
✅ user_input = get_core_processor('UserInputProcessor')      # OK
✅ gpt_chat = get_core_processor('OpenAIProcessor')           # OK  
✅ api_call = get_core_processor('HTTPRequestProcessor')      # OK
```

**Business (richiede PDK):**
```python
❌ event_proc = PDKNodeProcessor('...', 'event_input')        # HTTP Error se PDK down
❌ pdf_proc = PDKNodeProcessor('...', 'file_parsing')         # HTTP Error se PDK down
```

**Errore se business richiesto dal core:**
```python
❌ event_proc = get_core_processor('EventInputProcessor')     # KeyError esplicito
```

### Esempi di Errori Chiari

```python
# ❌ PDK non disponibile
PDKConnectionError: "Impossibile connettersi al PDK server su localhost:3001. 
Verificare che il PDK sia avviato e raggiungibile."

# ❌ Processore business richiesto dal core  
KeyError: "Processore 'EventInputProcessor' NON è un processore core. 
Per processori business usa PDKNodeProcessor e assicurati che PDK sia attivo."
```

## 🎯 Principi Architetturali

### ✅ Cosa Fare

1. **Server Minimale**: Solo funzionalità core essenziali
2. **PDK per Business**: Tutta la business logic nel PDK
3. **Errori Espliciti**: Niente fallback che nascondono problemi
4. **Separazione Clara**: Responsabilità ben definite

### ❌ Cosa NON Fare

1. **❌ Non aggiungere business logic nel server**
2. **❌ Non creare fallback silenziosi**  
3. **❌ Non nascondere errori PDK**
4. **❌ Non duplicare logica core/PDK**

## 🔄 Piano di Implementazione

### Fase 1: Core Stabilizzato ✅
- [x] Server con solo processori core
- [x] PDKNodeProcessor come proxy universale
- [x] Errori chiari senza fallback
- [x] Tests core funzionanti

### Fase 2: Plugin Business ✅  
- [x] Plugin core-business-processors-plugin
- [x] EventInputProcessor → event_input.js
- [x] FileParsingProcessor → file_parsing.js
- [ ] MetadataManagerProcessor → metadata_manager.js
- [ ] DocumentProcessorProcessor → document_processor.js  
- [ ] VectorStoreOperationsProcessor → vector_store.js
- [ ] EventLoggerProcessor → event_logger.js

### Fase 3: Test e Validazione 🔄
- [ ] Tests end-to-end con PDK
- [ ] Validazione performance  
- [ ] Documentazione aggiornata
- [ ] Training team di sviluppo

## 💡 FAQ

**Q: Cosa succede se PDK va down durante l'esecuzione?**
A: Le operazioni core continuano a funzionare. Le operazioni business falliscono con errore HTTP chiaro e tracciabile.

**Q: Come debugging quando qualcosa non funziona?**  
A: Controlla prima se è processore core (sempre disponibile) o business (richiede PDK). Error message ti dirà esattamente cosa manca.

**Q: Performance impact del PDK proxy?**
A: Latenza HTTP aggiuntiva per business logic, ma core operations sono istantanee. Trade-off accettabile per architettura pulita.

**Q: Come aggiungere nuovi processori?**
A: Core: raramente, solo per I/O/LLM essenziali. Business: sempre nel PDK come plugin.

---

**Data aggiornamento:** 16 Novembre 2025  
**Versione:** PramaIA v2.2.0 - PDK Architecture