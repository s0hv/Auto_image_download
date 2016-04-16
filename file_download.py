import os
import time
import json

from imgurpython import ImgurClient
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

import downloaders
from downloaders import Imgur, Gfycat, Deviantart, DirectLink, Tumblr


class GetFiles(object):
    def __init__(s):
        # Set up the variables
        s.path = ""
        s.phantom_on = False
        s.phantom_driver = None
        s.phantom_path = ""
        # Image sites
        s.gfycat = Gfycat()
        s.tumblr = None
        s.imgur = None
        s.deviantart = None
        # Chrome status
        s.driver = None
        s.chrome_working = False
        s.chrome_on = False
        s.chrome_extension = ""

    # Checks files in path and reads them. If image download fails the text file will not be deleted.
    def get_images(s):
        path = s.path
        files = [i for i in os.listdir(path) if ".txt" in i]
        for file in files:
            opened = path + "\\" + file
            with open(opened) as f:
                link = f.readline()
                f.close()
            s.download(link, file)

    def download(s, link, file=None):
        result = False
        if file is not None:
            path = s.path + "\\" + file
        else:
            path = None
        print(link)
        # Imgur images
        if 'imgur.com' in link:
            result = s.imgur.get(link, file)
            print("Result: ", result, path)
            if result is False:
                print("Could not download image")
            elif result is not False and not True:
                print("Big album")
                os.rename(path, path + "\\Imgur\\Big albums\\" + result + ".txt")
            elif result:
                print("Success")
                if path is not None and os.path.isfile(path):
                    os.remove(path)
                    print('\n')
                    # Gfycat images
        elif 'gfycat.com' in link:
            gfy_id = link.split("/")[-1].split(".")[0]
            result = s.gfycat.get_image(gfy_id)
            print(result)
            if result and path is not None:
                os.remove(path)
                print(link, '\n')
            else:
                print("Something went wrong in gfycat")
                # DeviantArt images. Doesn't work if Chrome didn't start correctly
        elif 'deviantart.com' in link:
            if not s.chrome_on:
                s.open_chrome(s.chrome_extension)
            if s.chrome_working:
                s.close_windows(s.driver.current_url)
                result = s.deviantart.get_image(path, link)
                if result:
                    print("Nice", result)
                else:
                    print("Fuck", result)
        elif '.tumblr.' in link and not '.media.tumblr.com/':
            if s.tumblr is not None:
                result = s.tumblr.download(link)
                print(result)
                if result is True and path is not None:
                    os.remove(path)
        else:
            if not s.phantom_on:
                s.start_phantomjs()
            result = DirectLink.download_image(link, path, s.phantom_driver)
            print(result, link)
            if not result:
                print("Fuck")
        print('\n')
        return result

    def bookmarks(self, path):
        if not os.path.isfile(path):
            return False
        with open(path, 'r', encoding='utf-8') as file:
            j = json.load(file)
            file.close()
        with open(r'Data\Links.txt') as l:
            links = l.read()
        new = ""
        for i in j['roots']['bookmark_bar']['children']:
            try:
                foldername = i['name']
                if foldername == 'Pictures':
                    for l in i['children']:
                        url = l['url']
                        if url not in links:
                            if self.download(url):
                                new += url + '\n'
            except KeyError:
                pass
        with open(r'Data\Links.txt', 'a') as l:
            l.write(new)

    def close_windows(s, curr_url):
        driver = s.driver
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

    def open_chrome(s, extension_path):
        # Initialize Chrome
        options = webdriver.ChromeOptions()
        options.add_extension(extension_path)
        try:
            s.driver = webdriver.Chrome(chrome_options=options)
        except (AttributeError, OSError) as e:
            print(e)
            pass
        driver = s.driver
        driver.set_window_position(x=-2000, y=0)
        s.chrome_on = True
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
                    elements = driver.find_elements_by_tag_name('input')
                    for e in elements:
                        if e.get_attribute('value') == 'Install':
                            e.click()
                            s.deviantart = Deviantart(driver)
                            s.chrome_working = True
                            break
                except NoSuchElementException:
                    s.chrome_working = False

    # Imgur api auth
    def set_imgur(s, id, secret):
        client = ImgurClient(id, secret)
        s.imgur = Imgur(imgurclient=client)

    # Set path to image folder
    def set_path(s, image_path):
        s.path = image_path
        downloaders.set_folder(image_path)
        downloaders.check_folders()

    def ext_path(s, path):
        s.chrome_extension = path

    def quit_chrome(s):
        if s.chrome_on:
            s.driver.quit()

    def start_phantomjs(s):
        try:
            s.phantom_driver = webdriver.PhantomJS(s.phantom_path)
        except (AttributeError, OSError) as e:
            print(e)
            pass
        s.phantom_on = True

    def set_phantom_path(s, path):
        s.phantom_path = path

    def set_tumblr(s, key):
        s.tumblr = Tumblr(key)

    def stop_phantom(s):
        if s.phantom_on:
            s.phantom_driver.quit()
