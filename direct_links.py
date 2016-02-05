import requests, shutil, os


class DirectLink(object):

    @staticmethod
    def download_image(url, file_path, driver):
        def download():
            if r.status_code == 200:
                path = os.path.normpath('E:/Dropbox/Images/Other')
                path_folder = path + "\\" + image_name.split(".")[0]
                if not os.path.exists(path_folder):
                    os.mkdir(path_folder)
                path = path_folder + "\\" + image_name
                print(path)
                with open(path, 'wb') as f:
                    f.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
                    f.close()
                    os.rename(file_path, path_folder + "\\Link.txt")
                    return True
            else:
                return False
        image_name = url.split('/')[-1]
        r = requests.get(url, stream=True)
        print(image_name)
        if "image" in r.headers['Content-Type']:
            return download()
        else:
            driver.get(url)
            images = driver.find_elements_by_tag_name('img')
            if len(images) > 5:
                os.rename(file_path, file_path + "\\Too many images\\" + file_path.split("\\")[-1])
                return False
            else:
                for image in images:
                    src = image.get_attribute('src')
                    if src is None:
                        src = image.get_attribute('data-src')
                        if src is None:
                            return False
                    r = requests.get(src, stream=True)
                    return download()
