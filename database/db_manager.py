import sqlite3
import os
import csv
import sys
import shutil

# ==============================================================================
# CONFIGURAÇÃO INTELIGENTE DO CAMINHO DO BANCO DE DADOS
# ==============================================================================

def get_database_path():
    """
    Determina o caminho correto do banco de dados, funcionando em qualquer ambiente.
    Prioridades:
    1. Se existe um banco na pasta do executável (ou do script), usa ele.
    2. Se não, procura em locais comuns onde o banco original possa estar.
    3. Se encontrar, copia para a pasta do executável e usa.
    4. Se nada encontrar, cria um novo banco na pasta do executável.
    """
    # 1. Define o diretório base (onde o executável ou script está)
    if getattr(sys, 'frozen', False):
        # Modo executável (gerado por flet pack ou pyinstaller)
        base_dir = os.path.dirname(sys.executable)
    else:
        # Modo desenvolvimento (script Python puro)
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # Caminho principal: banco ao lado do executável/script
    main_db_path = os.path.join(base_dir, 'gestao.db')
    
    # Se já existe nesse local, use-o imediatamente
    if os.path.exists(main_db_path):
        print(f"[INFO] Banco de dados encontrado: {main_db_path}")
        return main_db_path

    # 2. Procura em locais comuns onde o banco pode estar (especialmente o original)
    possible_locations = [
        os.path.join(os.getcwd(), 'gestao.db'),                     # Diretório atual de execução
        os.path.join(os.getcwd(), 'database', 'gestao.db'),
        r'C:\Projetos\gestao_ferramentas\gestao.db',                # Caminho original do projeto
        r'C:\Projetos\gestao_ferramentas\database\gestao.db',
        os.path.expanduser('~/Desktop/gestao.db'),
        os.path.join(base_dir, 'data', 'gestao.db'),                # Possível estrutura
    ]

    for loc in possible_locations:
        if os.path.exists(loc):
            print(f"[INFO] Banco encontrado em: {loc}")
            try:
                # Copia para a pasta do executável para uso futuro
                shutil.copy2(loc, main_db_path)
                print(f"[INFO] Banco copiado com sucesso para: {main_db_path}")
                return main_db_path
            except Exception as e:
                print(f"[AVISO] Não foi possível copiar banco de {loc}: {e}")
                # Se não conseguir copiar, usa o local original mesmo (mas pode dar problema)
                return loc

    # 3. Nenhum banco existente encontrado: cria um novo
    print(f"[INFO] Nenhum banco existente encontrado. Criando novo em: {main_db_path}")
    return main_db_path

# Define o caminho global do banco de dados
DB_PATH = get_database_path()
print(f"[DEBUG] DB_PATH definido como: {DB_PATH}")

# ==============================================================================
# CLASSES E FUNÇÕES AUXILIARES
# ==============================================================================

class DictRow(dict):
    def __init__(self, cursor, row):
        super().__init__()
        self._row = row
        for idx, col in enumerate(cursor.description):
            self[col[0]] = row[idx]
            
    def __getitem__(self, key):
        if isinstance(key, int):
            return self._row[key]
        return super().__getitem__(key)

def dict_factory(cursor, row):
    return DictRow(cursor, row)

def get_connection():
    """
    Retorna uma conexão com o banco de dados SQLite.
    Cria o diretório se necessário e configura row_factory.
    """
    try:
        # Garante que o diretório do arquivo existe
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = dict_factory
        return conn
    except sqlite3.Error as e:
        print(f"[ERRO] Falha ao conectar ao banco em {DB_PATH}: {e}")
        raise

def _ensure_column(cursor, table_name, column_name, column_definition):
    """Adiciona uma coluna à tabela se ela não existir."""
    try:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' not in str(e).lower():
            raise

