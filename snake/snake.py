#!/usr/bin/env python3
import curses
import random
import time

DIFFICULTIES = {
    "1": ("かんたん", 0.15),
    "2": ("ふつう", 0.10),
    "3": ("むずかしい", 0.06),
}

def draw_border(win, h, w):
    win.attron(curses.color_pair(3))
    win.border()
    win.attroff(curses.color_pair(3))

def show_menu(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    title = [
        " ____  _   _    _    _  _______ ",
        "/ ___|| \\ | |  / \\  | |/ / ____|",
        "\\___ \\|  \\| | / _ \\ | ' /|  _|  ",
        " ___) | |\\  |/ ___ \\| . \\| |___ ",
        "|____/|_| \\_/_/   \\_\\_|\\_\\_____|",
    ]

    start_y = h // 2 - 6
    for i, line in enumerate(title):
        x = max(0, w // 2 - len(line) // 2)
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(start_y + i, x, line)
        stdscr.attroff(curses.color_pair(2))

    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(start_y + 6, w // 2 - 8, "難易度を選んでください")
    stdscr.attroff(curses.color_pair(1))

    for key, (name, _) in DIFFICULTIES.items():
        stdscr.addstr(start_y + 7 + int(key), w // 2 - 6, f"  [{key}] {name}")

    stdscr.addstr(start_y + 12, w // 2 - 8, "  [Q] 終了")
    stdscr.refresh()

    while True:
        key = stdscr.getkey().lower()
        if key in DIFFICULTIES:
            return DIFFICULTIES[key]
        if key == "q":
            return None

def show_game_over(stdscr, score, high_score):
    h, w = stdscr.getmaxyx()
    stdscr.clear()

    msgs = [
        "ゲームオーバー！",
        f"スコア: {score}",
        f"ハイスコア: {high_score}",
        "",
        "[R] もう一度  [Q] 終了",
    ]
    start_y = h // 2 - len(msgs) // 2
    for i, msg in enumerate(msgs):
        x = max(0, w // 2 - len(msg) // 2)
        color = curses.color_pair(4) if i == 0 else curses.color_pair(1)
        stdscr.attron(color)
        stdscr.addstr(start_y + i, x, msg)
        stdscr.attroff(color)

    stdscr.refresh()
    while True:
        key = stdscr.getkey().lower()
        if key == "r":
            return True
        if key == "q":
            return False

def run_game(stdscr, speed, high_score):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.clear()

    h, w = stdscr.getmaxyx()
    # game area inside border
    gh, gw = h - 2, w - 2

    snake = [(gh // 2, gw // 2), (gh // 2, gw // 2 - 1), (gh // 2, gw // 2 - 2)]
    direction = (0, 1)
    pending_dir = direction

    def random_food():
        while True:
            fy = random.randint(1, gh)
            fx = random.randint(1, gw)
            if (fy, fx) not in snake:
                return (fy, fx)

    food = random_food()
    score = 0
    last_move = time.time()

    while True:
        # input
        try:
            key = stdscr.getkey()
        except curses.error:
            key = None

        if key in ("KEY_UP", "w", "k") and direction != (1, 0):
            pending_dir = (-1, 0)
        elif key in ("KEY_DOWN", "s", "j") and direction != (-1, 0):
            pending_dir = (1, 0)
        elif key in ("KEY_LEFT", "a", "h") and direction != (0, 1):
            pending_dir = (0, -1)
        elif key in ("KEY_RIGHT", "d", "l") and direction != (0, -1):
            pending_dir = (0, 1)
        elif key == "q":
            return score, high_score, False

        now = time.time()
        if now - last_move >= speed:
            last_move = now
            direction = pending_dir
            head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

            # collision with walls
            if not (1 <= head[0] <= gh and 1 <= head[1] <= gw):
                break
            # collision with self
            if head in snake:
                break

            snake.insert(0, head)
            if head == food:
                score += 10
                if score > high_score:
                    high_score = score
                food = random_food()
            else:
                snake.pop()

        # draw
        stdscr.clear()
        draw_border(stdscr, h, w)

        # score header
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(0, 2, f" スコア: {score}  ハイスコア: {high_score}  [Q]終了 ")
        stdscr.attroff(curses.color_pair(1))

        # food
        stdscr.attron(curses.color_pair(4))
        stdscr.addstr(food[0], food[1], "●")
        stdscr.attroff(curses.color_pair(4))

        # snake
        for i, (sy, sx) in enumerate(snake):
            if 1 <= sy <= gh and 1 <= sx <= gw:
                color = curses.color_pair(2) if i == 0 else curses.color_pair(1)
                stdscr.attron(color)
                stdscr.addstr(sy, sx, "■" if i == 0 else "□")
                stdscr.attroff(color)

        stdscr.refresh()
        time.sleep(0.01)

    return score, high_score, True

def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

    high_score = 0

    while True:
        result = show_menu(stdscr)
        if result is None:
            break
        name, speed = result

        while True:
            score, high_score, show_over = run_game(stdscr, speed, high_score)
            if not show_over:
                break
            again = show_game_over(stdscr, score, high_score)
            if not again:
                break

if __name__ == "__main__":
    curses.wrapper(main)
