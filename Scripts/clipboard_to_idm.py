# copy ASF link of Sentinel-1 data, then added to IDM automaticly.
# "Ctrl + C" to quit this script

import re
import sys
from subprocess import call

import pyperclip


def get_clipboard():
    plaintext = pyperclip.paste()
    pattern = r'https://d2jcx4uuy4zbnt.cloudfront.net/s3-06b3213905ebfa9144871d6c7f9306f0.+Expires=\d{10}'
    res = re.match(pattern, plaintext)
    if res:
        return plaintext
    return None


def get_zip_name(text):
    pattern = r'S1\w{65}\.zip'
    res = re.search(pattern, text)
    if res:
        return res.group()
    return None


def add_to_idm(idm_path, download_link, save_path):
    zip_name = get_zip_name(download_link)
    if zip_name:
        try:
            call([
                idm_path, '/d', download_link, '/p', save_path, '/f', zip_name,
                '/n', '/a'
            ])
            print('add to idm.\n')
        except:
            print('cannot add to idm.\n')
    else:
        print('not a suportted link.')
        sys.exit(1)


if __name__ == "__main__":
    clipboard_list = []
    idm_path = r'C:\thorly\Softwares\IDM\IDMan.exe'
    save_path = r'D:\xsc\zip'
    pyperclip.copy('just for fun.')
    print('start monitoring the clipboard.')
    while True:
        clipboard_text = get_clipboard()
        if clipboard_text and clipboard_text not in clipboard_list:
            clipboard_list.append(clipboard_text)
            print(clipboard_text)
            zip_name = get_zip_name(clipboard_text)
            print(zip_name)
            add_to_idm(idm_path, clipboard_text, save_path)
