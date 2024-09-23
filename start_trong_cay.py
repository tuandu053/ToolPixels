from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import time
import cv2
import numpy as np
import os
from time import sleep
from datetime import datetime
from random import uniform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException


class AppConfig:
    url_web = "https://play.pixels.xyz/"
    game_container_id = "game-container"
    start_game_button_xpath = "//button[contains(text(),'Start Game')]"
    login_signup_text_xpath = "//div[text()='Log In or Sign Up']"
    land_and_Bookmarks_button_xpath = "//img[@aria-label='Land and Bookmarks']/parent::button"
    go_to_Terra_Villa_button_xpath = "//button[text()='Go to Terra Villa']"
    my_Land_button_xpatch = "(//button[@class='LandAndTravel_tab__LD39V'])[2]"
    my_Land_Go_button_xpatch = "//button[text()='Go']"
    
    keys_dic_map = [[Keys.ARROW_RIGHT,1],[Keys.ARROW_DOWN,1],[Keys.ARROW_LEFT,1],[Keys.ARROW_UP,0]] 
    load_timeout = 30
    start_game_retries = 3
    login_wait_time = 60
    
    AVATAR_CONFIDENCE       = float(os.getenv('AVATAR_CONFIDENCE', 0.8))
#     AVATAR2_CONFIDENCE      = float(os.getenv('AVATAR2_CONFIDENCE', 0.8))
#    EMPTY_LAND_CONFIDENCE   = float(os.getenv('EMPTY_LAND_CONFIDENCE', 0.7))
#    SEED_CONFIDENCE         = float(os.getenv('SEED_CONFIDENCE', 0.9))
#     FULL_CONFIDENCE         = float(os.getenv('FULL_CONFIDENCE', 0.75))
#     DRY_CONFIDENCE          = float(os.getenv('DRY_CONFIDENCE', 0.75))
    
# Load environment variables from .env file (if present)
load_dotenv("config.txt")  



class GameController:
    def __init__(self, driver):
        self.driver = driver     
        self.PLANT_TYPE = os.getenv('PLANT_TYPE', "popberry")
#        self.updatePos()
        self.nhan_vat = (0,0)
        self.screenshot_size = (0,0)
        
        self.xpath_keo  = "//img[@src='"+self.getImg_item_xpath('1')+"']/parent::div"
        self.xpath_binh_tuoi = "//img[@src='"+self.getImg_item_xpath('2')+"']/parent::div"
        self.xpath_seed = "//img[@src='"+self.getImg_item_xpath('30')+"']/parent::div"
        
           
    
#===========++++=============    
    def element_exists(self, xpath):
        try:
            elements = self.driver.find_elements(By.XPATH, xpath)
            return len(elements) > 0
        except NoSuchElementException:
            return False
            
    def click_if_exists(self, xpath):
        try:
            elements = self.driver.find_elements(By.XPATH, xpath)
            if len(elements) > 0:
                elements[0].click()  # Click the first matching element
                print("Element found and clicked.")
                return True
            else:
                print("Element does not exist.")
                return False
        except NoSuchElementException:
            print("Element does not exist.")
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        
#===========++++=============        
    def toa_do_nhan_vat(self):  
        self.avatar     =   self.tim_mot_doi_tuong("avatar1", AppConfig.AVATAR_CONFIDENCE)
        self.avatar2    =   self.tim_mot_doi_tuong("avatar2", AppConfig.AVATAR_CONFIDENCE)
        
        if (self.avatar != None or self.avatar2 != None):
            if self.avatar != None:
                
                self.nhan_vat = self.adjust_coordinates(self.avatar)
            else:
                self.nhan_vat = self.adjust_coordinates(self.avatar2)
                
        print("Vị trí sau điều chỉnh của logo trên màn hình:", self.nhan_vat)


