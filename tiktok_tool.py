import tkinter as tk
from tkinter import messagebox, ttk
import math

# --- 财务与汇率配置 ---
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

def calculate_single(*args):
    """
    核心计算：支持所有输入变动时自动触发
    """
    try:
        # 1. 提取当前汇率（处理手动修改的情况）
        for curr in FULL_RATES.keys():
            if curr == "🇨🇳 RMB": continue
            try:
                rmb_val = float(rmb_var.get())
                display_val = float(rate_vars[curr].get())
                if rmb_val != 0: base_rates[curr] = display_val / rmb_val
            except: pass

        # 2. 获取输入数值
        cost_rmb = float(entry_cost_rmb.get() or 0)
        ship_val = float(entry_ship_val.get() or 0)
        ship_curr = combo_ship_curr.get()
        out_curr = combo_out_curr.get()
        
        # 3. 确定马币汇率模式
        target_myr_rate = FIXED_MYR_RATE if rate_mode.get() == "fixed" else base_rates["🇲🇾 MYR"]
        
        # 4. 换算逻辑：所有国家运费 -> 统一转马币算利润
        ship_myr = (ship_val / base_rates[ship_curr]) * target_myr_rate
        cost_myr = cost_rmb * target_myr_rate
        
        # 5. 定价公式
        d_myr = (cost_myr + ship_myr + FIXED_FEES_MYR) / DEDUCTION_COEFFICIENT
        o_myr = math.ceil(d_myr / (1 - TARGET_DISCOUNT_RATE))
        
        # 6. 转回显示币种
        to_out = lambda v: (v / target_myr_rate) * base_rates[out_curr]
        d, o = to_out(d_myr), to_out(o_myr)
        p, c = to_out(d_myr * TARGET_PROFIT_RATE), to_out(d_myr * 0.0702)
        
        # 7. 刷新 UI
        text_result.config(state=tk.NORMAL)
        text_result.delete(1.0, tk.END)
        text_result.insert(tk.END, 
            f"建议原价：{o:.2f}\n"
            f"折扣比例：{TARGET_DISCOUNT_RATE*100:.0f}%\n"
            f"实收成交：{d:.2f}\n"
            f"--------------------\n"
            f"平台佣金: {c:.2f}\n"
            f"预计利润: {p:.2f}\n"
            f"计算基准: 1 RMB = {base_rates[out_curr]:.3f} {out_curr.split()[-1]}"
        )
        text_result.config(state=tk.DISABLED)
    except:
        pass # 输入过程中产生的临时错误不弹窗

def on_rmb_change(*args):
    """RMB基准变动联动"""
    try:
        rmb_val = float(rmb_var.get() or 0)
        for curr, var in rate_vars.items():
            if curr == "🇨🇳 RMB": continue
            rate = FIXED_MYR_RATE if (rate_mode.get() == "fixed" and curr == "🇲🇾 MYR") else base_rates[curr]
            new_val = rmb_val * rate
            var.set(f"{new_val:.0f}" if rate > 100 else f"{new_val:.3f}")
        calculate_single()
    except: pass

def toggle_rate_mode():
    if rate_mode.get() == "fixed":
        rate_entries["🇲🇾 MYR"].config(state='disabled')
        base_rates["🇲🇾 MYR"] = FIXED_MYR_RATE
    else:
        rate_entries["🇲🇾 MYR"].config(state='normal')
    on_rmb_change()

# --- UI 构造 ---
root = tk.Tk()
root.title("TikTok定价助手 Pro")
root.geometry("540x680")

# 使用变量追踪实现输入即计算
cost_var = tk.StringVar(value="20")
ship_val_var = tk.StringVar(value="1.95")
cost_var.trace_add("write", calculate_single)
ship_val_var.trace_add("write", calculate_single)

main_frame = tk.Frame(root, padx=20, pady=5)
main_frame.pack(fill=tk.X)

# 1. 汇率设置
rate_lf = tk.LabelFrame(main_frame, text=" ⚙️ 汇率同步 (1 RMB=?) ", padx=10, pady=5)
rate_lf.pack(fill=tk.X, pady=(0, 5))

rate_mode = tk.StringVar(value="manual")
mf = tk.Frame(rate_lf); mf.grid(row=0, column=0, columnspan=6, sticky=tk.W)
tk.Radiobutton(mf, text="手动", variable=rate_mode, value="manual", command=toggle_rate_mode).pack(side=tk.LEFT)
tk.Radiobutton(mf, text="锁定1.75", variable=rate_mode, value="fixed", command=toggle_rate_mode).pack(side=tk.LEFT, padx=10)

rate_vars, rate_entries = {}, {}
rmb_var = tk.StringVar(value="1")
rmb_var.trace_add("write", on_rmb_change)

for i, curr in enumerate(FULL_RATES.keys()):
    r, c = (i // 3) + 1, (i % 3) * 2
    tk.Label(rate_lf, text=f"{curr}:", font=("Arial", 8)).grid(row=r, column=c, sticky=tk.W)
    v = rmb_var if curr == "🇨🇳 RMB" else tk.StringVar(value=str(FULL_RATES[curr]))
    rate_vars[curr] = v
    e = tk.Entry(rate_lf, width=7, textvariable=v)
    e.grid(row=r, column=c+1, padx=2, pady=1)
    rate_entries[curr] = e
    if curr != "🇨🇳 RMB": e.bind("<FocusOut>", lambda e, c=curr: calculate_single())

# 2. 输入区域
tk.Label(main_frame, text="💰 成本 (RMB):", font=("Arial", 9, "bold")).pack(anchor=tk.W)
entry_cost_rmb = tk.Entry(main_frame, font=("Arial", 12), textvariable=cost_var)
entry_cost_rmb.pack(fill=tk.X, pady=2)

tk.Label(main_frame, text="🚚 运费:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(5,0))
s_row = tk.Frame(main_frame); s_row.pack(fill=tk.X, pady=2)
entry_ship_val = tk.Entry(s_row, font=("Arial", 12), width=15, textvariable=ship_val_var)
entry_ship_val.pack(side=tk.LEFT, fill=tk.X, expand=True)

combo_ship_curr = ttk.Combobox(s_row, values=list(FULL_RATES.keys()), width=12, state="readonly")
combo_ship_curr.set("🇲🇾 MYR"); combo_ship_curr.pack(side=tk.RIGHT, padx=5)
# 核心修复：选择运费币种后立即重算
combo_ship_curr.bind("<<ComboboxSelected>>", calculate_single)

tk.Label(main_frame, text="💵 结果币种:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(5,0))
combo_out_curr = ttk.Combobox(main_frame, values=list(FULL_RATES.keys()), state="readonly")
combo_out_curr.set("🇲🇾 MYR"); combo_out_curr.pack(fill=tk.X, pady=2)
combo_out_curr.bind("<<ComboboxSelected>>", calculate_single)

# 3. 结果展示
text_result = tk.Text(main_frame, height=7, font=("Menlo", 11), state=tk.DISABLED, padx=10, pady=5)
text_result.pack(fill=tk.X, pady=10)

tk.Label(main_frame, text="* 适配黑暗模式 | 右键.app可修改图标 | 汇率即改即用", font=("Arial", 7), fg="gray").pack()

# 初始化计算一次
calculate_single()

if __name__ == "__main__":
    root.mainloop()
