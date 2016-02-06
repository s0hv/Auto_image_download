from imgurpython.helpers.error import ImgurClientError
import requests
import shutil
import os


class Imgur(object):

    max_images = 50
    max_size = 157286400 # In bytes

    def __init__(self, imgurclient=None):
        self.imgurclient = imgurclient

    # Get the Imgur image. Exceptions return False, otherwise True
    def get(self, url, filename):
        imgurclient = self.imgurclient
        if imgurclient is None:
            raise ImgurClientError
        try:
            link = url.split("/")
            if "i.imgur.com" in link:
                img_id = link[-1].split(".")[0]
                image = imgurclient.get_image(image_id=img_id)
                return self.download(image)
            elif "a" in link:
                print("k")
                if link[-1] == "gallery":
                    album_id = link[-2]
                else:
                    album_id = link[-1]
                album = imgurclient.get_album(album_id)
                images = imgurclient.get_album_images(album_id)
                return self.download(images, self.album_name(album), filename)
            elif "imgur.com" in link:
                img_id = link[-1]
                if img_id == "new":
                    img_id = link[-2]
                if len(img_id) == 5:
                    album = imgurclient.get_album(img_id)
                    images = imgurclient.get_album_images(img_id)
                    return self.download(images, self.album_name(album), filename)
                elif img_id is not None:
                    image = imgurclient.get_image(img_id)
                    return self.download(image)
                else:
                    return False
            else:
                print(link)
                return False

        except ImgurClientError as e:
            print(e.error_message)
            print(e.status_code)
            return False

    def download(self, images, album_name=None, file=None, moved=True):
        # Called for images. Returns True on success and False otherwise
        def download_image(image_obj, folder="", i=""):
            nonlocal moved
            r = requests.get(image_obj.link, stream=True)
            print(folder)
            if r.status_code == 200:
                path = os.path.normpath('E:/Dropbox/Images/Imgur/' + folder)
                if not os.path.exists(path):
                    os.mkdir(path)
                if file is not None and not moved:
                    os.rename('E:\\Dropbox\\Images\\' + file, path + '\\' + file)
                    moved = True
                if i != "":
                    i += " "
                path = path + "\\" + i + image_obj.id + "." + image_obj.type.replace("image/", "")
                print(path)
                with open(path, 'wb') as f:
                    f.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
                    f.close()
                    return True
            else:
                return False

        # Checks if it's an album or a single image
        if type(images) is list:
            amount = len(images)
            if amount > self.max_images:
                print("Too many images: ", amount)
                size = self.get_size(images)
                if size > self.max_size:
                    print("Too big:", size)
                    return "Images " + str(amount) + " Size " + str(size/1000000) + "MB"
            folder_name = album_name + "\\"
            index = ["%.2d" % i for i in range(1, amount+1)]
            moved = False
            for idx, image in enumerate(images):
                value = download_image(image, folder=folder_name, i=index[idx])
            return value
        else:
            title = ""
            if images.title is not None:
                title = images.title
            return download_image(images, i=title)

    # Returns album name if available
    def album_name(self,album):
        if album.title is None:
            print(album.id)
            return album.id
        else:
            print(album.title + " " + album.id)
            return album.title + " " + album.id

    def set_max_images(self, amount):
        self.max_images = amount

    def set_max_size(self, size):
        self.max_size = size

    def get_size(self, images):
        size = 0
        for image in images:
            size += image.size
        return size
