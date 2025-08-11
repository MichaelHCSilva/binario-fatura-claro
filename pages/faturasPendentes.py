from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from typing import Tuple, List
import locale

# Configurar locale para português do Brasil para obter nome do mês em pt_BR
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

class FaturasPendentesPage:
    def __init__(self, driver, timeout=30):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def _obter_mes_ano_atual_e_anterior(self) -> Tuple[Tuple[str, int], Tuple[str, int]]:
        hoje = datetime.today()
        mes_atual = hoje.strftime('%B').lower()  # agora em português, ex: 'agosto'
        ano_atual = hoje.year
        mes_anterior_data = hoje.replace(day=1) - timedelta(days=1)
        mes_anterior = mes_anterior_data.strftime('%B').lower()
        ano_anterior = mes_anterior_data.year
        return (mes_atual, ano_atual), (mes_anterior, ano_anterior)

    def _normalizar_texto(self, texto: str) -> str:
        return texto.strip().lower()

    def _clicar_aba_mes(self, mes: str, ano: int) -> bool:
        # XPath ajustado para achar <li> com texto que contenha mês e ano
        xpath_aba = (
            f"//li[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{mes}') "
            f"and contains(., '{ano}')]"
        )
        try:
            print(f"Tentando localizar a aba do mês '{mes} {ano}'...")
            aba_mes = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath_aba)))

            # Scroll para o elemento (centralizado)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", aba_mes)

            # Pequena espera para garantir visibilidade/clicabilidade
            self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath_aba)))

            # Clique via JS para evitar problemas
            self.driver.execute_script("arguments[0].click();", aba_mes)

            print(f"Aba do mês '{mes} {ano}' clicada com sucesso.")

            # Esperar as faturas carregarem, elementos <li class='invoice-list-item'>
            self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "invoice-list-item")))
            return True
        except Exception as e:
            print(f"Falha ao clicar na aba do mês '{mes} {ano}': {e}")
            return False

    def _buscar_faturas_pendentes(self, mes: str, ano: int) -> List:
        try:
            faturas = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "invoice-list-item"))
            )
        except Exception as e:
            print(f"Erro ao localizar faturas na aba '{mes} {ano}': {e}")
            return []

        mes_ano_str = f"{mes} {ano}".lower()
        faturas_pendentes = []
        for fatura in faturas:
            try:
                titulo = self._normalizar_texto(
                    fatura.find_element(By.CLASS_NAME, "invoice-list-item__content-infos-text--title").text
                )
                status = self._normalizar_texto(
                    fatura.find_element(By.CLASS_NAME, "status-tag").text
                )
                if mes_ano_str in titulo and status == 'aguardando':
                    faturas_pendentes.append(fatura)
            except Exception as e:
                print(f"Erro ao verificar fatura: {e}")
        return faturas_pendentes

    def _clicar_faturas_do_mes(self, mes: str, ano: int) -> bool:
        faturas_pendentes = self._buscar_faturas_pendentes(mes, ano)
        if not faturas_pendentes:
            print(f"Nenhuma fatura pendente encontrada para {mes} {ano}.")
            return False

        for fatura in faturas_pendentes:
            try:
                titulo = self._normalizar_texto(
                    fatura.find_element(By.CLASS_NAME, "invoice-list-item__content-infos-text--title").text
                )
                botao_selecionar = fatura.find_element(By.CSS_SELECTOR, "a.mdn-Button--primary")
                
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao_selecionar)

                self.wait.until(EC.element_to_be_clickable(botao_selecionar))

                self.driver.execute_script("arguments[0].click();", botao_selecionar)
                print(f"Fatura '{titulo}' selecionada com sucesso.")
                return True
            except Exception as e:
                print(f"Falha ao clicar na fatura '{titulo}': {e}")
        return False

    def selecionar_faturas_pendentes(self) -> None:
        (mes_atual, ano_atual), (mes_anterior, ano_anterior) = self._obter_mes_ano_atual_e_anterior()
        print(f"Meses para seleção: {mes_atual} {ano_atual} e {mes_anterior} {ano_anterior}")

        # Primeiro tenta o mês atual
        if self._clicar_aba_mes(mes_atual, ano_atual):
            if self._clicar_faturas_do_mes(mes_atual, ano_atual):
                return

        # Se não achar no mês atual, tenta o mês anterior
        if self._clicar_aba_mes(mes_anterior, ano_anterior):
            if self._clicar_faturas_do_mes(mes_anterior, ano_anterior):
                return

        print("Nenhuma fatura pendente encontrada nos meses atual e anterior.")
