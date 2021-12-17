import config_file, requests
from selenium import webdriver
from bs4 import BeautifulSoup as BS
from tqdm import tqdm
from os import listdir, mkdir, path


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('user-agent={0}'.format('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'))
    options.add_argument('log-level=3')
    options.add_argument('--no-sandbox')
    options.add_argument('--no-default-browser-check')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-default-apps')
    options.add_argument("--headless")
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return webdriver.Chrome(options=options, executable_path=config_file.CHROMEDRIVER_PATH)

driver = get_driver(); print()


class Section:
    def __init__(self, name, url):
        self.name = ' '.join(name.split())
        self.url = 'https://www.simonstalenhag.se/' + url
        self.img_url_dict = {}

    def add_img_url(self, img_url):
        img_nam = img_url.replace('/', '_').replace('.jpg', '')
        self.img_url_dict[img_nam] = 'https://www.simonstalenhag.se/' + img_url

    def print_all(self):
        print(f'Name: {self.name}')
        print(f'Url: {self.url}')
        print('Images:')
        for key, value in self.img_url_dict.items():
            print(f'{key}: {value}')
        print()


def get_html_source(driver):
    html_source = driver.page_source
    soup = BS(html_source, 'html.parser')
    return soup

def get_sections():
    driver.get('https://www.simonstalenhag.se/index.html')
    soup = get_html_source(driver)
    return [[Section(y.text, y['href']) for y in x.findAll('a')] for x in soup.find_all("span", {"class": "style2"})][0]

def get_images_from_section(section):
    driver.get(section.url)
    soup = get_html_source(driver)
    [section.add_img_url(s['href']) for s in soup.find_all("a", {"target": "_blank"}) if 'big' in s['href']]

def download_images(section):
    dir = config_file.SAVE_DIR
    folders_in_dir = listdir(dir)
    save_dir = path.join(dir, section.name)
    try:
        mkdir(save_dir)
    except:
        pass

    pbar = tqdm(section.img_url_dict.items(), desc='Downloading images')
    for img_nam, img_url in pbar:
        pbar.set_postfix_str(img_nam)
        img_data = requests.get(img_url).content
        with open(path.join(save_dir, section.name + '_' + img_nam + '.png'), 'wb') as handler:
            handler.write(img_data)

def main():
    try:
        section_lst = get_sections()
        pbar = tqdm(section_lst, desc='Getting section data')
        for section in pbar:
            pbar.set_postfix_str(section.name)
            get_images_from_section(section)

        pbar = tqdm(section_lst, desc='Downloading section images')
        for section in pbar:
            pbar.set_postfix_str(section.name)
            download_images(section)
    except Exceptions as e_msg:
        print(e_msg)
    finally:
        driver.quit()



if __name__ == '__main__':
    main()
