from microbit import *
import time
import random
import music

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

    global alive
    global score
    
    # define position
    snake_position = snake_list[-1].position
    head_position = [snake_position[0] + current_direction[0], snake_position[1] + current_direction[1]]

    if head_position[0] > 4 or head_position[0] < 0 or head_position[1] > 4 or head_position[1] < 0:
        alive = False
        return
    
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
            alive = False
        else:
            music.play(music.JUMP_UP, wait=False)
            has_apple = True
            score += 1
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



def game():
    
    global snake_list
    global alive
    global canvas
    global score
    global direction 
    global index_direction

    
    snake_list = []
    direction = ([0, 1], [-1, 0], [0, -1], [1, 0])
    index_direction = 3

    canvas = Canvas()

    SnakeBody.create_body(2)
    spawn_apple()


    
    time_passed = running_time()
    LATENCY = 0.2
    index_instance = index_direction
    current_direction = direction[index_direction]
    alive = True
    score = 0

    light_render(canvas)
    play_wait_sound = False

    music.play(music.POWER_UP, wait=False)
    # wait until button "a" or "b" is pressed
    screen_on = True
    while not (button_a.is_pressed() or button_b.is_pressed()):
        if (running_time() - time_passed) > 0.1 * 60**2:
            screen_on = not screen_on
            if not screen_on:
                for snake in snake_list:
                    display.set_pixel(snake.x, snake.y, 0)
            else:
                if play_wait_sound:
                    music.pitch(random.randint(300, 500), 1, wait=False)
                for snake in snake_list:
                    display.set_pixel(snake.x, snake.y, snake.value)
            time_passed = running_time()

        if running_time() > 0.5 * 60**2:
            play_wait_sound = True
        

    has_button_been_pressed = True
    
    while alive:
        

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
            pitch = random.randint(280, 300)
            for i in range(25):
                music.pitch(pitch + i * 100, 1, wait=False)
            move(current_direction)
            time_passed = running_time()
            index_direction = direction.index(current_direction)
        
        light_render(canvas)

    # UNUSED
    death_tune = ["C3", "B", "G#", "G", "G#:10"]


    for i in range(10):
        for snake in snake_list:
            display.set_pixel(snake.x, snake.y, 0)
    
        time.sleep(0.2 - i *0.05)
        for snake in snake_list:
            display.set_pixel(snake.x, snake.y, max(5 - i, 0))
        music.pitch(700 - i * 100, 100)
        time.sleep(0.2- i *0.05)




    display.show(str(score)[0])
    for i in range(5):
        display.off()
        time.sleep(0.05 + i *0.02)
        music.pitch(400 + i * 150, 100)
        display.on()

        if i > 1:
            display.show(str(score)[-1])
    
        time.sleep(0.05 - i *0.01)


    display.scroll(str(score), delay=125)

    display.clear()
    game()



# menu
select = [
    "Solo",
    "Multi",
    "Music"
]

has_button_been_pressed = False
menu_index = 0
wait_time = len(select[menu_index]) * 0.2
time_passed = running_time() - 1.1 * 60**2

music.set_tempo(bpm=150)

while True:
    # USER INPUT
    if not has_button_been_pressed:
        
        if button_a.is_pressed():
            has_button_been_pressed = True
            music.play(music.JUMP_UP, wait=False)
            menu_index += 1
            if menu_index == len(select):
                menu_index = 0
            time_passed -= wait_time * 60 **2
            wait_time = len(select[menu_index]) * 0.2
            
        
        elif button_b.is_pressed():
            break
    
    elif (not button_a.is_pressed()) and (not button_b.is_pressed()):
       has_button_been_pressed = False
    
    if (running_time() - time_passed) > wait_time * 60**2: 
        time_passed = running_time()
        display.scroll(select[menu_index], wait=False, delay=100)

music.reset()
display.scroll("", delay=1)
game()
