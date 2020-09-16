import asyncio
import logging

class Tasker:
    def __init__(self):
        self.running = False    

    async def addJob(self, coro):
        """ Add new coroutine to task queue """
        if not asyncio.iscoroutine(coro):
            raise ValueError("a coroutine was expected, got {!r}".format(coro))
        
        await self._queue.put(coro)
        logging.info(f"Added new coroutine {coro}")
    
    async def _loop(self):
        self._queue = asyncio.Queue()
        while 1:
            coro = await self._queue.get()
            try:
                asyncio.run(coro)
            except Exception as e:
                print(f"{self} Error: {e}")

    async def start(self):
        """ Return infinite task to asyncio.gather with other tasks in program """
        if self.running:
            return None # TODO: Add already running exception
        
        self.running = True
        return asyncio.create_task(self._loop())