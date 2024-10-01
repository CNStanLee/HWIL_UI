# 逻辑文件

import re
import sys
import binascii
import time
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtWidgets import *
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import *

from UI_HWIL import Ui_Form
from PyQt5.QtCore import QDate

import os
import subprocess
import pandas as pd
from datetime import datetime



class MyMainWindow(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        # set instance
        self.CreateItems()
        # set signal and slot
        self.CreateSignalSlot()
        # set receive buffer
        self.received_data = ""
        # data list
        self.parsed_data = []
        # 设置第一列宽度为200像素
        self.TB_CANMsg.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.TB_CANMsg.setColumnWidth(0, 210)
        # 设置第二列宽度为50像素
        self.TB_CANMsg.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.TB_CANMsg.setColumnWidth(1, 60)
        # 设置第三列宽度为150像素
        self.TB_CANMsg.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.TB_CANMsg.setColumnWidth(2, 150)

        # 设置第一列宽度为200像素
        self.TB_SpooftingEditor.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.TB_SpooftingEditor.setColumnWidth(0, 210)
        # 设置第二列宽度为50像素
        self.TB_SpooftingEditor.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.TB_SpooftingEditor.setColumnWidth(1, 60)
        # 设置第三列宽度为150像素
        self.TB_SpooftingEditor.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.TB_SpooftingEditor.setColumnWidth(2, 150)

        self.TB_SpooftingEditor.insertRow(0)
        self.TB_SpooftingEditor.insertRow(1)


        self.L_State.setStyleSheet("color: green;")


        self.auto_injection_stop_flag = False
        # Global Variable

        self.controller_life_signal_last = "00"
        self.ecu1_life_signal_last = "00"
        self.ecu2_life_signal_last = "00"
        self.ecu3_life_signal_last = "00"
        self.ecu4_life_signal_last = "00"

        self.controller_life_signal_last2 = "00"
        self.ecu1_life_signal_last2 = "00"
        self.ecu2_life_signal_last2 = "00"
        self.ecu3_life_signal_last2 = "00"
        self.ecu4_life_signal_last2 = "00"

        self.controller_life_signal_last3 = "00"
        self.ecu1_life_signal_last3 = "00"
        self.ecu2_life_signal_last3 = "00"
        self.ecu3_life_signal_last3 = "00"
        self.ecu4_life_signal_last3 = "00"

        self.controller_life_signal_bl = False
        self.ecu1_life_signal_bl = False
        self.ecu2_life_signal_bl = False
        self.ecu3_life_signal_bl = False
        self.ecu4_life_signal_bl = False

        # 初始化变量和定时器
        self.variable = None
        self.is_alive = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_variable_changes)

        # 启动定时器，每秒触发一次
        self.timer.start(1200)  # 1000毫秒 = 1秒

        # buffer solve
        self.variable = None
        self.is_alive = False
        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.check_msg)

        # 启动定时器，每秒触发一次
        self.timer2.start(10)

        self.AtkFlag = "Normal"

        self.dos_attack_count = 0

        self.atk_list = []

        self.auto_inject_msg = ""

        self.auto_injection_timer = QTimer()


        # make ecu status stable
        # 状态稳定确认计数器
        self.ecu_status_counter = 0
        self.tcu_status_counter = 0
        self.braker_status_counter = 0

        # 状态变化的阈值（如5次确认后更新状态）
        self.stable_threshold = 1

        # 初始状态
        self.last_ecu_status = None
        self.last_tcu_status = None
        self.last_braker_status = None

        self.last_airbag_status = None  # Cache for AirBag status
        self.last_scl_status = None  # Cache for SCL status

        self.last_cds_status = None  # Cache for CDS (Collision Detection System) status
        self.last_bds_status = None  # Cache for BDS (Brake Detection System) status
        self.last_slb_status = None  # Cache for SLB (Steering Light B) status
        self.last_flb_status = None  # Cache for FLB (Front Light B) status
        self.last_blb_status = None  # Cache for BLB (Back Light B) status

        self.ecu_status_stable_count = 0  # Tracks stability for ECU status
        self.tcu_status_stable_count = 0  # Tracks stability for TCU status
        self.braker_status_stable_count = 0  # Tracks stability for Braker status

        self.check_times = 3



    def check_msg(self):
        # check if contain "\r\n"
        if "\r\n" in self.received_data:
            # find index
            end_index = self.received_data.index("\r\n")

            # 检查前面是否有 "listen:"
            start_index = self.received_data.find("listen:")
            if start_index != -1 and start_index < end_index:
                # 提取 listen: 到 \r\n 之间的数据并打印
                # data_of_interest = self.received_data[start_index:end_index]
                data_of_interest = self.received_data[start_index + len("listen:"):end_index]
                #print(data_of_interest)
                # save the data to the list
                #parsed_bytes = bytes.fromhex(data_of_interest)
                parsed_bytes = "tst"
                self.parsed_data.append((data_of_interest, parsed_bytes))
                # check saved data
                last_data = self.parsed_data[-1]
                # print("Original string:", last_data[0])
                # print("Second byte:", last_data[1][1])
                # 插入一行到QTableWidget中
                row_position = self.TB_CANMsg.rowCount()
                self.TB_CANMsg.insertRow(row_position)

                # 设置每列的数据
                original_data_item = QTableWidgetItem(last_data[0])
                address_item = QTableWidgetItem(str(last_data[0][2:8]))  # 字节信息的1, 2, 3字节
                data_item = QTableWidgetItem(str(last_data[0][8:26]))  # 字节信息的5-12字节
                atk_item = QTableWidgetItem(str(self.AtkFlag))
                # 将项目添加到相应的列中
                self.TB_CANMsg.setItem(row_position, 0, original_data_item)
                self.TB_CANMsg.setItem(row_position, 1, address_item)
                self.TB_CANMsg.setItem(row_position, 2, data_item)
                self.TB_CANMsg.setItem(row_position, 3, atk_item)
                if self.CB_AutoSlide.isChecked():
                    self.TB_CANMsg.scrollToBottom()
                # self.TB_CANMsg.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                self.receive_data_analysis()

                # 清空暂存字符串，包括 \r\n 前的数据
            self.received_data = self.received_data[end_index + 2:]

    def check_variable_changes(self):
        # print("10s check life signal")

        self.controller_life_signal_bl = False
        self.ecu1_life_signal_bl = False
        self.ecu2_life_signal_bl = False
        self.ecu3_life_signal_bl = False
        self.ecu4_life_signal_bl = False

        self.controller_life_signal_bl = ((self.controller_life_signal_last2 != self.controller_life_signal_last) | (self.controller_life_signal_last3 != self.controller_life_signal_last2))
        self.ecu1_life_signal_bl = ((self.ecu1_life_signal_last2 != self.ecu1_life_signal_last      ) | (self.ecu1_life_signal_last3 != self.ecu1_life_signal_last))
        self.ecu2_life_signal_bl = ((self.ecu2_life_signal_last2 != self.ecu2_life_signal_last    ) | (self.ecu2_life_signal_last3 != self.ecu2_life_signal_last))
        self.ecu3_life_signal_bl = ((self.ecu3_life_signal_last2 != self.ecu3_life_signal_last      ) | (self.ecu3_life_signal_last3 != self.ecu3_life_signal_last))
        self.ecu4_life_signal_bl = ((self.ecu4_life_signal_last2 != self.ecu4_life_signal_last      ) | (self.ecu4_life_signal_last3 != self.ecu4_life_signal_last))

        if self.ecu1_life_signal_bl:
            self.L_Life1.setStyleSheet("background-color: green")
        else:
            self.L_Life1.setStyleSheet("")
            self.L_ECU.setStyleSheet("")
            self.L_TCU.setStyleSheet("")
            self.L_Braker.setStyleSheet("")

        if self.ecu2_life_signal_bl:
            self.L_Life2.setStyleSheet("background-color: green")
        else:
            self.L_Life2.setStyleSheet("")
            self.L_Airbag.setStyleSheet("")
            self.L_Slight.setStyleSheet("")

        if self.ecu3_life_signal_bl:
            self.L_Life3.setStyleSheet("background-color: green")
        else:
            self.L_Life3.setStyleSheet("")
            self.L_Collision.setStyleSheet("")
            self.L_Brake.setStyleSheet("")
            self.L_Steering.setStyleSheet("")
            self.L_FLightB.setStyleSheet("")
            self.L_BLightB.setStyleSheet("")

        self.controller_life_signal_last3 = self.controller_life_signal_last2
        self.ecu1_life_signal_last3 = self.ecu1_life_signal_last2
        self.ecu2_life_signal_last3 = self.ecu2_life_signal_last2
        self.ecu3_life_signal_last3 = self.ecu3_life_signal_last2
        self.ecu4_life_signal_last3 = self.ecu4_life_signal_last2

        self.controller_life_signal_last2 = self.controller_life_signal_last
        self.ecu1_life_signal_last2 = self.ecu1_life_signal_last
        self.ecu2_life_signal_last2 = self.ecu2_life_signal_last
        self.ecu3_life_signal_last2 = self.ecu3_life_signal_last
        self.ecu4_life_signal_last2 = self.ecu4_life_signal_last


        

    def CreateItems(self):
        # Qt 串口类
        self.com = QSerialPort()
        # # Qt 定时器类
        # self.timer = QTimer(self) #初始化一个定时器
        # self.timer.timeout.connect(self.ShowTime) #计时结束调用operate()方法
        # self.timer.start(100) #设置计时间隔 100ms 并启动
        self.TB_CANMsg.itemClicked.connect(self.on_item_clicked)

    def on_item_clicked(self, item):
        # 获取点击的行
        row = item.row()
        self.TB_SpooftingEditor.clearContents()

        # 获取该行的每一列数据并设置到TB_SpooftingEditor的第一行相应列中
        for col in range(self.TB_CANMsg.columnCount()):
            value = self.TB_CANMsg.item(row, col).text()
            self.TB_SpooftingEditor.setItem(0, col, QTableWidgetItem(str(value)))
        for col in range(self.TB_CANMsg.columnCount()):
            value = self.TB_CANMsg.item(row, col).text()
            self.TB_SpooftingEditor.setItem(1, col, QTableWidgetItem(str(value)))
            #self.TB_SpooftingEditor.setItem(0, col, QTableWidgetItem("test"))

    # 设置信号与槽
    def CreateSignalSlot(self):
        self.Com_Open_Button.clicked.connect(self.Com_Open_Button_clicked)
        self.Com_Close_Button.clicked.connect(self.Com_Close_Button_clicked)
        self.Send_Button.clicked.connect(self.SendButton_clicked)
        self.Com_Refresh_Button.clicked.connect(self.Com_Refresh_Button_Clicked)
        self.com.readyRead.connect(self.Com_Receive_Data)  # 接收数据
        self.hexSending_checkBox.stateChanged.connect(self.hexShowingClicked)
        self.hexSending_checkBox.stateChanged.connect(self.hexSendingClicked)
        # self.About_Button.clicked.connect(self.Goto_GitHub)
        self.Btn_ClearData.clicked.connect(self.Btn_ClearDataOnclickListener)
        self.Btn_Replay.clicked.connect(self.Btn_ReplayOnclickListener)
        self.Btn_Spoofing.clicked.connect(self.Btn_SpoofingOnClickListener)
        self.Btn_DosAttack.clicked.connect(self.Btn_DosAttackOnClickListener)
        self.Btn_Download.clicked.connect(self.Btn_DownloadOnClickListener)
        self.Btn_AutoInject.clicked.connect(self.Btn_AutoInjectOnClickListener)
        self.Btn_StopInject.clicked.connect(self.Btn_StopInjectOnClickListener)
        self.Btn_ExportData.clicked.connect(self.Btn_ExportDataOnClickListener)

    def extract_data(self, row, data):
        # 提取数据
        timestamp = row  # 时间戳，即行号
        address = data[0][4:8]  # 地址后两位
        length = int(data[0][1:2], 16)  # 数据长度
        payload = [data[0][10+i*2:12+i*2] for i in range(8)]  # 数据部分，将十六进制字符串转换为整数列表
        label = data[3]  # 标签
        return [timestamp, address, length] + payload + [label]
    def Btn_ExportDataOnClickListener(self):
        print("Export Dataset")
        row_count = self.TB_CANMsg.rowCount()


        data_list = []
        for row in range(row_count):
            row_data = [self.TB_CANMsg.item(row, col).text() for col in range(4)]  # 获取前4列数据
            extracted_data = self.extract_data(row, row_data)
            data_list.append(extracted_data)

        # 构建DataFrame
        df = pd.DataFrame(data_list,
                          columns=['Timestamp', 'Address', 'Length', 'Data1', 'Data2', 'Data3', 'Data4', 'Data5',
                                   'Data6', 'Data7', 'Data8', 'Label'])

        # 将DataFrame保存为CSV文件
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f'Dataset/export_data_{current_time}.csv'
        df.to_csv(file_name, index=False)
        print("clear data list")
        self.TB_CANMsg.clearContents()
        self.parsed_data.clear()
        self.TB_CANMsg.setRowCount(0)

    def Btn_StopInjectOnClickListener(self):
        print("Stop Auto Inject")
        if self.auto_injection_timer.isActive():
            self.auto_injection_timer.stop()
            #self.auto_injection_stop_flag = True
            self.L_State.setText("State: No Auto Instance")
            self.L_State.setStyleSheet("color: green;")
            print("Auto Injection stopped")
        else:
            print("Auto Injection is not activated")

    def Btn_AutoInjectOnClickListener(self):
        print("Auto Attack Injection begin")
        df = pd.read_csv('TestInstance/Instance2.csv')
        self.atk_list = df.values.tolist()
        for row in self.atk_list:
            atk_type = row[1]
            atk_msg = row[2]
            print("atk_type:" + atk_type + ";atk_msg:" + atk_msg)
        # init the attack timer
        self.auto_injection_timer = QTimer()
        self.auto_injection_timer.timeout.connect(self.auto_injection_excute_atk)
        self.auto_injection_timer.start(12000)

    def auto_injection_excute_atk(self):
        print("execute one atk")
        if self.atk_list:
            atk_unit = self.atk_list.pop(0)
            print(atk_unit)
            atk_type = atk_unit[1]
            atk_msg = atk_unit[2]

            self.L_State.setText(atk_unit[3])
            self.L_State.setStyleSheet("color: red;")

            if atk_type == "Dos":
                print("execute dos atk by auto injection")

                self.Btn_DosAttackOnClickListener()
            elif atk_type == "Spoofing":
                print("execute Spoofing atk by auto injection")
                #self.auto_inject_msg = atk_msg
                #self.AutoSpoofing()
                self.TB_SpooftingEditor.setItem(1, 0, QTableWidgetItem((atk_msg)))

                self.Btn_SpoofingOnClickListener()
            elif atk_type == "Fuzzing":
                print("execute Spoofing atk by auto injection")
                #self.auto_inject_msg = atk_msg
                #self.AutoSpoofing()
                self.TB_SpooftingEditor.setItem(1, 0, QTableWidgetItem((atk_msg)))

                self.Btn_FuzzingOnClickListener()

            elif atk_type == "Replay":
                print("execute Replay atk by auto injection")

                self.TB_SpooftingEditor.setItem(0, 0, QTableWidgetItem((atk_msg)))
                self.Btn_ReplayOnclickListener()
                #self.auto_inject_msg = atk_msg
                #self.AutoReplay()
            else:
                print("atk type not valid")
        else:
            print("Auto Injection Finished")
            self.auto_injection_timer.stop()
            self.L_State.setText("State: No Auto Instance")
            self.L_State.setStyleSheet("color: green;")
            if self.CB_Circular.isChecked():
                print("Next Circular Auto Inject")
                self.Btn_AutoInjectOnClickListener()


    def Btn_DownloadOnClickListener(self):
        print("download program to the ecus")
        command = "xsdb TclScripts/download.tcl"
        # print current path
        print(os.getcwd())
        try:
            subprocess.run(command, shell=True, check=True)
            print("download ok")
            QMessageBox.information(self, 'Success', 'Download Successful')

        except subprocess.CalledProcessError as e:
            print("download failed:", e)
            QMessageBox.critical(self, 'Error', 'Elf Download Failed')

    def Btn_DosAttackOnClickListener(self):
        print("Dos Attack on click")
        #self.DosAttack()
        self.AtkFlag = "Dos"
        self.SendMsg('*')
        self.recovery_timer2 = QTimer()
        self.recovery_timer2.setSingleShot(True)
        self.recovery_timer2.timeout.connect(self.recover_global_variable_dos)
        self.recovery_timer2.start(15000)

    def recover_global_variable_dos(self):
        self.AtkFlag = "Normal"
        command = "xsdb TclScripts/download.tcl"
        # try:
        #     subprocess.run(command, shell=True, check=True)
        #     print("reset ok")
        # except subprocess.CalledProcessError as e:
        #     print("reset failed:", e)
        # self.parsed_data = []


    def Btn_SpoofingOnClickListener(self):
        print("Spoofing Attack on click")
        self.SpoofingAttack()

    def Btn_FuzzingOnClickListener(self):
        print("Fuzzing Attack on click")
        self.FuzzingAttack()
    def Btn_ReplayOnclickListener(self):
        print("Replay Attack on click")
        self.ReplayAttack()

    def DosAtk(self):
        print("Dos attack")

    def DosAttack(self):
        print("Dos attack")
        self.AtkFlag = "Dos"
        self.dos_timer = QTimer()
        self.dos_timer.setSingleShot(True)
        self.dos_timer.timeout.connect(self.Dos_execute_attack)
        self.dos_timer.start(1000)

    def Dos_execute_attack(self):
        self.dos_timer = QTimer()
        self.dos_timer.timeout.connect(self.execute_dos_attack)
        self.dos_timer.start(100)

        # self.SendMsg('#' + Dos_msg + "$")
        # self.recovery_timer3 = QTimer()
        # self.recovery_timer3.setSingleShot(True)
        # self.recovery_timer3.timeout.connect(self.recover_global_variable)
        # self.recovery_timer3.start(1000)

    def execute_dos_attack(self):
        print("Execute Dos atk")
        dos_msg = "88000000f80000000000000000"
        if self.dos_attack_count < 50:
            self.SendMsg('#' + dos_msg + "$")
            self.dos_attack_count += 1
        else:
            self.dos_attack_count = 0
            self.dos_timer.stop()
            self.recovery_timer3 = QTimer()
            self.recovery_timer3.setSingleShot(True)
            self.recovery_timer3.timeout.connect(self.recover_global_variable)
            self.recovery_timer3.start(2000)


    def ReplayAttack(self):
        print("Replay attack")
        replay_msg = self.TB_SpooftingEditor.item(0, 0)
        if replay_msg is not None:
            self.AtkFlag = "Replay"
            self.replay_timer = QTimer()
            self.replay_timer.setSingleShot(True)
            self.replay_timer.timeout.connect(self.Replay_execute_attack)
            self.replay_timer.start(1000)
        else:
            QMessageBox.critical(self, 'Error', 'Must Select a Message')

    def Replay_execute_attack(self):
        replay_msg = self.TB_SpooftingEditor.item(0, 0).text()
        print(replay_msg)
        if replay_msg is not None:
            self.SendMsg('#' + replay_msg + "$")
            self.recovery_timer = QTimer()
            self.recovery_timer.setSingleShot(True)
            self.recovery_timer.timeout.connect(self.recover_global_variable)
            self.recovery_timer.start(1000)

    def AutoSpoofing(self):
        print("Spoofing attack")
        self.AtkFlag = "Spoofing"
        self.spoofing_timer = QTimer()
        self.spoofing_timer.setSingleShot(True)
        self.spoofing_timer.timeout.connect(self.AutoSpoofing_execute_attack)
        self.spoofing_timer.start(1000)

    def AutoSpoofing_execute_attack(self):
        replay_msg = self.auto_inject_msg
        if replay_msg is not None:
            self.SendMsg('#' + replay_msg + "$")
            self.recovery_timer2 = QTimer()
            self.recovery_timer2.setSingleShot(True)
            self.recovery_timer2.timeout.connect(self.recover_global_variable)
            self.recovery_timer2.start(1000)

    def AutoReplay(self):
        print("Replay attack")
        self.AtkFlag = "Replay"
        self.spoofing_timer = QTimer()
        self.spoofing_timer.setSingleShot(True)
        self.spoofing_timer.timeout.connect(self.AutoReplay_execute_attack)
        self.spoofing_timer.start(1000)

    def AutoReplay_execute_attack(self):
        replay_msg = self.auto_inject_msg
        if replay_msg is not None:
            self.SendMsg('#' + replay_msg + "$")
            self.recovery_timer2 = QTimer()
            self.recovery_timer2.setSingleShot(True)
            self.recovery_timer2.timeout.connect(self.recover_global_variable)
            self.recovery_timer2.start(1000)

    def SpoofingAttack(self):
        print("Spoofing attack")
        replay_msg = self.TB_SpooftingEditor.item(1, 0)
        if replay_msg is not None:
            self.AtkFlag = "Spoofing"
            self.spoofing_timer = QTimer()
            self.spoofing_timer.setSingleShot(True)
            self.spoofing_timer.timeout.connect(self.Spoofing_execute_attack)
            self.spoofing_timer.start(1000)
        else:
            QMessageBox.critical(self, 'Error', 'Must Select a Message')

    def FuzzingAttack(self):
        print("Fuzzing attack")
        replay_msg = self.TB_SpooftingEditor.item(1, 0)
        if replay_msg is not None:
            self.AtkFlag = "Fuzzing"
            self.spoofing_timer = QTimer()
            self.spoofing_timer.setSingleShot(True)
            self.spoofing_timer.timeout.connect(self.Spoofing_execute_attack)
            self.spoofing_timer.start(1000)
        else:
            QMessageBox.critical(self, 'Error', 'Must Select a Message')

    def Spoofing_execute_attack(self):
        replay_msg = self.TB_SpooftingEditor.item(1, 0).text()
        print(replay_msg)
        if replay_msg is not None:
            self.SendMsg('#' + replay_msg + "$")
            self.recovery_timer2 = QTimer()
            self.recovery_timer2.setSingleShot(True)
            self.recovery_timer2.timeout.connect(self.recover_global_variable)
            self.recovery_timer2.start(1000)

    def recover_global_variable(self):
        self.AtkFlag = "Normal"

    def SendMsg(self, msg):
        txData = msg
        if len(txData) == 0:
            return
        self.com.write(txData.encode('UTF-8'))

    def Btn_ClearDataOnclickListener(self):
        print("clear data list")
        self.TB_CANMsg.clearContents()
        self.parsed_data.clear()
        self.TB_CANMsg.setRowCount(0)

    # Serial Send data
    def Com_Send_Data(self):
        txData = self.textEdit_Send.toPlainText()
        if len(txData) == 0:
            return
        if self.hexSending_checkBox.isChecked() == False:
            self.com.write(txData.encode('UTF-8'))
        else:
            Data = txData.replace(' ', '')
            # 如果16进制不是偶数个字符, 去掉最后一个, [ ]左闭右开
            if len(Data) % 2 == 1:
                Data = Data[0:len(Data) - 1]
            # 如果遇到非16进制字符
            if Data.isalnum() is False:
                QMessageBox.critical(self, 'Error', 'Contain non-Hex Value')
            try:
                hexData = binascii.a2b_hex(Data)
            except:
                QMessageBox.critical(self, 'Error', 'Encoding Error')
                return
            # 发送16进制数据, 发送格式如 ‘31 32 33 41 42 43’, 代表'123ABC'
            try:
                self.com.write(hexData)
            except:
                QMessageBox.critical(self, 'Error', 'Transfer Hex Error')
                return

    # 串口接收数据
    def Com_Receive_Data(self):

        try:
            rxData = bytes(self.com.readAll())
        except:
            QMessageBox.critical(self, 'fatal error', 'Serial Rcv Data Error')
        if self.hexShowing_checkBox.isChecked() == False:
            try:
                self.textEdit_Recive.insertPlainText(rxData.decode('UTF-8'))
                self.textEdit_Recive.ensureCursorVisible()
                self.received_data += rxData.decode('UTF-8')
                # print(rxData)



            except:
                pass
        else:
            Data = binascii.b2a_hex(rxData).decode('ascii')
            # re 正则表达式 (.{2}) 匹配两个字母
            hexStr = ' 0x'.join(re.findall('(.{2})', Data))
            # 补齐第一个 0x
            hexStr = '0x' + hexStr
            self.textEdit_Recive.insertPlainText(hexStr)
            self.textEdit_Recive.insertPlainText(' ')
            # print(hexStr)

    # 串口刷新
    def Com_Refresh_Button_Clicked(self):
        self.Com_Name_Combo.clear()
        com = QSerialPort()
        com_list = QSerialPortInfo.availablePorts()
        for info in com_list:
            com.setPort(info)
            if com.open(QSerialPort.ReadWrite):
                self.Com_Name_Combo.addItem(info.portName())
                com.close()

    # 16进制显示按下
    def hexShowingClicked(self):
        if self.hexShowing_checkBox.isChecked() == True:
            # 接收区换行
            self.textEdit_Recive.insertPlainText('\n')

    # 16进制发送按下
    def hexSendingClicked(self):
        if self.hexSending_checkBox.isChecked() == True:
            pass

    # 发送按钮按下
    def SendButton_clicked(self):
        self.Com_Send_Data()

    # 串口刷新按钮按下
    def Com_Open_Button_clicked(self):
        #### com Open Code here ####
        comName = self.Com_Name_Combo.currentText()
        comBaud = int(self.Com_Baud_Combo.currentText())
        self.com.setPortName(comName)
        try:
            if self.com.open(QSerialPort.ReadWrite) == False:
                QMessageBox.critical(self, 'fatal error', 'serial open failed')
                return
        except:
            QMessageBox.critical(self, 'fatal error', 'serial open failed')
            return
        self.Com_Close_Button.setEnabled(True)
        self.Com_Open_Button.setEnabled(False)
        self.Com_Refresh_Button.setEnabled(False)
        self.Com_Name_Combo.setEnabled(False)
        self.Com_Baud_Combo.setEnabled(False)
        self.Com_isOpenOrNot_Label.setText('  opened')
        self.com.setBaudRate(comBaud)

    def Com_Close_Button_clicked(self):
        self.com.close()
        self.Com_Close_Button.setEnabled(False)
        self.Com_Open_Button.setEnabled(True)
        self.Com_Refresh_Button.setEnabled(True)
        self.Com_Name_Combo.setEnabled(True)
        self.Com_Baud_Combo.setEnabled(True)
        self.Com_isOpenOrNot_Label.setText('  closed')

    def receive_data_analysis(self):
        # check which host it belongs to
        last_data = self.parsed_data[-1]

        if len(last_data[0]) != 26:
            return

        address = str(last_data[0][2:8])  # 字节信息的1, 2, 3字节
        data_item = str(last_data[0][8:26])  # 字节信息的5-12字节
        # if address == '020202':
        #     #print("Controller Message Received")

        if address == '040404':
            #print("ECU1 Message Received")
            self.ecu1_data_process(last_data)
        if address == '050505':
            #print("ECU2 Message Received")
            self.ecu2_data_process(last_data)
        if address == '060606':
            #print("ECU3 Message Received")
            self.ecu3_data_process(last_data)

    def ecu1_data_process(self, data_frame):
        # check life signal
        life_signal = data_frame[0][10:12]
        self.ecu1_life_signal_last = life_signal

        # check ECU Status
        ECU_Status = bool((int(data_frame[0][12:14], 16) >> 0) & 0x01)
        if ECU_Status == self.last_ecu_status:
            self.ecu_status_stable_count += 1
        else:
            self.ecu_status_stable_count = 0

        if self.ecu_status_stable_count >= self.check_times:
            if ECU_Status & self.ecu1_life_signal_bl:
                self.L_ECU.setStyleSheet("background-color: green")
            else:
                self.L_ECU.setStyleSheet("")

        # check TCU Status
        TCU_Status = bool((int(data_frame[0][14:16], 16) >> 0) & 0x01)
        if TCU_Status == self.last_tcu_status:
            self.tcu_status_stable_count += 1
        else:
            self.tcu_status_stable_count = 0

        if self.tcu_status_stable_count >= self.check_times:
            if TCU_Status & self.ecu1_life_signal_bl:
                self.L_TCU.setStyleSheet("background-color: green")
            else:
                self.L_TCU.setStyleSheet("")

        # check Braker Status
        Braker_Status = bool((int(data_frame[0][16:18], 16) >> 0) & 0x01)
        if Braker_Status == self.last_braker_status:
            self.braker_status_stable_count += 1
        else:
            self.braker_status_stable_count = 0

        if self.braker_status_stable_count >= self.check_times:
            if Braker_Status & self.ecu1_life_signal_bl:
                self.L_Braker.setStyleSheet("background-color: green")
            else:
                self.L_Braker.setStyleSheet("")

        # Update last status variables
        self.last_ecu_status = ECU_Status
        self.last_tcu_status = TCU_Status
        self.last_braker_status = Braker_Status


    def ecu2_data_process(self, data_frame):
        # check life signal
        life_signal = data_frame[0][10:12]
        self.ecu2_life_signal_last = life_signal

        # check AirBag Status
        AirBag_Status = bool((int(data_frame[0][12:14], 16) >> 0) & 0x01)
        if AirBag_Status == self.last_airbag_status:
            if AirBag_Status & self.ecu2_life_signal_bl:
                self.L_Airbag.setStyleSheet("background-color: green")
            else:
                self.L_Airbag.setStyleSheet("")
        
        # check SCL Status
        SLC_Status = bool((int(data_frame[0][14:16], 16) >> 0) & 0x01)
        if SLC_Status == self.last_scl_status:
            if SLC_Status & self.ecu2_life_signal_bl:
                self.L_Slight.setStyleSheet("background-color: green")
            else:
                self.L_Slight.setStyleSheet("")

        # Update the last status variables
        self.last_airbag_status = AirBag_Status
        self.last_scl_status = SLC_Status

    def ecu3_data_process(self, data_frame):
        # check life signal
        life_signal = data_frame[0][10:12]
        self.ecu3_life_signal_last = life_signal

        # check CDS Status
        CDS_Status = bool((int(data_frame[0][12:14], 16) >> 0) & 0x01)
        if CDS_Status == self.last_cds_status:
            if CDS_Status & self.ecu3_life_signal_bl:
                self.L_Collision.setStyleSheet("background-color: green")
            else:
                self.L_Collision.setStyleSheet("")
        
        # check BDS Status
        BDS_Status = bool((int(data_frame[0][14:16], 16) >> 0) & 0x01)
        if BDS_Status == self.last_bds_status:
            if BDS_Status & self.ecu3_life_signal_bl:
                self.L_Brake.setStyleSheet("background-color: green")
            else:
                self.L_Brake.setStyleSheet("")
        
        # check SLB (Steering Light B)
        SLB_Status = bool((int(data_frame[0][16:18], 16) >> 2) & 0x01)
        if SLB_Status == self.last_slb_status:
            if SLB_Status & self.ecu3_life_signal_bl:
                self.L_Steering.setStyleSheet("background-color: green")
            else:
                self.L_Steering.setStyleSheet("")

        # check FLB (Front Light B)
        FLB_Status = bool((int(data_frame[0][16:18], 16) >> 1) & 0x01)
        if FLB_Status == self.last_flb_status:
            if FLB_Status & self.ecu3_life_signal_bl:
                self.L_FLightB.setStyleSheet("background-color: green")
            else:
                self.L_FLightB.setStyleSheet("")

        # check BLB (Back Light B)
        BLB_Status = bool((int(data_frame[0][16:18], 16) >> 0) & 0x01)
        if BLB_Status == self.last_blb_status:
            if BLB_Status & self.ecu3_life_signal_bl:
                self.L_BLightB.setStyleSheet("background-color: green")
            else:
                self.L_BLightB.setStyleSheet("")

        # Update the last status variables
        self.last_cds_status = CDS_Status
        self.last_bds_status = BDS_Status
        self.last_slb_status = SLB_Status
        self.last_flb_status = FLB_Status
        self.last_blb_status = BLB_Status


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())