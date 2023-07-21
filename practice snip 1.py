import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By

path = r"I:\bajaj hackrx\chromedriver-win64\chromedriver.exe"
driver = webdriver.Chrome(path)

# Navigate to the Instagram post page
def navigate_to_post_page():
    url = "https://www.instagram.com/p/Cu8MR0auf9Y/"
    driver.get(url)
    time.sleep(5)

# Extract data from the Instagram post page and save to CSV
def extract_data():
    profile_name = driver.find_element(By.XPATH, '//h2[contains(@class, "BrX75")]/a').text.strip()
    location = driver.find_element(By.XPATH, '//div[contains(@class, "M30cS")]/div/span').text.strip()
    timestamp = driver.find_element(By.XPATH, '//time[contains(@class, "FH9sR")]/@datetime').get_attribute("datetime")

    # Save the data to CSV file
    with open('instagram_attributes.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Profile Name', 'Location', 'Timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'Profile Name': profile_name, 'Location': location, 'Timestamp': timestamp})

if __name__ == "__main__":
    navigate_to_post_page()
    extract_data()

    time.sleep(10)
    driver.quit()
