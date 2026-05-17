import flet as ft
from database.db_manager import (
    atualizar_ferramenta,
    atualizar_funcionario,
    atualizar_local,
    buscar_todas_ferramentas,
    buscar_todos_funcionarios,
    buscar_todos_locais,
    cadastrar_ferramenta,
    cadastrar_funcionario,
    cadastrar_local,
)


def renderizar_cadastros(page):

    # =====================================================
    # MENSAGENS
    # =====================================================

    def mostrar_mensagem(texto):
        snack_bar = ft.SnackBar(
            content=ft.Text(texto)
        )
        if snack_bar not in page.overlay:
            page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

    # =====================================================
    # TABELAS (Permanece igual)
    # =====================================================

    def criar_tabela(columns):
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(column, weight=ft.FontWeight.BOLD))
                for column in columns
            ],
            rows=[]
        )

    def painel_tabela(tabela):
        return ft.Container(
            content=ft.Row([tabela], scroll=ft.ScrollMode.AUTO),
            padding=10,
            border=ft.Border(
                top=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
                bottom=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
                left=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
                right=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
            ),
            border_radius=8
        )

    ferramentas_tabela = criar_tabela(["Nome", "Patrimônio", "Status", "Situação", "Ações"])
    funcionarios_tabela = criar_tabela(["Nome", "Cargo", "Status", "Ações"])
    locais_tabela = criar_tabela(["Nome", "Status", "Ações"])

    # =====================================================
    # EDITAR FERRAMENTA
    # =====================================================

    def abrir_dialogo_editar(ferramenta):
        nome_field = ft.TextField(label="Nome", value=ferramenta["nome"], width=320)
        patrimonio_field = ft.TextField(label="Patrimônio", value=ferramenta["patrimonio"], width=320)
        situacao_dropdown = ft.Dropdown(
            label="Situação",
            value=ferramenta.get("situacao", "OK"),
            options=[
                ft.dropdown.Option("OK"),
                ft.dropdown.Option("Avaria"),
                ft.dropdown.Option("Em Manutenção"),
            ],
            width=320
        )

        def fechar_dialogo(e=None):
            dialog.open = False
            page.update()

        def salvar_edicao(e):
            try:
                atualizar_ferramenta(ferramenta["id"], nome_field.value, patrimonio_field.value, situacao_dropdown.value)
                dialog.open = False
                atualizar_tabelas()
                mostrar_mensagem("Ferramenta atualizada!")
            except Exception as ex:
                mostrar_mensagem(f"Erro: {str(ex)}")
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Ferramenta"),
            content=ft.Column([nome_field, patrimonio_field, situacao_dropdown], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Salvar", icon=ft.Icons.SAVE, on_click=salvar_edicao)
            ]
        )

        # CORREÇÃO AQUI
        if dialog not in page.overlay:
            page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # =====================================================
    # EDITAR FUNCIONÁRIO
    # =====================================================

    def abrir_dialogo_editar_funcionario(funcionario):
        nome_field = ft.TextField(label="Nome", value=funcionario["nome"], width=320)
        cargo_field = ft.TextField(label="Cargo", value=funcionario["cargo"], width=320)
        status_dropdown = ft.Dropdown(
            label="Status",
            value="Ativo" if funcionario.get("ativo", 1) == 1 else "Inativo",
            options=[ft.dropdown.Option("Ativo"), ft.dropdown.Option("Inativo")],
            width=320
        )

        def fechar_dialogo(e=None):
            dialog.open = False
            page.update()

        def salvar_edicao(e):
            try:
                atualizar_funcionario(funcionario["id"], nome_field.value, cargo_field.value, 1 if status_dropdown.value == "Ativo" else 0)
                dialog.open = False
                atualizar_tabelas()
                mostrar_mensagem("Funcionário atualizado!")
            except Exception as ex:
                mostrar_mensagem(f"Erro: {str(ex)}")
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Funcionário"),
            content=ft.Column([nome_field, cargo_field, status_dropdown], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Salvar", icon=ft.Icons.SAVE, on_click=salvar_edicao)
            ]
        )

        # CORREÇÃO AQUI
        if dialog not in page.overlay:
            page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # =====================================================
    # EDITAR LOCAL
    # =====================================================

    def abrir_dialogo_editar_local(local):
        nome_field = ft.TextField(label="Nome", value=local["nome"], width=320)
        status_dropdown = ft.Dropdown(
            label="Status",
            value="Ativo" if local.get("ativo", 1) == 1 else "Inativo",
            options=[ft.dropdown.Option("Ativo"), ft.dropdown.Option("Inativo")],
            width=320
        )

        def fechar_dialogo(e=None):
            dialog.open = False
            page.update()

        def salvar_edicao(e):
            try:
                atualizar_local(local["id"], nome_field.value, 1 if status_dropdown.value == "Ativo" else 0)
                dialog.open = False
                atualizar_tabelas()
                mostrar_mensagem("Local atualizado!")
            except Exception as ex:
                mostrar_mensagem(f"Erro: {str(ex)}")
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Local"),
            content=ft.Column([nome_field, status_dropdown], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Salvar", icon=ft.Icons.SAVE, on_click=salvar_edicao)
            ]
        )

        # CORREÇÃO AQUI
        if dialog not in page.overlay:
            page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # =====================================================
    # ATUALIZAR TABELAS
    # =====================================================

    def atualizar_tabelas():
        ferramentas = buscar_todas_ferramentas()
        funcionarios = buscar_todos_funcionarios()
        locais = buscar_todos_locais()

        ferramentas_tabela.rows.clear()
        funcionarios_tabela.rows.clear()
        locais_tabela.rows.clear()

        for ferramenta in ferramentas:
            ferramenta = dict(ferramenta)
            ferramentas_tabela.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(ferramenta["nome"])),
                    ft.DataCell(ft.Text(ferramenta["patrimonio"])),
                    ft.DataCell(ft.Text(ferramenta["status"] or "-")),
                    ft.DataCell(ft.Text(ferramenta.get("situacao", "OK"))),
                    ft.DataCell(ft.IconButton(icon=ft.Icons.EDIT, on_click=lambda e, f=ferramenta: abrir_dialogo_editar(f)))
                ])
            )

        for funcionario in funcionarios:
            funcionario = dict(funcionario)
            funcionarios_tabela.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(funcionario["nome"])),
                    ft.DataCell(ft.Text(funcionario["cargo"])),
                    ft.DataCell(ft.Text("Ativo" if funcionario.get("ativo", 1) == 1 else "Inativo")),
                    ft.DataCell(ft.IconButton(icon=ft.Icons.EDIT, on_click=lambda e, f=funcionario: abrir_dialogo_editar_funcionario(f)))
                ])
            )

        for local in locais:
            local = dict(local)
            locais_tabela.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(local["nome"])),
                    ft.DataCell(ft.Text("Ativo" if local.get("ativo", 1) == 1 else "Inativo")),
                    ft.DataCell(ft.IconButton(icon=ft.Icons.EDIT, on_click=lambda e, l=local: abrir_dialogo_editar_local(l)))
                ])
            )

    # =====================================================
    # CAMPOS E TELAS
    # =====================================================

    ferramenta_nome = ft.TextField(label="Nome da Ferramenta", width=300)
    ferramenta_patrimonio = ft.TextField(label="Número do Patrimônio", width=300)

    def salvar_ferramenta_click(e):
        if not ferramenta_nome.value or not ferramenta_patrimonio.value:
            mostrar_mensagem("Preencha Nome e Patrimônio.")
            return
        try:
            cadastrar_ferramenta(ferramenta_nome.value, ferramenta_patrimonio.value)
            ferramenta_nome.value = ""
            ferramenta_patrimonio.value = ""
            atualizar_tabelas()
            mostrar_mensagem("Ferramenta cadastrada!")
        except Exception as ex:
            mostrar_mensagem(f"Erro: {str(ex)}")
        page.update()

    salvar_ferramenta_btn = ft.ElevatedButton("Salvar Ferramenta", on_click=salvar_ferramenta_click)

    ferramentas_content = ft.Column([
        ferramenta_nome, ferramenta_patrimonio, salvar_ferramenta_btn, ft.Divider(),
        ft.Text("Ferramentas cadastradas", size=18, weight=ft.FontWeight.BOLD),
        painel_tabela(ferramentas_tabela)
    ], scroll=ft.ScrollMode.AUTO, expand=True)


    funcionario_nome = ft.TextField(label="Nome do Funcionário", width=300)
    funcionario_cargo = ft.TextField(label="Cargo", width=300)

    def salvar_funcionario_click(e):
        if not funcionario_nome.value or not funcionario_cargo.value:
            mostrar_mensagem("Preencha Nome e Cargo.")
            return
        try:
            cadastrar_funcionario(funcionario_nome.value, funcionario_cargo.value)
            funcionario_nome.value = ""
            funcionario_cargo.value = ""
            atualizar_tabelas()
            mostrar_mensagem("Funcionário cadastrado!")
        except Exception as ex:
            mostrar_mensagem(f"Erro: {str(ex)}")
        page.update()

    salvar_funcionario_btn = ft.ElevatedButton("Salvar Funcionário", on_click=salvar_funcionario_click)

    funcionarios_content = ft.Column([
        funcionario_nome, funcionario_cargo, salvar_funcionario_btn, ft.Divider(),
        ft.Text("Funcionários cadastrados", size=18, weight=ft.FontWeight.BOLD),
        painel_tabela(funcionarios_tabela)
    ], scroll=ft.ScrollMode.AUTO, expand=True)


    local_nome = ft.TextField(label="Nome do Local/Setor", width=300)

    def salvar_local_click(e):
        if not local_nome.value:
            mostrar_mensagem("Preencha o Nome do Local.")
            return
        try:
            cadastrar_local(local_nome.value)
            local_nome.value = ""
            atualizar_tabelas()
            mostrar_mensagem("Local cadastrado!")
        except Exception as ex:
            mostrar_mensagem(f"Erro: {str(ex)}")
        page.update()

    salvar_local_btn = ft.ElevatedButton("Salvar Local", on_click=salvar_local_click)

    locais_content = ft.Column([
        local_nome, salvar_local_btn, ft.Divider(),
        ft.Text("Locais cadastrados", size=18, weight=ft.FontWeight.BOLD),
        painel_tabela(locais_tabela)
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    atualizar_tabelas()

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        length=3,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Ferramentas", icon=ft.Icons.CONSTRUCTION),
                        ft.Tab(label="Funcionários", icon=ft.Icons.BADGE),
                        ft.Tab(label="Locais", icon=ft.Icons.PLACE),
                    ]
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[ferramentas_content, funcionarios_content, locais_content]
                )
            ]
        )
    )

    return ft.Column([
        ft.Text("Cadastros", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        tabs
    ], spacing=20, expand=True)