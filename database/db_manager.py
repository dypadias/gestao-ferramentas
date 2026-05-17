import sqlite3
import os
import csv

# Define o caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), 'gestao.db')


def get_connection():
    """
    Retorna uma conexão com o banco de dados SQLite.
    Configura row_factory para permitir acesso às colunas pelo nome.
    
    Returns:
        sqlite3.Connection: Conexão com o banco de dados
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Inicializa o banco de dados lendo e executando o schema.sql.
    Cria todas as tabelas se não existirem.
    """
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Lê o arquivo schema.sql
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        
        # Executa o schema
        cursor.executescript(schema)
        
        # Garante colunas novas em bases existentes
        _ensure_column(cursor, 'funcionarios', 'ativo', 'INTEGER DEFAULT 1')
        _ensure_column(cursor, 'locais', 'ativo', 'INTEGER DEFAULT 1')
        _ensure_column(cursor, 'ferramentas', 'status', "TEXT DEFAULT 'DISPONIVEL'")
        _ensure_column(cursor, 'ferramentas', 'situacao', "TEXT DEFAULT 'OK'")
        _ensure_column(cursor, 'emprestimos', 'data_devolucao_real', 'TIMESTAMP')
        _ensure_column(cursor, 'emprestimos', 'status', "TEXT DEFAULT 'ATIVO'")
        _ensure_column(cursor, 'emprestimos', 'local_id', 'INTEGER')
        _ensure_column(cursor, 'emprestimos', 'observacao_devolucao', 'TEXT')
        conn.commit()
        
        print("✓ Banco de dados inicializado com sucesso!")
        
    except FileNotFoundError:
        print(f"✗ Erro: Arquivo {schema_path} não encontrado")
        raise
    except sqlite3.Error as e:
        print(f"✗ Erro ao inicializar banco de dados: {e}")
        raise
    finally:
        if conn:
            conn.close()


def _ensure_column(cursor, table_name, column_name, column_definition):
    try:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' not in str(e).lower():
            raise


def cadastrar_funcionario(nome, cargo):
    """
    Cadastra um novo funcionário no banco de dados.
    
    Args:
        nome (str): Nome do funcionário
        cargo (str): Cargo do funcionário
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO funcionarios (nome, cargo) VALUES (?, ?)", (nome, cargo))
        conn.commit()
        print(f"✓ Funcionário '{nome}' cadastrado com sucesso!")
    except sqlite3.Error as e:
        print(f"✗ Erro ao cadastrar funcionário: {e}")
        raise
    finally:
        if conn:
            conn.close()


def cadastrar_ferramenta(nome, patrimonio):
    """
    Cadastra uma nova ferramenta no banco de dados.
    
    Args:
        nome (str): Nome da ferramenta
        patrimonio (str): Número do patrimônio
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ferramentas (nome, patrimonio) VALUES (?, ?)", (nome, patrimonio))
        conn.commit()
        print(f"✓ Ferramenta '{nome}' cadastrada com sucesso!")
    except sqlite3.Error as e:
        print(f"✗ Erro ao cadastrar ferramenta: {e}")
        raise
    finally:
        if conn:
            conn.close()


def cadastrar_local(nome):
    """
    Cadastra um novo local/setor no banco de dados.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO locais (nome) VALUES (?)", (nome,))
        conn.commit()
        print(f"✓ Local '{nome}' cadastrado com sucesso!")
    except sqlite3.Error as e:
        print(f"✗ Erro ao cadastrar local: {e}")
        raise
    finally:
        if conn:
            conn.close()


def buscar_todas_ferramentas():
    """
    Retorna todas as ferramentas cadastradas.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, patrimonio, status, situacao FROM ferramentas")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"âœ— Erro ao buscar ferramentas: {e}")
        raise
    finally:
        if conn:
            conn.close()


def atualizar_ferramenta(ferramenta_id, nome, patrimonio, situacao):
    """
    Atualiza os dados de uma ferramenta cadastrada.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE ferramentas SET nome = ?, patrimonio = ?, situacao = ? WHERE id = ?",
            (nome, patrimonio, situacao, ferramenta_id)
        )
        conn.commit()
        print(f"âœ“ Ferramenta '{nome}' atualizada com sucesso!")
    except sqlite3.Error as e:
        print(f"âœ— Erro ao atualizar ferramenta: {e}")
        raise
    finally:
        if conn:
            conn.close()


def buscar_todos_funcionarios():
    """
    Retorna todos os funcionários cadastrados.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, cargo, ativo FROM funcionarios")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"âœ— Erro ao buscar funcionários: {e}")
        raise
    finally:
        if conn:
            conn.close()


