import tkinter as tk
from tkinter import messagebox, ttk
import math

# --- 1. 财务与汇率配置 ---
FIXED_MYR_RATE = 1 / 1.75  
FULL_RATES = {
    "🇨🇳 RMB": 1.0, "🇲🇾 MYR": round(FIXED_MYR_RATE, 3), "🇺🇸 USD": 0.138, "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45, "🇭🇰 HKD": 1.08, "🇹🇭 THB": 4.85, "🇻🇳 VND": 3450.0,
    "🇧🇷 BRL": 0.72, "🇲🇽 MXN": 2.35, "🇦🇷 ARS": 120.0, "🇯🇵 JPY": 20.5,
    "🇵🇭 PHP": 7.8, "🇮🇩 IDR": 2150.0
}

WECHAT_GREEN = "#07C160" # 微信标准绿
COMMISSION_RATE = 0.0702 # 佣金 7.02%
PROFIT_MARGIN = 0.20    # 目标净利润率 20%
FIXED_FEE_MYR = 0.54    # 平台固定费 0.54 MYR
TARGET_DISCOUNT = 0.51  # 目标折扣 51% (用于计算原价)

# 倒求系数 = 1 - 0.0702 - 0.20 = 0.7298
CALC_COEFF = 1 - COMMISSION_RATE - PROFIT_MARGIN 

base_rates = {k: v for k, v in FULL_RATES.items()}

# --- 2. 核心计算逻辑 ---

def get_val(entry_widget):
    try: return float(entry_widget.get())
    except: return 0.0

def calculate_all(*args):
    """根据成本和运费，倒求 20% 净利的售价"""
    try:
        cost_rmb = get_val(entry_cost)
        ship_val = get_val(entry_ship)
        ship_curr, out_curr = combo_ship.get(), combo_out.get()
        
        myr_rate = FIXED_MYR_RATE if rate_mode.get() == "fixed" else base_rates["🇲🇾 MYR"]
        
        # 1. 成本与运费全部折算为马币
        ship_myr = (ship_val / base_rates[ship_curr]) * myr_rate
        cost_myr = cost_rmb * myr_rate
        
        # 2. 核心倒求公式：折后售价 = (成本 + 运费 + 固定费) / 0.7298
        p_deal_myr = (cost_myr + ship_myr + FIXED_FEE_MYR) / CALC_COEFF
        
        # 3. 反推建议原价 (基于 51% 折扣)
        p_orig_myr = math.ceil(p_deal_myr / (1 - TARGET_DISCOUNT))
        
        # 4. 转换至输出币种
        to_out = lambda v: (v / myr_rate) * base_rates[out_curr]
        
        final_deal = to_out(p_deal_myr)
        final_profit = final_deal * PROFIT_MARGIN # 这里的利润是售价的 20%
        
        text_res.config(state=tk.NORMAL)
        text_res.delete(1.0, tk.END)
        text_res.insert(tk.END, 
            f"建议原价：{to_out(p_orig_myr):.2f}\n"
            f"折后售价：{final_deal:.2f}\n" 
            f"--------------------\n"
            f"佣金扣除 (7.02%): {final_deal * COMMISSION_RATE:.2f}\n"
            f"预计净利 (20.0%): {final_profit:.2f}\n"
            f"--------------------\n"
            f"汇率基准: 1 RMB = {base_rates[out_curr]:.3f} {out_curr.split()[-1]}"
        )
        text_res.config(state=tk.DISABLED)
    except: pass

def sync_rates(*args):
    try:
        rb = get_val(entry_rmb_base)
        for curr, var in rate_vars.items():
            if curr == "🇨🇳 RMB": continue
            rate = FIXED_MYR_RATE if (rate_mode.get() == "fixed" and curr == "🇲🇾 MYR") else base_rates[curr]
            var.set(f"{rb * rate:.0f}" if rate > 100 else f"{rb * rate:.3f}")
        calculate_all()
    except: pass

def update_manual_rate(curr):
    if rate_mode.get() == "fixed" and curr == "🇲🇾 MYR": return
    try:
        rb = get_val(entry_rmb_base)
        cv = float(rate_vars[curr].get())
        if rb != 0: base_rates[curr] = cv / rb
        calculate_all()
    except: pass

