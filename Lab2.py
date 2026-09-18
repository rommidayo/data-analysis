from collections import defaultdict
from itertools import combinations

min_count = int(input("Введите критическую частоту: ")) / 100
min_conf = int(input("Введите минимальную достоверность: ")) / 100
sort_mode = input("Сортировка правил (support/lex): ").strip().lower()
if sort_mode not in ('support', 'lex'):
    sort_mode = 'support'

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

# ---------- Поиск ассоциативных правил ----------

support_map = {}
for level, itemsets in frequent_itemsets.items():
    for itemset, count in itemsets.items():
        support_map[itemset] = count

rules = []
for k_level, itemsets in frequent_itemsets.items():
    if k_level < 2 or k_level > 7:
        continue
    for itemset, count_z in itemsets.items():
        support_z = count_z / len(products)
        items = list(itemset)
        for r in range(1, k_level):
            for antecedent in combinations(items, r):
                antecedent = frozenset(antecedent)
                consequent = itemset - antecedent
                if not consequent:
                    continue
                count_a = support_map.get(antecedent)
                if count_a is None:
                    continue
                confidence = count_z / count_a
                if confidence >= min_conf:
                    rules.append((antecedent, consequent, support_z, confidence))

print("Ассоциативные правила:")
print(f"Найдено правил: {len(rules)}\n")

if sort_mode == 'support':
    rules.sort(key=lambda r: (r[2], r[3]), reverse=True)
else:
    rules.sort(key=lambda r: (sorted(r[0]), sorted(r[1])))

for ant, cons, sup, conf in rules:
    print(f"  {{{', '.join(sorted(ant))}}} -> {{{', '.join(sorted(cons))}}}: "
          f"support={sup * 100:.1f}%, confidence={conf * 100:.1f}%")