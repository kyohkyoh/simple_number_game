import socket
import threading
import time
import random

IP = ""
PORT = 5050
ADDR = (IP,PORT)

def client_handler(conn_list,
                   num_list,
                   answer_list,
                   point_list,
                   progress_list,
                   server_socket
                   ):
    '''
    define threading
    '''
    connect_socket, connect_addr = server_socket.accept()
    print('connected by ',connect_addr[1])

    notice(conn_list, num_list,answer_list,point_list,progress_list,connect_socket,connect_addr)
    try:
        print('connected_list : ',conn_list)
        index_num = get_index(conn_list, connect_addr)
        check_conn(conn_list,num_list,answer_list,point_list,progress_list,index_num,connect_socket,connect_addr)

        ask_start_game(answer_list,index_num,connect_socket,conn_list,connect_addr)
        game(conn_list,answer_list,num_list,point_list,index_num,answer_dict,connect_socket,connect_addr)
    except ConnectionResetError as e:
        disconn(conn_list,num_list,answer_list,point_list,progress_list,index_num,connect_socket,connect_addr)

def first_sentence(connect_addr,conn_list,num):
    '''
    when client connect server, it is the first
    sentence client can recieve
    it contains how to play
    '''
    if len(conn_list) == 0 :
        sentence = "\' No-one is here!"
    else:
        sentence = "\' "+str(conn_list) + "is(are) in room already!"
    sentence = "hello \'"+str(connect_addr[1])+sentence +\
        "\nyour number is {num}, remember it!".format(num = num)+\
            "\n"+"="*100+\
                "\n1.It proceeds in the order of arrival."+\
                    "\n2.If you guess other people's numbers,"+ \
                        "you get 1 point, and if no one success it,"+\
                            "number's owner get 1 point"+\
                                "\n3.Whoever gets the fastest 3 points wins"+\
                                    "\n"+"="*100 +"\nPlease Wait other player"    
    return sentence
    
def notice(conn_list,num_list,answer_list,point_list,pregress_list,connect_socket,connect_addr):
    '''
    1.Send #first sentence
    2.Create lists 
    '''
    if connect_addr[1] not in conn_list:
        num = random.randint(1, 3)
        sentence = first_sentence(connect_addr,conn_list, num) 
        connect_socket.send(sentence.encode("utf-8"))
        
        conn_list.append(connect_addr[1])
        num_list.append(num)
        print(num_list)
        answer_list.append(0)
        point_list.append(0)
        progress_list.append(0)

def disconn(conn_list,num_list,answer_list,point_list,progress_list,index_num,connect_socket,connect_addr):
    '''
    Delete user infomation form the list when connection is disconnected
    '''
    print("Disconnected by "+ str(connect_addr[1]))
    del conn_list[index_num]
    del num_list[index_num]
    del answer_list[index_num]
    del point_list[index_num]
    del progress_list[index_num]
    connect_socket.close()

def ask_start_game(answer_list,index_num,connect_socket,conn_list,connect_addr):
    '''
    when more than two clients gather, ask if clients want to play the game.
    '''

    if len(conn_list) >= 3:##
        
        ask_ready = "\n"+"+"*50 +\
            "\nmore than three people are in this room. Do you want a play game?(y,n)"+\
                "\n"+"+"*50

        connect_socket.send(ask_ready.encode("utf-8"))
        while True:
            time.sleep(1)
            answer = connect_socket.recv(1024)
            if answer.decode('utf-8') == 'y':
                answer_list[index_num] = 1
                break


def check_maximum(conn_list,connect_socket):
    '''
    limit max clients
    '''
    if len(conn_list) >= 6:
        msg = "Sorry, Our room is already full! see you next time"
        connect_socket.send(msg.encode("utf-8"))
        connect_socket.close()
        raise ConnectionResetError
    else:
        pass
        
def check_conn(conn_list,num_list,answer_list,point_list,progress_list,index_num,connect_socket,connect_addr):
    '''
    1.#check_maximum
    2. checking how many clinets are connecting
    '''
    while True :
        time.sleep(1)
        check_maximum(conn_list,connect_socket)
        if len(conn_list) >= 3:
            break
            
        
