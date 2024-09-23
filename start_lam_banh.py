from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import time
import cv2
import numpy as np
import os
import sys
from time import sleep
from datetime import datetime
from random import uniform
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path

class AppConfig:
    url_web = "https://play.pixels.xyz/"
    game_container_id = "game-container"
    start_game_button_xpath = "//button[contains(text(),'Start Game')]"
    login_signup_text_xpath = "//div[text()='Log In or Sign Up']"
    land_and_Bookmarks_button_xpath = "//img[@aria-label='Land and Bookmarks']/parent::button"
    go_to_Terra_Villa_button_xpath = "//button[text()='Go to Terra Villa']"
    my_Land_button_xpatch = "(//button[@class='LandAndTravel_tab__LD39V'])[2]"
    my_Land_Go_button_xpatch = "//button[text()='Go']"
    
    #banh_xpath = "//span[text()='Popberry Pie']/parent::div"
    banh_xpath = "//div[contains(@class,'Crafting_craftingRecipeItem')]//span[text()='Popberry Pie']"
    button_Create_xpath = "//button[@type='button' and not(@disabled)]//span[text()='Create']"
    button_In_Pregress_xpath = "//button[@type='button']//span[text()='In Progress']"
    button_X_xpath = "//img[@src='https://d31ss916pli4td.cloudfront.net/game/ui/crafting/crafting_exitbutton.png']/parent::button"
    
    
#    time_move_right_array = [.85,1.9,3.5,1.9] 
    time_move_right_array = [.85,1.9]
    load_timeout = 30
    start_game_retries = 3
    login_wait_time = 60
    
    AVATAR_CONFIDENCE       = float(os.getenv('AVATAR_CONFIDENCE', 0.8))

class GameController:
    def __init__(self, driver):
        self.driver = driver     
        self.toa_do_nhan_vat = (0,0)
        self.screenshot_size = (0,0)
        
        #self.go_nhom_lo_xpath  = "//img[@src='"+self.getImg_item_xpath('1')+"']/parent::div"
        self.go_nhom_lo_xpath  = "(//div[contains(@class,'Hud_item')])[1]//div[@class='clickable']"
        self.nang_luong_xpath = "//span[contains(@class,'Hud_energytext')]"
        self.thoat_bot = False
        self.remake_bot = False

#===========++++=============  
    def get_numeric_value_from_element(self, xpath):
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            value = element.text.strip()
            
            # Loại bỏ các ký tự không phải số và chuyển đổi giá trị thành float
            numeric_value = float(value.replace(',', ''))
            return numeric_value
        except NoSuchElementException:
            print("Không tìm thấy phần tử với XPath đã cho.")
            return None
        except ValueError:
            print("Không thể chuyển đổi giá trị thành float.")
            return None
          
    def element_exists(self, xpath):
        try:
            self.driver.find_element(By.XPATH, xpath)
            return True
        except NoSuchElementException:
            return False
    
    
    def click_if_exists(self, xpath):
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            element.click()  # Click the first matching element
            print("Element found and clicked.")
            return True
        except NoSuchElementException:
            print("Element does not exist.")
            self.thoat_bot = True
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            self.thoat_bot = True
            return False
        
#===========++++=============        
    def lay_toa_do_nhan_vat(self):  
        self.avatar     =   self.tim_mot_doi_tuong("avatar1", AppConfig.AVATAR_CONFIDENCE)
        self.avatar2    =   self.tim_mot_doi_tuong("avatar2", AppConfig.AVATAR_CONFIDENCE)
        
        if (self.avatar != None or self.avatar2 != None):
            if self.avatar != None:
                
                self.toa_do_nhan_vat = self.adjust_coordinates(self.avatar)
            else:
                self.toa_do_nhan_vat = self.adjust_coordinates(self.avatar2)
                
        print("Vị trí sau điều chỉnh của logo trên màn hình:", self.toa_do_nhan_vat)


#===========++++=============   
    def tim_mot_doi_tuong(self, img_name, confidence_threshold=0.7):
        try:
            screenshot = self.driver.get_screenshot_as_png()
            template_image = cv2.imread('./source/' + img_name + '.png')
            template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
        
            screen_img = Image.open(BytesIO(screenshot))
            screen_np = np.array(screen_img)
            screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)
            
            # screenshot_folder = Path('screenshots')
            # screenshot_folder.mkdir(parents=True, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại

            # # Tên tập tin screenshot
            # screenshot_file = screenshot_folder / 'example.png'

            # # Lưu screenshot vào tập tin
            # with open(screenshot_file, 'wb') as f:
            #     f.write(screenshot)

            result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
            if max_val >= confidence_threshold:
                top_left = max_loc
                template_height, template_width = template_gray.shape
                center_x = top_left[0] + template_width // 2 
                center_y = top_left[1] + template_height // 2
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
        print("page size:",page_size)
        print("page size:",self.screenshot_size)
        screenshot_width, screenshot_height = self.screenshot_size
    
        # Calculate the scale factors
        scale_x = page_width / screenshot_width
        scale_y = page_height / screenshot_height
    
        # Adjust the coordinates
        adjusted_x = int(coordinates[0] * scale_x)
        adjusted_y = int(coordinates[1] * scale_y)
    
        return (adjusted_x, adjusted_y)

