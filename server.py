import threading
import time

import wx
from socket import socket,AF_INET,SOCK_STREAM
class CjcServer(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id=1002, title='小程服务器', pos=wx.DefaultPosition,size=(400, 450))
        pl=wx.Panel(self)
        box=wx.BoxSizer(wx.VERTICAL)
        fgz1 = wx.FlexGridSizer(wx.HSCROLL)
        start_server_btn=wx.Button(pl,size=(133,40),label='启动服务')
        record_btn = wx.Button(pl, size=(133, 40), label='保存聊天记录')
        stop_server_btn = wx.Button(pl, size=(133, 40), label='停止服务')
        fgz1.Add(start_server_btn,1,wx.TOP)
        fgz1.Add(record_btn, 1, wx.TOP)
        fgz1.Add(stop_server_btn, 1, wx.TOP)
        box.Add(fgz1,1,wx.ALIGN_CENTRE)
        self.show_text = wx.TextCtrl(pl, size=(400, 410), style=wx.TE_MULTILINE | wx.TE_READONLY)
        box.Add(self.show_text, 1, wx.ALIGN_CENTRE)
        pl.SetSizer(box)
        '''-------------------------------以上代码为服务器界面代码-------------------------------------------'''
        self.isOn=False
        self.host_port=('',8888)
        self.server_socket=socket(AF_INET,SOCK_STREAM)
        self.server_socket.bind(self.host_port)
        self.server_socket.listen(5)
        self.session_thread_dict={}

        self.Bind(wx.EVT_BUTTON,self.start_server,start_server_btn)
        self.Bind(wx.EVT_BUTTON,self.save_record,record_btn)
        self.Bind(wx.EVT_BUTTON,self.stop_server,stop_server_btn)

    def stop_server(self,event):
        print('服务器以停止服务')
        self.isOn=False
    def save_record(self, event):
        record_data=self.show_text.GetValue()
        with open('record.log','w',encoding='utf-8') as file:
            file.write(record_data)
    def start_server(self,event):
        if not self.isOn:
            self.isOn=True
            main_thread=threading.Thread(target=self.do_work)
            main_thread.daemon=True
            main_thread.start()
    def do_work(self):
        while self.isOn:
            session_socket,client_addr=self.server_socket.accept()
            user_name=session_socket.recv(1024).decode('utf-8')
            sesstion_thread=SesstionThread(session_socket,user_name)
            self.session_thread_dict[user_name]=sesstion_thread
            sesstion_thread.start()
            self.show_info_and_send_client('服务器通知',f'欢迎{user_name}进入聊天室！',time.strftime('%Y-%m_%d %H:%M:%S',time.localtime()))
        self.server_socket.close()
    def show_info_and_send_client(self,data_source,data,date_time):
        send_data=f'{data_source}:{data}\n时间:{date_time}'
        self.show_text.AppendText('-'*40+'\n'+send_data+'\n')
        for client in self.session_thread_dict.values():
            if client.isOn:
                client.client_socket.send(send_data.encode('utf-8'))


class SesstionThread(threading.Thread):
    def __init__(self,client_socket,user_name):
        threading.Thread.__init__(self)
        self.client_socket=client_socket
        self.user_name=user_name
        self.server=server
        self.isOn=True

    def run(self)->None:
        print(f'客户端:{self.user_name}已经和服务器连接成功，服务器启动一个会话线程')
        while self.isOn:
            data=self.client_socket.recv(1024).decode('utf-8')
            if data=='断开':
                self.isOn=False
                self.server.show_info_and_send_client('服务器通知',f'{self.user_name}离开',time.strftime('%Y-%m_%d %H:%M:%S',time.localtime()))
            else:
                self.server.show_info_and_send_client(self.user_name,data,time.strftime('%Y-%m_%d %H:%M:%S',time.localtime()))

        self.client_socket.close()


if __name__=='__main__':

    app=wx.App()
    server=CjcServer()
    server.Show()
    app.MainLoop()
