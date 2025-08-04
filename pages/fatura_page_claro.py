from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

class FaturaPage:
    def __init__(self, driver, timeout=25):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def selecionar_contratos(self):
        pagina = 1
        while True:
            print(f"Processando página {pagina} de contratos...")
            index = 0
            try:
                contratos = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "contract")))
                if not contratos:
                    print("Nenhum contrato encontrado nesta página.")
                    break

                while index < len(contratos):
                    try:
                        contrato = contratos[index]

                        btn_selecionar = self.wait.until(
                            lambda driver: (
                                lambda btn: btn.is_displayed() and btn.is_enabled() and btn
                            )(contrato.find_element(By.XPATH, ".//button[contains(text(), 'Selecionar')]"))
                        )

                        self.driver.execute_script("arguments[0].click();", btn_selecionar)
                        time.sleep(2)

                        self.filtrar_por_status("open")

                        if self.verificar_fatura_em_aberto():
                            self.baixar_fatura()

                        self.voltar_para_lista_de_contratos()
                        time.sleep(2)

                        index += 1
                        contratos = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "contract")))

                    except Exception as e:
                        print(f"Erro ao processar contrato na página {pagina}: {e}")
                        self.voltar_para_lista_de_contratos()
                        time.sleep(2)
                        index += 1

                if not self.tem_proxima_pagina():
                    print("Todas as páginas foram processadas.")
                    break

                self.ir_para_proxima_pagina()
                time.sleep(3)
                pagina += 1

            except Exception as e:
                print(f"Erro geral ao processar página {pagina}: {e}")
                break

    def filtrar_por_status(self, status_value="open"):
        try:
            select = Select(self.wait.until(EC.presence_of_element_located((By.ID, "status"))))
            select.select_by_value(status_value)
            time.sleep(2)
        except Exception as e:
            print(f"Erro ao filtrar por status: {e}")

    def verificar_fatura_em_aberto(self):
        try:
            faturas = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "invoice-list-item")))
            for fatura in faturas:
                status = fatura.find_element(By.CLASS_NAME, "status-tag").text.lower()
                if "em aberto" in status:
                    btn_selecionar_fatura = fatura.find_element(By.XPATH, ".//a[contains(text(), 'Selecionar')]")
                    self.driver.execute_script("arguments[0].click();", btn_selecionar_fatura)
                    time.sleep(2)
                    return True
            return False
        except Exception as e:
            print(f"Erro ao verificar fatura em aberto: {e}")
            return False

    def baixar_fatura(self):
        try:
            download_link = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-testid='download-invoice']"))
            )
            self.driver.execute_script("arguments[0].click();", download_link)
            print("Fatura em aberto baixada com sucesso.")
            time.sleep(3)
        except Exception as e:
            print(f"Erro ao baixar a fatura: {e}")

    def voltar_para_lista_de_contratos(self):
        try:
            menu = self.wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "ul.mdn-Menu-top-list > li.mdn-Menu-top-list-item-location"
            )))
            self.driver.execute_script("arguments[0].click();", menu)
            print("Retornando para lista de contratos...")
            time.sleep(2)
        except Exception as e:
            print(f"Erro ao voltar para lista de contratos: {e}")

    def tem_proxima_pagina(self):
        try:
            proximo = self.driver.find_element(By.CSS_SELECTOR, "a.mdn-Pagination-Link--next")
            return proximo.get_attribute("disabled") is None
        except Exception:
            return False

    def ir_para_proxima_pagina(self):
        try:
            proximo = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.mdn-Pagination-Link--next")))
            self.driver.execute_script("arguments[0].click();", proximo)
            print("Indo para a próxima página de contratos...")
        except Exception as e:
            print(f"Erro ao mudar para a próxima página: {e}")
