import requests, os, shutil


class Gfycat(object):

    def __init__(self, down_path=os.path.normpath('E:/Dropbox/Images/Gfycat')):
        self.down_path = down_path

    def get_image(self, url):
        gfy_api = 'https://gfycat.com/cajax/get/'
        r = requests.get(gfy_api + url)
        json = r.json()
        if json.get('error') is None:
            gif_stuff = json.get('gfyItem')
            if gif_stuff is None:
                return False
            else:
                url = gif_stuff.get('gifUrl')
                if url is None:
                    return False
                else:
                    name = gif_stuff.get('gfyName')
                    title = gif_stuff.get('title')
                    if title is not None:
                        name = title + " " + gif_stuff.get('gfyName')
                    return self.download_image(url, name)

    def download_image(self, url, name):
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                path = self.down_path
                path = path + "\\" + name + ".gif"
                print(path)
                with open(path, 'wb') as f:
                    f.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
                    f.close()
                    return True
            else:
                return False
