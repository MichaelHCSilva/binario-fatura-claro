import os
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.downloadUtils import garantir_diretorio, mover_e_copiar_arquivo, DOWNLOAD_DIR

logger = logging.getLogger(__name__)

def baixar_faturas(driver, linux_download_dir, windows_download_dir, numero_contrato, timeout=60):
    garantir_diretorio(linux_download_dir)
    garantir_diretorio(windows_download_dir)

    wait = WebDriverWait(driver, timeout)

    try:
        links_download = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[data-testid="download-invoice"]'))
        )
    except Exception as e:
        logger.error(f"Não foi possível localizar links para download de faturas: {e}", exc_info=True)
        return

    if not links_download:
        logger.warning("Nenhum link para download encontrado na página.")
        return

    logger.info(f"Encontrados {len(links_download)} links para download de faturas.")

    for idx, link in enumerate(links_download, start=1):
        try:
            nome_arquivo = link.get_attribute("download")
            if not nome_arquivo or not nome_arquivo.strip():
                nome_arquivo = f"fatura_claro_{idx}.pdf"

            logger.info(f"Baixando fatura {idx}: {nome_arquivo}")

            arquivo_padrao = os.path.join(DOWNLOAD_DIR, nome_arquivo)
            if os.path.exists(arquivo_padrao):
                try:
                    os.remove(arquivo_padrao)
                    logger.info(f"Arquivo antigo removido no padrão: {arquivo_padrao}")
                except Exception as e:
                    logger.warning(f"Não foi possível remover arquivo antigo {arquivo_padrao}: {e}")

            # Clicar no link para iniciar o download
            driver.execute_script("arguments[0].click();", link)

            # Esperar o arquivo iniciar o download (existir na pasta, ou arquivo temporário)
            tempo_espera = 0
            intervalo_espera = 1
            while tempo_espera < timeout:
                if (os.path.exists(arquivo_padrao) or
                    os.path.exists(arquivo_padrao + ".crdownload") or
                    os.path.exists(arquivo_padrao + ".part")):
                    logger.info(f"Download do arquivo {nome_arquivo} detectado.")
                    break
                time.sleep(intervalo_espera)
                tempo_espera += intervalo_espera
            else:
                logger.warning(f"Timeout esperando download do arquivo {nome_arquivo} iniciar.")

            # Agora mover e copiar arquivo para os diretórios destino
            mover_e_copiar_arquivo(nome_arquivo, linux_download_dir, windows_download_dir, numero_contrato)

        except Exception as e:
            logger.error(f"Erro ao tentar baixar fatura {idx}: {e}", exc_info=True)
