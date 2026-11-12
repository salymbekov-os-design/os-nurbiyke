from collections import OrderedDict
import matplotlib.pyplot as plt


# ==========================================
# НАСТРОЙКИ
# ==========================================

PAGE_SIZE = 1024
NUM_PAGES = 16
ADDRESS_SPACE_SIZE = PAGE_SIZE * NUM_PAGES

MEMORY_ACCESS_NS = 100
TLB_ACCESS_NS = 10


# ==========================================
# ЗАГРУЗКА ТАБЛИЦЫ СТРАНИЦ
# ==========================================

def load_page_table(filename):
    page_table = {}

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            parts = line.split()

            page = int(parts[0])

            if parts[1] == "отсутствует":
                page_table[page] = None
            else:
                page_table[page] = int(parts[1])

    return page_table


# ==========================================
# ЗАГРУЗКА АДРЕСОВ
# ==========================================

def load_references(filename):
    references = []

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                references.append(int(line))

    return references


# ==========================================
# ТРАНСЛЯЦИЯ БЕЗ TLB
# ==========================================

def translate_address(logical_address, page_table):

    page = logical_address // PAGE_SIZE
    offset = logical_address % PAGE_SIZE

    if page not in page_table:
        return {
            "logical": logical_address,
            "page": page,
            "offset": offset,
            "frame": None,
            "physical": None,
            "page_fault": True
        }

    frame = page_table[page]

    if frame is None:
        return {
            "logical": logical_address,
            "page": page,
            "offset": offset,
            "frame": None,
            "physical": None,
            "page_fault": True
        }

    physical_address = frame * PAGE_SIZE + offset

    return {
        "logical": logical_address,
        "page": page,
        "offset": offset,
        "frame": frame,
        "physical": physical_address,
        "page_fault": False
    }


# ==========================================
# TLB С LRU
# ==========================================

class TLB:

    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

        self.hits = 0
        self.misses = 0

    def lookup(self, page):

        if page in self.cache:

            frame = self.cache.pop(page)

            # Перемещаем в конец:
            # это означает, что страница использовалась недавно
            self.cache[page] = frame

            self.hits += 1

            return frame

        self.misses += 1

        return None

    def insert(self, page, frame):

        if page in self.cache:
            self.cache.pop(page)

        elif len(self.cache) >= self.capacity:
            # Удаляем самый давно использованный элемент
            self.cache.popitem(last=False)

        self.cache[page] = frame

    @property
    def hit_rate(self):

        total = self.hits + self.misses

        if total == 0:
            return 0

        return self.hits / total


# ==========================================
# ТРАНСЛЯЦИЯ С TLB
# ==========================================

def translate_with_tlb(logical_address, page_table, tlb):

    page = logical_address // PAGE_SIZE
    offset = logical_address % PAGE_SIZE

    # Сначала проверяем TLB
    frame = tlb.lookup(page)

    # TLB HIT
    if frame is not None:

        physical_address = frame * PAGE_SIZE + offset

        return {
            "logical": logical_address,
            "page": page,
            "offset": offset,
            "frame": frame,
            "physical": physical_address,
            "tlb": "HIT",
            "page_fault": False
        }

    # TLB MISS
    frame = page_table.get(page)

    # Страница отсутствует
    if frame is None:

        return {
            "logical": logical_address,
            "page": page,
            "offset": offset,
            "frame": None,
            "physical": None,
            "tlb": "MISS",
            "page_fault": True
        }

    # Добавляем найденную страницу в TLB
    tlb.insert(page, frame)

    physical_address = frame * PAGE_SIZE + offset

    return {
        "logical": logical_address,
        "page": page,
        "offset": offset,
        "frame": frame,
        "physical": physical_address,
        "tlb": "MISS",
        "page_fault": False
    }


# ==========================================
# EAT
# ==========================================

