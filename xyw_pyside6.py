import sys
import requests
import socket
import uuid
import os
import configparser
from PySide6.QtCore import Qt, QLocale
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtWidgets import QApplication
from qfluentwidgets import (setTheme, Theme, FluentTranslator, setThemeColor,MessageBox,
                            SplitTitleBar, isDarkTheme)
from app.view.ui_loginwindow import Ui_Form
from app.resource import resource_rc
from bs4 import BeautifulSoup


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000

if isWin11():
    from qframelesswindow import AcrylicWindow as Window
else:
    from qframelesswindow import FramelessWindow as Window

# 获取本机 IP 地址
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('8.8.8.8', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

# 获取本机 MAC 地址
def get_mac_address():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 12, 2)])

# 获取接入控制器的 IP 地址
def get_wlanacip():
    return "120.194.123.250"

# # 检查当前连接的Wi-Fi是否为指定的WIFI
# def is_wifi_connected():
    
#     wifi = pywifi.PyWiFi()
#     iface = wifi.interfaces()[0]
    
#     iface.scan()  # 开始扫描Wi-Fi
#     time.sleep(0.1)  # 等待扫描结果返回

#     # 获取当前已连接的Wi-Fi名称
#     if iface.status() == const.IFACE_CONNECTED:
#         connected_ssid = iface.network_profiles()[0].ssid
#         if connected_ssid == "Teacher-WIFI"or connected_ssid=="Student-WIFI":
#             return True  # 已连接到Teacher-WIFI或Student-WIFI
#     return False