def _create_minimal_schema(cursor):
    """Cria a estrutura mínima do banco de dados caso o schema.sql não exista."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ferramentas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            patrimonio TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'disponivel',
            situacao TEXT DEFAULT 'OK'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cargo TEXT,
            ativo INTEGER DEFAULT 1
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            ativo INTEGER DEFAULT 1
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emprestimos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ferramenta_id INTEGER,
            funcionario_id INTEGER,
            local_id INTEGER,
            gestor_id INTEGER,
            data_emprestimo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_devolucao TIMESTAMP,
            data_previsao TIMESTAMP,
            data_devolucao_real TIMESTAMP,
            observacoes TEXT,
            observacao_devolucao TEXT,
            status TEXT DEFAULT 'ATIVO',
            FOREIGN KEY(ferramenta_id) REFERENCES ferramentas(id),
            FOREIGN KEY(funcionario_id) REFERENCES funcionarios(id),
            FOREIGN KEY(local_id) REFERENCES locais(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS manutencoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ferramenta_id INTEGER,
            data_envio DATETIME,
            data_retorno DATETIME,
            motivo TEXT,
            observacao TEXT,
            FOREIGN KEY(ferramenta_id) REFERENCES ferramentas(id)
        )
    ''')

def init_db():
    """
    Inicializa o banco de dados: cria tabelas e garante colunas necessárias.
    Se existir o arquivo schema.sql, o executa; caso contrário, cria estrutura mínima.
    """
    conn = None
    # Determina o caminho do schema.sql (pode estar ao lado do executável ou no pacote)
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        schema_path = os.path.join(base_dir, 'schema.sql')
        # Se não encontrar, tenta dentro do diretório 'database' (comum em empacotamentos)
        if not os.path.exists(schema_path):
            schema_path = os.path.join(base_dir, 'database', 'schema.sql')
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(base_dir, 'schema.sql')

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()
            cursor.executescript(schema)
            print(f"[INFO] Schema aplicado a partir de: {schema_path}")
        else:
            print(f"[AVISO] schema.sql não encontrado em {schema_path}. Criando estrutura mínima.")
            _create_minimal_schema(cursor)

        # Garante colunas novas em bases antigas
        _ensure_column(cursor, 'funcionarios', 'ativo', 'INTEGER DEFAULT 1')
        _ensure_column(cursor, 'locais', 'ativo', 'INTEGER DEFAULT 1')
        _ensure_column(cursor, 'ferramentas', 'status', "TEXT DEFAULT 'DISPONIVEL'")
        _ensure_column(cursor, 'ferramentas', 'situacao', "TEXT DEFAULT 'OK'")
        _ensure_column(cursor, 'emprestimos', 'data_devolucao_real', 'TIMESTAMP')
        _ensure_column(cursor, 'emprestimos', 'status', "TEXT DEFAULT 'ATIVO'")
        _ensure_column(cursor, 'emprestimos', 'local_id', 'INTEGER')
        _ensure_column(cursor, 'emprestimos', 'observacao_devolucao', 'TEXT')
        
        # Tabela de manutenções (caso não tenha sido criada)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS manutencoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ferramenta_id INTEGER,
                data_envio DATETIME,
                data_retorno DATETIME,
                motivo TEXT,
                observacao TEXT,
                FOREIGN KEY(ferramenta_id) REFERENCES ferramentas(id)
            )
        ''')

        conn.commit()
        print(f"[OK] Banco de dados inicializado/verificado em: {DB_PATH}")
    except Exception as e:
        print(f"[ERRO] Falha ao inicializar banco: {e}")
        raise
    finally:
        if conn:
            conn.close()

# ==============================================================================
# FUNCIONÁRIOS
# ==============================================================================

def cadastrar_funcionario(nome, cargo):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO funcionarios (nome, cargo) VALUES (?, ?)", (nome, cargo))
        conn.commit()
        print(f"[OK] Funcionário '{nome}' cadastrado.")
    except sqlite3.Error as e:
        print(f"[ERRO] cadastrar_funcionario: {e}")
        raise
    finally:
        if conn: conn.close()

def buscar_todos_funcionarios():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, cargo, ativo FROM funcionarios ORDER BY nome")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"[ERRO] buscar_todos_funcionarios: {e}")
        raise
    finally:
        if conn: conn.close()

def atualizar_funcionario(funcionario_id, nome, cargo, ativo):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE funcionarios SET nome=?, cargo=?, ativo=? WHERE id=?", (nome, cargo, ativo, funcionario_id))
        conn.commit()
        print(f"[OK] Funcionário {funcionario_id} atualizado.")
    except sqlite3.Error as e:
        print(f"[ERRO] atualizar_funcionario: {e}")
        raise
    finally:
        if conn: conn.close()

def buscar_funcionarios_ativos():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, cargo FROM funcionarios WHERE ativo=1 ORDER BY nome")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"[ERRO] buscar_funcionarios_ativos: {e}")
        raise
    finally:
        if conn: conn.close()

# ==============================================================================
# FERRAMENTAS
# ==============================================================================

def cadastrar_ferramenta(nome, patrimonio):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ferramentas (nome, patrimonio) VALUES (?, ?)", (nome, patrimonio))
        conn.commit()
        print(f"[OK] Ferramenta '{nome}' cadastrada.")
    except sqlite3.Error as e:
        print(f"[ERRO] cadastrar_ferramenta: {e}")
        raise
    finally:
        if conn: conn.close()

def buscar_todas_ferramentas():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, patrimonio, status, situacao FROM ferramentas ORDER BY nome")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"[ERRO] buscar_todas_ferramentas: {e}")
        raise
    finally:
        if conn: conn.close()

def atualizar_ferramenta(ferramenta_id, nome, patrimonio, situacao):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE ferramentas SET nome=?, patrimonio=?, situacao=? WHERE id=?", (nome, patrimonio, situacao, ferramenta_id))
        conn.commit()
        print(f"[OK] Ferramenta {ferramenta_id} atualizada.")
    except sqlite3.Error as e:
        print(f"[ERRO] atualizar_ferramenta: {e}")
        raise
    finally:
        if conn: conn.close()

def buscar_ferramentas_disponiveis():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, patrimonio
            FROM ferramentas
            WHERE LOWER(status)='disponivel' AND UPPER(COALESCE(situacao,'OK'))='OK'
            ORDER BY nome
        """)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"[ERRO] buscar_ferramentas_disponiveis: {e}")
        raise
    finally:
        if conn: conn.close()

