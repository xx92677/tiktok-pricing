import tkinter as tk
from tkinter import ttk
import math

# --- 1. 核心财务配置 ---
FIXED_MY_RATE = 0.57 
FULL_RATES = {
    "🇨🇳 RMB": 1.0, "🇲🇾 MYR": 0.588, "🇺🇸 USD": 0.138, "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45, "🇭🇰 HKD": 1.08, "🇹🇭 THB": 4.85, "🇻🇳 VND": 3450.0,
    "🇧🇷 BRL": 0.72, "🇲🇽 MXN": 2.35, "🇦🇷 ARS": 120.0, "🇯🇵 JPY": 20.5,
    "🇵🇭 PHP": 7.8, "🇮🇩 IDR": 2150.0
}

# 深度黑暗模式色板 (手动配置，不依赖系统主题)
HEX_BG = "#1A1A1A"      # 背景
HEX_CARD = "#252525"    # 卡片/结果框
HEX_INPUT = "#333333"   # 输入框
HEX_TEXT = "#FFFFFF"    # 主文字
HEX_SUB = "#999999"     # 辅助文字
HEX_BTN = "#444444"     # 按钮颜色

PLATFORM_COMMISSION = 0.0702 
FIXED_FEE_MYR = 0.54         
TARGET_DISCOUNT = 0.51       

CURR_MAP = {k: k.split()[-1] for k in FULL_RATES.keys()}
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
        
        bundle_discount = 1.0
        if bundle_mode.get():
            if qty == 2: bundle_discount = 0.8
            elif qty >= 3: bundle_discount = 0.7
        
        total_prod_cost_myr = cost_rmb * qty * my_rate
        total_ship_myr = (ship_val / base_rates.get(ship_curr, 1.0)) * my_rate
        total_base_expenses = total_prod_cost_myr + total_ship_myr + FIXED_FEE_MYR
        
        divisor = 1 - PLATFORM_COMMISSION - margin_pct - ads_pct - aff_pct
        if divisor <= 0:
            show_res("⚠️ 运营占比总和过高(>100%)")
            return

        total_deal_price_myr = total_base_expenses / divisor
        to_out = lambda v: (v / my_rate) * base_rates.get(out_curr, 1.0)
        
        f_total_deal = to_out(total_deal_price_myr)
        f_total_orig = (f_total_deal / bundle_discount) / (1 - TARGET_DISCOUNT)
        profit_rmb = (total_deal_price_myr * margin_pct) / my_rate
        
        res_str = (
            f"建议总原价： {f_total_orig:.2f} {suffix}\n"
            f"订单总售价： {f_total_deal:.2f} {suffix}\n"
            f"单件平均价： {f_total_deal/qty:.2f} {suffix}\n"
            f"----------------------------------\n"
            f"目标利润 ({int(margin_pct*100)}%): {f_total_deal * margin_pct:.2f} {suffix}\n"
            f"实拿利润 (RMB): {profit_rmb:.2f} RMB\n"
            f"----------------------------------\n"
            f"广告预估 ({int(ads_pct*100)}%): {f_total_deal * ads_pct:.2f} {suffix}\n"
            f"达人分销 ({int(aff_pct*100)}%): {f_total_deal * aff_pct:.2f} {suffix}\n"
            f"平台抽成 (7.02%): {f_total_deal * PLATFORM_COMMISSION:.2f} {suffix}"
        )
        show_res(res_str)
    except: pass

def show_res(msg):
    text_res.config(state="normal")
    text_res.delete(1.0, tk.END)
    text_res.insert(tk.END, msg)
    text_res.config(state="disabled")

# --- 3. UI 构造 ---
root = tk.Tk()
root.title("TikTok 定价助手 Pro")
root.geometry("820x940")
root.configure(bg=HEX_BG)

# 尽量避免手动缩放，让 Mac 系统自行处理
# 不再设置 root.attributes("-alpha")

