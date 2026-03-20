import tkinter as tk
from tkinter import messagebox, ttk
import math

# --- 1. 财务与基础配置 ---
FIXED_MYR_RATE = 0.57  # 1 RMB = 0.57 MYR (锁定汇率)
FULL_RATES = {
    "🇨🇳 人民币": 1.0, "🇲🇾 马币": 0.588, "🇺🇸 美元": 0.138, "🇪🇺 欧元": 0.127,
    "🇹🇼 台币": 4.45, "🇭🇰 港币": 1.08, "🇹🇭 泰铢": 4.85, "🇻🇳 越南盾": 3450.0,
    "🇧🇷 巴西雷亚尔": 0.72, "🇲🇽 墨西哥比索": 2.35, "🇦🇷 阿根廷比索": 120.0, "🇯🇵 日元": 20.5,
    "🇵🇭 菲律宾比索": 7.8, "🇮🇩 印尼盾": 2150.0
}

# 液态玻璃色板 (macOS 26 审美)
GLASS_BG = "#1C1C1E"       
GLASS_CARD = "#2C2C2E"     
GLASS_INPUT = "#3A3A3C"    
GLASS_TEXT = "#F5F5F7"     
GLASS_SUB = "#8E8E93"      

COMMISSION_RATE = 0.0702   # 佣金 7.02%
FIXED_FEE_MYR = 0.54       # 固定费
TARGET_DISCOUNT = 0.51     # 51% 折扣

CURR_MAP = {k: k.split()[-1] for k in FULL_RATES.keys()}
base_rates = {k: v for k, v in FULL_RATES.items()}

# --- 2. 核心逻辑 ---
def get_num(entry):
    try: 
        val = entry.get()
        return float(val) if val else 0.0
    except: return 0.0

def calculate_logic(*args):
    try:
        cost_rmb = get_num(entry_cost)
        ship_val = get_num(entry_ship)
        ship_curr, out_curr = combo_ship.get(), combo_out.get()
        suffix = CURR_MAP.get(out_curr, "N/A")
        
        p_str = combo_profit.get().strip('%')
        profit_margin = float(p_str) / 100 if p_str else 0.20
        
        # 汇率基准
        my_rate = FIXED_MYR_RATE if rate_mode.get() == "fixed" else base_rates["🇲🇾 马币"]
        ship_myr = (ship_val / base_rates[ship_curr]) * my_rate
        cost_myr = cost_rmb * my_rate
        
        # 售价利润率公式
        divisor = 1 - COMMISSION_RATE - profit_margin
        if divisor <= 0: return
        p_deal_myr = (cost_myr + ship_myr + FIXED_FEE_MYR) / divisor
        p_orig_myr = math.ceil(p_deal_myr / (1 - TARGET_DISCOUNT))
        
        to_out = lambda v: (v / my_rate) * base_rates[out_curr]
        f_deal = to_out(p_deal_myr)
        profit_rmb = (p_deal_myr * profit_margin) / my_rate
        
        text_res.config(state=tk.NORMAL)
        text_res.delete(1.0, tk.END)
        text_res.insert(tk.END, 
            f"建议原价： {to_out(p_orig_myr):.2f} {suffix}\n"
            f"折后售价： {f_deal:.2f} {suffix}\n"
            f"----------------------------------\n"
            f"目标利润 ({int(profit_margin*100)}%): {f_deal * profit_margin:.2f} {suffix}\n"
            f"预计利润 (RMB): {profit_rmb:.2f} RMB\n"
            f"----------------------------------\n"
            f"佣金扣除 (7.02%): {f_deal * COMMISSION_RATE:.2f} {suffix}\n"
            f"总成本 (含费): {to_out(cost_myr + ship_myr + FIXED_FEE_MYR):.2f} {suffix}\n"
            f"----------------------------------\n"
            f"当前汇率: 1 RMB = {base_rates[out_curr]:.3f} {suffix}"
        )
        text_res.config(state=tk.DISABLED)
    except: pass

def sync_rates(*args):
    try:
        rb = get_num(entry_rmb_base)
        for curr, var in rate_vars.items():
            if curr == "🇨🇳 人民币": continue
            rate = FIXED_MYR_RATE if (rate_mode.get() == "fixed" and curr == "🇲🇾 马币") else base_rates[curr]
            var.set(f"{rb * rate:.0f}" if rate > 100 else f"{rb * rate:.3f}")
        calculate_logic()
    except: pass

# --- 3. UI 构造 ---
root = tk.Tk()
root.title("TikTok 定价助手 Pro")
root.geometry("600x920")
root.configure(bg=GLASS_BG)
root.attributes("-alpha", 0.95) 

if root.tk.call('tk', 'windowingsystem') == 'aqua':
    root.tk.call('tk', 'scaling', 2.0)

style = ttk.Style()
style.theme_use('aqua')
style.configure("TCombobox", fieldbackground=GLASS_INPUT, foreground=GLASS_TEXT, background=GLASS_INPUT)

main = tk.Frame(root, padx=25, pady=10, bg=GLASS_BG)
main.pack(fill=tk.BOTH, expand=True)