# ==============================================================================
# LOCAIS
# ==============================================================================

def cadastrar_local(nome):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO locais (nome) VALUES (?)", (nome,))
        conn.commit()
        print(f"[OK] Local '{nome}' cadastrado.")
    except sqlite3.Error as e:
        print(f"[ERRO] cadastrar_local: {e}")
        raise
    finally:
        if conn: conn.close()

def buscar_todos_locais():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, ativo FROM locais ORDER BY nome")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"[ERRO] buscar_todos_locais: {e}")
        raise
    finally:
        if conn: conn.close()

def atualizar_local(local_id, nome, ativo):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE locais SET nome=?, ativo=? WHERE id=?", (nome, ativo, local_id))
        conn.commit()
        print(f"[OK] Local {local_id} atualizado.")
    except sqlite3.Error as e:
        print(f"[ERRO] atualizar_local: {e}")
        raise
    finally:
        if conn: conn.close()

def buscar_locais_ativos():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM locais WHERE ativo=1 ORDER BY nome")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"[ERRO] buscar_locais_ativos: {e}")
        raise
    finally:
        if conn: conn.close()

# ==============================================================================
# EMPRÉSTIMOS E DEVOLUÇÕES
# ==============================================================================

def registrar_emprestimo(funcionario_id, ferramenta_id, gestor_id, local_id, data_previsao):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO emprestimos (funcionario_id, ferramenta_id, gestor_id, local_id, data_previsao) VALUES (?,?,?,?,?)",
            (funcionario_id, ferramenta_id, gestor_id, local_id, data_previsao)
        )
        cursor.execute("UPDATE ferramentas SET status='EMPRESTADA' WHERE id=?", (ferramenta_id,))
        conn.commit()
        print(f"[OK] Empréstimo registrado (func={funcionario_id}, ferram={ferramenta_id})")
    except sqlite3.Error as e:
        if conn: conn.rollback()
        print(f"[ERRO] registrar_emprestimo: {e}")
        raise
    finally:
        if conn: conn.close()

