import serial
import configparser
import os
import binascii
import sys
import re
import time
import threading
import serial.tools.list_ports as LP


def get_hms(data):
    if isinstance(data,int) or isinstance(data, float):
        data = int(data)
        h = data//3600
        m = (data%3600)//60
        s = (data%3600)%60
        return ' {}小时 {}分 {}秒'.format(h,m,s)
    return 'None'

def time_now(st='%Y-%m-%d %H:%M:%S'):
    return time.strftime(st,time.localtime(time.time()))

def log(data, leader=''):
    t = time_now()
    res = '{}{}:|\t{}'.format(leader, time_now(), str(data))
    save(res, name='ErrLog')
    print(res)

def show(data, leader=''):
    res = '{}{}:|\t{}'.format(leader, time_now(), str(data))
    save(res, name='save')
    print(res)

def save(data, name='save', mode='a'):
    sep =os.path.sep
    path = os.path.abspath(__file__)
    path = path.split(sep)[:-1]
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
        path = path.split(sep)[:-1]
        path = sep.join(path) + sep
        config = configparser.ConfigParser()
        if 'setConfig.ini' in os.listdir(path):
            config.read(path + 'setConfig.ini', encoding='UTF-8')
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

def get_start_time():
    yn = input('是否断点续传/设置起始时间（y/n）:')
    if yn.upper() == 'Y':
        data = input('请输入时间：').replace('\n','')
        try: return time.mktime(time.strptime(data,'%y-%m-%d %H:%M:%S'))
        except: pass
        try: return time.mktime(time.strptime(data,'%y%m%d%H%M%S'))
        except: pass
        try: return time.mktime(time.strptime(data,'%Y%m%d%H%M%S'))
        except: pass
        try: return time.mktime(time.strptime(data,'%Y-%m-%d %H:%M:%S'))
        except: pass
        return False
    return None




class ser(serial.Serial):
    def __init__(self, port, baudrate=9600, parity=serial.PARITY_NONE, timeout=0.1):
        #parity: {'N': 'None', 'E': 'Even', 'O': 'Odd', 'M': 'Mark', 'S': 'Space'}
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.timeout = timeout

    def send(self,data):
        self.opend()
        self.flush()
        data = self.check_send_data(data)
        if not data:
            return False
        try:
            self.write(data)
            return True
        except Exception as e:
            print(e)
            return False

    def recv(self, times = 30, inter=0.1):
        self.opend()
        self.flush()
        for i in range(int(times/inter)):
            waiting = self.in_waiting
            if waiting:
                recv = self.read_all()
                recv = self.parse_recv(recv).upper()
                show('\trecv:\t'+str(recv).replace('\n','\t'))
                # return recv
            time.sleep(1 * inter)


    def parse_recv(self,data):
        try: return data.decode('GBK')
        except: pass

        try: return data.decode('ascii')
        except: pass

        try: return binascii.hexlify(data).decode()
        except: pass

        return data

    def check_send_data(self,data):
        if not isinstance(data,str): return False

        data_list = list(set(list(data.upper()+'1234567890ABCDEF')))
        if len(data_list) == 16:
            if len(data) % 2 == 0:
                return binascii.unhexlify(data.encode())
            else:
                return binascii.unhexlify((data + '0').encode())
        else:
            return data.encode('GBK')

    def opend(self):
        if not self.is_open: self.open()

    def close(self):
        if self.is_open: self.close()


class pro():
    def __init__(self, mode, leader):
        self.leader = leader + 'FEFEFEFEFE'
        self.choose(mode)

    def run(self, set_time, add = 5):
        psetTime = self.change_stamp2format(set_time-add,st='%y%m%d%H%M%S')
        pnowTime = self.change_stamp2format(time.time(),st='%y%m%d%H%M%S')
        pbase = self.phead + pnowTime + self.pmid + psetTime
        pcheck = self.checkSUM(pbase)
        res = (pbase + pcheck + self.pend).replace(' ','').replace('\n','').replace('\t','')
        show('\tsend:\t{}\t{}'.format(self.change_stamp2format(set_time-add,st='%Y-%m-%d %H:%M:%S'), res))
        return (self.leader+res).replace('\n','').replace('\t','')

    def choose(self, mode):
        if mode == '1':
            self.minyong()
        elif mode == '2':
            self.shangyong()
        else:
            self.others(mode)

    def minyong(self):
        self.phead = '68 00 00 00 01 00 00 68 04 10 00'
        self.pmid = '16 21 C6 00'
        self.pend = '16'

    def shangyong(self):
        self.phead = '68 FF FF FF FF FF FF 68 04 10 00'
        self.pmid = '02 03 AA 00'
        self.pend = '16'

    def others(self, mode):
        pass

    def checkSUM(self,data):
        data = data.replace(' ','').replace('\n','').replace('\t','')
        sum = 0
        for i in range(0, len(data), 2):
            sum += int(data[i:i+2], 16)
        res = hex(sum)[2:].rjust(2,'0')[-2:].upper()
        return res

    def change_format2stamp(self, data, st='%Y%m%d%H%M%S'):
        return time.mktime(time.strptime(data,st))

    def change_stamp2format(self, data, st='%Y%m%d%H%M%S'):
        return time.strftime(st,time.localtime(data))

