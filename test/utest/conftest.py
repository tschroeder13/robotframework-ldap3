# from time import sleep

import pytest, subprocess
from pathlib import Path

@pytest.fixture(scope="module")
def mokapi():
    """Fixture to run Mokapi."""
    # MOKAPI_PATH = "D:\\idmHelpers\\PortableApps\\mokapi_v0.15.0_windows_amd64\\mokapi.exe"  # Replace with the actual path to Mokapi
    # CWD = Path.cwd()
    # try:
    #     mokapi = Path(MOKAPI_PATH)
    #     # Command to run Mokapi
    #     command = [mokapi, 
    #                "--providers-file-filename",
    #                CWD / "test" / "mocks" / "ldap.yaml",]
        
    #     # Execute the command
    #     # process = subprocess.run(command, check=True, capture_output=True, text=True)
    #     process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     yield process
    #     process.terminate()

    # except Exception as e:
    #     print(f"An error occurred: {e}")