def calculate_eat(hit_rate):

    hit_time = TLB_ACCESS_NS + MEMORY_ACCESS_NS

    miss_time = TLB_ACCESS_NS + 2 * MEMORY_ACCESS_NS

    eat = (
        hit_rate * hit_time
        + (1 - hit_rate) * miss_time
    )

    return eat


# ==========================================
# ДВУХУРОВНЕВАЯ ТАБЛИЦА
# ==========================================

def two_level_indices(page):

    level_1 = page // 4
    level_2 = page % 4

    return level_1, level_2


def two_level_memory_accesses(tlb_hit=False):

    if tlb_hit:
        return 1

    return 3


# ==========================================
# MAIN
# ==========================================

def main():

    print("=" * 70)
    print("ПРАКТИЧЕСКАЯ РАБОТА №10")
    print("СТРАНИЧНАЯ ОРГАНИЗАЦИЯ")
    print("=" * 70)

    print()

    print("Размер страницы:", PAGE_SIZE, "байт")
    print("Количество страниц:", NUM_PAGES)
    print("Размер адресного пространства:", ADDRESS_SPACE_SIZE, "байт")

    # --------------------------------------
    # Загрузка данных
    # --------------------------------------

    page_table = load_page_table("data/pagetable.txt")
    refs = load_references("data/refs.txt")

    print()
    print("Количество обращений:", len(refs))

    # --------------------------------------
    # Таблица страниц
    # --------------------------------------

    print()
    print("=" * 70)
    print("ТАБЛИЦА СТРАНИЦ")
    print("=" * 70)

    for page in range(NUM_PAGES):

        frame = page_table.get(page)

        if frame is None:
            print(f"Страница {page:2} -> отсутствует")
        else:
            print(f"Страница {page:2} -> кадр {frame:2}")

    # --------------------------------------
    # Контрольные адреса
    # --------------------------------------

    print()
    print("=" * 70)
    print("КОНТРОЛЬНЫЕ АДРЕСА")
    print("=" * 70)

    control_addresses = [
        0,
        1023,
        1024,
        2500,
        4096,
        6144
    ]

    for address in control_addresses:

        result = translate_address(
            address,
            page_table
        )

        if result["page_fault"]:

            print(
                f"LA={address:5} | "
                f"page={result['page']:2} | "
                f"offset={result['offset']:4} | "
                f"PAGE FAULT"
            )

        else:

            print(
                f"LA={address:5} | "
                f"page={result['page']:2} | "
                f"offset={result['offset']:4} | "
                f"frame={result['frame']:2} | "
                f"PA={result['physical']:5}"
            )

    # --------------------------------------
    # TLB
    # --------------------------------------

    TLB_SIZE = 4

    tlb = TLB(TLB_SIZE)

    print()
    print("=" * 70)
    print("ТРАНСЛЯЦИЯ С TLB")
    print("=" * 70)

    for address in refs:

        result = translate_with_tlb(
            address,
            page_table,
            tlb
        )

        if result["page_fault"]:

            print(
                f"LA={address:5} | "
                f"page={result['page']:2} | "
                f"offset={result['offset']:4} | "
                f"TLB={result['tlb']:4} | "
                f"PAGE FAULT"
            )

        else:

            print(
                f"LA={address:5} | "
                f"page={result['page']:2} | "
                f"offset={result['offset']:4} | "
                f"TLB={result['tlb']:4} | "
                f"frame={result['frame']:2} | "
                f"PA={result['physical']:5}"
            )

    # --------------------------------------
    # Статистика TLB
    # --------------------------------------

    print()
    print("=" * 70)
    print("СТАТИСТИКА TLB")
    print("=" * 70)

    print("Размер TLB:", TLB_SIZE)
    print("TLB hits:", tlb.hits)
    print("TLB misses:", tlb.misses)
    print(f"Hit rate: {tlb.hit_rate:.2%}")

    # --------------------------------------
    # EAT
    # --------------------------------------

    print()
    print("=" * 70)
    print("ЭФФЕКТИВНОЕ ВРЕМЯ ДОСТУПА")
    print("=" * 70)

    print("Время доступа к памяти:", MEMORY_ACCESS_NS, "нс")
    print("Время обращения к TLB:", TLB_ACCESS_NS, "нс")

    hit_time = TLB_ACCESS_NS + MEMORY_ACCESS_NS
    miss_time = TLB_ACCESS_NS + 2 * MEMORY_ACCESS_NS

    print("При TLB HIT:", hit_time, "нс")
    print("При TLB MISS:", miss_time, "нс")

    print()

    test_hit_rates = [
        0,
        0.25,
        0.50,
        0.75,
        0.90,
        1.00
    ]

    print("Теоретический EAT:")

    for hit_rate in test_hit_rates:

        eat = calculate_eat(hit_rate)

        print(
            f"Hit rate = {hit_rate:.0%} "
            f"-> EAT = {eat:.2f} нс"
        )

    measured_eat = calculate_eat(tlb.hit_rate)

    print()
    print(
        f"Измеренный hit rate = "
        f"{tlb.hit_rate:.2%}"
    )

    print(
        f"EAT по измеренному hit rate = "
        f"{measured_eat:.2f} нс"
    )

    # --------------------------------------
    # График
    # --------------------------------------

    print()
    print("=" * 70)
    print("РАЗМЕР TLB -> HIT RATE")
    print("=" * 70)

    # Длинная последовательность с локальностью
    local_refs = []

    for _ in range(100):

        local_refs.extend([
            100,
            110,
            120,
            130,
            150,
            160,
            180,
            190,
            200,
            210
        ])

    tlb_sizes = [
        1,
        2,
        3,
        4,
        5,
        6,
        8,
        10,
        12,
        16
    ]

    hit_rates = []

    for size in tlb_sizes:

        test_tlb = TLB(size)

        for address in local_refs:

            translate_with_tlb(
                address,
                page_table,
                test_tlb
            )

        hit_rates.append(
            test_tlb.hit_rate
        )

        print(
            f"TLB size = {size:2} | "
            f"Hit rate = {test_tlb.hit_rate:.2%}"
        )

    # График
    plt.figure(figsize=(8, 5))

    plt.plot(
        tlb_sizes,
        [rate * 100 for rate in hit_rates],
        marker="o"
    )

    plt.xlabel("Размер TLB, записей")
    plt.ylabel("Доля попаданий, %")
    plt.title("Зависимость размера TLB от доли попаданий")
    plt.grid(True)

    plt.savefig(
        "tlb_hit_rate.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.show()

    # --------------------------------------
    # Двухуровневая таблица
    # --------------------------------------

    print()
    print("=" * 70)
    print("ДВУХУРОВНЕВАЯ ТАБЛИЦА СТРАНИЦ")
    print("=" * 70)

    for page in range(NUM_PAGES):

        level_1, level_2 = two_level_indices(page)

        print(
            f"Page {page:2} -> "
            f"L1={level_1}, "
            f"L2={level_2}"
        )

    print()
    print("Без TLB:")
    print("L1 -> L2 -> данные")
    print("Всего обращений к памяти: 3")

    print()
    print("При TLB HIT:")
    print("TLB -> данные")
    print("Обращений к памяти после поиска в TLB: 1")

    # --------------------------------------
    # Итог
    # --------------------------------------

    print()
    print("=" * 70)
    print("ИТОГ")
    print("=" * 70)

    print(f"Размер страницы: {PAGE_SIZE} Б")
    print(f"Количество страниц: {NUM_PAGES}")
    print(f"Размер TLB: {TLB_SIZE}")
    print(f"TLB hits: {tlb.hits}")
    print(f"TLB misses: {tlb.misses}")
    print(f"TLB hit rate: {tlb.hit_rate:.2%}")
    print(f"EAT: {measured_eat:.2f} нс")
    print("Двухуровневая таблица без TLB: 3 обращения к памяти")

    print()
    print("График сохранён в файл: tlb_hit_rate.png")


if __name__ == "__main__":
    main()
