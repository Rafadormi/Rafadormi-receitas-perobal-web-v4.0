import sqlite3
import os

def inspect_database(db_path):
    if not os.path.exists(db_path):
        print(f"Arquivo {db_path} não encontrado!")
        return
    
    print(f"\n=== INSPETORANDO: {db_path} ===")
    print(f"Tamanho do arquivo: {os.path.getsize(db_path)} bytes")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\nTabelas encontradas: {len(tables)}")
        for table in tables:
            table_name = table[0]
            print(f"\n--- TABELA: {table_name} ---")
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"Registros: {count}")
            
            # Mostrar estrutura
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("Colunas:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Mostrar alguns registros se houver
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()
                print("Primeiros registros:")
                for i, row in enumerate(rows, 1):
                    print(f"  {i}: {row}")
                if count > 5:
                    print(f"  ... e mais {count - 5} registros")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao inspecionar banco: {e}")

if __name__ == "__main__":
    # Inspecionar ambos os bancos
    inspect_database("receitas.db")
    inspect_database("app.db") 