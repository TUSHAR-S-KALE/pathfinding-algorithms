import pygame
import sys
import random
from queue import Queue
import heapq

pygame.init()

#Screen dimensions
WIDTH, HEIGHT = 800, 600
BUTTON_WIDTH, BUTTON_HEIGHT = 200, 50
CELL_SIZE = 20

#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

#Font
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game with Pathfinding Algorithms")
font = pygame.font.Font(None, 30)

player_pos = [1, 1]
goal_pos = None
maze = None

#Difficulty settings
DIFFICULTY_SETTINGS = {
    "Easy": (20, 20, 0.15),
    "Medium": (25, 25, 0.2),
    "Hard": (30, 30, 0.25)
}

difficulty = None
game_started = False
path = []
game_over = False

def generate_maze(cols, rows, break_probability):
    maze = [[1] * cols for _ in range(rows)]
    
    def carve(x, y):
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and maze[ny][nx] == 1:
                maze[ny][nx] = 0
                maze[y + dy // 2][x + dx // 2] = 0
                carve(nx, ny)
    
    maze[1][1] = 0
    carve(1, 1)
    
    #Adding random openings (probability)
    for y in range(1, rows - 1):
        for x in range(1, cols - 1):
            if random.random() < break_probability:
                maze[y][x] = 0
    return maze

#Algorithms
#Breadth First Search
def bfs(maze, start, goal):
    queue = Queue()
    queue.put((start, [start]))
    visited = set()
    
    while not queue.empty():
        (x, y), path = queue.get()
        if (x, y) == goal:
            return path
        visited.add((x, y))
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] == 0 and (nx, ny) not in visited:
                queue.put(((nx, ny), path + [(nx, ny)]))
    return []

#Depth First Search
def dfs(maze, start, goal):
    stack = [(start, [start])]
    visited = set()
    
    while stack:
        (x, y), path = stack.pop()
        if (x, y) == goal:
            return path
        visited.add((x, y))
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] == 0 and (nx, ny) not in visited:
                stack.append(((nx, ny), path + [(nx, ny)]))
    return []

#Best First Search
def best_first_search(maze, start, goal):
    queue = []
    heapq.heappush(queue, (heuristic(start, goal), start, [start]))
    visited = set()

    while queue:
        _, (x, y), path = heapq.heappop(queue)
        
        if (x, y) == goal:
            return path
        visited.add((x, y))

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and 
                maze[ny][nx] == 0 and (nx, ny) not in visited):
                new_path = path + [(nx, ny)]
                heapq.heappush(queue, (heuristic((nx, ny), goal), (nx, ny), new_path))
                visited.add((nx, ny))
    return []

def heuristic(cell, goal):
    return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])

#A* Search
def a_star(maze, start, goal):
    rows, cols = len(maze), len(maze[0])
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_cost = {start: 0}
    h_cost = {start: manhattan_distance(start, goal)}
    f_cost = {start: h_cost[start]}
    
    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            return reconstruct_path(came_from, current)

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < cols and 0 <= neighbor[1] < rows and maze[neighbor[1]][neighbor[0]] == 0:
                tentative_g_cost = g_cost[current] + 1

                if neighbor not in g_cost or tentative_g_cost < g_cost[neighbor]:
                    came_from[neighbor] = current
                    g_cost[neighbor] = tentative_g_cost
                    h_cost[neighbor] = manhattan_distance(neighbor, goal)
                    f_cost[neighbor] = g_cost[neighbor] + h_cost[neighbor]
                    heapq.heappush(open_set, (f_cost[neighbor], neighbor))
    
    return []

#For heuristic
def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.append(current)
    return path[::-1]


#AO Star
def ao_star(maze, start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))

    g_cost = {start: 0}
    parents = {start: None}
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == goal:
            return reconstruct_path_ao(parents, current)
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            
            if 0 <= neighbor[0] < len(maze[0]) and 0 <= neighbor[1] < len(maze):
                if maze[neighbor[1]][neighbor[0]] == 0:
                    tentative_g_cost = g_cost[current] + 1
                    
                    if neighbor not in g_cost or tentative_g_cost < g_cost[neighbor]:
                        g_cost[neighbor] = tentative_g_cost
                        parents[neighbor] = current
                        heapq.heappush(open_set, (tentative_g_cost, neighbor))
    
    return []

def reconstruct_path_ao(parents, current):
    path = []
    while current is not None:
        path.append(current)
        current = parents[current]
    return path[::-1]

