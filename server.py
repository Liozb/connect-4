import random
import socket
import threading
import time
from globals_var import *


def run(conn, buffer=1024):
    """
    function that manages the game for client thread.
    :param conn: the connection to client socket
    :param buffer: buffer for message receiving
    """
    new_q = ""
    # posing first question
    func, q = pose_q1()
    send_client(func, q, conn)
    while True:
        if func in [Q6, Q7]:  # for Q6 and Q7 we don't want to get new input
            new_q = f"{func}{SEP}{new_q}"
            func, new_q = server_listens(new_q, conn)
        elif func is None:
            # close connection for client
            conn.close()
        else:
            raw_res = conn.recv(buffer).decode(FORMAT)
            func, new_q = server_listens(raw_res, conn)
            if func not in [Q6, Q7]:  # for Q6 and Q7 we don't want to print new question
                send_client(func, new_q, conn)
            elif func is None:
                send_client(func, new_q, conn)
                conn.close()
                break
            if func == Q4 and "times" in new_q:  # those 2 conditions exists for fifth error in num_of_games only.
                time.sleep(60 * pause_count)


def server_listens(raw_res, conn):
    """
    All client responses arrive here
    qn functions follow the following interface
    receive the client response
    return the next function and the next question
    """
    func_dict = {
        Q1: q1,
        Q2: q2,
        Q4: q4,
        Q5: q5,
        Q6: easy_level,
        Q7: hard_level
    }

    func, res = raw_res.split(SEP)  # separates client response to relevant func + response
    func_int = int(func)
    if func_int in [Q6, Q7]:
        res = int(res)
        n_func, new_q = func_dict[func_int](conn, res)
    else:
        n_func, new_q = func_dict[func_int](res)

    return n_func, new_q


def send_client(func, q, conn):
    """
    send client relevant func and message as 1 string with a separator
    :param func: relevant function
    :param q: string to send to client
    :param conn: the connection to client socket
    """
    conn.send(f"{func}{SEP}{q}".encode(FORMAT))


def start_server():
    """
    the starting function of the program. connects clients as long their is less then 5 clients.
    """
    # Opening Server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # binding socket with specified (IP,PORT) tuple
    server_socket.bind(ADDR)
    # Server is open for connections
    server_socket.listen()

    while True:
        connection, address = server_socket.accept()  # Waiting for client to connect to server (blocking call)
        # condition that limits number of users 5
        if threading.activeCount() >= 6:
            # send client error message
            func, q = pose_q0('failed to connect: server capacity is full')
            send_client(func, q, connection)
            # close connection for client
            connection.close()
        else:
            thread = threading.Thread(target=run, args=(connection, 1024))  # Creating new Thread object.
            # Passing the handle func and full address to thread constructor
            thread.start()


def pose_q0(q):
    """
    :param q: exit message
    :return: func as None to exit the program and exit message
    """
    func = None
    return func, q


def pose_q1(valid=1):
    """
    :param valid: for invalid client input value different the default value
    :return: relevant function and question to ask
    """
    questions = "Who would you like to play against?\n" \
               "1. I don't want to play\n" \
               "2. Against the computer"
    func = Q1
    if valid == 0:
        new_questions = "Please enter valid number\n" + questions
        return func, new_questions
    else:
        return func, questions


def pose_q2(valid=1):
    """
    :param valid: for invalid client input value different the default value
    :return: relevant function and question to ask
    """

    questions = "What level of game do you want to play?\n" \
                "1. Easy\n" \
                "2. Hard"
    func = Q2
    if valid == 0:
        new_question = "pleas enter valid number\n" + questions
        return func, new_question
    else:
        return func, questions


def pose_q4(valid=0):
    """
    function posing question in case of easy level.
    :param valid: for invalid client input value different the default value
    :return: relevant function and question to ask
    """

    questions = "what would you like to be the numbers of wins to win the game?\n" \
                "(expects a number bigger than 1)"
    func = Q4
    if valid == -1:
        new_question = "pleas enter valid number\n" + questions
        return func, new_question
    elif valid == 0:
        return func, questions
    else:
        pause_error = "You have been wrong " + str(valid*5) + " times and locked yourself for " \
                      + str(valid) + " seconds"
        new_question = pause_error + questions
        return func, new_question


