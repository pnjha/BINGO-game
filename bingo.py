import random
import copy
import pandas as pd 

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
		player_status["sec"] = self.secondary_diag_sum

		flag = self.board.check_termination()
		
		if flag:
			player_status["status"] = 1

		print()
		self.board.paint_board()
		
		return player_status