#===========++++=============

    def getImg_item_xpath(self, num):
        try:
            element = self.driver.find_element(By.XPATH, f"(//div[@class='Hud_item__YGtIC'])[{num}]//div[@class='clickable']//img")
            # Lấy giá trị của thuộc tính 'src'
            src_value = element.get_attribute("src")
            if src_value is not None:
                print(f"Giá trị src là: {src_value}")
                return src_value
            else:
                print("Thuộc tính 'src' không tồn tại.")
                return None
        except NoSuchElementException:
            print("Hết Gỗ Đốt")
            return None

            
#===========++++=============           
    def click_at_coordinates(self, x, y):
        print("click_at_coordinates start")
        x = self.generate_random_float(x)
        y = self.generate_random_float(y)
        
        actions = ActionChains(self.driver)
        # Di chuyển chuột đến vị trí mong muốn và click
        actions.move_by_offset(x, y).click().perform()
        
        # Reset vị trí chuột (tránh ảnh hưởng đến các thao tác tiếp theo)
        actions.move_by_offset(-x, -y).perform()
        print("click_at_coordinates end")
        

#===========++++=============              
    def hold_key(self, key, duration):
        """Hold down a key for a specified duration."""
        actions = ActionChains(self.driver)
        actions.key_down(key).pause(duration).key_up(key).perform()


#===========B1=============  
    def move_character_ve_nha(self, up_duration, right_duration, up_duration2):
        """Move the character by simulating arrow key presses."""
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.element_to_be_clickable((By.XPATH, AppConfig.land_and_Bookmarks_button_xpath)))
        self.wait(2)
        actions = ActionChains(self.driver)
        # Move up
        actions.key_down(Keys.ARROW_UP).pause(up_duration).key_up(Keys.ARROW_UP)
        self.wait()
        # Move left
        actions.key_down(Keys.ARROW_RIGHT).pause(right_duration).key_up(Keys.ARROW_RIGHT) 
        self.wait()
        actions.key_down(Keys.ARROW_LEFT).pause(0.5).key_up(Keys.ARROW_LEFT) 
        self.wait()
        # Move up again
        actions.key_down(Keys.ARROW_UP).pause(up_duration2).key_up(Keys.ARROW_UP)
        self.wait()
        # Move righ
        actions.perform()
        self.wait(5)
        self.move_into_home_and_make_cakes()
        
#===========B2=============  
    def move_into_home_and_make_cakes(self):
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.element_to_be_clickable((By.XPATH, AppConfig.land_and_Bookmarks_button_xpath)))
        self.wait(2)
        actions = ActionChains(self.driver)
        actions.key_down(Keys.ARROW_UP).pause(1.5).key_up(Keys.ARROW_UP)
        #self.wait()
        actions.key_down(Keys.ARROW_LEFT).pause(5).key_up(Keys.ARROW_LEFT)
        self.wait()
        actions.perform()

        while self.thoat_bot == False:
            if self.kiem_tra_nang_luong(actions):
                self.move_o_lam_banh(actions)
            else:
                self.thoat_bot = True
        self.wait(3)
                   
    def kiem_tra_nang_luong(self, actions):
        try:
            nang_luong_value = self.get_numeric_value_from_element(self.nang_luong_xpath)
            print("nang luong con lai:", nang_luong_value)
            
            if nang_luong_value is not None:
                if nang_luong_value < 50:
                    print("Giá trị nhỏ hơn 50, dừng vòng lặp.")
                    self.thoat_bot = True
                    return False  # Trả về False để dừng vòng lặp ngoài
                else:
                    return True  # Trường hợp bằng 50, tiếp tục vòng lặp
            else:
                print("Không thể lấy giá trị float từ phần tử.")
                self.thoat_bot = True
                return False  # Trả về False để dừng vòng lặp ngoài

        except WebDriverException as e:
            print(f"Gặp vấn đề: {e}")
            return False  # Trả về False để dừng vòng lặp ngoài

