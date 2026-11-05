MEMORY = 1024


class Block:
    def __init__(self, pid, size):
        self.pid = pid
        self.size = size


class MemoryManager:
    def __init__(self, strategy="first", coalesce=False):
        self.strategy = strategy
        self.coalesce = coalesce
        self.blocks = [Block("-", MEMORY)]
        self.refused = 0

    def alloc(self, pid, size):
        holes = [
            block for block in self.blocks
            if block.pid == "-" and block.size >= size
        ]

        if not holes:
            self.refused += 1
            return False

        if self.strategy == "first":
            hole = holes[0]
        elif self.strategy == "best":
            hole = min(holes, key=lambda block: block.size)
        elif self.strategy == "worst":
            hole = max(holes, key=lambda block: block.size)
        else:
            raise ValueError("Unknown strategy")

        index = self.blocks.index(hole)

        if hole.size == size:
            self.blocks[index] = Block(pid, size)
        else:
            self.blocks[index:index + 1] = [
                Block(pid, size),
                Block("-", hole.size - size)
            ]

        return True

    def free(self, pid):
        for block in self.blocks:
            if block.pid == pid:
                block.pid = "-"
                break

        if self.coalesce:
            self.merge()

    def merge(self):
        merged = []

        for block in self.blocks:
            if (
                merged
                and merged[-1].pid == "-"
                and block.pid == "-"
            ):
                merged[-1].size += block.size
            else:
                merged.append(
                    Block(block.pid, block.size)
                )

        self.blocks = merged

    def stats(self):
        holes = [
            block.size
            for block in self.blocks
            if block.pid == "-"
        ]

        total_free = sum(holes)
        max_hole = max(holes, default=0)

        return total_free, max_hole


def load(filename):
    operations = []

    with open(filename, "r") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            parts = line.split()

            if parts[0] == "alloc":
                operations.append(
                    ("alloc", parts[1], int(parts[2]))
                )

            elif parts[0] == "free":
                operations.append(
                    ("free", parts[1])
                )

    return operations


def run(operations, strategy_name, coalesce=False, verbose=True):
    memory = MemoryManager(
        strategy=strategy_name,
        coalesce=coalesce
    )

    for number, operation in enumerate(operations, start=1):

        if operation[0] == "alloc":
            _, pid, size = operation
            success = memory.alloc(pid, size)

            if verbose:
                state = " ".join(
                    f"[{b.pid}:{b.size}"
                    "]"
                    for b in memory.blocks
                )

                result = (
                    f"{number} alloc {pid} {size} {state}"
                )

                if not success:
                    result += " — ОТКАЗ"

                print(result)

        elif operation[0] == "free":
            _, pid = operation
            memory.free(pid)

            if verbose:
                state = " ".join(
                    f"[{b.pid}:{b.size}]"
                    for b in memory.blocks
                )

                print(
                    f"{number} free {pid}  {state}"
                )

    total_free, max_hole = memory.stats()

    if verbose:
        holes = sum(
            1
            for block in memory.blocks
            if block.pid == "-"
        )

        print(
            f"свободно={total_free} "
            f"макс. дыра={max_hole} "
            f"дыр={holes} "
            f"отказов={memory.refused}"
        )

    return memory
