from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from py_basic_commands  import try_listdir
from selectolax.parser  import HTMLParser
from send2trash         import send2trash
from aiohttp            import ClientSession
from fsutil             import join_filepath
from tqdm               import tqdm
from os                 import makedirs

import httpx, asyncio



def create_and_remove_empty_dir(func):
    """Decorator to create and remove empty directories.
    
    Parameters
    ----------
    func : function
        The function to be decorated.
        
    Returns
    -------
    function
        The decorated function.
    """
    def wrapper(self, *args, **kwargs):
        # Create the section directory
        makedirs(self.section_dir, exist_ok=True)

        # Run the function in an asyncio event loop
        asyncio.run(func(self, *args, **kwargs))

        # Remove the section directory if it's empty
        if try_listdir(self.section_dir) == []:
            send2trash(self.section_dir)
    return wrapper



class Section:
    def __init__(
            self,
            parent_self:StalenhagDownloader,
            name:str,
            section_href:str
        ):
        
        self.parent_self = parent_self
        self.section_name = name.strip()
        self.section_url = self.parent_self.url_lambda(section_href)
        self.section_dir = join_filepath(self.parent_self.main_dir_path, self.section_name)


    async def fetch_section_image_urls(self, session:ClientSession):
        """Fetch all image urls from the section.
        
        Parameters
        ----------
        session : ClientSession
            The aiohttp ClientSession object.
            
        Returns
        -------
        list
            The list of image urls.
        """
        img_url_lst = []

        async with session.get(self.section_url) as resp:
            for node in HTMLParser(await resp.text()).css('a[target="_blank"]'):
                # Get the image href
                img_href = node.attributes.get('href', '')

                # Only yield big images
                if 'big' not in img_href: # type: ignore
                    continue
                
                # Format the whole image url
                img_url = self.parent_self.url_lambda(img_href)
                if img_url not in img_url_lst:
                    img_url_lst.append(img_url)
                
        return img_url_lst


    @create_and_remove_empty_dir
    async def download_all_section_images(self):
        """Download all images from the section to the section directory.
        
        Raises
        ------
        ValueError
            If the response status is not 200.
        """
        async def download_image(img_url:str):
            """Download an image from the section.
            
            Parameters
            ----------
            img_url : str
                The image url.
            """
            async with session.get(img_url) as resp:
                # Raise ValueError if response status is not 200
                if resp.status != 200:
                    raise ValueError(f'Error: {resp.status} -> {img_url}')

                # Save image to file in section directory
                file_name = f'{self.section_name}_{img_url.split("/")[-1]}'
                with open(
                    join_filepath(self.section_dir, file_name),
                    'wb'
                    ) as handler:
                    handler.write(await resp.read())

        async with ClientSession() as session:
            # Download all big images from the section
            await asyncio.gather(*[
                download_image(img_url) for img_url in
                await self.fetch_section_image_urls(session)
            ])
        




class StalenhagDownloader:
    website_homepage = 'https://www.simonstalenhag.se'

    def __init__(self, dir_path:str='Stalenhag collection'):
        self.main_dir_path = dir_path
        self.url_lambda = lambda url_suffix : f'{self.website_homepage}/{url_suffix}'


    @staticmethod
    def get_html_from_url(url:str) -> HTMLParser:
        """Get HTML from a website and return it as a HTMLParser object.
        
        Parameters
        ----------
        url : str
            The website url.
            
        Returns
        -------
        HTMLParser
            The HTMLParser object of the website.
        """
        resp = httpx.get(url)
        if resp.status_code != 200:
            raise ValueError('Website error!')

        return HTMLParser(resp.text)


    def start(self) -> None:
        """Start the download of all images from the website."""
        thread_lst = []


        with ThreadPoolExecutor(max_workers=5) as executor:
            for x in self.get_html_from_url(self.website_homepage).css('span[class="style2"] a'):
                section_href = x.attributes['href']

                if section_href is None:
                    raise ValueError(f'No href found! -> {x.text()}')

                thread_lst.append(
                    executor.submit(
                        Section(
                            self,
                            x.text(),
                            section_href
                        ).download_all_section_images
                    )
                )

            print('Starting threads...')
            pbar = tqdm(
                total = len(thread_lst),
                desc = 'Threads completed',
                unit = 'thread'
            )
            for future in as_completed(thread_lst):
                pbar.update(1)
            pbar.close()

        print('All threads completed!')

        
            



if __name__ == '__main__':
    StalenhagDownloader().start()
