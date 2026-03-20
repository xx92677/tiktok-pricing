import tkinter as tk
from tkinter import messagebox, ttk
import math

# --- 1. 财务逻辑配置 ---
FIXED_MY_RATE = 0.57 
FULL_RATES = {
    "🇨🇳 RMB": 1.0, "🇲🇾 MYR": 0.588, "🇺🇸 USD": 0.138, "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45, "🇭🇰 HKD": 1.08, "🇹🇭 THB": 4.85, "🇻🇳 VND": 3450.0,
    "🇧🇷 BRL": 0.72, "🇲🇽 MXN": 2.35, "🇦🇷 ARS": 120.0, "🇯🇵 JPY": 20.5,
    "🇵🇭 PHP": 7.8, "🇮🇩 IDR": 2150.0
}

# 审美色板
GLASS_BG = "#1C1C1E"
GLASS_CARD = "#2C2C2E"
GLASS_INPUT = "#3A3A3C"
GLASS_TEXT = "#F5F5F7"
GLASS_SUB = "#8E8E93"

PLATFORM_COMMISSION = 0.0702 # 7.02%
FIXED_FEE_MYR = 0.54         
TARGET_DISCOUNT = 0.51       

CURR_MAP = {k: k.split()[-1] for k in FULL_RATES.items()}
base_rates = {k: v for k, v in FULL_RATES.items()}

# --- 2. 核心计算逻辑 ---
def get_val(widget):
    try:
        val = widget.get().strip('%')
        return float(val) if val else 0.0
    except: return 0.0

def calculate_logic(*args):
    try:
        cost_rmb = get_val(entry_cost)
        ship_val = get_val(entry_ship)
        qty = int(spin_qty.get())
        
        margin_pct = get_val(combo_profit) / 100
        ads_pct = get_val(combo_ads) / 100
        aff_pct = get_val(combo_aff) / 100
        
        ship_curr, out_curr = combo_ship.get(), combo_out.get()
        suffix = CURR_MAP.get(out_curr, "N/A")
        
        my_rate = FIXED_MY_RATE if rate_mode.get() == "fixed" else base_rates.get("🇲🇾 MYR", 0.588)
        
        # 多件折逻辑：2件8折，3件及以上7折
        bundle_discount = 1.0
        if bundle_mode.get():
            if qty == 2: bundle_discount = 0.8
            elif qty >= 3: bundle_discount = 0.7
        
        total_prod_cost_myr = cost_rmb * qty * my_rate
        total_ship_myr = (ship_val / base_rates.get(ship_curr, 1.0)) * my_rate
        total_base_expenses = total_prod_cost_myr + total_ship_myr + FIXED_FEE_MYR
        
        # 分母：1 - 平台 - 利润 - 广告 - 达人
        divisor = 1 - PLATFORM_COMMISSION - margin_pct - ads_pct - aff_pct
        if divisor <= 0:
            show_res("⚠️ 运营占比总和超限(>100%)")
            return

        total_deal_price_myr = total_base_expenses / divisor
        to_out = lambda v: (v / my_rate) * base_rates.get(out_curr, 1.0)
        
        f_total_deal = to_out(total_deal_price_myr)
        f_total_orig = (f_total_deal / bundle_discount) / (1 - TARGET_DISCOUNT)
        profit_rmb = (total_deal_price_myr * margin_pct) / my_rate
        
        show_res(
            f"建议总原价： {f_total_orig:.2f} {suffix}\n"
            f"订单实付价： {f_total_deal:.2f} {suffix}\n"
            f"单件平均价： {f_total_deal/qty:.2f} {suffix}\n"
            f"----------------------------------\n"
            f"预计总利润 ({int(margin_pct*100)}%): {f_total_deal * margin_pct:.2f} {suffix}\n"
            f"折合利润 (RMB): {profit_rmb:.2f} RMB\n"
            f"----------------------------------\n"
            f"广告支出 ({int(ads_pct*100)}%): {f_total_deal * ads_pct:.2f} {suffix}\n"
            f"达人分账 ({int(aff_pct*100)}%): {f_total_deal * aff_pct:.2f} {suffix}\n"
            f"平台抽成 (7.02%): {f_total_deal * PLATFORM_COMMISSION:.2f} {suffix}\n"
            f"----------------------------------\n"
            f"当前营销： {int(bundle_discount*10) if bundle_mode.get() else 10} 折模式"
        )
    except Exception as e: pass

def show_res(msg):
    text_res.config(state=tk.NORMAL)
    text_res.delete(1.0, tk.END)
    text_res.insert(tk.END, msg)
    text_res.config(state=tk.DISABLED)

