import json, time
import os, time, asyncio

class AFileStream(object):
    def __init__(self, name, delay=1):
        self.name = name
        self.delay = delay

    async def _read_stream(self):
        with open(self.name, "rb") as current:
            curino = os.fstat(current.fileno()).st_ino
            while True:
                while True:
                    current.seek(0)
                    line =  current.read()
                    if not line:
                        break
                    time.sleep(self.delay)
                    return  line
                try:
                    if os.stat(self.name).st_ino != curino:
                        new = open(self.name, "r")
                        current.close()
                        current = new
                        current.seek(0)
                        curino = os.fstat(current.fileno()).st_ino
                        continue
                except IOError:
                    pass
                time.sleep(self.delay)
    async def read_stream(self):
        with open(self.name, "rb") as current:
            current.seek(0,2)      # Go to the end of the file
            while True:
                 line = thefile.readline()
                 if not line:
                     time.sleep(0.1)    # Sleep briefly
                     continue
                 return line

    def __await__(self):
        return self.read_stream().__await__()

if __name__ == '__main__':
    async def log(fs):
        while True:
            print(await fs)
    fs = AFileStream("/proc/meminfo")
    l = asyncio.get_event_loop(log(fs))
