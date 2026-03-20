import tkinter as tk
from tkinter import ttk
import math

# --- 1. 基础配置与汇率 ---
FIXED_MY_RATE = 0.57 
FULL_RATES = {
    "🇨🇳 RMB": 1.0, "🇲🇾 MYR": 0.588, "🇺🇸 USD": 0.138, "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45, "🇭🇰 HKD": 1.08, "🇹🇭 THB": 4.85, "🇻🇳 VND": 3450.0,
    "🇧🇷 BRL": 0.72, "🇲🇽 MXN": 2.35, "🇦🇷 ARS": 120.0, "🇯🇵 JPY": 20.5,
    "🇵🇭 PHP": 7.8, "🇮🇩 IDR": 2150.0
}

# 稳定版深色主题配色
BG_MAIN = "#1E1E1E"    # 纯正深空灰
BG_CARD = "#2D2D2D"    # 卡片色
BG_INPUT = "#3D3D3D"   # 输入框色
FG_TEXT = "#FFFFFF"    # 白色文字
FG_SUB = "#AAAAAA"     # 辅助灰
ACCENT = "#007AFF"     # 苹果蓝

PLATFORM_COMMISSION = 0.0702 
FIXED_FEE_MYR = 0.54         
TARGET_DISCOUNT = 0.51       

CURR_MAP = {k: k.split()[-1] for k in FULL_RATES.keys()}
base_rates = {k: v for k, v in FULL_RATES.items()}

# --- 2. 核心逻辑 ---
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
        
        bundle_discount = 1.0
        if bundle_mode.get():
            if qty == 2: bundle_discount = 0.8
            elif qty >= 3: bundle_discount = 0.7
        
        total_prod_cost_myr = cost_rmb * qty * my_rate
        total_ship_myr = (ship_val / base_rates.get(ship_curr, 1.0)) * my_rate
        total_base_expenses = total_prod_cost_myr + total_ship_myr + FIXED_FEE_MYR
        
        divisor = 1 - PLATFORM_COMMISSION - margin_pct - ads_pct - aff_pct
        if divisor <= 0:
            show_res("⚠️ 运营占比过高，请调整！")
            return

        total_deal_price_myr = total_base_expenses / divisor
        to_out = lambda v: (v / my_rate) * base_rates.get(out_curr, 1.0)
        
        f_total_deal = to_out(total_deal_price_myr)
        f_total_orig = (f_total_deal / bundle_discount) / (1 - TARGET_DISCOUNT)
        profit_rmb = (total_deal_price_myr * margin_pct) / my_rate
        
        show_res(
            f"建议总原价： {f_total_orig:.2f} {suffix}\n"
            f"订单总实付： {f_total_deal:.2f} {suffix}\n"
            f"单件实付价： {f_total_deal/qty:.2f} {suffix}\n"
            f"----------------------------------\n"
            f"目标纯利 ({int(margin_pct*100)}%): {f_total_deal * margin_pct:.2f} {suffix}\n"
            f"预计总利润 (RMB): {profit_rmb:.2f} RMB\n"
            f"----------------------------------\n"
            f"广告支出 ({int(ads_pct*100)}%): {f_total_deal * ads_pct:.2f} {suffix}\n"
            f"达人分账 ({int(aff_pct*100)}%): {f_total_deal * aff_pct:.2f} {suffix}\n"
            f"平台扣费 (7.02%): {f_total_deal * PLATFORM_COMMISSION:.2f} {suffix}\n"
            f"----------------------------------\n"
            f"营销折扣： {int(bundle_discount*10) if bundle_mode.get() else 10} 折模式"
        )
    except: pass

def show_res(msg):
    text_res.config(state=tk.NORMAL)
    text_res.delete(1.0, tk.END)
    text_res.insert(tk.END, msg)
    text_res.config(state=tk.DISABLED)

# --- 3. UI 构造 ---
root = tk.Tk()
root.title("TikTok 定价助手 Pro")
root.geometry("820x940")
root.configure(bg=BG_MAIN)

# 自定义 Combobox 样式以适配深色
style = ttk.Style()
style.theme_use('default')
style.configure("TCombobox", fieldbackground=BG_INPUT, background=BG_INPUT, foreground=FG_TEXT, arrowcolor=FG_TEXT)
root.option_add('*TCombobox*Listbox.background', BG_INPUT)
root.option_add('*TCombobox*Listbox.foreground', FG_TEXT)

