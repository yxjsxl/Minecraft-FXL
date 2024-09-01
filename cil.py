#建立tcp服务端
import socket
import threading
#导入日志库
import logging
#日志初始化
ver = 'bate1.0.0'
qb = 0
ykj=None
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s / %(levelname)s]>%(message)s')
logger = logging.getLogger(__name__)
logger.info('多人联机系统启动,正在连接多人联机服务器!')
#通过tcp连接服务端
def tcp_connect():
    global ykj
    global qb
    #创建套接字
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #连接服务端
    tcp_socket.connect(('127.0.0.1', 8080))
    #发送数据
    tcp_socket.send('FXL Ver'.encode('utf-8'))
    #接收数据
    data = tcp_socket.recv(1024)
    print(data.decode('utf-8'))
    if data.decode('utf-8') == 'FXL VerRv '+ver:
        logger.info('多人联机服务器连接成功!->协议版本:'+ver)
    else:
        logger.error('多人联机服务器连接失败!->协议版本不匹配,请 更新/降级 软件! 大厅协议版本:'+(data.decode('utf-8').split(' ')[2])+' 你的协议版本:'+ver)
        tcp_socket.close()
        exit()
    logger.info('请输入用户名:')
    username = input()
    logger.info("正在进行多人游戏大厅登录...")
    tcp_socket.send(('FXL KeySet ' + username).encode('utf-8'))
    data = tcp_socket.recv(1024)
    key = ""
    dataw=data.decode('utf-8').split(' ')
    if dataw[0] == 'FXL' and dataw[1] == 'KeySetRv' and dataw[2] == 'ready':
        logger.info('多人游戏大厅登录成功!')
        tcp_socket.send('FXL KeyGet'.encode('utf-8'))
        data = tcp_socket.recv(1024)
        key = (data.decode('utf-8').split(' '))[2]
        logger.info('获取到密钥:'+key)
    else:
        logger.error('多人游戏大厅登录失败!->未知错误!')
        tcp_socket.close()
        exit()
    logger.info('请输入开放端口(java默认25565/基岩默认19132):')
    port = input()
    logger.info('正在获取外部端口...')
    tcp_socket.send(('FXL portGet').encode('utf-8'))
    data = tcp_socket.recv(1024)
    wport = (data.decode('utf-8').split(' '))[2]
    logger.info("申请成功!内部端口:"+port+" 外部端口:"+wport)
    while True:
        data2w=tcp_socket.recv(1024)
        try:
            if data2w.decode('utf-8') == 'HCC connected':
                b=int(tcp_socket.recv(1024).decode('utf-8'))
                logger.info('玩家已连接!')
                #创建线程
                t = threading.Thread(target=hcc, args=(port,b,tcp_socket))
                t.start()
            else:
                # logger.debug("解码后出现异常信息:")
                # logger.debug(data2w.decode('utf-8'))
                pass
        except Exception as e:
            logger.debug(str(e))
            logger.debug("flag -> 65")
            yb = int(tcp_socket.recv(1024).decode('utf-8'))
            logger.debug("flag -> 67")
            ykj = data2w
            logger.debug("flag -> 69(更新)")
            qb=yb
            logger.debug("flag -> 71(success)")
def hcc(port,b,tcp_socket):
    old_qb = 0 # old_qb是上一个qb的值,用于判断qb是否改变,如果改变的话将会再while True的第一个old_qd检测被发现
    #创建套接字客户端
    hcc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 虚拟客户端套接字(hcc_socket),局部变量,用于转发客户端发给客户端的信息
    #连接服务端
    hcc_socket.connect(('127.0.0.1', int(port))) # 虚拟客户端连接服务端,以真实客户端的登录信息登录
    hcc_socket.setblocking(False) # 设置为非阻塞模式
    while True: # 进入循环检测(bug多发地)
        if old_qb != qb: # 检测qb是否改变
            logger.debug("flag -> 72(success Run if - 1)")
            if qb == b: # 检测真实客户端呼叫的是否是自己的线程编号
                logger.debug("flag -> 72(success Run if - 2)")
                hcc_socket.send(ykj) # 发送真实客户端的信息,用于转发给服务端
                old_qb = qb # 更新old_qb的值,以防重复检测
        try:
            msg=hcc_socket.recv(1024)
            tcp_socket.send(b)
            tcp_socket.send(msg)
        except:
            pass
tcp_connect()