#===========B3=============  
    def move_o_lam_banh(self,actions):
        for index_time, time_move in enumerate(AppConfig.time_move_right_array):
            actions.key_down(Keys.ARROW_RIGHT).pause(time_move).key_up(Keys.ARROW_RIGHT).perform()
            self.wait(0.5)
            if self.kiem_tra_nang_luong(actions):
                self.nhom_lo_lam_banh_9_o(index_time)
                self.wait(3)
            else:
                self.thoat_bot = True

        actions.key_down(Keys.ARROW_LEFT).pause(3).key_up(Keys.ARROW_LEFT).perform()
        self.wait(1)
            
    
#===========B4=============  
    def nhom_lo_lam_banh_9_o(self,index_time):
        
        self.lay_toa_do_nhan_vat() 
        self.wait(0.5) 
        x_character,y_character = self.toa_do_nhan_vat
        if index_time == 0 or index_time == 1:
            self.click_all_small_squares((x_character,y_character-5))
        else:
            self.click_6_o_small_squares((x_character,y_character-5))
        
#===========++++=============          
#     def click_nhom_lo(self):
#         if self.click_if_exists(self.go_nhom_lo_xpath):
#             print("Successfully clicked the element.")
#         else:
#             print("Could not find the element to click.")


#===========++++=============
    # def click_6_o_small_squares(self, character_position, square_size=64.0):
        
    #     x, y = character_position
        
    #     square_size = (self.adjust_coordinates((0,64)))[1]
        
    #     print(f"Character position: {x}, {y} and square size: {square_size}")
    #     offsets = [
    #         (-square_size, 0), (0, 0), (square_size, 0),                                  # Middle row
    #         (-square_size, square_size), (0, square_size), (square_size, square_size)      # Bottom row
    #     ]
        
    #     window_size = self.driver.get_window_size()
    #     window_width = window_size['width']
    #     window_height = window_size['height']
        
    #     # Locate the body element to move from its coordinates
    #     game_container = self.driver.find_element(By.ID, "game-container")
        
    #     for offset in offsets:
            
    #         target_x = x + offset[0]
    #         target_y = y + offset[1]
            
    #         if 0 <= target_x <= window_width and 0 <= target_y <= window_height:
    #             print(f"Clicking on square at: {target_x}, {target_y}")
    #             self.click_at_coordinates(target_x, target_y)
    #             self.wait(0.3)
    #             self.click_at_coordinates(target_x, target_y)
    #             self.wait(0.3)
    #             if self.element_exists("//div[text()='Cooking']"):
    #                 self.wait(0.2)
    #                 self.lam_banh() 
    #             elif self.click_if_exists(self.go_nhom_lo_xpath):
    #                 self.wait(0.3)
    #                 self.click_at_coordinates(target_x, target_y)
    #                 self.wait(0.3)
                    
    #                 actions = ActionChains(self.driver)
    #                 actions.send_keys(Keys.ESCAPE).perform()
    #                 self.wait(0.3)
    #                 self.click_at_coordinates(target_x, target_y)
    #                 self.wait(0.3)
    #                 self.lam_banh() 
    #             else:
    #                 self.wait(0.2)
    #                 self.thoat_bot = True
    #                 break

    #         else:
    #             print(f"Target {target_x}, {target_y} is out of bounds.")
                        
#===========B5=============
    def click_all_small_squares(self, character_position, square_size=51.0):
        
        x, y = character_position
        
        square_size = (self.adjust_coordinates((0,51)))[1]
        
        print(f"Character position: {x}, {y} and square size: {square_size}")
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
            
            if self.thoat_bot == True:
                print('Thoat vong lap')
                break
            elif 0 <= target_x <= window_width and 0 <= target_y <= window_height:
                print(f"Clicking on square at: {target_x}, {target_y}")
                self.click_at_coordinates(target_x, target_y)
                self.wait(0.15)
                self.click_at_coordinates(target_x, target_y)
                self.wait(0.3)
                if self.element_exists("//div[text()='Cooking']"):
                    print("Có Cooking")
                    self.wait(0.1)
                    self.lam_banh()
                    self.wait(0.2)
                elif self.click_if_exists(self.go_nhom_lo_xpath):
                    print("Có Gỗ")
                    self.wait(0.15)
                    self.click_at_coordinates(target_x, target_y)
                    self.wait(0.15)
                    actions = ActionChains(self.driver)
                    actions.send_keys(Keys.ESCAPE).perform()
                    self.wait(0.15)
                    self.click_at_coordinates(target_x, target_y)
                    self.wait(0.2)
                    self.lam_banh()
                    self.wait(0.2)
                else:
                    self.wait(0.1)
                    self.thoat_bot = True
            else:
                print(f"Target {target_x}, {target_y} is out of bounds.")
                self.thoat_bot = True
                




