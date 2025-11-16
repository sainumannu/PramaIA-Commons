# Guida al Push Multi-Repository PramaIA

## 📋 Panoramica

L'ecosistema PramaIA è strutturato con **repository multipli** per garantire modularità e indipendenza dei microservizi. Ogni componente ha il proprio repository GitHub dedicato, più un repository comune per file condivisi.

## 🏗️ Architettura Repository

### Repository Principale (Commons)
```
📁 C:\PramaIA (ROOT)
├── 🔗 Remote: https://github.com/sainumannu/PramaIA-Commons.git
├── 📄 File comuni: script, configurazioni, documentazione
├── 🔧 start-all.ps1 (script di avvio)
├── 📚 docs/ (documentazione condivisa)
└── 📝 File di configurazione globali
```

### Repository Microservizi
```
📁 PramaIAServer/
├── 🔗 Remote: https://github.com/sainumannu/PramaIA.git
├── 🐍 Backend FastAPI
├── ⚛️ Frontend React
└── 🗄️ Database principale

📁 PramaIA-PDK/
├── 🔗 Remote: https://github.com/sainumannu/PramaIA-PDK.git
├── 🔌 PDK Server Node.js
├── 🧩 Plugin Framework
└── 🔧 Development Kit

📁 PramaIA-Agents/
├── 🔗 Remote: https://github.com/sainumannu/PramaIA-Plugins.git
├── 🤖 Document Monitor Agent
├── 📄 PDF Processing Agents
└── 🔄 Autonomous Agents

📁 PramaIA-LogService/
├── 🔗 Remote: https://github.com/sainumannu/PramaIA-LogService.git
├── 📝 Centralized Logging
├── 🔍 Log Analysis
└── 📊 Monitoring Dashboard

📁 PramaIA-VectorstoreService/
├── 🔗 Remote: https://github.com/sainumannu/PramaIA-VectorstoreService.git
├── 🗄️ ChromaDB Management
├── 🔍 Vector Search
└── 🧠 Semantic Operations
```

### Directory Locali (Senza Git)
```
📁 PramaIA-Reconciliation/
├── ❌ Nessun remote (locale)
├── 🔄 Reconciliation Service
└── 🔧 Development/Testing
```

## 🚀 Procedura di Push Corretta

### 1. Verifica Status Multi-Repository

```powershell
# Verifica repository root
git status

# Verifica tutti i microservizi
Get-ChildItem -Directory | Where-Object { Test-Path "$($_.Name)/.git" } | ForEach-Object {
    Write-Host "=== $($_.Name) ===" -ForegroundColor Yellow
    Push-Location $_.Name
    git status
    Pop-Location
    Write-Host ""
}
```

### 2. Commit Repository Root (PramaIA-Commons)

```powershell
# Nel directory root C:\PramaIA
git add .
git commit -m "feat: [descrizione delle modifiche comuni]

- Script di configurazione
- Documentazione condivisa  
- File di configurazione globali
- Utilities cross-service"

git push origin main
```

### 3. Commit Microservizi Modificati

#### PramaIAServer (Backend + Frontend)
```powershell
cd PramaIAServer
git add .
git commit -m "feat: [descrizione modifiche server]

- Backend API updates
- Frontend components
- Database migrations
- Configuration updates"

git push origin main
cd ..
```

#### PDK Server
```powershell
cd PramaIA-PDK
git add .
git commit -m "feat: [descrizione modifiche PDK]

- Plugin implementations
- Node processors
- Framework updates
- Development tools"

git push origin main
cd ..
```

#### Altri Servizi (se modificati)
```powershell
# LogService
cd PramaIA-LogService
git add .
git commit -m "feat: [descrizione modifiche logging]"
git push origin main
cd ..

# VectorstoreService  
cd PramaIA-VectorstoreService
git add .
git commit -m "feat: [descrizione modifiche vectorstore]"
git push origin main
cd ..

# Agents
cd PramaIA-Agents
git add .
git commit -m "feat: [descrizione modifiche agents]"
git push origin main
cd ..
```

## 🔍 Script di Verifica Automatica

### Controllo Remote Repository

```powershell
# Script per verificare tutti i remote configurati
Write-Host "🔍 VERIFICA CONFIGURAZIONE REPOSITORY" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Repository root
Write-Host "`n📁 ROOT (PramaIA-Commons):" -ForegroundColor Cyan
git remote -v

# Microservizi
$services = @("PramaIAServer", "PramaIA-PDK", "PramaIA-Agents", "PramaIA-LogService", "PramaIA-VectorstoreService")

foreach ($service in $services) {
    if (Test-Path $service) {
        Write-Host "`n📁 $service" -ForegroundColor Cyan
        Push-Location $service
        if (Test-Path ".git") {
            git remote -v
        } else {
            Write-Host "   ❌ Nessun repository git configurato" -ForegroundColor Red
        }
        Pop-Location
    } else {
        Write-Host "`n📁 $service" -ForegroundColor Cyan  
        Write-Host "   ⚠️  Directory non trovata" -ForegroundColor Yellow
    }
}
```

### Controllo Status Multi-Repository

```powershell
# Script per verificare lo status di tutti i repository
Write-Host "📊 STATUS MULTI-REPOSITORY" -ForegroundColor Green
Write-Host "==========================" -ForegroundColor Green

