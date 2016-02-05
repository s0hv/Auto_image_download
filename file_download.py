from imgurpython import ImgurClient
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from imgur import Imgur
from gfycat import Gfycat
from deviantart import Deviantart
import logging, os, time


class GetFiles(object):
    # Set up the variables
    client_id = None
    client_secret = None
    path = ""
    # Image sites
    gfycat = Gfycat()
    imgur = None
    deviantart = None
    # The logger
    logging.basicConfig(level=logging.WARNING, filename="Errors/Error.log", format='%(asctime)s')
    # Chrome status
    chrome_working = False
    chrome_on = False

    # Checks files in path and reads them. If image download fails the text file will not be deleted.
    def get_images(self):
        global imgur, gfycat, deviantart, path
        files = [i for i in os.listdir(path) if ".txt" in i]
        for file in files:
            opened = path + "\\" + file
            with open(opened) as f:
                link = f.readline()
                f.close()
                # Imgur images
                if 'imgur.com/' in link:
                    print(link)
                    result = imgur.get(link)
                    print("Result: ", result, opened)
                    if result is not True:
                        os.rename(opened, path + "\\Imgur\\Big albums\\" + result + ".txt")
                        print("Something went wrong in imgur: " + result)
                    else:
                        os.remove(opened)
                        print('\n')
                # Gfycat images
                elif 'gfycat.com' in link:
                    gfy_id = link.split("/")[-1].split(".")[0]
                    result = gfycat.get_image(gfy_id)
                    print(result)
                    if result and f.closed:
                        os.remove(opened)
                        print('\n')
                    else:
                        print("Something went wrong in gfycat")
                # DeviantArt images. Doesn't work if Chrome didn't start correctly
                elif 'deviantart.com' in link:
                    if not chrome_on:
                        self.open_chrome()
                    if chrome_working:
                        self.close_windows(driver.current_url)
                        result = deviantart.get_image(opened, link)
                        if result:
                            print("Nice", result)
                        else:
                            print("Fuck")

    @staticmethod
    def close_windows(curr_url):
        h = driver.window_handles
        saved_handle = h[0]
        for n in h:
            driver.switch_to.window(n)
            url = driver.current_url
            if curr_url != url:
                driver.close()
            else:
                saved_handle = n
        driver.switch_to.window(saved_handle)

    @staticmethod
    def open_chrome():
        global chrome_on, chrome_working, driver, deviantart
        # Initialize Chrome
        options = webdriver.ChromeOptions()
        options.add_extension(r"C:\Users\Tariq\Scripts\projects\Image downloader\Tampermonkey.crx")
        driver = webdriver.Chrome(chrome_options=options)
        driver.set_window_position(x=-2000, y=0)
        chrome_on = True
        # Install Userscripts to Tampermonkey
        driver.get('chrome://extensions/dhdgffkkebhmkfjojejmpbldmpobfkfod')
        time.sleep(1)
        # Restart Tampermonkey to ensure that it works
        driver.switch_to.frame('extensions')
        b = driver.find_elements_by_class_name('enabled-text')
        b[-2].click()
        b = driver.find_elements_by_class_name('enable-text')
        b[-2].click()
        time.sleep(3)
        # Get DeviantArt download button script
        driver.get('https://openuserjs.org/install/TimidScript/%5BTS%5D_deviantART_Download_Link.user.js')
        time.sleep(3)
        windows = driver.window_handles
        for w in windows:
            driver.switch_to.window(w)
            url = driver.current_url
            if 'chrome-extension://' in url:
                try:
                    elem = driver.find_element_by_id('input_dG1fSW5zdGFsbA')
                    elem.click()
                    chrome_working = True
                    deviantart = Deviantart(driver)
                except NoSuchElementException:
                    chrome_working = False

    # Imgur api auth
    @staticmethod
    def set_imgur(id, secret):
        global client_id, client_secret, imgur
        client_secret = secret
        client_id = id
        client = ImgurClient(client_id, client_secret)
        imgur = Imgur(imgurclient=client)

    # Set path to image folder
    @staticmethod
    def set_path(image_path):
        global path
        path = image_path

    def quit_chrome(self):
        if chrome_on:
            driver.quit()
