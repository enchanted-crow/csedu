from bst import BST
from hash_table import HashTable
import seaborn as sns
import matplotlib.pyplot as plt
from cgi import print_form
import random
import pandas as pd
pd.plotting.register_matplotlib_converters()
# %matplotlib inline


def main():
    insert_keys, search_keys = create_insert_search_list()
    insert_search_mixed_seq = create_insert_search_mixed_seq(
        insert_keys, search_keys)
    # print(len(insert_search_mixed_seq))

    try:
        insert_keys = open("insert_keys.txt", 'w', encoding='utf-8')
        insert_keys.write(" ".join(str(i) for i in insert_search_mixed_seq))
        insert_keys.close()
    except IOError as e:
        errno, strerror = e.args
        print("I/O error({0}): {1}".format(errno, strerror))

    myBST = BST()
    insert_stats_bst, search_stats_bst, avg_hop_insert_bst, avg_hop_search_bst = insert_search(
        myBST, insert_search_mixed_seq)
    print("BST")
    print("Average hops in insert: " + str(avg_hop_insert_bst))
    print("Average hops in search: " + str(avg_hop_search_bst))

    myHashTable = HashTable(12000)
    insert_stats_hashtable, search_stats_hashtable, avg_hop_insert_hashtable, avg_hop_search_hashtable = insert_search(
        myHashTable, insert_search_mixed_seq)
    print("Hash Table")
    print("Average hops in insert: " + str(avg_hop_insert_hashtable))
    print("Average hops in search: " + str(avg_hop_search_hashtable))

    stats = pd.DataFrame({'avg_hops': [avg_hop_insert_bst, avg_hop_insert_hashtable,
                                       (avg_hop_search_bst), (avg_hop_search_hashtable)]},
                         index=['BST Insert', 'Double Hashing Insert', 'BST Search', 'Double Hashing Search'])

    stats.to_csv("stats.csv", index=True)

    # Draw the Plot
    plt.figure(figsize=(10, 6))
    # Add title
    plt.title("Average Hop Count in Insertion and Search in BST vs Double Hashing")
    # Bar chart showing average arrival delay for Spirit Airlines flights by month
    sns.barplot(x=stats.index, y=stats['avg_hops'])
    # Add label for vertical axis
    plt.ylabel("Average Hops")
    plt.show(block=True)


def insert_search(data_structure, insert_search_seq):
    insert_hop_count_sum = 0
    insert_n = 0
    insert_stats = []
    search_hop_count_sum = 0
    search_n = 0
    search_stats = []

    for i in insert_search_seq:
        type, data = i
        counter = HopCounter()
        if(type == 'I'):
            # print("Inserting " + str(data))
            data_structure.insert(data, counter.increment)
            insert_hop_count_sum += counter.count
            insert_n += 1
            insert_stats.append((i, counter.count))

            # print("Inserted " + str(data) +
            #       ". Hop Count = " + str(counter.count))
        if(type == 'S'):
            # print("Searching " + str(data))
            data_structure.search(data, counter.increment)
            search_hop_count_sum += counter.count
            search_n += 1
            search_stats.append((i, counter.count))

            # print("Searched for " + str(data) +
            #       ". Hop Count = " + str(counter.count))

    return insert_stats, search_stats, (insert_hop_count_sum / insert_n), (search_hop_count_sum / search_n)


def create_insert_search_list():
    # 10000 unique keys in range [1, 100000]
    insert_keys = random.sample(range(1, 100000000), 10000)

    # 1680 unique search keys (70% of 2100), 420 dups (30% of 2100)
    search_key_unique_temp = random.choices(insert_keys, k=2100)
    search_key_unique = []
    search_key_dup_temp = []
    for i in range(0, len(search_key_unique_temp)):
        if(i < 1680):
            search_key_unique.append(search_key_unique_temp[i])
        else:
            search_key_dup_temp.append(search_key_unique_temp[i])

    # print(len(search_key_unique))

    # We will have 420 dups (250 + 100 + 50 + 20)
    search_key_dup_occ1 = random.choices(search_key_dup_temp, k=250)
    search_key_dup_occ2 = random.choices(search_key_dup_occ1, k=100)
    search_key_dup_occ3 = random.choices(search_key_dup_occ2, k=50)
    search_key_dup_occ4 = random.choices(search_key_dup_occ3, k=20)
    search_key_dup = search_key_dup_occ1 + search_key_dup_occ2 + \
        search_key_dup_occ3 + search_key_dup_occ4

    search_key_not_present = random.sample(range(100000001, 200000000), 900)
    search_keys = search_key_unique + search_key_dup + search_key_not_present

    # print(len(search_keys))
    # print(len(insert_keys))

    return insert_keys, search_keys


def create_insert_search_mixed_seq(insert_keys, search_keys):
    insert_seq = [("I", i) for i in insert_keys]
    search_seq = [("S", i) for i in search_keys]

    insert_search_seq = insert_seq + search_seq
    random.shuffle(insert_search_seq)
    return insert_search_seq


class HopCounter:
    count = 0

    def increment(self):
        self.count += 1


if __name__ == '__main__':
    main()
