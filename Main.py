from microbit import *
import time
import random
import music
import os
import radio

ROUND = 3

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

def get_render_string():
    string_render = "R"
    for x in range(5):
        for y in range(5):
            string_render += str(display.get_pixel(x, y))
    return string_render


def send_multiplayer_update(is_multiplayer : bool):
    if is_multiplayer:
        radio.send(get_render_string())

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
    
    # defines position => takes last snake object
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
            tail_position = snake_list[0].position
            if tail_position != head_position:
                alive = False
        else:
            if is_music:
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



def game(multiplayer=False):

    global snake_list
    global alive
    global canvas
    global score
    global total_score
    global direction 
    global index_direction

    music.reset()
    display.scroll("", delay=1)
    
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

    has_button_been_pressed = True

    light_render(canvas)
    play_wait_sound = False
    if is_music:
        music.play(music.POWER_UP, wait=False)
    # wait until button "a" or "b" is pressed
    screen_on = True
    while not (button_a.is_pressed()):
        if (running_time() - time_passed) > 0.1 * 60**2:
            screen_on = not screen_on
            if not screen_on:
                for snake in snake_list:
                    display.set_pixel(snake.x, snake.y, 0)
                send_multiplayer_update(multiplayer)
            else:
                if play_wait_sound and is_music:
                    music.pitch(random.randint(300, 500), 1, wait=False)
                for snake in snake_list:
                    display.set_pixel(snake.x, snake.y, snake.value)
                send_multiplayer_update(multiplayer)
            time_passed = running_time()

        if button_b.is_pressed() and not has_button_been_pressed:
            return
        if (not button_b.is_pressed()) and (not button_a.is_pressed()):
            has_button_been_pressed = False
        
        if running_time() > 0.5 * 60**2:
            play_wait_sound = True

    
    del screen_on
    del play_wait_sound
    
    has_button_been_pressed = True
    
    
    while alive:
        
        # USER INPUT
        if not has_button_been_pressed:
            
            if button_a.is_pressed():
                print("changed direction")
                has_button_been_pressed = True
                current_direction = get_direction(-1)
            elif button_b.is_pressed():
                has_button_been_pressed = True
                current_direction = get_direction(1)
        elif (not button_a.is_pressed()) and (not button_b.is_pressed()):
            has_button_been_pressed = False

    
        if (running_time() - time_passed) >= (LATENCY * 60**2):
            if is_music:
                pitch = random.randint(280, 300)
                for i in range(25):
                    music.pitch(pitch + i * 100, 1, wait=False)
            move(current_direction)
            time_passed = running_time()
            index_direction = direction.index(current_direction)
            
        light_render(canvas)
        # stream the screen
        send_multiplayer_update(multiplayer)

    # UNUSED
    death_tune = ["C3", "B", "G#", "G", "G#:10"]


    for i in range(10):
        for snake in snake_list:
            display.set_pixel(snake.x, snake.y, 0)
        send_multiplayer_update(multiplayer)
        time.sleep(0.2 - i *0.05)
        for snake in snake_list:
            display.set_pixel(snake.x, snake.y, max(5 - i, 0))
        send_multiplayer_update(multiplayer)
        if is_music:
            music.pitch(700 - i * 100, 100)
        time.sleep(0.2- i *0.05)


    display.show(str(score)[0])
    for i in range(5):
        display.off()
        send_multiplayer_update(multiplayer)
        time.sleep(0.05 + i *0.02)
        if is_music:
            music.pitch(400 + i * 150, 100)
        display.on()
        send_multiplayer_update(multiplayer)
        if i > 1:
            display.show(str(score)[-1])
    
        time.sleep(0.05 - i *0.01)


    display.scroll(str(score), delay=125, wait=False)
    
    time_passed = running_time()
    while (running_time() - time_passed) < 0.5 * 60 ** 2:
        send_multiplayer_update(multiplayer)
    display.clear()

    if multiplayer:
        total_score += score
    else:
        game()

def sound_settings():
    global is_music
    is_music = not is_music
    if is_music:
        music.play(music.RINGTONE)
    else:
        music.play(music.JUMP_DOWN)

def get_session_id():
    current_time = running_time()
    id = 0
    for i in str(current_time):
        id += int(i)
    return str(id)[-1]

def round_ended(is_host=True):
    if is_host:
        type = "GUEST"
    else:
        type = "HOST"
    time_passed = running_time()
    while (radio.receive() != "GOT_END_ROUND") and (running_time() - time_passed) < 0.2 * 60 ** 2:
            radio.send(type + "_END_ROUND")
    print("info send succesfully, now beginning as a viewer")

def send_update_for(time : float):
    time_passed = running_time()
    while (running_time() - time_passed) < time * 60 ** 2:
        send_multiplayer_update(True)

