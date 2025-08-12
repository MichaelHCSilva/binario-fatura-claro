#faturaClaro.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.contractClaro import ContratoCard

class FaturaPage:
    def __init__(self, driver, timeout=30):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def _aguardar_renderizacao_contratos(self):
        """
        Aguarda até que todos os contratos tenham texto visível (evita elementos vazios).
        """
        print("Aguardando renderização completa dos contratos...")
        self.wait.until(
            lambda d: all(
                el.text.strip() != "" 
                for el in d.find_elements(By.CLASS_NAME, "contract")
            )
        )
        print("Todos os contratos possuem texto carregado.")

    def selecionar_contrato_ativo(self):
        """
        Seleciona o primeiro contrato ativo (não encerrado) encontrado.
        """
        try:
            print("Aguardando a página de contratos carregar...")
            contratos_elements = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "contract"))
            )

            # Espera extra para garantir que o texto de todos contratos foi carregado
            self._aguardar_renderizacao_contratos()

            print(f"Encontrados {len(contratos_elements)} contratos.")

            for i, contrato_element in enumerate(contratos_elements, start=1):
                card = ContratoCard(self.driver, contrato_element)

                if card.esta_encerrado():
                    print(f"Verificação de 'Contrato encerrado': True")
                    print(f"Contrato {i} encerrado. Pulando...")
                    continue

                print(f"Verificação de 'Contrato encerrado': False")
                print(f"Contrato {i} é ativo.")
                if card.clicar_selecionar():
                    print("Contrato ativo selecionado com sucesso.")
                    return True
                else:
                    print(f"Falha ao selecionar contrato {i}. Pulando...")

            print("Nenhum contrato ativo foi encontrado.")
            return False
        except Exception as e:
            print(f"Erro ao selecionar contratos: {e}")
            return False
