-- Tabela de gestores
CREATE TABLE IF NOT EXISTS gestores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    login TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    ativo BOOLEAN DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de funcionarios
CREATE TABLE IF NOT EXISTS funcionarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cargo TEXT NOT NULL,
    ativo BOOLEAN DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de ferramentas
CREATE TABLE IF NOT EXISTS ferramentas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    patrimonio TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'DISPONIVEL',
    situacao TEXT DEFAULT 'OK',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de locais
CREATE TABLE IF NOT EXISTS locais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    ativo BOOLEAN DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de emprestimos
CREATE TABLE IF NOT EXISTS emprestimos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    funcionario_id INTEGER NOT NULL,
    ferramenta_id INTEGER NOT NULL,
    gestor_id INTEGER NOT NULL,
    local_id INTEGER,
    data_emprestimo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_devolucao TIMESTAMP,
    data_devolucao_real TIMESTAMP,
    data_previsao TIMESTAMP,
    status TEXT DEFAULT 'ATIVO',
    observacoes TEXT,
    observacao_devolucao TEXT,
    FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id) ON DELETE RESTRICT,
    FOREIGN KEY (ferramenta_id) REFERENCES ferramentas(id) ON DELETE RESTRICT,
    FOREIGN KEY (gestor_id) REFERENCES gestores(id) ON DELETE RESTRICT,
    FOREIGN KEY (local_id) REFERENCES locais(id) ON DELETE SET NULL
);

-- Indices para melhor performance
CREATE INDEX IF NOT EXISTS idx_emprestimos_funcionario ON emprestimos(funcionario_id);
CREATE INDEX IF NOT EXISTS idx_emprestimos_ferramenta ON emprestimos(ferramenta_id);
CREATE INDEX IF NOT EXISTS idx_emprestimos_gestor ON emprestimos(gestor_id);
CREATE INDEX IF NOT EXISTS idx_emprestimos_data ON emprestimos(data_emprestimo);
