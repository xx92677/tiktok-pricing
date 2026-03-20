import tkinter as tk
from tkinter import messagebox, ttk
import math

# --- 1. 基础财务配置 ---
FIXED_MYR_RATE = 0.57  # 1 RMB = 0.57 MYR
FULL_RATES = {
    "🇨🇳 RMB": 1.0, "🇲🇾 MYR": 0.588, "🇺🇸 USD": 0.138, "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45, "🇭🇰 HKD": 1.08, "🇹🇭 THB": 4.85, "🇻🇳 VND": 3450.0,
    "🇧🇷 BRL": 0.72, "🇲🇽 MXN": 2.35, "🇦🇷 ARS": 120.0, "🇯🇵 JPY": 20.5,
    "🇵🇭 PHP": 7.8, "🇮🇩 IDR": 2150.0
}

# 审美配置
GLASS_BG = "#1C1C1E"
GLASS_CARD = "#2C2C2E"
GLASS_INPUT = "#3A3A3C"
GLASS_TEXT = "#F5F5F7"
GLASS_SUB = "#8E8E93"

PLATFORM_COMMISSION = 0.0702 # 平台固定扣点 7.02%
FIXED_FEE_MYR = 0.54         # 固定服务费
TARGET_DISCOUNT = 0.51       # 默认营销折扣 (折后价/0.49 = 原价)

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
        # 获取输入
        cost_rmb = get_val(entry_cost)
        ship_val = get_val(entry_ship)
        qty = int(get_val(combo_qty))
        
        # 获取百分比设置
        margin_pct = get_val(combo_profit) / 100
        ads_pct = get_val(combo_ads) / 100
        aff_pct = get_val(combo_aff) / 100
        
        ship_curr, out_curr = combo_ship.get(), combo_out.get()
        suffix = CURR_MAP.get(out_curr, "N/A")
        
        # 汇率基准
        my_rate = FIXED_MYR_RATE if rate_mode.get() == "fixed" else base_rates.get("🇲🇾 MYR", 0.588)
        
        # --- 多件折扣逻辑 ---
        # 2件8折 (0.8)，3件及以上7折 (0.7)
        bundle_discount = 1.0
        if qty == 2: bundle_discount = 0.8
        elif qty >= 3: bundle_discount = 0.7
        
        # --- 成本计算 (马币维度) ---
        total_prod_cost_myr = cost_rmb * qty * my_rate
        total_ship_myr = (ship_val / base_rates.get(ship_curr, 1.0)) * my_rate
        total_base_expenses = total_prod_cost_myr + total_ship_myr + FIXED_FEE_MYR
        
        # --- 倒求售价公式 ---
        # 售价 = 成本 / (1 - 平台佣金 - 利润率 - 广告占比 - 达人佣金)
        # 注意：这里的售价是“折后实付价”
        divisor = 1 - PLATFORM_COMMISSION - margin_pct - ads_pct - aff_pct
        
        if divisor <= 0:
            text_res.config(state=tk.NORMAL)
            text_res.delete(1.0, tk.END)
            text_res.insert(tk.END, "错误：各项占比总和超过100%\n请降低利润或佣金要求。")
            text_res.config(state=tk.DISABLED)
            return

        # 订单总实付售价 (MYR)
        total_deal_price_myr = total_base_expenses / divisor
        
        # 转换显示
        to_out = lambda v: (v / my_rate) * base_rates.get(out_curr, 1.0)
        
        f_total_deal = to_out(total_deal_price_myr) # 订单总售价
        f_unit_deal = f_total_deal / qty             # 单件实付价
        
        # 如果有折扣，原价需要根据折数反向覆盖
        # 建议原价 = (总实付 / 折扣系数) / (1 - 基础营销折扣)
        f_total_orig = (f_total_deal / bundle_discount) / (1 - TARGET_DISCOUNT)
        
        # 利润对账 (RMB)
        profit_rmb = (total_deal_price_myr * margin_pct) / my_rate
        
        text_res.config(state=tk.NORMAL)
        text_res.delete(1.0, tk.END)
        text_res.insert(tk.END, 
            f"【订单对账单】 数量：{qty} 件\n"
            f"建议总原价： {f_total_orig:.2f} {suffix}\n"
            f"订单总实付： {f_total_deal:.2f} {suffix}\n"
            f"单件平均价： {f_unit_deal:.2f} {suffix}\n"
            f"----------------------------------\n"
            f"目标利润 ({int(margin_pct*100)}%): {f_total_deal * margin_pct:.2f} {suffix}\n"
            f"预计纯利 (RMB): {profit_rmb:.2f} RMB\n"
            f"----------------------------------\n"
            f"广告支出 ({int(ads_pct*100)}%): {f_total_deal * ads_pct:.2f} {suffix}\n"
            f"达人佣金 ({int(aff_pct*100)}%): {f_total_deal * aff_pct:.2f} {suffix}\n"
            f"平台扣点 (7.02%): {f_total_deal * PLATFORM_COMMISSION:.2f} {suffix}\n"
            f"----------------------------------\n"
            f"多件折数： {int(bundle_discount*10)} 折 (已包含在计算内)"
        )
        text_res.config(state=tk.DISABLED)
    except: pass

