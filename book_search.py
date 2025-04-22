import gzip
import json
import time
import sys
import tracemalloc
import tkinter as tk
from tkinter import ttk
sys.setrecursionlimit(10000)

# -------------------- DATA STRUCTURES --------------------

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.entries = []

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, entry):
        cur = self.root
        for ch in word:
            if ch not in cur.children:
                cur.children[ch] = TrieNode()
            cur = cur.children[ch]
        cur.is_end = True
        cur.entries.append(entry)

    def search(self, query):
        node = self.root
        for ch in query:
            if ch not in node.children:
                return []
            node = node.children[ch]
        results = []
        self._collect_all(node, results)
        return results

    def _collect_all(self, node, results):
        if node.is_end:
            results.extend(node.entries)
        for child in node.children.values():
            self._collect_all(child, results)

class TSTNode:
    def __init__(self, char):
        self.char = char
        self.left = self.eq = self.right = None
        self.is_end = False
        self.entries = []

class TernarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, word, entry):
        self.root = self._insert(self.root, word, 0, entry)

    def _insert(self, node, word, index, entry):
        char = word[index]
        if not node:
            node = TSTNode(char)
        if char < node.char:
            node.left = self._insert(node.left, word, index, entry)
        elif char > node.char:
            node.right = self._insert(node.right, word, index, entry)
        else:
            if index + 1 < len(word):
                node.eq = self._insert(node.eq, word, index + 1, entry)
            else:
                node.is_end = True
                node.entries.append(entry)
        return node

    def search(self, query):
        node = self._traverse_to_node(self.root, query, 0)
        results = []
        if node:
            self._collect_all(node, results)
        return results

    def _traverse_to_node(self, node, word, index):
        if not node or index >= len(word):
            return None
        char = word[index]
        if char < node.char:
            return self._traverse_to_node(node.left, word, index)
        elif char > node.char:
            return self._traverse_to_node(node.right, word, index)
        else:
            if index + 1 == len(word):
                return node  
            return self._traverse_to_node(node.eq, word, index + 1)

    def _collect_all(self, node, results):
        if node is None:
            return
        self._collect_all(node.left, results)
        if node.is_end:
            results.extend(node.entries)
        self._collect_all(node.eq, results)
        self._collect_all(node.right, results)
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

# ---------------------------------------- GUI FUNCTION ----------------------------------------


