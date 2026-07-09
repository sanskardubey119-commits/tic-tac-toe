import math
import random
import tkinter as tk
from tkinter import messagebox, ttk

try:
    import winsound
except ImportError:
    winsound = None


WIN_LINES = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],
    [0, 3, 6], [1, 4, 7], [2, 5, 8],
    [0, 4, 8], [2, 4, 6],
]


def check_winner(board, player):
    for line in WIN_LINES:
        if all(board[pos] == player for pos in line):
            return True
    return False


def is_draw(board):
    return " " not in board


class TicTacToeGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tic-Tac-Toe")
        self.geometry("560x560")
        self.minsize(520, 520)
        self.resizable(True, True)
        self._updating_size = False
        self.bind("<Configure>", self.keep_window_square)

        self.board = [" " for _ in range(9)]
        self.current_player = "X"
        self.game_over = False
        self.game_started = False
        self.scoreboard = {"X": 0, "O": 0, "draw": 0}
        self.difficulty = tk.StringVar(value="Hard")
        self.sound_enabled = tk.BooleanVar(value=True)
        self.effects_enabled = tk.BooleanVar(value=True)
        self.thinking_animation_id = None
        self.confetti_pieces = []

        self.configure(bg="#f4f7fb")
        self.create_widgets()
        self.update_scoreboard()
        self.after(100, self.update_board_size)
        self.reset_board(start=False)

    def keep_window_square(self, event):
        if self._updating_size or event.widget != self:
            return

        if event.width != event.height:
            self._updating_size = True
            size = min(event.width, event.height)
            self.geometry(f"{size}x{size}")
            self._updating_size = False
            self.after(50, self.update_board_size)

    def update_board_size(self):
        if not hasattr(self, "board_holder") or not hasattr(self, "board_frame"):
            return

        holder_width = self.board_holder.winfo_width()
        holder_height = self.board_holder.winfo_height()
        if holder_width <= 1 or holder_height <= 1:
            self.after(50, self.update_board_size)
            return

        size = min(holder_width, holder_height)
        self.board_frame.place_configure(width=size, height=size, x=(holder_width - size) // 2, y=(holder_height - size) // 2)

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#f4f7fb")
        main_frame.pack(fill="both", expand=True, padx=16, pady=12)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=0)
        main_frame.rowconfigure(2, weight=0)
        main_frame.rowconfigure(3, weight=0)
        main_frame.rowconfigure(4, weight=1)
        main_frame.rowconfigure(5, weight=0)

        title = tk.Label(
            main_frame,
            text="Tic-Tac-Toe",
            font=("Segoe UI", 24, "bold"),
            fg="#1f2937",
            bg="#f4f7fb",
            pady=10,
        )
        title.grid(row=0, column=0, sticky="n")

        controls = tk.Frame(main_frame, bg="#f4f7fb")
        controls.grid(row=1, column=0, pady=(0, 10))

        tk.Label(controls, text="Difficulty:", bg="#f4f7fb", font=("Segoe UI", 11)).pack(side=tk.LEFT)
        ttk.Combobox(
            controls,
            textvariable=self.difficulty,
            values=["Easy", "Medium", "Hard"],
            state="readonly",
            width=10,
        ).pack(side=tk.LEFT, padx=(6, 0))

        tk.Checkbutton(
            controls,
            text="Sound",
            variable=self.sound_enabled,
            bg="#f4f7fb",
            activebackground="#f4f7fb",
            selectcolor="#f4f7fb",
            font=("Segoe UI", 10),
        ).pack(side=tk.LEFT, padx=(16, 10))
        tk.Checkbutton(
            controls,
            text="Effects",
            variable=self.effects_enabled,
            bg="#f4f7fb",
            activebackground="#f4f7fb",
            selectcolor="#f4f7fb",
            font=("Segoe UI", 10),
        ).pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Press Start to begin")
        status = tk.Label(
            main_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 11, "italic"),
            fg="#4b5563",
            bg="#f4f7fb",
            pady=6,
        )
        status.grid(row=2, column=0, sticky="n")

        score_frame = tk.Frame(main_frame, bg="#f4f7fb", pady=6)
        score_frame.grid(row=3, column=0)
        self.score_labels = {
            "X": tk.StringVar(value="You ❌: 0"),
            "O": tk.StringVar(value="AI ⭕: 0"),
            "draw": tk.StringVar(value="Draws: 0"),
        }
        tk.Label(score_frame, textvariable=self.score_labels["X"], bg="#f4f7fb", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=8)
        tk.Label(score_frame, textvariable=self.score_labels["O"], bg="#f4f7fb", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=8)
        tk.Label(score_frame, textvariable=self.score_labels["draw"], bg="#f4f7fb", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=8)

        self.board_holder = tk.Frame(main_frame, bg="#f4f7fb")
        self.board_holder.grid(row=4, column=0, pady=10, sticky="nsew")
        self.board_holder.grid_propagate(False)
        self.board_holder.bind("<Configure>", lambda event: self.update_board_size())

        self.board_frame = tk.Frame(self.board_holder, bg="#f4f7fb")
        self.board_frame.place(x=0, y=0)
        self.board_frame.rowconfigure((0, 1, 2), weight=1)
        self.board_frame.columnconfigure((0, 1, 2), weight=1)
        self.buttons = []
        for index in range(9):
            button = tk.Button(
                self.board_frame,
                text=" ",
                width=10,
                height=3,
                font=("Segoe UI", 22, "bold"),
                command=lambda i=index: self.handle_move(i),
                bg="#ffffff",
                fg="#111827",
                activebackground="#dbeafe",
                relief="ridge",
                bd=2,
            )
            button.grid(row=index // 3, column=index % 3, padx=4, pady=4, sticky="nsew")
            button.bind("<Enter>", lambda event, b=button: self.on_button_hover(b))
            button.bind("<Leave>", lambda event, b=button: self.on_button_leave(b))
            button.bind("<ButtonPress-1>", lambda event, b=button: self.on_button_press(b))
            button.bind("<ButtonRelease-1>", lambda event, b=button: self.on_button_release(b))
            button.bind("<Button-1>", lambda event: self.play_sound("click"))
            self.buttons.append(button)

        footer = tk.Frame(main_frame, bg="#f4f7fb")
        footer.grid(row=5, column=0, pady=10)
        self.start_button = tk.Button(footer, text="Start Game", width=10, command=self.start_button_action, bg="#10b981", fg="white", font=("Segoe UI", 11, "bold"))
        self.start_button.pack(side=tk.LEFT, padx=8)
        self.play_again_button = tk.Button(footer, text="Play Again", width=14, command=self.reset_board, bg="#2563eb", fg="white", font=("Segoe UI", 11, "bold"), state="disabled")
        self.play_again_button.pack(side=tk.LEFT, padx=8)
        tk.Button(footer, text="Reset Score", width=14, command=self.reset_scoreboard, bg="#ef4444", fg="white", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=8)

    def update_scoreboard(self):
        self.score_labels["X"].set(f"You ❌: {self.scoreboard['X']}")
        self.score_labels["O"].set(f"AI ⭕: {self.scoreboard['O']}")
        self.score_labels["draw"].set(f"Draws: {self.scoreboard['draw']}")

    def symbol_to_text(self, symbol):
        return "❌" if symbol == "X" else "⭕"

    def on_button_hover(self, button):
        if button["state"] == "normal":
            button.config(bg="#e0f2fe")

    def on_button_leave(self, button):
        if button["state"] == "normal":
            button.config(bg="#ffffff", relief="ridge")

    def on_button_press(self, button):
        if button["state"] == "normal":
            button.config(bg="#c7d2fe", relief="sunken")

    def on_button_release(self, button):
        if button["state"] == "normal":
            button.config(bg="#e0f2fe", relief="ridge")

    def set_board_state(self, enabled):
        for index, button in enumerate(self.buttons):
            if self.board[index] == " ":
                button.config(state="normal" if enabled else "disabled")
                button.config(bg="#ffffff" if enabled else "#f3f4f6")

    def play_sound(self, event_type):
        if winsound is None or not self.sound_enabled.get():
            return

        if event_type == "click":
            winsound.Beep(880, 70)
        elif event_type == "ai":
            winsound.Beep(740, 90)
        elif event_type == "win":
            winsound.Beep(1046, 120)
            winsound.Beep(1318, 100)
        elif event_type == "lose":
            winsound.Beep(392, 120)
            winsound.Beep(294, 100)
        elif event_type == "draw":
            winsound.Beep(659, 90)
            winsound.Beep(698, 80)
        elif event_type == "start":
            winsound.Beep(988, 100)
            winsound.Beep(1174, 80)
            winsound.Beep(1318, 60)

    def start_button_action(self):
        self.play_sound("start")
        if self.game_started:
            self.smooth_restart()
            return

        self.game_started = True
        self.start_button.config(text="Restart", bg="#f59e0b")
        self.play_again_button.config(state="normal")
        self.reset_board(start=True)
        self.status_var.set("Game started! Your turn")

    def smooth_restart(self):
        self.play_sound("click")
        self.status_var.set("Restarting...")
        self.set_board_state(False)
        for button in self.buttons:
            button.config(bg="#f8fafc")
        self.after(250, lambda: self.reset_board(start=True))

    def start_thinking_animation(self):
        self.stop_thinking_animation()
        self.thinking_dots = 0

        def animate():
            if self.game_over or self.current_player != "O":
                return
            dots = "." * ((self.thinking_dots % 3) + 1)
            self.status_var.set(f"AI is thinking{dots}")
            self.thinking_dots += 1
            self.thinking_animation_id = self.after(400, animate)

        animate()

    def stop_thinking_animation(self):
        if self.thinking_animation_id is not None:
            self.after_cancel(self.thinking_animation_id)
            self.thinking_animation_id = None

    def find_winning_line(self, player):
        for line in WIN_LINES:
            if all(self.board[pos] == player for pos in line):
                return line
        return None

    def highlight_winning_line(self, line, winner=None):
        if not line:
            return
        win_bg = "#4ade80"
        win_fg = "#065f46"
        for index in line:
            self.buttons[index].config(bg=win_bg, fg=win_fg)

    def flash_winner(self, line=None, winner=None):
        if winner == "X":
            win_bg = ["#4ade80", "#86efac"]
        elif winner == "O":
            win_bg = ["#93c5fd", "#bfdbfe"]
        else:
            win_bg = ["#f3f4f6", "#ffffff"]

        count = 0

        def animate():
            nonlocal count
            color = win_bg[count % len(win_bg)]
            if line:
                for index in line:
                    self.buttons[index].config(bg=color)
            else:
                for button in self.buttons:
                    button.config(bg=color)
            count += 1
            if count < 6:
                self.after(150, animate)

        animate()

    def create_confetti(self):
        self.stop_confetti()
        colors = ["#facc15", "#f472b6", "#60a5fa", "#a78bfa", "#34d399"]
        symbols = ["🎉", "✨", "🌟", "💫", "🥳"]
        width = self.board_holder.winfo_width() or 400
        height = self.board_holder.winfo_height() or 400

        for _ in range(18):
            x = random.randint(10, max(10, width - 30))
            y = random.randint(-120, -20)
            label = tk.Label(
                self.board_holder,
                text=random.choice(symbols),
                font=("Segoe UI Emoji", 18),
                bg="#f4f7fb",
                fg=random.choice(colors),
            )
            label.place(x=x, y=y)
            self.confetti_pieces.append({"label": label, "x": x, "y": y, "dy": random.uniform(2.5, 5.5)})

        self.animate_confetti()

    def animate_confetti(self):
        if not self.confetti_pieces:
            return
        height = self.board_holder.winfo_height() or 400
        for piece in list(self.confetti_pieces):
            piece["y"] += piece["dy"]
            piece["x"] += random.uniform(-1.5, 1.5)
            if piece["y"] > height:
                piece["y"] = random.randint(-120, -20)
                piece["x"] = random.randint(10, max(10, self.board_holder.winfo_width() - 30))
            piece["label"].place(x=piece["x"], y=piece["y"])
        self.after(50, self.animate_confetti)

    def stop_confetti(self):
        for piece in self.confetti_pieces:
            piece["label"].destroy()
        self.confetti_pieces = []

    def reset_scoreboard(self):
        self.scoreboard = {"X": 0, "O": 0, "draw": 0}
        self.update_scoreboard()
        self.reset_board()

    def reset_board(self, start=False):
        self.stop_thinking_animation()
        self.stop_confetti()
        self.board = [" " for _ in range(9)]
        self.current_player = "X"
        self.game_over = False
        for button in self.buttons:
            button.config(text=" ", fg="#111827")
        if start or self.game_started:
            self.set_board_state(True)
            self.play_again_button.config(state="normal")
            self.start_button.config(text="Restart", bg="#f59e0b")
            self.status_var.set("Your turn")
        else:
            self.set_board_state(False)
            self.play_again_button.config(state="disabled")
            self.start_button.config(text="Start Game", bg="#10b981")
            self.status_var.set("Press Start to begin")

    def update_button(self, index, symbol):
        self.board[index] = symbol
        self.buttons[index].config(text=self.symbol_to_text(symbol), state="disabled")

    def handle_move(self, index):
        if not self.game_started or self.game_over or self.board[index] != " ":
            return

        self.stop_thinking_animation()
        self.update_button(index, "X")
        self.current_player = "O"
        self.check_game_state()

        if not self.game_over:
            self.start_thinking_animation()
            self.status_var.set("AI is thinking...")
            self.after(700, self.ai_turn)

    def ai_turn(self):
        if self.game_over:
            self.stop_thinking_animation()
            return

        move = self.choose_ai_move()
        if move is None:
            self.stop_thinking_animation()
            return

        self.play_sound("ai")
        self.update_button(move, "O")
        self.current_player = "X"
        self.stop_thinking_animation()
        self.check_game_state()

    def choose_ai_move(self):
        available_moves = [i for i, cell in enumerate(self.board) if cell == " "]
        if not available_moves:
            return None

        difficulty = self.difficulty.get().lower()
        if difficulty == "easy":
            return random.choice(available_moves)

        if difficulty == "medium":
            for move in available_moves:
                board_copy = self.board.copy()
                board_copy[move] = "O"
                if check_winner(board_copy, "O"):
                    return move
            for move in available_moves:
                board_copy = self.board.copy()
                board_copy[move] = "X"
                if check_winner(board_copy, "X"):
                    return move
            if 4 in available_moves:
                return 4
            return random.choice(available_moves)

        return self.alpha_beta_move(self.board)

    def alpha_beta_move(self, board_state):
        best_score = -math.inf
        best_move = None
        available_moves = [i for i, cell in enumerate(board_state) if cell == " "]

        for move in available_moves:
            next_board = board_state.copy()
            next_board[move] = "O"
            score = self.minimax(next_board, 0, -math.inf, math.inf, False)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def minimax(self, board_state, depth, alpha, beta, maximizing):
        if check_winner(board_state, "O"):
            return 10 - depth
        if check_winner(board_state, "X"):
            return depth - 10
        if is_draw(board_state):
            return 0

        available_moves = [i for i, cell in enumerate(board_state) if cell == " "]
        if maximizing:
            value = -math.inf
            for move in available_moves:
                next_board = board_state.copy()
                next_board[move] = "O"
                value = max(value, self.minimax(next_board, depth + 1, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value

        value = math.inf
        for move in available_moves:
            next_board = board_state.copy()
            next_board[move] = "X"
            value = min(value, self.minimax(next_board, depth + 1, alpha, beta, True))
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value

    def check_game_state(self):
        if check_winner(self.board, "X"):
            self.scoreboard["X"] += 1
            self.update_scoreboard()
            self.game_over = True
            self.status_var.set("You won! 🎉")
            self.disable_board()
            winning_line = self.find_winning_line("X")
            self.highlight_winning_line(winning_line, winner="X")
            if self.effects_enabled.get():
                self.flash_winner(winning_line, winner="X")
                self.create_confetti()
            self.play_sound("win")
            return

        if check_winner(self.board, "O"):
            self.scoreboard["O"] += 1
            self.update_scoreboard()
            self.game_over = True
            self.status_var.set("AI wins ⭕")
            self.disable_board()
            winning_line = self.find_winning_line("O")
            self.highlight_winning_line(winning_line, winner="O")
            if self.effects_enabled.get():
                self.flash_winner(winning_line, winner="O")
            self.play_sound("lose")
            return

        if is_draw(self.board):
            self.scoreboard["draw"] += 1
            self.update_scoreboard()
            self.game_over = True
            self.status_var.set("It's a draw")
            self.disable_board()
            if self.effects_enabled.get():
                self.flash_winner(None)
            self.play_sound("draw")
            return

    def disable_board(self):
        for button in self.buttons:
            button.config(state="disabled")


if __name__ == "__main__":
    app = TicTacToeGUI()
    app.mainloop()