def sync_rates(*args):
    try:
        rb = get_num(entry_rmb_base)
        for curr, var in rate_vars.items():
            if curr == "🇨🇳 RMB": continue
            rate = FIXED_MYR_RATE if (rate_mode.get() == "fixed" and curr == "🇲🇾 MYR") else base_rates.get(curr, 1.0)
            var.set(f"{rb * rate:.0f}" if rate > 100 else f"{rb * rate:.3f}")
        calculate_logic()
    except: pass

# --- 3. UI 构建 ---
root = tk.Tk()
root.title("TikTok 定价助手 Pro - 运营旗舰版")
root.geometry("700x950")
root.configure(bg=GLASS_BG)

try:
    if root.tk.call('tk', 'windowingsystem') == 'aqua':
        root.tk.call('tk', 'scaling', 2.0)
except: pass

style = ttk.Style(root)
style.theme_use('aqua')
style.configure("TCombobox", fieldbackground=GLASS_INPUT, foreground=GLASS_TEXT, background=GLASS_INPUT)

main = tk.Frame(root, padx=20, pady=10, bg=GLASS_BG)
main.pack(fill=tk.BOTH, expand=True)

# 汇率面板 (4列)
lf = tk.LabelFrame(main, text=" 实时汇率设置 ", padx=10, pady=8, bg=GLASS_BG, fg=GLASS_SUB, font=("Arial", 9, "bold"))
lf.pack(fill=tk.X, pady=(0, 10))

rate_mode = tk.StringVar(value="fixed")
mf = tk.Frame(lf, bg=GLASS_BG)
mf.grid(row=0, column=0, columnspan=8, sticky=tk.W, pady=(0,5))
tk.Radiobutton(mf, text="手动", variable=rate_mode, value="manual", command=calculate_logic, bg=GLASS_BG, fg=GLASS_TEXT, selectcolor=GLASS_CARD).pack(side=tk.LEFT)
tk.Radiobutton(mf, text="锁定 0.57", variable=rate_mode, value="fixed", command=calculate_logic, bg=GLASS_BG, fg=GLASS_TEXT, selectcolor=GLASS_CARD).pack(side=tk.LEFT, padx=15)

rate_vars, rmb_var = {}, tk.StringVar(value="1")
rmb_var.trace_add("write", lambda *args: calculate_logic()) # 简化同步逻辑

for i, curr in enumerate(FULL_RATES.keys()):
    r, c = (i // 4) + 1, (i % 4) * 2
    tk.Label(lf, text=f"{curr}:", font=("Arial", 9), bg=GLASS_BG, fg=GLASS_TEXT).grid(row=r, column=c, sticky=tk.W, padx=2, pady=2)
    v = tk.StringVar(value=str(FULL_RATES[curr]))
    rate_vars[curr] = v
    e = tk.Entry(lf, width=6, textvariable=v, relief="flat", bg=GLASS_INPUT, fg=GLASS_TEXT, font=("Arial", 10))
    e.grid(row=r, column=c+1, padx=2, pady=2)
    e.bind("<KeyRelease>", lambda e: calculate_logic())

# 运营成本设置区 (广告、达人、利润)
op_f = tk.Frame(main, bg=GLASS_BG)
op_f.pack(fill=tk.X, pady=10)

# 1. 利润率 (16%-30%)
v_p = tk.Frame(op_f, bg=GLASS_BG)
v_p.pack(side=tk.LEFT, expand=True, fill=tk.X)
tk.Label(v_p, text="🎯 利润率", font=("Arial", 9, "bold"), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W)
combo_profit = ttk.Combobox(v_p, values=[f"{i}%" for i in range(16, 31)], width=8, state="readonly")
combo_profit.set("20%"); combo_profit.pack(pady=5, ipady=3); combo_profit.bind("<<ComboboxSelected>>", calculate_logic)

# 2. 广告费 (TikTok常用：0%, 10%, 15%, 20%, 25%)
v_a = tk.Frame(op_f, bg=GLASS_BG)
v_a.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)
tk.Label(v_a, text="🔥 广告支出", font=("Arial", 9, "bold"), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W)
combo_ads = ttk.Combobox(v_a, values=["0%", "10%", "15%", "20%", "25%"], width=8, state="readonly")
combo_ads.set("0%"); combo_ads.pack(pady=5, ipady=3); combo_ads.bind("<<ComboboxSelected>>", calculate_logic)