main = tk.Frame(root, padx=25, pady=20, bg=BG_MAIN)
main.pack(fill=tk.BOTH, expand=True)

# 1. 汇率区 (6列排布)
lf = tk.LabelFrame(main, text=" 实时汇率设置 ", padx=10, pady=10, bg=BG_MAIN, fg=FG_SUB, font=("Arial", 10, "bold"), bd=1, relief="flat")
lf.pack(fill=tk.X, pady=(0, 20))

rate_mode = tk.StringVar(value="fixed")
tk.Radiobutton(lf, text="手动模式", variable=rate_mode, value="manual", command=calculate_logic, bg=BG_MAIN, fg=FG_TEXT, selectcolor=BG_CARD, activebackground=BG_MAIN).grid(row=0, column=0, columnspan=2, sticky=tk.W)
tk.Radiobutton(lf, text="锁定 0.57", variable=rate_mode, value="fixed", command=calculate_logic, bg=BG_MAIN, fg=FG_TEXT, selectcolor=BG_CARD, activebackground=BG_MAIN).grid(row=0, column=2, columnspan=2, sticky=tk.W)

rate_vars = {}
for i, (curr, rate) in enumerate(FULL_RATES.items()):
    r, c = (i // 6) + 1, (i % 6) * 2
    tk.Label(lf, text=f"{curr}:", font=("Arial", 8), bg=BG_MAIN, fg=FG_TEXT).grid(row=r, column=c, sticky=tk.W, padx=2)
    v = tk.StringVar(value=str(rate))
    rate_vars[curr] = v
    e = tk.Entry(lf, width=7, textvariable=v, relief="flat", bg=BG_INPUT, fg=FG_TEXT, insertbackground="white", font=("Arial", 10))
    e.grid(row=r, column=c+1, padx=2, pady=4); e.bind("<KeyRelease>", lambda e: calculate_logic())

# 2. 运营层 (4列对齐)
op_frame = tk.Frame(main, bg=BG_MAIN)
op_frame.pack(fill=tk.X, pady=10)
for i in range(4): op_frame.columnconfigure(i, weight=1, uniform="group1")

def make_label(parent, text):
    return tk.Label(parent, text=text, font=("Arial", 11, "bold"), bg=BG_MAIN, fg=FG_TEXT)

# 利润
v_p = tk.Frame(op_frame, bg=BG_MAIN)
v_p.grid(row=0, column=0, sticky="ew")
make_label(v_p, "🎯 利润率").pack(anchor=tk.W)
combo_profit = ttk.Combobox(v_p, values=[f"{i}%" for i in range(16, 31)], state="readonly", font=("Arial", 11))
combo_profit.set("20%"); combo_profit.pack(fill=tk.X, pady=8, ipady=4); combo_profit.bind("<<ComboboxSelected>>", calculate_logic)

# 广告支出 (0-25%)
v_a = tk.Frame(op_frame, bg=BG_MAIN)
v_a.grid(row=0, column=1, sticky="ew", padx=15)
make_label(v_a, "🔥 广告支出").pack(anchor=tk.W)
combo_ads = ttk.Combobox(v_a, values=[f"{i}%" for i in range(26)], state="readonly", font=("Arial", 11))
combo_ads.set("0%"); combo_ads.pack(fill=tk.X, pady=8, ipady=4); combo_ads.bind("<<ComboboxSelected>>", calculate_logic)

# 达人佣金 (0-25%)
v_aff = tk.Frame(op_frame, bg=BG_MAIN)
v_aff.grid(row=0, column=2, sticky="ew", padx=(0,15))
make_label(v_aff, "🤝 达人佣金").pack(anchor=tk.W)
combo_aff = ttk.Combobox(v_aff, values=[f"{i}%" for i in range(26)], state="readonly", font=("Arial", 11))
combo_aff.set("0%"); combo_aff.pack(fill=tk.X, pady=8, ipady=4); combo_aff.bind("<<ComboboxSelected>>", calculate_logic)

# 多件多折
v_sw = tk.Frame(op_frame, bg=BG_MAIN)
v_sw.grid(row=0, column=3, sticky="ew")
make_label(v_sw, "📦 多件多折").pack(anchor=tk.W)
bundle_mode = tk.BooleanVar(value=True)
tk.Checkbutton(v_sw, text="启用(2件8折/3+件7折)", variable=bundle_mode, bg=BG_MAIN, fg=FG_SUB, selectcolor=BG_CARD, command=calculate_logic, font=("Arial", 10), activebackground=BG_MAIN).pack(pady=10, anchor=tk.W)

# 3. 输入层 (4列对齐)
in_frame = tk.Frame(main, bg=BG_MAIN)
in_frame.pack(fill=tk.X, pady=15)
for i in range(4): in_frame.columnconfigure(i, weight=1, uniform="group1")

# 成本
f1 = tk.Frame(in_frame, bg=BG_MAIN)
f1.grid(row=0, column=0, sticky="ew")
make_label(f1, "💰 单件成本(RMB)").pack(anchor=tk.W)
entry_cost = tk.Entry(f1, font=("Arial", 16, "bold"), relief="flat", bg=BG_INPUT, fg=FG_TEXT, insertbackground="white")
entry_cost.pack(fill=tk.X, pady=8); entry_cost.insert(0, "20"); entry_cost.bind("<KeyRelease>", lambda e: calculate_logic())

# 运费
f2 = tk.Frame(in_frame, bg=BG_MAIN)
f2.grid(row=0, column=1, sticky="ew", padx=15)
make_label(f2, "🚚 订单总运费").pack(anchor=tk.W)
entry_ship = tk.Entry(f2, font=("Arial", 16, "bold"), relief="flat", bg=BG_INPUT, fg=FG_TEXT, insertbackground="white")
entry_ship.pack(fill=tk.X, pady=8); entry_ship.insert(0, "1.95"); entry_ship.bind("<KeyRelease>", lambda e: calculate_logic())

# 币种
f3 = tk.Frame(in_frame, bg=BG_MAIN)
f3.grid(row=0, column=2, sticky="ew", padx=(0,15))
make_label(f3, "成本币种").pack(anchor=tk.W)
combo_ship = ttk.Combobox(f3, values=list(FULL_RATES.keys()), state="readonly", font=("Arial", 11))
combo_ship.set("🇲🇾 MYR"); combo_ship.pack(fill=tk.X, pady=8, ipady=4); combo_ship.bind("<<ComboboxSelected>>", calculate_logic)

# 数量 (步进器)
f4 = tk.Frame(in_frame, bg=BG_MAIN)
f4.grid(row=0, column=3, sticky="ew")
make_label(f4, "🔢 数量").pack(anchor=tk.W)
spin_qty = tk.Spinbox(f4, from_=1, to=100, font=("Arial", 16, "bold"), relief="flat", bg=BG_INPUT, fg=FG_TEXT, buttonbackground=BG_INPUT, command=calculate_logic)
spin_qty.pack(fill=tk.X, pady=8)
spin_qty.bind("<KeyRelease>", lambda e: calculate_logic())

# 底部展示币种
tk.Label(main, text="💵 结果显示币种:", font=("Arial", 10), bg=BG_MAIN, fg=FG_SUB).pack(anchor=tk.W, pady=(10,2))
combo_out = ttk.Combobox(main, values=list(FULL_RATES.keys()), state="readonly", font=("Arial", 11))
combo_out.set("🇲🇾 MYR"); combo_out.pack(fill=tk.X, pady=(0, 20), ipady=6); combo_out.bind("<<ComboboxSelected>>", calculate_logic)

# 计算按钮
btn = tk.Button(main, text="计 算 运 营 定 价", font=("Arial", 14, "bold"), bg=ACCENT, fg=FG_TEXT, relief="flat", command=calculate_logic, pady=12, activebackground="#0056b3", highlightthickness=0)
btn.pack(fill=tk.X)

# 结果展示
text_res = tk.Text(main, height=14, font=("Menlo", 12), state=tk.DISABLED, bg=BG_CARD, fg=FG_TEXT, relief="flat", padx=15, pady=15, bd=0)
text_res.pack(fill=tk.X, pady=(20, 0))

calculate_logic()
root.mainloop()
