#创建tcp服务端
import socket
import threading
import random
key_lst_bl={}#储存格式:{<key>:[b,data1数据]}
online_users = {} # 存储在线用户 格式{<key>:{"un":<用户名>,"start":<连接状态(int): 0>空闲状态 1>我的世界服务端状态 其中1和2需要进行无FXL头转发>,port:<端口号>}}
def handle_client(client_socket):
    key = str(random.randint(0,9))+str(random.randint(0,9))+str(random.randint(0,9))+str(random.randint(0,9))+str(random.randint(0,9))+str(random.randint(0,9))+str(random.randint(0,9))
    rv = "ok"
    online_users[key] = {"un":None,"start":0}
    while True: #检测连接是否被中止
        try:
            request = client_socket.recv(1024)
        except socket.error as e:
            print("Connection closed!")
            break
        except Exception as e:
            print("Error! info:")
            print(str(e))
        print("Received request!")
        if online_users[key]["start"] == 0 or online_users[key]["un"] == None:
            responsew = request.decode()
            response = responsew.split(" ")
            if response[0] == "FXL":
                if(response[1] == "Ver"):
                    rv = "FXL VerRv bate1.0.0"
                elif(response[1] == "KeySet"):
                    online_users[key] = {"un":response[2],"start":0}
                    rv = "FXL KeySetRv ready "
                elif(response[1] == "KeyGet"):
                    rv = "FXL KeyRv "+ key
                elif(response[1] == "start"):
                    if(response[2] == "1"):
                        online_users[key] = {"un":response[3],"start":1}
                        rv = "FXL startRv ready"

                elif(response[1] == "portGet"):
                    #开放tcp服务端端口
                    server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    while True:
                        try:
                            online_users[key]["port"] = random.randint(30000,65535)
                            server_socket1.bind(('0.0.0.0', online_users[key]["port"]))
                            break
                        except OSError as e:
                            continue
                    rv = "FXL portRv "+str(online_users[key]["port"])
                    print(rv)
                    client_socket.send(rv.encode())
                    server_socket1.listen(5)
                    print("zhuanfa Server started on port "+str(online_users[key]["port"]))
                    b=0
                    qb=0
                    server_socket1.setblocking(False)
                    while True:
                        try:
                            client_socket2, client_address = server_socket1.accept()
                            b+=1
                            #生成协程
                            client_handler2 = threading.Thread(target=hcc, args=(client_socket2,client_socket,b,key))
                            client_handler2.start()
                        except BlockingIOError as e:
                            pass
                        except Exception as e:
                            print("Error! info:")
                            print(str(e))
                            break
                        client_socket.setblocking(False)
                        try:
                            data1 = client_socket.recv(1024)
                            data2 = client_socket.recv(1024)
                            key_lst_bl[key] = [data1,data2]
                        except BlockingIOError as e:
                            pass
                        except:
                            break

            client_socket.send(rv.encode())
        elif online_users[key]["start"] == 1 and online_users != None:
            pass 
def hcc(cs2,cs1,b,key):
    #cs1对应开房间客户端(指多人游戏服务端)
    #cs2对应转发客户端(指多人游戏客户端)
    old_data = ""
    cs1.send("HCC connected".encode())
    cs1.send(str(b).encode())
    while True:
        try:
            data = cs2.recv(1024)# 接收来自cs2(转发客户端(指多人游戏客户端))的1024字节的数据 -> 经过测试发现运行时可能会报:[WinError 10035] 无法立即完成一个非阻止性套接字操作。 -> 原因是cs2.recv(1024)没有接收到数据
            cs1.send(data)# 将数据发送给cs1(开房间客户端(指多人游戏服务端))
            cs1.send(str(b).encode()) # 将b(b变量是对应的客户端线程编号)发送给cs1(开房间客户端(指多人游戏服务端))
            print(b) # debug语句
            # cs1接收后将data转发给b号虚拟客户端,虚拟客户端负责转发给服务端
        except BlockingIOError as e:
            print(str(e))
            pass
        except Exception as e:
            print("hcc子客户端断连")
            break
        try:
            if old_data != key_lst_bl[key][1] and b == key_lst_bl[key][0]:
                cs2.send(key_lst_bl[key][1].encode())
                old_data = data
        except:
            pass
        

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8080))
    server_socket.listen(5)
    print("Server started on port 8080")
    while True:
        client_socket, client_address = server_socket.accept()
        print("Accepted connection from %s:%s" % client_address)
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    main()
    