def draw_maze():
    if maze is None:
        return
    
    rows, cols = len(maze), len(maze[0])
    maze_offset_x = 250
    maze_offset_y = 50
    
    for y in range(rows):
        for x in range(cols):
            cell_color = WHITE if maze[y][x] == 0 else BLACK
            if (x, y) == tuple(player_pos):
                cell_color = BLUE
            elif (x, y) == goal_pos:
                cell_color = GREEN
            elif (x, y) in path:
                cell_color = YELLOW
            pygame.draw.rect(window, cell_color, 
                             (maze_offset_x + x * CELL_SIZE, maze_offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def difficulty_selection_screen():
    global difficulty, game_started

    while not game_started:
        window.fill(BLACK)
        title_text = font.render("Select Difficulty Level", True, WHITE)
        window.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
        
        for i, level in enumerate(DIFFICULTY_SETTINGS):
            button_rect = pygame.Rect(WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2 + i * (BUTTON_HEIGHT + 10), BUTTON_WIDTH, BUTTON_HEIGHT)
            pygame.draw.rect(window, WHITE, button_rect)
            text = font.render(level, True, BLACK)
            window.blit(text, (button_rect.x + (BUTTON_WIDTH - text.get_width()) // 2, button_rect.y + (BUTTON_HEIGHT - text.get_height()) // 2))

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for i, level in enumerate(DIFFICULTY_SETTINGS):
                    button_rect = pygame.Rect(WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2 + i * (BUTTON_HEIGHT + 10), BUTTON_WIDTH, BUTTON_HEIGHT)
                    if button_rect.collidepoint(pos):
                        difficulty = level
                        game_started = True
                        return

def display_game_over_screen():
    global game_over, game_started

    while game_over:
        window.fill(BLACK)
        title_text = font.render("Congratulations! You've reached the goal!", True, WHITE)
        window.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))

        new_game_button = pygame.Rect(WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2, BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(window, WHITE, new_game_button)
        new_game_text = font.render("New Game", True, BLACK)
        window.blit(new_game_text, (new_game_button.x + (BUTTON_WIDTH - new_game_text.get_width()) // 2, new_game_button.y + (BUTTON_HEIGHT - new_game_text.get_height()) // 2))

        exit_button = pygame.Rect(WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2 + BUTTON_HEIGHT + 10, BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(window, WHITE, exit_button)
        exit_text = font.render("Exit", True, BLACK)
        window.blit(exit_text, (exit_button.x + (BUTTON_WIDTH - exit_text.get_width()) // 2, exit_button.y + (BUTTON_HEIGHT - exit_text.get_height()) // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if new_game_button.collidepoint(pos):
                    reset_game()
                    #Starting a new game
                    main()
                elif exit_button.collidepoint(pos):
                    pygame.quit()
                    sys.exit()

def reset_game():
    global path, player_pos, goal_pos, maze, game_over
    path = []
    player_pos = [1, 1]
    maze = None
    goal_pos = None
    game_over = False

def main():
    global player_pos, goal_pos, maze, difficulty, path, CELL_SIZE, game_over

    difficulty_selection_screen()
    
    cols, rows, break_probability = DIFFICULTY_SETTINGS[difficulty]
    CELL_SIZE = min(20, WIDTH // (cols + 15))
    
    maze = generate_maze(cols, rows, break_probability)
    player_pos = [1, 1]
    goal_pos = (cols - 2, rows - 2)
    maze[goal_pos[1]][goal_pos[0]] = 0

    algorithms = [
    ("Breadth First Search", bfs),
    ("Depth First Search", dfs),
    ("Best First Search", best_first_search),
    ("A* Search", a_star),
    ("AO* Search", ao_star)
]

    selected_algorithm = None

    while True:
        window.fill(BLACK)
        for i, (name, _) in enumerate(algorithms):
            button_rect = pygame.Rect(25, 50 + i * (BUTTON_HEIGHT + 10), BUTTON_WIDTH, BUTTON_HEIGHT)
            pygame.draw.rect(window, WHITE, button_rect)
            text = font.render(name, True, BLACK)
            window.blit(text, (button_rect.x + (BUTTON_WIDTH - text.get_width()) // 2, button_rect.y + (BUTTON_HEIGHT - text.get_height()) // 2))

        draw_maze()

        if game_over:
            display_game_over_screen()
            continue

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    new_x, new_y = player_pos[0], player_pos[1] - 1
                elif event.key == pygame.K_DOWN:
                    new_x, new_y = player_pos[0], player_pos[1] + 1
                elif event.key == pygame.K_LEFT:
                    new_x, new_y = player_pos[0] - 1, player_pos[1]
                elif event.key == pygame.K_RIGHT:
                    new_x, new_y = player_pos[0] + 1, player_pos[1]
                else:
                    continue

                if 0 <= new_x < len(maze[0]) and 0 <= new_y < len(maze) and maze[new_y][new_x] == 0:
                    player_pos = [new_x, new_y]
                    if tuple(player_pos) == goal_pos:
                        game_over = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for name, algorithm in algorithms:
                    button_rect = pygame.Rect(25, 50 + algorithms.index((name, algorithm)) * (BUTTON_HEIGHT + 10), BUTTON_WIDTH, BUTTON_HEIGHT)
                    if button_rect.collidepoint(pos):
                        path = algorithm(maze, tuple(player_pos), goal_pos)
                        break

if __name__ == "__main__":
    main()
