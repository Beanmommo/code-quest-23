import random

import comms
from object_types import ObjectTypes
import sys
import math

class Game:
    """
    Stores all information about the game and manages the communication cycle.
    Available attributes after initialization will be:
    - tank_id: your tank id
    - objects: a dict of all objects on the map like {object-id: object-dict}.
    - width: the width of the map as a floating point number.
    - height: the height of the map as a floating point number.
    - current_turn_message: a copy of the message received this turn. It will be updated everytime `read_next_turn_data`
        is called and will be available to be used in `respond_to_turn` if needed.
    """

    
    def __init__(self):
        tank_id_message: dict = comms.read_message()
        self.last_path_req = None

        self.tank_id = tank_id_message["message"]["your-tank-id"]
        self.enemy_tank_id = tank_id_message["message"]["enemy-tank-id"]

        self.current_turn_message = None

        # We will store all game objects here
        self.objects = {}

        #Initialise static values
        self.UPDATED_OBJECTS = "updated_objects"
        self.DELETED_OBJECTS = "deleted_objects"
        self.MESSAGE = "message"

        next_init_message = comms.read_message()
        while next_init_message != comms.END_INIT_SIGNAL:
            # At this stage, there won't be any "events" in the message. So we only care about the object_info.
            object_info: dict = next_init_message["message"]["updated_objects"]

            # Store them in the objects dict
            self.objects.update(object_info)

            # Read the next message
            next_init_message = comms.read_message()

        # We are outside the loop, which means we must've received the END_INIT signal

        # Let's figure out the map size based on the given boundaries

        # Read all the objects and find the boundary objects
        boundaries = []
        for game_object in self.objects.values():
            if game_object["type"] == ObjectTypes.BOUNDARY.value:
                boundaries.append(game_object)

        # The biggest X and the biggest Y among all Xs and Ys of boundaries must be the top right corner of the map.

        # Let's find them. This might seem complicated, but you will learn about its details in the tech workshop.
        biggest_x, biggest_y = [
            max([max(map(lambda single_position: single_position[i], boundary["position"])) for boundary in boundaries])
            for i in range(2)
        ]

        self.width = biggest_x
        self.height = biggest_y

    def read_next_turn_data(self):
        """
        It's our turn! Read what the game has sent us and update the game info.
        :returns True if the game continues, False if the end game signal is received and the bot should be terminated
        """
        # Read and save the message
        self.current_turn_message = comms.read_message()

        if self.current_turn_message == comms.END_SIGNAL:
            return False

        # Delete the objects that have been deleted
        # NOTE: You might want to do some additional logic here. For example check if a powerup you were moving towards
        # is already deleted, etc.
        for deleted_object_id in self.current_turn_message["message"]["deleted_objects"]:
            try:
                del self.objects[deleted_object_id]
            except KeyError:
                pass

        # Update your records of the new and updated objects in the game
        # NOTE: you might want to do some additional logic here. For example check if a new bullet has been shot or a
        # new powerup is now spawned, etc.
        self.objects.update(self.current_turn_message["message"]["updated_objects"])

        return True
    
    def calculate_angle(self, x1, y1, x2, y2):
        """
        Courtesy of ChatGPT
        """
        delta_x = x2 - x1
        delta_y = y2 - y1
        theta_radians = math.atan2(delta_y, delta_x)
        angle_degrees = math.degrees(theta_radians)
        if angle_degrees < 0:
            return 360 + angle_degrees
        return angle_degrees

    def calculate_distance(x1, y1, x2, y2):
        """
        Courtesy of ChatGPT
        """
        delta_x = x2 - x1
        delta_y = y2 - y1
        distance = math.sqrt(delta_x2 + delta_y2)
        return distance
    

    def respond_to_turn(self):
        """
        This is where you should write your bot code to process the data and respond to the game.
        """

        # Write your code here... For demonstration, this bot just shoots randomly every turn.

        #get game message
        post_message = {}
        enemy_tank_coord = self.objects[self.enemy_tank_id]["position"]
        our_tank_coord = self.objects[self.tank_id]["position"]
        #Find shoot angle
        shoot_angle = self.calculate_angle(our_tank_coord[0], our_tank_coord[1], enemy_tank_coord[0], enemy_tank_coord[1])
        post_message["shoot"] = shoot_angle
        
        # print(updated_object_message, file=sys.stderr)
        # print("Start of test-------------------------------", file=sys.stderr)
        # print("END of test-------------------------------", file=sys.stderr)

        #Shoot 
        
        if self.last_path_req is None or self.last_path_req != enemy_tank_coord:
            post_message["path"] = enemy_tank_coord
        
        comms.post_message(post_message)
    
        