def multiplayer():

    global is_host
    global total_score

    is_host = False
    
    display.scroll("", delay=1)
    #display.scroll("waiting for opponent", loop=True)
    radio.on()

    time_passed = running_time()
    found_status = False
    id = "0"
    target_id = ""
    print("Looking...")
    
    while True:
        if (running_time() - time_passed) > 0.3 * 60**2:
            if found_status:
                break
            else:
                
                time_passed = running_time()
                id = get_session_id()
                print("New id :", id)
            
        radio.send(id)
        information = radio.receive()
        
        if not information is None:
            if id != information and (not found_status):
                print(str(id), ": ID, INFO : ", str(information))
                found_status = True
                target_id = information
                time_passed = running_time()

    print("Found status")
    if int(id) > int(target_id):
        # HOST
        print("HOST")

        total_score = 0
        
        is_host = True
        phase = 0
        for r in range(ROUND):
            phase += 1
            print("phase :", phase)
            game(multiplayer=True)
            # after ended change config
            print("round ended now sending info")
            round_ended(True)
            phase += 1
            print("phase :", phase)
            viewer()
        print("HOST : MATCH FINISHED")
        display.clear()
        opponent_score = 0
        print("Waiting for Guest to send his total score")
        #display.scroll("Waiting for the guest to send info...", wait=False)
        while True:
            radio_out = radio.receive()
            if not radio_out is None:
                if radio_out.isdigit():
                    opponent_score = int(radio_out)
                    break
        print("Score Received !")
        print("showing results")
        if total_score == opponent_score:
            if is_music:
                music.play(music.DADADADUM)
            display.scroll("Tie no one won, both have " + radio_out + "pts", wait=False, delay=105)
            send_update_for(2.5)
        
        elif total_score > opponent_score:
            if is_music:
                music.play(music.RINGTONE, wait=False)
            # HOST WINS (PLAYER 1)
            display.scroll("Player 1 wins with " + str(total_score) + "pts", wait=False, delay=105)
            send_update_for(3.5)
            display.scroll("Player 2 :" + radio_out, wait=False, delay=105)
            send_update_for(2.8)
            display.scroll("Difference : " + str(total_score - opponent_score), wait=False, delay=105)
            send_update_for(2.5)
        else:
            if is_music:
                music.play(music.FUNERAL, wait=False)
            # GUEST WINS (PLAYER 2)
            display.scroll("Player 2 wins with " + str(opponent_score) + "pts", wait=False, delay=105)
            send_update_for(3.5)
            display.scroll("Player 1 :" + str(total_score), wait=False, delay=75)
            send_update_for(3.5)
            display.scroll("Difference : " + str(opponent_score - total_score), wait=False, delay=105)
            send_update_for(3.5)
        round_ended()
    else:
        phase = 0
        print("Guest")
        # GUEST
        total_score = 0
        for r in range(ROUND):
            phase += 1
            print("phase :", phase)
            viewer()
            phase += 1
            print("phase :", phase)
            game(multiplayer=True)
            # after ended change config
            print("round ended now sending info")
            time_passed = running_time()
            round_ended(False)

        print("GUEST : MATCH FINISHED")
        time_passed = running_time()
        print("Sending Score")
        while (running_time() - time_passed) < 0.2 * 60**2:
            radio.send(str(total_score))
        print("Entering viewer mode to show result")
        viewer()
            
def viewer():

    message = ""
    
    if is_host:
        message = "HOST_END_ROUND"
    else:
        message = "GUEST_END_ROUND"
        
    while True:
        screen = radio.receive()
        if not screen is None:
            if screen.startswith("R"):
                light_value_index = 1
                for x in range(5):
                    for y in range(5):
                        light_value = screen[light_value_index]
                        display.set_pixel(x, y, int(light_value))
                        light_value_index += 1
            elif screen == message:
                print(screen, ", HOST? =", is_host)
                print("received end of the round")
                # say you have received the message
                time_passed = running_time()
                print("sendding that got the end")
                while (running_time() - time_passed) < (0.3 * 60 ** 2):
                    radio.send("GOT_END_ROUND")
                print("start as player now")
                return

# menu
def menu():

    global is_music
    
    select = [
        "Solo",
        "Multi",
        "Music"
        
    ]
    function_select = {
        0 : game,
        1 : multiplayer,
        2 : sound_settings
    }

    is_music = False
    
    has_button_been_pressed = False
    menu_index = 0
    wait_time = len(select[menu_index]) * 0.2
    time_passed = running_time() - 1.1 * 60**2

    music.set_tempo(bpm=180)
    print(os.listdir())

    
    
    while True:
        radio.off()
        # USER INPUT
        if not has_button_been_pressed:
            
            if button_a.is_pressed():
                
                has_button_been_pressed = True
                if is_music:
                    music.play(music.JUMP_UP, wait=False)
                menu_index += 1
                if menu_index == len(select):
                    menu_index = 0
                time_passed -= wait_time * 60 **2
                wait_time = len(select[menu_index]) * 0.2
                
            
            elif button_b.is_pressed():
                has_button_been_pressed = True
                function_select[menu_index]()
                music.set_tempo(bpm=150)
                
        
        elif (not button_a.is_pressed()) and (not button_b.is_pressed()):
           has_button_been_pressed = False
        
        if (running_time() - time_passed) > wait_time * 60**2: 
            time_passed = running_time()
            display.scroll(select[menu_index], wait=False, delay=100)
        

menu()
