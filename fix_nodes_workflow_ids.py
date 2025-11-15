"""
Correzione: Aggiorna workflow_id nei nodi e connessioni per usare la stringa FK corretta
"""
import sqlite3

conn = sqlite3.connect('backend/db/database.db')
cur = conn.cursor()

# Mappa id numerico -> workflow_id stringa
workflows_map = {
    1: 'pdf_document_add_workflow',
    2: 'pdf_document_delete_workflow',
    3: 'pdf_document_update_workflow'
}

print("Aggiornamento workflow_id nei nodi...")
for numeric_id, string_id in workflows_map.items():
    cur.execute(
        "UPDATE workflow_nodes SET workflow_id = ? WHERE workflow_id = ?",
        (string_id, str(numeric_id))
    )
    count = cur.rowcount
    print(f"  {numeric_id} -> '{string_id}': {count} nodi aggiornati")

print("\nAggiornamento workflow_id nelle connessioni...")
for numeric_id, string_id in workflows_map.items():
    cur.execute(
        "UPDATE workflow_connections SET workflow_id = ? WHERE workflow_id = ?",
        (string_id, str(numeric_id))
    )
    count = cur.rowcount
    print(f"  {numeric_id} -> '{string_id}': {count} connessioni aggiornate")

conn.commit()

# Verifica
print("\nVerifica nodi:")
cur.execute("SELECT workflow_id, COUNT(*) FROM workflow_nodes GROUP BY workflow_id")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} nodi")

print("\nVerifica connessioni:")
cur.execute("SELECT workflow_id, COUNT(*) FROM workflow_connections GROUP BY workflow_id")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} connessioni")

conn.close()
print("\n✅ Correzione completata!")