# --- 3. UI 布局 ---
root = tk.Tk()
root.title("TikTok 定价助手 Pro")
root.geometry("850x950")
root.configure(bg=GLASS_BG)

# 异常预防：尝试设置缩放，失败则忽略
try:
    if root.tk.call('tk', 'windowingsystem') == 'aqua':
        root.tk.call('tk', 'scaling', 2.0)
except: pass

style = ttk.Style(root)
style.theme_use('aqua')
style.configure("TCombobox", fieldbackground=GLASS_INPUT, foreground=GLASS_TEXT, background=GLASS_INPUT)

main = tk.Frame(root, padx=20, pady=10, bg=GLASS_BG)
main.pack(fill=tk.BOTH, expand=True)

# 汇率区 (6列排布)
lf = tk.LabelFrame(main, text=" 实时汇率设置 ", padx=10, pady=8, bg=GLASS_BG, fg=GLASS_SUB, font=("Arial", 9, "bold"))
lf.pack(fill=tk.X, pady=(0, 15))

rate_mode = tk.StringVar(value="fixed")
mf = tk.Frame(lf, bg=GLASS_BG)
mf.grid(row=0, column=0, columnspan=12, sticky=tk.W, pady=(0,8))
tk.Radiobutton(mf, text="手动", variable=rate_mode, value="manual", command=calculate_logic, bg=GLASS_BG, fg=GLASS_TEXT, selectcolor=GLASS_CARD).pack(side=tk.LEFT)
tk.Radiobutton(mf, text="锁定 0.57", variable=rate_mode, value="fixed", command=calculate_logic, bg=GLASS_BG, fg=GLASS_TEXT, selectcolor=GLASS_CARD).pack(side=tk.LEFT, padx=15)