class timeList():
    def __init__(self,
                 month_nums=0,
                 day_nums=0,
                 hour_nums=0,
                 frozen_month=None,
                 start_time = 0):

        self.month_nums = month_nums
        self.day_nums = day_nums
        self.hour_nums = hour_nums
        self.frozen_month = frozen_month
        self.start_time = start_time


    def run(self):
        base_time = self.base_time()

        base_day_time = base_time['base_day_time']
        base_hour_time = base_time['base_hour_time']
        base_month_time = base_time['base_month_time']

        hour_time_list = self.create_hour_list(base_hour_time)
        day_time_list = self.create_day_list(base_day_time)
        month_time_list = self.create_month_list(base_month_time)

        res = list(set(hour_time_list + day_time_list + month_time_list))
        res.sort(reverse=True)
        res.append(res[-1])

        return res

    def create_hour_list(self, base_time):
        res = []
        for i in range(self.hour_nums + 1):
            r = (base_time - (i * 3600))
            if r<self.start_time:
                break
            res.append(r)
        # print('hour：{}'.format(len(res)))
        return res

    def create_day_list(self, base_time):
        res = []
        for i in range(self.day_nums + 1):
            r = base_time - (i * 3600 * 24)
            if r < self.start_time:
                break
            res.append(r)
        # print('day：{}'.format(len(res)))
        return res

    def create_month_list(self, base_time):
        res = []
        while self.month_nums + 1:
            base_time = self.select_month(base_time)
            if base_time < self.start_time:
                break
            res.append(base_time)
            self.month_nums -= 1
        # print('month：{}'.format(len(res)))
        return res

    def select_month(self, base_time):
        year = self.change_stamp2format(base_time,'%Y')
        month = self.change_stamp2format(base_time,'%m')

        month_list = self.select_year(year)
        add = month_list[int(month) - 1]

        next_time = base_time - add * 24 * 3600
        return next_time

    def select_year(self, year):
        year = int(year)
        if year%4 == 0 and not (year%100 == 0 and year%400 != 0):
            return [31, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30]
        else:
            return [31, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30]

    def base_time(self,):
        st_base_hour_time = self.change_stamp2format(time.time(), '%Y%m%d%H') + '0000'
        st_base_day_time = self.change_stamp2format(time.time(), '%Y%m%d') + '000000'
        select = '010000'
        if self.frozen_month:
            select = self.frozen_month
        st_baes_month_time = self.change_stamp2format(time.time(), '%Y%m') + '{}00'.format(select)

        base_hour_time = self.change_format2stamp(st_base_hour_time)
        base_day_time = self.change_format2stamp(st_base_day_time)
        base_month_time = self.change_format2stamp(st_baes_month_time )

        return {
            'base_hour_time':base_hour_time,
            'base_day_time':base_day_time,
            'base_month_time':base_month_time,
            }

    def change_format2stamp(self, data, st='%Y%m%d%H%M%S'):
        return time.mktime(time.strptime(data,st))

    def change_stamp2format(self, data, st='%Y%m%d%H%M%S'):
        return time.strftime(st,time.localtime(data))


try:
    print('初始化...',end='\n')
    config_data = get_config()  # 每次import 都会读取
    BAUDRATE = int(config_data['baudrate'])  # 波特率
    FROZEN_HOUR_TIMES = int(config_data['frozen_hour'])  # 小时冻结次数
    FROZEN_DAY_TIMES = int(config_data['frozen_day'])  # 天冻结次数
    FROZEN_MONTH_TIME = int(config_data['frozen_month'])  # 月冻结次数
    INTERVAL = int(config_data['interval'])  # 两次设置间隔
    MONTH_FROZEN_DAY = eval(config_data['month_frozen_day'])  # 月冻结时间

    LEADER = int(config_data['leading']) * '55'  #前导码




    PORT = get_port() #串口端口号
    START_TIME = get_start_time()

    timeList = timeList(
                month_nums=FROZEN_MONTH_TIME,
                day_nums=FROZEN_DAY_TIMES,
                hour_nums=FROZEN_HOUR_TIMES,
                frozen_month=MONTH_FROZEN_DAY,
                start_time = START_TIME
                )

    time_list = timeList.run()
    ser = ser(port=PORT,baudrate=BAUDRATE)
    PRO_MODE = get_protocol_type()
    pro = pro(PRO_MODE, LEADER)
    print('初始化完成')
except Exception as e:
    print('初始化失败')
    print(e)
    input('exit')
    sys.exit() 




class APP():
    def __init__(self):
        self.ser = ser
        self.pro = pro
        self.time_list = time_list
        self.sum_time = 0


    def run(self):
        n = 0
        self.t_base = time.time()
        tips = get_hms(len(self.time_list) * INTERVAL)
        show('预计剩余时间为：{}'.format(tips), leader='\n')
        while len(self.time_list):
            try:
                t = time.time()
                p = pro.run(self.time_list.pop())
                ser.send(p)
                ser.recv(times = INTERVAL)
                n += 1
                self.sleep(t, n)
            except Exception as e:
                log(str(e))

    def sleep(self, t, n):
        cha = time.time() - t
        sleeps = INTERVAL - cha
        if sleeps < 0:
            sleeps = 0
        time.sleep(sleeps)
        time_sum = time.time() - self.t_base
        tips = get_hms((time_sum/n)*(len(self.time_list)))
        show('预计剩余时间为：{}'.format(tips),leader='\n')

if __name__ == "__main__":
    try:
        app = APP()
        app.run()
    except Exception as e:
        log(str(e))
    input('exit')
    sys.exit()   


