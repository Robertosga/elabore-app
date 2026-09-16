import pytest
from playwright.sync_api import Page, expect

APP_URL = "https://elabore-app-kus2ne4a6stuk9npsnhyjf.streamlit.app/"

def get_st_frame(page: Page):
    """Retorna o locator para o iframe principal do Streamlit Cloud."""
    return page.frame_locator("iframe").first

def test_streamlit_app_loads(page: Page):
    page.goto(APP_URL, wait_until="networkidle")
    
    st_frame = get_st_frame(page)
    main_container = st_frame.locator("[data-testid='stAppViewContainer']")
    
    # Aguarda a app carregar dentro do iframe
    expect(main_container).to_be_visible(timeout=45000)

def test_interact_with_inputs_and_buttons(page: Page):
    page.goto(APP_URL, wait_until="networkidle")
    st_frame = get_st_frame(page)
    
    # Exemplo: interagindo com o primeiro input de texto
    text_input = st_frame.locator("[data-testid='stTextInput'] input").first
    if text_input.is_visible(timeout=10000):
        text_input.fill("Teste E2E")
        text_input.press("Enter")

    # Exemplo: clicando em um botão
    button = st_frame.locator("[data-testid='stButton'] button").first
    if button.is_visible():
        button.click()