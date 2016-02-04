from imgurpython.helpers.error import ImgurClientError
import requests
import shutil
import os


class Imgur(object):

    def __init__(self, imgurclient=None):
        self.imgurclient = imgurclient

    # Get the Imgur image. Exceptions return False, otherwise True
    def get(self, url):
        imgurclient = self.imgurclient
        if imgurclient is None:
            return "No imgurclient"
        try:
            link = url.split("/")
            if "i.imgur.com" in link:
                img_id = link[-1].split(".")[0]
                image = imgurclient.get_image(image_id=img_id)
                print("First if ", img_id)
                return self.download(image)
            elif "a" in link:
                if link[-1] == "gallery":
                    album_id = link[-2]
                else:
                    album_id = link[-1]
                album = imgurclient.get_album(album_id)
                images = imgurclient.get_album_images(album_id)
                print("Second if ", album_id)
                return self.download(images, self.album_name(album))
            elif "imgur.com" in link:
                img_id = link[-1]
                if len(img_id) == 5:
                    album = imgurclient.get_album(img_id)
                    images = imgurclient.get_album_images(img_id)
                    print("Third if 1 ", album.title, album.id)
                    return self.download(images, self.album_name(album))
                else:
                    image = imgurclient.get_image(img_id)
                    print("Third if 2 ", img_id)
                    return self.download(image)

        except ImgurClientError as e:
            return False
            print(e.error_message)
            print(e.status_code)

    def download(self, images, album_name=None):
        # Called for images. Returns True on success and False otherwise
        def download_image(image_obj, folder="", i=""):
            r = requests.get(image_obj.link, stream=True)
            print(folder)
            if r.status_code == 200:
                path = os.path.normpath('E:/Dropbox/Images/Imgur/' + folder)
                if not os.path.exists(path):
                    os.mkdir(path)
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
            folder_name = album_name + "\\"
            index = ["%.2d" % i for i in range(1, len(images)+1)]
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
