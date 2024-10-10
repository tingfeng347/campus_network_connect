import requests
import socket
import uuid
import os
import configparser
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from bs4 import BeautifulSoup
from win10toast import ToastNotifier
import sys  # 导入sys模块
# import pywifi
# from pywifi import const
import time

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


# 检查是否连接到校园网认证页面
def check_campus_network():
    try:
        # 尝试访问校园网认证页面
        response = requests.get('http://1.1.1.1', timeout=2)
        # 如果返回状态码是200，说明可以访问校园网的认证页面
        if response.status_code == 200:
            return True
    except requests.RequestException:
        return False

#  检查当前连接的Wi-Fi是否为指定的WIFI
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



class LoginApp:
    def __init__(self, master):
        self.master = master
        self.master.title("校园网连接")
        self.master.geometry("400x300")  # 窗口尺寸

        # 居中窗口
        self.center_window()

        # 创建输入框和标签
        self.label_username = ttk.Label(master, text="用户名")
        self.label_username.pack(pady=10)

        self.entry_username = ttk.Entry(master)
        self.entry_username.pack(pady=10)

        self.label_password = ttk.Label(master, text="密码")
        self.label_password.pack(pady=10)

        self.entry_password = ttk.Entry(master, show="*")
        self.entry_password.pack(pady=10)

        self.login_button = ttk.Button(master, text="登录", command=self.verify_login)
        self.login_button.pack(pady=20)

        self.load_credentials()
        self.auto_connect()  # 程序启动时自动连接
        # self.check_wifi()

    def center_window(self):
        # 获取屏幕尺寸
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # 窗口宽高
        window_width = 300
        window_height = 350

        # 计算窗口居中位置
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # 设置窗口大小和位置
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")


    def load_credentials(self):
        # 加载保存的用户凭据
        config = configparser.ConfigParser()
        expanduser = os.path.expanduser('~')
        config_path = (expanduser + '\config_xyw.ini')  # 修改为新的路径
        config.read(config_path)
        if 'Credentials' in config:
            username = config['Credentials'].get('username', '')
            password = config['Credentials'].get('password', '')
            self.entry_username.insert(0, username)
            self.entry_password.insert(0, password)

    def save_credentials(self, username, password):
        # 保存用户凭据
        config = configparser.ConfigParser()
        config['Credentials'] = {
            'username': username,
            'password': password
        }
        expanduser = os.path.expanduser('~')
        config_path = (expanduser + '\config_xyw.ini')  # 修改为新的路径
        with open(config_path, 'w') as configfile:
            config.write(configfile)
    
    def clear_credentials(self):
    # 清空用户名和密码输入框
      self.entry_username.delete(0, tk.END)
      self.entry_password.delete(0, tk.END)
            
    def auto_connect(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if username and password:
            self.verify_login()  # 如果有凭据则自动连接

    # def check_wifi(self):
    #     if is_wifi_connected():
    #         pass
    #       # messagebox.showinfo('Wi-Fi状态', '已连接到校园网WIFI')
    #     else:
    #         messagebox.showinfo('Wi-Fi未连接', '请连接到校园网WIFI')
            

    def verify_login(self):
        # 仅在连接到校园网WIFI时获取并执行后续操作
        # if is_wifi_connected():
            wlanacip = get_wlanacip()
            wlanuserip = get_local_ip()
            mac = get_mac_address()

            name = self.entry_username.get()
            password = self.entry_password.get()

            if not name or not password:
                messagebox.showwarning('输入错误', '用户名和密码不能为空！')
                return

            base_url = "http://1.1.1.1:8888/webauth.do"
            query_params = {
                'wlanacip': wlanacip,
                'wlanacname': 'hnnydxwg',
                'wlanuserip': wlanuserip,
                'mac': mac,
                'vlan': '0',
            }
            login_url = f"{base_url}?{'&'.join([f'{key}={value}' for key, value in query_params.items()])}"
            print(login_url)
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
                response = requests.post(login_url, data=payload, timeout=7)  # 设置超时时间为7秒
                if response.status_code == 200:
                    response_text = response.text
                    soup = BeautifulSoup(response_text, 'lxml')
                    error_message = soup.find('input', {'id': 'errMessage'})
                    message = error_message['value']
                    if '认证成功!请关闭' in message:
                        self.save_credentials(name, password)  # 保存凭据
                        self.master.destroy()
                        ToastNotifier().show_toast(title = message,
                        msg = "校园网状态",
                        icon_path='_internal/Success.ico',
                        duration = 2,
                        threaded = False)
                        sys.exit()  # 退出程序
                    elif '账号不存在' in message:
                        messagebox.showerror('错误', message)
                        self.master.iconify()  # 最小化窗口
                        self.master.deiconify()  # 恢复窗口
                    elif '密码错误' in message:
                        messagebox.showerror('错误', message)
                        self.master.iconify()  # 最小化窗口
                        self.master.deiconify()  # 恢复窗口
                    elif '此IP已在线请勿重复认证' in message:
                        self.master.destroy()
                        ToastNotifier().show_toast(title = message,
                        msg = "校园网状态",
                        icon_path='_internal/Success.ico',
                        duration = 2,
                        threaded = False)
                        sys.exit()  # 退出程序
                    elif '账号被检测共享冻结使用' in message:
                        self.master.destroy()
                        ToastNotifier().show_toast(title = message,
                        msg = "校园网状态",
                        icon_path='_internal/Error.ico',
                        duration = 2,
                        threaded = False)
                        sys.exit()  # 退出程序
                else:
                    messagebox.showerror('错误', f'请求失败, 状态码: {response.status_code}')
            except requests.RequestException as e:
                 self.master.destroy()
                 ToastNotifier().show_toast(title = "认证超时,请重连校园网或关闭代理",
                        msg = "校园网状态",
                        duration = 2,
                        icon_path='_internal/Error.ico',
                        threaded = False)
                 sys.exit()  # 退出程序
                 
            except Exception as e:
                messagebox.showerror('错误', f'{str(e)}')
        # else:
        #     messagebox.showerror('错误', '未连接到校园网WIFI，无法继续操作')

if __name__ == '__main__':
    root = tk.Tk()
    # 等待连接到校园网
    
    max_retries = 3  # 最大重试次数
    retry_count = 0  # 当前重试次数
    
    # 等待连接到校园网
    while not check_campus_network():
        ToastNotifier().show_toast(
            title="等待校园网连接",
            msg="请连接到校园网...",
            icon_path='_internal/Info.ico',
            duration=2,
            threaded=True
        )
        time.sleep(5)  # 每5秒检测一次校园网连接状态

        retry_count += 1
        if retry_count >= max_retries:
            root.destroy()  # 关闭窗口
            sys.exit()  # 退出程序
    
    app = LoginApp(root)
    root.mainloop()