# --- 汇率区 (2列大字体排版) ---
lf = tk.LabelFrame(main, text=" 实时汇率设置 ", padx=10, pady=8, bg=GLASS_BG, fg=GLASS_SUB, font=("Arial", 10, "bold"))
lf.pack(fill=tk.X, pady=(0, 10))

rate_mode = tk.StringVar(value="fixed")
mf = tk.Frame(lf, bg=GLASS_BG)
mf.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0,8))
tk.Radiobutton(mf, text="手动", variable=rate_mode, value="manual", command=calculate_logic, bg=GLASS_BG, fg=GLASS_TEXT, selectcolor=GLASS_CARD).pack(side=tk.LEFT)
tk.Radiobutton(mf, text="锁定 0.57", variable=rate_mode, value="fixed", command=calculate_logic, bg=GLASS_BG, fg=GLASS_TEXT, selectcolor=GLASS_CARD).pack(side=tk.LEFT, padx=15)

rate_vars, rmb_var = {}, tk.StringVar(value="1")
rmb_var.trace_add("write", sync_rates)

# 2列布局，字体提升
for i, curr in enumerate(FULL_RATES.keys()):
    r, c = (i // 2) + 1, (i % 2) * 2
    tk.Label(lf, text=f"{curr}:", font=("Arial", 11), bg=GLASS_BG, fg=GLASS_TEXT).grid(row=r, column=c, sticky=tk.W, padx=(5,2), pady=3)
    v = rmb_var if curr == "🇨🇳 人民币" else tk.StringVar(value=str(FULL_RATES[curr]))
    rate_vars[curr] = v
    e = tk.Entry(lf, width=10, textvariable=v, relief="flat", bg=GLASS_INPUT, fg=GLASS_TEXT, insertbackground="white", font=("Arial", 12))
    e.grid(row=r, column=c+1, padx=5, pady=3)
    if curr == "🇨🇳 人民币": entry_rmb_base = e
    if curr != "🇨🇳 人民币": e.bind("<KeyRelease>", lambda e, c=curr: calculate_logic())

# --- 输入与结果区 ---
tk.Label(main, text="🎯 目标利润率 (Margin):", font=("Arial", 10, "bold"), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W, pady=(5,5))
combo_profit = ttk.Combobox(main, values=[f"{i}%" for i in range(20, 31)], state="readonly", font=("Arial", 12))
combo_profit.set("20%")
combo_profit.pack(fill=tk.X, pady=(0, 10), ipady=5)
combo_profit.bind("<<ComboboxSelected>>", calculate_logic)

in_f = tk.Frame(main, bg=GLASS_BG); in_f.pack(fill=tk.X, pady=5)
tk.Label(in_f, text="💰 成本 (RMB)", font=("Arial", 10), bg=GLASS_BG, fg=GLASS_TEXT).grid(row=0, column=0, sticky=tk.W)
entry_cost = tk.Entry(in_f, font=("Arial", 15, "bold"), width=12, relief="flat", bg=GLASS_INPUT, fg=GLASS_TEXT, insertbackground="white")
entry_cost.grid(row=1, column=0, sticky=tk.W, pady=5); entry_cost.insert(0, "20")
entry_cost.bind("<KeyRelease>", lambda e: calculate_logic())

tk.Label(in_f, text="🚚 运费及币种", font=("Arial", 10), bg=GLASS_BG, fg=GLASS_TEXT).grid(row=0, column=1, sticky=tk.W, padx=15)
s_b = tk.Frame(in_f, bg=GLASS_BG); s_b.grid(row=1, column=1, sticky=tk.W, padx=15)
entry_ship = tk.Entry(s_b, font=("Arial", 15, "bold"), width=8, relief="flat", bg=GLASS_INPUT, fg=GLASS_TEXT, insertbackground="white")
entry_ship.pack(side=tk.LEFT); entry_ship.insert(0, "1.95")
entry_ship.bind("<KeyRelease>", lambda e: calculate_logic())
combo_ship = ttk.Combobox(s_b, values=list(FULL_RATES.keys()), width=10, state="readonly", font=("Arial", 12))
combo_ship.set("🇲🇾 马币"); combo_ship.pack(side=tk.LEFT, padx=5, ipady=4); combo_ship.bind("<<ComboboxSelected>>", calculate_logic)

tk.Label(main, text="💵 结果显示币种:", font=("Arial", 10), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W, pady=(8,2))
combo_out = ttk.Combobox(main, values=list(FULL_RATES.keys()), state="readonly", font=("Arial", 12))
combo_out.set("🇲🇾 马币"); combo_out.pack(fill=tk.X, pady=(0, 15), ipady=6); combo_out.bind("<<ComboboxSelected>>", calculate_logic)

btn = tk.Button(main, text="计 算 定 价", font=("Arial", 13, "bold"), 
                bg="#F5F5F7", fg="#1C1C1E", highlightthickness=0,
                relief="flat", command=calculate_logic, pady=10)
btn.pack(fill=tk.X, pady=(0, 15))

text_res = tk.Text(main, height=13, font=("Menlo", 12), state=tk.DISABLED, 
                   bg=GLASS_CARD, fg=GLASS_TEXT, relief="flat", padx=15, pady=15)
text_res.pack(fill=tk.X)

calculate_logic()
root.mainloop()