def pose_q5(valid=0):
    """
    function posing question in case of hard level.
    :param valid: for invalid client input value different the default value
    :return: relevant function and question to ask
    """

    questions = "what would you like to be the numbers of wins to win the game?\n" \
                    "(expects a number bigger than 1)"
    func = Q5
    if valid == -1:
        new_question = "pleas enter valid number\n" + questions
        return func, new_question
    elif valid == 0:
        return func, questions
    else:
        pause_error = "You have been wrong " + str(valid*5) + " times and locked yourself for " \
                      + str(valid) + "seconds\n"
        new_question = pause_error + questions
        return func, new_question


def q1(res):
    """
    Processes the responses to Question 1
    :param res: user answer
    :return: next function, next questions
    """

    valids = ['1', '2']
    if res in valids:
        picked = int(res)
        if picked == 1:
            return pose_q0("Goodbye")
        elif picked == 2:
            return pose_q2()
        # elif picked == 3:
            # return pose_q3()
        #    pass
    else:
        # FAIL path
        return pose_q1(0)


def q2(res):
    """
        Processes the responses to Question 2
        :param res: user answer
        :return: next function, next questions
        """

    valids = ['1', '2']
    if res in valids:
        picked = int(res)
        if picked == 1:
            return pose_q4()
        elif picked == 2:
            return pose_q5()
    else:
        # FAIL path
        return pose_q2(0)


def q4(res):
    """
        Processes the responses to Question 4
        :param res: user answer
        :return: next function, next questions
        """

    # check if value is valid
    num, pause_count = number_of_games(res)

    if num == 0 and wrong_count % 5:
        return pose_q4(-1)
    elif num == 0:
        return pose_q4(pause_count)
    else:
        return Q6, num


def q5(res):
    """
        Processes the responses to Question 5
        :param res: user answer
        :return: next function, next questions
        """
    num, count = number_of_games(res)
    if num == 0 and count == 0:
        return pose_q5(-1)
    elif num == 0 and count != 0:
        return pose_q5(count)
    else:
        return Q7, num


def number_of_games(res):
    """
    :param res: get the result of number of games
    :return: The function checks for valid input and return the input if valid,
             else the function return 0 and number of minute to wait(in case of fifth error)
    """
    # we set global values to use at in outsider functions
    global wrong_count
    global pause_count

    # at first iteration we set initial value with except.
    try:
        if wrong_count:
            wrong_count = wrong_count
    except:
        pause_count = 0
        wrong_count = 0

    # make sure the client input is an integer
    if res.isnumeric():
        res = int(res)
    else:
        res = 0

    # check for a valid number
    if res >= 1:
        return res, 0
    else:
        res = 0

    # the client chose an invalid number
    wrong_count += 1
    if wrong_count % 5:
        return res, 0
    # the client chose an invalid number for the fifth time in a row
    else:
        pause_count += 1
        return res, pause_count