def atualizar_funcionario(funcionario_id, nome, cargo, ativo):
    """
    Atualiza os dados de um funcionário cadastrado.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE funcionarios SET nome = ?, cargo = ?, ativo = ? WHERE id = ?",
            (nome, cargo, ativo, funcionario_id)
        )
        conn.commit()
        print(f"✓ Funcionário '{nome}' atualizado com sucesso!")
    except sqlite3.Error as e:
        print(f"✗ Erro ao atualizar funcionário: {e}")
        raise
    finally:
        if conn:
            conn.close()


def buscar_todos_locais():
    """
    Retorna todos os locais cadastrados.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, ativo FROM locais")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"âœ— Erro ao buscar locais: {e}")
        raise
    finally:
        if conn:
            conn.close()


def atualizar_local(local_id, nome, ativo):
    """
    Atualiza os dados de um local cadastrado.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE locais SET nome = ?, ativo = ? WHERE id = ?",
            (nome, ativo, local_id)
        )
        conn.commit()
        print(f"✓ Local '{nome}' atualizado com sucesso!")
    except sqlite3.Error as e:
        print(f"✗ Erro ao atualizar local: {e}")
        raise
    finally:
        if conn:
            conn.close()


def buscar_funcionarios_ativos():
    """
    Retorna todos os funcionários ativos registrados no banco.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, cargo FROM funcionarios WHERE ativo = 1 ORDER BY nome")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"✗ Erro ao buscar funcionários ativos: {e}")
        raise
    finally:
        if conn:
            conn.close()


def buscar_locais_ativos():
    """
    Retorna os locais ativos para uso em empréstimos.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM locais WHERE ativo = 1 ORDER BY nome")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"✗ Erro ao buscar locais ativos: {e}")
        raise
    finally:
        if conn:
            conn.close()


def buscar_ferramentas_disponiveis():
    """
    Retorna todas as ferramentas disponíveis para empréstimo.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, nome, patrimonio
            FROM ferramentas
            WHERE LOWER(status) = 'disponivel'
              AND UPPER(COALESCE(situacao, 'OK')) = 'OK'
            ORDER BY nome
            """
        )
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"✗ Erro ao buscar ferramentas disponíveis: {e}")
        raise
    finally:
        if conn:
            conn.close()


def registrar_emprestimo(funcionario_id, ferramenta_id, gestor_id, local_id, data_previsao):
    """
    Registra um novo empréstimo e atualiza o status da ferramenta.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO emprestimos (funcionario_id, ferramenta_id, gestor_id, local_id, data_previsao) VALUES (?, ?, ?, ?, ?)",
            (funcionario_id, ferramenta_id, gestor_id, local_id, data_previsao)
        )
        cursor.execute(
            "UPDATE ferramentas SET status = 'EMPRESTADA' WHERE id = ?",
            (ferramenta_id,)
        )
        conn.commit()
        print(f"✓ Empréstimo registrado: funcionario={funcionario_id}, ferramenta={ferramenta_id}, local={local_id}")
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"✗ Erro ao registrar empréstimo: {e}")
        raise
    finally:
        if conn:
            conn.close()


def buscar_emprestimos_ativos():
    """
    Retorna os empréstimos ativos com dados do funcionário e da ferramenta.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                e.id AS emprestimo_id,
                e.ferramenta_id,
                f.nome AS ferramenta_nome,
                f.patrimonio AS ferramenta_patrimonio,
                func.nome AS funcionario_nome,
                l.nome AS local_nome,
                e.data_previsao
            FROM emprestimos AS e
            JOIN funcionarios AS func ON e.funcionario_id = func.id
            JOIN ferramentas AS f ON e.ferramenta_id = f.id
            LEFT JOIN locais AS l ON e.local_id = l.id
            WHERE e.status = 'ATIVO'
            ORDER BY e.data_previsao
            """
        )
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"✗ Erro ao buscar empréstimos ativos: {e}")
        raise
    finally:
        if conn:
            conn.close()