#===========++++=============   
    def tim_mot_doi_tuong(self, img_name, confidence_threshold=0.7):
        try:
            screenshot = self.driver.get_screenshot_as_png()
            template_image = cv2.imread('./source/' + img_name + '.png')
            template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
        
            screen_img = Image.open(BytesIO(screenshot))
            screen_np = np.array(screen_img)
            screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)
        
            result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
            if max_val >= confidence_threshold:
                top_left = max_loc
                template_height, template_width = template_gray.shape
                center_x = top_left[0] + template_width // 2 
                center_y = top_left[1] + template_height // 2 + 10
                center_location = (center_x, center_y)
                print("Vị trí trung tâm của đối tượng trên màn hình:", center_location)
                self.screenshot_size = screen_np.shape[1], screen_np.shape[0]
                return center_location
            else:
                print("Không tìm thấy đối tượng với độ tin cậy đủ.")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

#===========++++=============
    def tim_all_doi_tuong(self, img_name, confidence_threshold=0.7):
        try:
            screenshot = self.driver.get_screenshot_as_png()
            template_image = cv2.imread('./source/' + img_name + '.png')
            template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)

            screen_img = Image.open(BytesIO(screenshot))
            screen_np = np.array(screen_img)
            screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)

            result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= confidence_threshold)
            locations = [(int(x), int(y)) for x, y in zip(locations[1], locations[0])]

            print(f"Tìm thấy {len(locations)} vị trí:")
            for loc in locations:
                print(loc)

            self.screenshot_size = screen_np.shape[1], screen_np.shape[0]
            return locations
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

#===========++++=============
    def adjust_coordinates(self, coordinates):
        if coordinates is None:
            return None
    
        # Get the size of the visible portion of the web page
        page_size = self.driver.execute_script("return [document.documentElement.clientWidth, document.documentElement.clientHeight];")
        page_width = int(page_size[0])
        page_height = int(page_size[1])
    
        screenshot_width, screenshot_height = self.screenshot_size
    
        # Calculate the scale factors
        scale_x = page_width / screenshot_width
        scale_y = page_height / screenshot_height
    
        # Adjust the coordinates
        adjusted_x = int(coordinates[0] * scale_x)
        adjusted_y = int(coordinates[1] * scale_y)
    
        return (adjusted_x, adjusted_y)

#===========++++=============
    def getImg_item_xpath(self,num):
        try:
            element = self.driver.find_element(By.XPATH, "(//div[@class='Hud_item__YGtIC'])["+num+"]//div[@class='clickable']//img")
            # Lấy giá trị của thuộc tính 'src'
            src_value = element.get_attribute("src")
            print(f"Giá trị src là: {src_value}")
            return src_value
        except NoSuchElementException:
            print("Không tìm thấy phần tử với XPath đã cho.")
            return None
            
            
#===========++++=============           
    def click_at_coordinates(self, x, y):
        # Tạo đối tượng ActionChains
        actions = ActionChains(self.driver)
        
        # Di chuyển chuột đến vị trí mong muốn và click
        actions.move_by_offset(x, y).click().perform()
    
        # Reset vị trí chuột (tránh ảnh hưởng đến các thao tác tiếp theo)
        actions.move_by_offset(-x, -y).perform()

#===========++++=============
    def click_all_small_squares(self, character_position, square_size=32):
        
        x, y = character_position
        
        print(f"Character position: {x}, {y}")
        offsets = [
            (-square_size, -square_size), (0, -square_size), (square_size, -square_size),  # Top row
            (-square_size, 0), (0, 0), (square_size, 0),                                  # Middle row
            (-square_size, square_size), (0, square_size), (square_size, square_size)      # Bottom row
        ]
        
        window_size = self.driver.get_window_size()
        window_width = window_size['width']
        window_height = window_size['height']
        
        # Locate the body element to move from its coordinates
        game_container = self.driver.find_element(By.ID, "game-container")
        
        for offset in offsets:
            
            target_x = x + offset[0]
            target_y = y + offset[1]
            
            if 0 <= target_x <= window_width and 0 <= target_y <= window_height:
                print(f"Clicking on square at: {target_x}, {target_y}")
                self.click_at_coordinates(target_x, target_y)
                time.sleep(3)
            else:
                print(f"Target {target_x}, {target_y} is out of bounds.")


