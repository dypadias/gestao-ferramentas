import flet as ft
import datetime
from database.db_manager import (
    buscar_funcionarios_ativos,
    buscar_ferramentas_disponiveis,
    buscar_locais_ativos,
    registrar_emprestimo,
)


def renderizar_emprestimos(page):
    """
    Renderiza a tela de empréstimos com seleção de funcionário e ferramenta usando Flet.
    """
    def borda_sutil():
        return ft.Border(
            top=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
            right=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
            bottom=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
            left=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
        )

    # Buscar dados
    funcionarios = buscar_funcionarios_ativos()
    ferramentas = buscar_ferramentas_disponiveis()
    locais = buscar_locais_ativos()

    # Controles
    funcionario_dropdown = ft.Dropdown(
        label="Funcionário",
        options=[
            ft.dropdown.Option(key=str(f['id']), text=f"{f['nome']} - {f['cargo']}")
            for f in funcionarios
        ] if funcionarios else [],
        width=400,
    )

    ferramenta_dropdown = ft.Dropdown(
        label="Ferramenta",
        options=[
            ft.dropdown.Option(key=str(f['id']), text=f"{f['nome']} (Patrimônio: {f['patrimonio']})")
            for f in ferramentas
        ] if ferramentas else [],
        width=400,
    )

    local_dropdown = ft.Dropdown(
        label="Local de Uso",
        options=[
            ft.dropdown.Option(key=str(l['id']), text=l['nome'])
            for l in locais
        ] if locais else [],
        width=400,
    )

    def abrir_picker(picker):
        if hasattr(page, "open"):
            page.open(picker)
            return

        if picker not in page.overlay:
            page.overlay.append(picker)
        picker.open = True
        page.update()

    def data_picker_change(e):
        data_selecionada = e.control.value
        if data_selecionada:
            data_field.value = data_selecionada.strftime("%d/%m/%Y")
            page.update()

    def hora_picker_change(e):
        hora_selecionada = e.control.value
        if hora_selecionada:
            hora_field.value = hora_selecionada.strftime("%H:%M")
            page.update()

    data_field = ft.TextField(
        label="Data de Previsão",
        hint_text="DD/MM/YYYY",
        width=200,
        read_only=True,
        suffix_icon=ft.Icons.CALENDAR_MONTH,
        on_click=lambda e: abrir_picker(data_picker),
    )

    hora_field = ft.TextField(
        label="Hora de Previsão",
        hint_text="HH:MM",
        width=200,
        read_only=True,
        suffix_icon=ft.Icons.ACCESS_TIME,
        on_click=lambda e: abrir_picker(hora_picker),
    )

    data_picker = ft.DatePicker(on_change=data_picker_change)
    hora_picker = ft.TimePicker(on_change=hora_picker_change)

    def mostrar_mensagem(texto):
        snack_bar = ft.SnackBar(content=ft.Text(texto), open=True)
        page.overlay.append(snack_bar)
        page.update()

    # Função para registrar
    def registrar_click(e):
        if not funcionarios:
            mostrar_mensagem("Nenhum funcionário ativo encontrado.")
            return
        if not ferramentas:
            mostrar_mensagem("Nenhuma ferramenta disponível encontrada.")
            return
        if not locais:
            mostrar_mensagem("Nenhum local ativo encontrado.")
            return
        if not funcionario_dropdown.value or not ferramenta_dropdown.value or not local_dropdown.value or not data_field.value or not hora_field.value:
            mostrar_mensagem("Por favor, preencha todos os campos.")
            return

        try:
            # Parse data e hora
            data_obj = datetime.datetime.strptime(data_field.value, "%d/%m/%Y")
            hora_obj = datetime.datetime.strptime(hora_field.value, "%H:%M")
            previsao_datetime = datetime.datetime.combine(data_obj.date(), hora_obj.time())

            # IDs
            funcionario_id = int(funcionario_dropdown.value)
            ferramenta_id = int(ferramenta_dropdown.value)
            local_id = int(local_dropdown.value)
            gestor_id = 1  # Assumindo

            registrar_emprestimo(
                funcionario_id,
                ferramenta_id,
                gestor_id,
                local_id,
                previsao_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            )

            # Limpar campos
            funcionario_dropdown.value = ""
            ferramenta_dropdown.value = ""
            local_dropdown.value = ""
            data_field.value = ""
            hora_field.value = ""

            mostrar_mensagem("Empréstimo registrado com sucesso!")
            page.update()

        except ValueError as ve:
            mostrar_mensagem(f"Erro de formato: {str(ve)}")
        except Exception as ex:
            mostrar_mensagem(f"Erro ao registrar empréstimo: {str(ex)}")

    # Botão
    registrar_button = ft.ElevatedButton(
        "Registrar Empréstimo",
        icon=ft.Icons.OUTBOX,
        bgcolor=ft.Colors.BLUE_GREY_800,
        color=ft.Colors.WHITE,
        on_click=registrar_click,
    )

    # Mensagens de aviso
    mensagens = []
    if not funcionarios:
        mensagens.append(ft.Text("Nenhum funcionário ativo encontrado. Cadastre funcionários antes de registrar empréstimos.", color=ft.Colors.ORANGE))
    if not ferramentas:
        mensagens.append(ft.Text("Nenhuma ferramenta disponível encontrada. Cadastre ferramentas ou libere ferramentas emprestadas.", color=ft.Colors.ORANGE))
    if not locais:
        mensagens.append(ft.Text("Nenhum local ativo encontrado. Cadastre um local antes de registrar empréstimos.", color=ft.Colors.ORANGE))

    formulario = ft.Card(
        elevation=1,
        content=ft.Container(
            content=ft.Column(
                [
                    *mensagens,
                    funcionario_dropdown,
                    ferramenta_dropdown,
                    local_dropdown,
                    ft.Divider(color=ft.Colors.BLUE_GREY_100),
                    ft.Row([data_field, hora_field], wrap=True, spacing=12),
                    registrar_button,
                ],
                spacing=18,
            ),
            bgcolor=ft.Colors.WHITE,
            border=borda_sutil(),
            border_radius=8,
            padding=20,
        ),
    )

    # Layout
    return ft.Column([
        ft.Text("Novo Empréstimo", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900),
        ft.Divider(color=ft.Colors.BLUE_GREY_100),
        formulario,
    ], spacing=20, expand=True)
