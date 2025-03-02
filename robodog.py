from picarx import Picarx
import random
import threading
from queue import Queue
import time
from time import sleep
from robot_hat import Music,TTS
import readchar
from os import geteuid
from vilib import Vilib
# import vosk
import pyaudio
import json

# Global vars
POWER = 0

class Robodog:
    def __init__(self):
        """Plays starting music and initializes attributes."""
        print("initializing")
        # Field variables for detection
        self.current_state = "NOTHING"  # EXPLORING, LOCKED_ON, AVOIDING
        self.target_obj = None  # Object to find
        self.target_obj_position = None # Where the target is in the FOV: [x, y, width, height]
        self.thirds = {
            'left': (0, 213),
            'center': (213, 426),
            'right': (426, 640)
        }
        self.object_found = False
        # Field variables for movement
        global POWER
        self.px = Picarx()

        # Field variables for music
        ## Ensure sudo is being run
        if geteuid() != 0:
          print(f"\033[0;33m{'The program needs to be run using sudo, otherwise there may be no sound.'}\033[0m")
        ## Default values
        self.music = Music()
        self.default_volume = 30
        self.music.music_set_volume(30)
        self.tts = TTS()
        ## Starting music
        ##music.music_play('mariostart.mp3')

        # Field variables for vilib

        # Initialize camera
        Vilib.camera_start(vflip=False, hflip=False)
        Vilib.show_fps()
        Vilib.display(local=True, web=True)
        sleep(1)

        # Enable object detection
        Vilib.object_detect_switch(True)

        # Field variables for threads
        # Queues for threads
        self.detection_queue = Queue()
        self.audio_queue = Queue()

        # Threads running
        self.running = True

        # Initialize threads
        self.threads = {
            "vision": threading.Thread(target=self.vision_thread),
            "movement": threading.Thread(target=self.movement_thread),
            "audio": threading.Thread(target=self.audio_thread),
            "state_manager": threading.Thread(target=self.state_thread),
        }

    def run_dog(self):
        """Run the dog to find the object you request."""
        # Loop until done
        while not (self.object_found):
            # Explore until target in sights
            while not (self.target_obj_position):
                self.explore()
            # Lock-in until found or lose sight:
            while(self.target_obj_position):
                self.locked_on()

    def explore(self):
        """Logic for random exploration, checking for target object."""
        # Movement logic (Nick)
        SafeDistance = 40   # > 40 safe
        DangerDistance = 20 # > 20 && < 40 turn around,
                    # < 20 backward
        try:
            #px = Picarx()
            # px = Picarx(ultrasonic_pins=['D2','D3']) # tring, echo

            forward_time = 4

            random_direction = random.randint(-30, 30)

            self.px.set_dir_servo_angle(random_direction)

            self.px.forward(POWER)
            x = 0
            while x < forward_time:
                distance = round(self.px.ultrasonic.read(), 2)
                print("distance: ",distance)


                time.sleep(1)
                if distance < 20 and distance > 0:
                    self.px.set_dir_servo_angle(-30)
                    self.px.backward(POWER)
                    time.sleep(1)

                elif distance > 40:
                    self.px.set_dir_servo_angle(random_direction)
                    self.px.forward(POWER)

                elif distance >= DangerDistance:
                    if random_direction > 0:
                        self.px.set_dir_servo_angle(random_direction - 30)
                    else:
                        self.px.set_dir_servo_angle(random_direction + 30)
                    self.px.forward(POWER)
                    time.sleep(0.1)

                x += 1
            self.px.backward(POWER)
            time.sleep(2)
    

        finally:
            self.px.forward(0)

            # Music (Hannah)
            # play_bgm_music(True, 40)

    def lock_on(self):
        """Logic for locked-on movement."""
        print("TARGET IDENTIFIED. GATHERING INFORMATION FOR FIRST RESPONDERS")
        self.get_user_responses()
    
    def get_user_responses(self):
        self.music.music_set_volume(100)
        self.tts.say("Person located.")
        time.sleep(2)
        
        self.music.music_set_volume(50)
        self.tts.say("Help is on the way!")
        
        
        """
        Listens to user's responses for key safety questions.

        Returns:
            responses (dict): A dictionary containing the user's responses.
        """
        """
        model = vosk.Model("vosk-model/vosk-model-small-en-us-0.15")
        recognizer = vosk.KaldiRecognizer(model, 16000)
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
        stream.start_stream()

        questions = [
            "What is your name?",
            "Are there other people in the  building with you?",
            "Do you need help?",
            "Are you in danger?"
        ]

        responses = {}

        try:
            for question in questions:
                tts.say(question)
                while True:
                    data = stream.read(4096)
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        recognized_text = result["text"].strip()
                        if recognized_text:
                            tts.say(f"Did you say '{recognized_text}'? Please confirm with 'yes' or 'no'.")

                            while True:
                                data = stream.read(4096)
                                if recognizer.AcceptWaveform(data):
                                    confirmation = json.loads(recognizer.Result())["text"].strip().lower()

                                    if confirmation == "yes":
                                        responses[question] = recognized_text
                                        break
                                    elif confirmation == "no":
                                        tts.say("Let's try again.")
                                        break
            print("QUESTION: ANSWER")
            for i in range(len(recognized_text.upper)):
                print(f"{question[i].upper()}: {recognized_text[i].upper()}")

        except KeyboardInterrupt:
            print("\n?? Stopped recording.")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

        return responses
    """
        
    '''
        # Movement logic
        self.px.forward(POWER)

        if self.detect_obj() == "RIGHT":
            self.px.set_dir_servo_angle(-10)
        elif self.detect_obj() == "LEFT":
            self.px.set_dir_servo_angle(10)
        else:
            self.px.set_dir_servo_angle(0)
        time.sleep(0.5)
    '''

    def obstacle_evasion(self):
        """Called when an obstacle is encountered."""
        # Movement logic (Nick)

        # Music (Hannah)
        pass

    def set_target_obj(self, obj):
        """Listens to userâ€™s request to set target object."""
        # Listen for request (Hannah)

        # Set field (Hannah)
        pass

    def detect_obj(self):
        """Detects where the object is in the FOV."""
        if self.target_obj_position is None:
            return None

        x = self.target_obj_position[0]
        if x < self.target_obj_position[0]:
            return "LEFT"
        elif x > self.target_obj_position[1]:
            return "RIGHT"
        else: 
            return "CENTER"



    def found_object(self):
        """Play a jingle when the object is found."""
        # play_bgm_music(False)
        # object_spotted_music = music.sound_play('metal_gear_exclamation_sound.mp3')

    def play_music(self, music_file, volume=None):
        """
        Play music that depends on the state of robodog.

        Args:
            music_file (string): music file to play
            volume (int): level of sound to play music

        Returns:
            None
        """
        # Default volume
        if volume == None:
            volume = 30

        # volume of bgm
        self.music.music_set_volume(volume)
        # bgm music
        self.music.music_play(music_file)



    def start(self):
        """Start all threads"""
        self.running = True
        for thread in self.threads.values():
            thread.start()
        

    def stop(self):
        """Stop all threads"""
        self.running = False
        for thread in self.threads.values():
            thread.join()

    def vision_thread(self):
        """Handles camera and object detection"""
        while self.running:
            try:
                # Get detection results
                detections = Vilib.object_detection_list_parameter
                
                # Debug print to see what we're getting
                #print("Raw detections:", detections)


                # Update target position if we see target object
                if detections:  # If we detected any objects
                    for detection in detections:
                        # [object_name, confidence, x, y, width, height]
                        if detection["class_name"] == self.target_obj:
                            if detection["score"] >= 0.60:
                                self.target_obj_position = detection["bounding_box"]  # x,y,width,height
                                # Put detection in queue
                                self.detection_queue.put(detection)
                                print("FOUND A HUMAN. GATHERING DATA.")
                                print(f"COORDINATES IN MY FIELD OF VIEW: {self.target_obj_position}")
                            break # stop the for loop early
                else:  # If no detections at all
                    self.target_obj_position = None

                time.sleep(0.5)

            except Exception as e:
                print({e})
                time.sleep(1)

    def movement_thread(self):
        """Handles motor control and movement"""
        while self.running:
            if self.current_state == "EXPLORING":
                self.explore()
            elif self.current_state == "LOCKED_ON":
                self.lock_on()
            time.sleep(0.02)

    def audio_thread(self):
        """Handles sound effects and music"""
        while self.running:
            #print("Audio thread running")
            if not self.audio_queue.empty():
                sound = self.audio_queue.get()
                self.play_music(sound)
            time.sleep(0.1)

    def state_thread(self):
        """Manages robot state and decision making"""
        global POWER
        while self.running:
            # State changes to explore for the first time
            if not self.current_state in ["EXPLORING", "LOCKED_ON", "FOUND"]:
            # Add starting up music to queue
                self.audio_queue.put('mariostart.mp3')
                time.sleep(4.5)
                self.audio_queue.put('carefree.mp3')
                print("Starting Exploring!")
                POWER = 40
                self.current_state = "EXPLORING"

            # State changes to explore from locked_on
            if (self.current_state == "LOCKED_ON") and (self.target_obj_position is None):
                POWER = 40
                # Add bgm to queue
                #self.audio_queue.pop(0)
                self.music.music_stop()

                self.audio_queue.put('carefree.mp3')
                self.current_state = "EXPLORING"

            # State changes to locked on
            if (self.current_state == "EXPLORING") and (self.target_obj_position is not None):
                # Stop playing BGM
                #self.audio_queue.pop(0)
                POWER = 0
                self.music.music_stop()
                # Add Alert to the queues
                self.audio_queue.put('metal_gear_exclamation_sound.mp3')
                time.sleep(1)
                # Add approaching music to queue

                # Change state field
                self.current_state = "LOCKED_ON"
                #self.audio_queue.put("shark_theme.mp3")

            # State changes to found
            if self.object_found:
                self.current_state = "FOUND"

            time.sleep(0.1)


  

if __name__ == "__main__":
    print("hello")
    try:
        print("Creating the dog")
        # Create robodog object/instance
        dog = Robodog()
        
        # Set what object to look for
        dog.target_obj = "person"
        
        # Start all threads
        dog.start()
        
        # Keep main thread alive and print detections
        while dog.running:
            if not dog.detection_queue.empty():
                print(f"Detected: {dog.detection_queue.get()}")
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        dog.stop()
        Vilib.camera_close()
