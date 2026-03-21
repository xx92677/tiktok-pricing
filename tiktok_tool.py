import tkinter as tk
from tkinter import ttk
import math
import subprocess

# --- 1. 基础财务配置 ---
FIXED_MY_RATE = 0.57 
FULL_RATES = {
    "🇨🇳 RMB": 1.0, "🇲🇾 MYR": 0.588, "🇺🇸 USD": 0.138, "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45, "🇭🇰 HKD": 1.08, "🇹🇭 THB": 4.85, "🇻🇳 VND": 3450.0,
    "🇧🇷 BRL": 0.72, "🇲🇽 MXN": 2.35, "🇦🇷 ARS": 120.0, "🇯🇵 JPY": 20.5,
    "🇵🇭 PHP": 7.8, "🇮🇩 IDR": 2150.0
}

# --- 2. 深度主题色板 ---
THEMES = {
    "DARK": {
        "bg": "#1E1E1E", "card": "#2D2D2D", "input": "#3D3D3D",
        "text": "#F5F5F7", "sub": "#A1A1A6", "btn": "#48484A", 
        "accent": "#0A84FF", "res_bg": "#161617"
    },
    "LIGHT": {
        "bg": "#F5F5F7", "card": "#FFFFFF", "input": "#FFFFFF",
        "text": "#1D1D1F", "sub": "#86868B", "btn": "#E5E5EA", 
        "accent": "#007AFF", "res_bg": "#F2F2F7"
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
            show_res("⚠️ 占比总和过高 (>100%)")
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
            f"达人分账 ({int(aff_pct*100)}%): {f_total_deal * aff_pct:.2f} {suffix}\n"
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
    try:
        cmd = 'defaults read -g AppleInterfaceStyle'
        out = subprocess.check_output(cmd, shell=True).decode().strip()
        return "DARK" if out == "Dark" else "LIGHT"
    except: return "LIGHT"

def update_theme():
    global current_mode
    mode = get_macos_mode()
    if mode == current_mode:
        root.after(1500, update_theme)
        return
    
    current_mode = mode
    c = THEMES[mode]
    
    root.configure(bg=c["bg"])
    main.configure(bg=c["bg"])
    
    # 深度配置 ttk 样式 (让选项框变漂亮)
    style.configure("TCombobox", fieldbackground=c["input"], background=c["bg"], foreground=c["text"])
    root.option_add('*TCombobox*Listbox.background', c["input"])
    root.option_add('*TCombobox*Listbox.foreground', c["text"])
    root.option_add('*TCombobox*Listbox.selectBackground', c["accent"])
    
    # 递归更新颜色
    def apply_to_all(parent):
        for child in parent.winfo_children():
            w_type = child.winfo_class()
            if w_type in ("Frame", "Labelframe"):
                child.configure(bg=c["bg"])
                if w_type == "Labelframe": child.configure(fg=c["sub"])
                apply_to_all(child)
            elif w_type == "Label":
                child.configure(bg=c["bg"], fg=c["text"])
            elif w_type == "Entry":
                child.configure(bg=c["input"], fg=c["text"], insertbackground=c["text"])
            elif w_type == "Radiobutton":
                child.configure(bg=c["bg"], fg=c["text"], selectcolor=c["card"], activebackground=c["bg"])
            elif w_type == "Checkbutton":
                child.configure(bg=c["bg"], fg=c["sub"], selectcolor=c["card"])
            elif w_type == "Button":
                child.configure(bg=c["btn"], fg=c["text"], activebackground=c["input"])
            elif "Spinbox" in w_type:
                child.configure(bg=c["input"], fg=c["text"], buttonbackground=c["input"])
    
    apply_to_all(main)
    text_res.configure(bg=c["res_bg"], fg=c["text"])
    root.after(1500, update_theme)

# --- 5. UI 构建 ---
root = tk.Tk()
root.title("TikTok 定价助手 Pro")
root.geometry("820x940")

# 全局指针锁定为原生箭头
root.config(cursor="arrow")

style = ttk.Style()
style.theme_use('aqua') 

main = tk.Frame(root, padx=25, pady=15)
main.pack(fill=tk.BOTH, expand=True)

# 汇率区 (6列大字)
lf = tk.LabelFrame(main, text=" 实时汇率设置 (RMB 基准) ", padx=10, pady=10, font=("Arial", 10, "bold"), bd=1)
lf.pack(fill=tk.X, pady=(0, 20))

rate_mode = tk.StringVar(value="fixed")
tk.Radiobutton(lf, text="手动模式", variable=rate_mode, value="manual", command=calculate_logic).grid(row=0, column=0, columnspan=2, sticky="w")
tk.Radiobutton(lf, text="锁定 0.57", variable=rate_mode, value="fixed", command=calculate_logic).grid(row=0, column=2, columnspan=2, sticky="w", padx=20)

for i, (curr, rate) in enumerate(FULL_RATES.items()):
    r, c = (i // 6) + 1, (i % 6) * 2
    tk.Label(lf, text=f"{curr}:", font=("Arial", 12)).grid(row=r, column=c, sticky="w", padx=2, pady=5)
    e = tk.Entry(lf, width=7, relief="flat", font=("Arial", 11))
    e.insert(0, str(rate))
    e.grid(row=r, column=c+1, padx=4, pady=5); e.bind("<KeyRelease>", lambda e: calculate_logic())

# 运营层 (4列对齐)
op_frame = tk.Frame(main)
op_frame.pack(fill=tk.X, pady=10)
for i in range(4): op_frame.columnconfigure(i, weight=1, uniform="group_x")

def ml(parent, text): return tk.Label(parent, text=text, font=("Arial", 11, "bold"))

v_p = tk.Frame(op_frame); v_p.grid(row=0, column=0, sticky="ew")
ml(v_p, "🎯 利润率").pack(anchor="w")
combo_profit = ttk.Combobox(v_p, values=[f"{i}%" for i in range(16, 31)], state="readonly")
combo_profit.set("20%"); combo_profit.pack(fill="x", pady=8, ipady=3); combo_profit.bind("<<ComboboxSelected>>", calculate_logic)

v_a = tk.Frame(op_frame); v_a.grid(row=0, column=1, sticky="ew", padx=15)
ml(v_a, "🔥 广告支出").pack(anchor="w")
combo_ads = ttk.Combobox(v_a, values=[f"{i}%" for i in range(26)], state="readonly")
combo_ads.set("0%"); combo_ads.pack(fill="x", pady=8, ipady=3); combo_ads.bind("<<ComboboxSelected>>", calculate_logic)

v_aff = tk.Frame(op_frame); v_aff.grid(row=0, column=2, sticky="ew", padx=(0,15))
ml(v_aff, "🤝 达人佣金").pack(anchor="w")
combo_aff = ttk.Combobox(v_aff, values=[f"{i}%" for i in range(26)], state="readonly")
combo_aff.set("0%"); combo_aff.pack(fill="x", pady=8, ipady=3); combo_aff.bind("<<ComboboxSelected>>", calculate_logic)

v_sw = tk.Frame(op_frame); v_sw.grid(row=0, column=3, sticky="ew")
ml(v_sw, "📦 多件多折").pack(anchor="w")
bundle_mode = tk.BooleanVar(value=True)
tk.Checkbutton(v_sw, text="启用优惠单", variable=bundle_mode, command=calculate_logic, font=("Arial", 11)).pack(pady=10, anchor="w")

# 输入层 (4列对齐)
in_frame = tk.Frame(main)
in_frame.pack(fill=tk.X, pady=10)
for i in range(4): in_frame.columnconfigure(i, weight=1, uniform="group_x")

f1 = tk.Frame(in_frame); f1.grid(row=0, column=0, sticky="ew")
ml(f1, "💰 单件成本").pack(anchor="w")
entry_cost = tk.Entry(f1, font=("Arial", 16, "bold"), relief="flat")
entry_cost.pack(fill="x", pady=8); entry_cost.insert(0, "20"); entry_cost.bind("<KeyRelease>", lambda e: calculate_logic())

f2 = tk.Frame(in_frame); f2.grid(row=0, column=1, sticky="ew", padx=15)
ml(f2, "🚚 运费小计").pack(anchor="w")
entry_ship = tk.Entry(f2, font=("Arial", 16, "bold"), relief="flat")
entry_ship.pack(fill="x", pady=8); entry_ship.insert(0, "1.95"); entry_ship.bind("<KeyRelease>", lambda e: calculate_logic())

f3 = tk.Frame(in_frame); f3.grid(row=0, column=2, sticky="ew", padx=(0,15))
ml(f3, "币种选择").pack(anchor="w")
combo_ship = ttk.Combobox(f3, values=list(FULL_RATES.keys()), state="readonly")
combo_ship.set("🇲🇾 MYR"); combo_ship.pack(fill="x", pady=8, ipady=3); combo_ship.bind("<<ComboboxSelected>>", calculate_logic)

f4 = tk.Frame(in_frame); f4.grid(row=0, column=3, sticky="ew")
ml(f4, "🔢 数量").pack(anchor="w")
spin_qty = tk.Spinbox(f4, from_=1, to=100, font=("Arial", 16, "bold"), relief="flat", command=calculate_logic)
spin_qty.pack(fill="x", pady=8); spin_qty.bind("<KeyRelease>", lambda e: calculate_logic())

# 底部展示
tk.Label(main, text="💵 最终结果币种:", font=("Arial", 10)).pack(anchor="w", pady=(10,2))
combo_out = ttk.Combobox(main, values=list(FULL_RATES.keys()), state="readonly")
combo_out.set("🇲🇾 MYR"); combo_out.pack(fill=tk.X, pady=(0, 20), ipady=6); combo_out.bind("<<ComboboxSelected>>", calculate_logic)

btn = tk.Button(main, text="计 算 运 营 定 价", font=("Arial", 14, "bold"), relief="flat", command=calculate_logic, pady=12)
btn.pack(fill="x")

text_res = tk.Text(main, height=14, font=("Menlo", 12), relief="flat", padx=15, pady=15, state="disabled")
text_res.pack(fill=tk.X, pady=(20, 0))

# 启动
update_theme()
calculate_logic()
root.mainloop()