def game_msg(orderal,conn_list,connect_socket,connect_addr):
    '''
    game message
    '''
    orderal_list = ["first","second","third","firth","fifth","sixth","seventh","eighth"]
    if connect_addr[1] == conn_list[(orderal-1)%3]:
        msg = "[{}]it's your turn. other players are guessing your number. plz wait a sec".format(orderal_list[orderal-1])
        connect_socket.send(msg.encode("utf-8"))
        answer = -1
    else:
        msg = "\n"+"+"*50 +\
            "\n[{} round]Geuss {}'s number".format(orderal_list[orderal-1],connect_addr[1]) +\
                "\n"+"+"*50
        connect_socket.send(msg.encode("utf-8"))
        
        
        answer = connect_socket.recv(1024)
        answer = answer.decode("utf-8")
        answer = int(answer)
    return answer

def check(orderal,answer, conn_list,num_list,point_list,index_num,answer_dict,connect_socket,connect_addr):
    '''
    1. checking answer whether correct or not
    2. adding point
    '''
    
    if answer == num_list[(orderal-1)%3]:
        point_list[index_num] += 1 
        msg = "Good! your answer is right! you have {} point".format(point_list[index_num])
        connect_socket.send(msg.encode("utf-8"))
    elif (answer != num_list[(orderal-1)%3]) & (conn_list[(orderal-1)%3] != connect_addr[1]):
        msg = "Sorry you are wrong! you have {} point".format(point_list[index_num])
        connect_socket.send(msg.encode("utf-8"))
    answer_dict[orderal][connect_addr[1]]=answer
    
    
    while True:
        if len(answer_dict[orderal]) == len(conn_list): 
            if (conn_list[(orderal-1)%3] == connect_addr[1]):
                if num_list[(orderal-1)%3] not in tuple(answer_dict[orderal].values()):
                        point_list[index_num] += 1
                        msg = "Other player don't guess your number! you have {} point".format(point_list[index_num])
                        connect_socket.send(msg.encode("utf-8"))
                        break
                else :
                    msg = "Sorry, Other player guess your number. you have {} point".format(point_list[index_num])
                    connect_socket.send(msg.encode("utf-8"))
                    break             
            elif conn_list[(orderal-1)%3] != connect_addr[1]:
                break

def game(conn_list,answer_list,num_list,point_list,index_num,answer_dict,connect_socket,connect_addr):
    '''
    Game progress
    '''
    while True:
        time.sleep(1)
        if 0 not in answer_list:
            break
    i = 1
    while True:
        time.sleep(1)
        answer = game_msg(i,conn_list,connect_socket,connect_addr)
        check(i,answer, conn_list,num_list,point_list,index_num,answer_dict,connect_socket,connect_addr)
        
        if 2 in point_list:  ###
            if point_list[index_num]==2:##
                msg = "You Win!"
            else:
                msg = "You Lose"
            connect_socket.send(msg.encode("utf-8"))    
            break
        i += 1
        
def get_index(conn_list, connect_addr):
    '''
    Check the index of the currently connected clinet
    '''
    i = 0
    for k in conn_list:
        if k == connect_addr[1]:
            index_num = i
        i += 1
    return index_num

def make_answer_dict():
    '''
    Make dict contain client's answers
    '''
    answer_dict = {}
    for i in range(8):
        answer_dict[i]={}
    return answer_dict

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(ADDR)
server_socket.listen(5)
print("[server]Ready to listen")

conn_list = []
num_list = []
answer_list = []
point_list = []
progress_list = []
answer_dict = make_answer_dict()
        
while True:
    time.sleep(1)

    t = threading.Thread(target = client_handler, args = (conn_list,
                                                          num_list,
                                                          answer_list,
                                                          point_list, 
                                                          progress_list,
                                                          server_socket))
    t.start()

connect_socket.close()
server_socket.close()

    
    
            