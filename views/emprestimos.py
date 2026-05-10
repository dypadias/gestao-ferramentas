import datetime

import streamlit as st
from database.db_manager import (
    buscar_funcionarios_ativos,
    buscar_ferramentas_disponiveis,
    buscar_locais_ativos,
    registrar_emprestimo,
)


def renderizar_emprestimos():
    """
    Renderiza a tela de empréstimos com seleção de funcionário e ferramenta.
    """
    st.header('Novo Empréstimo')

    funcionarios = buscar_funcionarios_ativos()
    ferramentas = buscar_ferramentas_disponiveis()
    locais = buscar_locais_ativos()

    if not funcionarios:
        st.warning('Nenhum funcionário ativo encontrado. Cadastre funcionários antes de registrar empréstimos.')

    if not ferramentas:
        st.warning('Nenhuma ferramenta disponível encontrada. Cadastre ferramentas ou libere ferramentas emprestadas.')

    if not locais:
        st.warning('Nenhum local ativo encontrado. Cadastre um local antes de registrar empréstimos.')

    with st.form('form_emprestimo'):
        if funcionarios:
            funcionario_options = [
                f"{funcionario['nome']} - {funcionario['cargo']}"
                for funcionario in funcionarios
            ]
            funcionario_selecionado = st.selectbox('Funcionário', funcionario_options)
        else:
            funcionario_selecionado = None

        if ferramentas:
            ferramenta_options = [
                f"{ferramenta['nome']} (Patrimônio: {ferramenta['patrimonio']})"
                for ferramenta in ferramentas
            ]
            ferramenta_selecionada = st.selectbox('Ferramenta', ferramenta_options)
        else:
            ferramenta_selecionada = None

        if locais:
            local_options = [
                f"{local['id']} - {local['nome']}" for local in locais
            ]
            local_selecionado = st.selectbox('Local de Uso', local_options)
        else:
            local_selecionado = None

        data_previsao = st.date_input('Data de Previsão', format='DD/MM/YYYY')
        hora_previsao = st.time_input('Hora de Previsão')

        submitted = st.form_submit_button('Registrar Empréstimo')

        if submitted:
            if not funcionarios:
                st.error('Não há funcionários ativos disponíveis para registrar o empréstimo.')
            elif not ferramentas:
                st.error('Não há ferramentas disponíveis para registrar o empréstimo.')
            elif not locais:
                st.error('Não há locais ativos disponíveis para registrar o empréstimo.')
            elif not local_selecionado:
                st.error('Informe o local de uso.')
            else:
                try:
                    funcionario_index = funcionario_options.index(funcionario_selecionado)
                    ferramenta_index = ferramenta_options.index(ferramenta_selecionada)
                    local_index = local_options.index(local_selecionado)
                    funcionario_id = funcionarios[funcionario_index]['id']
                    ferramenta_id = ferramentas[ferramenta_index]['id']
                    local_id = locais[local_index]['id']
                    gestor_id = 1
                    previsao_datetime = datetime.datetime.combine(data_previsao, hora_previsao)
                    registrar_emprestimo(
                        funcionario_id,
                        ferramenta_id,
                        gestor_id,
                        local_id,
                        previsao_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    )
                    st.success('Empréstimo registrado com sucesso!')
                except Exception as e:
                    st.error(f'Erro ao registrar empréstimo: {e}')
