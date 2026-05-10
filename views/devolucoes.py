import datetime

import flet as ft
from database.db_manager import buscar_emprestimos_ativos, registrar_devolucao


def renderizar_devolucoes(page: ft.Page):
    """
    Renderiza a tela de devoluções usando Flet.
    """
    tabela_container = ft.Column(spacing=12)

    def borda_sutil():
        return ft.Border(
            top=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
            right=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
            bottom=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
            left=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
        )

    def mostrar_snack_bar(mensagem, sucesso=True):
        snack_bar = ft.SnackBar(
            content=ft.Text(mensagem, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_700 if sucesso else ft.Colors.RED_700,
            show_close_icon=True,
            open=True,
        )

        if hasattr(page, "snack_bar"):
            page.snack_bar = snack_bar
        else:
            page.overlay.append(snack_bar)

    def formatar_previsao(valor):
        if not valor:
            return "-"
        try:
            data_previsao = datetime.datetime.strptime(str(valor), "%Y-%m-%d %H:%M:%S")
            return data_previsao.strftime("%d/%m/%Y às %H:%M")
        except ValueError:
            return str(valor)

    def devolver_emprestimo(emprestimo_id, ferramenta_id):
        try:
            registrar_devolucao(emprestimo_id, ferramenta_id)
            mostrar_snack_bar("Devolução registrada com sucesso.")
            atualizar_tabela()
            page.update()
        except Exception as ex:
            mostrar_snack_bar(f"Erro ao registrar devolução: {str(ex)}", sucesso=False)
            page.update()

    def criar_linha(emprestimo):
        emprestimo_id = emprestimo["emprestimo_id"]
        ferramenta_id = emprestimo["ferramenta_id"]

        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(emprestimo["ferramenta_nome"])),
                ft.DataCell(ft.Text(emprestimo["ferramenta_patrimonio"])),
                ft.DataCell(ft.Text(emprestimo["funcionario_nome"])),
                ft.DataCell(ft.Text(emprestimo["local_nome"] or "-")),
                ft.DataCell(ft.Text(formatar_previsao(emprestimo["data_previsao"]))),
                ft.DataCell(
                    ft.ElevatedButton(
                        "Devolver",
                        icon=ft.Icons.CHECK,
                        bgcolor=ft.Colors.GREEN_700,
                        color=ft.Colors.WHITE,
                        on_click=lambda e, emp_id=emprestimo_id, ferr_id=ferramenta_id: devolver_emprestimo(emp_id, ferr_id),
                    )
                ),
            ]
        )

    def atualizar_tabela():
        emprestimos = buscar_emprestimos_ativos()
        tabela_container.controls.clear()

        if not emprestimos:
            tabela_container.controls.append(
                ft.Text(
                    "Nenhuma ferramenta pendente de devolução.",
                    size=16,
                    color=ft.Colors.GREY_700,
                )
            )
            return

        tabela_container.controls.append(
            ft.Row(
                [
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Ferramenta", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Patrimônio", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Funcionário", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Setor/Local", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Previsão", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Ação", weight=ft.FontWeight.BOLD)),
                        ],
                        rows=[criar_linha(emprestimo) for emprestimo in emprestimos],
                        border=borda_sutil(),
                        border_radius=8,
                        heading_row_color=ft.Colors.BLUE_GREY_50,
                        horizontal_lines=ft.BorderSide(1, ft.Colors.BLUE_GREY_50),
                        column_spacing=24,
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
            )
        )

    atualizar_tabela()

    painel_devolucoes = ft.Card(
        elevation=1,
        content=ft.Container(
            content=tabela_container,
            bgcolor=ft.Colors.WHITE,
            border=borda_sutil(),
            border_radius=8,
            padding=16,
        ),
        expand=True,
    )

    return ft.Column(
        [
            ft.Text("Devoluções", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900),
            ft.Divider(color=ft.Colors.BLUE_GREY_100),
            painel_devolucoes,
        ],
        spacing=20,
        expand=True,
    )
