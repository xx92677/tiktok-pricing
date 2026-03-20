import tkinter as tk
from tkinter import messagebox, ttk
import math

# --- 配置 ---
FIXED_MYR_RATE = 1 / 1.75  
DEFAULT_RATES = {
    "🇨🇳 RMB": 1.0,
    "🇲🇾 MYR": round(FIXED_MYR_RATE, 3),
    "🇺🇸 USD": 0.138,
    "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45,
    "🇭🇰 HKD": 1.08,
    "🇹🇭 THB": 4.85,
    "Standard": 1.0 # 占位防错
}

# 财务常量
TARGET_PROFIT_RATE = 0.20
TARGET_DISCOUNT_RATE = 0.51
FIXED_FEES_MYR = 0.54
DEDUCTION_COEFFICIENT = 0.692

# 补全缺失的币种（保持与之前一致）
FULL_RATES = {
    "🇨🇳 RMB": 1.0, "🇲🇾 MYR": round(FIXED_MYR_RATE, 3), "🇺🇸 USD": 0.138, "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45, "🇭🇰 HKD": 1.08, "🇹🇭 THB": 4.85, "🇳 VND": 3450.0,
    "🇧🇷 BRL": 0.72, "🇲🇽 MXN": 2.35, "🇦🇷 ARS": 120.0, "🇯🇵 JPY": 20.5,
    "🇵🇭 PHP": 7.8, "🇮🇩 IDR": 2150.0
}

base_rates = {k: v for k, v in FULL_RATES.items()}

def toggle_rate_mode():
    if rate_mode.get() == "fixed":
        rate_entries["🇲🇾 MYR"].config(state='disabled')
        base_rates["🇲🇾 MYR"] = FIXED_MYR_RATE
        on_rmb_change()
    else:
        rate_entries["🇲🇾 MYR"].config(state='normal')

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
    try:
        for curr in FULL_RATES.keys():
            if curr != "🇨🇳 RMB": update_base_rate(curr)
        cost_rmb = float(entry_cost_rmb.get())
        ship_val = float(entry_ship_val.get())
        ship_curr = combo_ship_curr.get()
        out_curr = combo_out_curr.get()
        target_myr_rate = FIXED_MYR_RATE if rate_mode.get() == "fixed" else base_rates["🇲🇾 MYR"]
        ship_myr = (ship_val / base_rates[ship_curr]) * target_myr_rate
        cost_myr = cost_rmb * target_myr_rate
        d_myr = (cost_myr + ship_myr + FIXED_FEES_MYR) / DEDUCTION_COEFFICIENT
        o_myr = math.ceil(d_myr / (1 - TARGET_DISCOUNT_RATE))
        to_out = lambda v: (v / target_myr_rate) * base_rates[out_curr]
        d, o = to_out(d_myr), to_out(o_myr)
        p, c = to_out(d_myr * TARGET_PROFIT_RATE), to_out(d_myr * 0.0702)
        curr_code = out_curr.split()[-1]
        text_result.config(state=tk.NORMAL)
        text_result.delete(1.0, tk.END)
        text_result.insert(tk.END, f"建议原价：{o:.2f}\n后台折扣：{TARGET_DISCOUNT_RATE*100:.0f}%\n成交价格：{d:.2f}\n"
                                   f"--------------------\n平台佣金: {c:.2f}\n预计利润: {p:.2f}\n"
                                   f"\n* 模式: {'固定 1.75' if rate_mode.get()=='fixed' else '实时'}")
        text_result.config(state=tk.DISABLED)
    except: messagebox.showerror("错误", "输入有误")

root = tk.Tk()
root.title("TikTok定价助手 Pro")
# --- 修改点 1: 缩小窗口高度 ---
root.geometry("540x740") 

main_frame = tk.Frame(root, padx=20, pady=10)
main_frame.pack(fill=tk.BOTH)

# 汇率区
rate_label_frame = tk.LabelFrame(main_frame, text=" ⚙️ 汇率同步 ", padx=10, pady=5)
rate_label_frame.pack(fill=tk.X, pady=(0, 10))

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

# 输入区 (紧凑布局)
tk.Label(main_frame, text="💰 成本 (RMB):", font=("Arial", 9, "bold")).pack(anchor=tk.W)
entry_cost_rmb = tk.Entry(main_frame, font=("Arial", 12)); entry_cost_rmb.pack(fill=tk.X, pady=2); entry_cost_rmb.insert(0, "20")

tk.Label(main_frame, text="🚚 运费:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(5,0))
ship_row = tk.Frame(main_frame); ship_row.pack(fill=tk.X, pady=2)
entry_ship_val = tk.Entry(ship_row, font=("Arial", 12), width=15); entry_ship_val.pack(side=tk.LEFT, fill=tk.X, expand=True); entry_ship_val.insert(0, "1.95")
combo_ship_curr = ttk.Combobox(ship_row, values=list(FULL_RATES.keys()), width=10, state="readonly"); combo_ship_curr.set("🇲🇾 MYR"); combo_ship_curr.pack(side=tk.RIGHT, padx=5)

tk.Label(main_frame, text="💵 结果币种:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(5,0))
combo_out_curr = ttk.Combobox(main_frame, values=list(FULL_RATES.keys()), state="readonly"); combo_out_curr.set("🇲🇾 MYR"); combo_out_curr.pack(fill=tk.X, pady=2)

btn_calc = tk.Button(main_frame, text="开始定价 (Enter)", font=("Arial", 12, "bold"), bg="#00f2ea", command=calculate_single, pady=8)
btn_calc.pack(fill=tk.X, pady=10); root.bind('<Return>', calculate_single)

# 结果区
text_result = tk.Text(main_frame, height=8, font=("Menlo", 11), state=tk.DISABLED, padx=10, pady=10)
text_result.pack(fill=tk.X)

# --- 修改点 2: 紧贴结果框显示的说明小字 ---
tk.Label(main_frame, text="* 适配黑暗模式 | 右键.app可修改图标 | 汇率即改即用", font=("Arial", 7), fg="gray").pack(pady=2)

if __name__ == "__main__":
    root.mainloop()
