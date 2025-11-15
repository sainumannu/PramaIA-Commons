"""
Correzione: Aggiungi ID UUID ai trigger che non ne hanno
"""
import sqlite3
import uuid

conn = sqlite3.connect('backend/db/database.db')
cur = conn.cursor()

# Aggiorna i trigger esistenti con UUID
cur.execute("SELECT rowid, name FROM workflow_triggers WHERE id IS NULL OR id = ''")
triggers = cur.fetchall()

print(f"Trovati {len(triggers)} trigger senza ID")

for rowid, name in triggers:
    new_id = str(uuid.uuid4())
    cur.execute("UPDATE workflow_triggers SET id = ? WHERE rowid = ?", (new_id, rowid))
    print(f"Aggiunto ID {new_id} al trigger '{name}'")

conn.commit()

# Verifica
cur.execute("SELECT id, name, event_type FROM workflow_triggers")
print("\nTrigger aggiornati:")
for row in cur.fetchall():
    print(f"  ID={row[0]}, name='{row[1]}', event_type='{row[2]}'")

conn.close()
print("\nCorrezione completata!")
