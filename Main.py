from microbit import *
import time
import random

class Canvas:
    __slot__ = "render_dict"
    def __init__(self):
        self.render_dict = {}
    

class Sprite:

    __slot__ = "position", "value", "canvas_owner", "x", "y"
    
    def __init__(self, canvas_owner, position : list, value : int):
        self.position = position
        self.value = value
        self.canvas_owner = canvas_owner
        position_cache = canvas_owner.render_dict.setdefault(tuple(position), [])
        position_cache.append(self)
        self.x = self.position[0]
        self.y = self.position[1]

    

    def set_position(self, new_position : list):
        tuple_position = tuple(self.position)
        render_dict = self.canvas_owner.render_dict

        
        render_dict[tuple_position].remove(self)
        if render_dict[tuple_position] == []:
            # if nothing else to render remove key
            del render_dict[tuple_position]
        
        tuple_position = tuple(new_position)
        self.position = new_position
        # add new position
        position_cache = render_dict.setdefault(tuple_position, [])
        position_cache.append(self)


    def kill(self):
        render_position_list = self.canvas_owner.render_dict[(self.x, self.y)]
        render_position_list.remove(self)
        if render_position_list == []:
            del self.canvas_owner.render_dict[(self.x, self.y)]

        del self


def light_render(canvas : Canvas):
    render_dict = canvas.render_dict
    for x in range(5):
        for y in range(5):
            if (x, y) in render_dict:
                # update screen
                # get the ref of the sprite rendered at x, y
                sprite_rendered = render_dict[(x, y)][0]
                light_value = sprite_rendered.value
                display.set_pixel(x, y, light_value)

            # if led is supposed to be off but isn't put it off
            elif display.get_pixel(x, y) != 0:
                display.set_pixel(x, y, 0)

### CODE ###

snake_list = []
direction = ([0, 1], [-1, 0], [0, -1], [1, 0])
index_direction = 3

canvas = Canvas()


class SnakeBody(Sprite):

    __slot__ = "canvas_owner", "position", "value", "x", "y"
    
    def __init__(self, canvas_owner : Canvas, position : list):
        super().__init__(canvas_owner, position, 3)
        snake_list.append(self)

    def kill(self):
        super().kill()
        snake_list.remove(self)

    @staticmethod
    def create_body(length : int):
        for i in range(length):
            head = SnakeBody(canvas, [1 + i, 2])
            head.value = 7

def get_direction(value : int):
    global index_direction
    
    instance_direction = index_direction + value
    if instance_direction > 3:
        instance_direction = 0
    elif instance_direction < 0:
       instance_direction = 3 
    return direction[instance_direction]
    
def move(current_direction : list):

    # define position
    snake_position = snake_list[-1].position
    head_position = [snake_position[0] + current_direction[0], snake_position[1] + current_direction[1]]
    
    # change the color of the old head
    old_head = snake_list[-1]
    old_head.value = 3

    # add head in the direction you are going
    head = SnakeBody(canvas, head_position)
    head.value = 7

    has_apple = False
    
    if len(canvas.render_dict[tuple(head_position)]) > 1:
        # check if snake or apple
        render_list = canvas.render_dict[tuple(head_position)].copy()
        render_list.remove(head)
        object = render_list[0]
        if isinstance(object, SnakeBody):
            pass
        else:
            has_apple = True
            object.kill()
            spawn_apple()
        
    if not has_apple:
        # delete tail
        tail = snake_list[0]
        tail.kill()

def spawn_apple():
    possible_positions = []
    for x in range(5):
        for y in range(5):
            if not (x, y) in canvas.render_dict:
                possible_positions.append([x, y])

    random_position = random.choice(possible_positions)
    apple = Sprite(canvas, random_position, 9)

SnakeBody.create_body(2)
spawn_apple()

#while not (button_a.is_pressed() or button_b.is_pressed()):
    #pass
    # wait until button "a" or "b" is pressed


has_button_been_pressed = False
time_passed = running_time()
LATENCY = 0.25
index_instance = index_direction
current_direction = direction[index_direction]



while True:

    # USER INPUT
    if not has_button_been_pressed:
        
        if button_a.is_pressed():
            has_button_been_pressed = True
            current_direction = get_direction(-1)
        elif button_b.is_pressed():
            has_button_been_pressed = True
            current_direction = get_direction(1)
    elif not (button_a.is_pressed() and button_b.is_pressed()):
        has_button_been_pressed = False

    
    if (running_time() - time_passed) >= (LATENCY * 60**2):
        move(current_direction)
        time_passed = running_time()
        index_direction = direction.index(current_direction)
        
    
    light_render(canvas)


