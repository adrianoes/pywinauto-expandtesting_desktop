import pytest
from pywinauto import Application
import time
import psutil
import json
import os
from faker import Faker
from tests.support import create_user, delete_json_output_file, delete_json_test_data_file, delete_user, login_user, terminate_cmder_process_tree, write_json_test_data_file


def test_crete_user():
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

    # Generate random user data using Faker
    user_name = Faker().name()
    user_email = Faker().lexify(text='??').lower() + Faker().company_email().replace("-", "")
    user_password = Faker().password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True)

    # cURL command to create a new user and save the response in the 'resources' folder
    curl_command = f'curl -X "POST" "https://practice.expandtesting.com/notes/api/users/register" ' \
                   f'-H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" ' \
                   f'-d "name={user_name}&email={user_email}&password={user_password}" > "{output_file}"'

    terminal_window.type_keys(curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("cURL command sent successfully!")

    time.sleep(10)

    with open(output_file, "r") as f:
        response_text = f.read().strip()
    try:
        response_json = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    success = response_json.get("success")
    status = response_json.get("status")
    message = response_json.get("message")
    user_id = response_json.get("data", {}).get("id")

    print(f"Extracted data: success={success}, status={status}, message='{message}', user_id={user_id}")

    # Assertions
    assert success is True, "The 'success' field is not True."
    assert status == 201, f"Expected status 201, but received: {status}"
    assert message == "User account created successfully", f"Unexpected message: {message}"
    assert user_name == response_json.get("data", {}).get("name"), "User name mismatch"
    assert user_email == response_json.get("data", {}).get("email"), "User email mismatch"

    # Save the test data in a JSON file
    test_data = {
        "user_name": user_name,
        "user_email": user_email,
        "user_password": user_password,
        "user_id": user_id
    }

    write_json_test_data_file(test_data_file, test_data)

    delete_json_output_file(output_file) 

    login_user(randomData, test_data_file, output_dir, terminal_window)

    delete_user(randomData, test_data_file, output_dir, terminal_window)
    
    terminate_cmder_process_tree(app)

def test_login_user():
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

    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    # Extract the user data from the test data file
    user_name = test_data.get("user_name")
    user_email = test_data.get("user_email")
    user_password = test_data.get("user_password")  # We read user_password even if not used yet
    user_id = test_data.get("user_id")  # Read user_id from the JSON file

    # cURL command to login the user and save the response in the 'resources' folder
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    login_curl_command = f'curl -X "POST" "https://practice.expandtesting.com/notes/api/users/login" ' \
                        f'-H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" ' \
                        f'-d "email={user_email}&password={user_password}" > "{output_file}"'

    terminal_window.type_keys(login_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Login cURL command sent successfully!")

    time.sleep(10)

    with open(output_file, "r") as f:
        login_response_text = f.read().strip()

    try:
        login_response_json = json.loads(login_response_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    login_success = login_response_json.get("success")
    login_status = login_response_json.get("status")
    login_message = login_response_json.get("message")
    user_token_from_response = login_response_json.get("data", {}).get("token")
    login_user_id = login_response_json.get("data", {}).get("id")

    print(f"Login extracted data: success={login_success}, status={login_status}, message='{login_message}', "
        f"user_id={login_user_id}, token={user_token_from_response}")

    # Assertions
    assert login_success is True, "The 'success' field is not True for login."
    assert login_status == 200, f"Expected status 200 for login, but received: {login_status}"
    assert login_message == "Login successful", f"Unexpected message for login: {login_message}"
    assert user_name == login_response_json.get("data", {}).get("name"), "User name mismatch for account deletion."
    assert user_email == login_response_json.get("data", {}).get("email"), "User email mismatch for login."
    assert user_token_from_response is not None, "Token should not be None after login."
    assert user_id == login_user_id, f"User ID mismatch: expected {user_id}, but got {login_user_id}"

    # Update the test data with the token and user_id (just in case we need them later)
    test_data.update({
        "user_token": user_token_from_response
    })

    write_json_test_data_file(test_data_file, test_data)

    delete_json_output_file(output_file)

    delete_user(randomData, test_data_file, output_dir, terminal_window)

    terminate_cmder_process_tree(app)

def test_get_user():
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

    # Lê novamente os dados do usuário (incluindo o token) do arquivo JSON
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    # Extrai as variáveis necessárias
    user_name = test_data.get("user_name")
    user_email = test_data.get("user_email")
    user_id = test_data.get("user_id")
    user_token = test_data.get("user_token")

    # Define o caminho do output file para salvar a resposta do GET
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    # cURL para obter o perfil do usuário usando o token
    get_profile_curl_command = f'curl -X "GET" "https://practice.expandtesting.com/notes/api/users/profile" ' \
                            f'-H "accept: application/json" ' \
                            f'-H "x-auth-token: {user_token}" > "{output_file}"'

    terminal_window.type_keys(get_profile_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("GET profile cURL command sent successfully!")

    time.sleep(10)

    # Lê e processa a resposta do GET
    with open(output_file, "r") as f:
        get_response_text = f.read().strip()

    try:
        get_response_json = json.loads(get_response_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from GET profile response: {e}")

    # Extração dos campos da resposta
    get_success = get_response_json.get("success")
    get_status = get_response_json.get("status")
    get_message = get_response_json.get("message")
    profile_data = get_response_json.get("data", {})

    profile_id = profile_data.get("id")
    profile_name = profile_data.get("name")
    profile_email = profile_data.get("email")

    print(f"GET Profile extracted: success={get_success}, status={get_status}, message='{get_message}', "
        f"id={profile_id}, name={profile_name}, email={profile_email}")

    # Assertions
    assert get_success is True, "The 'success' field is not True in GET profile response."
    assert get_status == 200, f"Expected status 200 in GET profile, but received: {get_status}"
    assert get_message == "Profile successful", f"Unexpected message: {get_message}"
    assert user_id == profile_id, f"User ID mismatch: expected {user_id}, got {profile_id}"
    assert user_name == profile_name, f"User name mismatch: expected {user_name}, got {profile_name}"
    assert user_email == profile_email, f"User email mismatch: expected {user_email}, got {profile_email}"

    # Cleanup do arquivo de resposta
    delete_json_output_file(output_file)

    delete_user(randomData, test_data_file, output_dir, terminal_window)

    terminate_cmder_process_tree(app)

def test_update_user():
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

    # Lê novamente os dados do usuário (incluindo o token) do arquivo JSON
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    # Extrai as variáveis necessárias
    user_email = test_data.get("user_email")
    user_id = test_data.get("user_id")
    user_token = test_data.get("user_token")

    updated_name = Faker().name()
    updated_phone = Faker().bothify(text='############')
    updated_company = Faker().company()[:24]

    # Define o caminho do output file para salvar a resposta do PATCH
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    # Comando cURL para atualizar o perfil
    update_profile_curl_command = f'curl -X "PATCH" "https://practice.expandtesting.com/notes/api/users/profile" ' \
                                f'-H "accept: application/json" ' \
                                f'-H "x-auth-token: {user_token}" ' \
                                f'-H "Content-Type: application/x-www-form-urlencoded" ' \
                                f'-d "name={updated_name}&phone={updated_phone}&company={updated_company}" > "{output_file}"'

    terminal_window.type_keys(update_profile_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("PATCH profile cURL command sent successfully!")

    time.sleep(10)

    # Lê e processa a resposta do PATCH
    with open(output_file, "r") as f:
        patch_response_text = f.read().strip()

    try:
        patch_response_json = json.loads(patch_response_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from PATCH profile response: {e}")

    # Extração dos campos da resposta
    patch_success = patch_response_json.get("success")
    patch_status = patch_response_json.get("status")
    patch_message = patch_response_json.get("message")
    updated_data = patch_response_json.get("data", {})

    updated_id_resp = updated_data.get("id")
    updated_name_resp = updated_data.get("name")
    updated_email_resp = updated_data.get("email")
    updated_phone_resp = updated_data.get("phone")
    updated_company_resp = updated_data.get("company")

    print(f"PATCH Profile extracted: success={patch_success}, status={patch_status}, message='{patch_message}', "
        f"id={updated_id_resp}, name={updated_name_resp}, email={updated_email_resp}, "
        f"phone={updated_phone_resp}, company={updated_company_resp}")

    # Assertions
    assert patch_success is True, "The 'success' field is not True in PATCH profile response."
    assert patch_status == 200, f"Expected status 200 in PATCH profile, but received: {patch_status}"
    assert patch_message == "Profile updated successful", f"Unexpected message: {patch_message}"
    assert user_id == updated_id_resp, f"User ID mismatch: expected {user_id}, got {updated_id_resp}"
    assert user_email == updated_email_resp, f"User email mismatch: expected {user_email}, got {updated_email_resp}"
    assert updated_name == updated_name_resp, f"Name mismatch: expected {updated_name}, got {updated_name_resp}"
    assert updated_phone == updated_phone_resp, f"Phone mismatch: expected {updated_phone}, got {updated_phone_resp}"
    assert updated_company == updated_company_resp, f"Company mismatch: expected {updated_company}, got {updated_company_resp}"

    # Cleanup do arquivo de resposta
    delete_json_output_file(output_file)

    delete_user(randomData, test_data_file, output_dir, terminal_window)

    terminate_cmder_process_tree(app)

def test_update_user_password():
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

    # Lê novamente os dados do usuário (incluindo o token) do arquivo JSON
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    # Extrai as variáveis necessárias
    user_token = test_data.get("user_token")
    current_password = test_data.get("user_password")
    
    new_password = Faker().password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True)

    # Define o caminho do output file para salvar a resposta da troca de senha
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    # Comando cURL para troca de senha
    change_password_curl_command = f'curl -X "POST" "https://practice.expandtesting.com/notes/api/users/change-password" ' \
                                f'-H "accept: application/json" ' \
                                f'-H "x-auth-token: {user_token}" ' \
                                f'-H "Content-Type: application/x-www-form-urlencoded" ' \
                                f'-d "currentPassword={current_password}&newPassword={new_password}" > "{output_file}"'

    terminal_window.type_keys(change_password_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Password change cURL command sent successfully!")

    time.sleep(10)

    # Lê e processa a resposta da troca de senha
    with open(output_file, "r") as f:
        password_response_text = f.read().strip()

    try:
        password_response_json = json.loads(password_response_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from password change response: {e}")

    # Extração dos campos da resposta
    password_change_success = password_response_json.get("success")
    password_change_status = password_response_json.get("status")
    password_change_message = password_response_json.get("message")

    print(f"Password change response: success={password_change_success}, status={password_change_status}, message='{password_change_message}'")

    # Assertions
    assert password_change_success is True, "The 'success' field is not True in password change response."
    assert password_change_status == 200, f"Expected status 200 in password change, but received: {password_change_status}"
    assert password_change_message == "The password was successfully updated", f"Unexpected message: {password_change_message}"

    # Cleanup do arquivo de resposta
    delete_json_output_file(output_file)

    delete_user(randomData, test_data_file, output_dir, terminal_window)

    terminate_cmder_process_tree(app)

def test_logout_user():
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

    # Lê novamente os dados do usuário (incluindo o token) do arquivo JSON
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    # Extrai o token do usuário
    user_token = test_data.get("user_token")

    # Define o caminho do output file para salvar a resposta do logout
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    # Comando cURL para logout
    logout_curl_command = f'curl -X "DELETE" "https://practice.expandtesting.com/notes/api/users/logout" ' \
                        f'-H "accept: application/json" ' \
                        f'-H "x-auth-token: {user_token}" > "{output_file}"'

    terminal_window.type_keys(logout_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Logout cURL command sent successfully!")

    time.sleep(10)

    # Lê e processa a resposta do logout
    with open(output_file, "r") as f:
        logout_response_text = f.read().strip()

    try:
        logout_response_json = json.loads(logout_response_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from logout response: {e}")

    # Extração dos campos da resposta
    logout_success = logout_response_json.get("success")
    logout_status = logout_response_json.get("status")
    logout_message = logout_response_json.get("message")

    print(f"Logout response: success={logout_success}, status={logout_status}, message='{logout_message}'")

    # Assertions
    assert logout_success is True, "The 'success' field is not True in logout response."
    assert logout_status == 200, f"Expected status 200 in logout, but received: {logout_status}"
    assert logout_message == "User has been successfully logged out", f"Unexpected message: {logout_message}"

    # Cleanup do arquivo de resposta
    delete_json_output_file(output_file)

    #login again to grab a new token and delete the user
    login_user(randomData, test_data_file, output_dir, terminal_window)

    delete_user(randomData, test_data_file, output_dir, terminal_window)

    terminate_cmder_process_tree(app)

def test_delete_user():
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

    # Read the user token from the saved JSON file
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    user_token = test_data["user_token"]  # Directly getting the user token without checking for existence

    # cURL command to login the user and save the response in the 'resources' folder
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    # cURL command to delete the user account using the user token
    delete_account_command = f'curl -X "DELETE" "https://practice.expandtesting.com/notes/api/users/delete-account" -H "accept: application/json" -H "x-auth-token: {user_token}" > "{output_file}"'
    
    # Send the cURL command to the terminal to delete the account
    terminal_window.type_keys(delete_account_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Delete account cURL command sent successfully!")

    time.sleep(10)  # Wait for the response to come back

    # Read the response from the output file
    with open(output_file, "r") as f:
        delete_response_text = f.read().strip()

    # Parse the response JSON
    delete_response_json = json.loads(delete_response_text)

    # Extract response details
    delete_success = delete_response_json.get("success")
    delete_status = delete_response_json.get("status")
    delete_message = delete_response_json.get("message")

    print(f"Delete response data: success={delete_success}, status={delete_status}, message='{delete_message}'")

    # Assertions for account deletion
    assert delete_success is True, "The 'success' field is not True."
    assert delete_status == 200, f"Expected status 200, but received: {delete_status}"
    assert delete_message == "Account successfully deleted", f"Unexpected message: {delete_message}"

    delete_json_test_data_file(test_data_file)

    delete_json_output_file(output_file)

    terminate_cmder_process_tree(app)

   