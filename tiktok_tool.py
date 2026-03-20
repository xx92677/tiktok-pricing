import tkinter as tk
from tkinter import messagebox, ttk
import math

# --- 1. 财务与基础配置 ---
FIXED_MYR_RATE = 0.57  # 1 RMB = 0.57 MYR
FULL_RATES = {
    "🇨🇳 RMB": 1.0, "🇲🇾 MYR": 0.588, "🇺🇸 USD": 0.138, "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45, "🇭🇰 HKD": 1.08, "🇹🇭 THB": 4.85, "🇻🇳 VND": 3450.0,
    "🇧🇷 BRL": 0.72, "🇲🇽 MXN": 2.35, "🇦🇷 ARS": 120.0, "🇯🇵 JPY": 20.5,
    "🇵🇭 PHP": 7.8, "🇮🇩 IDR": 2150.0
}

# 液态玻璃色板 (macOS 26 Vibe)
GLASS_BG = "#1C1C1E"       # 深空黑底色
GLASS_CARD = "#2C2C2E"     # 半透明卡片感
GLASS_INPUT = "#3A3A3C"    # 输入框深度色
GLASS_TEXT = "#F5F5F7"     # 亮白文字
GLASS_SUB = "#8E8E93"      # 辅助灰色

COMMISSION_RATE = 0.0702
FIXED_FEE_MYR = 0.54
TARGET_DISCOUNT = 0.51

base_rates = {k: v for k, v in FULL_RATES.items()}

# --- 2. 核心逻辑 ---
def get_num(entry):
    try: return float(entry.get()) if entry.get() else 0.0
    except: return 0.0

def calculate_logic(*args):
    try:
        cost_rmb = get_num(entry_cost)
        ship_val = get_num(entry_ship)
        ship_curr, out_curr = combo_ship.get(), combo_out.get()
        suffix = out_curr.split()[-1]
        
        # 利润率解析
        p_str = combo_profit.get().strip('%')
        profit_margin = float(p_str) / 100 if p_str else 0.20
        
        myr_rate_val = FIXED_MYR_RATE if rate_mode.get() == "fixed" else base_rates["🇲🇾 MYR"]
        cost_myr = cost_rmb * myr_rate_val
        ship_myr = (ship_val / base_rates[ship_curr]) * myr_rate_val
        
        # 售价利润率公式
        divisor = 1 - COMMISSION_RATE - profit_margin
        if divisor <= 0: return
        p_deal_myr = (cost_myr + ship_myr + FIXED_FEE_MYR) / divisor
        p_orig_myr = math.ceil(p_deal_myr / (1 - TARGET_DISCOUNT))
        
        to_out = lambda v: (v / myr_rate_val) * base_rates[out_curr]
        final_deal = to_out(p_deal_myr)
        
        # 人民币利润独立核算
        profit_rmb = (p_deal_myr * profit_margin) / myr_rate_val
        
        text_res.config(state=tk.NORMAL)
        text_res.delete(1.0, tk.END)
        text_res.insert(tk.END, 
            f"建议原价： {to_out(p_orig_myr):.2f} {suffix}\n"
            f"折后售价： {final_deal:.2f} {suffix}\n"
            f"----------------------------------\n"
            f"目标利润 ({int(profit_margin*100)}%): {final_deal * profit_margin:.2f} {suffix}\n"
            f"预计利润 (RMB): {profit_rmb:.2f} RMB\n"
            f"----------------------------------\n"
            f"佣金扣除 (7.02%): {final_deal * COMMISSION_RATE:.2f} {suffix}\n"
            f"总成本 (含费): {to_out(cost_myr + ship_myr + FIXED_FEE_MYR):.2f} {suffix}\n"
            f"----------------------------------\n"
            f"汇率基准: 1 RMB = {base_rates[out_curr]:.3f} {suffix}"
        )
        text_res.config(state=tk.DISABLED)
    except: pass

def sync_rates(*args):
    try:
        rb = get_num(entry_rmb_base)
        for curr, var in rate_vars.items():
            if curr == "🇨🇳 RMB": continue
            rate = FIXED_MYR_RATE if (rate_mode.get() == "fixed" and curr == "🇲🇾 MYR") else base_rates[curr]
            var.set(f"{rb * rate:.0f}" if rate > 100 else f"{rb * rate:.3f}")
        calculate_logic()
    except: pass

# --- 3. UI 构造 (液态玻璃视觉) ---
root = tk.Tk()
root.title("TikTok Pricing Assistant Pro")
root.geometry("600x920")
root.configure(bg=GLASS_BG)

# 开启窗口透明度模拟液态玻璃
root.attributes("-alpha", 0.94) 

if root.tk.call('tk', 'windowingsystem') == 'aqua':
    root.tk.call('tk', 'scaling', 2.0)

style = ttk.Style()
style.theme_use('aqua')
# 下拉框美化
style.configure("TCombobox", fieldbackground=GLASS_INPUT, background=GLASS_INPUT, foreground=GLASS_TEXT)

main = tk.Frame(root, padx=30, pady=20, bg=GLASS_BG)
main.pack(fill=tk.BOTH, expand=True)

# 汇率区 (液态卡片)
lf = tk.LabelFrame(main, text=" REAL-TIME RATES ", padx=15, pady=15, bg=GLASS_BG, fg=GLASS_SUB, font=("Impact", 10))
lf.pack(fill=tk.X, pady=(0, 20))

