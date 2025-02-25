from seleniumbase import SB
from time import sleep
from lxml import html
import requests
import json
import yaml
import os


# Fetches an HTML page and returns an HTML element tree. Retries once if rate-limited (HTTP 429 or 503).
def get_page(url: str) -> None | html.HtmlElement:
    response = requests.get(url, headers=headers, cookies=cookies)

    if response.status_code == 429 or response.status_code == 503:
        print("Bot is being rate limited, waiting and retrying...")
        sleep(15)
        response = requests.get(url, headers=headers, cookies=cookies)

    if response.status_code != 200:
        print(f"Failed to retrieve the page: {response.url}. Status code: {response.status_code}")
        return None
    
    return html.fromstring(response.content)


# Saves an image to the specified path if it doesn't already exist.
def save_img(path: str, img: bytes) -> None:
    if not os.path.exists(path):
        with open(path, "wb") as file:
            file.write(img)
    else:
        print(f"File {path} already exists.")


if __name__ == "__main__":

    # Handle the captcha and save the cookies.
    with SB(uc=True, locale_code="en") as sb:
        sb.open("https://platesmania.com/countries")
        sb.click('//p[text()="Consent"]')
        sb.click('(//a[@href!="/"]/img/..)[1]')
        sb.uc_gui_click_captcha()
        sb.save_cookies(name="cookies.txt")
        user_agent = sb.execute_script("return navigator.userAgent;")

    # Load the cookies and the configuration.
    with open("saved_cookies/cookies.txt", "r") as file:
        cookies = json.load(file)
        cookies = {cookie["name"]: cookie["value"] for cookie in cookies}

    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    countries = config['countries']
    save_real_img = config['save_real_img']
    save_generated_img = config['save_generated_img']
    max_pages = config['max_pages']

    headers = {"User-Agent": user_agent}
    domain = "https://platesmania.com"

    plate_counter = 0

    for country in countries:
        print(f"> Country: {country}")

        ctypes = {}

        # Get available plate types for the country# Get available plate types for the country
        country_page = get_page(f"{domain}/{country}")
        plate_types = country_page.xpath("//a[contains(@href, 'typenomer')]")
        for plate_type in plate_types:
            ctypes[plate_type.text_content().strip()] = plate_type.attrib['href'].strip()[9:]

        if not ctypes:
            ctypes = {'other': 0}

        for plate_type in ctypes:
            ctype = ctypes[plate_type]

            # Create directories to store images
            if save_real_img:
                local_real_path = f"plates/{country}/{plate_type}/real"
                os.makedirs(local_real_path, exist_ok=True)

            if save_generated_img:
                local_generated_path = f"plates/{country}/{plate_type}/generated"
                os.makedirs(local_generated_path, exist_ok=True)

            print(f">> Plate type: {plate_type}")            
            page_counter = 0

            while(True):
                url = f"{domain}/{country}/gallery.php?ctype={ctype}&start={page_counter}" if page_counter > 0 else f"{domain}/{country}/gallery.php?ctype={ctype}"
                tree = get_page(url)

                if tree is None:
                    break

                plates = tree.xpath('//div[@class="panel panel-grey"]')

                if len(plates) <= 1:
                    print("No more plates found.")
                    break
                
                print(f">>> Page: {page_counter}")
                for plate in plates:
                    plate_page_id = str(plate.xpath('(.//a)[2]/@href')[0])[9:]
                    plate_page_link = f"{domain}/{country}/nomer{plate_page_id}"
                    
                    plate_page = get_page(plate_page_link)
                    plate_html_element = plate_page.xpath('//h1[@class="pull-left"]')[0]
                    plate_number = plate_html_element.text_content().strip().replace(" ", "")

                    # Get and save generated image
                    if save_generated_img:
                        generated_img_link = plate_page.xpath('(//img[@class="img-responsive center-block margin-bottom-20"])[1]')[0].attrib['src']
                        generated_img = requests.get(generated_img_link, headers=headers)
                        generated_img_path = f"{local_generated_path}/{plate_number}.png"
                        save_img(generated_img_path, generated_img.content)

                    # Get and save real-world image
                    if save_real_img:
                        real_img_page = get_page(f"{domain}/{country}/foto{plate_page_id}")
                        real_img_link = real_img_page.xpath('//img[@class="img-responsive center-block"]')[0].attrib['src']
                        real_img = requests.get(real_img_link, headers=headers)
                        real_img_path = f"{local_real_path}/{plate_number}.png"
                        save_img(real_img_path, real_img.content)

                    plate_counter += 1
                    print(f"{plate_counter}. {plate_number} {plate_page_link} {generated_img_link if save_generated_img else ''} {real_img_link if save_real_img else ''}")
                    
                page_counter += 1

                if page_counter > max_pages:
                    break

    print("Done.")