#===========B6============= 
    def lam_banh(self): 
        if self.element_exists(AppConfig.button_In_Pregress_xpath):
            self.wait(0.5)
        else:
            if self.click_if_exists(AppConfig.banh_xpath):
                print("Successfully clicked the element.")
            else:
                print("Could not find the element to click.")
                self.thoat_bot = True 
            self.wait(0.5)
        
            if self.click_if_exists(AppConfig.button_Create_xpath):
                print("Successfully clicked the element.")
            else:
                print("Could not find the element to click.")
                self.thoat_bot = True
                
            self.wait(0.8)
        
        
        if self.click_if_exists(AppConfig.button_X_xpath):
            print("Successfully clicked the element.")
        else:
            print("Could not find the element to click.")
            self.thoat_bot = True
            
        self.wait(0.5)

#===========++++=============  
    
    def generate_random_float(self,x):
        random_float = random.uniform(0.1, 1)
        return x + random_float
    
    def wait(self, length=0.01):
        sleep(uniform(length - 0.01, length + 0.01))
    
    def time_rand(self, length=0.01):
        return uniform(length - 0.01, length + 0.01)

    def send_keys(self, keys):
        action = ActionChains(self.driver)
        action.send_keys(keys).perform()

    def log(self, msg):
        t = datetime.now().strftime('%H:%M:%S')
        print(f'[{t}] MESSAGE: {msg}')
     

#===========Start_BOT=============  
        
# def start_game_thread(profile_path):
#     options = webdriver.ChromeOptions()
#     options.add_argument(f"--user-data-dir={profile_path}")
# 
#     # Initialize Chrome driver
#     driver = webdriver.Chrome(options=options)
#     
#     try:
#         # Load website URL from profile
#         load_website(driver)
#         time.sleep(3)
#         
#         if open_game(driver):
#             start_playing(driver)
#         else:
#             print("Failed to start the game.")
#     finally:
#         # Quit the driver session
#         driver.quit()
        
def start_game_thread(driver):
    try:
        # Load website URL from profile 
        if open_game(driver):
            start_playing(driver)
        else:
            print("Failed to start the game.")
    finally:
        # Quit the driver session
        driver.quit()

def open_game(driver, retries = AppConfig.start_game_retries):
    
    driver.get(AppConfig.url_web)
    WebDriverWait(driver, AppConfig.load_timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print(f"Loaded website {AppConfig.url_web}")
    time.sleep(3)
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
            time.sleep(15)
            print("Game loaded successfully")


            game_controller = GameController(driver)
        
            # Example actions after game loads
            land_and_Bookmarks_button = wait.until(EC.element_to_be_clickable((By.XPATH, AppConfig.land_and_Bookmarks_button_xpath)))
            land_and_Bookmarks_button.click()
            game_controller.wait(1)
            print("Clicked 'land_and_Bookmarks' button")

            go_to_Terra_Villa_button = wait.until(EC.element_to_be_clickable((By.XPATH, AppConfig.go_to_Terra_Villa_button_xpath)))
            game_controller.wait(1)
            go_to_Terra_Villa_button.click()
            game_loaded = wait.until(EC.presence_of_element_located((By.ID, AppConfig.game_container_id)))
            game_controller.wait(8)
            print("Clicked 'Go_to_Terra_Villa_button' button")
            
            land_and_Bookmarks_button = wait.until(EC.element_to_be_clickable((By.XPATH, AppConfig.land_and_Bookmarks_button_xpath)))
            game_controller.wait(1)
            land_and_Bookmarks_button.click()
            game_controller.wait(1.5)
            print("Clicked 'land_and_Bookmarks' button")

            my_Land_button = wait.until(EC.element_to_be_clickable((By.XPATH, AppConfig.my_Land_button_xpatch)))
            game_controller.wait(1)
            my_Land_button.click()
            
            game_controller.wait(1.5)
            print("my_Land_button.click")
            
            my_Land_Go_button = wait.until(EC.element_to_be_clickable((By.XPATH, AppConfig.my_Land_Go_button_xpatch)))
            game_controller.wait(1)
            my_Land_Go_button.click()
            game_controller.wait(1.5)
            print("my_Land_Go_button.click()")

            wait.until(EC.element_to_be_clickable((By.XPATH, AppConfig.land_and_Bookmarks_button_xpath)))
            print("game_loaded")
            game_controller.wait(3)
            
            
            # Example usage of GameController methods
            game_controller.move_character_ve_nha(2.5,3.2,4.5)
            game_controller.wait(5)
            
    except Exception as e:
        print(f"An error occurred: {e}")


