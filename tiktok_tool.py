import tkinter as tk
from tkinter import ttk
import math

# --- 1. 基础财务配置 ---
FIXED_MY_RATE = 0.57 
FULL_RATES = {
    "🇨🇳 RMB": 1.0, "🇲🇾 MYR": 0.588, "🇺🇸 USD": 0.138, "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45, "🇭🇰 HKD": 1.08, "🇹🇭 THB": 4.85, "🇻🇳 VND": 3450.0,
    "🇧🇷 BRL": 0.72, "🇲🇽 MXN": 2.35, "🇦🇷 ARS": 120.0, "🇯🇵 JPY": 20.5,
    "🇵🇭 PHP": 7.8, "🇮🇩 IDR": 2150.0
}

# 黑暗模式极致色板
BG_DARK = "#1C1C1E"       # 苹果深空黑
CARD_DARK = "#2C2C2E"     # 卡片色
INPUT_DARK = "#3A3A3C"    # 输入框色
TEXT_WHITE = "#FFFFFF"    # 纯白
TEXT_GRAY = "#8E8E93"     # 辅助灰
MAC_BLUE = "#0A84FF"      # macOS 黑暗模式标准蓝色

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
            show_res("⚠️ 占比总和过高！")
            return

        total_deal_price_myr = total_base_expenses / divisor
        to_out = lambda v: (v / my_rate) * base_rates.get(out_curr, 1.0)
        
        f_total_deal = to_out(total_deal_price_myr)
        f_total_orig = (f_total_deal / bundle_discount) / (1 - TARGET_DISCOUNT)
        profit_rmb = (total_deal_price_myr * margin_pct) / my_rate
        
        show_res(
            f"建议总原价： {f_total_orig:.2f} {suffix}\n"
            f"订单总实付： {f_total_deal:.2f} {suffix}\n"
            f"单件平均价： {f_total_deal/qty:.2f} {suffix}\n"
            f"----------------------------------\n"
            f"目标利润 ({int(margin_pct*100)}%): {f_total_deal * margin_pct:.2f} {suffix}\n"
            f"预计利润 (RMB): {profit_rmb:.2f} RMB\n"
            f"----------------------------------\n"
            f"流量支出 ({int(ads_pct*100)}%): {f_total_deal * ads_pct:.2f} {suffix}\n"
            f"达人分账 ({int(aff_pct*100)}%): {f_total_deal * aff_pct:.2f} {suffix}\n"
            f"平台抽佣 (7.02%): {f_total_deal * PLATFORM_COMMISSION:.2f} {suffix}"
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
root.geometry("820x960")
root.configure(bg=BG_DARK)

# 强制开启 Retina 渲染
if root.tk.call('tk', 'windowingsystem') == 'aqua':
    root.tk.call('tk', 'scaling', 2.0)

style = ttk.Style(root)
style.theme_use('aqua')

main = tk.Frame(root, padx=25, pady=20, bg=BG_DARK)
main.pack(fill=tk.BOTH, expand=True)

# --- 汇率区 (大字体) ---
lf = tk.LabelFrame(main, text=" 实时汇率设置 (RMB 基准) ", padx=10, pady=10, bg=BG_DARK, fg=TEXT_GRAY, font=("Arial", 10, "bold"))
lf.pack(fill=tk.X, pady=(0, 15))

rate_mode = tk.StringVar(value="fixed")
tk.Radiobutton(lf, text="手动模式", variable=rate_mode, value="manual", command=calculate_logic, bg=BG_DARK, fg=TEXT_WHITE, selectcolor=CARD_DARK, activebackground=BG_DARK).grid(row=0, column=0, columnspan=2, sticky=tk.W)
tk.Radiobutton(lf, text="锁定 0.57", variable=rate_mode, value="fixed", command=calculate_logic, bg=BG_DARK, fg=TEXT_WHITE, selectcolor=CARD_DARK, activebackground=BG_DARK).grid(row=0, column=2, columnspan=2, sticky=tk.W, padx=20)

rate_vars = {}
for i, (curr, rate) in enumerate(FULL_RATES.items()):
    r, c = (i // 6) + 1, (i % 6) * 2
    tk.Label(lf, text=f"{curr}:", font=("Arial", 12), bg=BG_DARK, fg=TEXT_WHITE).grid(row=r, column=c, sticky=tk.W, padx=4, pady=5)
    v = tk.StringVar(value=str(rate))
    rate_vars[curr] = v
    e = tk.Entry(lf, width=7, textvariable=v, relief="flat", bg=INPUT_DARK, fg=TEXT_WHITE, insertbackground="white", font=("Arial", 12))
    e.grid(row=r, column=c+1, padx=4, pady=5); e.bind("<KeyRelease>", lambda e: calculate_logic())

# --- 运营与输入层 ---
op_frame = tk.Frame(main, bg=BG_DARK)
op_frame.pack(fill=tk.X, pady=15)
for i in range(4): op_frame.columnconfigure(i, weight=1, uniform="group1")

def make_label(parent, text):
    return tk.Label(parent, text=text, font=("Arial", 11, "bold"), bg=BG_DARK, fg=TEXT_WHITE)

# 1. 利润
v_p = tk.Frame(op_frame, bg=BG_DARK)
v_p.grid(row=0, column=0, sticky="ew")
make_label(v_p, "🎯 利润率").pack(anchor=tk.W)
combo_profit = ttk.Combobox(v_p, values=[f"{i}%" for i in range(16, 31)], state="readonly")
combo_profit.set("20%"); combo_profit.pack(fill=tk.X, pady=8, ipady=3); combo_profit.bind("<<ComboboxSelected>>", calculate_logic)

# 2. 广告
v_a = tk.Frame(op_frame, bg=BG_DARK)
v_a.grid(row=0, column=1, sticky="ew", padx=15)
make_label(v_a, "🔥 广告支出").pack(anchor=tk.W)
combo_ads = ttk.Combobox(v_a, values=[f"{i}%" for i in range(26)], state="readonly")
combo_ads.set("0%"); combo_ads.pack(fill=tk.X, pady=8, ipady=3); combo_ads.bind("<<ComboboxSelected>>", calculate_logic)

# 3. 达人
v_aff = tk.Frame(op_frame, bg=BG_DARK)
v_aff.grid(row=0, column=2, sticky="ew", padx=(0,15))
make_label(v_aff, "🤝 达人佣金").pack(anchor=tk.W)
combo_aff = ttk.Combobox(v_aff, values=[f"{i}%" for i in range(26)], state="readonly")
combo_aff.set("0%"); combo_aff.pack(fill=tk.X, pady=8, ipady=3); combo_aff.bind("<<ComboboxSelected>>", calculate_logic)

# 4. 开关
v_sw = tk.Frame(op_frame, bg=BG_DARK)
v_sw.grid(row=0, column=3, sticky="ew")
make_label(v_sw, "📦 多件多折").pack(anchor=tk.W)
bundle_mode = tk.BooleanVar(value=True)
tk.Checkbutton(v_sw, text="启用优惠", variable=bundle_mode, bg=BG_DARK, fg=TEXT_GRAY, selectcolor=CARD_DARK, command=calculate_logic, font=("Arial", 11), activebackground=BG_DARK).pack(pady=10, anchor=tk.W)

# 核心输入
in_frame = tk.Frame(main, bg=BG_DARK)
in_frame.pack(fill=tk.X, pady=15)
for i in range(4): in_frame.columnconfigure(i, weight=1, uniform="group1")

# 成本/运费/币种/数量
f1 = tk.Frame(in_frame, bg=BG_DARK); f1.grid(row=0, column=0, sticky="ew")
make_label(f1, "💰 成本(RMB)").pack(anchor=tk.W)
entry_cost = tk.Entry(f1, font=("Arial", 16, "bold"), relief="flat", bg=INPUT_DARK, fg=TEXT_WHITE, insertbackground="white")
entry_cost.pack(fill=tk.X, pady=8); entry_cost.insert(0, "20"); entry_cost.bind("<KeyRelease>", lambda e: calculate_logic())

f2 = tk.Frame(in_frame, bg=BG_DARK); f2.grid(row=0, column=1, sticky="ew", padx=15)
make_label(f2, "🚚 订单运费").pack(anchor=tk.W)
entry_ship = tk.Entry(f2, font=("Arial", 16, "bold"), relief="flat", bg=INPUT_DARK, fg=TEXT_WHITE, insertbackground="white")
entry_ship.pack(fill=tk.X, pady=8); entry_ship.insert(0, "1.95"); entry_ship.bind("<KeyRelease>", lambda e: calculate_logic())

f3 = tk.Frame(in_frame, bg=BG_DARK); f3.grid(row=0, column=2, sticky="ew", padx=(0,15))
make_label(f3, "运费币种").pack(anchor=tk.W)
combo_ship = ttk.Combobox(f3, values=list(FULL_RATES.keys()), state="readonly")
combo_ship.set("🇲🇾 MYR"); combo_ship.pack(fill=tk.X, pady=8, ipady=3); combo_ship.bind("<<ComboboxSelected>>", calculate_logic)

f4 = tk.Frame(in_frame, bg=BG_DARK); f4.grid(row=0, column=3, sticky="ew")
make_label(f4, "🔢 数量").pack(anchor=tk.W)
spin_qty = tk.Spinbox(f4, from_=1, to=100, font=("Arial", 16, "bold"), relief="flat", bg=INPUT_DARK, fg=TEXT_WHITE, buttonbackground=INPUT_DARK, command=calculate_logic)
spin_qty.pack(fill=tk.X, pady=8); spin_qty.bind("<KeyRelease>", lambda e: calculate_logic())

# --- 按钮优化：黑暗模式下的 Apple 蓝 ---
btn_container = tk.Frame(main, bg=BG_DARK, pady=20)
btn_container.pack(fill=tk.X)

btn = tk.Button(
    btn_container, 
    text="计 算 运 营 定 价", 
    font=("Arial", 14, "bold"), 
    bg=MAC_BLUE,            # 苹果蓝
    fg=TEXT_WHITE,          # 纯白字
    activebackground="#005FB8", # 点击时的深蓝色
    activeforeground=TEXT_WHITE,
    relief="flat",          # 去掉边框感
    highlightthickness=0,   # 去掉 Mac 默认的光晕
    bd=0,                   # 边框宽度为0
    pady=15,                # 增加上下内边距，让它更有实体感
    cursor="hand2",         # 鼠标悬停变手型
    command=calculate_logic
)
btn.pack(fill=tk.X)

# 结果展示
text_res = tk.Text(main, height=14, font=("Menlo", 13), state=tk.DISABLED, bg=CARD_DARK, fg=TEXT_WHITE, relief="flat", padx=15, pady=15)
text_res.pack(fill=tk.X)

calculate_logic()
root.mainloop()
