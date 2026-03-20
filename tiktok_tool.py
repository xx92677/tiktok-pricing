import tkinter as tk
from tkinter import messagebox, ttk
import math

# --- 1. 财务与基础配置 ---
FIXED_MYR_RATE = 1 / 1.75  
FULL_RATES = {
    "🇨🇳 RMB": 1.0, "🇲🇾 MYR": 0.588, "🇺🇸 USD": 0.138, "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45, "🇭🇰 HKD": 1.08, "🇹🇭 THB": 4.85, "🇻🇳 VND": 3450.0,
    "🇧🇷 BRL": 0.72, "🇲🇽 MXN": 2.35, "🇦🇷 ARS": 120.0, "🇯🇵 JPY": 20.5,
    "🇵🇭 PHP": 7.8, "🇮🇩 IDR": 2150.0
}

# 现代配色方案 (Mac Style)
COLOR_BG = "#F5F5F7"      # 系统底色
COLOR_CARD = "#FFFFFF"    # 卡片色
COLOR_TEXT = "#1D1D1F"    # 主文字
COLOR_BORDER = "#D1D1D6"  # 边框
COLOR_BTN = "#1D1D1F"     # 按钮

COMMISSION_RATE = 0.0702  # 佣金 7.02%
FIXED_FEE_MYR = 0.54      # 固定费 0.54
TARGET_DISCOUNT = 0.51    # 51% 折扣

base_rates = {k: v for k, v in FULL_RATES.items()}

# --- 2. 核心逻辑 ---

def get_num(entry):
    try: return float(entry.get())
    except: return 0.0

