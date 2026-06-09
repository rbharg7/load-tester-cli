import asyncio
import aiohttp 
import time

class LoadRunner:

    def __init__ (self, url, method = 'GET', headers = None, body = None, concurrency = 10, duration = 5):
        self.url = url
        self.method = method
        self.headers = headers or {}
        self.body = body
        self.concurrency = concurrency  
        self.duration = duration
        self.results = []

    async def _send_one(self, session, semaphore):

        async with semaphore:
            start = time.monotonic()
            try: 
                async with session.request(

                    self.method,
                    self.url,
                    headers = self.headers, 
                    data = self.body
                ) as response:
                    await response.read()
                    latency = (time.monotonic() - start ) * 1000
                    self.results.append({
                        "latency_ms": round(latency, 2),
                        "status" : response.status,
                        "error": None
                    })
            except Exception as e:
                latency = (time.monotonic() - start ) * 1000
                self.results.append({

                    "latency_ms": round(latency, 2),
                    "status": 0,
                    "error": str(e)

                })



    async def run(self):

        semaphore = asyncio.Semaphore(self.concurrency)
        connector = aiohttp.TCPConnector(limit = self.concurrency)

        async with aiohttp.ClientSession(
            connector = connector,
            headers  = self.headers
        ) as session :
            tasks = []
            start = time.monotonic()

            while time.monotonic() - start < self.duration:
                task = asyncio.create_task(
                    self._send_one(session, semaphore)
                )
                tasks.append(task)
                await asyncio.sleep(0.001)
           
            await asyncio.gather(*tasks)

        return self.results 

        
            
