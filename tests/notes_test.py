import pytest
from pywinauto import Application
import time
import psutil
import json
import os
import glob
from faker import Faker
from tests.support import create_user, delete_json_output_file, delete_json_test_data_file, delete_user, login_user, terminate_cmder_process_tree, write_json_test_data_file


def test_crete_note():
    #start random data number
    randomData = Faker().hexify(text='^^^^^^^^^^^^')

    # Start Cmder
    cmder_path = r'Cmder.exe'        
    app = Application().start(cmder_path, create_new_console=True, wait_for_idle=False)
    time.sleep(10)
        # Find the process ID of ConEmu
    def find_conemu_pid():
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'ConEmu64.exe':
                return proc.info['pid']
        return None
    pid = find_conemu_pid()
    app = Application().connect(process=pid)
    time.sleep(2)
    terminal_window = app.window(title_re=".*Cmder.*")
    terminal_window.wait('visible', timeout=15)
    terminal_window.maximize()

    #define paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
    output_file = os.path.abspath(os.path.join(output_dir, f'output-{randomData}.json'))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    create_user(terminal_window, output_file, test_data_file)

    login_user(randomData, test_data_file, output_dir, terminal_window)

    # Lê os dados existentes do JSON
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    user_token = test_data.get("user_token")
    user_id = test_data.get("user_id")

    # Gera dados da nota com Faker
    faker = Faker()
    note_title = faker.sentence(4)
    note_description = faker.sentence(5)
    note_category = faker.random_element(elements=('Home', 'Personal', 'Work'))

    # Define o caminho para salvar a resposta do cURL
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    # Monta comando cURL para criar nota
    create_note_curl_command = f'''curl -X "POST" "https://practice.expandtesting.com/notes/api/notes" \
    -H "accept: application/json" \
    -H "x-auth-token: {user_token}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "title={note_title}&description={note_description}&category={note_category}" > "{output_file}"'''

    # Executa o comando no terminal
    terminal_window.type_keys(create_note_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Note creation cURL command sent successfully!")

    time.sleep(10)

    # Lê e processa a resposta
    with open(output_file, "r") as f:
        note_response_text = f.read().strip()

    try:
        note_response_json = json.loads(note_response_text)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da resposta de criação de nota: {e}")
        return

    # Extrai dados da resposta
    note_success = note_response_json.get("success")
    note_status = note_response_json.get("status")
    note_message = note_response_json.get("message")
    note_data = note_response_json.get("data", {})

    note_id = note_data.get("id")
    note_completed = note_data.get("completed")
    note_created_at = note_data.get("created_at")
    note_updated_at = note_data.get("updated_at")
    note_user_id_resp = note_data.get("user_id")
    note_title_resp = note_data.get("title")
    note_description_resp = note_data.get("description")
    note_category_resp = note_data.get("category")

    print(f"Note creation response: success={note_success}, status={note_status}, message='{note_message}'")

    # Assertions
    assert note_success is True, "The 'success' field is not True in note creation response."
    assert note_status == 200, f"Expected status 200 in note creation, but received: {note_status}"
    assert note_message == "Note successfully created", f"Unexpected message: {note_message}"
    assert note_id is not None, "Note ID is missing in the response."
    assert note_user_id_resp == user_id, f"User ID mismatch: expected {user_id}, got {note_user_id_resp}"
    assert note_title_resp == note_title, f"Note title mismatch: expected {note_title}, got {note_title_resp}"
    assert note_description_resp == note_description, f"Note description mismatch: expected {note_description}, got {note_description_resp}"
    assert note_category_resp == note_category, f"Note category mismatch: expected {note_category}, got {note_category_resp}"

    # Atualiza JSON com dados da nota e dados de usuário
    test_data.update({
        "user_id": user_id,
        "user_token": user_token,
        "note_id": note_id,
        "note_title": note_title,
        "note_description": note_description,
        "note_category": note_category,
        "note_completed": note_completed,
        "note_created_at": note_created_at,
        "note_updated_at": note_updated_at
    })

    with open(test_data_file, "w") as f:
        json.dump(test_data, f, indent=4)

    print("Note creation data saved successfully in JSON.")

    delete_user(randomData, test_data_file, output_dir, terminal_window)
    
    terminate_cmder_process_tree(app)

