import flet as ft
import datetime
from database.db_manager import buscar_emprestimos_ativos, buscar_metricas_dashboard


def renderizar_dashboard(page):
    """
    Renderiza o dashboard com métricas gerenciais usando Flet.
    """
    # Buscar métricas
    metricas = buscar_metricas_dashboard()

    def borda_sutil():
        return ft.Border(
            top=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
            right=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
            bottom=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
            left=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
        )

    def titulo_com_icone(icon, texto, cor_icone, tamanho_texto=20, tamanho_icone=24):
        return ft.Row(
            [
                ft.Icon(icon, size=tamanho_icone, color=cor_icone),
                ft.Text(texto, size=tamanho_texto, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )

    def formatar_data_previsao(valor):
        try:
            data_previsao_obj = datetime.datetime.strptime(valor, '%Y-%m-%d %H:%M:%S')
            return data_previsao_obj.strftime('%d/%m/%Y às %H:%M')
        except (TypeError, ValueError):
            return str(valor or '-')

    def criar_tabela_emprestimos(emprestimos):
        columns = [
            ft.DataColumn(ft.Text("Ferramenta")),
            ft.DataColumn(ft.Text("Patrimônio")),
            ft.DataColumn(ft.Text("Funcionário")),
            ft.DataColumn(ft.Text("Setor/Local")),
            ft.DataColumn(ft.Text("Data Prevista")),
        ]

        rows = []
        for emprestimo in emprestimos:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(emprestimo['ferramenta_nome'])),
                        ft.DataCell(ft.Text(emprestimo['ferramenta_patrimonio'])),
                        ft.DataCell(ft.Text(emprestimo['funcionario_nome'])),
                        ft.DataCell(ft.Text(emprestimo['local_nome'] or 'N/A')),
                        ft.DataCell(ft.Text(formatar_data_previsao(emprestimo['data_previsao']))),
                    ]
                )
            )

        return ft.Card(
            elevation=1,
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.DataTable(
                            columns=columns,
                            rows=rows,
                            border=borda_sutil(),
                            border_radius=8,
                            heading_row_color=ft.Colors.BLUE_GREY_50,
                            horizontal_lines=ft.BorderSide(1, ft.Colors.BLUE_GREY_50),
                            column_spacing=24,
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
                bgcolor=ft.Colors.WHITE,
                border=borda_sutil(),
                border_radius=8,
                padding=10,
            ),
        )

    # Cards de métricas
    cards = ft.Row([
        ft.Card(
            elevation=1,
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Total de Ferramentas", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_700),
                    ft.Text(str(metricas['total_ferramentas']), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border=borda_sutil(),
                border_radius=8,
            ),
            width=300,
            height=100,
        ),
        ft.Card(
            elevation=1,
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Ferramentas Disponíveis", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_700),
                    ft.Text(str(metricas['disponiveis']), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border=borda_sutil(),
                border_radius=8,
            ),
            width=300,
            height=100,
        ),
        ft.Card(
            elevation=1,
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Ferramentas Emprestadas", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_700),
                    ft.Text(str(metricas['emprestadas']), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_800),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border=borda_sutil(),
                border_radius=8,
            ),
            width=300,
            height=100,
        ),
    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)

    # Seção de empréstimos atrasados
    atrasados = metricas['atrasados']
    todos_ativos = buscar_emprestimos_ativos()
    atrasados_ids = {atrasado['emprestimo_id'] for atrasado in atrasados}
    no_prazo = [
        emprestimo
        for emprestimo in todos_ativos
        if emprestimo['emprestimo_id'] not in atrasados_ids
    ]

    if not atrasados:
        tabela_atrasados = ft.Row(
            [
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.GREEN),
                ft.Text("Nenhum empréstimo atrasado.", size=16, color=ft.Colors.GREEN),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )
    else:
        tabela_atrasados = criar_tabela_emprestimos(atrasados)

    if not no_prazo:
        tabela_no_prazo = ft.Text("Nenhuma ferramenta em uso no prazo.", size=16, color=ft.Colors.GREY_700)
    else:
        tabela_no_prazo = criar_tabela_emprestimos(no_prazo)

    secoes_tabelas = ft.Card(
        elevation=1,
        content=ft.Container(
            content=ft.Column(
                [
                    titulo_com_icone(ft.Icons.WARNING_AMBER, "Empréstimos Atrasados", ft.Colors.RED),
                    tabela_atrasados,
                    ft.Divider(color=ft.Colors.BLUE_GREY_100),
                    titulo_com_icone(ft.Icons.VERIFIED, "Em Uso (No Prazo)", ft.Colors.GREEN),
                    tabela_no_prazo,
                ],
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            bgcolor=ft.Colors.WHITE,
            border=borda_sutil(),
            border_radius=8,
            padding=16,
        ),
        expand=True,
    )

    # Layout principal
    return ft.Column([
        titulo_com_icone(
            ft.Icons.ANALYTICS,
            "Dashboard de Gestão de Ferramentas",
            ft.Colors.BLUE_GREY_700,
            tamanho_texto=24,
            tamanho_icone=30,
        ),
        ft.Divider(color=ft.Colors.BLUE_GREY_100),
        cards,
        ft.Divider(color=ft.Colors.BLUE_GREY_100),
        secoes_tabelas,
    ], spacing=20, expand=True)
