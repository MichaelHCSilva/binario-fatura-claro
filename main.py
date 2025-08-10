# main.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from pages.loginClaro import LoginPage
from pages.faturaClaro import FaturaPage

def main():
    load_dotenv()  

    options = Options()
    
    options.add_argument("--user-data-dir=/mnt/c/Users/compu/AppData/Local/Google/Chrome/User Data")
    options.add_argument("--profile-directory=Profile 2")

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")

    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })

    try:
        login_page = LoginPage(driver)
        login_page.open_login_page()

        if not login_page.esta_logado():
            login_page.click_entrar()
            login_page.selecionar_minha_claro_residencial()
            login_page.preencher_login_usuario()
            login_page.clicar_continuar()
            login_page.preencher_senha()
            login_page.clicar_botao_acessar()
        else:
            print("Sessão já ativa, pulando login.")

        fatura_page = FaturaPage(driver)
        fatura_page.selecionar_contrato_ativo()
        
    finally:
        input("⏸ Pressione Enter para encerrar...")
        driver.quit()

if __name__ == "__main__":
    main()
