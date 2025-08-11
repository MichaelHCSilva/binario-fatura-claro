import os
import time
import shutil
import logging

logger = logging.getLogger(__name__)

# Diretório padrão do Chrome (ajuste conforme seu ambiente)
DOWNLOAD_DIR = "/home/allancdev/Downloads"

def garantir_diretorio(diretorio: str) -> None:
    """Garante que o diretório exista, cria caso não exista."""
    try:
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
            logger.info(f"Diretório criado: {diretorio}")
        else:
            logger.info(f"Diretório já existe: {diretorio}")
    except Exception as e:
        logger.error(f"Erro ao garantir diretório {diretorio}: {e}", exc_info=True)

def esperar_arquivo_download_concluido(caminho_arquivo: str, timeout: int = 60) -> bool:
    """
    Espera até que o arquivo de download esteja concluído.
    Verifica se o arquivo existe e não possui arquivos temporários do Chrome (.crdownload, .part).
    """
    tempo_espera = 0
    intervalo_checagem = 1
    logger.info(f"Aguardando arquivo: {caminho_arquivo}")
    while tempo_espera < timeout:
        try:
            # Arquivo existe e não está em download temporário
            if os.path.isfile(caminho_arquivo) and not (
                os.path.exists(caminho_arquivo + ".crdownload") or
                os.path.exists(caminho_arquivo + ".part")
            ):
                logger.info(f"Arquivo {caminho_arquivo} baixado com sucesso.")
                return True
        except Exception as e:
            logger.warning(f"Erro ao verificar arquivo {caminho_arquivo}: {e}", exc_info=True)

        time.sleep(intervalo_checagem)
        tempo_espera += intervalo_checagem

    logger.warning(f"Timeout: arquivo {caminho_arquivo} não apareceu após {timeout}s.")
    return False

def mover_e_copiar_arquivo(nome_arquivo_original: str, linux_dir: str, windows_dir: str, numero_contrato: str) -> None:
    """
    Move o arquivo da pasta padrão de download para o diretório Linux e depois copia para o diretório Windows.
    Mantém o nome original do arquivo.
    """
    origem = os.path.join(DOWNLOAD_DIR, nome_arquivo_original)
    destino_linux = os.path.join(linux_dir, nome_arquivo_original)
    destino_windows = os.path.join(windows_dir, nome_arquivo_original)

    logger.info(f"Iniciando mover/copiar para arquivo: {nome_arquivo_original}")
    logger.info(f"Caminho origem: {origem}")
    logger.info(f"Caminho destino Linux: {destino_linux}")
    logger.info(f"Caminho destino Windows: {destino_windows}")

    if esperar_arquivo_download_concluido(origem):
        try:
            garantir_diretorio(linux_dir)
            garantir_diretorio(os.path.dirname(destino_windows))

            shutil.move(origem, destino_linux)
            logger.info(f"Arquivo movido para {destino_linux}")

            shutil.copy2(destino_linux, destino_windows)
            logger.info(f"Arquivo copiado para Windows: {destino_windows}")
        except Exception as e:
            logger.error(f"Erro ao mover/copiar arquivo {nome_arquivo_original}: {e}", exc_info=True)
    else:
        logger.warning(f"Arquivo {origem} não foi baixado no diretório padrão do Chrome.")
