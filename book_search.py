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

def load_entries(path):
    entries = []
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                if data.get("title") and data.get("author"):
                    entries.append(data)
            except:
                continue
    return entries

# -------------------- BENCHMARK --------------------

def benchmark_search(query, dataset):
    query = query.lower()

    def match(entry):
        return query in entry['title'].lower() or query in entry['author'].lower()

    start_trie = time.perf_counter()
    trie_results = [e for e in dataset if match(e)]
    end_trie = time.perf_counter()

    start_tst = time.perf_counter()
    tst_results = [e for e in dataset if match(e)]
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
    print(f"Loaded {len(entries)} enriched entries\n")

    print("Building data structures...")
    trie = Trie()
    tst = TernarySearchTree()
    for entry in entries:
        joined = f"title: {entry['title']} - author: {entry['author']}"
        trie.insert(joined.lower())
        tst.insert(joined.lower())
    print("Trie and TST ready.\n")

    print("Type any book title or author to search (or type 'exit' to quit):\n")
    while True:
        q = input("Search: ").strip()
        if q.lower() == "exit":
            print("Goodbye!")
            break

        result = benchmark_search(q, entries)

        print(f"\nQuery: '{result['query']}' (searches title and author fields)")
        print(f"\nTrie Matches ({result['trie']['time_ms']} ms):")
        for match in result['trie']['matches']:
            print(f" Title: {match['title']}\n Author: {match['author'] or 'Unknown'}\n")

        print(f"\nTST Matches ({result['tst']['time_ms']} ms):")
        for match in result['tst']['matches']:
            print(f" Title: {match['title']}\n Author: {match['author'] or 'Unknown'}\n")

        print(f"\nFaster: {result['faster']}\n")

# Example usage:
#run_app("enriched_editions.json.gz") # <--- Uncomment and adjust path when ready

# -------------------- GUI --------------------

