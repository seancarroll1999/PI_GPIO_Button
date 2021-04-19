import RPi.GPIO as GPIO 
import time
import threading

#Initialise GPIO pins for button control 
buttonPin = 17
ledPin = 27

#GPIO settings
GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM)

#Sets the buttonPon as an input with inital vel set to UP
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  

#Sets the ledPin as an output
GPIO.setup(ledPin,GPIO.OUT)

#Turns the LED off on start
GPIO.output(ledPin,GPIO.LOW)

#Variable which times how long button is pressed for
pressTime = time.time()

#Thread variables to control
thread = "over"
pill2kill = ""

#Speed value for LED blink
speed = 0.5

#Handles the button event and determines whether the button press was short or long
def button_call(channel):
    global buttonPin

    #GPIO EventTrigger is removed to prevent the code from thinking a long press is multiple presses
    GPIO.remove_event_detect(buttonPin)
    
    #Inital time of button press
    pressTime = time.time()

    #While button is pressed (0) get new time for calculation
    while GPIO.input(buttonPin) == 0:
        newTime = time.time()

        #If the difference between the inital start time and current time is above 0.8 seconds then its a long press 
        if newTime - pressTime > 0.8:
            print("longPress")
            LongPress()

            #Hold long press in infinite loop until release 
            while GPIO.input(buttonPin) == 0:
                continue

            #Now long press is over re-attach the EventTrigger for future calls
            GPIO.add_event_detect(buttonPin, GPIO.FALLING, callback=button_call, bouncetime=300)
            return
    
    #If the differnece between the inital start time and current time is below 0.8 seconds then its a short press
    print("short press")
    ShortPress()

    #GPIO EventTigger must be re-enabled now the button process is complete for future calls
    GPIO.add_event_detect(buttonPin, GPIO.FALLING, callback=button_call, bouncetime=300)
    
#If blink is active then cancel blinking else just toggle the LED ON and OFF
def ShortPress():
    global speed
    if(thread != "over"):
        speed = 0.5
        EndBlink()
        return
    ToggleLed()

#If blink is not active then start the blink otherwise increase the blink speed by 0.2 speed
def LongPress():
    global speed
    if thread == "over":
        StartBlink(speed)
    else:
        speed = speed - 0.2
        EndBlink()
        StartBlink(speed)
    

#region BLINKING

#Blinking must start in its own thread to allow for while loop to continue
def StartBlink(speed):
    global pill2kill
    global thread
    pill2kill = threading.Event()
    thread = threading.Thread(target=Blink, args=(pill2kill, speed))
    thread.start()

#Sends the Pill2Kill value to the thread which stops the while loop and exists the blinking
def EndBlink():
    global pill2kill
    global thread
    global speed
    pill2kill.set()
    thread.join()
    thread = "over"
    LedOff()

#Blinking code which uses speed value to control blink
def Blink(pill, speed):
    while not pill.wait(speed):
        ToggleLed()
    print("stopping blink")
#endregion

#region LED CONTROL

#Toggles LED on and off 
def ToggleLed():
    global led
    if led:
        LedOff()  
    else:
        LedOn()

#Turns the button LED on
def LedOn():
    global led
    global ledPin
    GPIO.output(ledPin,GPIO.HIGH)
    led = True

#Turns the button LED off
def LedOff():
    global led
    global ledPin
    GPIO.output(ledPin,GPIO.LOW)
    led = False
#endregion

#Starts the thread which detects if the button is pressed
def StartButton():
    global led
    led = False
    GPIO.add_event_detect(buttonPin, GPIO.FALLING, callback=button_call, bouncetime=300)
    while True:
        continue