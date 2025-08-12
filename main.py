#main.py
import logging
import sys
import os

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Ajusta path para importar modules locais
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pages.downloadFaturaClaro import baixar_faturas
from utils.downloadUtils import garantir_diretorio

logger = logging.getLogger(__name__)

def main():
    load_dotenv()

    # Diretórios finais
    LINUX_DOWNLOAD_DIR = "/home/allancdev/faturas_temp"  # Pasta Linux para mover os arquivos
    WINDOWS_DOWNLOAD_DIR = "/mnt/c/Users/compu/OneDrive/Documentos/binario-fatura-claro/fatura/Claro"  # Pasta Windows via WSL

    garantir_diretorio(LINUX_DOWNLOAD_DIR)
    garantir_diretorio(WINDOWS_DOWNLOAD_DIR)

    options = Options()

    # Usa perfil real para manter sessão e cookies, evitando login a toda execução
    options.add_argument("--user-data-dir=/mnt/c/Users/compu/AppData/Local/Google/Chrome/User Data")
    options.add_argument("--profile-directory=Profile 2")

    # Evita ser detectado como automação
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")

    # NÃO setar download.default_directory para não sobrescrever o perfil real

    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    # Remove navigator.webdriver para evitar detecção
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })

    try:
        logger.info("Abrindo página de login...")

        from pages.loginClaro import LoginPage
        from pages.faturaClaro import FaturaPage
        from pages.faturasPendentes import FaturasPendentesPage

        login_page = LoginPage(driver)
        login_page.open_login_page()

        if not login_page.esta_logado():
            logger.info("Usuário não está logado. Iniciando login...")
            login_page.click_entrar()
            login_page.selecionar_minha_claro_residencial()
            login_page.preencher_login_usuario()
            login_page.clicar_continuar()
            login_page.preencher_senha()
            login_page.clicar_botao_acessar()
        else:
            logger.info("Sessão já ativa, pulando login.")

        fatura_page = FaturaPage(driver)
        fatura_page.selecionar_contrato_ativo()

        faturas_pendentes_page = FaturasPendentesPage(driver)
        faturas_pendentes_page.selecionar_faturas_pendentes()

        logger.info("Iniciando download das faturas...")
        # Aqui deve passar o número do contrato, se necessário — ajuste conforme sua lógica
        numero_contrato = "123/456"  # exemplo, ajuste para capturar dinamicamente
        baixar_faturas(driver, LINUX_DOWNLOAD_DIR, WINDOWS_DOWNLOAD_DIR, numero_contrato)
        
        # --- NOVO CÓDIGO AQUI ---
        faturas_pendentes_page.verificar_mes_anterior_e_voltar_contratos()
        # --- FIM DO NOVO CÓDIGO ---

    except Exception as e:
        logger.error(f"Erro geral na execução: {e}", exc_info=True)

    finally:
        input("⏸ Pressione Enter para encerrar...")
        driver.quit()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
    )
    main()