import sqlite3
import os

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
        _ensure_column(cursor, 'ferramentas', 'status', "TEXT DEFAULT 'DISPONIVEL'")
        _ensure_column(cursor, 'emprestimos', 'data_devolucao_real', 'TIMESTAMP')
        _ensure_column(cursor, 'emprestimos', 'status', "TEXT DEFAULT 'ATIVO'")
        _ensure_column(cursor, 'emprestimos', 'local_id', 'INTEGER')
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
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")


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
        cursor.execute("SELECT id, nome, patrimonio FROM ferramentas WHERE UPPER(status) = 'DISPONIVEL' ORDER BY nome")
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


def registrar_devolucao(emprestimo_id, ferramenta_id):
    """
    Registra a devolução do empréstimo e atualiza o status da ferramenta.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE emprestimos SET data_devolucao_real = CURRENT_TIMESTAMP, status = 'CONCLUIDO' WHERE id = ?",
            (emprestimo_id,)
        )
        cursor.execute(
            "UPDATE ferramentas SET status = 'DISPONIVEL' WHERE id = ?",
            (ferramenta_id,)
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
