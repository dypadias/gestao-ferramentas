import streamlit as st
from database.db_manager import cadastrar_funcionario, cadastrar_ferramenta, cadastrar_local


def renderizar_cadastros():
    """
    Renderiza a tela de cadastros com abas para funcionários, ferramentas e locais.
    """
    st.header('Cadastros')
    
    # Cria as abas
    tab1, tab2, tab3 = st.tabs(['Funcionários', 'Ferramentas', 'Locais'])
    
    # Aba Funcionários
    with tab1:
        st.subheader('Cadastrar Funcionário')
        
        with st.form('form_funcionario'):
            nome = st.text_input('Nome do Funcionário')
            cargo = st.text_input('Cargo')
            submitted = st.form_submit_button('Cadastrar Funcionário')
            
            if submitted:
                if nome and cargo:
                    try:
                        cadastrar_funcionario(nome, cargo)
                        st.success(f'Funcionário "{nome}" cadastrado com sucesso!')
                    except Exception as e:
                        st.error(f'Erro ao cadastrar funcionário: {e}')
                else:
                    st.error('Por favor, preencha todos os campos.')
    
    # Aba Ferramentas
    with tab2:
        st.subheader('Cadastrar Ferramenta')
        
        with st.form('form_ferramenta'):
            nome = st.text_input('Nome da Ferramenta')
            patrimonio = st.text_input('Número do Patrimônio')
            submitted = st.form_submit_button('Cadastrar Ferramenta')
            
            if submitted:
                if nome and patrimonio:
                    try:
                        cadastrar_ferramenta(nome, patrimonio)
                        st.success(f'Ferramenta "{nome}" cadastrada com sucesso!')
                    except Exception as e:
                        st.error(f'Erro ao cadastrar ferramenta: {e}')
                else:
                    st.error('Por favor, preencha todos os campos.')

    # Aba Locais
    with tab3:
        st.subheader('Cadastrar Local/Setor')
        
        with st.form('form_local'):
            nome = st.text_input('Nome do Local/Setor')
            submitted = st.form_submit_button('Cadastrar Local')
            
            if submitted:
                if nome:
                    try:
                        cadastrar_local(nome)
                        st.success(f'Local "{nome}" cadastrado com sucesso!')
                    except Exception as e:
                        st.error(f'Erro ao cadastrar local: {e}')
                else:
                    st.error('Por favor, preencha o nome do local.')
