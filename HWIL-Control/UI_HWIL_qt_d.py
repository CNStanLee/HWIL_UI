# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_HWIL_qt_d.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setWindowModality(QtCore.Qt.NonModal)
        Form.resize(1087, 794)
        font = QtGui.QFont()
        font.setFamily("方正兰亭中黑_GBK")
        font.setPointSize(9)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        Form.setFont(font)
        Form.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        Form.setMouseTracking(False)
        Form.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(25, 25, 25);\n"
"font: 9pt \"方正兰亭中黑_GBK\";")
        self.L_ReceiverRaw = QtWidgets.QLabel(Form)
        self.L_ReceiverRaw.setGeometry(QtCore.QRect(30, 240, 91, 21))
        self.L_ReceiverRaw.setObjectName("L_ReceiverRaw")
        self.L_TransmitterRaw = QtWidgets.QLabel(Form)
        self.L_TransmitterRaw.setGeometry(QtCore.QRect(20, 620, 101, 16))
        self.L_TransmitterRaw.setTextFormat(QtCore.Qt.AutoText)
        self.L_TransmitterRaw.setObjectName("L_TransmitterRaw")
        self.Send_Button = QtWidgets.QPushButton(Form)
        self.Send_Button.setGeometry(QtCore.QRect(300, 750, 75, 23))
        self.Send_Button.setObjectName("Send_Button")
        self.ClearButton = QtWidgets.QPushButton(Form)
        self.ClearButton.setGeometry(QtCore.QRect(320, 240, 75, 23))
        self.ClearButton.setObjectName("ClearButton")
        self.textEdit_Recive = QtWidgets.QTextEdit(Form)
        self.textEdit_Recive.setGeometry(QtCore.QRect(30, 270, 361, 341))
        self.textEdit_Recive.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"background-color: rgb(0, 0, 0);")
        self.textEdit_Recive.setObjectName("textEdit_Recive")
        self.textEdit_Send = QtWidgets.QTextEdit(Form)
        self.textEdit_Send.setGeometry(QtCore.QRect(30, 640, 361, 101))
        self.textEdit_Send.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.textEdit_Send.setObjectName("textEdit_Send")
        self.gridLayoutWidget = QtWidgets.QWidget(Form)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(30, 40, 221, 171))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.Com_Baud_Label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.Com_Baud_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Com_Baud_Label.setObjectName("Com_Baud_Label")
        self.gridLayout.addWidget(self.Com_Baud_Label, 1, 0, 1, 1)
        self.Com_Close_Button = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.Com_Close_Button.setDefault(False)
        self.Com_Close_Button.setObjectName("Com_Close_Button")
        self.gridLayout.addWidget(self.Com_Close_Button, 4, 1, 1, 1)
        self.Com_Name_Label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.Com_Name_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Com_Name_Label.setObjectName("Com_Name_Label")
        self.gridLayout.addWidget(self.Com_Name_Label, 2, 0, 1, 1)
        self.Com_Name_Combo = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.Com_Name_Combo.setObjectName("Com_Name_Combo")
        self.gridLayout.addWidget(self.Com_Name_Combo, 2, 1, 1, 1)
        self.Com_Refresh_Label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.Com_Refresh_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Com_Refresh_Label.setObjectName("Com_Refresh_Label")
        self.gridLayout.addWidget(self.Com_Refresh_Label, 0, 0, 1, 1)
        self.Com_Refresh_Button = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.Com_Refresh_Button.setObjectName("Com_Refresh_Button")
        self.gridLayout.addWidget(self.Com_Refresh_Button, 0, 1, 1, 1)
        self.Com_State_Label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.Com_State_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Com_State_Label.setObjectName("Com_State_Label")
        self.gridLayout.addWidget(self.Com_State_Label, 3, 0, 1, 1)
        self.Com_Baud_Combo = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.Com_Baud_Combo.setEditable(True)
        self.Com_Baud_Combo.setDuplicatesEnabled(False)
        self.Com_Baud_Combo.setModelColumn(0)
        self.Com_Baud_Combo.setObjectName("Com_Baud_Combo")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.gridLayout.addWidget(self.Com_Baud_Combo, 1, 1, 1, 1)
        self.Com_Open_Button = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.Com_Open_Button.setObjectName("Com_Open_Button")
        self.gridLayout.addWidget(self.Com_Open_Button, 3, 1, 1, 1)
        self.Com_isOpenOrNot_Label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.Com_isOpenOrNot_Label.setText("")
        self.Com_isOpenOrNot_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Com_isOpenOrNot_Label.setObjectName("Com_isOpenOrNot_Label")
        self.gridLayout.addWidget(self.Com_isOpenOrNot_Label, 4, 0, 1, 1)
        self.hexSending_checkBox = QtWidgets.QCheckBox(Form)
        self.hexSending_checkBox.setGeometry(QtCore.QRect(200, 750, 91, 31))
        self.hexSending_checkBox.setObjectName("hexSending_checkBox")
        self.hexShowing_checkBox = QtWidgets.QCheckBox(Form)
        self.hexShowing_checkBox.setGeometry(QtCore.QRect(210, 240, 101, 20))
        self.hexShowing_checkBox.setObjectName("hexShowing_checkBox")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(30, 10, 81, 21))
        self.label_3.setObjectName("label_3")
        self.TB_CANMsg = QtWidgets.QTableWidget(Form)
        self.TB_CANMsg.setGeometry(QtCore.QRect(400, 270, 611, 341))
        self.TB_CANMsg.setColumnCount(4)
        self.TB_CANMsg.setObjectName("TB_CANMsg")
        self.TB_CANMsg.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.TB_CANMsg.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.TB_CANMsg.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.TB_CANMsg.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.TB_CANMsg.setHorizontalHeaderItem(3, item)
        self.TB_CANMsg.horizontalHeader().setDefaultSectionSize(150)
        self.L_CANMessageList = QtWidgets.QLabel(Form)
        self.L_CANMessageList.setGeometry(QtCore.QRect(400, 240, 131, 16))
        self.L_CANMessageList.setTextFormat(QtCore.Qt.AutoText)
        self.L_CANMessageList.setObjectName("L_CANMessageList")
        self.L_Attacker = QtWidgets.QLabel(Form)
        self.L_Attacker.setGeometry(QtCore.QRect(580, 70, 67, 17))
        self.L_Attacker.setFrameShape(QtWidgets.QFrame.Box)
        self.L_Attacker.setObjectName("L_Attacker")
        self.L_ECU1 = QtWidgets.QLabel(Form)
        self.L_ECU1.setGeometry(QtCore.QRect(260, 70, 67, 17))
        self.L_ECU1.setFrameShape(QtWidgets.QFrame.Box)
        self.L_ECU1.setObjectName("L_ECU1")
        self.L_ECU2 = QtWidgets.QLabel(Form)
        self.L_ECU2.setGeometry(QtCore.QRect(340, 70, 67, 17))
        self.L_ECU2.setFrameShape(QtWidgets.QFrame.Box)
        self.L_ECU2.setObjectName("L_ECU2")
        self.L_ECU3 = QtWidgets.QLabel(Form)
        self.L_ECU3.setGeometry(QtCore.QRect(420, 70, 67, 17))
        self.L_ECU3.setFrameShape(QtWidgets.QFrame.Box)
        self.L_ECU3.setObjectName("L_ECU3")
        self.L_ECU4 = QtWidgets.QLabel(Form)
        self.L_ECU4.setGeometry(QtCore.QRect(500, 70, 67, 17))
        self.L_ECU4.setFrameShape(QtWidgets.QFrame.Box)
        self.L_ECU4.setObjectName("L_ECU4")
        self.Btn_DosAttack = QtWidgets.QPushButton(Form)
        self.Btn_DosAttack.setGeometry(QtCore.QRect(620, 750, 106, 23))
        self.Btn_DosAttack.setObjectName("Btn_DosAttack")
        self.Btn_Replay = QtWidgets.QPushButton(Form)
        self.Btn_Replay.setGeometry(QtCore.QRect(400, 750, 106, 23))
        self.Btn_Replay.setObjectName("Btn_Replay")
        self.L_Main = QtWidgets.QLabel(Form)
        self.L_Main.setGeometry(QtCore.QRect(260, 90, 67, 17))
        self.L_Main.setFrameShape(QtWidgets.QFrame.Box)
        self.L_Main.setObjectName("L_Main")
        self.L_Life1 = QtWidgets.QLabel(Form)
        self.L_Life1.setGeometry(QtCore.QRect(260, 110, 67, 17))
        self.L_Life1.setFrameShape(QtWidgets.QFrame.Box)
        self.L_Life1.setObjectName("L_Life1")
        self.L_ECU = QtWidgets.QLabel(Form)
        self.L_ECU.setGeometry(QtCore.QRect(260, 130, 67, 17))
        self.L_ECU.setFrameShape(QtWidgets.QFrame.Box)
        self.L_ECU.setObjectName("L_ECU")
        self.L_TCU = QtWidgets.QLabel(Form)
        self.L_TCU.setGeometry(QtCore.QRect(260, 150, 67, 17))
        self.L_TCU.setFrameShape(QtWidgets.QFrame.Box)
        self.L_TCU.setObjectName("L_TCU")
        self.L_Slight = QtWidgets.QLabel(Form)
        self.L_Slight.setGeometry(QtCore.QRect(340, 150, 67, 17))
        self.L_Slight.setFrameShape(QtWidgets.QFrame.Box)
        self.L_Slight.setObjectName("L_Slight")
        self.L_Airbag = QtWidgets.QLabel(Form)
        self.L_Airbag.setGeometry(QtCore.QRect(340, 130, 67, 17))
        self.L_Airbag.setFrameShape(QtWidgets.QFrame.Box)
        self.L_Airbag.setObjectName("L_Airbag")
        self.L_Life2 = QtWidgets.QLabel(Form)
        self.L_Life2.setGeometry(QtCore.QRect(340, 110, 67, 17))
        self.L_Life2.setFrameShape(QtWidgets.QFrame.Box)
        self.L_Life2.setObjectName("L_Life2")
        self.L_IO1 = QtWidgets.QLabel(Form)
        self.L_IO1.setGeometry(QtCore.QRect(340, 90, 67, 17))
        self.L_IO1.setFrameShape(QtWidgets.QFrame.Box)
        self.L_IO1.setObjectName("L_IO1")
        self.L_Collision = QtWidgets.QLabel(Form)
        self.L_Collision.setGeometry(QtCore.QRect(420, 130, 67, 17))
        self.L_Collision.setFrameShape(QtWidgets.QFrame.Box)
        self.L_Collision.setObjectName("L_Collision")
        self.L_IO2 = QtWidgets.QLabel(Form)
        self.L_IO2.setGeometry(QtCore.QRect(420, 90, 67, 17))
        self.L_IO2.setFrameShape(QtWidgets.QFrame.Box)
        self.L_IO2.setObjectName("L_IO2")
        self.L_Life3 = QtWidgets.QLabel(Form)
        self.L_Life3.setGeometry(QtCore.QRect(420, 110, 67, 17))
        self.L_Life3.setFrameShape(QtWidgets.QFrame.Box)
        self.L_Life3.setObjectName("L_Life3")
        self.L_Brake = QtWidgets.QLabel(Form)
        self.L_Brake.setGeometry(QtCore.QRect(420, 150, 67, 17))
        self.L_Brake.setFrameShape(QtWidgets.QFrame.Box)
        self.L_Brake.setObjectName("L_Brake")
        self.L_Steering = QtWidgets.QLabel(Form)
        self.L_Steering.setGeometry(QtCore.QRect(420, 170, 67, 17))
        self.L_Steering.setFrameShape(QtWidgets.QFrame.Box)
        self.L_Steering.setObjectName("L_Steering")
        self.L_IO3 = QtWidgets.QLabel(Form)
        self.L_IO3.setGeometry(QtCore.QRect(500, 90, 67, 17))
        self.L_IO3.setFrameShape(QtWidgets.QFrame.Box)
        self.L_IO3.setObjectName("L_IO3")
        self.L_FLight = QtWidgets.QLabel(Form)
        self.L_FLight.setGeometry(QtCore.QRect(500, 110, 67, 17))
        self.L_FLight.setFrameShape(QtWidgets.QFrame.Box)
        self.L_FLight.setObjectName("L_FLight")
        self.L_BLight = QtWidgets.QLabel(Form)
        self.L_BLight.setGeometry(QtCore.QRect(500, 130, 67, 17))
        self.L_BLight.setFrameShape(QtWidgets.QFrame.Box)
        self.L_BLight.setObjectName("L_BLight")
        self.L_FLightB = QtWidgets.QLabel(Form)
        self.L_FLightB.setGeometry(QtCore.QRect(420, 190, 67, 17))
        self.L_FLightB.setFrameShape(QtWidgets.QFrame.Box)
        self.L_FLightB.setObjectName("L_FLightB")
        self.L_BLightB = QtWidgets.QLabel(Form)
        self.L_BLightB.setGeometry(QtCore.QRect(420, 210, 67, 17))
        self.L_BLightB.setFrameShape(QtWidgets.QFrame.Box)
        self.L_BLightB.setObjectName("L_BLightB")
        self.Btn_ClearData = QtWidgets.QPushButton(Form)
        self.Btn_ClearData.setGeometry(QtCore.QRect(770, 200, 106, 23))
        self.Btn_ClearData.setObjectName("Btn_ClearData")
        self.Btn_ExportData = QtWidgets.QPushButton(Form)
        self.Btn_ExportData.setGeometry(QtCore.QRect(890, 200, 106, 23))
        self.Btn_ExportData.setObjectName("Btn_ExportData")
        self.L_Braker = QtWidgets.QLabel(Form)
        self.L_Braker.setGeometry(QtCore.QRect(260, 170, 67, 17))
        self.L_Braker.setFrameShape(QtWidgets.QFrame.Box)
        self.L_Braker.setObjectName("L_Braker")
        self.L_SpoofingEditor = QtWidgets.QLabel(Form)
        self.L_SpoofingEditor.setGeometry(QtCore.QRect(400, 620, 521, 16))
        self.L_SpoofingEditor.setTextFormat(QtCore.Qt.AutoText)
        self.L_SpoofingEditor.setObjectName("L_SpoofingEditor")
        self.TB_SpooftingEditor = QtWidgets.QTableWidget(Form)
        self.TB_SpooftingEditor.setGeometry(QtCore.QRect(400, 640, 611, 101))
        self.TB_SpooftingEditor.setColumnCount(4)
        self.TB_SpooftingEditor.setObjectName("TB_SpooftingEditor")
        self.TB_SpooftingEditor.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.TB_SpooftingEditor.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.TB_SpooftingEditor.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.TB_SpooftingEditor.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.TB_SpooftingEditor.setHorizontalHeaderItem(3, item)
        self.TB_SpooftingEditor.horizontalHeader().setDefaultSectionSize(150)
        self.TE_Filter = QtWidgets.QTextEdit(Form)
        self.TE_Filter.setGeometry(QtCore.QRect(630, 230, 371, 31))
        self.TE_Filter.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.TE_Filter.setObjectName("TE_Filter")
        self.Btn_AutoInject = QtWidgets.QPushButton(Form)
        self.Btn_AutoInject.setGeometry(QtCore.QRect(730, 750, 106, 23))
        self.Btn_AutoInject.setObjectName("Btn_AutoInject")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(260, 10, 81, 21))
        self.label_4.setObjectName("label_4")
        self.Btn_Spoofing = QtWidgets.QPushButton(Form)
        self.Btn_Spoofing.setGeometry(QtCore.QRect(510, 750, 106, 23))
        self.Btn_Spoofing.setObjectName("Btn_Spoofing")
        self.CB_AutoSlide = QtWidgets.QCheckBox(Form)
        self.CB_AutoSlide.setGeometry(QtCore.QRect(530, 240, 101, 20))
        self.CB_AutoSlide.setChecked(True)
        self.CB_AutoSlide.setObjectName("CB_AutoSlide")
        self.Btn_Filter = QtWidgets.QPushButton(Form)
        self.Btn_Filter.setGeometry(QtCore.QRect(630, 200, 106, 23))
        self.Btn_Filter.setObjectName("Btn_Filter")
        self.L_Replay = QtWidgets.QLabel(Form)
        self.L_Replay.setGeometry(QtCore.QRect(1020, 670, 61, 20))
        self.L_Replay.setTextFormat(QtCore.Qt.AutoText)
        self.L_Replay.setObjectName("L_Replay")
        self.L_Spoof = QtWidgets.QLabel(Form)
        self.L_Spoof.setGeometry(QtCore.QRect(1020, 710, 61, 20))
        self.L_Spoof.setTextFormat(QtCore.Qt.AutoText)
        self.L_Spoof.setObjectName("L_Spoof")
        self.Btn_Download = QtWidgets.QPushButton(Form)
        self.Btn_Download.setGeometry(QtCore.QRect(510, 200, 106, 23))
        self.Btn_Download.setObjectName("Btn_Download")
        self.CB_Circular = QtWidgets.QCheckBox(Form)
        self.CB_Circular.setGeometry(QtCore.QRect(840, 750, 101, 20))
        self.CB_Circular.setChecked(False)
        self.CB_Circular.setObjectName("CB_Circular")
        self.Btn_StopInject = QtWidgets.QPushButton(Form)
        self.Btn_StopInject.setGeometry(QtCore.QRect(910, 750, 106, 23))
        self.Btn_StopInject.setObjectName("Btn_StopInject")

        self.retranslateUi(Form)
        self.ClearButton.clicked.connect(self.textEdit_Recive.clear) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "CAN HWIL Terminal"))
        self.L_ReceiverRaw.setText(_translate("Form", "Receiver Raw"))
        self.L_TransmitterRaw.setText(_translate("Form", "Transmitter Raw"))
        self.Send_Button.setText(_translate("Form", "Send"))
        self.ClearButton.setText(_translate("Form", "Clear"))
        self.textEdit_Recive.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'方正兰亭中黑_GBK\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'SimSun\';\"><br /></p></body></html>"))
        self.Com_Baud_Label.setText(_translate("Form", "Baud Rate"))
        self.Com_Close_Button.setText(_translate("Form", "Close"))
        self.Com_Name_Label.setText(_translate("Form", "Serial Select"))
        self.Com_Refresh_Label.setText(_translate("Form", "Serial Search"))
        self.Com_Refresh_Button.setText(_translate("Form", "Refresh"))
        self.Com_State_Label.setText(_translate("Form", "Activation"))
        self.Com_Baud_Combo.setCurrentText(_translate("Form", "1200"))
        self.Com_Baud_Combo.setItemText(0, _translate("Form", "1200"))
        self.Com_Baud_Combo.setItemText(1, _translate("Form", "2400"))
        self.Com_Baud_Combo.setItemText(2, _translate("Form", "4800"))
        self.Com_Baud_Combo.setItemText(3, _translate("Form", "9600"))
        self.Com_Baud_Combo.setItemText(4, _translate("Form", "14400"))
        self.Com_Baud_Combo.setItemText(5, _translate("Form", "19200"))
        self.Com_Baud_Combo.setItemText(6, _translate("Form", "38400"))
        self.Com_Baud_Combo.setItemText(7, _translate("Form", "43000"))
        self.Com_Baud_Combo.setItemText(8, _translate("Form", "57600"))
        self.Com_Baud_Combo.setItemText(9, _translate("Form", "76800"))
        self.Com_Baud_Combo.setItemText(10, _translate("Form", "115200"))
        self.Com_Baud_Combo.setItemText(11, _translate("Form", "128000"))
        self.Com_Baud_Combo.setItemText(12, _translate("Form", "230400"))
        self.Com_Baud_Combo.setItemText(13, _translate("Form", "256000"))
        self.Com_Baud_Combo.setItemText(14, _translate("Form", "460800"))
        self.Com_Baud_Combo.setItemText(15, _translate("Form", "921600"))
        self.Com_Baud_Combo.setItemText(16, _translate("Form", "1382400"))
        self.Com_Open_Button.setText(_translate("Form", "Open"))
        self.hexSending_checkBox.setText(_translate("Form", "Hex Format"))
        self.hexShowing_checkBox.setText(_translate("Form", "Hex Format"))
        self.label_3.setText(_translate("Form", "Basic Setup"))
        item = self.TB_CANMsg.horizontalHeaderItem(0)
        item.setText(_translate("Form", "OriData"))
        item = self.TB_CANMsg.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Addr"))
        item = self.TB_CANMsg.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Data"))
        item = self.TB_CANMsg.horizontalHeaderItem(3)
        item.setText(_translate("Form", "AtkTag"))
        self.L_CANMessageList.setText(_translate("Form", "CAN Message List"))
        self.L_Attacker.setText(_translate("Form", "Attacker"))
        self.L_ECU1.setText(_translate("Form", "ECU1"))
        self.L_ECU2.setText(_translate("Form", "ECU2"))
        self.L_ECU3.setText(_translate("Form", "ECU3"))
        self.L_ECU4.setText(_translate("Form", "ECU4"))
        self.Btn_DosAttack.setText(_translate("Form", "Dos Attack"))
        self.Btn_Replay.setText(_translate("Form", "Replay"))
        self.L_Main.setText(_translate("Form", "Main"))
        self.L_Life1.setText(_translate("Form", "Life"))
        self.L_ECU.setText(_translate("Form", "ECU"))
        self.L_TCU.setText(_translate("Form", "TCU"))
        self.L_Slight.setText(_translate("Form", "Slight"))
        self.L_Airbag.setText(_translate("Form", "Airbag"))
        self.L_Life2.setText(_translate("Form", "Life"))
        self.L_IO1.setText(_translate("Form", "IO1"))
        self.L_Collision.setText(_translate("Form", "Collision"))
        self.L_IO2.setText(_translate("Form", "IO2"))
        self.L_Life3.setText(_translate("Form", "Life"))
        self.L_Brake.setText(_translate("Form", "Brake"))
        self.L_Steering.setText(_translate("Form", "Steering"))
        self.L_IO3.setText(_translate("Form", "IO3"))
        self.L_FLight.setText(_translate("Form", "FLight"))
        self.L_BLight.setText(_translate("Form", "BLight"))
        self.L_FLightB.setText(_translate("Form", "FLightB"))
        self.L_BLightB.setText(_translate("Form", "BLightB"))
        self.Btn_ClearData.setText(_translate("Form", "Clear Data"))
        self.Btn_ExportData.setText(_translate("Form", "Export Data"))
        self.L_Braker.setText(_translate("Form", "Braker"))
        self.L_SpoofingEditor.setText(_translate("Form", "Attack Editor(Line 1 Oridata, Line 2 SpoofingData(editable))"))
        item = self.TB_SpooftingEditor.horizontalHeaderItem(0)
        item.setText(_translate("Form", "OriData"))
        item = self.TB_SpooftingEditor.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Addr"))
        item = self.TB_SpooftingEditor.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Data"))
        item = self.TB_SpooftingEditor.horizontalHeaderItem(3)
        item.setText(_translate("Form", "AtkTag"))
        self.Btn_AutoInject.setText(_translate("Form", "Auto Inject"))
        self.label_4.setText(_translate("Form", "Topo"))
        self.Btn_Spoofing.setText(_translate("Form", "Spoofing"))
        self.CB_AutoSlide.setText(_translate("Form", "AutoSlide"))
        self.Btn_Filter.setText(_translate("Form", "Filter"))
        self.L_Replay.setText(_translate("Form", "Replay"))
        self.L_Spoof.setText(_translate("Form", "Spoof"))
        self.Btn_Download.setText(_translate("Form", "DownLoad elfs"))
        self.CB_Circular.setText(_translate("Form", "Circular"))
        self.Btn_StopInject.setText(_translate("Form", "Stop Inject"))