def buscar_historico_completo(termo_busca=""):
    """
    Retorna o historico completo de emprestimos devolvidos.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT
                e.id AS emprestimo_id,
                e.funcionario_id,
                e.ferramenta_id,
                e.gestor_id,
                e.local_id,
                f.nome AS ferramenta_nome,
                f.patrimonio AS ferramenta_patrimonio,
                func.nome AS funcionario_nome,
                l.nome AS local_nome,
                e.data_emprestimo,
                e.data_devolucao,
                e.data_previsao,
                e.status,
                e.observacoes,
                e.observacao_devolucao
            FROM emprestimos AS e
            JOIN funcionarios AS func ON e.funcionario_id = func.id
            JOIN ferramentas AS f ON e.ferramenta_id = f.id
            LEFT JOIN locais AS l ON e.local_id = l.id
            WHERE e.data_devolucao IS NOT NULL
        """
        params = []

        if termo_busca:
            query += """
                AND (
                    f.nome LIKE ?
                    OR f.patrimonio LIKE ?
                    OR func.nome LIKE ?
                    OR l.nome LIKE ?
                )
            """
            termo_like = f"%{termo_busca}%"
            params.extend([termo_like, termo_like, termo_like, termo_like])

        query += " ORDER BY e.data_devolucao DESC, e.data_emprestimo DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"âœ— Erro ao buscar histórico completo: {e}")
        raise
    finally:
        if conn:
            conn.close()


def exportar_historico_csv(termo_busca="", caminho_arquivo=None):
    """
    Exporta o histórico de empréstimos para um arquivo CSV compatível com Excel.
    """
    registros = buscar_historico_completo(termo_busca)

    if caminho_arquivo is None:
        caminho_arquivo = os.path.join(os.path.dirname(__file__), 'historico_emprestimos.csv')

    with open(caminho_arquivo, 'w', encoding='utf-8-sig', newline='') as arquivo:
        escritor = csv.writer(arquivo, delimiter=';')
        escritor.writerow([
            'Ferramenta',
            'Patrimônio',
            'Funcionário',
            'Local de Uso',
            'Data Empréstimo',
            'Data Devolução',
            'Observação',
        ])

        for registro in registros:
            escritor.writerow([
                registro.get('ferramenta_nome', ''),
                registro.get('ferramenta_patrimonio', ''),
                registro.get('funcionario_nome', ''),
                registro.get('local_nome', ''),
                registro.get('data_emprestimo', ''),
                registro.get('data_devolucao', ''),
                registro.get('observacao_devolucao') or registro.get('observacoes', ''),
            ])

    return caminho_arquivo


def registrar_devolucao(emprestimo_id, ferramenta_id, situacao='OK', observacao=''):
    """
    Registra a devolução do empréstimo e atualiza o status da ferramenta.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE emprestimos
            SET data_devolucao = CURRENT_TIMESTAMP,
                data_devolucao_real = CURRENT_TIMESTAMP,
                observacao_devolucao = ?,
                status = 'CONCLUIDO'
            WHERE id = ?
            """,
            (observacao, emprestimo_id)
        )
        cursor.execute(
            "UPDATE ferramentas SET status = 'disponivel', situacao = ? WHERE id = ?",
            (situacao, ferramenta_id)
        )
        conn.commit()
        print(f"✓ Devolução registrada: emprestimo={emprestimo_id}, ferramenta={ferramenta_id}")
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"✗ Erro ao registrar devolução: {e}")
        raise
    finally:
        if conn:
            conn.close()

def buscar_metricas_dashboard():
    """
    Retorna métricas para o dashboard: total de ferramentas, disponíveis, emprestadas e atrasados.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Total de ferramentas
        cursor.execute("SELECT COUNT(*) FROM ferramentas")
        total_ferramentas = cursor.fetchone()[0]
        
        # Disponíveis
        cursor.execute("SELECT COUNT(*) FROM ferramentas WHERE UPPER(status) = 'DISPONIVEL'")
        disponiveis = cursor.fetchone()[0]
        
        # Emprestadas
        cursor.execute("SELECT COUNT(*) FROM ferramentas WHERE UPPER(status) = 'EMPRESTADA'")
        emprestadas = cursor.fetchone()[0]
        
        # Atrasados: empréstimos ativos com data_previsao passada
        cursor.execute(
            """
            SELECT
                e.id AS emprestimo_id,
                f.nome AS ferramenta_nome,
                f.patrimonio AS ferramenta_patrimonio,
                func.nome AS funcionario_nome,
                l.nome AS local_nome,
                e.data_previsao
            FROM emprestimos AS e
            JOIN ferramentas AS f ON e.ferramenta_id = f.id
            JOIN funcionarios AS func ON e.funcionario_id = func.id
            LEFT JOIN locais AS l ON e.local_id = l.id
            WHERE e.status = 'ATIVO' AND e.data_previsao < CURRENT_TIMESTAMP
            ORDER BY e.data_previsao
            """
        )
        atrasados = cursor.fetchall()
        
        return {
            'total_ferramentas': total_ferramentas,
            'disponiveis': disponiveis,
            'emprestadas': emprestadas,
            'atrasados': atrasados
        }
    except sqlite3.Error as e:
        print(f"✗ Erro ao buscar métricas do dashboard: {e}")
        raise
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    init_db()
