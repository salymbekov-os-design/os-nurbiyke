
import random
import os
import matplotlib.pyplot as plt


# =====================================================
# 1. ИСХОДНЫЕ ДАННЫЕ
# =====================================================

REFERENCE_STRING = [
    7, 0, 1, 2, 0, 3, 0, 4, 2, 3,
    0, 3, 2, 1, 2, 0, 1, 7, 0, 1
]

BELADY_STRING = [
    1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5
]

os.makedirs("results", exist_ok=True)
os.makedirs("reports", exist_ok=True)


# =====================================================
# 2. FIFO
# =====================================================

def fifo(pages, frames_count):
    frames = []
    faults = 0
    pointer = 0

    for page in pages:
        if page not in frames:
            faults += 1

            if len(frames) < frames_count:
                frames.append(page)
            else:
                frames[pointer] = page
                pointer = (pointer + 1) % frames_count

    return faults


# =====================================================
# 3. LRU
# =====================================================

def lru(pages, frames_count):
    frames = []
    last_used = {}
    faults = 0

    for time, page in enumerate(pages):
        if page not in frames:
            faults += 1

            if len(frames) < frames_count:
                frames.append(page)
            else:
                oldest = min(frames, key=lambda p: last_used[p])
                frames[frames.index(oldest)] = page

        # Обновляем время при КАЖДОМ обращении
        last_used[page] = time

    return faults


# =====================================================
# 4. OPTIMAL
# =====================================================

def optimal(pages, frames_count):
    frames = []
    faults = 0

    for i, page in enumerate(pages):
        if page not in frames:
            faults += 1

            if len(frames) < frames_count:
                frames.append(page)
            else:
                future = pages[i + 1:]

                farthest_page = None
                farthest_position = -1

                for frame_page in frames:
                    if frame_page not in future:
                        farthest_page = frame_page
                        break

                    position = future.index(frame_page)

                    if position > farthest_position:
                        farthest_position = position
                        farthest_page = frame_page

                frames[frames.index(farthest_page)] = page

    return faults


# =====================================================
# 5. CLOCK (SECOND CHANCE)
# =====================================================

def clock(pages, frames_count):
    frames = [None] * frames_count
    reference_bits = [0] * frames_count

    pointer = 0
    faults = 0

    for page in pages:

        if page in frames:
            index = frames.index(page)
            reference_bits[index] = 1
            continue

        faults += 1

        while reference_bits[pointer] == 1:
            reference_bits[pointer] = 0
            pointer = (pointer + 1) % frames_count

        frames[pointer] = page
        reference_bits[pointer] = 1

        pointer = (pointer + 1) % frames_count

    return faults


ALGORITHMS = {
    "FIFO": fifo,
    "LRU": lru,
    "Optimal": optimal,
    "Clock": clock
}


# =====================================================
# 6. VARIANT A: СРАВНЕНИЕ 3 И 4 КАДРОВ
# =====================================================

def variant_a():
    print("\n" + "=" * 55)
    print("VARIANT A: BASIC ALGORITHMS")
    print("=" * 55)

    results = {}

    for count in [3, 4]:
        print(f"\nКоличество кадров: {count}")
        results[count] = {}

        for name, algorithm in ALGORITHMS.items():
            value = algorithm(REFERENCE_STRING, count)
            results[count][name] = value
            print(f"{name:10}: {value} отказов")

    print("\nЭталон при 3 кадрах:")
    print("FIFO = 15")
    print("LRU = 12")
    print("Optimal = 9")

    return results


# =====================================================
# 7. VARIANT B: ГРАФИК 1-8 КАДРОВ
# =====================================================

def variant_b_graph():
    print("\n" + "=" * 55)
    print("VARIANT B: PAGE FAULT GRAPH")
    print("=" * 55)

    results = {
        name: []
        for name in ALGORITHMS
    }

    frame_counts = list(range(1, 9))

    for count in frame_counts:
        for name, algorithm in ALGORITHMS.items():
            faults = algorithm(REFERENCE_STRING, count)
            results[name].append(faults)

    for name, values in results.items():
        print(f"{name}: {values}")

    plt.figure(figsize=(10, 6))

    for name, values in results.items():
        plt.plot(
            frame_counts,
            values,
            marker="o",
            label=name
        )

    plt.title("Page Faults vs Number of Frames")
    plt.xlabel("Number of Frames")
    plt.ylabel("Page Faults")
    plt.xticks(frame_counts)
    plt.grid(True)
    plt.legend()

    plt.savefig("results/page_faults.png", dpi=150)
    plt.close()

    print("График сохранён: results/page_faults.png")

    return results


# =====================================================
# 8. АНОМАЛИЯ БЕЛАДИ
# =====================================================

