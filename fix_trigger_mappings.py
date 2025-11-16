#!/usr/bin/env python3
"""
AGGIORNAMENTO TRIGGER → WORKFLOW CRUD
=====================================

Aggiorna i trigger per utilizzare i nuovi workflow CRUD importati.
"""

import sqlite3
import sys

def update_trigger_mappings():
    """Aggiorna il mapping dei trigger verso i workflow CRUD."""
    print("🔧 AGGIORNAMENTO MAPPING TRIGGER → WORKFLOW")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('C:/PramaIA/backend/db/database.db')
        cursor = conn.cursor()
        
        # Backup stato attuale
        cursor.execute("SELECT * FROM workflow_triggers")
        backup_triggers = cursor.fetchall()
        print(f"📋 Backup di {len(backup_triggers)} trigger esistenti")
        
        # Query di aggiornamento
        updates = [
            {
                "query": "UPDATE workflow_triggers SET workflow_id = ? WHERE event_type = ?",
                "params": ("wf_7af99caf311a", "pdf_file_added"),
                "description": "pdf_file_added → PDF Document CREATE Pipeline"
            },
            {
                "query": "UPDATE workflow_triggers SET workflow_id = ? WHERE event_type = ?",
                "params": ("wf_fcad5d0befdb", "pdf_file_updated"),
                "description": "pdf_file_updated → PDF Document UPDATE Pipeline"
            },
            {
                "query": "UPDATE workflow_triggers SET workflow_id = ? WHERE event_type = ?",
                "params": ("wf_04f5046263ff", "pdf_file_deleted"),
                "description": "pdf_file_deleted → PDF Document DELETE Pipeline"
            }
        ]
        
        # Esegui aggiornamenti
        for update in updates:
            print(f"🔄 Aggiorno: {update['description']}")
            cursor.execute(update["query"], update["params"])
            rows_affected = cursor.rowcount
            print(f"   ✅ {rows_affected} record aggiornati")
        
        # Aggiungi nuovo trigger per READ
        print("🆕 Aggiungendo trigger per READ Pipeline...")
        cursor.execute("""
            INSERT INTO workflow_triggers (id, name, event_type, source, workflow_id, active, conditions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "trigger_pdf_read_query",
            "Trigger Query PDF", 
            "pdf_search_query",
            "search-api-source",
            "wf_86ee1359f7f8",
            1,
            "{}"
        ))
        print("   ✅ Nuovo trigger READ aggiunto")
        
        # Commit delle modifiche
        conn.commit()
        print("\n✅ Tutte le modifiche salvate nel database")
        
        # Verifica risultato
        print("\n🔍 VERIFICA POST-AGGIORNAMENTO:")
        cursor.execute("""
            SELECT t.name, t.event_type, t.workflow_id, w.name as workflow_name, t.active
            FROM workflow_triggers t
            LEFT JOIN workflows w ON t.workflow_id = w.workflow_id
            ORDER BY t.event_type
        """)
        
        results = cursor.fetchall()
        for trigger_name, event_type, workflow_id, workflow_name, active in results:
            status = "✅ Attivo" if active else "❌ Disattivo"
            wf_status = workflow_name if workflow_name else "❌ NON TROVATO"
            print(f"   • {trigger_name} ({event_type}) → {wf_status} | {status}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Errore aggiornamento: {e}")
        return False

def verify_trigger_coverage():
    """Verifica che tutti i workflow CRUD abbiano un trigger."""
    print("\n📊 VERIFICA COPERTURA TRIGGER")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('C:/PramaIA/backend/db/database.db')
        cursor = conn.cursor()
        
        # Workflow CRUD
        cursor.execute("SELECT workflow_id, name FROM workflows WHERE name LIKE '%PDF%'")
        crud_workflows = cursor.fetchall()
        
        # Trigger attivi
        cursor.execute("SELECT workflow_id, event_type FROM workflow_triggers WHERE active = 1")
        trigger_mappings = cursor.fetchall()
        
        print("🔧 COPERTURA WORKFLOW → TRIGGER:")
        
        workflows_with_triggers = set(wid for wid, _ in trigger_mappings)
        
        for workflow_id, workflow_name in crud_workflows:
            if workflow_id in workflows_with_triggers:
                # Trova i trigger associati
                triggers = [event_type for wid, event_type in trigger_mappings if wid == workflow_id]
                print(f"   ✅ {workflow_name}")
                for trigger in triggers:
                    print(f"      ↳ {trigger}")
            else:
                print(f"   ⚠️  {workflow_name} (nessun trigger)")
        
        print(f"\n📈 STATISTICHE:")
        print(f"   • Workflow CRUD: {len(crud_workflows)}")
        print(f"   • Workflow con trigger: {len(workflows_with_triggers & set(wid for wid, _ in crud_workflows))}")
        print(f"   • Trigger attivi: {len(trigger_mappings)}")
        
        # Suggerimenti per trigger mancanti
        missing_triggers = []
        for workflow_id, workflow_name in crud_workflows:
            if workflow_id not in workflows_with_triggers:
                missing_triggers.append((workflow_id, workflow_name))
        
        if missing_triggers:
            print("\n💡 TRIGGER MANCANTI SUGGERITI:")
            for workflow_id, workflow_name in missing_triggers:
                if "READ" in workflow_name.upper():
                    print(f"   • {workflow_name} → query/search events")
                elif "CREATE" in workflow_name.upper():
                    print(f"   • {workflow_name} → file upload events")
        
        conn.close()
        return len(missing_triggers) == 0
        
    except Exception as e:
        print(f"❌ Errore verifica copertura: {e}")
        return False

def main():
    """Aggiornamento principale dei trigger."""
    print("🚀 AGGIORNAMENTO TRIGGER SISTEMA PDF")
    print("=" * 80)
    
    results = []
    
    # 1. Aggiorna mapping esistenti
    results.append(update_trigger_mappings())
    
    # 2. Verifica copertura
    if results[0]:
        results.append(verify_trigger_coverage())
    
    # Risultato finale
    print("\n" + "=" * 80)
    if all(results):
        print("✅ AGGIORNAMENTO TRIGGER COMPLETATO")
        print("   • Mapping aggiornati con successo")
        print("   • Copertura trigger verificata") 
        print("   • Sistema pronto per eventi PDF")
        print("\n💡 NEXT STEPS:")
        print("   1. Testare trigger con eventi simulati")
        print("   2. Verificare esecuzione workflow end-to-end")
        print("   3. Monitorare log per confermare funzionamento")
    else:
        print("⚠️ AGGIORNAMENTO PARZIALMENTE COMPLETATO")
        print("   Verificare i log sopra per dettagli")
    
    print("=" * 80)

if __name__ == "__main__":
    main()