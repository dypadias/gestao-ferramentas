import datetime
import os
import tkinter as tk
from tkinter import filedialog

import flet as ft


from database.db_manager import buscar_historico_completo, exportar_historico_csv


def renderizar_historico(page):
    """
    Renderiza a tela de historico de emprestimos finalizados.
    """
    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Ferramenta", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Patrimônio", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Funcionário", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Local de Uso", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Data Empréstimo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Data Devolução", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Observação", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=ft.Border(
            top=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
            right=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
            bottom=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
            left=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
        ),
        border_radius=8,
        heading_row_color=ft.Colors.BLUE_GREY_50,
        horizontal_lines=ft.BorderSide(1, ft.Colors.BLUE_GREY_50),
        column_spacing=24,
    )

    def formatar_data(valor):
        if not valor:
            return "-"

        valor_texto = str(valor)
        formatos = (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        )

        for formato in formatos:
            try:
                data = datetime.datetime.strptime(valor_texto, formato)
                return data.strftime("%d/%m/%Y às %H:%M")
            except ValueError:
                pass

        return valor_texto

    def criar_linha(registro):
        observacao = registro.get("observacao_devolucao") or registro.get("observacoes") or "-"

        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(registro.get("ferramenta_nome") or "-")),
                ft.DataCell(ft.Text(registro.get("ferramenta_patrimonio") or "-")),
                ft.DataCell(ft.Text(registro.get("funcionario_nome") or "-")),
                ft.DataCell(ft.Text(registro.get("local_nome") or "-")),
                ft.DataCell(ft.Text(formatar_data(registro.get("data_emprestimo")))),
                ft.DataCell(ft.Text(formatar_data(registro.get("data_devolucao")))),
                ft.DataCell(ft.Text(observacao)),
            ]
        )

    def carregar_dados(termo=""):
        registros = buscar_historico_completo(termo)
        tabela.rows.clear()

        if registros:
            tabela.rows.extend(criar_linha(registro) for registro in registros)
        else:
            tabela.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Nenhum registro encontrado.")),
                        ft.DataCell(ft.Text("-")),
                        ft.DataCell(ft.Text("-")),
                        ft.DataCell(ft.Text("-")),
                        ft.DataCell(ft.Text("-")),
                        ft.DataCell(ft.Text("-")),
                        ft.DataCell(ft.Text("-")),
                    ]
                )
            )

    def on_busca_change(e):
        carregar_dados(e.control.value)
        page.update()

    def mostrar_mensagem(texto, sucesso=True):
        snack_bar = ft.SnackBar(
            content=ft.Text(texto, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_700 if sucesso else ft.Colors.RED_700,
            show_close_icon=True,
            open=True,
        )
        page.overlay.append(snack_bar)

    def exportar_excel_click(e):
        termo = campo_busca.value or ""

        # Use tkinter to open a save file dialog
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        caminho_selecionado = filedialog.asksaveasfilename(
            title="Salvar histórico como",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="historico_emprestimos.csv",
        )

        if caminho_selecionado:
            exportar_historico_csv(termo, caminho_selecionado)
            snack_bar = ft.SnackBar(
                content=ft.Text(f"Histórico exportado com sucesso para {os.path.basename(caminho_selecionado)}!"),
                open=True,
            )
            page.overlay.append(snack_bar)
            page.update()

    campo_busca = ft.TextField(
        label="Pesquisar no histórico...",
        suffix_icon=ft.Icons.SEARCH,
        on_change=on_busca_change,
    )

    botao_exportar = ft.ElevatedButton(
        "Exportar Excel",
        icon=ft.Icons.FILE_DOWNLOAD,
        on_click=exportar_excel_click,
    )

    carregar_dados()

    return ft.Column(
        [
            ft.Text("Histórico", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900),
            ft.Row([campo_busca, botao_exportar], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([tabela], scroll=ft.ScrollMode.AUTO),
        ],
        spacing=20,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
