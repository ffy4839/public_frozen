from bin.func import *

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
        show('send set time:{}\t{}'.format(self.change_stamp2format(set_time-add,st='%Y-%m-%d %H:%M:%S'), res))
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
                 frozen_month=None):

        self.month_nums = month_nums
        self.day_nums = day_nums
        self.hour_nums = hour_nums
        self.frozen_month = frozen_month


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
        res = [(base_time - (i * 3600)) for i in range(self.hour_nums+1)]
        # print('hour：{}'.format(len(res)))
        return res

    def create_day_list(self, base_time):
        res = [(base_time - (i * 3600 * 24)) for i in range(self.day_nums+1)]
        # print('day：{}'.format(len(res)))
        return res

    def create_month_list(self, base_time):
        res = []
        while self.month_nums + 1:
            base_time = self.select_month(base_time)
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

if __name__ =='__main__':
    a = timeList(month_nums = 120, day_nums = 20, hour_nums = 48, frozen_month = None)
    t1 = time.time()
    res = a.run()
    print(time.time()-t1)
    print(len(res))
    for i in res:
        print(a.change_stamp2format(i-5))
