import tkinter as tk
from tkinter import messagebox, ttk
import math

# --- 财务配置 ---
FIXED_MYR_RATE = 1 / 1.75  
FULL_RATES = {
    "🇨🇳 RMB": 1.0, "🇲🇾 MYR": round(FIXED_MYR_RATE, 3), "🇺🇸 USD": 0.138, "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45, "🇭🇰 HKD": 1.08, "🇹🇭 THB": 4.85, "🇻🇳 VND": 3450.0,
    "🇧🇷 BRL": 0.72, "🇲🇽 MXN": 2.35, "🇦🇷 ARS": 120.0, "🇯🇵 JPY": 20.5,
    "🇵🇭 PHP": 7.8, "🇮🇩 IDR": 2150.0
}

TARGET_PROFIT_RATE, TARGET_DISCOUNT_RATE = 0.20, 0.51
FIXED_FEES_MYR, DEDUCTION_COEFFICIENT = 0.54, 0.692
base_rates = {k: v for k, v in FULL_RATES.items()}

def toggle_rate_mode():
    if rate_mode.get() == "fixed":
        rate_entries["🇲🇾 MYR"].config(state='disabled')
        base_rates["🇲🇾 MYR"] = FIXED_MYR_RATE
        on_rmb_change()
    else:
        rate_entries["🇲🇾 MYR"].config(state='normal')
    calculate_single() # 模式切换后自动重算

def on_rmb_change(*args):
    try:
        val = rmb_var.get()
        rmb_val = float(val) if val else 0
        for curr, var in rate_vars.items():
            if curr == "🇨🇳 RMB": continue
            rate = FIXED_MYR_RATE if (rate_mode.get() == "fixed" and curr == "🇲🇾 MYR") else base_rates[curr]
            new_val = rmb_val * rate
            var.set(f"{new_val:.0f}" if rate > 100 else f"{new_val:.3f}")
    except ValueError: pass

def update_base_rate(curr):
    if rate_mode.get() == "fixed" and curr == "🇲🇾 MYR": return
    try:
        rmb_val = float(rmb_var.get())
        current_display = float(rate_vars[curr].get())
        if rmb_val != 0: base_rates[curr] = current_display / rmb_val
    except ValueError: pass

def calculate_single(event=None):
    """核心计算函数，增加 event 参数以支持自动触发"""
    try:
        # 同步所有汇率输入
        for curr in FULL_RATES.keys():
            if curr != "🇨🇳 RMB": update_base_rate(curr)
            
        cost_rmb = float(entry_cost_rmb.get())
        ship_val = float(entry_ship_val.get())
        ship_curr, out_curr = combo_ship_curr.get(), combo_out_curr.get()
        
        target_myr_rate = FIXED_MYR_RATE if rate_mode.get() == "fixed" else base_rates["🇲🇾 MYR"]
        
        # 换算逻辑
        ship_myr = (ship_val / base_rates[ship_curr]) * target_myr_rate
        cost_myr = cost_rmb * target_myr_rate
        
        d_myr = (cost_myr + ship_myr + FIXED_FEES_MYR) / DEDUCTION_COEFFICIENT
        o_myr = math.ceil(d_myr / (1 - TARGET_DISCOUNT_RATE))
        
        to_out = lambda v: (v / target_myr_rate) * base_rates[out_curr]
        d, o = to_out(d_myr), to_out(o_myr)
        p, c = to_out(d_myr * TARGET_PROFIT_RATE), to_out(d_myr * 0.0702)
        
        text_result.config(state=tk.NORMAL)
        text_result.delete(1.0, tk.END)
        text_result.insert(tk.END, f"建议原价：{o:.2f}\n折扣比例：{TARGET_DISCOUNT_RATE*100:.0f}%\n实收成交：{d:.2f}\n"
                                   f"--------------------\n平台佣金: {c:.2f}\n预估利润: {p:.2f}\n"
                                   f"计算基准: 1 RMB = {base_rates[out_curr]:.3f} {out_curr.split()[-1]}")
        text_result.config(state=tk.DISABLED)
    except:
        pass # 自动计算时静默处理错误

root = tk.Tk()
root.title("TikTok定价助手 Pro")
root.geometry("520x660") # 进一步压缩高度

