from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pages.login_page import LoginPage

def main():
    options = Options()
    options.binary_location = "/usr/bin/google-chrome"

    # ✅ Usar perfil real do usuário (onde já está logado com Google)
    options.add_argument("--user-data-dir=/mnt/c/Users/compu/AppData/Local/Google/Chrome/User Data")
    options.add_argument("--profile-directory=Profile 2")

    # ✅ Evitar detecção do Selenium
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # ✅ Melhor estabilidade
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")

    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    # ✅ Remove 'navigator.webdriver = true'
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
        login_page.click_entrar()
    finally:
        input("⏸ Pressione Enter para encerrar...")  # para manter o navegador aberto
        driver.quit()

if __name__ == "__main__":
    main()
