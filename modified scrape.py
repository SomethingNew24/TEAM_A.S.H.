import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login_to_mouthshut(username, password):
    # Start the Chrome WebDriver
    driver = webdriver.Chrome()

    try:
        # Open the login page
        driver.get("https://www.mouthshut.com")
        driver.find_element(By.ID, "sign-in").click()

        # Wait for the email input field to be visible
        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "loginId"))
        )

        # Enter username and password and submit the form
        email_input.send_keys(username)
        driver.find_element(By.ID, "pwd").send_keys(password)
        driver.find_element(By.ID, "btnAjax_Login").click()

        # Wait for the login to complete (you may need to adjust the wait time based on your internet speed)
        time.sleep(5)

        return driver
    except Exception as e:
        print("Error during login:", e)
        driver.quit()
        return None

def extract_data(driver, url):
    try:
        # Open the URL
        driver.get(url)

        # Find all review articles
        review_articles = driver.find_elements(By.XPATH, "//div[@id='dvreview-listing']/div[@class='row review-article']")

        # Store the data in a list of dictionaries
        data_list = []
        for review_article in review_articles:
            # Find the comment
            comment_element = review_article.find_element(By.XPATH, ".//div[@class='more reviewdata']/p")
            comment = comment_element.text.strip()

            # Find the user profile link
            user_profile_link_element = review_article.find_element(By.XPATH, ".//div[@class='user-ms-name']/a")
            user_profile_link = user_profile_link_element.get_attribute("href")

            # Find the stars count for this review
            stars_element = review_article.find_elements(By.XPATH, ".//div[@class='rating']//i[@class='icon-rating rated-star']")
            stars_count = len(stars_element)

            data_list.append({"Comment": comment, "User Profile Link": user_profile_link, "Stars": stars_count})

        return data_list

    except Exception as e:
        print("Error during data extraction:", e)
        return []

def save_to_csv(data_list, file_name):
    # Save the data to a CSV file
    with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Comment", "User Profile Link", "Stars"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in data_list:
            writer.writerow(data)

if __name__ == "__main__":
    # Input your MouthShut username and password
    username = input("Enter your MouthShut email: ")
    password = input("Enter your MouthShut password: ")

    # List of URLs of the pages you want to scrape
    urls = [
        "https://www.mouthshut.com/product-reviews/Max-Life-Insurance-reviews-925022894-page-5",
        "https://www.mouthshut.com/product-reviews/Max-Life-Insurance-reviews-925022894",
        "https://www.mouthshut.com/product-reviews/Max-Life-Insurance-reviews-925022894-page-2",
        "https://www.mouthshut.com/product-reviews/Max-Life-Insurance-reviews-925022894-page-3",
        "https://www.mouthshut.com/product-reviews/Max-Life-Insurance-reviews-925022894-page-4",
        "https://www.mouthshut.com/product-reviews/Max-Life-Insurance-reviews-925022894-page-6",
        # Add more URLs here as needed
    ]

    # File name to save the CSV data
    file_name = "lead_gen.csv"

    # Login to MouthShut
    driver = login_to_mouthshut(username, password)

    if driver:
        # Create an empty list to store data from multiple pages
        data_list = []

        # Iterate through each URL and extract data
        for url in urls:
            data_list.extend(extract_data(driver, url))

        # Save the combined data to CSV
        save_to_csv(data_list, file_name)

        # Close the browser window
        driver.quit()