def create_gui(path):
    entries = load_entries(path)
    trie = Trie()
    tst = TernarySearchTree()
    for entry in entries:
        if entry.get("title"):
            for word in entry["title"].lower().split():
                trie.insert(word, entry)
                tst.insert(word, entry)
        if entry.get("author"):
            for word in entry["author"].lower().split():
                trie.insert(word, entry)
                tst.insert(word, entry)

    root = tk.Tk()
    root.title("Project 3")
    root.geometry("1500x900")
    root.configure(bg="#ebf2f5")

    # -------------------------- Header --------------------------

    header_frame = tk.Frame(root, bg="#84afbd")
    header_frame.pack(fill="x")
    header_label = tk.Label(header_frame, text="Book Search", bg="#84afbd", fg="white",font=("Segoe UI", 16, "bold"), pady=10)
    header_label.pack(fill="x")

    # -------------------------- Top Frame --------------------------

    top_frame = tk.Frame(root, bg="#ebf2f5")
    top_frame.pack(pady=15, padx=150, fill="x")

    style = ttk.Style()
    style.configure("Rounded.TCombobox",relief="flat",borderwidth=0,arrowsize=12,padding=5,background="#ffffff",fieldbackground="#ffffff", foreground="#4d4d4d")

    trie_time_var = tk.StringVar(value="Trie: ")
    tst_time_var = tk.StringVar(value="TST: ")

    tk.Label(top_frame, textvariable=trie_time_var, foreground="#137a7f", bg="#ebf2f5", font=("Segoe UI", 10)).grid(row=0, column=2, padx=5, sticky="w")
    tk.Label(top_frame, textvariable=tst_time_var, foreground="#e12885", bg="#ebf2f5", font=("Segoe UI", 10)).grid(row=0, column=3, padx=5, sticky="w")


    # -------------------------- Mid Frame with Canvas for Rounded Entry --------------------------

    mid_frame = tk.Frame(root, bg="#ebf2f5")
    mid_frame.pack(pady=10, padx=150, fill="x")

    search_term = tk.StringVar()

    search_container = tk.Frame(mid_frame, bg="#ebf2f5")
    search_container.pack(fill="x",pady=15)

    entry_canvas_frame = tk.Frame(search_container, bg="#ebf2f5")
    entry_canvas_frame.pack(side="left", padx=(0, 10))

    canvas_entry = tk.Canvas(entry_canvas_frame, width = 1100,height=40, bg="#ebf2f5", highlightthickness=0)
    canvas_entry.pack(side="left", padx=(0, 10))

    canvas_entry.bind("<Configure>", lambda e: draw_rounded_entry(canvas_entry, e.width, 40))

    search_entry = tk.Entry(entry_canvas_frame,width = 1100,textvariable=search_term, bd=0, font=("Segoe UI", 11), bg="white")
    search_entry.place(relx=0.02, rely=0.15, relwidth=0.96, height=25)

    button_frame = tk.Frame(search_container, bg="#ebf2f5")
    button_frame.pack(side="left")


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


    suggestion_frame = tk.Frame(mid_frame, bg="#ebf2f5")
    suggestion_frame.config(bg="#ebf2f5",bd=0)
    suggestion_frame.pack(fill="x", pady=(10))

    suggestion_buttons = []


    # ------------- Auto Suggestions Functions -------------


    def autofill_and_search(match):
        search_term.set(match['title'].split()[0].lower())
        clear_suggestions()
        perform_search()

    def clear_suggestions():
        for btn in suggestion_buttons:
            btn.destroy()
        suggestion_buttons.clear()
        suggestion_frame.pack_forget()



    def show_suggestions(query):
        for btn in suggestion_buttons:
            btn.destroy()
        suggestion_buttons.clear()
        suggestion_frame.pack_forget()

        if not query or query == placeholder_text.lower():
            return

        matches = [
            entry for entry in entries
            if query in entry['title'].lower() or query in entry['author'].lower()
        ][:3]

        suggestion_frame.pack(fill="x", pady=(10))

        for match in matches[:3]:
            text = f"{match['title']} - {match['author'] or 'Unknown'}"
            btn = tk.Button(suggestion_frame, text=text, anchor="w", font=("Segoe UI", 9),bg="white", fg="#4d4d4d", bd=0, relief="solid",command=lambda m=match: autofill_and_search(m))
            btn.bind("<Enter>", lambda e: e.widget.config(bg="#d5dce0"))
            btn.bind("<Leave>", lambda e: e.widget.config(bg="white"))
            btn.pack(fill="x", padx=2, pady=0)
            suggestion_buttons.append(btn)




    # ------------- UI Search Logic -----------------

    def perform_search(event=None):
        query = search_term.get().strip().lower()
        clear_suggestions()
        if not query or query == placeholder_text:
            return

        runs = 1000
        durations_trie = []
        durations_tst = []
        total_memory_trie = 0
        total_memory_tst = 0

        # TRIE
        tracemalloc.start()
        for _ in range(runs):
            start = time.perf_counter_ns()
            trie_matches = trie.search(query)
            end = time.perf_counter_ns()
            durations_trie.append((end - start) / 1_000_000)
            _, peak = tracemalloc.get_traced_memory()
            total_memory_trie += peak
        tracemalloc.stop()

        # TST
        tracemalloc.start()
        for _ in range(runs):
            start = time.perf_counter_ns()
            tst_matches = tst.search(query)
            end = time.perf_counter_ns()
            durations_tst.append((end - start) / 1_000_000)
            _, peak = tracemalloc.get_traced_memory()
            total_memory_tst += peak
        tracemalloc.stop()

        # Display
        trie_results_box.delete(0, tk.END)
        tst_results_box.delete(0, tk.END)

        for match in trie_matches[:1000]:
            trie_results_box.insert(tk.END, f"Title: {match['title']}")
            trie_results_box.insert(tk.END, f"Author: {match['author']}")
            trie_results_box.insert(tk.END, "-" * 40)

        for match in tst_matches[:1000]:
            tst_results_box.insert(tk.END, f"Title: {match['title']}")
            tst_results_box.insert(tk.END, f"Author: {match['author']}")
            tst_results_box.insert(tk.END, "-" * 40)

        # Timings + memory
        avg_time_trie = sum(durations_trie) / runs
        avg_time_tst = sum(durations_tst) / runs
        total_time_trie = sum(durations_trie)
        total_time_tst = sum(durations_tst)
        avg_mem_trie = total_memory_trie / runs / 1024
        avg_mem_tst = total_memory_tst / runs / 1024
        total_mem_trie = total_memory_trie / 1024
        total_mem_tst = total_memory_tst / 1024

        trie_time_var.set(f"Trie: {avg_time_trie:.4f} ms avg, {total_time_trie:.4f} ms total | {avg_mem_trie:.2f} KB avg, {total_mem_trie:.2f} KB total")
        tst_time_var.set(f"TST:  {avg_time_tst:.4f} ms avg, {total_time_tst:.4f} ms total | {avg_mem_tst:.2f} KB avg, {total_mem_tst:.2f} KB total")

    # ------------- UI Rounded Canvas Function -----------------

    def draw_rounded_entry(canvas, width, height):
        canvas.delete("all")
        r = 20
        canvas.create_arc(0, 0, r*2, r*2, start=90, extent=90, fill="white", outline="white")
        canvas.create_arc(width - r*2, 0, width, r*2, start=0, extent=90, fill="white", outline="white")
        canvas.create_arc(width - r*2, height - r*2, width, height, start=270, extent=90, fill="white", outline="white")
        canvas.create_arc(0, height - r*2, r*2, height, start=180, extent=90, fill="white", outline="white")
        canvas.create_rectangle(r, 0, width - r, height, fill="white", outline="white")
        canvas.create_rectangle(0, r, width, height - r, fill="white", outline="white")



# -------------------------- Bottom Frame --------------------------


    bottom_frame = tk.Frame(root, bg="#ebf2f5")
    bottom_frame.pack(fill="both", expand=True, padx=50, pady=15)

    # ------------- Result Box -------------
    bottom_frame.rowconfigure(0, weight=1)
    bottom_frame.columnconfigure(0, weight=1)

    trie_results_box = tk.Listbox(bottom_frame, bd=0, highlightthickness=0, relief="flat",font=("Courier New", 10), background="#ebf2f5", foreground="#137a7f")
    trie_results_box.grid(row=0, column=0, sticky="nsew", padx=(0, 25), pady=10)

    tst_results_box = tk.Listbox(bottom_frame, bd=0, highlightthickness=0, relief="flat",font=("Courier New", 10), background="#ebf2f5", foreground="#e12885")
    tst_results_box.grid(row=0, column=1, sticky="nsew", padx=(25, 0), pady=10)


# -------------------------- Binding Events --------------------------

    def on_key_release(event):
        if event.keysym != "Return":
            show_suggestions(search_term.get().strip().lower())


    search_entry.bind("<Return>", perform_search)
    search_entry.bind("<KeyRelease>", on_key_release)
    root.mainloop()

create_gui("fulldata.json.gz") #change to your path
