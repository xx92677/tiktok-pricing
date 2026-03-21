import tkinter as tk
from tkinter import ttk
import math
import subprocess

# --- 1. 财务与基础配置 ---
FIXED_MY_RATE = 0.57 
FULL_RATES = {
    "🇨🇳 RMB": 1.0, "🇲🇾 MYR": 0.588, "🇺🇸 USD": 0.138, "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45, "🇭🇰 HKD": 1.08, "🇹🇭 THB": 4.85, "🇻🇳 VND": 3450.0,
    "🇧🇷 BRL": 0.72, "🇲🇽 MXN": 2.35, "🇦🇷 ARS": 120.0, "🇯🇵 JPY": 20.5,
    "🇵🇭 PHP": 7.8, "🇮🇩 IDR": 2150.0
}

# --- 2. 主题配色方案 ---
THEMES = {
    "DARK": {
        "bg": "#1A1A1A", "card": "#252525", "input": "#333333",
        "text": "#FFFFFF", "sub": "#999999", "btn": "#444444", "border": "#404040"
    },
    "LIGHT": {
        "bg": "#F5F5F7", "card": "#FFFFFF", "input": "#EBEBEB",
        "text": "#000000", "sub": "#86868B", "btn": "#E2E2E2", "border": "#D2D2D7"
    }
}

PLATFORM_COMMISSION = 0.0702 
FIXED_FEE_MYR = 0.54         
TARGET_DISCOUNT = 0.51       

CURR_MAP = {k: k.split()[-1] for k in FULL_RATES.keys()}
base_rates = {k: v for k, v in FULL_RATES.items()}

# --- 3. 核心功能逻辑 ---
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
            show_res("⚠️ 运营占比总和过高 (>100%)")
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
            f"预计纯利 (RMB): {profit_rmb:.2f} RMB\n"
            f"----------------------------------\n"
            f"流量支出 ({int(ads_pct*100)}%): {f_total_deal * ads_pct:.2f} {suffix}\n"
            f"达人分摊 ({int(aff_pct*100)}%): {f_total_deal * aff_pct:.2f} {suffix}\n"
            f"平台抽佣 (7.02%): {f_total_deal * PLATFORM_COMMISSION:.2f} {suffix}"
        )
        show_res(res_str)
    except: pass

def show_res(msg):
    text_res.config(state="normal")
    text_res.delete(1.0, tk.END)
    text_res.insert(tk.END, msg)
    text_res.config(state="disabled")

# --- 4. 自动主题切换引擎 ---
current_mode = None

def get_macos_mode():
    """检测 macOS 是否处于深色模式"""
    try:
        cmd = 'defaults read -g AppleInterfaceStyle'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        return "DARK" if out.decode('utf-8').strip() == "Dark" else "LIGHT"
    except:
        return "LIGHT"

def apply_theme():
    global current_mode
    mode = get_macos_mode()
    if mode == current_mode:
        root.after(2000, apply_theme)
        return
    
    current_mode = mode
    c = THEMES[mode]
    
    # 更新根窗口和主框架
    root.configure(bg=c["bg"])
    main.configure(bg=c["bg"])
    
    # 更新所有容器和标签
    for widget in root.winfo_children():
        update_widget_color(widget, c)
    
    # 结果框特殊处理
    text_res.configure(bg=c["card"], fg=c["text"], highlightbackground=c["sub"])
    
    # 下拉框样式更新
    style.configure("TCombobox", fieldbackground=c["input"], background=c["input"], foreground=c["text"])
    
    root.after(2000, apply_theme)

def update_widget_color(parent, c):
    """递归更新所有组件颜色"""
    try:
        if isinstance(parent, (tk.Frame, tk.LabelFrame)):
            parent.configure(bg=c["bg"])
            if isinstance(parent, tk.LabelFrame):
                parent.configure(fg=c["sub"])
        elif isinstance(parent, tk.Label):
            parent.configure(bg=c["bg"], fg=c["text"])
        elif isinstance(parent, tk.Entry):
            parent.configure(bg=c["input"], fg=c["text"], insertbackground=c["text"])
        elif isinstance(parent, tk.Radiobutton):
            parent.configure(bg=c["bg"], fg=c["text"], selectcolor=c["card"], activebackground=c["bg"])
        elif isinstance(parent, tk.Checkbutton):
            parent.configure(bg=c["bg"], fg=c["sub"], selectcolor=c["card"], activebackground=c["bg"])
        elif isinstance(parent, tk.Button):
            parent.configure(bg=c["btn"], fg=c["text"], activebackground=c["input"])
        elif isinstance(parent, tk.Spinbox):
            parent.configure(bg=c["input"], fg=c["text"], buttonbackground=c["input"])
        
        for child in parent.winfo_children():
            update_widget_color(child, c)
    except: pass

# --- 5. UI 构造 ---
root = tk.Tk()
root.title("TikTok 定价助手 Pro")
root.geometry("820x940")

style = ttk.Style()
style.theme_use('default')

main = tk.Frame(root, padx=25, pady=20)
main.pack(fill=tk.BOTH, expand=True)

# --- 汇率面板 (6列排布) ---
lf = tk.LabelFrame(main, text=" 实时汇率设置 ", padx=10, pady=10, font=("Arial", 10, "bold"), bd=1)
lf.pack(fill=tk.X, pady=(0, 20))

rate_mode = tk.StringVar(value="fixed")
tk.Radiobutton(lf, text="手动模式", variable=rate_mode, value="manual", command=calculate_logic).grid(row=0, column=0, columnspan=2, sticky="w")
tk.Radiobutton(lf, text="锁定 0.57", variable=rate_mode, value="fixed", command=calculate_logic).grid(row=0, column=2, columnspan=2, sticky="w", padx=20)