# Root
Write-Host "`n🔹 ROOT:" -ForegroundColor Cyan
$status = git status --porcelain
if ($status) {
    Write-Host "   📝 Modifiche presenti" -ForegroundColor Yellow
    git status --short
} else {
    Write-Host "   ✅ Repository pulito" -ForegroundColor Green
}

# Microservizi
$services = @("PramaIAServer", "PramaIA-PDK", "PramaIA-Agents", "PramaIA-LogService", "PramaIA-VectorstoreService")

foreach ($service in $services) {
    if (Test-Path "$service/.git") {
        Write-Host "`n🔹 $service" -ForegroundColor Cyan
        Push-Location $service
        $status = git status --porcelain
        if ($status) {
            Write-Host "   📝 Modifiche presenti" -ForegroundColor Yellow
            git status --short
        } else {
            Write-Host "   ✅ Repository pulito" -ForegroundColor Green
        }
        Pop-Location
    }
}
```

## ⚠️ Considerazioni Importanti

### 🔒 **Ordine di Push Raccomandato**
1. **Prima i microservizi** (dipendenze specifiche)
2. **Poi il repository commons** (configurazioni generali)
3. **Verificare la sincronizzazione** tra tutti i repository

### 🎯 **Best Practices**
- **Commit atomici**: Un commit per feature/bugfix
- **Messaggi descrittivi**: Seguire conventional commits
- **Branch strategy**: Usare feature branches per sviluppo
- **Tag releases**: Taggare le versioni stabili

### 🚨 **Errori Comuni da Evitare**
- ❌ Non verificare lo status dei submoduli
- ❌ Pushare solo il repository root dimenticando i microservizi  
- ❌ Commit troppo grandi che mescolano microservizi diversi
- ❌ Non sincronizzare le dipendenze tra repository

### 📋 **Checklist Pre-Push**
- [ ] Verificato status di tutti i repository
- [ ] Testato che tutti i servizi si avviano correttamente
- [ ] Controllato che non ci siano conflitti di configurazione
- [ ] Verificato che le dipendenze tra servizi siano soddisfatte
- [ ] Commit messages seguono lo standard conventional commits

## 🔧 Script di Automazione Completa

### Push Automatico Multi-Repository

```powershell
# Script completo per push coordinato
param(
    [string]$CommitMessage = "Update: Multi-service changes",
    [switch]$DryRun = $false
)

Write-Host "🚀 PUSH MULTI-REPOSITORY AUTOMATICO" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

if ($DryRun) {
    Write-Host "🔍 MODALITÀ DRY-RUN - Nessun push effettivo" -ForegroundColor Yellow
}

$services = @(
    @{Name="ROOT"; Path="."; Remote="PramaIA-Commons"},
    @{Name="PramaIAServer"; Path="PramaIAServer"; Remote="PramaIA"},
    @{Name="PDK"; Path="PramaIA-PDK"; Remote="PramaIA-PDK"},
    @{Name="Agents"; Path="PramaIA-Agents"; Remote="PramaIA-Plugins"},
    @{Name="LogService"; Path="PramaIA-LogService"; Remote="PramaIA-LogService"},
    @{Name="VectorStore"; Path="PramaIA-VectorstoreService"; Remote="PramaIA-VectorstoreService"}
)

foreach ($service in $services) {
    Write-Host "`n📁 Processing $($service.Name)" -ForegroundColor Cyan
    
    if ($service.Path -ne "." -and !(Test-Path $service.Path)) {
        Write-Host "   ⚠️  Directory non trovata: $($service.Path)" -ForegroundColor Yellow
        continue
    }
    
    Push-Location $service.Path
    
    # Verifica se ci sono modifiche
    $status = git status --porcelain
    if (-not $status) {
        Write-Host "   ✅ Nessuna modifica da committare" -ForegroundColor Green
        Pop-Location
        continue
    }
    
    Write-Host "   📝 Modifiche trovate:" -ForegroundColor Yellow
    git status --short
    
    if (-not $DryRun) {
        # Add, commit e push
        git add .
        git commit -m "$CommitMessage - $($service.Name)"
        git push origin main
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Push completato con successo" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Errore durante il push" -ForegroundColor Red
        }
    } else {
        Write-Host "   🔍 Sarebbe stato fatto: git add . && git commit && git push" -ForegroundColor Gray
    }
    
    Pop-Location
}

Write-Host "`n🎉 Processo completato!" -ForegroundColor Green
```

### Utilizzo dello Script

```powershell
# Test senza modifiche effettive
.\push-all-repos.ps1 -DryRun

# Push effettivo con messaggio personalizzato
.\push-all-repos.ps1 -CommitMessage "feat: Implement CRUD pipeline architecture"

# Push rapido con messaggio standard
.\push-all-repos.ps1
```

---

*Documentazione aggiornata: 15 Novembre 2025*  
*Versione: v1.0.0*  
*Ecosistema PramaIA Multi-Repository*