# PlatesMania Scraper

## Overview

This is a web scraping tool designed to extract license plate images from PlatesMania.com. It automates the process of collecting both real-world and generated plate images, categorizing them by country and plate type as displayed on the website. Each license plate image is labeled with its corresponding registration number.

## Features

* Uses SeleniumBase for handling authentication and CAPTCHA.
* Scrapes license plate numbers, generated images, and real-world images and saves them locally.
* Handles rate limiting by pausing and retrying requests.
* Organizes images into folders based on country and plate type
* Uses requests and lxml for efficient data extraction.

## Installation

1. **Clone the repository**:
   ```sh
   git clone https://github.com/krzsmal/PlatesManiaScraper.git
   cd PlatesManiaScraper
   ```

2. **Install dependencies**:
   ```sh
   pip install seleniumbase lxml
   ```

## Usage

1. **Modify the configuration file**:  
   Before running the script, edit the `config.yaml` file to ensure that only the countries you want to scrape registrations for are uncommented.  

2. **Run the script**:
    ```sh
    python scraper.py
    ```

## License

This project is open-source under the MIT License.

## Disclaimer

This project was created for educational purposes only. Web scraping may be illegal or violate the terms of service of certain websites. The author does not encourage or support unauthorized data extraction. Use this tool at your own risk.