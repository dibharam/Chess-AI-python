import copy

# Define the board as an 8x8 list of lists with piece notation
# Uppercase = White, Lowercase = Black
# P/p = Pawn, R/r = Rook, N/n = Knight, B/b = Bishop, Q/q = Queen, K/k = King
initial_board = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p", "p", "p", "p", "p", "p", "p", "p"],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    ["P", "P", "P", "P", "P", "P", "P", "P"],
    ["R", "N", "B", "Q", "K", "B", "N", "R"],
]

# Function to print the board in a readable format
def print_board(board):
    print("  a b c d e f g h")
    for i, row in enumerate(board):
        print(8 - i, end=" ")
        for piece in row:
            print(piece, end=" ")
        print(8 - i)
    print("  a b c d e f g h\n")

# Simple evaluation function: sum piece values for AI
piece_values = {
    'P': 10, 'N': 30, 'B': 30, 'R': 50, 'Q': 90, 'K': 900,
    'p': -10, 'n': -30, 'b': -30, 'r': -50, 'q': -90, 'k': -900,
    '.': 0
}

def evaluate_board(board):
    total = 0
    for row in board:
        for piece in row:
            total += piece_values.get(piece, 0)
    return total

# Check if the move is inside the board boundaries
def is_in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8

# Generate all possible moves for a given color ('white' or 'black')
# For simplicity, this only implements pawn and knight moves fully, and limited moves for others
def generate_moves(board, color):
    moves = []
    enemy_color = 'black' if color == 'white' else 'white'

    # Helper to check if piece belongs to player color
    def is_own_piece(piece):
        if color == 'white':
            return piece.isupper()
        else:
            return piece.islower()

    # Helper to check if piece belongs to enemy color
    def is_enemy_piece(piece):
        if color == 'white':
            return piece.islower()
        else:
            return piece.isupper()

    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if not is_own_piece(piece):
                continue

            if piece.upper() == 'P':
                # Pawns: move forward one or two on first move, capture diagonally
                direction = -1 if color == 'white' else 1
                start_row = 6 if color == 'white' else 1
                # Move forward
                if is_in_bounds(r + direction, c) and board[r + direction][c] == '.':
                    moves.append(((r, c), (r + direction, c)))
                    # Two squares on first move
                    if r == start_row and board[r + 2*direction][c] == '.':
                        moves.append(((r, c), (r + 2*direction, c)))
                # Capture diagonally
                for dc in [-1, 1]:
                    nr, nc = r + direction, c + dc
                    if is_in_bounds(nr, nc) and is_enemy_piece(board[nr][nc]):
                        moves.append(((r, c), (nr, nc)))

            elif piece.upper() == 'N':
                # Knight moves in L shape
                knight_moves = [
                    (r + 2, c + 1), (r + 2, c - 1), (r - 2, c + 1), (r - 2, c - 1),
                    (r + 1, c + 2), (r + 1, c - 2), (r - 1, c + 2), (r - 1, c - 2)
                ]
                for nr, nc in knight_moves:
                    if is_in_bounds(nr, nc):
                        if not is_own_piece(board[nr][nc]):
                            moves.append(((r, c), (nr, nc)))

            elif piece.upper() == 'B':
                # Bishop moves diagonally
                for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    nr, nc = r + dr, c + dc
                    while is_in_bounds(nr, nc):
                        if board[nr][nc] == '.':
                            moves.append(((r, c), (nr, nc)))
                        elif is_enemy_piece(board[nr][nc]):
                            moves.append(((r, c), (nr, nc)))
                            break
                        else:  # own piece
                            break
                        nr += dr
                        nc += dc

            elif piece.upper() == 'R':
                # Rook moves straight
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    while is_in_bounds(nr, nc):
                        if board[nr][nc] == '.':
                            moves.append(((r, c), (nr, nc)))
                        elif is_enemy_piece(board[nr][nc]):
                            moves.append(((r, c), (nr, nc)))
                            break
                        else:
                            break
                        nr += dr
                        nc += dc

            elif piece.upper() == 'Q':
                # Queen moves like rook + bishop
                for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    while is_in_bounds(nr, nc):
                        if board[nr][nc] == '.':
                            moves.append(((r, c), (nr, nc)))
                        elif is_enemy_piece(board[nr][nc]):
                            moves.append(((r, c), (nr, nc)))
                            break
                        else:
                            break
                        nr += dr
                        nc += dc

            elif piece.upper() == 'K':
                # King moves one square any direction
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if is_in_bounds(nr, nc):
                            if not is_own_piece(board[nr][nc]):
                                moves.append(((r, c), (nr, nc)))

    return moves

