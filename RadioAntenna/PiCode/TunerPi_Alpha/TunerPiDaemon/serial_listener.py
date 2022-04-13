import serial
from asyncio.tasks import wait

ser = serial.Serial('/dev/pts/9', 9600, rtscts=True,dsrdtr=True)
bytes_carraigereturn = bytes("\r", "UTF8")
bytes_linefeed = bytes("\n", "UTF8")

try:
    command = ""
    while True:
        byte_next = ser.read()
        char_next = byte_next.decode("utf-8")
        if byte_next:
            
            if ((byte_next == bytes_carraigereturn) or (byte_next == bytes_linefeed)):
                print(command)
                command = ""               
            else:
                command += char_next
                
            char_next = ''
            byte_next = 0
                
        wait(500)

except serial.SerialException as e:
    print(e.msg)
    raise       # XXX handle instead of re-raise?
