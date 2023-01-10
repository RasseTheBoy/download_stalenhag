import requests, threading

from py_basic_commands  import create_file_dir, func_timer, join_path, get_dir_path_for_file, fprint
from selectolax.parser  import HTMLParser


def get_html_from_url(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        raise ValueError('Website error!')

    html = HTMLParser(resp.text)
    
    return html

def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


class Section:
    def __init__(self, root, name:str, url_suffix:str) -> None:
        self.section_name = name.strip()
        self.url_fill = root.website_homepage + '{}'
        self.section_url = self.url_fill.format(url_suffix)
        self.section_dir = join_path(root.main_dir_path, self.section_name)
        self.section_file_path_fill = join_path(self.section_dir, '{}')

    @threaded
    def get_section_images(self):
        html = get_html_from_url(self.section_url)
        self.href_lst = [x.attributes['href'] for x in html.css('[target=_blank]') if 'big' in x.attributes['href']]

    def download_section_images(self):
        @threaded
        def download_image(href):
            img_file_path = self.section_file_path_fill.format(get_dir_path_for_file(href, 'fnam'))
            img_url = self.url_fill.format(href)

            reqs = requests.get(img_url)

            if reqs.status_code != 200:
                return

            with open(img_file_path, 'wb') as handler:
                handler.write(reqs.content)

        if not self.href_lst:
            return

        create_file_dir('d', self.section_dir)

        fprint(f'Downloading: {self.section_name}')
        download_thr_lst = [download_image(href) for href in self.href_lst]
        [thr.join() for thr in download_thr_lst]


class StalenhagDownloader:
    """
    The StalenhagDownloader class is used to download all images from the website simonstalenhag.se.
    This class uses the 'requests' library to make HTTP GET requests to the website and 'selectolax' library to parse the HTML content of the website.
    It uses threading to make request and download concurrently for faster downloading time.
    It takes an optional argument 'main_dir_path' which represents the path where the downloaded images will be stored.

    Args:
    - `main_dir_path` (str, optional): path where the downloaded images will be stored. Defaults to 'Stalenhag collection'.

    Methods:
    - `start()`: Initiates the download process.

    """
    website_homepage = 'https://www.simonstalenhag.se/'

    def __init__(self, main_dir_path:str='Stalenhag collection'):
        if not main_dir_path:
            main_dir_path = 'Stalenhag collection'

        self.main_dir_path = main_dir_path

    @func_timer()
    def start(self):
        create_file_dir('d', self.main_dir_path)

        html = get_html_from_url(self.website_homepage)
        obj_lst = [Section(self, x.text(), x.attributes['href']) for x in html.css('span.style2 a')]

        obj_thr_lst = [x.get_section_images() for x in obj_lst]
        [x.join() for x in obj_thr_lst]

        [x.download_section_images() for x in obj_lst]

        print('Code complete!')


if __name__ == '__main__': 
    StalenhagDownloader().start()