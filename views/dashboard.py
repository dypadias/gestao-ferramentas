import streamlit as st
import datetime
import pandas as pd
from database.db_manager import buscar_metricas_dashboard


def renderizar_dashboard():
    """
    Renderiza o dashboard com métricas gerenciais.
    """
    st.header('📊 Dashboard de Gestão de Ferramentas')

    # Buscar métricas
    metricas = buscar_metricas_dashboard()

    # Cards de métricas no topo
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Total de Ferramentas",
            value=metricas['total_ferramentas']
        )

    with col2:
        st.metric(
            label="Ferramentas Disponíveis",
            value=metricas['disponiveis']
        )

    with col3:
        st.metric(
            label="Ferramentas Emprestadas",
            value=metricas['emprestadas']
        )

    # Seção de empréstimos atrasados
    st.markdown('---')
    st.subheader('🚨 Empréstimos Atrasados')

    atrasados = metricas['atrasados']
    if not atrasados:
        st.success('Nenhum empréstimo atrasado! 🎉')
    else:
        st.warning(f'Encontrados {len(atrasados)} empréstimos atrasados.')
        
        # Preparar dados para o DataFrame
        dados_tabela = []
        for atrasado in atrasados:
            # Formatar a data de previsão
            data_previsao_obj = datetime.datetime.strptime(atrasado['data_previsao'], '%Y-%m-%d %H:%M:%S')
            data_previsao_formatada = data_previsao_obj.strftime('%d/%m/%Y às %H:%M')
            
            dados_tabela.append({
                'Ferramenta': atrasado['ferramenta_nome'],
                'Patrimônio': atrasado['ferramenta_patrimonio'],
                'Funcionário': atrasado['funcionario_nome'],
                'Setor/Local': atrasado['local_nome'] or 'N/A',
                'Data Prevista': data_previsao_formatada
            })
        
        # Criar DataFrame e exibir
        df_atrasados = pd.DataFrame(dados_tabela)
        st.dataframe(df_atrasados, use_container_width=True)