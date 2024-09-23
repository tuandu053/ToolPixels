import concurrent.futures
import time
from pathlib import Path
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from GPMLoginApiV3 import GPMLoginApiV3  # Import your custom GPMLoginApiV3 module
from start_lam_banh import start_game_thread

URL_API = "http://127.0.0.1:19995"
async def start_profile(api, profile_id,index):
    start_result_obj = await api.start_profile_async(profile_id,index)
    if not start_result_obj:
        print(f"Failed to start profile {profile_id}: API response is None")
        return

    try:
        print(f"API response for profile {profile_id}: {start_result_obj}")
        gpm_driver_file_info = Path(start_result_obj["data"]["driver_path"])
        remote_address = start_result_obj["data"]["remote_debugging_address"]
        
        print(f"Driver Path: {gpm_driver_file_info}")
        print(f"Remote Debugging Address: {remote_address}")

        # Selenium
        chrome_service = ChromeService(str(gpm_driver_file_info))
        chrome_options = ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", remote_address)

        print(f"Initializing ChromeDriver for profile {profile_id}...")
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        
        print(f"Loading URL for profile {profile_id}...")

        start_game_thread(driver)  # Nếu bạn cần chạy start_game_thread ở đây

        await asyncio.sleep(5)  # Wait for 5 seconds between starting profiles
        
        driver.quit()
        print(f"Completed profile {profile_id}.")
        # Đóng profile sau khi hoàn thành
        await api.close_profile_async(profile_id)
    except KeyError as e:
        print(f"Error with profile {profile_id}: Missing key in API response - {e}")
    except Exception as e:
        print(f"Error with profile {profile_id}: {e}")

def read_profile_ids(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def run_profile(api, profile_id,index):
    asyncio.run(start_profile(api, profile_id,index))

def main():
    api = GPMLoginApiV3(URL_API)
    profile_ids = read_profile_ids('profiles.txt')

    while True:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for index,profile_id in enumerate(profile_ids):
                print("index:",index)
                futures.append(executor.submit(run_profile, api, profile_id,index))
                time.sleep(10)  # Wait for 5 seconds before starting the next profile

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error: {e}")

        time.sleep(21600) #Chạy lại tool sau 6 tiếng
    

if __name__ == "__main__":
    main()
