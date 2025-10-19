import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List

from .recommend import analyze_and_rank, analyze_and_rank_with_loader
from .utils import discover_symbols, parse_symbols, validate_and_suggest


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Stock Trend Advisor")
        self.geometry("900x600")
        # Defaults for cache/throttle options
        self.throttle_ms = 400
        self.ttl_hours = 24

        self._build_controls()
        self._build_table()

    def _build_controls(self) -> None:
        # Section 1: Source & Symbols
        src_frm = ttk.LabelFrame(self, text="1. Source & Symbols", padding=10)
        src_frm.pack(fill=tk.X, padx=8, pady=(8, 4))

        ttk.Label(src_frm, text="Source:").grid(row=0, column=0, sticky=tk.W)
        self.source_var = tk.StringVar(value="yahoo")
        self.source_cmb = ttk.Combobox(src_frm, textvariable=self.source_var, values=["yahoo", "alphavantage", "csv"], state="readonly", width=14)
        self.source_cmb.grid(row=0, column=1, sticky=tk.W)
        self.source_cmb.bind("<<ComboboxSelected>>", lambda _e: self._toggle_controls())

        ttk.Label(src_frm, text="API Key:").grid(row=0, column=2, sticky=tk.W, padx=(12, 0))
        self.apikey_var = tk.StringVar(value="")
        self.apikey_ent = ttk.Entry(src_frm, textvariable=self.apikey_var, width=28, show="*")
        self.apikey_ent.grid(row=0, column=3, sticky=tk.W)

        ttk.Label(src_frm, text="Preset:").grid(row=0, column=4, sticky=tk.W, padx=(12, 0))
        self.preset_var = tk.StringVar(value="S&P 100")
        self.preset_cmb = ttk.Combobox(src_frm, textvariable=self.preset_var, values=["S&P 100", "NASDAQ 100"], state="readonly", width=14)
        self.preset_cmb.grid(row=0, column=5, sticky=tk.W)

        ttk.Label(src_frm, text="Auto Count:").grid(row=0, column=6, sticky=tk.W, padx=(12, 0))
        self.auto_count_var = tk.StringVar(value="20")
        self.auto_count_cmb = ttk.Combobox(src_frm, textvariable=self.auto_count_var, values=["20", "50", "80", "All"], state="readonly", width=8)
        self.auto_count_cmb.grid(row=0, column=7, sticky=tk.W)

        self.btn_auto_yahoo = ttk.Button(src_frm, text="Auto (Yahoo)", command=self._auto_yahoo)
        self.btn_auto_yahoo.grid(row=0, column=8, padx=(8, 0))
        self.btn_auto_api = ttk.Button(src_frm, text="Auto (API)", command=self._auto_api)
        self.btn_auto_api.grid(row=0, column=9, padx=(8, 0))

        ttk.Label(src_frm, text="Symbols (optional):").grid(row=1, column=0, sticky=tk.W, pady=(8, 0))
        self.symbols_var = tk.StringVar(value="")
        self.symbols_ent = ttk.Entry(src_frm, textvariable=self.symbols_var, width=50)
        self.symbols_ent.grid(row=1, column=1, columnspan=3, sticky=tk.W, pady=(8, 0))

        ttk.Label(src_frm, text="Data Dir:").grid(row=1, column=4, sticky=tk.W, pady=(8, 0))
        self.data_dir_var = tk.StringVar(value="data")
        self.data_dir_ent = ttk.Entry(src_frm, textvariable=self.data_dir_var, width=28)
        self.data_dir_ent.grid(row=1, column=5, sticky=tk.W, pady=(8, 0))
        self.btn_browse = ttk.Button(src_frm, text="Browse", command=self._browse_dir)
        self.btn_browse.grid(row=1, column=6, padx=5, pady=(8, 0))
        self.btn_discover = ttk.Button(src_frm, text="Discover", command=self._discover)
        self.btn_discover.grid(row=1, column=7, pady=(8, 0))

        for c in range(0, 10):
            src_frm.grid_columnconfigure(c, weight=0)
        src_frm.grid_columnconfigure(1, weight=1)

        # Section 2: Parameters
        prm_frm = ttk.LabelFrame(self, text="2. Strategy Parameters", padding=10)
        prm_frm.pack(fill=tk.X, padx=8, pady=(0, 4))

        ttk.Label(prm_frm, text="Fast SMA:").grid(row=0, column=0, sticky=tk.W)
        self.fast_var = tk.IntVar(value=50)
        ttk.Spinbox(prm_frm, from_=2, to=1000, textvariable=self.fast_var, width=8).grid(row=0, column=1, sticky=tk.W)

        ttk.Label(prm_frm, text="Slow SMA:").grid(row=0, column=2, sticky=tk.W)
        self.slow_var = tk.IntVar(value=200)
        ttk.Spinbox(prm_frm, from_=2, to=2000, textvariable=self.slow_var, width=8).grid(row=0, column=3, sticky=tk.W)

        ttk.Label(prm_frm, text="Top N:").grid(row=0, column=4, sticky=tk.W, padx=(12, 0))
        self.top_var = tk.IntVar(value=10)
        ttk.Spinbox(prm_frm, from_=1, to=500, textvariable=self.top_var, width=8).grid(row=0, column=5, sticky=tk.W)

        # Section 3: Actions
        act_frm = ttk.LabelFrame(self, text="3. Analyze", padding=10)
        act_frm.pack(fill=tk.X, padx=8, pady=(0, 6))

        ttk.Button(act_frm, text="Analyze", command=self._analyze).grid(row=0, column=0, padx=(0, 8))
        self.only_buy_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(act_frm, text="Show BUY only", variable=self.only_buy_var).grid(row=0, column=1, sticky=tk.W)
        ttk.Button(act_frm, text="Columns", command=self._show_columns_help).grid(row=0, column=2, padx=(8, 0))
        ttk.Button(act_frm, text="Options", command=self._open_options).grid(row=0, column=3, padx=(8, 0))

        # Status
        self.status_var = tk.StringVar(value="Ready")
        self.status_lbl = ttk.Label(self, textvariable=self.status_var, anchor=tk.W)
        self.status_lbl.pack(fill=tk.X, padx=10, pady=4)

        # Initialize control states
        self._toggle_controls()

    def _build_table(self) -> None:
        columns = ("symbol", "score", "decision", "last_close", "dist200", "slope50", "last_signal")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("symbol", text="Symbol")
        self.tree.heading("score", text="Score")
        self.tree.heading("decision", text="Decision")
        self.tree.heading("last_close", text="Last Close")
        self.tree.heading("dist200", text="Dist 200SMA %")
        self.tree.heading("slope50", text="50SMA Slope")
        self.tree.heading("last_signal", text="Last Signal")

        self.tree.column("symbol", width=90, anchor=tk.W)
        self.tree.column("score", width=80, anchor=tk.E)
        self.tree.column("decision", width=100, anchor=tk.W)
        self.tree.column("last_close", width=100, anchor=tk.E)
        self.tree.column("dist200", width=120, anchor=tk.E)
        self.tree.column("slope50", width=110, anchor=tk.E)
        self.tree.column("last_signal", width=100, anchor=tk.W)

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 10))
        vsb.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=(0, 10))

        # Striped rows and sortable columns
        try:
            style = ttk.Style(self)
            if "clam" in style.theme_names():
                style.theme_use("clam")
        except Exception:
            pass

        self.tree.tag_configure("odd", background="#f7f7f7")
        self.tree.tag_configure("even", background="#ffffff")

        for col in columns:
            self.tree.heading(col, text=self.tree.heading(col, option="text"), command=lambda c=col: self._sort_by(c, False))

    def _browse_dir(self) -> None:
        path = filedialog.askdirectory(initialdir=self.data_dir_var.get() or ".")
        if path:
            self.data_dir_var.set(path)

    def _toggle_controls(self) -> None:
        src = self.source_var.get()
        # API key field
        self.apikey_ent.configure(state=("normal" if src == "alphavantage" else "disabled"))
        # Discover and data dir for CSV only
        csv_only = (src == "csv")
        self.data_dir_ent.configure(state=("normal" if csv_only else "disabled"))
        self.btn_discover.configure(state=("normal" if csv_only else "disabled"))
        self.btn_browse.configure(state=("normal" if csv_only else "disabled"))
        # Auto controls
        self.btn_auto_api.configure(state=("normal" if src == "alphavantage" else "disabled"))
        self.btn_auto_yahoo.configure(state=("normal" if src == "yahoo" else "disabled"))
        self.auto_count_cmb.configure(state=("readonly" if src == "yahoo" else "disabled"))
        self.preset_cmb.configure(state=("readonly" if src == "yahoo" else "disabled"))

    def _discover(self) -> None:
        data_dir = self.data_dir_var.get().strip()
        if self.source_var.get() != "csv":
            messagebox.showinfo("Discover Symbols", "Discovery works only for CSV source.")
            return
        syms = discover_symbols(data_dir)
        if not syms:
            messagebox.showinfo("Discover Symbols", f"No CSV files found in: {data_dir}")
            return
        self.symbols_var.set(",".join(syms))
        self.status_var.set(f"Discovered {len(syms)} symbols")

    def _auto_api(self) -> None:
        if self.source_var.get() != "alphavantage":
            messagebox.showinfo("Auto (API)", "Set Source to 'alphavantage' and provide an API key.")
            return
        key = (self.apikey_var.get().strip() or "")
        if not key:
            messagebox.showwarning("API Key", "Please enter your Alpha Vantage API key.")
            return
        self.status_var.set("Fetching symbols from API...")
        self.update_idletasks()
        try:
            from .data.alpha_vantage import list_symbols_alphavantage
            # Keep it small due to rate limits
            syms = list_symbols_alphavantage(key, state="active", max_symbols=10, exchanges=["NYSE", "NASDAQ"]) or []
        except Exception:
            syms = []
        if not syms:
            messagebox.showwarning("Auto (API)", "Could not fetch symbols (rate limit or network). Try again in ~60s.")
            self.status_var.set("Ready")
            return
        self.symbols_var.set(",".join(syms))
        self.status_var.set(f"Fetched {len(syms)} symbols from API")

    def _analyze(self) -> None:
        data_dir = self.data_dir_var.get().strip()
        symbols_text = self.symbols_var.get().strip()
        if symbols_text:
            symbols: List[str] = parse_symbols(symbols_text)
        else:
            symbols = [] if self.source_var.get() != "csv" else discover_symbols(data_dir)

        if not symbols:
            if self.source_var.get() == "yahoo":
                try:
                    from .universe import get_preset
                    count_val = (self.auto_count_var.get() or "20").strip()
                    max_syms = 1000 if count_val.lower() == "all" else max(1, int(count_val))
                    symbols = get_preset(self.preset_var.get())[: max_syms]
                except Exception:
                    symbols = []
            if not symbols:
                messagebox.showwarning("Analyze", "No symbols to analyze. Enter symbols or use Auto buttons.")
                return

        # If using demo API key, suggest MSFT-only
        if self.source_var.get() == "alphavantage" and (self.apikey_var.get().strip() or "").lower() == "demo":
            non_msft = [s for s in symbols if s != "MSFT"]
            if non_msft:
                if messagebox.askyesno(
                    "Demo key limitation",
                    "The Alpha Vantage demo key only returns data for MSFT.\n\n"
                    "Click Yes to analyze MSFT now, or No to keep your list."
                ):
                    symbols = ["MSFT"]

        # Validate and suggest fixes for unusual symbols
        valid_syms, issues = validate_and_suggest(symbols)
        if issues:
            lines = []
            for raw, sug in issues:
                if sug:
                    lines.append(f"{raw} -> {sug}")
                else:
                    lines.append(f"{raw} (no suggestion)")
            if any(sug for _, sug in issues):
                if messagebox.askyesno(
                    "Symbol check",
                    "Some symbols look unusual. Apply suggested fixes?\n\n" + "\n".join(lines)
                ):
                    mapped = {}
                    for raw, sug in issues:
                        if sug:
                            mapped[raw] = sug
                    symbols = [mapped.get(s, s) for s in symbols]
                else:
                    symbols = valid_syms + [raw for raw, sug in issues if not sug]
            else:
                symbols = valid_syms + [raw for raw, _ in issues]

        try:
            fast = int(self.fast_var.get())
            slow = int(self.slow_var.get())
            top = int(self.top_var.get())
        except Exception:
            messagebox.showerror("Parameters", "Fast/Slow/Top must be integers.")
            return

        self.status_var.set("Analyzing...")
        self.update_idletasks()

        # Build loader and analyze
        from .data.provider import get_loader
        loader = get_loader(self.source_var.get(), data_dir=data_dir, api_key=self.apikey_var.get().strip())
        # Add cache + throttle
        try:
            from .data.cache import make_cached_loader
            loader = make_cached_loader(loader, source=self.source_var.get(), cache_dir=".cache", ttl_hours=self.ttl_hours, throttle_ms=self.throttle_ms)
        except Exception:
            pass
        ranked = analyze_and_rank_with_loader(symbols, loader, fast=fast, slow=slow)
        if self.only_buy_var.get():
            ranked = [r for r in ranked if (r.get("meta", {}).get("decision") == "BUY")]

        # Clear table
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        # Populate
        for item in ranked[: top]:
            meta = item["meta"]
            last_close = meta.get("last_close")
            dist200 = meta.get("dist_200sma_pct")
            slope50 = meta.get("sma50_slope")
            last_signal = meta.get("last_signal") or "none"
            decision = meta.get("decision") or "DON'T BUY"

            def fmt(v, f):
                return f.format(v) if isinstance(v, (int, float)) else "nan"

            row = (
                item["symbol"],
                f"{item['score']:.3f}",
                decision,
                fmt(last_close, "{:.2f}"),
                fmt(dist200, "{:.2f}"),
                fmt(slope50, "{:.4f}"),
                last_signal,
            )
            tag = "even" if (len(self.tree.get_children()) % 2 == 0) else "odd"
            self.tree.insert("", tk.END, values=row, tags=(tag,))

        self.status_var.set(f"Done. Shown {min(top, len(ranked))} of {len(ranked)} symbols.")
        if len(ranked) == 0 and len(symbols) > 0:
            # Provide a targeted diagnostic for Alpha Vantage
            if self.source_var.get() == "alphavantage":
                try:
                    from .data.alpha_vantage import probe_alphavantage
                    probe = probe_alphavantage(symbols[0], self.apikey_var.get().strip() or "")
                    status = probe.get("status", "error")
                    msg = probe.get("message", "Unknown error")
                    extra = ""
                    if probe.get("keys"):
                        extra = f"\nKeys: {probe.get('keys')}"
                    if probe.get("raw"):
                        extra += f"\nRaw: {probe.get('raw')}"
                    messagebox.showwarning(
                        "No Data",
                        f"Alpha Vantage returned no data for {symbols[0]}\n\n"
                        f"Status: {status}\nMessage: {msg}{extra}\n\n"
                        "Tips: 1) Use demo+MSFT for a quick test, 2) one symbol at a time,\n"
                        "3) wait 60s (rate limits), 4) verify API key and internet connectivity."
                    )
                except Exception:
                    messagebox.showwarning(
                        "No Data",
                        "Alpha Vantage returned no data for the requested symbols.\n\n"
                        "Try: 1) testing with demo key + MSFT, 2) one symbol at a time,\n"
                        "3) wait 60s (rate limits), 4) verify API key and internet connectivity."
                    )
            elif self.source_var.get() == "yahoo":
                try:
                    from .data.yahoo import probe_yahoo
                    probe = probe_yahoo(symbols[0])
                    status = probe.get("status", "error")
                    msg = probe.get("message", "Unknown error")
                    host = probe.get("host", "query1")
                    messagebox.showwarning(
                        "No Data",
                        f"Yahoo returned no data for {symbols[0]}\n\n"
                        f"Status: {status}\nMessage: {msg}\nHost: {host}\n\n"
                        "Tips: 1) Try a single liquid ticker like MSFT, 2) wait 30s to avoid limits,\n"
                        "3) check network/proxy settings, 4) try CSV files if blocked."
                    )
                except Exception:
                    messagebox.showwarning(
                        "No Data",
                        "Yahoo returned no data. Try a single symbol (e.g., MSFT), wait briefly, or check network."
                    )

    def _open_options(self) -> None:
        win = tk.Toplevel(self)
        win.title("Options")
        win.transient(self)
        ttk.Label(win, text="Cache TTL (hours):").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        ttl_var = tk.IntVar(value=self.ttl_hours)
        ttk.Spinbox(win, from_=1, to=168, textvariable=ttl_var, width=8).grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(win, text="Throttle (ms per request):").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        thr_var = tk.IntVar(value=self.throttle_ms)
        ttk.Spinbox(win, from_=0, to=5000, textvariable=thr_var, width=8).grid(row=1, column=1, padx=10, pady=10)

        def save_close() -> None:
            try:
                self.ttl_hours = int(ttl_var.get())
                self.throttle_ms = int(thr_var.get())
                self.status_var.set(f"Options saved: TTL={self.ttl_hours}h, throttle={self.throttle_ms}ms")
            except Exception:
                messagebox.showerror("Options", "Invalid values.")
                return
            win.destroy()

        ttk.Button(win, text="Save", command=save_close).grid(row=2, column=0, padx=10, pady=10)
        ttk.Button(win, text="Cancel", command=win.destroy).grid(row=2, column=1, padx=10, pady=10)

    def _auto_yahoo(self) -> None:
        if self.source_var.get() != "yahoo":
            messagebox.showinfo("Auto (Yahoo)", "Set Source to 'yahoo' to use this.")
            return
        count_val = (self.auto_count_var.get() or "20").strip()
        max_syms = 1000 if count_val.lower() == "all" else max(1, int(count_val))
        try:
            from .universe import get_preset
            syms = get_preset(self.preset_var.get())[: max_syms]
        except Exception:
            from .data.provider import get_universe
            syms = get_universe("yahoo", max_symbols=max_syms)
        if not syms:
            messagebox.showwarning("Auto (Yahoo)", "Could not load preset universe.")
            return
        self.symbols_var.set(",".join(syms))
        self.status_var.set(f"Loaded {len(syms)} Yahoo preset symbols")

    def _show_columns_help(self) -> None:
        messagebox.showinfo(
            "Columns",
            "Symbol: Ticker symbol.\n"
            "Score: Composite score from crossover recency, price vs 200SMA, and 50SMA slope (higher is better).\n"
            "Decision: BUY if 2/3 checks pass (bullish crossover, above 200SMA, 50SMA trending up); else DON'T BUY.\n"
            "Last Close: Most recent closing price.\n"
            "Dist 200SMA %: Percentage distance of price above/below 200-day SMA.\n"
            "50SMA Slope: Recent slope of 50-day SMA (positive = rising).\n"
            "Last Signal: Most recent SMA crossover event (bull/bear)."
        )

    def _sort_by(self, col: str, descending: bool) -> None:
        data = []
        for iid in self.tree.get_children(""):
            vals = self.tree.item(iid, "values")
            data.append((vals, iid))
        index_map = {"symbol": 0, "score": 1, "decision": 2, "last_close": 3, "dist200": 4, "slope50": 5, "last_signal": 6}
        idx = index_map.get(col, 0)

        def parse(v: str):
            try:
                return float(v)
            except Exception:
                return v

        data.sort(key=lambda x: parse(x[0][idx]), reverse=descending)
        for i, (_, iid) in enumerate(data):
            self.tree.move(iid, "", i)
        # Toggle sort order next time
        self.tree.heading(col, command=lambda c=col: self._sort_by(c, not descending))


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
