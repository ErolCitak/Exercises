"""
PYTHON GLOBAL INTERPRETER LOCK (GIL) - KAPSAMLI AÇIKLAMA
========================================================

GIL NEDİR?
-----------
Global Interpreter Lock (GIL), CPython'da aynı anda sadece bir thread'in 
Python bytecode çalıştırmasına izin veren bir mutex (karşılıklı dışlama kilidi)'dir.

Bu, Python'da TRUE PARALLELISM'in mümkün olmadığı anlamına gelir.
Sadece CONCURRENCY (eşzamanlılık) mümkündür.
"""

import threading
import time
import multiprocessing
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import sys

# ================ GIL'İN ETKİSİNİ GÖSTERME ================

def cpu_bound_task(n):
    """CPU-intensive task - GIL'den etkilenir"""
    total = 0
    for i in range(n):
        total += i * i
    return total

def io_bound_task():
    """I/O-intensive task - GIL'den daha az etkilenir"""
    time.sleep(1)  # I/O operasyonu simülasyonu
    return "I/O completed"

# ================ THREADING VS MULTIPROCESSING KARŞILAŞTIRMA ================

def demonstrate_gil_effect():
    """GIL'in etkisini threading vs multiprocessing ile göster"""
    print("=== GIL ETKİSİ DEMONSTRASYONu ===\n")
    
    n = 1000000  # CPU-intensive task için parametre
    num_workers = 4
    
    # 1. SEQUENTIAL EXECUTION
    print("1. Sequential Execution (Tek thread):")
    start_time = time.time()
    results = []
    for _ in range(num_workers):
        results.append(cpu_bound_task(n))
    sequential_time = time.time() - start_time
    print(f"   Süre: {sequential_time:.2f} saniye")
    print(f"   Sonuç: {len(results)} task tamamlandı\n")
    
    # 2. THREADING (GIL'den etkilenir)
    print("2. Threading (GIL'den etkilenir):")
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(cpu_bound_task, n) for _ in range(num_workers)]
        results = [future.result() for future in futures]
    threading_time = time.time() - start_time
    print(f"   Süre: {threading_time:.2f} saniye")
    print(f"   Sonuç: {len(results)} task tamamlandı")
    print(f"   Speedup: {sequential_time/threading_time:.2f}x (idealde {num_workers}x olmalıydı)\n")
    
    # 3. MULTIPROCESSING (GIL'den etkilenmez)
    print("3. Multiprocessing (GIL'den etkilenmez):")
    start_time = time.time()
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(cpu_bound_task, n) for _ in range(num_workers)]
        results = [future.result() for future in futures]
    multiprocessing_time = time.time() - start_time
    print(f"   Süre: {multiprocessing_time:.2f} saniye")
    print(f"   Sonuç: {len(results)} task tamamlandı")
    print(f"   Speedup: {sequential_time/multiprocessing_time:.2f}x\n")
    
    print("SONUÇ:")
    print(f"   Sequential: {sequential_time:.2f}s")
    print(f"   Threading:  {threading_time:.2f}s (speedup: {sequential_time/threading_time:.2f}x)")
    print(f"   Multiproc:  {multiprocessing_time:.2f}s (speedup: {sequential_time/multiprocessing_time:.2f}x)")

def demonstrate_io_bound_threading():
    """I/O-bound tasklar için threading'in avantajını göster"""
    print("\n=== I/O-BOUND TASKLAR İÇİN THREADING ===\n")
    
    num_tasks = 5
    
    # Sequential I/O
    print("1. Sequential I/O:")
    start_time = time.time()
    results = []
    for _ in range(num_tasks):
        results.append(io_bound_task())
    sequential_io_time = time.time() - start_time
    print(f"   Süre: {sequential_io_time:.2f} saniye\n")
    
    # Threading ile I/O
    print("2. Threading ile I/O:")
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=num_tasks) as executor:
        futures = [executor.submit(io_bound_task) for _ in range(num_tasks)]
        results = [future.result() for future in futures]
    threading_io_time = time.time() - start_time
    print(f"   Süre: {threading_io_time:.2f} saniye")
    print(f"   Speedup: {sequential_io_time/threading_io_time:.2f}x\n")
    
    print("I/O-bound tasklar için threading çok etkili!")

# ================ GIL RELEASE MEKANİZMASI ================

def gil_release_demonstration():
    """GIL'in ne zaman release edildiğini göster"""
    print("\n=== GIL RELEASE MEKANİZMALARI ===\n")
    
    import sys
    
    # Python'da GIL check interval
    print(f"Python GIL check interval: {sys.getswitchinterval()} saniye")
    print("Bu, thread'ler arasında geçiş için maksimum süre\n")
    
    # GIL release durumları
    gil_release_scenarios = [
        "1. I/O operasyonları (file read/write, network calls)",
        "2. time.sleep() çağrıları",
        "3. C extension'lar (NumPy, Pandas gibi)",
        "4. sys.getswitchinterval() süresinde bir kez",
        "5. Garbage collection sırasında",
        "6. Bazı built-in fonksiyonlar (sorted, map, filter)"
    ]
    
    print("GIL şu durumlarda release edilir:")
    for scenario in gil_release_scenarios:
        print(f"   {scenario}")

