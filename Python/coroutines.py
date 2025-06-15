import asyncio

async def main():
    print('hello')
    await asyncio.sleep(1)
    print('world')

asyncio.run(main())

print("-"*20)
print("\n"*2)

"""
Coroutines are a type of function that allow you to pause and resume execution, facilitating asynchronous programming. 
Unlike regular functions that run until completion, coroutines can yield control back to the caller mid-execution, allowing other tasks to run concurrently.
"""

async def task1():
    print("Starting task 1")
    await asyncio.sleep(5)
    print("Finished task 1")

async def task2():
    print("Starting task 2")
    await asyncio.sleep(2)
    print("Finished task 2")

async def main():
    await asyncio.gather(task1(), task2())

asyncio.run(main())

print("-"*20)
print("\n"*2)


import asyncio
import aiohttp # type: ignore

async def fetch(session, url):
    try:
        async with session.get(url, timeout=5) as response:
            if response.status == 200:
                data = await response.text()
                return data
            else:
                return None
    except Exception as e:
        return None

async def fetch_first_success(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]

        # as_completed: ilk tamamlanan task'lar sırayla döner
        for completed in asyncio.as_completed(tasks):
            result = await completed
            if result:
                return result  # ilk başarılı sonucu döndür
        return None  # Hiçbiri başarılı değilse

# Örnek çağrı:
if __name__ == "__main__":
    urls = [
        "https://httpstat.us/404",     # başarısız
        "https://httpstat.us/200?sleep=2000",  # geç gelen başarılı
        "https://httpstat.us/200?sleep=1000",  # daha erken başarılı
    ]
    result = asyncio.run(fetch_first_success(urls))
    print("✅ İlk başarılı yanıt:", result[:50] if result else "YOK")



"""
1. "Python’da coroutine nedir? Ne zaman kullanırsın?"
Cevap Stratejisi:

Coroutine, async def ile tanımlanan, duraklayabilen ve devam edebilen fonksiyondur.

I/O-bound işlemlerde, CPU boşta bekliyorsa (örneğin: dosya okuma, ağ isteği, DB sorgusu), coroutine ile bu beklemeyi başka işlemlerle paralel yürütürüz.

Örnek: API isteklerini aynı anda göndermek ya da aynı anda birden çok dosya okumak.


##########################################################################################################
##########################################################################################################

2. "Senkron ve asenkron fonksiyonlar arasındaki fark nedir?"
Cevap Stratejisi:

Senkron fonksiyonlar çalışırken tüm işlem akışını durdurur, sonucu alınana kadar diğer işler bekler.

Asenkron fonksiyonlar await edilen noktada kontrolü bırakır ve başka coroutine'lerin çalışmasına izin verir.

CPU-bound işler için threading/multiprocessing daha uygundur; I/O-bound için coroutine’ler idealdir.


##########################################################################################################
##########################################################################################################

Seni Öne Geçirecek Cümleler

"Coroutine’ler blocking olmayan, tek-threadli concurrency sağlar. Özellikle network, dosya sistemi, ya da kullanıcıdan gelen sinyaller gibi I/O-bound işlemlerde büyük performans artışı sağlar."

"CPU-bound işlemler için asyncio yerine multiprocessing tercih ederim çünkü asyncio event loop CPU’yu verimli kullanamaz."

"Gerçek hayatta asyncio'yu genellikle REST API paralel çağrılarında, socket sunucularında, log/dosya okuma gibi non-blocking yapılarda kullanırım."

"""