rate_mode = tk.StringVar(value="fixed") # 默认锁定
mf = tk.Frame(lf, bg=GLASS_BG)
mf.grid(row=0, column=0, columnspan=6, sticky=tk.W, pady=(0,10))
tk.Radiobutton(mf, text="Manual", variable=rate_mode, value="manual", command=calculate_logic, bg=GLASS_BG, fg=GLASS_TEXT, selectcolor=GLASS_CARD).pack(side=tk.LEFT)
tk.Radiobutton(mf, text="Lock 0.57", variable=rate_mode, value="fixed", command=calculate_logic, bg=GLASS_BG, fg=GLASS_TEXT, selectcolor=GLASS_CARD).pack(side=tk.LEFT, padx=20)

rate_vars, rmb_var = {}, tk.StringVar(value="1")
rmb_var.trace_add("write", sync_rates)

for i, curr in enumerate(FULL_RATES.keys()):
    r, c = (i // 3) + 1, (i % 3) * 2
    tk.Label(lf, text=f"{curr}:", font=("Verdana", 9), bg=GLASS_BG, fg=GLASS_SUB).grid(row=r, column=c, sticky=tk.W)
    v = rmb_var if curr == "🇨🇳 RMB" else tk.StringVar(value=str(FULL_RATES[curr]))
    rate_vars[curr] = v
    e = tk.Entry(lf, width=9, textvariable=v, relief="flat", bg=GLASS_INPUT, fg=GLASS_TEXT, insertbackground="white", highlightthickness=0)
    e.grid(row=r, column=c+1, padx=4, pady=4)
    if curr == "🇨🇳 RMB": entry_rmb_base = e
    if curr != "🇨🇳 RMB": e.bind("<KeyRelease>", lambda e, c=curr: calculate_logic())

# 利润率卡片
tk.Label(main, text="TARGET MARGIN (20%-30%)", font=("Verdana", 10, "bold"), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W, pady=(5,5))
combo_profit = ttk.Combobox(main, values=[f"{i}%" for i in range(20, 31)], state="readonly")
combo_profit.set("20%")
combo_profit.pack(fill=tk.X, pady=(0, 20), ipady=8)
combo_profit.bind("<<ComboboxSelected>>", calculate_logic)

# 输入卡片
in_f = tk.Frame(main, bg=GLASS_BG); in_f.pack(fill=tk.X)
tk.Label(in_f, text="COST (RMB)", font=("Verdana", 10), bg=GLASS_BG, fg=GLASS_TEXT).grid(row=0, column=0, sticky=tk.W)
entry_cost = tk.Entry(in_f, font=("Verdana", 16), width=12, relief="flat", bg=GLASS_INPUT, fg=GLASS_TEXT, insertbackground="white")
entry_cost.grid(row=1, column=0, sticky=tk.W, pady=8); entry_cost.insert(0, "20")
entry_cost.bind("<KeyRelease>", lambda e: calculate_logic())

tk.Label(in_f, text="SHIP + CURR", font=("Verdana", 10), bg=GLASS_BG, fg=GLASS_TEXT).grid(row=0, column=1, sticky=tk.W, padx=20)
s_b = tk.Frame(in_f, bg=GLASS_BG); s_b.grid(row=1, column=1, sticky=tk.W, padx=20)
entry_ship = tk.Entry(s_b, font=("Verdana", 16), width=8, relief="flat", bg=GLASS_INPUT, fg=GLASS_TEXT, insertbackground="white")
entry_ship.pack(side=tk.LEFT); entry_ship.insert(0, "1.95")
entry_ship.bind("<KeyRelease>", lambda e: calculate_logic())

combo_ship = ttk.Combobox(s_b, values=list(FULL_RATES.keys()), width=10, state="readonly")
combo_ship.set("🇲🇾 MYR"); combo_ship.pack(side=tk.LEFT, padx=10, ipady=5); combo_ship.bind("<<ComboboxSelected>>", calculate_logic)

# 结果币种
tk.Label(main, text="OUTPUT CURRENCY", font=("Verdana", 10), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W, pady=(15,5))
combo_out = ttk.Combobox(main, values=list(FULL_RATES.keys()), state="readonly")
combo_out.set("🇲🇾 MYR"); combo_out.pack(fill=tk.X, pady=(0, 25), ipady=8); combo_out.bind("<<ComboboxSelected>>", calculate_logic)

# 悬浮感大按钮
btn = tk.Button(main, text="ANALYZE PRICING", font=("Impact", 16), 
                bg="#F5F5F7", fg="#1C1C1E", highlightthickness=0,
                relief="flat", command=calculate_logic, pady=15)
btn.pack(fill=tk.X, pady=(0, 20))

# 结果液态显示区域
text_res = tk.Text(main, height=11, font=("Menlo", 14), state=tk.DISABLED, 
                   bg=GLASS_CARD, fg=GLASS_TEXT, relief="flat", padx=20, pady=20)
text_res.pack(fill=tk.X)

tk.Label(main, text="LIQUID GLASS UI • MAC SILICON NATIVE", font=("Impact", 9), fg="#48484A", bg=GLASS_BG).pack(pady=15)

calculate_logic()
root.mainloop()