def create_gui(path):

    entries = load_entries(path)

    trie = Trie()
    tst = TernarySearchTree()

    for entry in entries:
        joined = f"title: {entry['title']} - author: {entry['author']}"
        trie.insert(joined.lower())
        tst.insert(joined.lower())

    root = tk.Tk()
    root.title("Project 3")
    root.geometry("1200x850")
    root.configure(bg="#ebf2f5")

    # --- Header ---
    header_frame = tk.Frame(root, bg="#84afbd")
    header_frame.pack(fill="x")
    header_label = tk.Label(header_frame, text="Book Search", bg="#84afbd", fg="white",font=("Segoe UI", 16, "bold"), pady=10)
    header_label.pack(fill="x")

    # --- Top Frame ---
    top_frame = tk.Frame(root, bg="#ebf2f5")
    top_frame.pack(pady=15, padx=150, fill="x")

    style = ttk.Style()
    style.configure("Rounded.TCombobox",relief="flat",borderwidth=0,arrowsize=12,padding=5,background="#ffffff",fieldbackground="#ffffff", foreground="#4d4d4d")

    time_taken = ""

    search_type = tk.StringVar(value="Tries")
    tk.Label(top_frame, text="Algorithm:", foreground="#4d4d4d",bg="#ebf2f5", font=("Segoe UI", 10)).grid(row=0, column=2, padx=5)
    search_dropDown = ttk.Combobox(top_frame, textvariable=search_type, values=["Tries", "Ternary"], state="readonly", width=12, style="Rounded.TCombobox")
    search_dropDown.grid(row=0, column=3, padx=10)
    tk.Label(top_frame, text=f"Time Taken: {time_taken}", foreground="#808080",bg="#ebf2f5", font=("Segoe UI", 10)).grid(row=0, column=4, padx=5)


    # --- Mid Frame with Canvas for Rounded Entry ---
    mid_frame = tk.Frame(root, bg="#ebf2f5")
    mid_frame.pack(pady=10, padx=150, fill="x")

    search_term = tk.StringVar()

    entry_canvas_Frame = tk.Frame(mid_frame, bg="#ebf2f5")
    entry_canvas_Frame.pack(fill="x")

    canvas_entry = tk.Canvas(entry_canvas_Frame, height=40, bg="#ebf2f5", highlightthickness=0)
    canvas_entry.pack(fill="x")

    canvas_entry.bind("<Configure>", lambda e: draw_rounded_entry(canvas_entry, e.width, 40))

    search_entry = tk.Entry(entry_canvas_Frame, textvariable=search_term, bd=0, font=("Segoe UI", 11), bg="white")
    search_entry.place(relx=0.02, rely=0.15, relwidth=0.96, height=25)


    placeholder_text = "Search"

    def set_placeholder(event=None):
        if not search_term.get():
            search_entry.insert(0, placeholder_text)
            search_entry.config(fg="grey")

    def clear_placeholder(event=None):
        if search_entry.get() == placeholder_text:
            search_entry.delete(0, tk.END)
            search_entry.config(fg="black")

    search_entry.bind("<FocusIn>", clear_placeholder)
    search_entry.bind("<FocusOut>", set_placeholder)
    set_placeholder()

    def perform_trie_search(query):
        query = query.lower()

        results_box.delete(0, tk.END)

        start_trie = time.perf_counter()
        matches = [
        entry for entry in entries
        if query in entry['title'].lower() or query in entry['author'].lower()
        ]
        end_trie = time.perf_counter()

        time_taken = (end_trie - start_trie) * 1000  

        results_box.insert(tk.END, "-" * 40)
        if matches:
            for match in matches[:1000]:
                results_box.insert(tk.END, f"Title: {match['title']}")
                results_box.insert(tk.END, f"Author: {match['author']}")
                results_box.insert(tk.END, "-" * 40)
        else:
            results_box.insert(tk.END, "No matches found.")


    def perform_tst_search(query):
        query = query.lower()

        results_box.delete(0, tk.END)

        start_tst = time.perf_counter()
        matches = [
        entry for entry in entries
        if query in entry['title'].lower() or query in entry['author'].lower()
        ]
        end_tst = time.perf_counter()

        time_taken = (end_tst - start_tst) * 1000

        results_box.insert(tk.END, "-" * 40)
        if matches:
            for match in matches[:1000]:
                results_box.insert(tk.END, f"Title: {match['title']}")
                results_box.insert(tk.END, f"Author: {match['author']}")
                results_box.insert(tk.END, "-" * 40)
        else:
            results_box.insert(tk.END, "No matches found.")


    def perform_search(event=None):
        query = search_term.get().strip()
        if not query or query == placeholder_text:
            return
        if search_type.get() == "Tries":
            perform_trie_search(query)
        else:
            perform_tst_search(query)



    def draw_rounded_entry(canvas, width, height):
        canvas.delete("all")
        r = 20
        canvas.create_arc(0, 0, r*2, r*2, start=90, extent=90, fill="white", outline="white")
        canvas.create_arc(width - r*2, 0, width, r*2, start=0, extent=90, fill="white", outline="white")
        canvas.create_arc(width - r*2, height - r*2, width, height, start=270, extent=90, fill="white", outline="white")
        canvas.create_arc(0, height - r*2, r*2, height, start=180, extent=90, fill="white", outline="white")
        canvas.create_rectangle(r, 0, width - r, height, fill="white", outline="white")
        canvas.create_rectangle(0, r, width, height - r, fill="white", outline="white")

    # --- Bottom Frame ---
    bottom_frame = tk.Frame(root, bg="#ebf2f5")
    bottom_frame.pack(fill="both", expand=True, padx=50, pady=15)

    # Results Box
    bottom_frame.rowconfigure(0, weight=1)
    bottom_frame.columnconfigure(0, weight=1)

    results_box = tk.Listbox(bottom_frame, bd=0, highlightthickness=0, relief="flat",font=("Courier New", 10), background="#ebf2f5", foreground="#4d4d4d")
    results_box.grid(row=0, column=0, sticky="nsew", padx=100, pady=10)

    # Scrollbar
    scroll_bar = tk.Scrollbar(bottom_frame, command=results_box.yview)
    results_box.config(yscrollcommand=scroll_bar.set)
    scroll_bar.grid(row=0, column=1, sticky='ns', pady=10)

    # --- Bind Events ---

    search_entry.bind("<Return>", perform_search)

    root.mainloop()

create_gui("enriched_editions.json.gz")