def easy_level(conn, games_num):
    """
    the function responsible for the easy level.
    :param conn: the connection to client socket
    :param games_num: numbers of wint to get to.
    :return: if the game is over the function returns None to close connection for client.
    """
    shortest_round_cli = 100
    shortest_round_com = 100
    com_win = 0
    cli_win = 0
    while True:
        count_turns = 1
        # build game matrix
        matrix = [["*" for col in range(7)] for row in range(6)]
        matrix.append([str(i) for i in range(7)])
        # flips a coin to see who starts
        your_turn = random.randint(0, 1)
        while True:
            if your_turn == 0:
                # the client turn
                matrix = client_turn(conn, matrix)
                # checks for winning after client turn
                if win_test(matrix):
                    cli_win += 1
                    # checks for the shortest round
                    if count_turns < shortest_round_cli:
                        shortest_round_cli = count_turns
                    # build matrix as a string
                    str_matrix_cli_won = ""
                    for row in matrix:
                        str_matrix_cli_won += f"{row}\n"
                    # checks for winning the game vs. winning the round
                    if cli_win == games_num:
                        uni_win = str_matrix_cli_won + "You won the game\n" \
                                  f"computer won {com_win} times while you won {games_num} times\n" \
                                  f"the shortest game you've played went for {shortest_round_cli} turns"
                        send_client(None, uni_win, conn)
                        return None, None
                    else:
                        client_win_str = str_matrix_cli_won + "You won this round\n" \
                                  f"computer won {com_win} times while you won {cli_win} times\n" \
                                  f"the game you've played went for {count_turns} turns\n" \
                                  f"(your turns + computer turns)\n"

                        send_client(Q100, client_win_str, conn)
                        break
                elif full_board(matrix):
                    msg = "it's a tie, starting a a new game\n"
                    send_client(None, msg, conn)
                    break
                else:
                    count_turns += 1
                your_turn = 1
                continue
            else:
                # the computer turn
                while True:
                    # computer picks randomly
                    com_pick = random.randint(0, 6)
                    for i in matrix[::-1]:
                        if i[com_pick] == "*":
                            i[com_pick] = "X"
                            your_turn = 0
                            break
                    if your_turn == 0:
                        break
                #  sending board game to client
                str_matrix = ""
                for row in matrix:
                    str_matrix += f"{row}\n"
                # checks for a win
                if win_test(matrix):
                    if count_turns < shortest_round_com:
                        shortest_round_com = count_turns
                    com_win += 1
                    # winning the game vs. winning the round
                    if com_win == games_num:
                        uni_win_com = str_matrix + "computer won the game\n" \
                                                f"you won {cli_win} times while the computer won {games_num} times\n" \
                                                f"the shortest game you lost went for {shortest_round_com} turns\n" \
                                                f"better luck next time"
                        send_client(None, uni_win_com, conn)
                        return None, None
                    else:
                        client_win_str_com = str_matrix + "computer won this round\n" \
                                                          f"computer won {com_win} times while you won" \
                                                          f" {cli_win} times\n" \
                                                          f"the game you've played went for {count_turns} turns\n"

                    send_client(Q100, client_win_str_com, conn)
                    break
                # check for a tie
                elif full_board(matrix):
                    msg = "it's a tie, starting a new game\n"
                    send_client(None, msg, conn)
                    break
                else:
                    count_turns += 1


def full_board(matrix):
    """
    checks for a tie
    :param matrix: the game matrix
    :return: 1 for a tie, 0 if there is an open place on matrix
    """
    if "*" in matrix[0]:
        return 0
    else:
        return 1


def hard_level(conn, games_num):
    """
    the function responsible for the hard level.
    :param conn: the connection to client socket
    :param games_num: numbers of wint to get to.
    :return: if the game is over the function returns None to close connection for client.
    """

    shortest_round_cli = 100
    shortest_round_com = 100
    com_win = 0
    cli_win = 0
    while True:
        count_turns = 1
        # building game matrix
        matrix = [["*" for col in range(7)] for row in range(6)]
        matrix.append([str(i) for i in range(7)])
        # flips a coin to start the game
        your_turn = random.randint(0, 1)
        while True:
            if your_turn == 0:
                # the client turn
                matrix = client_turn(conn, matrix)
                # checks for a win
                if win_test(matrix):
                    cli_win += win_test(matrix)
                    if count_turns < shortest_round_cli:
                        shortest_round_cli = count_turns
                    # building matrix as a string
                    str_matrix_cli_won = ""
                    for row in matrix:
                        str_matrix_cli_won += f"{row}\n"
                    # winning the game vs. winning the round
                    if cli_win == games_num:
                        uni_win = str_matrix_cli_won + "You won the game\n" \
                                                       f"computer won {com_win} times while you won" \
                                                       f" {games_num} times\n" \
                                                       f"the shortest game you've played went for" \
                                                       f" {shortest_round_cli} turns"
                        send_client(None, uni_win, conn)
                        return None, None
                    else:
                        client_win_str = str_matrix_cli_won + "You won this round\n" \
                                                              f"computer won {com_win} times while you won" \
                                                              f" {cli_win} times\n" \
                                                              f"the game you've played went for {count_turns} turns\n"

                        send_client(Q100, client_win_str, conn)
                        break
                elif full_board(matrix):
                    msg = "it's a tie, starting a a new game\n"
                    send_client(None, msg, conn)
                    break
                else:
                    count_turns += 1
                your_turn = 1
                continue
            else:
                # the computer turn
                # checks for winning options
                col1, col2 = about_to_win(matrix, 3)
                if col1 in range(7):
                    com_pick = col1
                elif col2 in range(7):
                    com_pick = col2
                else:
                    # checks for blocking client from winning
                    col1, col2 = about_to_win(matrix, 3, "O")
                    if col1 in range(7):
                        com_pick = col1
                    elif col2 in range(7):
                        com_pick = col2
                    else:
                        # checks for optional flush
                        col1, col2 = about_to_win(matrix, 2)
                        if col1 in range(7):
                            com_pick = col1
                        elif col2 in range(7):
                            com_pick = col2
                        else:
                            # checks for optional flush
                            col1, col2 = about_to_win(matrix, 1)
                            if col1 in range(7):
                                com_pick = col1
                            elif col2 in range(7):
                                com_pick = col2
                            else:
                                com_pick = random.randint(0, 6)
                for i in matrix[::-1]:
                    if i[com_pick] == "*":
                        i[com_pick] = "X"
                        your_turn = 0
                        break
            #  sending board game to client
            str_matrix = ""
            for row in matrix:
                str_matrix += f"{row}\n"
            # checks for a win
            if win_test(matrix):
                # checks for the shortest round that was played
                if count_turns < shortest_round_com:
                    shortest_round_com = count_turns
                com_win += win_test(matrix)
                # winning the game vs. winning a round
                if com_win == games_num:
                    uni_win_com = str_matrix + "computer won the game\n" \
                                               f"you won {cli_win} times while the computer won {games_num} times\n" \
                                               f"the shortest game you lost went for {shortest_round_com} turns\n" \
                                               f"better luck next time\n"
                    send_client(None, uni_win_com, conn)
                    return None, None
                else:
                    client_win_str_com = str_matrix + "computer won this round\n" \
                                                      f"computer won {com_win} times while you won {cli_win} times\n" \
                                                      f"the game you've played went for {count_turns} turns\n"

                send_client(Q100, client_win_str_com, conn)
                break
            # checks for a tie
            elif full_board(matrix):
                msg = "it's a tie, starting a new game\n"
                send_client(Q100, msg, conn)
                break
            else:
                count_turns += 1


