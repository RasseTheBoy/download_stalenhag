
# Download Simon Stålenhag images

Downloads all images from [simontålenhag.se](https://www.simonstalenhag.se/) to your computer


## Made by

- [@RasseTheBoy](https://github.com/RasseTheBoy)


## Installation guide

pip:
```bash
  pip3 install download_stalenhag
```
## Needed libraries

[bs4](https://pypi.org/project/beautifulsoup4/)

[tqdm](https://pypi.org/project/tqdm/)

[selenium](https://pypi.org/project/selenium/)
## Environment Variables

To run this project, you will need to add the following variables to your config_file.py file

`CHROMEDRIVER_PATH` --> Path to your ChromeDriver (Firefox should also work)

`SAVE_DIR` --> Directory where images should be saved


## How does it work?

- Selenium scrapes [simontålenhag.se](https://www.simonstalenhag.se/) and gets all of the available sections.

- Then one by one downloads every image from each section.
## Run file

Python:
```bash
  python download_stalenhag.py
```

Cmd:
```bash
  cd path/to/directory
  python download_stalenhag.py
```
## Demo gif

(Video is sped up)

![Alt Text](https://media.giphy.com/media/gVPcQhQ9MvYJ6jX0Kh/giphy.gif)


## FAQ

#### **Is bs4/tqdm/selenium required?**

Yes.

#### **Will the code work without `CHROMEDRIVER_PATH`/`SAVE_DIR`?**

No.

#### **I can't see selenium!**

Selenium downloads the images in the background and destroys itself when ready.

#### **Will selenium be destroyed if I stop the code**

Not necessarily. To be sure, open task manager on Windows (ctrl+shift+tab) and kill all Chrome tabs.

#### **I can't get selenium working**

Make sure you follow the [instructions](https://selenium-python.readthedocs.io/installation.html) clealry.

#### **How long will it take to download all of the images?**

The download speed depends on your network speed.

#### **Why is it taking so long?**

The download speed depends on your network speed.

#### **Are the images HD?**

Images are downlaoded by the highest qaulity possible (hence the reason it may take some time).

#### **Do I need to change anything in the `main.py` file?**

No. Only the `CHROMEDRIVER_PATH` and `SAVE_DIR` variables needs to be added into `config-file.py`.
