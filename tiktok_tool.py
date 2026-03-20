import tkinter as tk
from tkinter import messagebox, ttk
import math

# --- 1. 基础配置与颜色定义 ---
FIXED_MYR_RATE = 0.57  # 按照要求：锁定汇率设为 0.57
FULL_RATES = {
    "🇨🇳 RMB": 1.0, "🇲🇾 MYR": 0.588, "🇺🇸 USD": 0.138, "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45, "🇭🇰 HKD": 1.08, "🇹🇭 THB": 4.85, "🇻🇳 VND": 3450.0,
    "🇧🇷 BRL": 0.72, "🇲🇽 MXN": 2.35, "🇦🇷 ARS": 120.0, "🇯🇵 JPY": 20.5,
    "🇵🇭 PHP": 7.8, "🇮🇩 IDR": 2150.0
}

# 黑暗模式色板 (Apple Dark Mode Palette)
DB_MAIN = "#1C1C1E"       
DB_CARD = "#2C2C2E"       
DB_INPUT = "#3A3A3C"      
DB_TEXT = "#FFFFFF"       
DB_SUBTEXT = "#A1A1AA"    
COMMISSION_RATE = 0.0702  # 佣金 7.02%
FIXED_FEE_MYR = 0.54      # 固定费 0.54
TARGET_DISCOUNT = 0.51    # 默认折扣 51%

base_rates = {k: v for k, v in FULL_RATES.items()}

# --- 2. 核心计算逻辑 ---
def get_num(entry):
    try:
        val = entry.get()
        return float(val) if val else 0.0
    except: return 0.0

