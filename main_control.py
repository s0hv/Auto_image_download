from imgurpython import ImgurClient
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from imgur import Imgur
from gfycat import Gfycat
from deviantart import Deviantart
import logging, os, time


# Checks files in path and reads them. If image download fails the text file will not be deleted.
def get_images(path=os.path.normpath("E:/Dropbox/Images")):
    global imgur, gfycat, deviantart
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
                if result and f.closed:
                    os.remove(opened)
                    print('\n')
                else:
                    print("Something went wrong in imgur")
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
            elif 'deviantart.com' in link and chrome_working:
                close_windows(driver.current_url)
                result = deviantart.get_image(opened, link)
                if result:
                    print("Nice", result)
                else:
                    print("Fuck")


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

# Set up the variables
# Start Imgur
client_id = 'b903704e3bee004'
client_Secret = 'f53909a6dc51f30b8477fa3c8d896b0af5c7d52b'
client = ImgurClient(client_id, client_Secret)
# Initialize Chrome
options = webdriver.ChromeOptions()
options.add_extension(r"C:\Users\Tariq\Scripts\projects\Image downloader\Tampermonkey.crx")
driver = webdriver.Chrome(chrome_options=options)
driver.set_window_position(x=-2000, y=0)
# Create image site objects
deviantart = Deviantart(driver)
gfycat = Gfycat()
imgur = Imgur(imgurclient=client)
# The logger
logging.basicConfig(level=logging.WARNING, filename="Errors/Error.log", format='%(asctime)s')
# Determines if pictures can be loaded with Chrome
chrome_working = False


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
        except NoSuchElementException:
            chrome_working = False

# Tries to Download images. Writes errors in file.
try:
    get_images()
except:
    driver.quit()
    logging.exception("Error ")

driver.quit()

#driver.set_window_position(x=-2000, y=0)
#time.sleep(4)
#if len(driver.window_handles) < 2:
#    driver.quit()
#    sys.exit("Error installing tampermonkey")
#time.sleep(4)
#tabs = driver.window_handles

#for tab in tabs:
    #driver.switch_to.window(tab)
    # if r"https://www.google.com/_/chrome/newtab?espv=2&ie=UTF-8" in driver.current_url:
    #      continue
    #   driver.close()

#driver.switch_to.window(driver.window_handles[0])
