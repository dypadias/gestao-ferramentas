import flet as ft
from database.db_manager import (
    buscar_todas_ferramentas,
    buscar_todos_funcionarios,
    buscar_todos_locais,
    cadastrar_ferramenta,
    cadastrar_funcionario,
    cadastrar_local,
)


def renderizar_cadastros(page):
    """
    Renderiza a tela de cadastros usando Flet.
    """
    def mostrar_mensagem(texto):
        snack_bar = ft.SnackBar(content=ft.Text(texto), open=True)
        page.overlay.append(snack_bar)

    def criar_borda_tabela():
        return ft.Border(
            top=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
            right=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
            bottom=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
            left=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
        )

    def criar_tabela(columns):
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(column, weight=ft.FontWeight.BOLD))
                for column in columns
            ],
            rows=[],
            border=criar_borda_tabela(),
            border_radius=8,
            heading_row_color=ft.Colors.BLUE_GREY_50,
            horizontal_lines=ft.BorderSide(1, ft.Colors.BLUE_GREY_50),
            column_spacing=24,
        )

    def painel_tabela(tabela):
        return ft.Card(
            elevation=1,
            content=ft.Container(
                content=ft.Row([tabela], scroll=ft.ScrollMode.AUTO),
                bgcolor=ft.Colors.WHITE,
                border=criar_borda_tabela(),
                border_radius=8,
                padding=10,
            ),
        )

    ferramentas_tabela = criar_tabela(["Nome", "Patrimônio", "Status"])
    funcionarios_tabela = criar_tabela(["Nome", "Cargo"])
    locais_tabela = criar_tabela(["Nome"])

    def atualizar_tabelas():
        ferramentas = buscar_todas_ferramentas()
        funcionarios = buscar_todos_funcionarios()
        locais = buscar_todos_locais()

        ferramentas_tabela.rows.clear()
        funcionarios_tabela.rows.clear()
        locais_tabela.rows.clear()

        for ferramenta in ferramentas:
            ferramentas_tabela.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(ferramenta["nome"])),
                        ft.DataCell(ft.Text(ferramenta["patrimonio"])),
                        ft.DataCell(ft.Text(ferramenta["status"] or "-")),
                    ]
                )
            )

        for funcionario in funcionarios:
            funcionarios_tabela.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(funcionario["nome"])),
                        ft.DataCell(ft.Text(funcionario["cargo"])),
                    ]
                )
            )

        for local in locais:
            locais_tabela.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(local["nome"])),
                    ]
                )
            )

    # Controles para Ferramentas
    ferramenta_nome = ft.TextField(label="Nome da Ferramenta", width=300)
    ferramenta_patrimonio = ft.TextField(label="Número do Patrimônio", width=300)

    def salvar_ferramenta_click(e):
        if not ferramenta_nome.value or not ferramenta_patrimonio.value:
            mostrar_mensagem("Por favor, preencha Nome e Patrimônio.")
            page.update()
            return
        try:
            cadastrar_ferramenta(ferramenta_nome.value, ferramenta_patrimonio.value)
            ferramenta_nome.value = ""
            ferramenta_patrimonio.value = ""
            atualizar_tabelas()
            mostrar_mensagem("Ferramenta cadastrada com sucesso!")
            page.update()
        except Exception as ex:
            mostrar_mensagem(f"Erro ao cadastrar ferramenta: {str(ex)}")
            page.update()

    salvar_ferramenta_btn = ft.ElevatedButton("Salvar Ferramenta", on_click=salvar_ferramenta_click)

    ferramentas_content = ft.Column(
        [
            ferramenta_nome,
            ferramenta_patrimonio,
            salvar_ferramenta_btn,
            ft.Divider(color=ft.Colors.BLUE_GREY_100),
            ft.Text("Ferramentas cadastradas", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900),
            painel_tabela(ferramentas_tabela),
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    # Controles para Funcionários
    funcionario_nome = ft.TextField(label="Nome do Funcionário", width=300)
    funcionario_cargo = ft.TextField(label="Cargo", width=300)

    def salvar_funcionario_click(e):
        if not funcionario_nome.value or not funcionario_cargo.value:
            mostrar_mensagem("Por favor, preencha Nome e Cargo.")
            page.update()
            return
        try:
            cadastrar_funcionario(funcionario_nome.value, funcionario_cargo.value)
            funcionario_nome.value = ""
            funcionario_cargo.value = ""
            atualizar_tabelas()
            mostrar_mensagem("Funcionário cadastrado com sucesso!")
            page.update()
        except Exception as ex:
            mostrar_mensagem(f"Erro ao cadastrar funcionário: {str(ex)}")
            page.update()

    salvar_funcionario_btn = ft.ElevatedButton("Salvar Funcionário", on_click=salvar_funcionario_click)

    funcionarios_content = ft.Column(
        [
            funcionario_nome,
            funcionario_cargo,
            salvar_funcionario_btn,
            ft.Divider(color=ft.Colors.BLUE_GREY_100),
            ft.Text("Funcionários cadastrados", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900),
            painel_tabela(funcionarios_tabela),
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    # Controles para Locais
    local_nome = ft.TextField(label="Nome do Local/Setor", width=300)

    def salvar_local_click(e):
        if not local_nome.value:
            mostrar_mensagem("Por favor, preencha o Nome do Local.")
            page.update()
            return
        try:
            cadastrar_local(local_nome.value)
            local_nome.value = ""
            atualizar_tabelas()
            mostrar_mensagem("Local cadastrado com sucesso!")
            page.update()
        except Exception as ex:
            mostrar_mensagem(f"Erro ao cadastrar local: {str(ex)}")
            page.update()

    salvar_local_btn = ft.ElevatedButton("Salvar Local", on_click=salvar_local_click)

    locais_content = ft.Column(
        [
            local_nome,
            salvar_local_btn,
            ft.Divider(color=ft.Colors.BLUE_GREY_100),
            ft.Text("Locais cadastrados", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900),
            painel_tabela(locais_tabela),
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    atualizar_tabelas()

    tabs = ft.Tabs(
        content=ft.Column(
            [
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Ferramentas", icon=ft.Icons.CONSTRUCTION),
                        ft.Tab(label="Funcionários", icon=ft.Icons.BADGE),
                        ft.Tab(label="Locais", icon=ft.Icons.PLACE),
                    ],
                    indicator_color=ft.Colors.BLUE_GREY_700,
                    label_color=ft.Colors.GREY_900,
                    unselected_label_color=ft.Colors.BLUE_GREY_400,
                ),
                ft.TabBarView(
                    controls=[
                        ferramentas_content,
                        funcionarios_content,
                        locais_content,
                    ],
                    expand=True,
                ),
            ],
            spacing=20,
            expand=True,
        ),
        length=3,
        selected_index=0,
        expand=True,
    )

    return ft.Column(
        [
            ft.Text("Cadastros", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900),
            ft.Divider(color=ft.Colors.BLUE_GREY_100),
            tabs,
        ],
        spacing=20,
        expand=True,
    )
