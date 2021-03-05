import pandas as pd
import numpy as np
import cv2
import time

matrix_monday = pd.read_csv('../data/mm_monday.csv', index_col = 0).T
matrix_monday = np.array(matrix_monday)
simulated_data = pd.read_csv('../data/sim_c10_till_20.csv', sep=',')

TILE_SIZE = 32
OFS = 50

MARKET = """
##################
#................#
#D..DR..RS..SF..F#
#D..DR..RS..SF..F#
#D..DR..RS..SF..F#
#D..DR..RS..SF..F#
#D..DR..RS..SF..F#
#................#
#...CC..CC..CC...#
#...CC..CC..CC...#
#................#
##WW##WW##WW##GG##
""".strip()

class Customer:
    
    def __init__(self, idn, state, transition_mat, terrain_map, image, x, y):
    #def __init__(self,terrain_map, image, x, y):
        self.id = idn
        self.state = state
        self.transition_mat = transition_mat

        self.terrain_map = terrain_map
        self.image = image
        self.x = x
        self.y = y

        self.tr_array_dict = {
        'dairy' : self.transition_mat[0,:],
        'drinks' : self.transition_mat[1,:],
        'entry' : self.transition_mat[2,:],
        'fruit' : self.transition_mat[3,:],
        'spices' : self.transition_mat[4,:]
        }

    def __repr__(self):
        """
        Returns a csv string for that customer.
        """
        #return f'{self.id};{self.state}'
        return f'{self.x};{self.y}'

    def draw(self, frame):
        xpos = OFS + self.x * TILE_SIZE
        ypos = OFS + self.y * TILE_SIZE 
        frame[ypos-32:ypos, xpos-32:xpos] = self.image 
        # overlay the Customer image / sprite onto the frame

    def move(self, direction, frame):
        newx = self.x
        newy = self.y
        if direction == 'up':
            newy -= 1
        if direction == 'down':
            newy += 1
        if direction == 'right':
            newx += 1
        if direction == 'left':
            newx -= 1
        if self.terrain_map.contents[newy][newx] == '.':
        #if self.terrain_map.contents[newy] == '.':
            self.x = newx
            self.y = newy
        self.draw(frame)

    def is_active(self):
        """
        Returns True if the customer has not reached the checkout
        for the second time yet, False otherwise.
        """
        if self.state != 'checkout':
             return True 
        if self.state == 'checkout':
            return False 

    def next_state(self):
        """
        Propagates the customer to the next state
        using a weighted random choice from the transition probabilities
        conditional on the current state.
        Returns nothing.
        """
      
        self.state = np.random.choice(['checkout', 'dairy', 'drinks', 'fruit', 'spices'], p=self.tr_array_dict[f'{self.state}'])

class SupermarketMap:
    """Visualizes the supermarket background"""

    def __init__(self, layout, tiles):
        """
        layout : a string with each character representing a tile
        tile   : a numpy array containing the tile image
        """
        self.tiles = tiles
        self.contents = [list(row) for row in layout.split("\n")]
        self.xsize = len(self.contents[0])
        self.ysize = len(self.contents)
        self.image = np.zeros(
            (self.ysize * TILE_SIZE, self.xsize * TILE_SIZE, 3), dtype=np.uint8
        )
        self.prepare_map()

    def get_tile(self, char):
        """returns the array for a given tile character"""
        if char == "#":
            return self.tiles[0:32, 0:32]
        elif char == "G": # gates
            return self.tiles[8 * 32 : 9 * 32, 3 * 32 : 4 * 32] 
        elif char == "W": # window
            return self.tiles[8 * 32 : 9 * 32, 4 * 32 : 5 * 32]
        elif char == "C": # checkout
            return self.tiles[2 * 32 : 3 * 32, 8 * 32 : 9 * 32]
        elif char == "F": # fruits
            return self.tiles[1 * 32 : 2 * 32, 4 * 32 : 5 * 32] 
        elif char == "S": # spices
            return self.tiles[1 * 32 : 2 * 32, 3 * 32 : 4 * 32]       
        elif char == "R": # dairy
            return self.tiles[8 * 32 : 9 * 32, 7 * 32 : 8 * 32] 
        elif char == "D": # drinks
            return self.tiles[6 * 32 : 7 * 32, 13 * 32 : 14 * 32] 
        elif char == "c": # customer/shopping cart
            return self.tiles[8 * 32 : 9 * 32, 6 * 32 : 7 * 32] 
        else:
            return self.tiles[32:64, 64:96]

    def prepare_map(self):
        """prepares the entire image as a big numpy array"""
        for y, row in enumerate(self.contents):
            for x, tile in enumerate(row):
                bm = self.get_tile(tile)
                self.image[
                    y * TILE_SIZE : (y + 1) * TILE_SIZE,
                    x * TILE_SIZE : (x + 1) * TILE_SIZE,
                ] = bm

    def draw(self, frame, offset=OFS):
        """
        draws the image into a frame
        offset pixels from the top left corner
        """
        frame[
            OFS : OFS + self.image.shape[0], OFS : OFS + self.image.shape[1]
        ] = self.image

    def write_image(self, filename):
        """writes the image into a file"""
        cv2.imwrite(filename, self.image)


if __name__ == "__main__":

    background = np.zeros((700, 1000, 3), np.uint8)
    tiles = cv2.imread("tiles_new.png") # the cv2.imread() function reads in the image as a NumPy array, so it can be sliced within the program.

    market = SupermarketMap(MARKET, tiles)
    customer_image = SupermarketMap(MARKET, tiles).get_tile('c')

    customer1 = Customer(1, 'drinks', matrix_monday, market, customer_image, 4, 5)
    customer2 = Customer(2, 'entry', matrix_monday, market, customer_image, 16, 11)
    #customer = Customer(market, customer_image, 4, 5)
    #Customer(terrain_map, image, x, y)

    while True:
        frame = background.copy()
        market.draw(frame)
        
        #customer1.draw(frame)
        #customer2.draw(frame)
        
        customer1.move('down',frame)
        customer2.move('up',frame)
        time.sleep(1)
        cv2.imshow("frame", frame) # the cv2.imshow() method is what’s actually displaying each frame on the screen

        key = chr(cv2.waitKey(1) & 0xFF)
        if key == "q":
            break

    cv2.destroyAllWindows()
    
    market.write_image("supermarket.png")