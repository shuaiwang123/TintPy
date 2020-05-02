from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QColor
from bs4 import BeautifulSoup
from subprocess import call
import requests
import urllib
import re
import os
import sys
import time
import datetime
from download_ui import Ui_Form


class ProcessData:
    @staticmethod
    def get_orbit_date(date):
        """
        :param date: date of Sentinel-1
        :return: date of orbit
        """
        image_date = datetime.datetime.strptime(date, '%Y%m%d')
        delta = datetime.timedelta(days=-1)
        orbit_date = image_date + delta
        return orbit_date.strftime('%Y-%m-%d')

    @staticmethod
    def check_date_and_mission(date_and_mission):
        """
        check orbit date, delete date of no orbit data
        :param date_and_mission: sentinel-1 date and mission
        :return: no_orbit_date
        """
        no_orbit_date_and_mission = []
        now = datetime.datetime.now()
        for d in date_and_mission:
            orbit_date = datetime.datetime.strptime(ProcessData.get_orbit_date(d[0:8]), '%Y-%m-%d')
            if (now - orbit_date).days <= 21:
                no_orbit_date_and_mission.append(d)
                date_and_mission.remove(d)
        return no_orbit_date_and_mission

    @staticmethod
    def get_sentinel1_date_and_mission_from_zip(images_path):
        """
        :param images_path: path of directory including Sentinel-1A/B (.zip)
        :return: date and mission (list)
        """
        images_date_and_mission = []
        files = os.listdir(images_path)
        for file in files:
            if re.search(r'S1\w{65}\.zip', file):
                date_and_mission = re.findall(r"\d{8}", file)[0] + file[0:3]
                if date_and_mission not in images_date_and_mission:
                    images_date_and_mission.append(date_and_mission)
        return images_date_and_mission

    @staticmethod
    def get_sentinel1_date_and_mission_from_text(text_path):
        """
        :param text_path: path of file including Sentinel-1A/B names
        :return: date and mission (list)
        """
        images_date_and_mission = []
        with open(text_path, encoding='utf-8') as file:
            for f in file:
                if re.search(r'S1\w{65}', f):
                    date_and_mission = re.findall(r"\d{8}", f)[0] + f[0:3]
                    if date_and_mission not in images_date_and_mission:
                        images_date_and_mission.append(date_and_mission)
        return images_date_and_mission

    @staticmethod
    def get_sentinel1_date_and_mission(path):
        """
        :param path: path of directory or file
        :return: date and mission
        """
        if os.path.isdir(path):
            return ProcessData.get_sentinel1_date_and_mission_from_zip(path)
        else:
            return ProcessData.get_sentinel1_date_and_mission_from_text(path)


