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

   