def belady_experiment():
    print("\n" + "=" * 55)
    print("BELADY'S ANOMALY")
    print("=" * 55)

    results = {}

    for name, algorithm in ALGORITHMS.items():
        three = algorithm(BELADY_STRING, 3)
        four = algorithm(BELADY_STRING, 4)

        results[name] = (three, four)

        print(
            f"{name:10}: "
            f"3 кадра = {three}, "
            f"4 кадра = {four}"
        )

    fifo_three, fifo_four = results["FIFO"]

    print("\nПроверка аномалии:")
    if fifo_four > fifo_three:
        print("Аномалия Белади воспроизведена!")
    else:
        print("Аномалия не обнаружена!")

    plt.figure(figsize=(8, 5))

    for name, (three, four) in results.items():
        plt.plot(
            [3, 4],
            [three, four],
            marker="o",
            label=name
        )

    plt.title("Belady's Anomaly")
    plt.xlabel("Number of Frames")
    plt.ylabel("Page Faults")
    plt.xticks([3, 4])
    plt.grid(True)
    plt.legend()

    plt.savefig("results/belady.png", dpi=150)
    plt.close()

    return results


# =====================================================
# 9. ЛОКАЛЬНАЯ И СЛУЧАЙНАЯ ПОСЛЕДОВАТЕЛЬНОСТИ
# =====================================================

def generate_locality(length=1000):
    pages = []

    # Частые обращения к небольшой группе страниц
    for _ in range(length):
        if random.random() < 0.8:
            pages.append(random.randint(0, 4))
        else:
            pages.append(random.randint(5, 19))

    return pages


def generate_random(length=1000):
    return [
        random.randint(0, 19)
        for _ in range(length)
    ]


def workload_experiment():
    print("\n" + "=" * 55)
    print("LOCALITY VS RANDOM")
    print("=" * 55)

    random.seed(42)

    workloads = {
        "Locality": generate_locality(),
        "Random": generate_random()
    }

    results = {}

    for workload_name, pages in workloads.items():

        print(f"\n{workload_name}:")

        results[workload_name] = {}

        for name, algorithm in ALGORITHMS.items():
            faults = algorithm(pages, 5)

            results[workload_name][name] = faults

            print(f"{name:10}: {faults}")

    plt.figure(figsize=(9, 5))

    names = list(ALGORITHMS.keys())
    x = list(range(len(names)))
    width = 0.35

    local_values = [
        results["Locality"][name]
        for name in names
    ]

    random_values = [
        results["Random"][name]
        for name in names
    ]

    plt.bar(
        [i - width / 2 for i in x],
        local_values,
        width,
        label="Locality"
    )

    plt.bar(
        [i + width / 2 for i in x],
        random_values,
        width,
        label="Random"
    )

    plt.title("Locality vs Random Workload")
    plt.xlabel("Algorithm")
    plt.ylabel("Page Faults")
    plt.xticks(x, names)
    plt.legend()
    plt.grid(axis="y")

    plt.savefig(
        "results/workload_comparison.png",
        dpi=150
    )

    plt.close()

    return results


# =====================================================
# 10. СОХРАНЕНИЕ ОТЧЁТА
# =====================================================

def save_report(a_results, graph_results,
                belady_results, workload_results):

    with open(
        "reports/experiment_results.txt",
        "w",
        encoding="utf-8"
    ) as file:

        file.write("PRACTICAL WORK 11\n")
        file.write("PAGE REPLACEMENT ALGORITHMS\n\n")

        file.write("VARIANT A\n")

        for count, values in a_results.items():
            file.write(f"\nFrames: {count}\n")

            for name, faults in values.items():
                file.write(f"{name}: {faults}\n")

        file.write("\nVARIANT B: GRAPH DATA\n")

        for name, values in graph_results.items():
            file.write(f"{name}: {values}\n")

        file.write("\nBELADY'S ANOMALY\n")

        for name, values in belady_results.items():
            file.write(
                f"{name}: 3 frames={values[0]}, "
                f"4 frames={values[1]}\n"
            )

        file.write("\nLOCALITY VS RANDOM\n")

        for workload, values in workload_results.items():
            file.write(f"\n{workload}\n")

            for name, faults in values.items():
                file.write(f"{name}: {faults}\n")

    print("\nОтчёт сохранён в reports/experiment_results.txt")


# =====================================================
# 11. MAIN
# =====================================================

def main():

    print("PRACTICAL WORK 11")
    print("PAGE REPLACEMENT ALGORITHMS")

    a_results = variant_a()

    graph_results = variant_b_graph()

    belady_results = belady_experiment()

    workload_results = workload_experiment()

    save_report(
        a_results,
        graph_results,
        belady_results,
        workload_results
    )

    print("\nВсе эксперименты Python завершены!")
    print("Проверь папки results/ и reports/")


if __name__ == "__main__":
    main()