def calculate_logic(*args):
    """基于售价利润率(Margin)的财务核心"""
    try:
        cost_rmb = get_num(entry_cost)
        ship_val = get_num(entry_ship)
        ship_curr, out_curr = combo_ship.get(), combo_out.get()
        
        # 结果币种后缀 (如 "MYR")
        suffix = out_curr.split()[-1]
        
        # 利润率解析 (20%-30%)
        p_str = combo_profit.get().strip('%')
        profit_margin = float(p_str) / 100 if p_str else 0.20
        
        # 确定马币汇率基准
        myr_rate_val = FIXED_MYR_RATE if rate_mode.get() == "fixed" else base_rates["🇲🇾 MYR"]
        
        # 换算成本
        ship_myr = (ship_val / base_rates[ship_curr]) * myr_rate_val
        cost_myr = cost_rmb * myr_rate_val
        
        # 倒求售价公式：Price = (Cost + Ship + FixedFee) / (1 - Comm - Margin)
        divisor = 1 - COMMISSION_RATE - profit_margin
        if divisor <= 0: return
        p_deal_myr = (cost_myr + ship_myr + FIXED_FEE_MYR) / divisor
        p_orig_myr = math.ceil(p_deal_myr / (1 - TARGET_DISCOUNT))
        
        # 转换显示
        to_out = lambda v: (v / myr_rate_val) * base_rates[out_curr]
        
        final_deal = to_out(p_deal_myr)
        final_profit = final_deal * profit_margin
        # 特色功能：无论显示什么币种，单独核算人民币利润
        profit_rmb = (p_deal_myr * profit_margin) / myr_rate_val
        
        text_res.config(state=tk.NORMAL)
        text_res.delete(1.0, tk.END)
        text_res.insert(tk.END, 
            f"建议原价：{to_out(p_orig_myr):.2f} {suffix}\n"
            f"折后售价：{final_deal:.2f} {suffix}\n"
            f"--------------------\n"
            f"目标利润 ({int(profit_margin*100)}%): {final_profit:.2f} {suffix}\n"
            f"预计利润 (RMB): {profit_rmb:.2f} RMB\n"
            f"--------------------\n"
            f"佣金扣除 (7.02%): {final_deal * COMMISSION_RATE:.2f} {suffix}\n"
            f"成本总计 (含费): {to_out(cost_myr + ship_myr + FIXED_FEE_MYR):.2f} {suffix}\n"
            f"--------------------\n"
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

# --- 3. UI 界面 ---
root = tk.Tk()
root.title("TikTok定价助手 Pro")
root.geometry("580x900")
root.configure(bg=DB_MAIN)

if root.tk.call('tk', 'windowingsystem') == 'aqua':
    root.tk.call('tk', 'scaling', 2.0)

style = ttk.Style()
style.theme_use('aqua')
style.configure("TCombobox", fieldbackground=DB_INPUT, foreground=DB_TEXT, background=DB_INPUT)

main = tk.Frame(root, padx=25, pady=15, bg=DB_MAIN)
main.pack(fill=tk.BOTH, expand=True)

# 汇率设置面板
lf = tk.LabelFrame(main, text=" 实时汇率设置 ", padx=12, pady=10, bg=DB_MAIN, fg=DB_SUBTEXT, font=("Arial", 9, "bold"))
lf.pack(fill=tk.X, pady=(0, 15))

rate_mode = tk.StringVar(value="manual")
mf = tk.Frame(lf, bg=DB_MAIN)
mf.grid(row=0, column=0, columnspan=6, sticky=tk.W, pady=(0,5))
tk.Radiobutton(mf, text="手动", variable=rate_mode, value="manual", command=calculate_logic, bg=DB_MAIN, fg=DB_TEXT, selectcolor=DB_CARD).pack(side=tk.LEFT)
tk.Radiobutton(mf, text="锁定0.57", variable=rate_mode, value="fixed", command=calculate_logic, bg=DB_MAIN, fg=DB_TEXT, selectcolor=DB_CARD).pack(side=tk.LEFT, padx=15)

rate_vars, rmb_var = {}, tk.StringVar(value="1")
rmb_var.trace_add("write", sync_rates)

for i, curr in enumerate(FULL_RATES.keys()):
    r, c = (i // 3) + 1, (i % 3) * 2
    tk.Label(lf, text=f"{curr}:", font=("Arial", 9), bg=DB_MAIN, fg=DB_TEXT).grid(row=r, column=c, sticky=tk.W)
    v = rmb_var if curr == "🇨🇳 RMB" else tk.StringVar(value=str(FULL_RATES[curr]))
    rate_vars[curr] = v
    e = tk.Entry(lf, width=8, textvariable=v, relief="flat", bg=DB_INPUT, fg=DB_TEXT, insertbackground="white")
    e.grid(row=r, column=c+1, padx=3, pady=3)
    if curr == "🇨🇳 RMB": entry_rmb_base = e
    if curr != "🇨🇳 RMB": e.bind("<KeyRelease>", lambda e, c=curr: calculate_logic())

# 利润率下拉 (20%-30%)
tk.Label(main, text="🎯 目标利润率 (Margin):", font=("Arial", 10, "bold"), bg=DB_MAIN, fg=DB_TEXT).pack(anchor=tk.W, pady=(5,5))
combo_profit = ttk.Combobox(main, values=[f"{i}%" for i in range(20, 31)], state="readonly")
combo_profit.set("20%")
combo_profit.pack(fill=tk.X, pady=(0, 15), ipady=5)
combo_profit.bind("<<ComboboxSelected>>", calculate_logic)

# 输入区
row_i = tk.Frame(main, bg=DB_MAIN); row_i.pack(fill=tk.X, pady=5)
tk.Label(row_i, text="💰 成本 (RMB):", font=("Arial", 10, "bold"), bg=DB_MAIN, fg=DB_TEXT).grid(row=0, column=0, sticky=tk.W)
entry_cost = tk.Entry(row_i, font=("Arial", 15), width=12, relief="flat", bg=DB_INPUT, fg=DB_TEXT, insertbackground="white")
entry_cost.grid(row=1, column=0, sticky=tk.W, pady=5); entry_cost.insert(0, "20")
entry_cost.bind("<KeyRelease>", lambda e: calculate_logic())

tk.Label(row_i, text="🚚 运费及币种:", font=("Arial", 10, "bold"), bg=DB_MAIN, fg=DB_TEXT).grid(row=0, column=1, sticky=tk.W, padx=15)
s_b = tk.Frame(row_i, bg=DB_MAIN); s_b.grid(row=1, column=1, sticky=tk.W, padx=15)
entry_ship = tk.Entry(s_b, font=("Arial", 15), width=8, relief="flat", bg=DB_INPUT, fg=DB_TEXT, insertbackground="white")
entry_ship.pack(side=tk.LEFT); entry_ship.insert(0, "1.95")
entry_ship.bind("<KeyRelease>", lambda e: calculate_logic())

combo_ship = ttk.Combobox(s_b, values=list(FULL_RATES.keys()), width=10, state="readonly")
combo_ship.set("🇲🇾 MYR"); combo_ship.pack(side=tk.LEFT, padx=10, ipady=4); combo_ship.bind("<<ComboboxSelected>>", calculate_logic)

# 结果显示币种
tk.Label(main, text="💵 结果显示币种:", font=("Arial", 10, "bold"), bg=DB_MAIN, fg=DB_TEXT).pack(anchor=tk.W, pady=(10,5))
combo_out = ttk.Combobox(main, values=list(FULL_RATES.keys()), state="readonly")
combo_out.set("🇲🇾 MYR"); combo_out.pack(fill=tk.X, pady=(0, 20), ipady=6); combo_out.bind("<<ComboboxSelected>>", calculate_logic)

# 计算按钮 (白色块)
btn = tk.Button(main, text="计 算 定 价", font=("Arial", 14, "bold"), 
                bg="#FFFFFF", fg="#000000", highlightbackground=DB_MAIN,
                relief="flat", command=calculate_logic, pady=12)
btn.pack(fill=tk.X, pady=(0, 15))

# 结果框
text_res = tk.Text(main, height=11, font=("Menlo", 13), state=tk.DISABLED, 
                   bg=DB_CARD, fg=DB_TEXT, relief="flat", padx=15, pady=15)
text_res.pack(fill=tk.X)

tk.Label(main, text="* 汇率锁定模式: 1 RMB = 0.57 MYR", font=("Arial", 8), fg=DB_SUBTEXT, bg=DB_MAIN).pack(pady=10)

calculate_logic()
root.mainloop()
