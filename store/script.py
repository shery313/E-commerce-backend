from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def calculate_shipping(type, services, origin, destination, weight, retries=3):
    # Set up headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

    driver = webdriver.Chrome(options=chrome_options)  # Ensure you have the ChromeDriver in PATH or specify its location
    
    try:
        for attempt in range(retries):
            try:
                # Navigate to the Leopard Courier page
                driver.get('https://www.leopardscourier.com/dynamic_rate-calculator')

                # Fill out the form
                select_type = Select(driver.find_element(By.ID, 'ship-type'))  # Replace with actual ID
                select_type.select_by_visible_text(type)
                select_services = Select(driver.find_element(By.ID, 'shipResult'))  # Replace with actual ID
                select_services.select_by_visible_text(services)
                select_origin = Select(driver.find_element(By.ID, 'originCityList'))  # Replace with actual ID
                select_origin.select_by_visible_text(origin)
                select_destination = Select(driver.find_element(By.ID, 'countryList'))  # Replace with actual ID
                select_destination.select_by_visible_text(destination)
                
                # Wait for the weight input field to be visible
                weight_input = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.ID, 'from_Weight'))
                )
                weight_input.clear()
                weight_input.send_keys(weight)
                
                # Submit the form (if necessary)
                submit_button = driver.find_element(By.ID, 'submit')  # Replace with actual ID
                submit_button.click()
                
                # Wait for the results to load
                result_container = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, 'demo-container'))
                )
                
                # Extract the shipping cost
                amount_text = result_container.find_element(By.TAG_NAME, 'span').text
                
                
                return amount_text
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                # Take a screenshot for debugging
                driver.save_screenshot(f"error_screenshot_attempt_{attempt + 1}.png")
                if attempt < retries - 1:
                    time.sleep(2)  # Wait a bit before retrying
                else:
                    raise e
    
    finally:
        # Close the browser
        driver.quit()

# Example usage
# calculate_shipping('DOMESTIC', 'DETAIN', 'ISLAMABAD', 'KARACHI', '5')
