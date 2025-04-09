import pytest
from pywinauto import Application
import time
import psutil

def test_health_curl():

    cmder_path = r'C:\pywinauto-expandtesting_desktop\Cmder.exe'

    # Inicia o Cmder
    app = Application().start(cmder_path, create_new_console=True, wait_for_idle=False)

    # Aguarda para garantir que a janela foi aberta
    time.sleep(10)

    # Localiza o processo do ConEmu
    def find_conemu_pid():
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'ConEmu64.exe':
                return proc.info['pid']
        return None

    pid = find_conemu_pid()
    assert pid is not None, "ConEmu64.exe não encontrado. Cmder pode não ter iniciado corretamente."

    print(f"ConEmu encontrado com PID: {pid}")

    # Conecta ao processo
    app = Application().connect(process=pid)
    time.sleep(2)

    # Lista janelas para depuração
    windows = app.windows()
    assert windows, "Nenhuma janela foi encontrada pelo pywinauto."
    for win in windows:
        print(f"Found window with title: {win.window_text()}")

    # Busca janela com título correspondente ao Cmder
    terminal_window = app.window(title_re=".*Cmder.*")
    terminal_window.wait('visible', timeout=15)
    terminal_window.maximize()

    # Comando curl a ser executado
    curl_command = r'curl -X "GET" "https://practice.expandtesting.com/notes/api/health-check" -H "accept: application/json"'

    # Digita e executa
    terminal_window.type_keys(curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")

    print("Comando curl enviado com sucesso!")

    # Espera a saída aparecer (opcional)
    time.sleep(3)

    # Aqui você poderia capturar a saída da janela, se quisesse validar a resposta