class GetUrlThread(QThread):
    sin_out_current_process = pyqtSignal(int)
    sin_out_current_url = pyqtSignal(str)
    sin_out_task_num = pyqtSignal(int)
    sin_out_urls_found = pyqtSignal(list)
    sin_out_no_orbit_date = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.name_path = ''
        self.url_prefix = 'https://qc.sentinel1.eo.esa.int/aux_poeorb/'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36\
                     (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

    def run(self):
        urls_found = []
        process = 0  # 抓取链接进度
        date_and_mission = ProcessData.get_sentinel1_date_and_mission(self.name_path)  # 得到影像日期和对应的mission
        no_orbit_date_and_mission = ProcessData.check_date_and_mission(date_and_mission)  # 检查所有影像是否都有对应的精轨，若有不对应的则删除
        self.sin_out_no_orbit_date.emit(no_orbit_date_and_mission)  # 发射无精轨日期
        print('no_orbit_date_and_mission', no_orbit_date_and_mission)
        print('date_and_mission', date_and_mission)
        self.sin_out_task_num.emit(len(date_and_mission))  # 发射总任务数量
        for d in date_and_mission:
            url_param_json = {}
            url_param_json['sentinel1__mission'] = d[-3:]
            url_param_json['validity_start'] = ProcessData.get_orbit_date(d[0:8])
            url_param = urllib.parse.urlencode(url_param_json)
            url = self.url_prefix + "?" + url_param
            html = requests.get(url, headers=self.headers)
            if html.status_code == 200:  # 请求成功
                dom = BeautifulSoup(html.text, "html.parser")  # 解析请求到的数据
                eofs = re.findall(r"http.*EOF", str(dom))  # 查找下载链接
                if eofs:
                    urls_found.append(eofs[0])
                    process += 1  # 查找到链接，进度加1
                    self.sin_out_current_process.emit(process)  # 发射抓取链接进度
                    self.sin_out_current_url.emit(eofs[0])
                else:
                    print('cannot find http.*EOF from html.text')
            else:
                print('error to request.get')
        self.sin_out_urls_found.emit(urls_found)  # 发射抓取到的url


class ExecIDMThread(QThread):
    def __init__(self):
        super().__init__()
        self.idm_path = ''

    def run(self):
        os.system(self.idm_path)


class AddToIDMThread(QThread):
    sin_out_if_success = pyqtSignal(str)
    sin_out_error_num = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.save_path = ''
        self.idm_path = ''
        self.urls = []

    @staticmethod
    def add_to_idm(idm_path, urls, save_path):
        """
        :param idm_path: path of IDMan.exe
        :param urls: urls of orbits
        :param save_path: path of saving orbits
        :return: num of error
        """
        error_num = 0
        for i in range(len(urls)):
            try:
                call([
                    idm_path, '/d', urls[i], '/p', save_path, '/f',
                    urls[i], '/n', '/a'])
            except:
                print('error')
                error_num += 1
        return error_num

    def run(self):
        error_num = self.add_to_idm(self.idm_path, self.urls, self.save_path)
        if not error_num:
            time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.sin_out_if_success.emit("{} 所有下载任务都被添加到了IDM".format(time))
        else:
            time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.sin_out_if_success.emit("{} 有 {} 个未被添加到IDM".format(time, error_num))


class Window(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.get_url_thread = GetUrlThread()
        self.exec_idm_thread = ExecIDMThread()
        self.add_to_idm_thread = AddToIDMThread()
        self.setupUi(self)
        self.connect_slots()

    def connect_slots(self):
        # GetUrlThread
        self.get_url_thread.sin_out_current_process.connect(lambda value: self.progressBar.setValue(value))
        self.get_url_thread.sin_out_task_num.connect(self.get_task_num)
        self.get_url_thread.sin_out_urls_found.connect(self.assign_urls_found)
        self.get_url_thread.sin_out_no_orbit_date.connect(self.get_no_orbit_date)
        self.get_url_thread.sin_out_current_url.connect(self.set_current_url)
        # AddToIDMThread
        self.add_to_idm_thread.sin_out_error_num.connect(self.error_add_to_idm)
        self.add_to_idm_thread.sin_out_if_success.connect(self.success_add_to_idm)
        # others
        self.pushButton_name_path.clicked.connect(self.get_name_path_from_text)
        self.radioButton_text.toggled.connect(lambda: self.switch_btn_connect_state(self.radioButton_text))
        self.radioButton_zip.toggled.connect(lambda: self.switch_btn_connect_state(self.radioButton_zip))
        self.pushButton_save_path.clicked.connect(self.get_save_path)
        self.pushButton_idm_path.clicked.connect(self.get_idm_path)
        self.pushButton_get_urls.clicked.connect(self.get_urls)
        self.pushButton_add_to_idm.clicked.connect(self.add_to_idm)

    def warning(self, info):
        """弹出警告信息"""
        mb = QMessageBox(QMessageBox.Warning, "Warning", info, QMessageBox.Ok, self)
        mb.show()

    def get_task_num(self, num):
        if num:
            self.progressBar.setEnabled(True)
            self.progressBar.setMaximum(num)
            self.progressBar.setValue(0)
            self.textEdit_info.setFontUnderline(False)
            self.textEdit_info.setTextColor(QColor('black'))
            time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.textEdit_info.append("{} 需要抓取 {} 个精轨链接\n".format(time1, num))
            time2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.textEdit_info.append("{} 开始抓取精轨链接\n\n".format(time2))
        else:
            self.warning("未找到哨兵影像名，请重新设置{}".format(self.label_type.text()[:-1]))
            self.progressBar.setEnabled(False)

    def get_no_orbit_date(self, date):
        self.textEdit_info.clear()
        if date:
            for d in date:
                time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.textEdit_info.append("{} {}-{} 目前无对应的精轨\n".format(time, d[-3:], d[:8]))

    def assign_urls_found(self, urls):
        self.add_to_idm_thread.urls = urls

    def get_name_path_from_text(self):
        file_name = QFileDialog.getOpenFileName(
            self, '选择文本文件路径', './', 'All files(*.*);;txt file(*.txt)', 'txt file(*.txt)')
        if file_name[0]:
            self.lineEdit_name_path.setText(file_name[0])

    def get_name_path_from_zip(self):
        dir_name = QFileDialog.getExistingDirectory(
            self, '选择压缩文件路径', './')
        if dir_name:
            self.lineEdit_name_path.setText(dir_name)

    def switch_btn_connect_state(self, radio_btn):
        text = radio_btn.text()
        check_state = radio_btn.isChecked()
        if text == 'text mode' and check_state:
            try:
                self.pushButton_name_path.clicked.disconnect(self.get_name_path_from_zip)
                self.pushButton_name_path.clicked.disconnect(self.get_name_path_from_text)
            except TypeError:
                print(TypeError)
            self.pushButton_name_path.clicked.connect(self.get_name_path_from_text)
            self.label_mode.setText('文本文件路径：')
        if text == 'zip mode' and check_state:
            try:
                self.pushButton_name_path.clicked.disconnect(self.get_name_path_from_text)
                self.pushButton_name_path.clicked.disconnect(self.get_name_path_from_zip)
            except TypeError:
                print(TypeError)
            self.pushButton_name_path.clicked.connect(self.get_name_path_from_zip)
            self.label_mode.setText('压缩文件路径：')

    def get_save_path(self):
        dir_name = QFileDialog.getExistingDirectory(
            self, '选择精轨保存路径', '../')
        if dir_name:
            self.lineEdit_save_path.setText(dir_name)
            self.add_to_idm_thread.save_path = dir_name

    def get_idm_path(self):
        file_name = QFileDialog.getOpenFileName(
            self, '选择IDMan.exe', 'C:/thorly/Softwares/IDM', 'IDMan.exe (IDMan.exe);;exe file(*.exe)')
        if file_name[0]:
            self.lineEdit_idm_path.setText(file_name[0])
            self.add_to_idm_thread.idm_path = file_name[0]
            self.exec_idm_thread.idm_path = file_name[0]

    def get_urls(self):
        path = self.lineEdit_name_path.text()
        if not path:
            self.warning("请设置{}".format(self.label_mode.text()[:-1]))
        elif not os.path.exists(path):
            self.warning("{}不存在，请重新设置".format(self.label_mode.text()[:-1]))
        else:
            self.get_url_thread.name_path = path
            self.get_url_thread.start()

    def set_current_url(self, url):
        def get_image_date(u):
            temp = re.findall(r"\d{8}", u)[-1]
            temp = datetime.datetime.strptime(temp, '%Y%m%d')
            delta = datetime.timedelta(days=-1)
            date = temp + delta
            return date.strftime('%Y%m%d')

        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        html = "{} ({}) 精轨对应的影像日期（点击右侧日期即可下载）：<a href={}>{}</a>".format(time, self.progressBar.value(), url,
                                                                       get_image_date(url))
        self.textEdit_info.insertHtml(html)
        self.textEdit_info.append('\n')

    def add_to_idm(self):
        idm_path = self.lineEdit_idm_path.text()
        save_path = self.lineEdit_save_path.text()
        if not idm_path and not save_path:
            self.warning("请设置精轨保存路径和IDMan.exe路径")
        elif not idm_path and save_path:
            self.warning("请设置IDMan.exe路径")
        elif not save_path and idm_path:
            self.warning("请设置精轨保存路径")
        elif not os.path.exists(save_path) and not os.path.exists(idm_path):
            self.warning("精轨保存路径和IDMan.exe路径不存在，请重新设置")
        elif not os.path.exists(save_path):
            self.warning("精轨保存路径不存在，请重新设置")
        elif not os.path.exists(idm_path):
            self.warning("IDMan.exe路径不存在，请重新设置")
        else:
            if self.add_to_idm_thread.urls:
                self.exec_idm_thread.start()
                self.add_to_idm_thread.start()
            else:
                self.warning("请先抓取精轨链接")

    def success_add_to_idm(self, info):
        self.textEdit_info.setFontUnderline(False)
        self.textEdit_info.setTextColor(QColor('black'))
        self.textEdit_info.append(info)

    def error_add_to_idm(self, info):
        self.textEdit_info.setFontUnderline(False)
        self.textEdit_info.setTextColor(QColor('black'))
        self.textEdit_info.append(info)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
