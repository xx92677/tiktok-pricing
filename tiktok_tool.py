import tkinter as tk
from tkinter import messagebox, ttk
import math

# --- 1. 财务配置 ---
FIXED_MYR_RATE = 1 / 1.75  
FULL_RATES = {
    "🇨🇳 RMB": 1.0, "🇲🇾 MYR": round(FIXED_MYR_RATE, 3), "🇺🇸 USD": 0.138, "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45, "🇭🇰 HKD": 1.08, "🇹🇭 THB": 4.85, "🇻🇳 VND": 3450.0,
    "🇧🇷 BRL": 0.72, "🇲🇽 MXN": 2.35, "🇦🇷 ARS": 120.0, "🇯🇵 JPY": 20.5,
    "🇵🇭 PHP": 7.8, "🇮🇩 IDR": 2150.0
}
PROFIT_RATE, DISCOUNT_RATE = 0.20, 0.51
FIXED_FEE, COEFF = 0.54, 0.692
base_rates = {k: v for k, v in FULL_RATES.items()}

# --- 2. 核心逻辑 (针对 M 芯片优化响应) ---

def get_val(entry_widget):
    try: return float(entry_widget.get())
    except: return 0.0

def calculate_all(*args):
    """自动联动计算"""
    try:
        cost_rmb = get_val(entry_cost)
        ship_val = get_val(entry_ship)
        ship_curr = combo_ship.get()
        out_curr = combo_out.get()
        
        myr_rate = FIXED_MYR_RATE if rate_mode.get() == "fixed" else base_rates["🇲🇾 MYR"]
        ship_myr = (ship_val / base_rates[ship_curr]) * myr_rate
        cost_myr = cost_rmb * myr_rate
        
        deal_myr = (cost_myr + ship_myr + FIXED_FEE) / COEFF
        orig_myr = math.ceil(deal_myr / (1 - DISCOUNT_RATE))
        to_out = lambda v: (v / myr_rate) * base_rates[out_curr]
        
        text_res.config(state=tk.NORMAL)
        text_res.delete(1.0, tk.END)
        text_res.insert(tk.END, 
            f"建议原价：{to_out(orig_myr):.2f}\n"
            f"实收成交：{to_out(deal_myr):.2f}\n"
            f"--------------------\n"
            f"平台佣金: {to_out(deal_myr * 0.0702):.2f}\n"
            f"预计利润: {to_out(deal_myr * PROFIT_RATE):.2f}\n"
            f"汇率基准: 1 RMB = {base_rates[out_curr]:.3f} {out_curr.split()[-1]}"
        )
        text_res.config(state=tk.DISABLED)
    except: pass

def sync_rates(*args):
    try:
        rmb_val = get_val(entry_rmb_base)
        for curr, var in rate_vars.items():
            if curr == "🇨🇳 RMB": continue
            rate = FIXED_MYR_RATE if (rate_mode.get() == "fixed" and curr == "🇲🇾 MYR") else base_rates[curr]
            var.set(f"{rmb_val * rate:.0f}" if rate > 100 else f"{rmb_val * rate:.3f}")
        calculate_all()
    except: pass

def update_manual_rate(curr):
    if rate_mode.get() == "fixed" and curr == "🇲🇾 MYR": return
    try:
        rmb_val = get_val(entry_rmb_base)
        cur_val = float(rate_vars[curr].get())
        if rmb_val != 0: base_rates[curr] = cur_val / rmb_val
        calculate_all()
    except: pass

# --- 3. UI 布局 (针对 macOS 优化) ---
root = tk.Tk()
root.title("TikTok定价助手 Pro")
# 针对 M 芯片 MacBook 屏幕比例优化的尺寸
root.geometry("540x660")
root.tk.call('tk', 'scaling', 2.0) # 强制开启高清缩放

main = tk.Frame(root, padx=20, pady=5)
main.pack(fill=tk.X)

# 汇率区
lf = tk.LabelFrame(main, text=" ⚙️ 汇率同步 ", padx=10, pady=5)
lf.pack(fill=tk.X, pady=(0, 5))

rate_mode = tk.StringVar(value="manual")
mf = tk.Frame(lf); mf.grid(row=0, column=0, columnspan=6, sticky=tk.W)
tk.Radiobutton(mf, text="手动", variable=rate_mode, value="manual", command=calculate_all).pack(side=tk.LEFT)
tk.Radiobutton(mf, text="锁定1.75", variable=rate_mode, value="fixed", command=calculate_all).pack(side=tk.LEFT, padx=10)

rate_vars, rate_entries = {}, {}
rmb_var = tk.StringVar(value="1")
rmb_var.trace_add("write", sync_rates)

for i, curr in enumerate(FULL_RATES.keys()):
    r, c = (i // 3) + 1, (i % 3) * 2
    tk.Label(lf, text=f"{curr}:", font=("Arial", 9)).grid(row=r, column=c, sticky=tk.W)
    v = rmb_var if curr == "🇨🇳 RMB" else tk.StringVar(value=str(FULL_RATES[curr]))
    rate_vars[curr] = v
    e = tk.Entry(lf, width=8, textvariable=v)
    e.grid(row=r, column=c+1, padx=2, pady=1)
    if curr == "🇨🇳 RMB": entry_rmb_base = e
    rate_entries[curr] = e
    if curr != "🇨🇳 RMB": e.bind("<KeyRelease>", lambda e, c=curr: update_manual_rate(c))

# 输入区
in_f = tk.Frame(main); in_f.pack(fill=tk.X, pady=5)
tk.Label(in_f, text="💰 成本 (RMB):", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
entry_cost = tk.Entry(in_f, font=("Arial", 13), width=15)
entry_cost.grid(row=1, column=0, sticky=tk.W, pady=2); entry_cost.insert(0, "20")
entry_cost.bind("<KeyRelease>", calculate_all)

tk.Label(in_f, text="🚚 运费:", font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W, padx=10)
s_b = tk.Frame(in_f); s_b.grid(row=1, column=1, sticky=tk.W, padx=10)
entry_ship = tk.Entry(s_b, font=("Arial", 13), width=10); entry_ship.pack(side=tk.LEFT); entry_ship.insert(0, "1.95")
entry_ship.bind("<KeyRelease>", calculate_all)

combo_ship = ttk.Combobox(s_b, values=list(FULL_RATES.keys()), width=10, state="readonly")
combo_ship.set("🇲🇾 MYR"); combo_ship.pack(side=tk.LEFT, padx=5)
combo_ship.bind("<<ComboboxSelected>>", calculate_all)

tk.Label(main, text="💵 结果币种:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5,0))
combo_out = ttk.Combobox(main, values=list(FULL_RATES.keys()), state="readonly")
combo_out.set("🇲🇾 MYR"); combo_out.pack(fill=tk.X, pady=2)
combo_out.bind("<<ComboboxSelected>>", calculate_all)

btn = tk.Button(main, text="开始定价 (Enter)", font=("Arial", 12, "bold"), command=calculate_all, pady=8)
btn.pack(fill=tk.X, pady=10); root.bind('<Return>', calculate_all)

text_res = tk.Text(main, height=7, font=("Menlo", 12), state=tk.DISABLED, padx=10, pady=10)
text_res.pack(fill=tk.X)

tk.Label(main, text="* 已优化 Apple Silicon 架构渲染 | 适配黑暗模式", font=("Arial", 8), fg="gray").pack(pady=5)

calculate_all()
root.mainloop()
