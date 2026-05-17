import flet as ft
import inspect
from database.db_manager import init_db
from views.dashboard import renderizar_dashboard
from views.emprestimos import renderizar_emprestimos
from views.devolucoes import renderizar_devolucoes
from views.cadastros import renderizar_cadastros
from views.historico import renderizar_historico
from views.manutencoes import renderizar_manutencoes

async def main(page: ft.Page):
    page.title = "Gestão de Ferramentas"
    
    # Define o ícone da janela (busca na pasta assets)
    page.window.icon = "logo.ico" 
    
    # Propriedades da Janela
    page.window.width = 1200
    page.window.height = 800
    page.window.min_width = 1000
    page.window.min_height = 700
    page.theme_mode = ft.ThemeMode.SYSTEM  # Suporte a tema do sistema
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE_GREY)
    page.bgcolor = ft.Colors.WHITE

    if hasattr(page, "window_center"):
        result = page.window_center()
        if inspect.isawaitable(result):
            await result
    elif hasattr(page, "window") and hasattr(page.window, "center"):
        result = page.window.center()
        if inspect.isawaitable(result):
            await result

    # Inicializa o banco de dados
    init_db()

    # Estado para controlar a aba selecionada
    page.data = {"selected_index": 0}

    # Container para o conteúdo principal
    content_container = ft.Container()

    def on_navigation_change(e):
        page.data["selected_index"] = e.control.selected_index
        update_content(page)
        page.update()

    def update_content(page):
        idx = page.data["selected_index"]
        if idx == 0:
            content_container.content = renderizar_dashboard(page)
        elif idx == 1:
            content_container.content = renderizar_emprestimos(page)
        elif idx == 2:
            content_container.content = renderizar_devolucoes(page)
        elif idx == 3:
            content_container.content = renderizar_cadastros(page)
        elif idx == 4:
            content_container.content = renderizar_historico(page)
        elif idx == 5:
            content_container.content = renderizar_manutencoes(page)
        else:
            content_container.content = ft.Text("Página não encontrada")

    def rail_icon(icon, selected=False):
        return ft.Icon(
            icon,
            color=ft.Colors.WHITE if selected else ft.Colors.BLUE_GREY_100,
        )

    # NavigationRail
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        bgcolor=ft.Colors.GREY_900,
        indicator_color=ft.Colors.BLUE_GREY_700,
        selected_label_text_style=ft.TextStyle(color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        unselected_label_text_style=ft.TextStyle(color=ft.Colors.BLUE_GREY_100),
        
                leading=ft.Container(
            content=ft.Column(
                [
                    ft.Image(src="logo.png", width=100, fit=ft.BoxFit.CONTAIN),
                    ft.Text("DM Gestão", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text("Controle de Ferramentas", size=10, color=ft.Colors.BLUE_GREY_200),
                    ft.Divider(color=ft.Colors.BLUE_GREY_700),
                ],
                spacing=6,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=10,
        ),
        
        # As opções de navegação
        destinations=[
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.DASHBOARD_OUTLINED),
                selected_icon=rail_icon(ft.Icons.DASHBOARD_OUTLINED, selected=True),
                label="Dashboard"
            ),
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.OUTBOX),
                selected_icon=rail_icon(ft.Icons.OUTBOX, selected=True),
                label="Novo Empréstimo"
            ),
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.INBOX),
                selected_icon=rail_icon(ft.Icons.INBOX, selected=True),
                label="Devoluções"
            ),
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED),
                selected_icon=rail_icon(ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED, selected=True),
                label="Cadastros"
            ),
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.HISTORY),
                selected_icon=rail_icon(ft.Icons.HISTORY, selected=True),
                label="Histórico"
            ),
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.BUILD), 
                selected_icon=rail_icon(ft.Icons.BUILD, selected=True),
                label="Manutenção"
            ),
        ],
        
        # 2. ASSINATURA: O rodapé da barra lateral (trailing)
        trailing=ft.Container(
            content=ft.Column(
                [
                    ft.Text("Criado e desenvolvido por:", size=10, color=ft.Colors.BLUE_GREY_400, text_align=ft.TextAlign.CENTER),
                    ft.Text("Diego Matos", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_200, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2
            ),
            expand=True, 
            alignment=ft.Alignment(0, 1), 
            # CORREÇÃO AQUI: Passou a ser ft.Padding (com 'P' maiúsculo)
            padding=ft.Padding.only(bottom=20) 
        ),
        
        on_change=on_navigation_change,
    )

    # Layout principal
    page.add(
        ft.Row([
            rail,
            ft.VerticalDivider(width=1, color=ft.Colors.BLUE_GREY_100),
            ft.Container(
                content=content_container,
                expand=True,
                padding=20,
                bgcolor=ft.Colors.WHITE,
            )
        ], expand=True)
    )

    # Inicializar com Dashboard
    update_content(page)

# Inicia a aplicação passando o diretório base para as imagens
ft.run(main, assets_dir="assets")