# Make a move on the board, returning a new board (does not mutate original)
def make_move(board, move):
    new_board = copy.deepcopy(board)
    (r1, c1), (r2, c2) = move
    piece = new_board[r1][c1]
    new_board[r1][c1] = '.'
    new_board[r2][c2] = piece
    return new_board

# Minimax algorithm to choose the best move for the AI
def minimax(board, depth, maximizing_player):
    if depth == 0:
        return evaluate_board(board), None

    color = 'white' if maximizing_player else 'black'
    moves = generate_moves(board, color)

    if not moves:
        # No moves available, so check for checkmate or stalemate (simplified)
        return evaluate_board(board), None

    if maximizing_player:
        max_eval = float('-inf')
        best_move = None
        for move in moves:
            new_board = make_move(board, move)
            eval, _ = minimax(new_board, depth - 1, False)
            if eval > max_eval:
                max_eval = eval
                best_move = move
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        for move in moves:
            new_board = make_move(board, move)
            eval, _ = minimax(new_board, depth - 1, True)
            if eval < min_eval:
                min_eval = eval
                best_move = move
        return min_eval, best_move

# Helper to convert chess notation (like 'e2') to board indices
def notation_to_index(notation):
    col = ord(notation[0]) - ord('a')
    row = 8 - int(notation[1])
    return row, col

# Main game loop
def play_game():
    board = copy.deepcopy(initial_board)
    player_turn = 'white'  # player is white, AI is black

    while True:
        print_board(board)

        if player_turn == 'white':
            # Player's turn
            while True:
                try:
                    move_input = input("Enter your move (e.g., e2e4): ")
                    if len(move_input) != 4:
                        raise ValueError("Invalid input length")
                    start = notation_to_index(move_input[:2])
                    end = notation_to_index(move_input[2:])
                    move = (start, end)
                    legal_moves = generate_moves(board, 'white')
                    print(f"Legal moves for white: {[f'{chr(c1+97)}{8-r1}{chr(c2+97)}{8-r2}' for (r1,c1),(r2,c2) in legal_moves]}")  # debug
                    if move not in legal_moves:
                        raise ValueError("Illegal move")
                    break
                except Exception as e:
                    print(f"Invalid move: {e}")

            board = make_move(board, move)
            player_turn = 'black'

        else:
            print("AI thinking...")
            legal_moves = generate_moves(board, 'black')
            print(f"Legal moves for black: {[f'{chr(c1+97)}{8-r1}{chr(c2+97)}{8-r2}' for (r1,c1),(r2,c2) in legal_moves]}")  # debug

            if not legal_moves:
                print("AI has no moves left. Game over!")
                break

            eval_score, ai_move = minimax(board, 3, False)
            print(f"AI evaluation score: {eval_score}")
            if ai_move is None:
                print("AI cannot find a move. Game over!")
                break

            print(f"AI moves: {chr(ai_move[0][1]+97)}{8-ai_move[0][0]} to {chr(ai_move[1][1]+97)}{8-ai_move[1][0]}")

            board = make_move(board, ai_move)
            player_turn = 'white'



# Start the game
if __name__ == "__main__":
    play_game()
