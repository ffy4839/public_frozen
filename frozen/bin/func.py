import serial
import configparser
import os
import binascii
import sys
import re
import time
import threading
import serial.tools.list_ports as LP


def time_now(st='%Y-%m-%d %H:%M:%S',t=time.time()):
    return time.strftime(st,time.localtime(t))

def log(data):
    res = '{} | {}'.format(time_now(), str(data))
    save(res, name='ErrLog')
    print(res)

def show(data):
    res = '{} | {}'.format(time_now(), str(data))
    save(res, name='save')
    print(res)

def save(data, name='save', mode='a'):
    sep =os.path.sep
    path = os.path.abspath(__file__)
    path = path.split(sep)[:-2]
    path = sep.join(path) + sep
    file_path = path + name + '.txt'
    try:
        with open(file_path, mode) as f:
            f.write(data)
            f.write('\n')
    except Exception as e:
        print('{} | {}'.format(time_now(), str(e)))

def get_config():
    sections = 'configs'
    try:
        data = {}
        sep = os.path.sep
        path = os.path.abspath(__file__)
        path = path.split(sep)[:-2]
        path = sep.join(path) + sep
        config = configparser.ConfigParser()
        if 'setConfig.ini' in os.listdir(path):
            config.read('setConfig.ini', encoding='UTF-8')
            for i in config.items(section=sections):
                data[i[0]] = i[1]
            return data

        else:
            config['configs'] = {}
            config['configs']['baudrate'] = '9600'
            config['configs']['frozen_hour'] = '24'
            config['configs']['frozen_day'] = '3'
            config['configs']['frozen_month'] = '2'
            config['configs']['interval'] = '30'
            config['configs']['month_frozen_day'] = 'None'
            config['configs']['leading'] = '500'
            with open(path + 'setConfig.ini', 'w') as f:
                config.write(f)
            input('创建成功, 重启后开始冻结')
            sys.exit()
    except Exception as e:
        print(e)
        input()


def get_port():
    port_list = [str(i).replace(' ','') for i in list(LP.comports())]
    sort_port_list = [re.findall('COM(.*?)-',i)[0] for i in port_list]
    sort_port_dict = {}
    for i in range(len(port_list)):
        sort_port_dict[sort_port_list[i]] = port_list[i]
    sort_port_list = [int(i) for i in sort_port_list]
    sort_port_list.sort()
    port_list = [sort_port_dict[str(i)] for i in sort_port_list]
    for i in port_list:
        print('\t{}'.format(i))
    while True:
        input_port = input('输入串口：').replace(' ', '').upper()
        for i in range(len(port_list)):
            if input_port in port_list[i]:
                input_port = 'com' + re.findall('COM(.*?)-', port_list[i])[0]
                return input_port
        log('串口输入错误,请重新输入\t{}'.format(input_port))

def get_protocol_type():
    tips = '\t1.{}\n\t2.{}\n\t3.{}\n请输入序号进行选择:'.format(
                                            '民用物联网',
                                            '商业物联网',
                                            '自定义')
    while True:
        pro_input = input(tips).replace(' ','').replace('\n','')
        if pro_input == '3':
            inp_a = input('\t输入发送帧部分：').replace(' ', '')
            inp_b = input('\t输入帧时间部分：').replace(' ', '')
            inp_now_time1 = time.strftime('%y%m%d%H%M%S',time.localtime(time.time()))
            inp_now_time2 = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            return (inp_a,inp_b,inp_now_time1,inp_now_time2)
        else:
            if pro_input in ['1','2']:
                return pro_input
        log('串口输入错误,请重新输入\t{}'.format(pro_input))
        tips = '请输入序号进行选择:'