def buscar_emprestimos_ativos():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id AS emprestimo_id, e.ferramenta_id,
                   f.nome AS ferramenta_nome, f.patrimonio AS ferramenta_patrimonio,
                   func.nome AS funcionario_nome, l.nome AS local_nome,
                   e.data_previsao
            FROM emprestimos e
            JOIN ferramentas f ON e.ferramenta_id = f.id
            JOIN funcionarios func ON e.funcionario_id = func.id
            LEFT JOIN locais l ON e.local_id = l.id
            WHERE e.status = 'ATIVO'
            ORDER BY e.data_previsao
        """)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"[ERRO] buscar_emprestimos_ativos: {e}")
        raise
    finally:
        if conn: conn.close()

def registrar_devolucao(emprestimo_id, ferramenta_id, situacao='OK', observacao=''):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE emprestimos
            SET data_devolucao = DATETIME('now', 'localtime'),
                data_devolucao_real = DATETIME('now', 'localtime'),
                observacao_devolucao = ?,
                status = 'CONCLUIDO'
            WHERE id = ?
        """, (observacao, emprestimo_id))
        cursor.execute("UPDATE ferramentas SET status='disponivel', situacao=? WHERE id=?", (situacao, ferramenta_id))
        conn.commit()
        print(f"[OK] Devolução registrada (emp={emprestimo_id}, ferram={ferramenta_id})")
    except sqlite3.Error as e:
        if conn: conn.rollback()
        print(f"[ERRO] registrar_devolucao: {e}")
        raise
    finally:
        if conn: conn.close()

def buscar_historico_completo(termo_busca=""):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT e.id AS emprestimo_id, e.funcionario_id, e.ferramenta_id, e.gestor_id, e.local_id,
                   f.nome AS ferramenta_nome, f.patrimonio AS ferramenta_patrimonio,
                   func.nome AS funcionario_nome, l.nome AS local_nome,
                   e.data_emprestimo, e.data_devolucao, e.data_previsao,
                   e.status, e.observacoes, e.observacao_devolucao
            FROM emprestimos e
            JOIN funcionarios func ON e.funcionario_id = func.id
            JOIN ferramentas f ON e.ferramenta_id = f.id
            LEFT JOIN locais l ON e.local_id = l.id
            WHERE e.data_devolucao IS NOT NULL
        """
        params = []
        if termo_busca:
            query += " AND (f.nome LIKE ? OR f.patrimonio LIKE ? OR func.nome LIKE ? OR l.nome LIKE ?)"
            termo_like = f"%{termo_busca}%"
            params = [termo_like, termo_like, termo_like, termo_like]
        query += " ORDER BY e.data_devolucao DESC, e.data_emprestimo DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"[ERRO] buscar_historico_completo: {e}")
        raise
    finally:
        if conn: conn.close()

# ==============================================================================
# MANUTENÇÕES
# ==============================================================================

def enviar_para_manutencao(ferramenta_id, motivo):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO manutencoes (ferramenta_id, data_envio, motivo) VALUES (?, DATETIME('now', 'localtime'), ?)",
                       (ferramenta_id, motivo))
        cursor.execute("UPDATE ferramentas SET status='manutencao', situacao='Em Manutenção' WHERE id=?", (ferramenta_id,))
        conn.commit()
        print(f"[OK] Ferramenta {ferramenta_id} enviada para manutenção.")
    except sqlite3.Error as e:
        if conn: conn.rollback()
        print(f"[ERRO] enviar_para_manutencao: {e}")
        raise
    finally:
        if conn: conn.close()

def registrar_retorno_manutencao(manutencao_id, ferramenta_id, observacao):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE manutencoes SET data_retorno = DATETIME('now', 'localtime'), observacao = ? WHERE id = ?",
                       (observacao, manutencao_id))
        cursor.execute("UPDATE ferramentas SET status='disponivel', situacao='OK' WHERE id=?", (ferramenta_id,))
        conn.commit()
        print(f"[OK] Retorno de manutenção registrado (ferram {ferramenta_id})")
    except sqlite3.Error as e:
        if conn: conn.rollback()
        print(f"[ERRO] registrar_retorno_manutencao: {e}")
        raise
    finally:
        if conn: conn.close()

def buscar_manutencoes_ativas():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.id, m.ferramenta_id, m.data_envio, m.motivo, f.nome, f.patrimonio
            FROM manutencoes m
            JOIN ferramentas f ON m.ferramenta_id = f.id
            WHERE m.data_retorno IS NULL
            ORDER BY m.data_envio DESC
        """)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"[ERRO] buscar_manutencoes_ativas: {e}")
        raise
    finally:
        if conn: conn.close()

