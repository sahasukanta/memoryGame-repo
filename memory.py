import pygame, random

# User-defined functions

def main():
   # initialize all pygame modules (some need initialization)
   pygame.init()
   # create a pygame display window
   pygame.display.set_mode((530,410))
   # set the title of the display window
   pygame.display.set_caption('Memory')
   # get the display surface
   w_surface = pygame.display.get_surface()
   # create a game object
   game = Game(w_surface)
   # start the main game loop by calling the play method on the game object
   game.play()
   # quit pygame and clean up the pygame window
   pygame.quit()

# User-defined classes

class Game:
   # An object in this class represents a complete game.

    def __init__(self, surface):
        # Initialize a Game.
        # - self is the Game to initialize
        # - surface is the display window surface object

        # === objects that are part of every game that we will discuss
        self.surface = surface
        self.bg_color = pygame.Color('blue')

        self.FPS = 60
        self.game_Clock = pygame.time.Clock()
        self.close_clicked = False
        self.continue_game = True

        # === game specific objects
        self.board_row_size = 4
        self.board = []
        self.create_board()
        # time elapsed
        self.time_elapsed = None
        # number of tiles chosen (max=2) at any given time
        self.number_of_tiles_chosen = 0
        # list of tiles (max=2) currently selected
        self.selected_tiles = []
        # counter used to block mouse events after two tiles are selected
        self.mouse_block_delay = 0
        # list of tiles that are already found
        self.tiles_matched = 0

        # loading the default tile image
        self.default_tile = pygame.image.load("images/image0.bmp")
        # assigning images to tiles
        self.add_image_to_tiles()

        # adding the indicator (misc.)
        self.indicator_color = pygame.Color('green')
        self.indicator = pygame.Rect((self.surface.get_width()-121),102,120,30)

    def add_image_to_tiles(self):

        # creating the image objects with the images
        self.images = []
        self.image_dict = {}
        for i in range(1,9):
            image_name = "images/image{}.bmp".format(i)
            load_image = pygame.image.load(image_name)
            self.images.append(load_image)

        # copying original images list
        self.image_list = self.images + self.images

        # pairing up the same images for match-checking in a dict format
        images_A = self.image_list[:len(self.images)]
        images_B = self.image_list[len(self.images):]
        for i in range(len(self.images)):
            self.image_dict[images_A[i]] = images_B[i]

        # shuffling images
        random.shuffle(self.image_list)

        # assigning image to each tile
        for row in self.board:
            for tile in row:
                chosen_image = self.image_list[0]
                tile.set_image(chosen_image)
                self.image_list = self.image_list[1:]

    def create_board(self):
        # creates the tiles on the board
        width = (self.surface.get_width()-120)//4
        height = (self.surface.get_height()+5)//4
        for row_index in range(self.board_row_size):
            row = []
            for col_index in range(self.board_row_size):
                x = col_index*width
                y = row_index*height
                tile = Tile(x,y,width,height, self.surface)
                row.append(tile)
            self.board.append(row)

    def play(self):
        # Play the game until the player presses the close box.
        # - self is the Game that should be continued or not.
        while not self.close_clicked:  # until player clicks close box
            # play frame
            self.handle_events()
            if self.continue_game:
                self.draw()
                self.update()
                self.decide_continue()
            self.game_Clock.tick(self.FPS) # run at most with FPS Frames Per Second

    def handle_events(self):
        # Handle each user event by changing the game state appropriately.
        # - self is the Game whose events will be handled
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.close_clicked = True
            if event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_up(event)

    def update_game_state(self):
        # setting game state: blocking mouse button up event if two tiles are already selected
        if self.number_of_tiles_chosen > 1:
            pygame.event.set_blocked(pygame.MOUSEBUTTONUP)
            self.mouse_block_delay += 1
            self.indicator_color = pygame.Color('red')
            # reverting the mouse button up block
            if self.mouse_block_delay == 30:
                pygame.event.set_allowed(pygame.MOUSEBUTTONUP)
                # if two tiles are matched
                if self.image_dict[self.selected_tiles[0].get_image()] == self.selected_tiles[1].get_image():
                    self.tiles_matched += 2
                # if two tiles are not matched
                else:
                    for i in range(2):
                        self.selected_tiles[i].hidden = True
                # resetting dynamic variables
                self.mouse_block_delay = 0
                self.number_of_tiles_chosen = 0
                self.selected_tiles = []
                self.indicator_color = pygame.Color('green')

    def handle_mouse_up(self, event):
        # Respond to the player releasing the mouse button by
        # taking appropriate actions.
        # - self is the Game where the mouse up occurred.
        # - event is the pygame.event.Event object to handle
        for row in self.board:
            for tile in row:
                if tile.select(event.pos):
                    if tile.is_hidden():
                        tile.set_hidden(False)
                        self.number_of_tiles_chosen += 1
                        self.selected_tiles.append(tile)

    def draw(self):
        # Draw all game objects.
        # - self is the Game to draw
        self.surface.fill(self.bg_color) # clear the display surface first
        for row in self.board:
            for tile in row:
                if tile.is_hidden():
                    self.surface.blit(self.default_tile, tile)
                else:
                    self.surface.blit(tile.image, tile)
        # draw timer
        self.draw_time()
        # draw indicator
        pygame.draw.rect(self.surface, self.indicator_color, self.indicator)
        pygame.display.update() # make the updated surface appear on the display

    def draw_time(self):
        text_color = pygame.Color('white')
        text_font = pygame.font.SysFont('', 100)
        text_image = text_font.render(self.time_elapsed, True, text_color)
        x = self.surface.get_width()-122
        y = 2
        self.surface.blit(text_image, (x, y))

    def update(self):
        # Update the game objects for the next frame.
        # - self is the Game to update
        self.update_game_state()
        # update time
        self.time_elapsed = str(pygame.time.get_ticks()//1000)

    def decide_continue(self):
        # Check and remember if the game should continue
        # - self is the Game to check
        if self.tiles_matched >= self.board_row_size**2:
            self.continue_game = False

class Tile:

    def __init__(self, x, y, width, height, surface):
        self.surface = surface
        self.rect = pygame.Rect(x, y, width, height)
        self.color = pygame.Color("white")
        self.hidden = True
        self.image = None

    # def assign_image(self, image):
    #     self.image = image

    def draw(self):
        line_width = 3
        pygame.draw.rect(self.surface, self.color, self.rect, line_width)
        border_width = 3
        if not self.flashing:
            pygame.draw.rect(self.surface, self.color, self.rect, border_width)
            self.draw_content()
        else:
            pygame.draw.rect(self.surface, self.color, self.rect)
            self.flashing = False

    def select(self, position):
        # returns true if mouse selects a tile, false otherwise
        return self.rect.collidepoint(position)

    def get_image(self):
        return self.image

    def set_image(self, image):
        self.image = image

    def is_hidden(self):
        return self.hidden

    def set_hidden(self, state):
        self.hidden = state

main()


