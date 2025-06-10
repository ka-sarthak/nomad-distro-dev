import time
import threading
import multiprocessing


# Task: CPU-bound
def cpu_task():
    sum(x * x for x in range(10**8))
    # with open("testing.txt", "w") as f:
    # for i in range(10**6):
    # f.write(f"{i}\n")


# Multithreading version
def run_multithreading():
    threads = []
    for _ in range(10):
        t = threading.Thread(target=cpu_task)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


# Multiprocessing version
def run_multiprocessing(num_processes):
    processes = []
    for _ in range(num_processes):
        p = multiprocessing.Process(target=cpu_task)
        p.start()
        processes.append(p)
    for p in processes:
        p.join()


if __name__ == "__main__":
    # print("Running multithreading...")
    # start = time.time()
    # run_multithreading()
    # print(f"Multithreading took: {time.time() - start:.2f} seconds\n")

    time_taken = []
    for i in range(16):
        # print("Running multiprocessing...")
        start = time.time()
        run_multiprocessing(num_processes=i + 1)
        time_taken.append(time.time() - start)
        # print(f"Multiprocessing took: {time.time() - start:.2f} seconds")

    import matplotlib.pyplot as plt

    plt.plot(time_taken, marker="o")
    plt.savefig("multi_threading_processing_test.png")