def client_turn(conn, matrix):
    """
    handles the client turn.
    :param conn: the connection to client socket.
    :param matrix: the game matrix.
    :return: the matrix after the client turn.
    """
    your_turn = 0
    # sending current matrix to client
    str_matrix = ""
    for row in matrix:
        str_matrix += f"{row}\n"
    ask1 = "Please choose a column:"
    ask = str_matrix + ask1
    send_client(Q10, ask, conn)
    # checks for a valid input
    while True:
        res = conn.recv(1024).decode(FORMAT)
        func, column = res.split(SEP)
        if column not in ["0", "1", "2", "3",  "4", "5", "6"]:
            send_client(Q10, "Please enter a valid number:", conn)
            continue
        else:
            column = int(column)
            for i in matrix[::-1]:
                if i[column] == "*":
                    i[column] = "O"
                    your_turn = 1
                    break
            if your_turn == 0:
                send_client(Q10, "The column is full please choose another:", conn)
            else:
                return matrix


def win_test(matrix):
    """
    checks for winning.
    :param matrix: the matrix of the game
    :return: 1 for a win, else 0.
    """
    for row_i, row in enumerate(matrix[::-1]):
        # check for computer win
        if "X" in row:
            c_row = 0
            c_column = 0
            c_diag_r = 0
            c_diag_l = 0
            shift_r = 0
            shift_l = 0
            for index, i in enumerate(row):
                if i == "X":
                    c_row += 1
                    if c_row == 4:
                        return 1
                    # check column
                    for row_j, j in enumerate(matrix[::-1]):
                        if j[index] == "X":
                            c_column += 1
                        else:
                            c_column = 0
                        if c_column == 4:
                            return 1
                        # check right diagonal
                        if index < 4:
                            if index + shift_r <= 6:
                                if j[index + shift_r] == "X":
                                    c_diag_r += 1
                                    shift_r += 1
                                else:
                                    c_diag_r = 0
                        # check left diagonal
                        if index > 2:
                            if index - shift_l >= 0:
                                if j[index - shift_l] == "X":
                                    c_diag_l += 1
                                    shift_l += 1
                                else:
                                    c_diag_l = 0
                        if c_diag_r == 4:
                            return 1
                        if c_diag_l == 4:
                            return 1
                else:
                    c_row = 0
        # check for user win
        if "O" in row:
            c_row = 0
            c_column = 0
            c_diag_r = 0
            c_diag_l = 0
            shift_r = 0
            shift_l = 0
            for index, i in enumerate(row):
                if i == "O":
                    c_row += 1
                    if c_row == 4:
                        return 1
                    # check column
                    for row_j, j in enumerate(matrix[::-1]):
                        if j[index] == "O":
                            c_column += 1
                        else:
                            c_column = 0
                        if c_column == 4:
                            return 1
                        # check right diagonal
                        if index < 4:
                            if index + shift_r <= 6:
                                if j[index + shift_r] == "O":
                                    c_diag_r += 1
                                    shift_r += 1
                                else:
                                    c_diag_r = 0
                        # check left diagonal
                        if index > 2:
                            if index - shift_l >= 0:
                                if j[index - shift_l] == "O":
                                    c_diag_l += 1
                                    shift_l += 1
                                else:
                                    c_diag_l = 0
                        if c_diag_r == 4:
                            return 1
                        if c_diag_l == 4:
                            return 1
                else:
                    c_row = 0
    return 0