#===========++++=============   
    def move_with_arrow(self,key_arrow):
        move_duration   = 1.0
        actions = ActionChains(self.driver)
        actions.key_down(key_arrow).pause(move_duration).key_up(key_arrow).perform()
        time.sleep(move_duration)
        
        
            
#===========++++=============   
    def plantAll(self):
        #Ô đầu
        self.toa_do_nhan_vat()
        if self.click_if_exists(self.xpath_seed):
            print("Successfully clicked the element.")
        else:
            print("Could not find the element to click.")
        self.wait(1)
        self.click_all_small_squares(self.nhan_vat)
        
        #Tưới nước
        self.wait(2)
        if self.click_if_exists(self.xpath_binh_tuoi):
            print("Successfully clicked the element.")
        else:
            print("Could not find the element to click.")
        self.wait(1)
        self.click_all_small_squares(self.nhan_vat)
        
        #Các ô sau 
        for key_arrow,is_plant in AppConfig.keys_dic_map:
            self.move_with_arrow(key_arrow)
            self.wait()
            if is_plant:    
                self.toa_do_nhan_vat()
                
                #Gieo hạt
                if self.click_if_exists(self.xpath_seed):
                    print("Successfully clicked the element.")
                else:
                    print("Could not find the element to click.")
                self.wait(1)
                self.click_all_small_squares(self.nhan_vat)
                
                #Tưới nước
                self.wait(2)
                if self.click_if_exists(self.xpath_binh_tuoi):
                    print("Successfully clicked the element.")
                else:
                    print("Could not find the element to click.")
                self.wait(1)
                self.click_all_small_squares(self.nhan_vat)
            
        self.wait(2)


    
    def harvestAll(self):
        #Ô đầu
        self.toa_do_nhan_vat()
        if self.click_if_exists(self.xpath_keo):
            print("Successfully clicked the element.")
        else:
            print("Could not find the element to click.")
        self.wait(1)
        self.click_all_small_squares(self.nhan_vat)
        self.wait(2)
        
        for key_arrow in AppConfig.keys_dic_map:
            self.move_and_plant(key_arrow,is_plant)
            self.wait(1)
            self.toa_do_nhan_vat()
            if self.click_if_exists(self.xpath_keo):
                print("Successfully clicked the element.")
            else:
                print("Could not find the element to click.")
            self.wait(1)
            self.click_all_small_squares(self.nhan_vat)
            self.wait(2)
            

            
    def hold_key(self, key, duration):
        """Hold down a key for a specified duration."""
        actions = ActionChains(self.driver)
        actions.key_down(key).pause(duration).key_up(key).perform()


    def move_character_ve_goc(self, up_duration, left_duration, up_duration2):
        """Move the character by simulating arrow key presses."""
        actions = ActionChains(self.driver)
        # Move up
        actions.key_down(Keys.ARROW_UP).pause(up_duration).key_up(Keys.ARROW_UP)
        self.wait()
        # Move left
        actions.key_down(Keys.ARROW_LEFT).pause(left_duration).key_up(Keys.ARROW_LEFT) 
        self.wait()
        # Move up again
        actions.key_down(Keys.ARROW_UP).pause(up_duration2).key_up(Keys.ARROW_UP)
       
        # Move to Center
        self.wait()
        # Move righ
        actions.key_down(Keys.ARROW_RIGHT).pause(0.25).key_up(Keys.ARROW_RIGHT)
        # Move left
        self.wait()
        actions.key_down(Keys.ARROW_DOWN).pause(0.25).key_up(Keys.ARROW_DOWN)
        # Perform the actions
        actions.perform()
    


      
    def walk(self, dir, length=0.05):
        actions = ActionChains(self.driver)
        actions.key_down(dir).perform()
        self.wait(length)
        actions.key_up(dir).perform()
              
    def wait(self, length=0.01):
        sleep(uniform(length - 0.01, length + 0.01))


    def send_keys(self, keys):
        action = ActionChains(self.driver)
        action.send_keys(keys).perform()

    def log(self, msg):
        t = datetime.now().strftime('%H:%M:%S')
        print(f'[{t}] MESSAGE: {msg}')
     


        