# 3. 达人佣金 (常用：0%, 10%, 15%, 20%, 30%)
v_aff = tk.Frame(op_f, bg=GLASS_BG)
v_aff.pack(side=tk.LEFT, expand=True, fill=tk.X)
tk.Label(v_aff, text="🤝 达人佣金", font=("Arial", 9, "bold"), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W)
combo_aff = ttk.Combobox(v_aff, values=["0%", "10%", "15%", "20%", "30%"], width=8, state="readonly")
combo_aff.set("0%"); combo_aff.pack(pady=5, ipady=3); combo_aff.bind("<<ComboboxSelected>>", calculate_logic)

# 核心输入行
row_f = tk.Frame(main, bg=GLASS_BG); row_f.pack(fill=tk.X, pady=5)
tk.Label(row_f, text="💰 单件成本(RMB)", font=("Arial", 9), bg=GLASS_BG, fg=GLASS_TEXT).grid(row=0, column=0, sticky=tk.W)
entry_cost = tk.Entry(row_f, font=("Arial", 14, "bold"), width=9, relief="flat", bg=GLASS_INPUT, fg=GLASS_TEXT, insertbackground="white")
entry_cost.grid(row=1, column=0, pady=5); entry_cost.insert(0, "20"); entry_cost.bind("<KeyRelease>", lambda e: calculate_logic())

tk.Label(row_f, text="🚚 运费", font=("Arial", 9), bg=GLASS_BG, fg=GLASS_TEXT).grid(row=0, column=1, sticky=tk.W, padx=10)
entry_ship = tk.Entry(row_f, font=("Arial", 14, "bold"), width=7, relief="flat", bg=GLASS_INPUT, fg=GLASS_TEXT, insertbackground="white")
entry_ship.grid(row=1, column=1, padx=10, pady=5); entry_ship.insert(0, "1.95"); entry_ship.bind("<KeyRelease>", lambda e: calculate_logic())

tk.Label(row_f, text="币种", font=("Arial", 9), bg=GLASS_BG, fg=GLASS_TEXT).grid(row=0, column=2, sticky=tk.W)
combo_ship = ttk.Combobox(row_f, values=list(FULL_RATES.keys()), width=8, state="readonly")
combo_ship.set("🇲🇾 MYR"); combo_ship.grid(row=1, column=2, pady=5, ipady=3); combo_ship.bind("<<ComboboxSelected>>", calculate_logic)

tk.Label(row_f, text="📦 数量", font=("Arial", 9), bg=GLASS_BG, fg=GLASS_TEXT).grid(row=0, column=3, sticky=tk.W, padx=10)
combo_qty = ttk.Combobox(row_f, values=[str(i) for i in range(1, 101)], width=5, state="readonly")
combo_qty.set("1"); combo_qty.grid(row=1, column=3, padx=10, pady=5, ipady=3); combo_qty.bind("<<ComboboxSelected>>", calculate_logic)

# 底部结果
tk.Label(main, text="💵 结果显示币种:", font=("Arial", 10), bg=GLASS_BG, fg=GLASS_TEXT).pack(anchor=tk.W, pady=(5,2))
combo_out = ttk.Combobox(main, values=list(FULL_RATES.keys()), state="readonly")
combo_out.set("🇲🇾 MYR"); combo_out.pack(fill=tk.X, pady=(0, 10), ipady=6); combo_out.bind("<<ComboboxSelected>>", calculate_logic)

btn = tk.Button(main, text="计 算 运 营 定 价", font=("Arial", 13, "bold"), bg="#F5F5F7", fg="#1C1C1E", highlightthickness=0, relief="flat", command=calculate_logic, pady=10)
btn.pack(fill=tk.X, pady=(0, 10))

text_res = tk.Text(main, height=14, font=("Menlo", 12), state=tk.DISABLED, bg=GLASS_CARD, fg=GLASS_TEXT, relief="flat", padx=15, pady=15)
text_res.pack(fill=tk.X)

root.after(200, lambda: [root.attributes("-alpha", 0.96), calculate_logic()])
root.mainloop()
