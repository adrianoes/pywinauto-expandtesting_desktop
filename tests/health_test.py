from pywinauto import Application
import time
import psutil

# Caminho completo para o Cmder
cmder_path = r'C:\pywinauto-expandtesting_desktop\Cmder.exe'

# Inicia o Cmder com o /k para manter a janela aberta
app = Application().start(cmder_path, create_new_console=True, wait_for_idle=False)

# Aguarda um pouco mais para garantir que a janela foi aberta completamente
time.sleep(10)

# Função para encontrar o PID do ConEmu (que gerencia o Cmder)
def find_conemu_pid():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'ConEmu64.exe':  # Processo principal do ConEmu
            return proc.info['pid']
    return None

# Encontrar o PID do ConEmu
pid = find_conemu_pid()

if pid:
    print(f"ConEmu encontrado com PID: {pid}")
    
    # Conectar ao ConEmu usando o PID
    app = Application().connect(process=pid)

    # Aguarda um pouco para garantir que a janela foi aberta completamente
    time.sleep(2)

    # Listar todas as janelas abertas para verificar o título exato
    windows = app.windows()
    for win in windows:
        print(f"Found window with title: {win.window_text()}")

    # Usar o título exato da janela do Cmder
    # Aqui estamos assumindo que o título pode ser "Console Emulator" ou algo relacionado
    terminal_window = app.window(title_re=".*Cmder.*")

    # Aguarda até que a janela esteja visível
    terminal_window.wait('visible')

    # Maximiza a janela
    terminal_window.maximize()

    # Comando curl que queremos digitar
    curl_command = r'curl -X "GET" "https://practice.expandtesting.com/notes/api/health-check" -H "accept: application/json"'

    # Digita o comando curl na janela do Cmder
    terminal_window.type_keys(curl_command, with_spaces=True)

    # Pressiona Enter para enviar o comando
    terminal_window.type_keys("{ENTER}")

    print("Comando curl enviado com sucesso!")

else:
    print("Não foi possível encontrar o processo do ConEmu.")