def buscar_historico_manutencoes():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.id, m.ferramenta_id, m.data_envio, m.data_retorno, m.motivo, m.observacao, f.nome, f.patrimonio
            FROM manutencoes m
            JOIN ferramentas f ON m.ferramenta_id = f.id
            WHERE m.data_retorno IS NOT NULL
            ORDER BY m.data_retorno DESC
        """)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"[ERRO] buscar_historico_manutencoes: {e}")
        raise
    finally:
        if conn: conn.close()

def buscar_historico_manutencoes_filtrado(termo_busca=""):
    """
    Retorna o histórico de manutenções (finalizadas) com filtro por nome da ferramenta, patrimônio ou motivo.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT m.id, m.ferramenta_id, m.data_envio, m.data_retorno, m.motivo, m.observacao,
                   f.nome, f.patrimonio
            FROM manutencoes m
            JOIN ferramentas f ON m.ferramenta_id = f.id
            WHERE m.data_retorno IS NOT NULL
        """
        params = []
        if termo_busca:
            query += " AND (f.nome LIKE ? OR f.patrimonio LIKE ? OR m.motivo LIKE ?)"
            termo_like = f"%{termo_busca}%"
            params = [termo_like, termo_like, termo_like]
        query += " ORDER BY m.data_retorno DESC"
        cursor.execute(query, params)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"[Erro] buscar_historico_manutencoes_filtrado: {e}")
        raise
    finally:
        if conn:
            conn.close()

# ==============================================================================
# DASHBOARD / MÉTRICAS
# ==============================================================================

def buscar_metricas_dashboard():
    """
    Retorna métricas principais para o dashboard.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM ferramentas")
        total_ferramentas = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) AS disp FROM ferramentas WHERE UPPER(status)='DISPONIVEL'")
        disponiveis = cursor.fetchone()['disp']
        cursor.execute("SELECT COUNT(*) AS emp FROM ferramentas WHERE UPPER(status)='EMPRESTADA'")
        emprestadas = cursor.fetchone()['emp']
        cursor.execute("SELECT COUNT(*) AS manut FROM ferramentas WHERE UPPER(status)='MANUTENCAO'")
        manutencao = cursor.fetchone()['manut']

        cursor.execute("""
            SELECT e.id AS emprestimo_id, f.nome AS ferramenta_nome, f.patrimonio AS ferramenta_patrimonio,
                   func.nome AS funcionario_nome, l.nome AS local_nome, e.data_previsao
            FROM emprestimos e
            JOIN ferramentas f ON e.ferramenta_id = f.id
            JOIN funcionarios func ON e.funcionario_id = func.id
            LEFT JOIN locais l ON e.local_id = l.id
            WHERE e.status = 'ATIVO' AND e.data_previsao < DATETIME('now', 'localtime')
            ORDER BY e.data_previsao
        """)
        atrasados = cursor.fetchall()

        return {
            'total_ferramentas': total_ferramentas,
            'disponiveis': disponiveis,
            'emprestadas': emprestadas,
            'manutencao': manutencao,
            'atrasados': atrasados
        }
    except sqlite3.Error as e:
        print(f"[ERRO] buscar_metricas_dashboard: {e}")
        return {'total_ferramentas': 0, 'disponiveis': 0, 'emprestadas': 0, 'manutencao': 0, 'atrasados': []}
    finally:
        if conn: conn.close()

# ==============================================================================
# EXPORTAÇÃO CSV
# ==============================================================================

def exportar_historico_csv(termo_busca="", caminho_arquivo=None):
    registros = buscar_historico_completo(termo_busca)
    if caminho_arquivo is None:
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(base_dir, 'historico_emprestimos.csv')
    
    with open(caminho_arquivo, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Ferramenta','Patrimônio','Funcionário','Local de Uso','Data Empréstimo','Data Devolução','Observação'])
        for r in registros:
            writer.writerow([
                r.get('ferramenta_nome',''), r.get('ferramenta_patrimonio',''),
                r.get('funcionario_nome',''), r.get('local_nome',''),
                r.get('data_emprestimo',''), r.get('data_devolucao',''),
                r.get('observacao_devolucao') or r.get('observacoes','')
            ])
    return caminho_arquivo

# ==============================================================================
# INICIALIZAÇÃO
# ==============================================================================

if __name__ == '__main__':
    init_db()