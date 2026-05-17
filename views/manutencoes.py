import flet as ft
from database.db_manager import (
    buscar_todas_ferramentas,
    enviar_para_manutencao,
    buscar_manutencoes_ativas,
    registrar_retorno_manutencao,
    buscar_historico_manutencoes,
)
from datetime import datetime


def renderizar_manutencoes(page):

    def mostrar_msg(texto, sucesso=True):
        cor = ft.Colors.GREEN_700 if sucesso else ft.Colors.RED_700
        snackbar = ft.SnackBar(
            content=ft.Text(texto, color=ft.Colors.WHITE),
            bgcolor=cor,
        )
        # CORREÇÃO AQUI
        if snackbar not in page.overlay:
            page.overlay.append(snackbar)
        snackbar.open = True
        page.update()

    def formatar_data(data_str):
        if not data_str:
            return "-"
        try:
            return datetime.strptime(
                str(data_str), "%Y-%m-%d %H:%M:%S"
            ).strftime("%d/%m/%Y às %H:%M")
        except Exception:
            return str(data_str)

    ferramenta_dropdown = ft.Dropdown(label="Selecione a Ferramenta", width=450)
    motivo_field = ft.TextField(label="Motivo do Defeito / Avaria", width=450, multiline=True, min_lines=4)

    def carregar_ferramentas_dropdown():
        try:
            todas = buscar_todas_ferramentas()
            elegiveis = []
            for f in todas:
                status = str(f.get("status", "")).lower()
                situacao = str(f.get("situacao", "")).lower()
                if status == "disponivel" and situacao != "em manutenção":
                    elegiveis.append(f)

            ferramenta_dropdown.options = [
                ft.dropdown.Option(
                    key=str(f["id"]),
                    text="%s | Patrimônio: %s" % (f["nome"], f["patrimonio"]),
                )
                for f in elegiveis
            ]
        except Exception as ex:
            mostrar_msg("Erro ao carregar ferramentas: %s" % ex, False)

    def btn_enviar_click(e):
        if not ferramenta_dropdown.value:
            mostrar_msg("Selecione uma ferramenta.", False)
            return
        if not motivo_field.value:
            mostrar_msg("Informe o motivo da manutenção.", False)
            return
        try:
            enviar_para_manutencao(int(ferramenta_dropdown.value), motivo_field.value)
            mostrar_msg("Ferramenta enviada para manutenção!")
            ferramenta_dropdown.value = None
            motivo_field.value = ""
            atualizar_telas()
        except Exception as ex:
            mostrar_msg("Erro: %s" % ex, False)

    # ABA NOVA MANUTENÇÃO
    aba_nova = ft.Column(
        controls=[
            ft.Text("Enviar Ferramenta para Oficina", size=22, weight=ft.FontWeight.BOLD),
            ferramenta_dropdown,
            motivo_field,
            # CORREÇÃO AQUI: String primeiro
            ft.ElevatedButton("Enviar para Conserto", icon=ft.Icons.BUILD, on_click=btn_enviar_click),
        ],
        spacing=20, expand=True,
    )

    tabela_ativas = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Ferramenta")),
            ft.DataColumn(ft.Text("Patrimônio")),
            ft.DataColumn(ft.Text("Data Envio")),
            ft.DataColumn(ft.Text("Motivo")),
            ft.DataColumn(ft.Text("Ação")),
        ],
        rows=[],
    )

    def fechar_dialogo(dialogo):
        dialogo.open = False
        page.update()

    def abrir_dialogo_retorno(manutencao_id, ferramenta_id, nome):
        observacao_field = ft.TextField(label="Descrição do conserto", multiline=True, width=400, min_lines=4)

        def confirmar(e):
            try:
                registrar_retorno_manutencao(manutencao_id, ferramenta_id, observacao_field.value)
                mostrar_msg("%s retornou ao estoque!" % nome)
                fechar_dialogo(dialogo)
                atualizar_telas()
            except Exception as ex:
                mostrar_msg("Erro: %s" % ex, False)

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Retorno da Ferramenta: %s" % nome),
            content=observacao_field,
            actions=[
                # CORREÇÃO AQUI: Strings primeiro
                ft.TextButton("Cancelar", on_click=lambda e: fechar_dialogo(dialogo)),
                ft.ElevatedButton("Confirmar Retorno", icon=ft.Icons.CHECK, on_click=confirmar),
            ],
        )

        # CORREÇÃO AQUI
        if dialogo not in page.overlay:
            page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    def carregar_ativas():
        tabela_ativas.rows.clear()
        try:
            manutencoes = buscar_manutencoes_ativas()
            for item in manutencoes:
                tabela_ativas.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(item["nome"]))),
                            ft.DataCell(ft.Text(str(item["patrimonio"]))),
                            ft.DataCell(ft.Text(formatar_data(item["data_envio"]))),
                            ft.DataCell(ft.Text(str(item["motivo"]))),
                            ft.DataCell(
                                # CORREÇÃO AQUI: String primeiro
                                ft.ElevatedButton(
                                    "Dar Baixa",
                                    icon=ft.Icons.CHECK,
                                    on_click=lambda e, m=item["id"], f=item["ferramenta_id"], n=item["nome"]: abrir_dialogo_retorno(m, f, n),
                                )
                            ),
                        ]
                    )
                )
        except Exception as ex:
            mostrar_msg("Erro ao carregar manutenções: %s" % ex, False)

    aba_ativas = ft.Column(
        controls=[
            ft.Text("Ferramentas em Conserto", size=22, weight=ft.FontWeight.BOLD),
            ft.Row(controls=[tabela_ativas], scroll=ft.ScrollMode.AUTO, expand=True),
        ],
        expand=True,
    )

    tabela_historico = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Ferramenta")),
            ft.DataColumn(ft.Text("Patrimônio")),
            ft.DataColumn(ft.Text("Data Envio")),
            ft.DataColumn(ft.Text("Data Retorno")),
            ft.DataColumn(ft.Text("Motivo")),
            ft.DataColumn(ft.Text("Laudo")),
        ],
        rows=[],
    )

    def carregar_historico():
        tabela_historico.rows.clear()
        try:
            historico = buscar_historico_manutencoes()
            for item in historico:
                tabela_historico.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(item["nome"]))),
                            ft.DataCell(ft.Text(str(item["patrimonio"]))),
                            ft.DataCell(ft.Text(formatar_data(item["data_envio"]))),
                            ft.DataCell(ft.Text(formatar_data(item["data_retorno"]))),
                            ft.DataCell(ft.Text(str(item["motivo"]))),
                            ft.DataCell(ft.Text(str(item["observacao"] or "-"))),
                        ]
                    )
                )
        except Exception as ex:
            mostrar_msg("Erro ao carregar histórico: %s" % ex, False)

        # Campo de busca e tabela do histórico
    campo_busca = ft.TextField(
        hint_text="Buscar por ferramenta, patrimônio ou motivo",
        expand=True,
        on_change=lambda e: carregar_historico_filtrado(e.control.value)
    )
    btn_buscar = ft.IconButton(icon=ft.Icons.SEARCH, on_click=lambda e: carregar_historico_filtrado(campo_busca.value))

    tabela_historico = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Ferramenta")),
            ft.DataColumn(ft.Text("Patrimônio")),
            ft.DataColumn(ft.Text("Data Envio")),
            ft.DataColumn(ft.Text("Data Retorno")),
            ft.DataColumn(ft.Text("Motivo")),
            ft.DataColumn(ft.Text("Laudo")),
        ],
        rows=[],
    )

    def carregar_historico_filtrado(termo=""):
        tabela_historico.rows.clear()
        try:
            # Usa a nova função que aceita filtro
            from database.db_manager import buscar_historico_manutencoes_filtrado
            historico = buscar_historico_manutencoes_filtrado(termo)
            for item in historico:
                tabela_historico.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(item["nome"]))),
                            ft.DataCell(ft.Text(str(item["patrimonio"]))),
                            ft.DataCell(ft.Text(formatar_data(item["data_envio"]))),
                            ft.DataCell(ft.Text(formatar_data(item["data_retorno"]))),
                            ft.DataCell(ft.Text(str(item["motivo"]))),
                            ft.DataCell(ft.Text(str(item["observacao"] or "-"))),
                        ]
                    )
                )
        except Exception as ex:
            mostrar_msg(f"Erro ao carregar histórico: {ex}", False)
        page.update()

    def carregar_historico():
        carregar_historico_filtrado("")

    aba_historico = ft.Column(
        controls=[
            ft.Text("Histórico de Manutenções", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([campo_busca, btn_buscar], spacing=10),
            ft.Row(controls=[tabela_historico], scroll=ft.ScrollMode.AUTO, expand=True),
        ],
        expand=True,
    )
    def atualizar_telas():
        carregar_ferramentas_dropdown()
        carregar_ativas()
        carregar_historico()
        page.update()

    atualizar_telas()

    tab_bar = ft.TabBar(
        tabs=[
            ft.Tab(label="Nova Manutenção"),
            ft.Tab(label="Em Conserto"),
            ft.Tab(label="Histórico"),
        ]
    )

    tab_view = ft.TabBarView(
        expand=True,
        controls=[
            ft.Container(content=aba_nova, expand=True, padding=10),
            ft.Container(content=aba_ativas, expand=True, padding=10),
            ft.Container(content=aba_historico, expand=True, padding=10),
        ],
    )

    tabs = ft.Tabs(
        selected_index=0,
        length=3,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[tab_bar, tab_view],
        ),
    )

    return ft.Column(
        controls=[
            ft.Text("Oficina e Manutenção", size=26, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            tabs,
        ],
        expand=True,
    )