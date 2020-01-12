import sys, traceback
import socket
import pickle
import os
import random
import copy
import pandas as pd 
import copy
import threading as th


class Player():
	
	def __init__(self,name):
		self.pid = random.randint(1,100000)
		self.games = []
		self.name = name
		self.wins = 0
		self.loss = 0

	def get_player_id(self):
		return self.pid

	def get_player_stats(self):
		print("Player Id : ",self.pid)
		print("Player Name : ",self.name)
		print("Wins : ",self.wins)
		print("Loss : ",self.loss)
		print("Wining %: ",self.wins/(self.wins+self.loss+(float('-inf')*-1)))

	def send_to_server(self,conn,msg):
	    m = pickle.dumps(msg)
	    conn.send(m)

	def receive_from_server(self,conn):
	    received_msg = conn.recv(4096)
	    if received_msg:
	        received_obj = pickle.loads(received_msg)  
	        return received_obj
	    return None

	def close_connection(self,conn):
	    msg = "quit"
	    msg = pickle.dumps(msg)
	    conn.send(msg)
	    conn.close() 


if __name__ == '__main__':

	if len(sys.argv) != 5:
		print("Invalid Input Format\n python3 [FileName][Client IP][Client Port][Server IP][Server Port]")
		exit()

	client_IP = str(sys.argv[1])
	client_port = int(sys.argv[2])
	server_IP = str(sys.argv[3])
	server_port = int(sys.argv[4])
	try:
		conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		conn.bind((client_IP, client_port))
		conn.connect((server_IP, server_port))
	except:
		print("Failed to connect with Server")
		exit()

	player = Player(str(input("Enter player name: ")))
	reply = {}
	request = {}

	while True:
		cmd = str(input("Enter your command: ")).lower()

		if cmd == "create_game":
			dimension = int(input("Input board dimension: "))
			player.dimension = dimension
			
			request["type"] = "create_game"
			request["pid"] = player.pid
			request["dimension"] = dimension
			player.send_to_server(conn,request)
			
			reply = player.receive_from_server(conn)
			if reply and reply["status"] == 1: 
				game_id = reply["game_id"]
				configuration = reply["configuration"]
				player.games.append(game_id)
			else:
				print("Error creating new game")

		elif cmd == "join_game":
			game_id = int(input("Input game id you want: "))
			request["type"] = "join_game"
			request["pid"] = player.pid
			request["game_id"] = game_id
			
			player.send_to_server(conn,request)
			reply = player.receive_from_server(conn)

			if reply and reply["status"] == 1: 
				
				dimension = reply["dimension"]
				configuration = reply["configuration"]
				player.games.append(game_id)
			else:
				print("Error joining game")

		elif cmd == "play":
			game_id = int(input("Game ID: "))
			request["type"] = "turn"
			request["game_id"] = game_id
			request["pid"] = player.pid
			player.send_to_server(conn,request)
			reply = player.receive_from_server(conn)
			
			if reply:
				if reply["winner"]!=-1:
					if reply[winner] == player.pid:
						print("Game: ",game_id," won!!!!")
						player.won += 1
					else:
						print("Game: ",game_id," lost!!!!")
						player.loss += 1
					player.get_player_stats()
					player.games.remove(game_id)

				elif reply["turn"]:
					value = int(input("Enter the value: "))
					request["type"] = "play"
					request["game_id"] = game_id
					request["pid"] = player.pid
					request["value"] = value
					player.send_to_server(conn,request)

					reply = player.receive_from_server(conn)
					if reply and "winner" in reply and reply["status"] == 1:
						if reply["winner"] == player.pid:
							print("Game: ",game_id," won!!!!")
							player.wins += 1
						else:
							print("Game: ",game_id," lost!!!!")
							player.loss += 1
						player.get_player_stats()
						player.games.remove(game_id)
				else:
					print("Wait for your turn")
				reply = None
			else:
				print("Unable to process play request")

		elif cmd == "get_all_games":
			request["type"] = "get_all_games"
			request["pid"] = player.pid
			player.send_to_server(conn,request)
			reply = player.receive_from_server(conn)
			if reply: 
				game_details = reply["game_details"]
				for item in game_details:
	 				print("Game_id: ",item)
			else:
				print("Error fetching all games details")

		elif cmd == "get_game_status":
 			game_id = input("Enter game id: ")
 			
 			request["type"] = "get_game_status"
 			request["game_id"] = game_id
 			request["pid"] = player.pid
 			player.send_to_server(conn,request)
 			
 			reply = player.receive_from_server(conn)
 			if reply:
 				print("Board: ")
 				print(pd.DataFrame(reply["board"]))
 				print("Turn: ",reply["turn"])
 				print("Dimensions: ",reply["dimension"])
 				print("Winner: ", reply["winner"])
	 		else:
	 			print("Error fetching game status")			

		elif cmd == "player_stat":
			player.get_player_stats() 			

		elif cmd == "get_my_games":
			print(player.games)

		elif cmd == "exit":
			request["type"] = "quit"
			request["pid"] = player.pid
			player.close_connection(conn)
			print("Exiting....")
			exit()