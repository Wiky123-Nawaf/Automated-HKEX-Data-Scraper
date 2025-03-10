
**HKEX News** is the official platform of the Hong Kong Exchanges and Clearing Limited (HKEX), providing real-time access to regulatory announcements, disclosures, and corporate filings. It serves as a crucial resource for investors, analysts, and financial professionals by offering transparent and structured financial data. The website features advanced search tools, filtering options, and categorized reports to facilitate informed investment decisions.

**Features of the Web Scraping Script**

✅ Automated Web Scraping – Extracts stock announcement data from the HKEX website dynamically over a date range.

✅ Date Range Automation – Iterates from a start date (1999) to a specified end date (2025) while handling month-end adjustments.

✅ Smart "Load More" Handling – Detects the number of loaded records and dynamically clicks the "Load More" button until all records are retrieved.

✅ Accurate Table Extraction – Extracts structured data, including release time, stock code, stock name, category, and document links.

✅ Enhanced Category Extraction – Combines category text and headline information from the extracted table for better classification.

✅ Dynamic JavaScript Execution – Interacts with the search filters using JavaScript to set date ranges and apply filters.

✅ Resilient Error Handling – Implements retries for stale element issues, missing elements, and page load failures to ensure smooth execution.

✅ CSV Data Storage – Saves extracted data into a CSV file while maintaining proper formatting, including stock codes as strings.

✅ Automated ChromeDriver Installation – Uses chromedriver_autoinstaller to ensure the correct version of ChromeDriver is installed before execution.

This script efficiently scrapes stock-related announcements, handles pagination, and ensures data integrity while managing different edge cases. 🚀

**Requirements**

1. Python
2. Selenium
3. Pandas
4. Os
5. Time
6. datetime

**Scrapping Code for HKEX Website—So You Don’t Have To! 📈🤖**

![Image](https://github.com/user-attachments/assets/fed5d9e5-e41c-4217-8b15-32918b642237)
