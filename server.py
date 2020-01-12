import random
import copy
import pandas as pd
import sys, traceback
import socket
import pickle
import os
import threading as th


global MAX_PLAYERS
MAX_PLAYERS = 2
games_dict = {}

class Board():
	
	def __init__(self,dimension,configuration):
		
		self.board = [[0]*dimension]*dimension
		self.dimension = dimension
		self.row_sum = [0]*dimension
		self.col_sum = [0]*dimension
		self.primary_diag_sum = 0
		self.secondary_diag_sum = 0
		self.random_initialize_board(configuration)

	def get_board(self):

		return self.board

	def random_initialize_board(self,configuration):

		k = 0;
		for i in range(self.dimension):
			temp_list = self.board[i]
			for j in range(self.dimension):
				temp_list[j] = configuration[k]
				k += 1
			self.board[i] = copy.deepcopy(temp_list)

	def mark_cell(self,value):
		flag = False
		for i in range(self.dimension):
			temp_list = self.board[i]
			for j in range(self.dimension):
				if temp_list[j] == value:
					temp_list[j] = -1
					self.board[i] = copy.deepcopy(temp_list)
					self.row_sum[i] += 1
					self.col_sum[j] += 1
					flag = True
					if i == j:
						self.primary_diag_sum += 1
					if i+j+1 == self.dimension:
						self.secondary_diag_sum += 1
					break

			if flag:
				break

	def check_termination(self):
		
		if self.dimension in self.row_sum:
			return True
		if self.dimension in self.col_sum:
			return True
		if self.dimension == self.primary_diag_sum:
			return True
		if self.dimension == self.secondary_diag_sum:
			return True
		return False

	def paint_board(self):
		print(pd.DataFrame(self.board))

class Game():

	def __init__(self,game_id,board_dimension,configuration):
		self.game_id = game_id
		self.board = Board(board_dimension,configuration)

	def play(self,value): 

		self.board.paint_board()

		player_status = {}
		
		self.board.mark_cell(value)
		
		player_status["status"] = 0
		player_status["row_sum"] = self.board.row_sum
		player_status["col_sum"] = self.board.col_sum
		player_status["pri"] = self.board.primary_diag_sum
		player_status["sec"] = self.board.secondary_diag_sum

		flag = self.board.check_termination()
		
		if flag:
			player_status["status"] = 1

		print()
		self.board.paint_board()
		
		return player_status

def send_to_client(conn,msg):
    m = pickle.dumps(msg)
    conn.send(m)

def receive_from_client(conn):
    received_msg = conn.recv(2048)
    if received_msg:
        received_obj = pickle.loads(received_msg)
        return received_obj
    return None

def close_connection(conn):
    conn.close()

def process_client(conn, client_addr, server_ip):

    client_IP = client_addr[0]
    client_port = client_addr[1]
    reply = {}
    request = {}

    while True:
    	request = receive_from_client(conn)
    	
    	if request["type"] == "create_game":
    		pid = request["pid"]
    		dimension = request["dimension"]
    		config = random.sample(range(1,dimension**2+1),dimension**2)
    		game_id = random.randint(1,100000)
    		games_dict[game_id] = {}
    		games_dict[game_id]["objects"] = []
    		games_dict[game_id]["objects"].append(Game(game_id,dimension,config))
    		games_dict[game_id]["players"] = []
    		games_dict[game_id]["players"].append(pid)
    		games_dict[game_id]["turn"] = 0
    		games_dict[game_id]["winner"] = -1
    		games_dict[game_id]["dimension"] = dimension
    		reply["game_id"] = game_id
    		reply["configuration"] = config
    		reply["status"] = 1
    		
    		send_to_client(conn,reply)

    	elif request["type"] == "join_game":
    		game_id = request["game_id"]
    		pid = request["pid"]

    		if game_id in games_dict:
    			
    			if len(games_dict[game_id]["players"]) < MAX_PLAYERS:
    				
    				dimension = games_dict[game_id]["dimension"]
    				config = random.sample(range(1,dimension**2+1),dimension**2)
    				games_dict[game_id]["players"].append(pid)
    				games_dict[game_id]["objects"].append(Game(game_id,dimension,config))

    				reply["configuration"] = config
    				reply["dimension"] = dimension
    				reply["status"] = 1
    			else:
    				reply["status"] = 0

    		send_to_client(conn,reply)

    	elif request["type"] == "play":
    		game_id = request["game_id"]
    		pid = request["pid"]
    		value = request["value"]
    		reply["status"] = 0

    		games_dict[game_id]["turn"] = (games_dict[game_id]["turn"] + 1)%MAX_PLAYERS

    		if game_id in games_dict:
    			if pid in games_dict[game_id]["players"]:
    				print("size cmp: ",MAX_PLAYERS,len(games_dict[game_id]["objects"]))
    				print("size cmp: ",MAX_PLAYERS,len(games_dict[game_id]["players"]))
    				for i in range(MAX_PLAYERS):
    					player_status = games_dict[game_id]["objects"][i].play(value)

    					print("status: ",player_status["status"])
    					print("row_sum")
    					l = player_status["row_sum"]
    					for item in l:
    						print(item,end=",")
    					print()
    					print("col_sum")
    					l = player_status["col_sum"]
    					for item in l:
    						print(item,end=",")
    					print()
    					print("primary_diag_sum: ",player_status["pri"])
    					print("secondary_diag_sum: ",player_status["sec"])

    					if player_status["status"] == 1:
    						reply["winner"] = games_dict[game_id]["players"][i]
    						reply["status"] = 1
    						break

    		send_to_client(conn,reply)

    	elif request["type"] == "turn":
    		game_id = request["game_id"]
    		pid = request["pid"]
    		index = 0
    		
    		for i in games_dict[game_id]["players"]:
    			print(i)
    			if i == pid:
    				break
    			index += 1

    		reply = {}
    		reply["winner"] = games_dict[game_id]["winner"]
    		if games_dict[game_id]["turn"] == index:
    			reply["turn"] = True
    		else:
    			reply["turn"] = False
    		send_to_client(conn,reply)

    	elif request["type"] == "get_all_games":
    		game_names = []
    		for key,value in games_dict.items():
    			game_names.append(key)
    		reply["game_details"] = game_names
    		send_to_client(conn,reply)
    	
    	elif request["type"] == "get_game_status":
    		game_id = request["game_id"]
    		pid = request["pid"]
    		
    		reply = {}
    		reply["turn"] = games_dict[game_id]["players"][games_dict[game_id]["turn"]]
    		reply["winner"] = games_dict[game_id]["winner"]
    		reply["dimension"] = games_dict[game_id]["dimension"]
    		
    		k = 0
    		for item in games_dict[game_id]["players"]:
    			if item == pid:
    				reply["board"] = games_dict[game_id]["objects"][k].board.board
    				break
    			k += 1
    		send_to_client(conn,reply)

    	elif request["type"] == "quit":
    		pid = request["pid"]
    		close_connection(conn)
    		break


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print ("Invalid argument format\n Correct usage:python3 [filename][IP Address][Port Number]")
        exit()
    server_IP = str(sys.argv[1])
    server_port = int(sys.argv[2])
    
    try:
    	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except:
    	print("Error creating the socket")

    try:
    	server.bind((server_IP, server_port))
    	server.listen(15)
    except:
    	print("Error binding to IP and port")
    while True:
    	conn, client_addr = server.accept()
    	print("Connection accepted for client: ", client_addr)
    	th.Thread(target=process_client, args=(conn, client_addr, server_IP)).start()

    server.close()
