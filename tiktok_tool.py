import tkinter as tk
from tkinter import messagebox, ttk
import math

# --- 1. 核心财务配置 ---
FIXED_MYR_RATE = 0.57  # 1 RMB = 0.57 MYR
FULL_RATES = {
    "🇨🇳 RMB": 1.0, "🇲🇾 MYR": 0.57, "🇺🇸 USD": 0.138, "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45, "🇭🇰 HKD": 1.08, "🇹🇭 THB": 4.85, "🇻🇳 VND": 3450.0,
    "🇧🇷 BRL": 0.72, "🇲🇽 MXN": 2.35, "🇦🇷 ARS": 120.0, "🇯🇵 JPY": 20.5,
    "🇵🇭 PHP": 7.8, "🇮🇩 IDR": 2150.0
}

# 液态玻璃配色
GLASS_BG = "#1C1C1E"
GLASS_CARD = "#2C2C2E"
GLASS_INPUT = "#3A3A3C"
GLASS_TEXT = "#F5F5F7"
GLASS_SUB = "#8E8E93"

COMMISSION_RATE = 0.0702
FIXED_FEE_MYR = 0.54
TARGET_DISCOUNT = 0.51

# 简写后缀映射
CURR_MAP = {k: k.split()[-1] for k in FULL_RATES.keys()}
base_rates = {k: v for k, v in FULL_RATES.items()}

# --- 2. 核心逻辑 (增强稳定性) ---
def get_num(entry):
    try:
        val = entry.get().strip()
        return float(val) if val else 0.0
    except ValueError:
        return 0.0

def calculate_logic(*args):
    try:
        cost_rmb = get_num(entry_cost)
        ship_val = get_num(entry_ship)
        ship_curr = combo_ship.get()
        out_curr = combo_out.get()
        suffix = CURR_MAP.get(out_curr, "N/A")
        
        # 利润率解析
        p_str = combo_profit.get().strip('%')
        profit_margin = float(p_str) / 100 if p_str else 0.25
        
        # 确定马币汇率基准
        my_rate = FIXED_MYR_RATE if rate_mode.get() == "fixed" else base_rates.get("🇲🇾 MYR", 0.57)
        
        # 计算折算为马币的成本
        ship_myr = (ship_val / base_rates.get(ship_curr, 1.0)) * my_rate
        cost_myr = cost_rmb * my_rate
        
        # 售价利润率公式: Price = (Cost + Ship + Fee) / (1 - Comm - Margin)
        divisor = 1 - COMMISSION_RATE - profit_margin
        if divisor <= 0: return
        
        p_deal_myr = (cost_myr + ship_myr + FIXED_FEE_MYR) / divisor
        p_orig_myr = math.ceil(p_deal_myr / (1 - TARGET_DISCOUNT))
        
        # 转换至显示币种
        to_out = lambda v: (v / my_rate) * base_rates.get(out_curr, 1.0)
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
            f"当前汇率: 1 RMB = {base_rates.get(out_curr, 1.0):.3f} {suffix}"
        )
        text_res.config(state=tk.DISABLED)
    except Exception:
        pass

def sync_rates(*args):
    try:
        rb = get_num(entry_rmb_base)
        for curr, var in rate_vars.items():
            if curr == "🇨🇳 RMB": continue
            rate = FIXED_MYR_RATE if (rate_mode.get() == "fixed" and curr == "🇲🇾 MYR") else base_rates.get(curr, 1.0)
            var.set(f"{rb * rate:.0f}" if rate > 100 else f"{rb * rate:.3f}")
        calculate_logic()
    except Exception:
        pass

# --- 3. UI 初始化 (稳健模式) ---
root = tk.Tk()
root.title("TikTok 定价助手 Pro")
root.geometry("620x920")
root.configure(bg=GLASS_BG)

# Retina 缩放适配 (必须在 UI 构建前)
try:
    if root.tk.call('tk', 'windowingsystem') == 'aqua':
        root.tk.call('tk', 'scaling', 2.0)
except:
    pass

style = ttk.Style(root)
style.theme_use('aqua')
style.configure("TCombobox", fieldbackground=GLASS_INPUT, foreground=GLASS_TEXT, background=GLASS_INPUT)