def calculate_logic(*args):
    """根据选定的 20%-30% 利润率倒求售价"""
    try:
        cost_rmb = get_num(entry_cost)
        ship_val = get_num(entry_ship)
        ship_curr, out_curr = combo_ship.get(), combo_out.get()
        
        # 解析利润率下拉菜单 (20%-30%)
        profit_pct_str = combo_profit.get().strip('%')
        profit_margin = float(profit_pct_str) / 100
        
        # 确定汇率
        myr_rate = FIXED_MYR_RATE if rate_mode.get() == "fixed" else base_rates["🇲🇾 MYR"]
        
        # 折算马币
        cost_myr = cost_rmb * myr_rate
        ship_myr = (ship_val / base_rates[ship_curr]) * myr_rate
        
        # 倒求公式：售价 = (成本 + 运费 + 固定费) / (1 - 佣金率 - 利润率)
        divisor = 1 - COMMISSION_RATE - profit_margin
        if divisor <= 0: return
            
        p_deal_myr = (cost_myr + ship_myr + FIXED_FEE_MYR) / divisor
        p_orig_myr = math.ceil(p_deal_myr / (1 - TARGET_DISCOUNT))
        
        # 币种转换
        to_out = lambda v: (v / myr_rate) * base_rates[out_curr]
        res_deal = to_out(p_deal_myr)
        
        text_res.config(state=tk.NORMAL)
        text_res.delete(1.0, tk.END)
        text_res.insert(tk.END, 
            f"建议原价：{to_out(p_orig_myr):.2f}\n"
            f"折后售价：{res_deal:.2f}\n"
            f"--------------------\n"
            f"目标利润 ({profit_pct_str}%): {res_deal * profit_margin:.2f}\n"
            f"佣金扣除 (7.02%): {res_deal * COMMISSION_RATE:.2f}\n"
            f"成本总计 (含税费): {to_out(cost_myr + ship_myr + FIXED_FEE_MYR):.2f}\n"
            f"--------------------\n"
            f"汇率基准: 1 RMB = {base_rates[out_curr]:.3f} {out_curr.split()[-1]}"
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

# --- 3. UI 构造 ---
root = tk.Tk()
root.title("TikTok定价助手 Pro")
root.geometry("580x820")
root.configure(bg=COLOR_BG)
root.tk.call('tk', 'scaling', 2.0)

# 统一 Combobox 样式
style = ttk.Style()
style.theme_use('apple') if 'apple' in style.theme_names() else style.theme_use('alt')
style.configure("TCombobox", padding=5, font=("Helvetica", 11))

main = tk.Frame(root, padx=25, pady=10, bg=COLOR_BG)
main.pack(fill=tk.BOTH, expand=True)

# --- 汇率面板 ---
lf = tk.LabelFrame(main, text=" ⚙️ 实时汇率同步 ", padx=12, pady=10, bg=COLOR_BG, fg="#8E8E93", font=("Helvetica", 9, "bold"))
lf.pack(fill=tk.X, pady=(0, 15))

rate_mode = tk.StringVar(value="manual")
mf = tk.Frame(lf, bg=COLOR_BG)
mf.grid(row=0, column=0, columnspan=6, sticky=tk.W, pady=(0,5))
tk.Radiobutton(mf, text="手动", variable=rate_mode, value="manual", command=calculate_logic, bg=COLOR_BG).pack(side=tk.LEFT)
tk.Radiobutton(mf, text="锁定1.75", variable=rate_mode, value="fixed", command=calculate_logic, bg=COLOR_BG).pack(side=tk.LEFT, padx=15)

rate_vars, rmb_var = {}, tk.StringVar(value="1")
rmb_var.trace_add("write", sync_rates)

for i, curr in enumerate(FULL_RATES.keys()):
    r, c = (i // 3) + 1, (i % 3) * 2
    tk.Label(lf, text=f"{curr}:", font=("Helvetica", 9), bg=COLOR_BG).grid(row=r, column=c, sticky=tk.W)
    v = rmb_var if curr == "🇨🇳 RMB" else tk.StringVar(value=str(FULL_RATES[curr]))
    rate_vars[curr] = v
    e = tk.Entry(lf, width=8, textvariable=v, relief="flat", highlightthickness=1, highlightbackground=COLOR_BORDER)
    e.grid(row=r, column=c+1, padx=3, pady=2)
    if curr == "🇨🇳 RMB": entry_rmb_base = e
    if curr != "🇨🇳 RMB": e.bind("<KeyRelease>", lambda e, c=curr: calculate_logic())

# --- 设置与输入区 ---
# 1. 目标利润率下拉菜单 (20%-30% 全覆盖)
tk.Label(main, text="🎯 目标利润率 (Margin):", font=("Helvetica", 10, "bold"), bg=COLOR_BG).pack(anchor=tk.W, pady=(5,5))
profit_values = [f"{i}%" for i in range(20, 31)] # 生成 20% 到 30%
combo_profit = ttk.Combobox(main, values=profit_values, state="readonly", font=("Helvetica", 12))
combo_profit.set("20%")
combo_profit.pack(fill=tk.X, pady=(0, 15), ipady=5)
combo_profit.bind("<<ComboboxSelected>>", calculate_logic)

# 2. 成本与运费输入
row_input = tk.Frame(main, bg=COLOR_BG)
row_input.pack(fill=tk.X, pady=5)

tk.Label(row_input, text="💰 成本 (RMB):", font=("Helvetica", 10, "bold"), bg=COLOR_BG).grid(row=0, column=0, sticky=tk.W)
entry_cost = tk.Entry(row_input, font=("Helvetica", 15), width=12, relief="flat", highlightthickness=1, highlightbackground=COLOR_BORDER)
entry_cost.grid(row=1, column=0, sticky=tk.W, pady=5); entry_cost.insert(0, "20")
entry_cost.bind("<KeyRelease>", calculate_all)

tk.Label(row_input, text="🚚 运费及币种:", font=("Helvetica", 10, "bold"), bg=COLOR_BG).grid(row=0, column=1, sticky=tk.W, padx=15)
ship_box = tk.Frame(row_input, bg=COLOR_BG)
ship_box.grid(row=1, column=1, sticky=tk.W, padx=15)
entry_ship = tk.Entry(ship_box, font=("Helvetica", 15), width=8, relief="flat", highlightthickness=1, highlightbackground=COLOR_BORDER)
entry_ship.pack(side=tk.LEFT); entry_ship.insert(0, "1.95")
entry_ship.bind("<KeyRelease>", calculate_all)

combo_ship = ttk.Combobox(ship_box, values=list(FULL_RATES.keys()), width=10, state="readonly")
combo_ship.set("🇲🇾 MYR"); combo_ship.pack(side=tk.LEFT, padx=10, ipady=4); combo_ship.bind("<<ComboboxSelected>>", calculate_logic)

# 3. 结果币种
tk.Label(main, text="💵 结果显示币种:", font=("Helvetica", 10, "bold"), bg=COLOR_BG).pack(anchor=tk.W, pady=(10,5))
combo_out = ttk.Combobox(main, values=list(FULL_RATES.keys()), state="readonly", font=("Helvetica", 12))
combo_out.set("🇲🇾 MYR"); combo_out.pack(fill=tk.X, pady=(0, 20), ipady=6); combo_out.bind("<<ComboboxSelected>>", calculate_logic)

# 4. 确认按钮
btn = tk.Button(main, text="计算定价", font=("Helvetica", 14, "bold"), 
                bg=COLOR_BTN, fg="white", activebackground="#3A3A3C",
                relief="flat", cursor="hand2", command=calculate_logic, pady=12)
btn.pack(fill=tk.X, pady=(0, 15))

# 5. 结果文本域
text_res = tk.Text(main, height=7, font=("Menlo", 13), state=tk.DISABLED, 
                   bg="white", relief="flat", highlightthickness=1, highlightbackground=COLOR_BORDER, padx=15, pady=15)
text_res.pack(fill=tk.X)

tk.Label(main, text="* Native Apple Silicon Architecture Optimized", font=("Helvetica", 8), fg="#C7C7CC", bg=COLOR_BG).pack(pady=5)

calculate_logic()
root.mainloop()
