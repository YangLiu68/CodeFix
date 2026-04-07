"""
Gomoku (Five in a Row) Game
A classic two-player strategy board game.
Players take turns placing stones. First to get 5 in a row wins!
"""

import pygame
import sys

# Initialize pygame
pygame.init()

# Constants
BOARD_SIZE = 15  # 15x15 board
CELL_SIZE = 40
MARGIN = 50
WINDOW_SIZE = BOARD_SIZE * CELL_SIZE + MARGIN * 2

# Colors
BOARD_COLOR = (220, 179, 92)
LINE_COLOR = (50, 50, 50)
BLACK_STONE = (20, 20, 20)
WHITE_STONE = (240, 240, 240)
HIGHLIGHT_COLOR = (255, 100, 100)
TEXT_COLOR = (50, 50, 50)
BUTTON_COLOR = (100, 150, 200)
BUTTON_HOVER_COLOR = (130, 180, 230)

# Stone constants
EMPTY = 0
BLACK = 1
WHITE = 2


class GomokuGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 60))
        pygame.display.set_caption("Gomoku - Five in a Row")
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        self.reset_game()
        
    def reset_game(self):
        """Reset the game to initial state"""
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = BLACK
        self.game_over = False
        self.winner = None
        self.winning_stones = []
        self.move_count = 0
        
    def get_board_position(self, mouse_pos):
        """Convert mouse position to board coordinates"""
        x, y = mouse_pos
        board_x = round((x - MARGIN) / CELL_SIZE)
        board_y = round((y - MARGIN) / CELL_SIZE)
        
        # Check if within board bounds
        if 0 <= board_x < BOARD_SIZE and 0 <= board_y < BOARD_SIZE:
            # Check if click is close enough to intersection
            actual_x = MARGIN + board_x * CELL_SIZE
            actual_y = MARGIN + board_y * CELL_SIZE
            if abs(x - actual_x) < CELL_SIZE // 2 and abs(y - actual_y) < CELL_SIZE // 2:
                return board_x, board_y
        return None
    
    def place_stone(self, x, y):
        """Place a stone at the given position"""
        if self.board[y][x] == EMPTY and not self.game_over:
            self.board[y][x] = self.current_player
            self.move_count += 1
            
            # Check for win
            if self.check_win(x, y):
                self.game_over = True
                self.winner = self.current_player
            elif self.move_count >= BOARD_SIZE * BOARD_SIZE:
                self.game_over = True
                self.winner = None  # Draw
            else:
                # Switch player
                self.current_player = WHITE if self.current_player == BLACK else BLACK
            return True
        return False
    
    def check_win(self, x, y):
        """Check if the current move wins the game"""
        player = self.board[y][x]
        directions = [
            (1, 0),   # Horizontal
            (0, 1),   # Vertical
            (1, 1),   # Diagonal \
            (1, -1)   # Diagonal /
        ]
        
        for dx, dy in directions:
            stones = [(x, y)]
            
            # Check positive direction
            nx, ny = x + dx, y + dy
            while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and self.board[ny][nx] == player:
                stones.append((nx, ny))
                nx += dx
                ny += dy
            
            # Check negative direction
            nx, ny = x - dx, y - dy
            while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and self.board[ny][nx] == player:
                stones.append((nx, ny))
                nx -= dx
                ny -= dy
            
            if len(stones) >= 5:
                self.winning_stones = stones
                return True
        
        return False
    
    def draw_board(self):
        """Draw the game board"""
        self.screen.fill(BOARD_COLOR)
        
        # Draw grid lines
        for i in range(BOARD_SIZE):
            # Horizontal lines
            start_x = MARGIN
            end_x = MARGIN + (BOARD_SIZE - 1) * CELL_SIZE
            y = MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, LINE_COLOR, (start_x, y), (end_x, y), 1)
            
            # Vertical lines
            x = MARGIN + i * CELL_SIZE
            start_y = MARGIN
            end_y = MARGIN + (BOARD_SIZE - 1) * CELL_SIZE
            pygame.draw.line(self.screen, LINE_COLOR, (x, start_y), (x, end_y), 1)
        
        # Draw star points (traditional markers)
        star_points = [3, 7, 11] if BOARD_SIZE >= 13 else [2, 4] if BOARD_SIZE >= 5 else []
        for i in star_points:
            for j in star_points:
                x = MARGIN + i * CELL_SIZE
                y = MARGIN + j * CELL_SIZE
                pygame.draw.circle(self.screen, LINE_COLOR, (x, y), 4)
    
    def draw_stones(self):
        """Draw all stones on the board"""
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if self.board[y][x] != EMPTY:
                    pos_x = MARGIN + x * CELL_SIZE
                    pos_y = MARGIN + y * CELL_SIZE
                    
                    # Determine stone color
                    color = BLACK_STONE if self.board[y][x] == BLACK else WHITE_STONE
                    
                    # Draw stone shadow
                    pygame.draw.circle(self.screen, (100, 100, 100), (pos_x + 2, pos_y + 2), CELL_SIZE // 2 - 2)
                    
                    # Draw stone
                    pygame.draw.circle(self.screen, color, (pos_x, pos_y), CELL_SIZE // 2 - 2)
                    
                    # Add highlight for white stones
                    if self.board[y][x] == WHITE:
                        pygame.draw.circle(self.screen, (255, 255, 255), (pos_x - 5, pos_y - 5), 5)
                    
                    # Highlight winning stones
                    if (x, y) in self.winning_stones:
                        pygame.draw.circle(self.screen, HIGHLIGHT_COLOR, (pos_x, pos_y), CELL_SIZE // 2 - 2, 3)
    
    def draw_hover(self, mouse_pos):
        """Draw a preview of where the stone will be placed"""
        if not self.game_over:
            pos = self.get_board_position(mouse_pos)
            if pos:
                x, y = pos
                if self.board[y][x] == EMPTY:
                    pos_x = MARGIN + x * CELL_SIZE
                    pos_y = MARGIN + y * CELL_SIZE
                    color = BLACK_STONE if self.current_player == BLACK else WHITE_STONE
                    # Draw semi-transparent preview
                    s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    pygame.draw.circle(s, (*color, 100), (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 2 - 2)
                    self.screen.blit(s, (pos_x - CELL_SIZE // 2, pos_y - CELL_SIZE // 2))
    
    def draw_status(self):
        """Draw game status and controls"""
        # Status area background
        pygame.draw.rect(self.screen, (180, 140, 70), (0, WINDOW_SIZE, WINDOW_SIZE, 60))
        
        if self.game_over:
            if self.winner == BLACK:
                text = "Black Wins!"
            elif self.winner == WHITE:
                text = "White Wins!"
            else:
                text = "Draw!"
        else:
            player = "Black" if self.current_player == BLACK else "White"
            text = f"{player}'s Turn"
        
        # Draw status text
        text_surface = self.font.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE + 20))
        self.screen.blit(text_surface, text_rect)
        
        # Draw restart button
        button_rect = pygame.Rect(WINDOW_SIZE // 2 - 60, WINDOW_SIZE + 35, 120, 20)
        mouse_pos = pygame.mouse.get_pos()
        button_color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=5)
        
        restart_text = self.small_font.render("Restart (R)", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=button_rect.center)
        self.screen.blit(restart_text, restart_rect)
        
        return button_rect
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        
        while True:
            mouse_pos = pygame.mouse.get_pos()
            button_rect = pygame.Rect(WINDOW_SIZE // 2 - 60, WINDOW_SIZE + 35, 120, 20)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Check restart button
                        if button_rect.collidepoint(mouse_pos):
                            self.reset_game()
                        else:
                            # Try to place stone
                            pos = self.get_board_position(mouse_pos)
                            if pos:
                                self.place_stone(pos[0], pos[1])
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Restart with R key
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:  # Quit with ESC
                        pygame.quit()
                        sys.exit()
            
            # Draw everything
            self.draw_board()
            self.draw_hover(mouse_pos)
            self.draw_stones()
            self.draw_status()
            
            pygame.display.flip()
            clock.tick(60)


def main():
    """Entry point for the game"""
    game = GomokuGame()
    game.run()


if __name__ == "__main__":
    main()
