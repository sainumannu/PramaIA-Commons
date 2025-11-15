"""
Correzione: Aggiorna workflow_id nei trigger per usare la stringa invece dell'INTEGER
"""
import sqlite3

conn = sqlite3.connect('backend/db/database.db')
cur = conn.cursor()

# Mappa id -> workflow_id
workflows_map = {
    1: 'pdf_document_add_workflow',
    2: 'pdf_document_delete_workflow',
    3: 'pdf_document_update_workflow'
}

print("Aggiornamento workflow_id nei trigger...")

for numeric_id, string_id in workflows_map.items():
    cur.execute(
        "UPDATE workflow_triggers SET workflow_id = ? WHERE workflow_id = ?",
        (string_id, str(numeric_id))
    )
    print(f"  {numeric_id} -> '{string_id}'")

conn.commit()

# Verifica
cur.execute("SELECT id, name, event_type, workflow_id FROM workflow_triggers")
print("\nTrigger aggiornati:")
for row in cur.fetchall():
    print(f"  {row[1]}:")
    print(f"    event_type = '{row[2]}'")
    print(f"    workflow_id = '{row[3]}'")
    print()

conn.close()
print("Correzione completata!")