# ================ GIL'İ BYPASS ETME YÖNTEMLERİ ================

def gil_bypass_methods():
    """GIL'i bypass etme yöntemlerini göster"""
    print("\n=== GIL'İ BYPASS ETME YÖNTEMLERİ ===\n")
    
    methods = {
        "1. Multiprocessing": {
            "description": "Ayrı Python process'leri kullanma",
            "pros": ["Gerçek paralellik", "CPU-bound tasklar için ideal"],
            "cons": ["Memory overhead", "IPC (Inter-Process Communication) gerekli"]
        },
        "2. AsyncIO": {
            "description": "Asenkron programlama",
            "pros": ["I/O-bound tasklar için mükemmel", "Tek thread, yüksek concurrency"],
            "cons": ["CPU-bound tasklar için uygun değil", "Learning curve"]
        },
        "3. C Extensions": {
            "description": "C/C++ ile yazılmış modüller",
            "pros": ["GIL release edebilir", "Yüksek performans"],
            "cons": ["Kompleks geliştirme", "Platform bağımlılığı"]
        },
        "4. Alternative Implementations": {
            "description": "Jython, IronPython, PyPy",
            "pros": ["GIL yok (bazılarında)", "JVM/CLR avantajları"],
            "cons": ["C extensions uyumluluğu", "Ecosystem eksiklikleri"]
        }
    }
    
    for method, details in methods.items():
        print(f"{method}: {details['description']}")
        print(f"   Avantajlar: {', '.join(details['pros'])}")
        print(f"   Dezavantajlar: {', '.join(details['cons'])}\n")

# ================ ASYNCIO ÖRNEK ================

import asyncio

async def async_io_task(task_id, duration):
    """Asenkron I/O task örneği"""
    print(f"Task {task_id} başladı")
    await asyncio.sleep(duration)
    print(f"Task {task_id} tamamlandı")
    return f"Task {task_id} result"

async def demonstrate_asyncio():
    """AsyncIO ile GIL'i bypass etme örneği"""
    print("=== ASYNCIO İLE GIL BYPASS ===\n")
    
    print("5 asenkron task çalıştırılıyor...")
    start_time = time.time()
    
    tasks = [
        async_io_task(i, 1) for i in range(1, 6)
    ]
    
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    print(f"\nToplam süre: {end_time - start_time:.2f} saniye")
    print("5 task 1 saniyede paralel olarak tamamlandı!")

# ================ NUMPY İLE GIL BYPASS ================

def numpy_gil_bypass():
    """NumPy'ın GIL'i nasıl bypass ettiğini göster"""
    print("\n=== NUMPY İLE GIL BYPASS ===\n")
    
    try:
        import numpy as np
        
        # Büyük NumPy array işlemleri
        def numpy_computation():
            arr1 = np.random.rand(1000, 1000)
            arr2 = np.random.rand(1000, 1000)
            result = np.dot(arr1, arr2)  # Matrix multiplication
            return result.sum()
        
        # Threading ile NumPy - GIL bypass edilir
        print("NumPy işlemleri threading ile:")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(numpy_computation) for _ in range(4)]
            results = [future.result() for future in futures]
        
        numpy_time = time.time() - start_time
        print(f"   4 thread ile süre: {numpy_time:.2f} saniye")
        print("   NumPy C extensions GIL'i release eder!")
        
    except ImportError:
        print("NumPy yüklü değil, örnek atlandı")

# ================ GIL MONİTÖRİNG ================

def gil_monitoring():
    """GIL'in etkisini monitoring etme"""
    print("\n=== GIL MONİTÖRİNG ===\n")
    
    import threading
    import time
    
    # Thread'lerin ne kadar süre çalıştığını ölçme
    results = {}
    
    def worker_thread(thread_id, work_amount):
        start_time = time.time()
        
        # CPU-intensive work
        total = 0
        for i in range(work_amount):
            total += i * i
        
        end_time = time.time()
        results[thread_id] = {
            'duration': end_time - start_time,
            'result': total
        }
        print(f"Thread {thread_id}: {end_time - start_time:.3f} saniye")
    
    print("4 thread'i aynı anda başlatıyoruz:")
    threads = []
    start_time = time.time()
    
    for i in range(4):
        thread = threading.Thread(target=worker_thread, args=(i, 500000))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    total_time = time.time() - start_time
    print(f"\nToplam süre: {total_time:.3f} saniye")
    print("Thread'ler sırayla çalıştı (GIL nedeniyle)!")

# ================ EN İYİ PRATİKLER ================

