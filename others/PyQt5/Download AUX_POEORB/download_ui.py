# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'download_ui.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(852, 407)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(9)
        Form.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/orbit.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.radioButton_text = QtWidgets.QRadioButton(Form)
        self.radioButton_text.setChecked(True)
        self.radioButton_text.setObjectName("radioButton_text")
        self.gridLayout.addWidget(self.radioButton_text, 0, 1, 1, 1)
        self.radioButton_zip = QtWidgets.QRadioButton(Form)
        self.radioButton_zip.setObjectName("radioButton_zip")
        self.gridLayout.addWidget(self.radioButton_zip, 0, 2, 1, 1)
        self.label_mode = QtWidgets.QLabel(Form)
        self.label_mode.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_mode.setObjectName("label_mode")
        self.gridLayout.addWidget(self.label_mode, 1, 0, 1, 1)
        self.lineEdit_name_path = QtWidgets.QLineEdit(Form)
        self.lineEdit_name_path.setMinimumSize(QtCore.QSize(0, 32))
        self.lineEdit_name_path.setObjectName("lineEdit_name_path")
        self.gridLayout.addWidget(self.lineEdit_name_path, 1, 1, 1, 2)
        self.pushButton_name_path = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_name_path.sizePolicy().hasHeightForWidth())
        self.pushButton_name_path.setSizePolicy(sizePolicy)
        self.pushButton_name_path.setMinimumSize(QtCore.QSize(0, 32))
        self.pushButton_name_path.setObjectName("pushButton_name_path")
        self.gridLayout.addWidget(self.pushButton_name_path, 1, 3, 1, 1)
        self.pushButton_get_urls = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_get_urls.sizePolicy().hasHeightForWidth())
        self.pushButton_get_urls.setSizePolicy(sizePolicy)
        self.pushButton_get_urls.setMinimumSize(QtCore.QSize(0, 32))
        self.pushButton_get_urls.setObjectName("pushButton_get_urls")
        self.gridLayout.addWidget(self.pushButton_get_urls, 1, 4, 1, 1)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.lineEdit_save_path = QtWidgets.QLineEdit(Form)
        self.lineEdit_save_path.setMinimumSize(QtCore.QSize(0, 32))
        self.lineEdit_save_path.setObjectName("lineEdit_save_path")
        self.gridLayout.addWidget(self.lineEdit_save_path, 2, 1, 1, 2)
        self.pushButton_save_path = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_save_path.sizePolicy().hasHeightForWidth())
        self.pushButton_save_path.setSizePolicy(sizePolicy)
        self.pushButton_save_path.setMinimumSize(QtCore.QSize(0, 32))
        self.pushButton_save_path.setObjectName("pushButton_save_path")
        self.gridLayout.addWidget(self.pushButton_save_path, 2, 3, 1, 1)
        self.pushButton_add_to_idm = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_add_to_idm.sizePolicy().hasHeightForWidth())
        self.pushButton_add_to_idm.setSizePolicy(sizePolicy)
        self.pushButton_add_to_idm.setObjectName("pushButton_add_to_idm")
        self.gridLayout.addWidget(self.pushButton_add_to_idm, 2, 4, 2, 1)
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.lineEdit_idm_path = QtWidgets.QLineEdit(Form)
        self.lineEdit_idm_path.setMinimumSize(QtCore.QSize(0, 32))
        self.lineEdit_idm_path.setObjectName("lineEdit_idm_path")
        self.gridLayout.addWidget(self.lineEdit_idm_path, 3, 1, 1, 2)
        self.pushButton_idm_path = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_idm_path.sizePolicy().hasHeightForWidth())
        self.pushButton_idm_path.setSizePolicy(sizePolicy)
        self.pushButton_idm_path.setMinimumSize(QtCore.QSize(0, 32))
        self.pushButton_idm_path.setObjectName("pushButton_idm_path")
        self.gridLayout.addWidget(self.pushButton_idm_path, 3, 3, 1, 1)
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.textEdit_info = TextEdit(Form)
        self.textEdit_info.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.textEdit_info.setReadOnly(True)
        self.textEdit_info.setObjectName("textEdit_info")
        self.gridLayout.addWidget(self.textEdit_info, 5, 0, 1, 5)
        self.progressBar = QtWidgets.QProgressBar(Form)
        self.progressBar.setEnabled(True)
        self.progressBar.setMinimumSize(QtCore.QSize(0, 32))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 4, 1, 1, 4)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Download AUX_POEORB"))
        self.label.setText(_translate("Form", "模式："))
        self.radioButton_text.setText(_translate("Form", "text mode"))
        self.radioButton_zip.setText(_translate("Form", "zip mode"))
        self.label_mode.setText(_translate("Form", "文本文件路径："))
        self.pushButton_name_path.setText(_translate("Form", "选择路径"))
        self.pushButton_get_urls.setText(_translate("Form", "抓取链接"))
        self.label_3.setText(_translate("Form", "保存路径："))
        self.pushButton_save_path.setText(_translate("Form", "选择路径"))
        self.pushButton_add_to_idm.setText(_translate("Form", "添加任务\n"
"到IDM"))
        self.label_4.setText(_translate("Form", "IDMan.exe路径："))
        self.pushButton_idm_path.setText(_translate("Form", "选择路径"))
        self.label_5.setText(_translate("Form", "抓取链接进度："))
        self.textEdit_info.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Consolas\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic; color:#000000;\">@author </span><span style=\" color:#000000;\"> : leiyuan </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic; color:#000000;\">@version</span><span style=\" color:#000000;\"> : 3.5</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic; color:#000000;\">@date </span><span style=\" color:#000000;\">   : 2020-03-05</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; color:#000000;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" color:#000000;\">text mode: 从\'文本文件\'获取Sentinel-1A/B影像名，用于获取影像日期，从而获取精轨日期</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; color:#000000;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" color:#000000;\">zip  mode: 从\'压缩文件\'获取Sentinel-1A/B影像名，用于获取影像日期，从而获取精轨日期</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; color:#000000;\"><br /></p></body></html>"))
        self.progressBar.setFormat(_translate("Form", "%v/%m"))
from textedit import TextEdit
import res_rc