def about_to_win(matrix, n, d="X"):
    """
    check for wanted sequence.
    :param matrix: the matrix of the game.
    :param n: number of variables for wanted sequence.
    :param d: X or O.
    :return: column for next move.
    """

    for row_i, row in enumerate(matrix[::-1]):
        if "X" in row:
            c_row = 0
            c_column = 0
            c_diag_r = 0
            c_diag_l = 0
            shift_r = 0
            shift_l = 0
            for index, i in enumerate(row):
                if i == d:
                    c_row += 1
                    if c_row >= n:
                        if n - 1 < index < 6:
                            if row[index + 1] == "*" and row[index - n] == "*":
                                return index - n, index + 1
                            elif row[index + 1] == "*":
                                return None, index + 1
                            elif row[index - n] == "*":
                                return index - n, None
                        elif index < 6:
                            if row[index + 1] == "*":
                                return None, index + 1
                        else:
                            if row[index - n] == "*":
                                return index - n, None
                    # check column
                    for row_j, j in enumerate(matrix[::-1]):
                        if j[index] == d:
                            c_column += 1
                        else:
                            c_column = 0
                        if c_column >= n:
                            if row_j < 6:
                                if matrix[len(matrix) - row_j - 2][index] == "*":
                                    return index, None
                        # check right diagonal
                        if index < 8 - n:
                            if index + shift_r <= 6:
                                if j[index + shift_r] == d:
                                    c_diag_r += 1
                                    shift_r += 1
                                else:
                                    c_diag_r = 0
                        # check left diagonal
                        if index > n - 2:
                            if index - shift_l >= 0:
                                if j[index - shift_l] == d:
                                    c_diag_l += 1
                                    shift_l += 1
                                else:
                                    c_diag_l = 0
                        if c_diag_r >= n:
                            if 0 < index < 7 - n and n < row_j < 6:
                                if matrix[len(matrix) - row_j - 1 + n][index - 1] == "*" and \
                                        matrix[len(matrix) - row_j - 2][index + n] == "*":
                                    return index - 1, index + n
                                elif matrix[len(matrix) - row_j - 1 + n][index - 1] == "*":
                                    return index - 1, None
                                elif matrix[len(matrix) - row_j - 2][index + n] == "*":
                                    return index + n, None
                            elif index < 7 - n and row_j < 6:
                                if matrix[len(matrix) - row_j - 2][index + n] == "*":
                                    return index + n, None
                            elif 0 < index and n < row_j:
                                if matrix[len(matrix) - row_j - 1 + n][index - 1] == "*":
                                    return None, index - 1
                            else:
                                return None, None
                        if c_diag_l >= n:
                            if n - 1 < index < 6 and n < row_j < 6:
                                if matrix[len(matrix) - row_j - 1 + n][index + 1] == "*" and \
                                        matrix[len(matrix) - row_j - 2][index - n] == "*":
                                    return index + 1,  index - n
                                elif matrix[len(matrix) - row_j - 1 + n][index + 1] == "*":
                                    return index + 1, None
                                elif matrix[len(matrix) - row_j - 2][index - n]:
                                    return None, index - n
                            elif n - 1 < index and row_j < 6:
                                if matrix[len(matrix) - row_j - 2][index - n]:
                                    return index - n, None
                            elif index < 6 and n < row_j:
                                if matrix[len(matrix) - row_j - 1 + n][index + 1] == "*":
                                    return None, index + 1
                            else:
                                return None, None
                else:
                    c_row = 0
    return None, None


start_server()
