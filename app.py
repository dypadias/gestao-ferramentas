import streamlit as st
from database.db_manager import init_db

# 1. Configuração da página deve ser a primeira coisa
st.set_page_config(page_title="Gestão de Ferramentas", page_icon="🔧", layout="wide")

# Logo da empresa no sidebar
st.sidebar.image("assets/logo.png", use_container_width=True)

# 2. Inicializa o banco de dados
init_db()

# 3. Importa as telas
from views.emprestimos import renderizar_emprestimos
from views.devolucoes import renderizar_devolucoes
from views.cadastros import renderizar_cadastros
from views.dashboard import renderizar_dashboard

# Função temporária para o Dashboard enquanto não o construímos
# def renderizar_dashboard():
#     st.header('🚨 Dashboard de Alertas')
#     st.write('Visão geral das ferramentas da oficina aparecerá aqui.')

# 4. Criação das Páginas Modernas (st.Page) com ícones
page_dashboard = st.Page(renderizar_dashboard, title="Dashboard", icon="📊")
page_emprestimos = st.Page(renderizar_emprestimos, title="Novo Empréstimo", icon="📤")
page_devolucoes = st.Page(renderizar_devolucoes, title="Devoluções", icon="📥")
page_cadastros = st.Page(renderizar_cadastros, title="Cadastros", icon="📋")

# 5. Orquestra a navegação nativa do Streamlit
pg = st.navigation({
    "Gestão Diária": [page_dashboard, page_emprestimos, page_devolucoes],
    "Administração": [page_cadastros]
})

# 6. Executa a página selecionada
pg.run()