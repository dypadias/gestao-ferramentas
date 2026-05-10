import datetime

import streamlit as st
from database.db_manager import buscar_emprestimos_ativos, registrar_devolucao


def renderizar_devolucoes():
    """
    Renderiza a tela de devoluções e permite registrar a devolução de empréstimos ativos.
    """
    st.header('Devoluções')

    emprestimos = buscar_emprestimos_ativos()

    if not emprestimos:
        st.info('Nenhum empréstimo ativo encontrado.')
        return

    st.markdown('### Empréstimos ativos')

    # Cabeçalho da tabela manual
    col_id, col_ferramenta, col_funcionario, col_setor, col_previsao, col_acao = st.columns([1, 2, 2, 2, 2, 1])
    with col_id:
        st.write("**ID**")
    with col_ferramenta:
        st.write("**Ferramenta**")
    with col_funcionario:
        st.write("**Funcionário**")
    with col_setor:
        st.write("**Setor/Local**")
    with col_previsao:
        st.write("**Previsão**")
    with col_acao:
        st.write("**Ação**")

    st.markdown('---')

    for emprestimo in emprestimos:
        # Formatar a data de previsão para o formato brasileiro
        data_previsao_obj = datetime.datetime.strptime(emprestimo['data_previsao'], '%Y-%m-%d %H:%M:%S')
        data_previsao_formatada = data_previsao_obj.strftime('%d/%m/%Y às %H:%M')
        
        # Linha da tabela
        col_id, col_ferramenta, col_funcionario, col_setor, col_previsao, col_acao = st.columns([1, 2, 2, 2, 2, 1])
        with col_id:
            st.write(emprestimo['emprestimo_id'])
        with col_ferramenta:
            st.write(f"{emprestimo['ferramenta_nome']} ({emprestimo['ferramenta_patrimonio']})")
        with col_funcionario:
            st.write(emprestimo['funcionario_nome'])
        with col_setor:
            st.write(emprestimo['local_nome'] or 'N/A')
        with col_previsao:
            st.write(data_previsao_formatada)
        with col_acao:
            button_key = f"dev_{emprestimo['emprestimo_id']}"
            if st.button('Devolver', key=button_key):
                try:
                    registrar_devolucao(emprestimo['emprestimo_id'], emprestimo['ferramenta_id'])
                    st.success('Devolução registrada com sucesso!')
                    st.rerun()
                except Exception as e:
                    st.error(f'Erro ao registrar devolução: {e}')
