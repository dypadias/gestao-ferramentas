from database.db_manager import get_connection

def limpar_tabelas():
    conn = get_connection()
    cursor = conn.cursor()
    # Desativa temporariamente as chaves estrangeiras para evitar conflitos
    cursor.execute("PRAGMA foreign_keys = OFF")
    cursor.execute("DELETE FROM emprestimos")
    cursor.execute("DELETE FROM manutencoes")
    cursor.execute("DELETE FROM ferramentas")
    cursor.execute("DELETE FROM funcionarios")
    cursor.execute("DELETE FROM locais")
    # Reseta os contadores de auto-incremento (opcional)
    cursor.execute("DELETE FROM sqlite_sequence")
    cursor.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    conn.close()
    print("✅ Banco de dados limpo com sucesso! Todos os dados foram removidos.")

if __name__ == "__main__":
    limpar_tabelas()