main = tk.Frame(root, padx=20, pady=10, bg=GLASS_BG)
main.pack(fill=tk.BOTH, expand=True)

# 汇率面板 (3列排布)
lf = tk.LabelFrame(main, text=" 实时汇率设置 (RMB基准) ", padx=10, pady=8, bg=GLASS_BG, fg=GLASS_SUB, font=("Arial", 10, "bold"))
lf.pack(fill=tk.X, pady=(0, 10))

rate_mode = tk.StringVar(value="fixed")
mf = tk.Frame(lf, bg=GLASS_BG)
mf.grid(row=0, column=0, columnspan=6, sticky=tk.W, pady=(0,8))
tk.Radiobutton(mf, text="手动", variable=rate_mode, value="manual", command=calculate_logic, bg=GLASS_BG, fg=GLASS_TEXT, selectcolor=GLASS_CARD, activebackground=GLASS_BG).pack(side=tk.LEFT)
tk.Radiobutton(mf, text="锁定 0.57", variable=rate_mode, value="fixed", command=calculate_logic, bg=GLASS_BG, fg=GLASS_TEXT, selectcolor=GLASS_CARD, activebackground=GLASS_BG).pack(side=tk.LEFT, padx=15)

rate_vars, rmb_var = {}, tk.StringVar(value="1")
rmb_var.trace_add("write", sync_rates)

for i, curr in enumerate(FULL_RATES.keys()):
    r, c = (i // 3) + 1, (i % 3) * 2
    tk.Label(lf, text=f"{curr}:", font=("Arial", 11), bg=GLASS_BG, fg=GLASS_TEXT).grid(row=r, column=c, sticky=tk.W, padx=(2,1), pady=4)
    v = rmb_var if curr == "🇨🇳 RMB" else tk.StringVar(value=str(FULL_RATES[curr]))
    rate_vars[curr] = v
    e = tk.Entry(lf, width=7, textvariable=v, relief="flat", bg=GLASS_INPUT, fg=GLASS_TEXT, insertbackground="white", font=("Arial", 12))
    e.grid(row=r, column=c+1, padx=4, pady=4)
    if curr == "🇨🇳 RMB": entry_rmb_base = e
    if curr != "🇨🇳 RMB": e.bind("<KeyRelease>", lambda e, c=curr: calculate_logic())

# 利润选择
tk.Label(main, text="🎯 目标利润率 (Margin):", font=("Arial", 10, "bold"), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W, pady=(5,5))
combo_profit = ttk.Combobox(main, values=[f"{i}%" for i in range(20, 31)], state="readonly", font=("Arial", 12))
combo_profit.set("25%")
combo_profit.pack(fill=tk.X, pady=(0, 10), ipady=5)
combo_profit.bind("<<ComboboxSelected>>", calculate_logic)

# 输入卡片
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
combo_ship.set("🇲🇾 MYR"); combo_ship.pack(side=tk.LEFT, padx=5, ipady=4); combo_ship.bind("<<ComboboxSelected>>", calculate_logic)

# 结果显示币种
tk.Label(main, text="💵 结果显示币种:", font=("Arial", 10), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W, pady=(8,2))
combo_out = ttk.Combobox(main, values=list(FULL_RATES.keys()), state="readonly", font=("Arial", 12))
combo_out.set("🇲🇾 MYR"); combo_out.pack(fill=tk.X, pady=(0, 15), ipady=6); combo_out.bind("<<ComboboxSelected>>", calculate_logic)

btn = tk.Button(main, text="计 算 定 价", font=("Arial", 13, "bold"), 
                bg="#F5F5F7", fg="#1C1C1E", highlightthickness=0,
                relief="flat", command=calculate_logic, pady=10)
btn.pack(fill=tk.X, pady=(0, 15))

text_res = tk.Text(main, height=13, font=("Menlo", 12), state=tk.DISABLED, 
                   bg=GLASS_CARD, fg=GLASS_TEXT, relief="flat", padx=15, pady=15)
text_res.pack(fill=tk.X)

# --- 4. 延迟设置透明度 (防闪退关键) ---
def set_appearance():
    root.attributes("-alpha", 0.96)
    calculate_logic()

root.after(200, set_appearance)
root.mainloop()
