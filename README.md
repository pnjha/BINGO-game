to run server
python3 [filename][server IP][sserver port]

to run client 
python3 [filename][client IP][client port][server ip][server port]

Commands at Client's end
create_game -> to create new game
get_all_games -> to fetch all games
join_game -> to participate in a game
play -> to make game moves
get_game_status -> to get status of a game

Game implemented: BINGO
Each player has a randomly arrange square grid of numbers ranging from 1 to dimensions*dimensions. Each player generates a random number in that range and strikes of the corresponding grid entry. First player to completely strike of a row or a column or a any diagonal wins the game