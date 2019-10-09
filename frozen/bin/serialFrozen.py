from bin.func import *


class ser(serial.Serial):
    def __init__(self,port, baudrate,interval=30):
        super(ser, self).__init__()
        self.port = port
        self.baudrate = baudrate
        self.interval = interval
        self.open_ser()
        self.parse_data = 'recv'

    def open_ser(self):
        self.timeout = 0.5
        self.open()

    def send(self, data):
        '''串口发送数据'''
        data = binascii.unhexlify(data)
        if self.is_open:
            try:
                self.flushOutput()
                self.write(data)
            except Exception as e:
                log('{}, 串口发送错误'.format(e))
                quit()
        else:
            self.open_ser()

    def recv(self):
        self.isopened()
        self.flushInput()
        times = self.interval
        for i in range(times-1):
            inwaiting = self.in_waiting
            if inwaiting:
                recv = self.read_all()
                self.recv_parse(recv)
            time.sleep(1)

        # recv_data_all = self.parse_data
        # self.parse_data = 'recv'
        # return

    def recv_parse(self, data, code='utf-8'):
        if code == 'utf-8':
            try:
                datas = binascii.hexlify(data).decode('utf-8').upper()
                re_com = re.compile('68.*16')
                datas = re.findall(re_com, datas)[0]
                show('recv:'+str(datas).replace('\n','\t'))
            except:
                self.recv_parse(data,'ascii')

        if code == 'ascii':
            try:
                datas = data.decode('ascii')
                # self.parse_data += datas + '\n'
                show('recv:'+str(datas).replace('\n','\t'))
            except:
                self.recv_parse(data,'GBK')

        if code == 'GBK':
            try:
                datas = data.decode('GBK').replace('\n','').replace('\r','')
                # self.parse_data += datas + '\n'
                show('recv:'+str(datas).replace('\n','\t'))
            except:
                show('recv:'+str(data).replace('\n','\t'))

    def sopen(self):
        if not self.is_open:
            self.open()

    def sclose_ser(self):
        if self.is_open:
            self.close()

    def isclosed(self):
        if self.is_open:
            self.close()

    def isopened(self):
        if not self.is_open:
            self.open()