# --- 3. UI 界面 ---
root = tk.Tk()
root.title("TikTok定价助手 Pro")
root.geometry("580x740")
root.tk.call('tk', 'scaling', 2.0)

style = ttk.Style()
style.theme_use('alt')
style.configure("Green.TCombobox", fieldbackground="white", background=WECHAT_GREEN, font=("Arial", 12))

main = tk.Frame(root, padx=20, pady=5); main.pack(fill=tk.X)

# 汇率
lf = tk.LabelFrame(main, text=" ⚙️ 汇率同步 ", padx=10, pady=5); lf.pack(fill=tk.X, pady=(0, 10))
rate_mode = tk.StringVar(value="manual")
mf = tk.Frame(lf); mf.grid(row=0, column=0, columnspan=6, sticky=tk.W)
tk.Radiobutton(mf, text="手动", variable=rate_mode, value="manual", command=calculate_all).pack(side=tk.LEFT)
tk.Radiobutton(mf, text="锁定1.75", variable=rate_mode, value="fixed", command=calculate_all, fg=WECHAT_GREEN).pack(side=tk.LEFT, padx=10)

rate_vars, rate_entries = {}, {}
rmb_var = tk.StringVar(value="1"); rmb_var.trace_add("write", sync_rates)

for i, curr in enumerate(FULL_RATES.keys()):
    r, c = (i // 3) + 1, (i % 3) * 2
    tk.Label(lf, text=f"{curr}:", font=("Arial", 9)).grid(row=r, column=c, sticky=tk.W)
    v = rmb_var if curr == "🇨🇳 RMB" else tk.StringVar(value=str(FULL_RATES[curr]))
    rate_vars[curr] = v
    e = tk.Entry(lf, width=8, textvariable=v); e.grid(row=r, column=c+1, padx=2, pady=1)
    if curr == "🇨🇳 RMB": entry_rmb_base = e
    rate_entries[curr] = e
    if curr != "🇨🇳 RMB": e.bind("<KeyRelease>", lambda e, c=curr: update_manual_rate(c))

# 输入
in_f = tk.Frame(main); in_f.pack(fill=tk.X, pady=5)
tk.Label(in_f, text="💰 成本 (RMB):", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
entry_cost = tk.Entry(in_f, font=("Arial", 14), width=12); entry_cost.grid(row=1, column=0, sticky=tk.W, pady=5)
entry_cost.insert(0, "20"); entry_cost.bind("<KeyRelease>", calculate_all)

tk.Label(in_f, text="🚚 运费及币种:", font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W, padx=15)
s_b = tk.Frame(in_f); s_b.grid(row=1, column=1, sticky=tk.W, padx=15)
entry_ship = tk.Entry(s_b, font=("Arial", 14), width=8); entry_ship.pack(side=tk.LEFT)
entry_ship.insert(0, "1.95"); entry_ship.bind("<KeyRelease>", calculate_all)

# --- 放大版微信绿选择框 ---
combo_ship = ttk.Combobox(s_b, values=list(FULL_RATES.keys()), width=12, state="readonly", style="Green.TCombobox")
combo_ship.set("🇲🇾 MYR"); combo_ship.pack(side=tk.LEFT, padx=10, ipady=5)
combo_ship.bind("<<ComboboxSelected>>", calculate_all)

tk.Label(main, text="💵 结果显示币种:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10,0))
combo_out = ttk.Combobox(main, values=list(FULL_RATES.keys()), state="readonly", style="Green.TCombobox")
combo_out.set("🇲🇾 MYR"); combo_out.pack(fill=tk.X, pady=5, ipady=6)
combo_out.bind("<<ComboboxSelected>>", calculate_all)

btn = tk.Button(main, text="开始定价 (Enter)", font=("Arial", 13, "bold"), bg=WECHAT_GREEN, fg="white", highlightbackground=WECHAT_GREEN, command=calculate_all, pady=12)
btn.pack(fill=tk.X, pady=15); root.bind('<Return>', calculate_all)

text_res = tk.Text(main, height=7, font=("Menlo", 13), state=tk.DISABLED, padx=15, pady=15); text_res.pack(fill=tk.X)
tk.Label(main, text="* 净利 = 折后售价 × 20% (已剔除佣金与固定费)", font=("Arial", 8), fg="gray").pack(pady=5)

calculate_all()
root.mainloop()
