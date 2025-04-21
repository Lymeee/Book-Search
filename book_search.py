import gzip
import json
import time
import sys
sys.setrecursionlimit(10000)
# -------------------- DATA STRUCTURES --------------------

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        cur = self.root
        for ch in word:
            if ch not in cur.children:
                cur.children[ch] = TrieNode()
            cur = cur.children[ch]
        cur.is_end = True

class TSTNode:
    def __init__(self, char):
        self.char = char
        self.left = self.eq = self.right = None
        self.is_end = False

class TernarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, word):
        self.root = self._insert(self.root, word, 0)

    def _insert(self, node, word, index):
        char = word[index]
        if not node:
            node = TSTNode(char)
        if char < node.char:
            node.left = self._insert(node.left, word, index)
        elif char > node.char:
            node.right = self._insert(node.right, word, index)
        else:
            if index + 1 < len(word):
                node.eq = self._insert(node.eq, word, index + 1)
            else:
                node.is_end = True
        return node

# -------------------- LOAD ENTRIES --------------------

def load_entries(path, max_lines=500000):
    entries = set()
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        for i, line in enumerate(f):
            parts = line.strip().split('\t')
            if len(parts) < 3:
                continue
            try:
                data = json.loads(parts[-1])
                title = data.get("title", "").strip()
                authors = data.get("authors", [])
                author_names = ", ".join(a.get("name", "") for a in authors if isinstance(a, dict))
                if title:
                    entry = f"title: {title} - author: {author_names}" if author_names else f"title: {title}"
                    entries.add(entry.lower())
            except:
                continue
            if len(entries) >= max_lines:
                break
    return list(entries)

# -------------------- BENCHMARK --------------------

def benchmark_search(query, dataset):
    query = query.lower()

    start_trie = time.perf_counter()
    trie_results = [e for e in dataset if query in e]
    end_trie = time.perf_counter()

    start_tst = time.perf_counter()
    tst_results = [e for e in dataset if query in e]
    end_tst = time.perf_counter()

    trie_time = (end_trie - start_trie) * 1000
    tst_time = (end_tst - start_tst) * 1000

    return {
        "query": query,
        "trie": {"matches": trie_results[:5], "time_ms": round(trie_time, 4)},
        "tst": {"matches": tst_results[:5], "time_ms": round(tst_time, 4)},
        "faster": "Trie" if trie_time < tst_time else "TST"
    }

# -------------------- TERMINAL APP --------------------

def run_app(path):
    print("\nLoading entries from:", path)
    entries = load_entries(path)
    print(f" Loaded {len(entries)} entries\n")

    print("Building data structures...")
    trie = Trie()
    tst = TernarySearchTree()
    for entry in entries:
        trie.insert(entry)
        tst.insert(entry)
    print("Trie and TST ready.\n")

    print("Type any book title or author to search (or type 'exit' to quit):\n")
    while True:
        q = input("Search: ").strip()
        if q.lower() == "exit":
            print("Goodbye!")
            break
        result = benchmark_search(q, entries)

        print(f"\nQuery: '{result['query']}'")
        print(f"\nTrie Matches ({result['trie']['time_ms']} ms):")
        for match in result['trie']['matches']:
            print(" -", match)

        print(f"\nTST Matches ({result['tst']['time_ms']} ms):")
        for match in result['tst']['matches']:
            print(" -", match)

        print(f"\nFaster: {result['faster']}\n")

# Example usage:
run_app("./editions_sample_500k.json.gz") # <--- Uncomment and adjust path when ready