def start_game_thread(profile_path):
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={profile_path}")

    # Initialize Chrome driver
    driver = webdriver.Chrome(options=options)
    
    try:
        # Load website URL from profile
        load_website(driver)
        time.sleep(3)
        
        if open_game(driver):
            start_playing(driver)
        else:
            print("Failed to start the game.")
    finally:
        # Quit the driver session
        driver.quit()

def load_website(driver):
    # Open the website and wait until it's fully loaded
    driver.get(AppConfig.url_web)
    WebDriverWait(driver, AppConfig.load_timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print(f"Loaded website {AppConfig.url_web}")

def open_game(driver, retries=AppConfig.start_game_retries):
    wait = WebDriverWait(driver, 20)
    for attempt in range(retries):
        try:
            condition = EC.any_of(
                EC.element_to_be_clickable((By.XPATH, AppConfig.start_game_button_xpath)),
                EC.presence_of_element_located((By.XPATH, AppConfig.login_signup_text_xpath))
            )
            element = wait.until(condition)

            if element.tag_name == 'button' and 'Start Game' in element.text:
                element.click()
                print("Clicked 'Start Game' button")
                return True
            elif element.tag_name == 'div' and 'Log In or Sign Up' in element.text:
                print("Found 'Log In or Sign Up' text, waiting for 60 seconds")
                time.sleep(AppConfig.login_wait_time)
                return False
        except Exception as e:
            print(f"Condition not met, refreshing page. Attempt {attempt + 1} of {retries}. Error: {e}")
            driver.refresh()
            time.sleep(3)
    return False

def start_playing(driver):
    wait = WebDriverWait(driver, 20)
    try:
        game_loaded = wait.until(EC.presence_of_element_located((By.ID, AppConfig.game_container_id)))

        if game_loaded:
            driver.implicitly_wait(10)
            time.sleep(10)
            print("Game loaded successfully")
            
            """
            # Example actions after game loads
            land_and_Bookmarks_button = wait.until(EC.element_to_be_clickable((By.XPATH, AppConfig.land_and_Bookmarks_button_xpath)))
            land_and_Bookmarks_button.click()
            time.sleep(1)
            print("Clicked 'land_and_Bookmarks' button")

            go_to_Terra_Villa_button = wait.until(EC.element_to_be_clickable((By.XPATH, AppConfig.go_to_Terra_Villa_button_xpath)))
            go_to_Terra_Villa_button.click()
            game_loaded = wait.until(EC.presence_of_element_located((By.ID, AppConfig.game_container_id)))
            time.sleep(5)
            print("Clicked 'Go_to_Terra_Villa_button' button")
            
            land_and_Bookmarks_button = wait.until(EC.element_to_be_clickable((By.XPATH, AppConfig.land_and_Bookmarks_button_xpath)))
            land_and_Bookmarks_button.click()
            time.sleep(1)
            print("Clicked 'land_and_Bookmarks' button")

            my_Land_button = wait.until(EC.element_to_be_clickable((By.XPATH, AppConfig.my_Land_button_xpatch)))
            time.sleep(1)
            my_Land_button.click()
            print("my_Land_button.click")
            time.sleep(1)
            my_Land_Go_button = wait.until(EC.element_to_be_clickable((By.XPATH, AppConfig.my_Land_Go_button_xpatch)))
            time.sleep(1)
            my_Land_Go_button.click()
            print("my_Land_Go_button.click()")
            time.sleep(1)
            game_loaded = wait.until(EC.presence_of_element_located((By.ID, AppConfig.game_container_id)))
            print("game_loaded")
            time.sleep(5)
            """
            
            # Example usage of GameController methods
            game_controller = GameController(driver)
            """
            game_controller.move_character_ve_goc(1.5, 3.5, 5)
            print("move_character_ve_goc executed")
            time.sleep(5)
            game_controller.move_with_distance(AppConfig.ARROW_RIGHT,30)
            time.sleep(5)
            """
    #game_controller.move_from_current_position (x1, y1)
#            game_controller.plantAll()
#            game_controller.harvestAll()
            #time.sleep(50)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    start_game_thread("đường_dẫn_profile")
