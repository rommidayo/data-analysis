from collections import defaultdict
from itertools import combinations

min_count = int(input("Введите критическую частоту: ")) / 100

with open("baskets.csv", 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

products = []
c = 0
for line in lines:
    items = [item.strip() for item in line.split(',')]
    if items:
        products.append(items)
        c += 1
        # print(items)
print(f"Датасет загружен, транзакций: {c}\n")

frequent_itemsets = {}

item_counts = defaultdict(int)
for transaction in products:
    for item in transaction:
        item_counts[item] += 1

L1 = {frozenset([item]): count for item, count in item_counts.items()
      if count / len(products) >= min_count}

if not L1:
    print("Нет товаров, удовлетворяющих критической частоте!")
    exit()

frequent_itemsets[1] = L1
print(f"L1: найдено {len(L1)} частых товаров")
for itemset, count in sorted(L1.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {set(itemset)}: {count} ({count / len(products) * 100:.1f}%)")
if len(L1) > 10:
    print(f"  ... и еще {len(L1) - 10} товаров")
print()

k = 2
while True:
    prev_itemsets = list(frequent_itemsets[k - 1].keys())

    if len(prev_itemsets) < k:
        break

    candidates = set()

    for i in range(len(prev_itemsets)):
        for j in range(i + 1, len(prev_itemsets)):
            union = set(prev_itemsets[i]) | set(prev_itemsets[j])

            if len(union) == k:
                is_valid = True
                for subset in combinations(union, k - 1):
                    if frozenset(subset) not in frequent_itemsets[k - 1]:
                        is_valid = False
                        break

                if is_valid:
                    candidates.add(frozenset(union))

    if not candidates:
        break

    candidate_counts = defaultdict(int)

    for transaction in products:
        transaction_set = set(transaction)
        for candidate in candidates:
            if candidate.issubset(transaction_set):
                candidate_counts[candidate] += 1

    Lk = {candidate: count for candidate, count in candidate_counts.items()
          if count / len(products) >= min_count}

    if not Lk:
        break

    frequent_itemsets[k] = Lk
    print(f"L{k}: найдено {len(Lk)} частых наборов")

    for itemset, count in sorted(Lk.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {set(itemset)}: {count} ({count / len(products) * 100:.1f}%)")
    if len(Lk) > 10:
        print(f"  ... и еще {len(Lk) - 10} наборов")
    print()

    k += 1