main = tk.Frame(root, padx=25, pady=20, bg=HEX_BG)
main.pack(fill=tk.BOTH, expand=True)

# 汇率区 (6列大字)
lf = tk.LabelFrame(main, text=" 实时汇率设置 ", padx=10, pady=10, bg=HEX_BG, fg=HEX_SUB, font=("Arial", 10, "bold"), bd=1)
lf.pack(fill=tk.X, pady=(0, 20))

rate_mode = tk.StringVar(value="fixed")
tk.Radiobutton(lf, text="手动模式", variable=rate_mode, value="manual", command=calculate_logic, bg=HEX_BG, fg=HEX_TEXT, selectcolor=HEX_CARD, activebackground=HEX_BG).grid(row=0, column=0, columnspan=2, sticky="w")
tk.Radiobutton(lf, text="锁定 0.57", variable=rate_mode, value="fixed", command=calculate_logic, bg=HEX_BG, fg=HEX_TEXT, selectcolor=HEX_CARD, activebackground=HEX_BG).grid(row=0, column=2, columnspan=2, sticky="w", padx=20)

rate_vars = {}
for i, (curr, rate) in enumerate(FULL_RATES.items()):
    r, c = (i // 6) + 1, (i % 6) * 2
    tk.Label(lf, text=f"{curr}:", font=("Arial", 12), bg=HEX_BG, fg=HEX_TEXT).grid(row=r, column=c, sticky="w", padx=4, pady=5)
    v = tk.StringVar(value=str(rate))
    rate_vars[curr] = v
    e = tk.Entry(lf, width=7, textvariable=v, relief="flat", bg=HEX_INPUT, fg=HEX_TEXT, insertbackground="white", font=("Arial", 11))
    e.grid(row=r, column=c+1, padx=4, pady=5); e.bind("<KeyRelease>", lambda e: calculate_logic())

# 运营层 (4列等宽)
op_frame = tk.Frame(main, bg=HEX_BG)
op_frame.pack(fill=tk.X, pady=10)
for i in range(4): op_frame.columnconfigure(i, weight=1, uniform="g1")

def ml(parent, text): return tk.Label(parent, text=text, font=("Arial", 11, "bold"), bg=HEX_BG, fg=HEX_TEXT)

v_p = tk.Frame(op_frame, bg=HEX_BG); v_p.grid(row=0, column=0, sticky="ew")
ml(v_p, "🎯 利润率").pack(anchor="w")
combo_profit = ttk.Combobox(v_p, values=[f"{i}%" for i in range(16, 31)], state="readonly", font=("Arial", 11))
combo_profit.set("20%"); combo_profit.pack(fill="x", pady=8, ipady=3); combo_profit.bind("<<ComboboxSelected>>", calculate_logic)

v_a = tk.Frame(op_frame, bg=HEX_BG); v_a.grid(row=0, column=1, sticky="ew", padx=15)
ml(v_a, "🔥 广告支出").pack(anchor="w")
combo_ads = ttk.Combobox(v_a, values=[f"{i}%" for i in range(26)], state="readonly", font=("Arial", 11))
combo_ads.set("0%"); combo_ads.pack(fill="x", pady=8, ipady=3); combo_ads.bind("<<ComboboxSelected>>", calculate_logic)

v_aff = tk.Frame(op_frame, bg=HEX_BG); v_aff.grid(row=0, column=2, sticky="ew", padx=(0,15))
ml(v_aff, "🤝 达人佣金").pack(anchor="w")
combo_aff = ttk.Combobox(v_aff, values=[f"{i}%" for i in range(26)], state="readonly", font=("Arial", 11))
combo_aff.set("0%"); combo_aff.pack(fill="x", pady=8, ipady=3); combo_aff.bind("<<ComboboxSelected>>", calculate_logic)

v_sw = tk.Frame(op_frame, bg=HEX_BG); v_sw.grid(row=0, column=3, sticky="ew")
ml(v_sw, "📦 多件多折").pack(anchor="w")
bundle_mode = tk.BooleanVar(value=True)
tk.Checkbutton(v_sw, text="启用优惠", variable=bundle_mode, bg=HEX_BG, fg=HEX_SUB, selectcolor=HEX_CARD, activebackground=HEX_BG, command=calculate_logic, font=("Arial", 11)).pack(pady=10, anchor="w")

# 输入层 (4列对齐)
in_frame = tk.Frame(main, bg=HEX_BG)
in_frame.pack(fill=tk.X, pady=10)
for i in range(4): in_frame.columnconfigure(i, weight=1, uniform="g1")

f1 = tk.Frame(in_frame, bg=HEX_BG); f1.grid(row=0, column=0, sticky="ew")
ml(f1, "💰 成本(RMB)").pack(anchor="w")
entry_cost = tk.Entry(f1, font=("Arial", 15, "bold"), relief="flat", bg=HEX_INPUT, fg=HEX_TEXT, insertbackground="white")
entry_cost.pack(fill="x", pady=8); entry_cost.insert(0, "20"); entry_cost.bind("<KeyRelease>", lambda e: calculate_logic())

f2 = tk.Frame(in_frame, bg=HEX_BG); f2.grid(row=0, column=1, sticky="ew", padx=15)
ml(f2, "🚚 订单运费").pack(anchor="w")
entry_ship = tk.Entry(f2, font=("Arial", 15, "bold"), relief="flat", bg=HEX_INPUT, fg=HEX_TEXT, insertbackground="white")
entry_ship.pack(fill="x", pady=8); entry_ship.insert(0, "1.95"); entry_ship.bind("<KeyRelease>", lambda e: calculate_logic())

f3 = tk.Frame(in_frame, bg=HEX_BG); f3.grid(row=0, column=2, sticky="ew", padx=(0,15))
ml(f3, "成本币种").pack(anchor="w")
combo_ship = ttk.Combobox(f3, values=list(FULL_RATES.keys()), state="readonly", font=("Arial", 11))
combo_ship.set("🇲🇾 MYR"); combo_ship.pack(fill="x", pady=8, ipady=3); combo_ship.bind("<<ComboboxSelected>>", calculate_logic)

f4 = tk.Frame(in_frame, bg=HEX_BG); f4.grid(row=0, column=3, sticky="ew")
ml(f4, "🔢 数量").pack(anchor="w")
# 使用 tk.Spinbox (更稳定)
spin_qty = tk.Spinbox(f4, from_=1, to=100, font=("Arial", 15, "bold"), bg=HEX_INPUT, fg=HEX_TEXT, buttonbackground=HEX_INPUT, relief="flat", command=calculate_logic)
spin_qty.pack(fill="x", pady=8); spin_qty.bind("<KeyRelease>", lambda e: calculate_logic())

# 底部展示
tk.Label(main, text="💵 结果显示币种:", font=("Arial", 10), bg=HEX_BG, fg=HEX_SUB).pack(anchor="w", pady=(10,2))
combo_out = ttk.Combobox(main, values=list(FULL_RATES.keys()), state="readonly", font=("Arial", 11))
combo_out.set("🇲🇾 MYR"); combo_out.pack(fill="x", pady=(0, 20), ipady=6); combo_out.bind("<<ComboboxSelected>>", calculate_logic)

btn = tk.Button(main, text="计 算 运 营 定 价", font=("Arial", 14, "bold"), bg=HEX_BTN, fg=HEX_TEXT, relief="flat", command=calculate_logic, pady=12, activebackground="#555555", highlightthickness=0)
btn.pack(fill="x")

text_res = tk.Text(main, height=14, font=("Menlo", 12), bg=HEX_CARD, fg=HEX_TEXT, relief="flat", padx=15, pady=15, state="disabled", highlightbackground=HEX_SUB)
text_res.pack(fill="x", pady=(20, 0))

# 延迟 100 毫秒初次计算，确保组件加载完毕
root.after(100, calculate_logic)
root.mainloop()