def best_practices():
    """GIL ile çalışırken en iyi pratikler"""
    print("\n=== GIL İLE ÇALIŞMA PRATİKLERİ ===\n")
    
    practices = [
        "1. CPU-bound tasklar için multiprocessing kullanın",
        "2. I/O-bound tasklar için threading veya asyncio kullanın",
        "3. NumPy, Pandas gibi C-based library'leri tercih edin",
        "4. Uzun süren hesaplamalar için C extensions yazın",
        "5. Profile edin: cProfile, threading profiler kullanın",
        "6. GIL'in ne zaman release edildiğini bilin",
        "7. Uygun concurrency pattern'i seçin (thread vs process vs async)",
        "8. Memory sharing vs message passing trade-off'unu değerlendirin"
    ]
    
    for practice in practices:
        print(f"   {practice}")
    
    print("\n=== SEÇIM REHBERİ ===")
    decision_guide = {
        "CPU-bound + Parallelism gerekli": "→ Multiprocessing",
        "I/O-bound + Many connections": "→ AsyncIO",
        "I/O-bound + Simple threading": "→ Threading",
        "Mixed workload": "→ Hybrid approach",
        "High performance computing": "→ C extensions + multiprocessing",
        "Web scraping": "→ Threading veya AsyncIO",
        "Data processing": "→ Pandas/NumPy + multiprocessing"
    }
    
    for scenario, solution in decision_guide.items():
        print(f"   {scenario} {solution}")

# ================ ANA ÇALIŞTIRMA KODU ================

def main():
    """Ana demonstration fonksiyonu"""
    print("PYTHON GLOBAL INTERPRETER LOCK (GIL) DEMONSTRASYONu")
    print("=" * 55)
    
    # GIL'in temel etkisini göster
    demonstrate_gil_effect()
    
    # I/O-bound tasklar için threading avantajını göster
    demonstrate_io_bound_threading()
    
    # GIL release mekanizmalarını açıkla
    gil_release_demonstration()
    
    # GIL bypass yöntemlerini göster
    gil_bypass_methods()
    
    # NumPy ile GIL bypass
    numpy_gil_bypass()
    
    # GIL monitoring
    gil_monitoring()
    
    # En iyi pratikler
    best_practices()
    
    print("\n=== GIL HAKKINDA ÖNEMLİ NOTLAR ===")
    important_notes = [
        "• GIL sadece CPython'da var (PyPy, Jython'da yok)",
        "• Python 3.13'te nogil branch geliştiriliyor",
        "• Threading ≠ Parallelism (Python'da)",
        "• I/O-bound tasklar için threading hala yararlı",
        "• CPU-bound tasklar için multiprocessing şart",
        "• AsyncIO single-threaded ama highly concurrent",
        "• C extensions GIL'i release edebilir"
    ]
    
    for note in important_notes:
        print(f"   {note}")

# AsyncIO örneğini çalıştırmak için ayrı fonksiyon
def run_asyncio_demo():
    """AsyncIO demosunu çalıştır"""
    asyncio.run(demonstrate_asyncio())

if __name__ == "__main__":
    main()
    print("\n" + "="*55)
    print("ASYNCIO DEMO ÇALIŞTIIRILIYOR...")
    print("="*55)
    run_asyncio_demo()

# ================ SONUÇ VE ÖZETֵ ================

"""
GIL ÖZET:
=========

NEDİR: Python bytecode'un aynı anda sadece bir thread tarafından çalıştırılmasını 
       sağlayan mutex

NEDEN VAR: 
- Memory management basitliği
- C extensions ile uyumluluk  
- Reference counting thread-safety

ETKİLERİ:
- CPU-bound tasklar için threading etkisiz
- I/O-bound tasklar için threading hala yararlı
- True parallelism için multiprocessing gerekli

ÇÖZÜMLER:
- Multiprocessing (CPU-bound)
- AsyncIO (I/O-bound)
- C Extensions (NumPy, Pandas)
- Alternative Python implementations

GELECEK:
- Python 3.13'te nogil branch
- Sub-interpreter based parallelism
- Free-threading experiments
"""

"""
CPU-bound Task Örneği: 1 milyon sayının karelerinin toplamı
I/O-bound Task Örneği: 10 web sitesinden veri çekme

🎯 Hangi Durumda Ne Kullanmalı?
CPU-bound için:

❌ Threading kullanma
✅ Multiprocessing kullan
✅ NumPy/Pandas gibi C-based kütüphaneler kullan

I/O-bound için:

✅ Threading basit ve etkili
⭐ AsyncIO en performanslı
❓ Multiprocessing gereksiz (overhead fazla)

Karma durumlar için:

CPU + I/O karışımı → Multiprocessing + AsyncIO hibrit yaklaşım
Veri işleme pipeline'ları → Pandas/NumPy + Multiprocessing


🧠 Neden Bu Farklar Oluşuyor?
CPU-bound'da Threading neden işe yaramaz?

Python kodu sürekli çalışır → GIL sürekli kilitli
Thread'ler sıra bekler → paralellik yok
Context switching maliyeti → ek yavaşlık

I/O-bound'da Threading neden işe yarar?

I/O sırasında Python kodu çalışmaz → GIL serbest
Beklerken başka thread çalışabilir → verimlilik
I/O paralel → CPU kullanımı optimize
"""