class LoginWindow(Window, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        setThemeColor('#3F7DCA')

        self.setTitleBar(SplitTitleBar(self))
        self.titleBar.raise_()

        self.label.setScaledContents(False)
        self.setWindowTitle('校园网连接')
        self.setWindowIcon(QIcon(":/qfluentwidgets/images/logo.png"))
        self.resize(1000, 675)
        self.windowEffect.setMicaEffect(self.winId(), isDarkMode=isDarkTheme())
        if not isWin11():
            color = QColor(25, 33, 42) if isDarkTheme() else QColor(240, 244, 249)
            self.setStyleSheet(f"LoginWindow{{background: {color.name()}}}")

        self.titleBar.titleLabel.setStyleSheet("""
            QLabel{
                background: transparent;
                font: 15px;
                padding: 0 10px;
                color: white;
            }
        """)

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.pushButton.clicked.connect(self.verify_login)

        self.load_credentials()


    def load_credentials(self):
        # 加载保存的用户凭据
        config = configparser.ConfigParser()
        expanduser=os.path.expanduser('~')
        config_path = (expanduser+'\config_xyw.ini')  # 修改为新的路径
        config.read(config_path)
        if 'Credentials' in config:
            username = config['Credentials'].get('username', '')
            password = config['Credentials'].get('password', '')
            self.lineEdit_3.setText(username)
            self.lineEdit_4.setText(password)

    def save_credentials(self, username, password):
        # 保存用户凭据
        config = configparser.ConfigParser()
        config['Credentials'] = {
            'username': username,
            'password': password
        }
        expanduser=os.path.expanduser('~')
        config_path = (expanduser+'\config_xyw.ini')  # 修改为新的路径
        with open(config_path, 'w') as configfile:
            config.write(configfile)
               

    def resizeEvent(self, e):
        super().resizeEvent(e)
        pixmap = QPixmap(":/images/background.jpg").scaled(
            self.label.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.label.setPixmap(pixmap)

    def verify_login(self):
    #  if is_wifi_connected():
        name = self.lineEdit_3.text()
        password = self.lineEdit_4.text()

        if not name or not password:
            self.showMessageBox5()
            return

        wlanacip = get_wlanacip()
        wlanuserip = get_local_ip()
        mac = get_mac_address()

        base_url = "http://1.1.1.1:8888/webauth.do"
        query_params = {
            'wlanacip': wlanacip,
            'wlanacname': 'hnnydxwg',
            'wlanuserip': wlanuserip,
            'mac': mac,
            'vlan': '0',
        }
        login_url = f"{base_url}?{'&'.join([f'{key}={value}' for key, value in query_params.items()])}"

        payload = {
            'scheme': 'http',
            'serverIp': '1.1.1.1:80',
            'hostIp': 'http://127.0.0.1:8082/',
            'loginType': '',
            'auth_type': '0',
            'isBindMac1': '0',
            'pageid': '34',
            'templatetype': '1',
            'listbindmac': '0',
            'recordmac': '0',
            'isRemind': '1',
            'loginTimes': '',
            'groupId': '',
            'distoken': '',
            'echostr': '',
            'url': 'http://www.msftconnecttest.com',
            'isautoauth': '',
            'notice_pic_loop2': '/portal/uploads/pc/demo2/images/bj.png',
            'notice_pic_loop1': '/portal/uploads/pc/demo2/images/logo.png',
            'userId': name,
            'passwd': password,
            'remInfo': 'on'
        }

        try:
            response = requests.post(login_url, data=payload,timeout=7)
            if response.status_code == 200:
                response_text = response.text
                soup = BeautifulSoup(response_text, 'lxml')
                error_message = soup.find('input', {'id': 'errMessage'})
                message = error_message['value']
                
                if '认证成功!请关闭' in message:
                    self.showMessageBox1()
                    self.save_credentials(name, password)  # 保存凭据
                    self.close()
                elif '账号不存在' in message:
                    self.showMessageBox2()
                elif '密码错误' in message:
                    self.showMessageBox3()
                elif '此IP已在线请勿重复认证' in message:
                    self.showMessageBox4()
                    self.close()
                elif '账号被检测共享冻结使用' in message:
                    self.showMessageBox9()
                    self.close()
            else:
                 self.showMessageBox7()

        except requests.RequestException as e:
            self.showMessageBox6()
        except Exception as e:
            self.showMessageBox8()
    #  else:
    #         self.showMessageBox0()
    
    # def showMessageBox0(self):
    #     w = MessageBox(
    #         '😂😂😂😂😂😂😂😂😂😂\n\n'
    #         '未连接到校园网WIFI，请先连上校园网',
    #         '',
    #         self
    #     )
    #     w.yesButton.setText('确定')
    #     w.cancelButton.setText('取消')
    #     w.exec()

    def showMessageBox1(self):
        w = MessageBox(
            '🥰🥰🥰🥰🥰🥰🥰🥰🥰🥰\n\n'
            '登录成功',
            '',
            self
        )
        w.yesButton.setText('确定')
        w.cancelButton.setText('取消')
        w.exec()

    def showMessageBox2(self):
        w = MessageBox(
            '😂😂😂😂😂😂😂😂😂😂\n\n'
            '账号不存在',
            '',
            self
        )
        w.yesButton.setText('确定')
        w.cancelButton.setText('取消')
        w.exec()

    def showMessageBox3(self):
        w = MessageBox(
            '😂😂😂😂😂😂😂😂😂😂\n\n'
            '密码错误',
            '',
            self
        )
        w.yesButton.setText('确定')
        w.cancelButton.setText('取消')
        w.exec()
    
    def showMessageBox4(self):
        w = MessageBox(
            '😁😁😁😁😁😁😁😁😁😁\n\n'
            '此IP已在线请勿重复认证',
            '',
            self
        )
        w.yesButton.setText('确定')
        w.cancelButton.setText('取消')
        w.exec()

    def showMessageBox5(self):
        w = MessageBox(
            '😂😂😂😂😂😂😂😂😂😂\n\n'
            '用户名和密码不能为空！',
            '',
            self
        )
        w.yesButton.setText('确定')
        w.cancelButton.setText('取消')
        w.exec()
    
    def showMessageBox6(self):
        w = MessageBox(
            '😂😂😂😂😂😂😂😂😂😂\n\n'
            '认证超时！请重连校园网或关闭代理',
            '',
            self
        )
        w.yesButton.setText('确定')
        w.cancelButton.setText('取消')
        w.exec()
    
    def showMessageBox7(self):
        w = MessageBox(
            '😂😂😂😂😂😂😂😂😂😂\n\n'
            '请求失败！',
            '',
            self
        )
        w.yesButton.setText('确定')
        w.cancelButton.setText('取消')
        w.exec()
    
    def showMessageBox8(self):
        w = MessageBox(
            '😂😂😂😂😂😂😂😂😂😂\n\n'
            '发生未知错误！',
            '',
            self
        )
        w.yesButton.setText('确定')
        w.cancelButton.setText('取消')
        w.exec()
        
    def showMessageBox9(self):
        w = MessageBox(
            '😂😂😂😂😂😂😂😂😂😂\n\n'
            '账号被检测共享冻结使用8分钟',
            '',
            self
        )
        w.yesButton.setText('确定')
        w.cancelButton.setText('取消')
        w.exec()
    


if __name__ == '__main__':
    setTheme(Theme.AUTO)
    app = QApplication(sys.argv)
    translator = FluentTranslator(QLocale())
    app.installTranslator(translator)
    login_window = LoginWindow()
    login_window.show()
    app.exec()