main_frame = tk.Frame(root, padx=20, pady=5)
main_frame.pack(fill=tk.X)

# --- 汇率区 ---
rate_label_frame = tk.LabelFrame(main_frame, text=" ⚙️ 汇率同步 (RMB基准) ", padx=10, pady=5)
rate_label_frame.pack(fill=tk.X, pady=(0, 5))

rate_mode = tk.StringVar(value="manual")
mode_frame = tk.Frame(rate_label_frame)
mode_frame.grid(row=0, column=0, columnspan=6, sticky=tk.W)
tk.Radiobutton(mode_frame, text="手动", variable=rate_mode, value="manual", command=toggle_rate_mode).pack(side=tk.LEFT)
tk.Radiobutton(mode_frame, text="锁定1.75", variable=rate_mode, value="fixed", command=toggle_rate_mode).pack(side=tk.LEFT, padx=10)

rate_vars, rate_entries = {}, {}
rmb_var = tk.StringVar(value="1")
rmb_var.trace_add("write", on_rmb_change)

for i, curr in enumerate(FULL_RATES.keys()):
    r, c = (i // 3) + 1, (i % 3) * 2
    tk.Label(rate_label_frame, text=f"{curr}:", font=("Arial", 8)).grid(row=r, column=c, sticky=tk.W)
    v = rmb_var if curr == "🇨🇳 RMB" else tk.StringVar(value=str(FULL_RATES[curr]))
    rate_vars[curr] = v
    e = tk.Entry(rate_label_frame, width=7, textvariable=v)
    e.grid(row=r, column=c+1, padx=2, pady=1)
    rate_entries[curr] = e
    if curr != "🇨🇳 RMB": e.bind("<FocusOut>", lambda e, c=curr: update_base_rate(c))

# --- 输入区 ---
input_frame = tk.Frame(main_frame)
input_frame.pack(fill=tk.X, pady=5)

tk.Label(input_frame, text="💰 成本 (RMB):", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W)
entry_cost_rmb = tk.Entry(input_frame, font=("Arial", 12), width=15)
entry_cost_rmb.grid(row=1, column=0, sticky=tk.EW, padx=(0,10), pady=2)
entry_cost_rmb.insert(0, "20")

tk.Label(input_frame, text="🚚 运费:", font=("Arial", 9, "bold")).grid(row=0, column=1, sticky=tk.W)
ship_box = tk.Frame(input_frame)
ship_box.grid(row=1, column=1, sticky=tk.EW)
entry_ship_val = tk.Entry(ship_box, font=("Arial", 12), width=10); entry_ship_val.pack(side=tk.LEFT, fill=tk.X, expand=True)
entry_ship_val.insert(0, "1.95")

combo_ship_curr = ttk.Combobox(ship_box, values=list(FULL_RATES.keys()), width=10, state="readonly")
combo_ship_curr.set("🇲🇾 MYR"); combo_ship_curr.pack(side=tk.RIGHT, padx=5)
# 关键优化：选择即计算
combo_ship_curr.bind("<<ComboboxSelected>>", calculate_single)

tk.Label(main_frame, text="💵 结果币种:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(5,0))
combo_out_curr = ttk.Combobox(main_frame, values=list(FULL_RATES.keys()), state="readonly")
combo_out_curr.set("🇲🇾 MYR"); combo_out_curr.pack(fill=tk.X, pady=2)
# 关键优化：选择即计算
combo_out_curr.bind("<<ComboboxSelected>>", calculate_single)

btn_calc = tk.Button(main_frame, text="开始定价 (Enter)", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#000000", command=calculate_single, pady=8)
btn_calc.pack(fill=tk.X, pady=10)
root.bind('<Return>', calculate_single)

# --- 结果区 ---
text_result = tk.Text(main_frame, height=7, font=("Menlo", 11), state=tk.DISABLED, padx=10, pady=5)
text_result.pack(fill=tk.X)

tk.Label(main_frame, text="* 适配黑暗模式 | 右键.app可修改图标 | 汇率即改即用", font=("Arial", 7), fg="gray").pack(pady=2)

if __name__ == "__main__":
    calculate_single() # 启动时先算一次
    root.mainloop()
