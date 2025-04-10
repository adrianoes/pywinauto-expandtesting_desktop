import pytest
from pywinauto import Application
import time
import psutil
import json
import os

def test_health_curl():
    cmder_path = r'Cmder.exe'
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
    output_file = os.path.abspath(os.path.join(output_dir, 'api_output.json'))

    # Ensure the 'resources' folder exists
    os.makedirs(output_dir, exist_ok=True)

    # Remove the previous file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)

    # Start Cmder
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

    # cURL command to fetch the health status and save output to the 'resources' folder
    curl_command = f'curl -X "GET" "https://practice.expandtesting.com/notes/api/health-check" -H "accept: application/json" > "{output_file}"'

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

    print(f"Extracted data: success={success}, status={status}, message='{message}'")

    # Assertions
    assert success is True, "The 'success' field is not True."
    assert status == 200, f"Expected status 200, but received: {status}"
    assert message == "Notes API is Running", f"Unexpected message: {message}"

    # Remove the JSON file after the test
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed the JSON file: {output_file}")

    # Close Cmder by terminating the entire process tree (including cmd.exe subprocesses)
    def terminate_process_tree(pid):
        process = psutil.Process(pid)
        for child in process.children(recursive=True):
            child.terminate()
        process.terminate()

    cmder_pid = app.process
    terminate_process_tree(cmder_pid)
    print("Cmder process and its children have been terminated.")
