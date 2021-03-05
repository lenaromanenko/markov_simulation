import pandas as pd
import numpy as np
import cv2

matrix_monday = pd.read_csv('../data/mm_monday.csv', index_col = 0).T
matrix_monday = np.array(matrix_monday)

TILE_SIZE = 32
OFS = 50

MARKET = """
##################
##...............#
##..DE..ES..SA..A#
##..DE..ES..SA..A#
##..DE..ES..SA..A#
##..DE..ES..SA..A#
##..DE..ES..SA..A#
##...............#
##..CC..CC..CC...#
##...............#
##...............#
##############GG##
""".strip()

class Customer:
    
    #def __init__(self, idn, state, transition_mat, terrain_map, image, x, y):
    def __init__(self,terrain_map, image, x, y):
        #self.id = idn
        #self.state = state
        #self.transition_mat = transition_mat

        self.terrain_map = terrain_map
        self.image = image
        self.x = x
        self.y = y

        #self.tr_array_dict = {
        #'dairy' : self.transition_mat[0,:],
        #'drinks' : self.transition_mat[1,:],
        #'entry' : self.transition_mat[2,:],
        #'fruit' : self.transition_mat[3,:],
        #'spices' : self.transition_mat[4,:]
        #}

    def __repr__(self):
        """
        Returns a csv string for that customer.
        """
        #return f'{self.id};{self.state}'
        return f'{self.x};{self.y}'

    def draw(self, frame):
        xpos = OFS + self.x * TILE_SIZE
        ypos = OFS + self.y * TILE_SIZE # Pavel: not too sure about this
        #frame[ypos:ypos+32, xpos:xpos+32] = self.image # Pavel: absolutely not sure about this
        frame[ypos-32:ypos, xpos-32:xpos] = self.image # Pavel: absolutely not sure about this
        #frame[ypos:ypos, xpos:xpos] = self.image # Pavel: absolutely not sure about this
        # overlay the Customer image / sprite onto the frame

    #def is_active(self):
    #    """
    #    Returns True if the customer has not reached the checkout
    #    for the second time yet, False otherwise.
    #    """
    #    if self.state != 'checkout':
    #         return True 
    #    if self.state == 'checkout':
    #        return False 

    #def next_state(self):
    #    """
    #    Propagates the customer to the next state
    #    using a weighted random choice from the transition probabilities
    #    conditional on the current state.
    #    Returns nothing.
    #    """
    #  
    #    self.state = np.random.choice(['checkout', 'dairy', 'drinks', 'fruit', 'spices'], p=self.tr_array_dict[f'{self.state}'])

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
            return self.tiles[7 * 32 : 8 * 32, 3 * 32 : 4 * 32] # 7th row, 3rd column
        elif char == "C": # checkout
            return self.tiles[2 * 32 : 3 * 32, 8 * 32 : 9 * 32]
        elif char == "A": # apple --> fruits
            return self.tiles[1 * 32 : 2 * 32, 4 * 32 : 5 * 32] 
        elif char == "B": # banana
            return self.tiles[0 * 32 : 1 * 32, 4 * 32 : 5 * 32] 
        elif char == "S": # spices
            return self.tiles[1 * 32 : 2 * 32, 3 * 32 : 4 * 32] 
        elif char == "E": # eggs --> dairy
            return self.tiles[7 * 32 : 8 * 32, 11 * 32 : 12 * 32] 
        elif char == "D": # drinks
            return self.tiles[6 * 32 : 7 * 32, 13 * 32 : 14 * 32] 
        elif char == "c": # consumers
            return self.tiles[3 * 32 : 4 * 32, 0 * 32 : 1 * 32] 
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
    tiles = cv2.imread("tiles.png") # the cv2.imread() function reads in the image as a NumPy array, so it can be sliced within the program.

    market = SupermarketMap(MARKET, tiles)
    customer_image = SupermarketMap(MARKET, tiles).get_tile('c')

    #customer = Customer(1, 'entry', matrix_monday, market, customer_image, 16, 2)
    customer = Customer(market, customer_image, 4, 5)
    #Customer(terrain_map, image, x, y)

    while True:
        frame = background.copy()
        market.draw(frame)
        
        customer.draw(frame)

        cv2.imshow("frame", frame) # the cv2.imshow() method is what’s actually displaying each frame on the screen

        key = chr(cv2.waitKey(1) & 0xFF)
        if key == "q":
            break

    cv2.destroyAllWindows()
    
    market.write_image("supermarket.png")