rate_vars = {}
for i, (curr, rate) in enumerate(FULL_RATES.items()):
    r, c = (i // 6) + 1, (i % 6) * 2
    tk.Label(lf, text=f"{curr}:", font=("Arial", 8), bg=GLASS_BG, fg=GLASS_TEXT).grid(row=r, column=c, sticky=tk.W, padx=2)
    v = tk.StringVar(value=str(rate))
    rate_vars[curr] = v
    e = tk.Entry(lf, width=6, textvariable=v, relief="flat", bg=GLASS_INPUT, fg=GLASS_TEXT, font=("Arial", 9))
    e.grid(row=r, column=c+1, padx=2, pady=2); e.bind("<KeyRelease>", lambda e: calculate_logic())

# --- 运营与输入层对齐设计 ---
# 运营层 (4列等宽)
op_frame = tk.Frame(main, bg=GLASS_BG)
op_frame.pack(fill=tk.X, pady=10)
for i in range(4): op_frame.columnconfigure(i, weight=1, uniform="group1")

# 1. 利润率
v_p = tk.Frame(op_frame, bg=GLASS_BG)
v_p.grid(row=0, column=0, sticky="ew")
tk.Label(v_p, text="🎯 利润率", font=("Arial", 11, "bold"), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W)
combo_profit = ttk.Combobox(v_p, values=[f"{i}%" for i in range(16, 31)], state="readonly", font=("Arial", 11))
combo_profit.set("20%"); combo_profit.pack(fill=tk.X, pady=6, ipady=4); combo_profit.bind("<<ComboboxSelected>>", calculate_logic)

# 2. 广告支出 (0-25%)
v_a = tk.Frame(op_frame, bg=GLASS_BG)
v_a.grid(row=0, column=1, sticky="ew", padx=15)
tk.Label(v_a, text="🔥 广告支出", font=("Arial", 11, "bold"), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W)
combo_ads = ttk.Combobox(v_a, values=[f"{i}%" for i in range(26)], state="readonly", font=("Arial", 11))
combo_ads.set("0%"); combo_ads.pack(fill=tk.X, pady=6, ipady=4); combo_ads.bind("<<ComboboxSelected>>", calculate_logic)

# 3. 达人佣金 (0-25%)
v_aff = tk.Frame(op_frame, bg=GLASS_BG)
v_aff.grid(row=0, column=2, sticky="ew", padx=(0,15))
tk.Label(v_aff, text="🤝 达人佣金", font=("Arial", 11, "bold"), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W)
combo_aff = ttk.Combobox(v_aff, values=[f"{i}%" for i in range(26)], state="readonly", font=("Arial", 11))
combo_aff.set("0%"); combo_aff.pack(fill=tk.X, pady=6, ipady=4); combo_aff.bind("<<ComboboxSelected>>", calculate_logic)

# 4. 多件多折开关 (字体加大)
v_sw = tk.Frame(op_frame, bg=GLASS_BG)
v_sw.grid(row=0, column=3, sticky="ew")
tk.Label(v_sw, text="📦 多件多折", font=("Arial", 11, "bold"), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W)
bundle_mode = tk.BooleanVar(value=True)
tk.Checkbutton(v_sw, text="启用优惠", variable=bundle_mode, bg=GLASS_BG, fg=GLASS_SUB, selectcolor=GLASS_CARD, command=calculate_logic, font=("Arial", 11)).pack(pady=8, anchor=tk.W)

# 输入层 (4列等宽，与运营层纵向对齐)
in_frame = tk.Frame(main, bg=GLASS_BG)
in_frame.pack(fill=tk.X, pady=10)
for i in range(4): in_frame.columnconfigure(i, weight=1, uniform="group1")

# 1. 成本
f1 = tk.Frame(in_frame, bg=GLASS_BG)
f1.grid(row=0, column=0, sticky="ew")
tk.Label(f1, text="💰 单价成本(RMB)", font=("Arial", 11, "bold"), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W)
entry_cost = tk.Entry(f1, font=("Arial", 15, "bold"), relief="flat", bg=GLASS_INPUT, fg=GLASS_TEXT, insertbackground="white")
entry_cost.pack(fill=tk.X, pady=6); entry_cost.insert(0, "20"); entry_cost.bind("<KeyRelease>", lambda e: calculate_logic())

# 2. 运费
f2 = tk.Frame(in_frame, bg=GLASS_BG)
f2.grid(row=0, column=1, sticky="ew", padx=15)
tk.Label(f2, text="🚚 运费总额", font=("Arial", 11, "bold"), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W)
entry_ship = tk.Entry(f2, font=("Arial", 15, "bold"), relief="flat", bg=GLASS_INPUT, fg=GLASS_TEXT, insertbackground="white")
entry_ship.pack(fill=tk.X, pady=6); entry_ship.insert(0, "1.95"); entry_ship.bind("<KeyRelease>", lambda e: calculate_logic())

# 3. 币种
f3 = tk.Frame(in_frame, bg=GLASS_BG)
f3.grid(row=0, column=2, sticky="ew", padx=(0,15))
tk.Label(f3, text="成本币种", font=("Arial", 11, "bold"), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W)
combo_ship = ttk.Combobox(f3, values=list(FULL_RATES.keys()), state="readonly", font=("Arial", 11))
combo_ship.set("🇲🇾 MYR"); combo_ship.pack(fill=tk.X, pady=6, ipady=4); combo_ship.bind("<<ComboboxSelected>>", calculate_logic)

# 4. 数量 (步进器 Spinbox)
f4 = tk.Frame(in_frame, bg=GLASS_BG)
f4.grid(row=0, column=3, sticky="ew")
tk.Label(f4, text="🔢 数量(上下键)", font=("Arial", 11, "bold"), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W)
spin_qty = tk.Spinbox(f4, from_=1, to=100, font=("Arial", 15, "bold"), bg=GLASS_INPUT, fg=GLASS_TEXT, 
                      buttonbackground=GLASS_INPUT, relief="flat", command=calculate_logic)
spin_qty.pack(fill=tk.X, pady=6); spin_qty.bind("<KeyRelease>", lambda e: calculate_logic())

# 底部展示
tk.Label(main, text="💵 结果显示币种:", font=("Arial", 10), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W, pady=(8,2))
combo_out = ttk.Combobox(main, values=list(FULL_RATES.keys()), state="readonly", font=("Arial", 11))
combo_out.set("🇲🇾 MYR"); combo_out.pack(fill=tk.X, pady=(0, 15), ipady=6); combo_out.bind("<<ComboboxSelected>>", calculate_logic)

btn = tk.Button(main, text="精 准 运 营 算 账 (MAC 稳定版)", font=("Arial", 13, "bold"), bg="#F5F5F7", fg="#1C1C1E", relief="flat", command=calculate_logic, pady=10)
btn.pack(fill=tk.X, pady=(0, 10))

text_res = tk.Text(main, height=15, font=("Menlo", 12), state=tk.DISABLED, bg=GLASS_CARD, fg=GLASS_TEXT, relief="flat", padx=15, pady=15)
text_res.pack(fill=tk.X)

# 防闪退核心：延迟设置透明度并首次计算
def safe_start():
    try: root.attributes("-alpha", 0.96)
    except: pass
    calculate_logic()

root.after(500, safe_start)
root.mainloop()
