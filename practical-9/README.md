cd ~/practicals/practical-9

cat > README.md <<'EOF'
# Practical 9 — Моделирование управления памятью

## Цель работы

Изучить и сравнить алгоритмы динамического распределения памяти:

- First Fit
- Best Fit
- Worst Fit
- Buddy System

Также исследовать влияние слияния соседних свободных блоков на внешнюю фрагментацию.

## Структура проекта

```text
practical-9/
├── memsim.py       # алгоритмы First Fit, Best Fit, Worst Fit
├── buddy.py        # алгоритм Buddy System
├── compare.py      # сравнение всех подходов
├── run_ops1.py     # запуск операций из ops1.txt
├── gen_ops2.py     # генерация набора операций
├── ops1.txt        # тестовый набор из 12 операций
├── ops2.txt        # набор из 200 операций
└── README.md
