import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import time
import pandas as pd
import os
import chromedriver_autoinstaller

# Automatically install ChromeDriver
chromedriver_autoinstaller.install()

def get_end_of_month(date):
    """Get the last day of the month for a given date."""
    if date.month == 12:
        next_month = datetime.date(date.year + 1, 1, 1)
    else:
        next_month = datetime.date(date.year, date.month + 1, 1)
    return next_month - datetime.timedelta(days=1)

def extract_table_data(driver):
    """Extract table data, ensuring correct 'Category' extraction."""
    try:
        print("Extracting table data...")
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.sticky-header-table"))
        )
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header row
        data = []

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            
            # Extract "Category" column text from the <a> tag
            category_col = cols[3]
            document_link_elem = category_col.find_element(By.TAG_NAME, "a")
            document_text = document_link_elem.text.strip()  # Extract category text
            document_link = document_link_elem.get_attribute("href")  # Extract link

            # Extract headline information from the <div class="headline"> tag
            headline_div = category_col.find_element(By.CSS_SELECTOR, "div.headline")
            headline_text = headline_div.text.strip()  # Extract headline text

            # Combine both pieces of information for the 'Category' column
            combined_category = f"{document_text} - {headline_text}"

            row_data = [
                cols[0].text.strip(),  # Release Time
                cols[1].text.strip(),  # Stock Code
                cols[2].text.strip(),  # Stock Name
                combined_category,     # Category (combined: previous + headline)
                document_link          # Document Link
            ]
            data.append(row_data)

        print(f"Extracted {len(data)} records from table.")

        # Create DataFrame
        df = pd.DataFrame(data, columns=["Release Time", "Stock Code", "Stock Name", "Category", "Document Link"])

        # Convert release time to date format for filtering
        df['Release Date'] = pd.to_datetime(df['Release Time'].str.split().str[0], format='%d/%m/%Y', errors='coerce')

        # Define document classification based on date
        mask = (df['Release Date'] >= pd.Timestamp('1990-01-01')) & (df['Release Date'] <= pd.Timestamp('2007-06-25'))
        df['Document Type'] = ''
        df['Headline Category'] = 'Yes'
        df.loc[mask, 'Document Type'] = 'Yes'
        df.loc[mask, 'Headline Category'] = ''

        # Drop temporary date column
        df = df.drop(columns=['Release Date'])

        # Reorder columns
        df = df[["Release Time", "Stock Code", "Stock Name", "Document Link", "Headline Category", "Document Type", "Category"]]

        return df
    except Exception as e:
        print(f"[ERROR] Error extracting table data: {e}")
        return pd.DataFrame()

def get_load_more_info(driver):
    """Get the number of currently displayed records and total records."""
    retries = 3
    for _ in range(retries):
        try:
            load_more_container = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".component-loadmore-leftPart__container"))
            )
            text = load_more_container.text.replace(',', '').strip()
            parts = text.split()
            current_shown = int(parts[1])
            total_records = int(parts[3])
            print(f"Showing {current_shown}/{total_records} records.")
            return current_shown, total_records
        except StaleElementReferenceException:
            time.sleep(1)
        except Exception as e:
            print(f"[ERROR] Error getting load more info: {e}")
            break
    return 0, 0

def click_load_more(driver):
    """Click the 'Load More' button to load additional records."""
    retries = 3
    for _ in range(retries):
        try:
            load_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.component-loadmore__link"))
            )
            driver.execute_script("arguments[0].click();", load_more_button)
            print("Clicked 'Load More' button.")
            return True
        except StaleElementReferenceException:
            time.sleep(1)
        except Exception as e:
            print(f"Error clicking load more: {e}")
            break
    return False

# Main script
print("Starting web scraping script...")
driver = webdriver.Chrome()
url = "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=en"

max_date = datetime.date(2025, 2, 15)
current_date = datetime.date(1999, 4, 1)

os.makedirs("data", exist_ok=True)
all_data = pd.DataFrame()

while current_date <= max_date:
    end_of_month = get_end_of_month(current_date)
    if end_of_month > max_date:
        end_of_month = max_date

    from_date = current_date.strftime("%Y/%m/%d")
    to_date = end_of_month.strftime("%Y/%m/%d")

    print(f"Scraping data from {from_date} to {to_date}")

    driver.get(url)
    time.sleep(2)

    driver.execute_script(f"document.getElementById('searchDate-From').value = '{from_date}';")
    driver.execute_script(f"document.getElementById('searchDate-To').value = '{to_date}';")

    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.filter__btn-applyFilters-js.btn-blue"))
    )
    search_button.click()

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.sticky-header-table"))
        )
        print("Search results loaded.")
    except Exception as e:
        print(f"[ERROR] Results not loaded for {from_date} to {to_date}: {e}")
        current_date = end_of_month + datetime.timedelta(days=1)
        continue

    try:
        while True:
            current_shown, total_records = get_load_more_info(driver)
            if current_shown >= total_records or total_records == 0:
                break
            if not click_load_more(driver):
                break
            WebDriverWait(driver, 30).until(
                lambda d: get_load_more_info(d)[0] > current_shown
            )
    except Exception as e:
        print(f"[ERROR] Load More process interrupted: {e}")

    df = extract_table_data(driver)
    if not df.empty:
        print(f"Adding {len(df)} records to final dataset.")
        all_data = pd.concat([all_data, df], ignore_index=True)

    current_date = end_of_month + datetime.timedelta(days=1)

# Save the data to a CSV file
if not all_data.empty:
    file_path = os.path.join("data", "all_data.csv")
    
    # Convert "Stock Code" to string before saving
    all_data["Stock Code"] = all_data["Stock Code"].astype(str)
    
    all_data.to_csv(file_path, index=False)
    print(f"Data saved to {file_path}")

# Close the browser
try:
    driver.quit()
except:
    print("Driver already closed.")