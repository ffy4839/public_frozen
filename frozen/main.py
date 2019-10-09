input('waiting for Start')

from bin.func import *
from bin import protocol
from bin.serialFrozen import ser



config_data = get_config()  # 每次import 都会读取

BAUDRATE = int(config_data['baudrate'])  # 波特率
FROZEN_HOUR_TIMES = int(config_data['frozen_hour'])  # 小时冻结次数
FROZEN_DAY_TIMES = int(config_data['frozen_day'])  # 天冻结次数
FROZEN_MONTH_TIME = int(config_data['frozen_month'])  # 月冻结次数
INTERVAL = int(config_data['interval'])  # 两次设置间隔
MONTH_FROZEN_DAY = eval(config_data['month_frozen_day'])  # 月冻结时间

LEADER = int(config_data['leading']) * '55'  #前导码



PORT = get_port() #串口端口号

timeList = protocol.timeList(
            month_nums=FROZEN_MONTH_TIME,
            day_nums=FROZEN_DAY_TIMES,
            hour_nums=FROZEN_HOUR_TIMES,
            frozen_month=MONTH_FROZEN_DAY
            )

time_list = timeList.run()
ser = ser(port=PORT,baudrate=BAUDRATE,interval=INTERVAL)
PRO_MODE = get_protocol_type()
pro = protocol.pro(PRO_MODE, LEADER)




class APP():
    def __init__(self):
        self.ser = ser
        self.pro = pro
        self.time_list = time_list
        self.sum_time = 0
        self.L = len(self.time_list) - 1

    def run(self):
        n = 0
        while len(self.time_list):
            t = time.time()
            p = pro.run(self.time_list.pop())
            ser.send(p)
            ser.recv()
            self.sleep(t,n)
            n+=1



    def sleep(self, t, n):
        cha = time.time() - t
        sleeps = INTERVAL - cha
        if n == 0:
            sleeps = 2 * 60
            tips = 'None'
        else:
            if sleeps < 0:
                sleeps = 0
                self.sum_time += cha
            else:
                self.sum_time += sleeps + cha
            tips = (self.sum_time/(self.L - len(self.time_list) + 1)) * len(self.time_list)
            if tips < 24 *3600:
                st = '%H:%M:%S'
            elif tips < 28 * 24 *3600:
                st = '%d %H:%M:%S'
            else:
                st = '%Y-%m-%d %H:%M:%S'
            tips = time_now(st=st,t=tips)
        show('\n预计剩余时间为：{}'.format(tips))
        time.sleep(sleeps)

try:
    app = APP()
    app.run()
except:
    input('exit')
    sys.exit()