rate_vars = {}
for i, (curr, rate) in enumerate(FULL_RATES.items()):
    r, c = (i // 6) + 1, (i % 6) * 2
    tk.Label(lf, text=f"{curr}:", font=("Arial", 12)).grid(row=r, column=c, sticky="w", padx=4, pady=5)
    v = tk.StringVar(value=str(rate))
    rate_vars[curr] = v
    e = tk.Entry(lf, width=7, textvariable=v, relief="flat", font=("Arial", 11))
    e.grid(row=r, column=c+1, padx=4, pady=5); e.bind("<KeyRelease>", lambda e: calculate_logic())

# --- 运营层 (4列对齐) ---
op_frame = tk.Frame(main)
op_frame.pack(fill=tk.X, pady=10)
for i in range(4): op_frame.columnconfigure(i, weight=1, uniform="g1")

def ml(parent, text): return tk.Label(parent, text=text, font=("Arial", 11, "bold"))

# 利润/广告/达人/开关
v_p = tk.Frame(op_frame); v_p.grid(row=0, column=0, sticky="ew")
ml(v_p, "🎯 利润率").pack(anchor="w")
combo_profit = ttk.Combobox(v_p, values=[f"{i}%" for i in range(16, 31)], state="readonly", font=("Arial", 11))
combo_profit.set("20%"); combo_profit.pack(fill="x", pady=8, ipady=3); combo_profit.bind("<<ComboboxSelected>>", calculate_logic)

v_a = tk.Frame(op_frame); v_a.grid(row=0, column=1, sticky="ew", padx=15)
ml(v_a, "🔥 广告支出").pack(anchor="w")
combo_ads = ttk.Combobox(v_a, values=[f"{i}%" for i in range(26)], state="readonly", font=("Arial", 11))
combo_ads.set("0%"); combo_ads.pack(fill="x", pady=8, ipady=3); combo_ads.bind("<<ComboboxSelected>>", calculate_logic)

v_aff = tk.Frame(op_frame); v_aff.grid(row=0, column=2, sticky="ew", padx=(0,15))
ml(v_aff, "🤝 达人佣金").pack(anchor="w")
combo_aff = ttk.Combobox(v_aff, values=[f"{i}%" for i in range(26)], state="readonly", font=("Arial", 11))
combo_aff.set("0%"); combo_aff.pack(fill="x", pady=8, ipady=3); combo_aff.bind("<<ComboboxSelected>>", calculate_logic)

v_sw = tk.Frame(op_frame); v_sw.grid(row=0, column=3, sticky="ew")
ml(v_sw, "📦 多件多折").pack(anchor="w")
bundle_mode = tk.BooleanVar(value=True)
tk.Checkbutton(v_sw, text="启用优惠", variable=bundle_mode, command=calculate_logic, font=("Arial", 11)).pack(pady=10, anchor="w")

# --- 输入层 (4列对齐) ---
in_frame = tk.Frame(main)
in_frame.pack(fill=tk.X, pady=10)
for i in range(4): in_frame.columnconfigure(i, weight=1, uniform="g1")

f1 = tk.Frame(in_frame); f1.grid(row=0, column=0, sticky="ew")
ml(f1, "💰 成本(RMB)").pack(anchor="w")
entry_cost = tk.Entry(f1, font=("Arial", 15, "bold"), relief="flat")
entry_cost.pack(fill="x", pady=8); entry_cost.insert(0, "20"); entry_cost.bind("<KeyRelease>", lambda e: calculate_logic())

f2 = tk.Frame(in_frame); f2.grid(row=0, column=1, sticky="ew", padx=15)
ml(f2, "🚚 订单运费").pack(anchor="w")
entry_ship = tk.Entry(f2, font=("Arial", 15, "bold"), relief="flat")
entry_ship.pack(fill="x", pady=8); entry_ship.insert(0, "1.95"); entry_ship.bind("<KeyRelease>", lambda e: calculate_logic())

f3 = tk.Frame(in_frame); f3.grid(row=0, column=2, sticky="ew", padx=(0,15))
ml(f3, "成本币种").pack(anchor="w")
combo_ship = ttk.Combobox(f3, values=list(FULL_RATES.keys()), state="readonly", font=("Arial", 11))
combo_ship.set("🇲🇾 MYR"); combo_ship.pack(fill="x", pady=8, ipady=3); combo_ship.bind("<<ComboboxSelected>>", calculate_logic)

f4 = tk.Frame(in_frame); f4.grid(row=0, column=3, sticky="ew")
ml(f4, "🔢 数量").pack(anchor="w")
spin_qty = tk.Spinbox(f4, from_=1, to=100, font=("Arial", 15, "bold"), relief="flat", command=calculate_logic)
spin_qty.pack(fill="x", pady=8); spin_qty.bind("<KeyRelease>", lambda e: calculate_logic())

# --- 底部 ---
tk.Label(main, text="💵 结果显示币种:", font=("Arial", 10)).pack(anchor="w", pady=(10,2))
combo_out = ttk.Combobox(main, values=list(FULL_RATES.keys()), state="readonly", font=("Arial", 11))
combo_out.set("🇲🇾 MYR"); combo_out.pack(fill="x", pady=(0, 20), ipady=6); combo_out.bind("<<ComboboxSelected>>", calculate_logic)

btn = tk.Button(main, text="计 算 运 营 定 价", font=("Arial", 14, "bold"), relief="flat", command=calculate_logic, pady=12)
btn.pack(fill="x")

text_res = tk.Text(main, height=14, font=("Menlo", 12), relief="flat", padx=15, pady=15, state="disabled")
text_res.pack(fill=tk.X, pady=(20, 0))

# 启动引擎
apply_theme()
calculate_logic()
root.mainloop()
