import tkinter as tk
from tkinter import messagebox, ttk
import math

# --- 配置 ---
FIXED_MYR_RATE = 1 / 1.75  # 1:1.75 换算出的 1RMB 兑 MYR 值 (约 0.5714)
DEFAULT_RATES = {
    "🇨🇳 RMB": 1.0,
    "🇲🇾 MYR": round(FIXED_MYR_RATE, 3),
    "🇺🇸 USD": 0.138,
    "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45,
    "🇭🇰 HKD": 1.08,
    "🇹🇭 THB": 4.85,
    "🇻🇳 VND": 3450.0,
    "🇧🇷 BRL": 0.72,
    "🇲🇽 MXN": 2.35,
    "🇦🇷 ARS": 120.0,
    "🇯🇵 JPY": 20.5,
    "🇵🇭 PHP": 7.8,
    "🇮🇩 IDR": 2150.0
}

TARGET_PROFIT_RATE = 0.20
TARGET_DISCOUNT_RATE = 0.51
FIXED_FEES_MYR = 0.54
DEDUCTION_COEFFICIENT = 0.692

# 存储原始汇率 (1:X)
base_rates = {k: v for k, v in DEFAULT_RATES.items()}

def toggle_rate_mode():
    """切换汇率模式"""
    mode = rate_mode.get()
    if mode == "fixed":
        # 锁定马币输入框并设置固定值
        rate_entries["🇲🇾 MYR"].config(state='disabled')
        base_rates["🇲🇾 MYR"] = FIXED_MYR_RATE
        on_rmb_change() # 刷新显示
    else:
        # 恢复手动输入
        rate_entries["🇲🇾 MYR"].config(state='normal')

def on_rmb_change(*args):
    """基准人民币变动逻辑"""
    try:
        rmb_val = float(rmb_var.get()) if rmb_var.get() else 0
        for curr, var in rate_vars.items():
            if curr == "🇨🇳 RMB": continue
            
            # 如果是固定模式且是马币，强制使用固定比例
            current_rate = FIXED_MYR_RATE if (rate_mode.get() == "fixed" and curr == "🇲🇾 MYR") else base_rates[curr]
            
            new_val = rmb_val * current_rate
            if current_rate > 100:
                var.set(f"{new_val:.0f}")
            else:
                var.set(f"{new_val:.3f}")
    except ValueError:
        pass

def update_base_rate(curr):
    """手动修改非RMB框时更新基准"""
    if rate_mode.get() == "fixed" and curr == "🇲🇾 MYR": return
    try:
        rmb_val = float(rmb_var.get())
        current_display_val = float(rate_vars[curr].get())
        if rmb_val != 0:
            base_rates[curr] = current_display_val / rmb_val
    except ValueError:
        pass

def calculate_single(event=None):
    try:
        # 同步汇率
        for curr in DEFAULT_RATES.keys():
            if curr != "🇨🇳 RMB": update_base_rate(curr)
        
        cost_rmb = float(entry_cost_rmb.get())
        ship_val = float(entry_ship_val.get())
        ship_curr = combo_ship_curr.get()
        out_curr = combo_out_curr.get()
        
        # 核心换算
        ship_in_rmb = shipping_val / base_rates[ship_curr]
        target_myr_rate = FIXED_MYR_RATE if rate_mode.get() == "fixed" else base_rates["🇲🇾 MYR"]
        
        ship_myr = ship_in_rmb * target_myr_rate
        cost_myr = cost_rmb * target_myr_rate
        
        deal_price_myr = (cost_myr + ship_myr + FIXED_FEES_MYR) / DEDUCTION_COEFFICIENT
        original_price_myr = math.ceil(deal_price_myr / (1 - TARGET_DISCOUNT_RATE))
        profit_myr = deal_price_myr * TARGET_PROFIT_RATE
        commission_myr = deal_price_myr * 0.0702
        
        to_out = lambda val_myr: (val_myr / target_myr_rate) * base_rates[out_curr]
        d, o, c, p = to_out(deal_price_myr), to_out(original_price_myr), to_out(commission_myr), to_out(profit_myr)
        
        curr_code = out_curr.split()[-1]
        text_result.config(state=tk.NORMAL)
        text_result.delete(1.0, tk.END)
        text_result.insert(tk.END, f"--- 定价建议 ({curr_code}) ---\n建议原价：{o:.2f}\n后台折扣：{TARGET_DISCOUNT_RATE*100:.0f}%\n成交价格：{d:.2f}\n"
                                   f"--------------------\n--- 预估财务预览 ---\n平台佣金: {c:.2f}\n预计利润: {p:.2f}\n"
                                   f"\n* 汇率模式: {'固定 1:1.75' if rate_mode.get()=='fixed' else '手动实时'}")
        text_result.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror("错误", "请检查输入数值是否正确")

# --- UI 界面 ---
root = tk.Tk()
root.title("TikTok定价助手 Pro")
root.geometry("540x880")

main_frame = tk.Frame(root, padx=20, pady=15)
main_frame.pack(fill=tk.BOTH, expand=True)

# 汇率设置区
rate_label_frame = tk.LabelFrame(main_frame, text=" ⚙️ 汇率同步设置 ", padx=10, pady=10)
rate_label_frame.pack(fill=tk.X, pady=(0, 15))

# 模式切换
rate_mode = tk.StringVar(value="manual")
mode_frame = tk.Frame(rate_label_frame)
mode_frame.grid(row=0, column=0, columnspan=6, sticky=tk.W, pady=(0,10))
tk.Radiobutton(mode_frame, text="手动/实时汇率", variable=rate_mode, value="manual", command=toggle_rate_mode).pack(side=tk.LEFT)
tk.Radiobutton(mode_frame, text="锁定 MYR 固定汇率 (1:1.75)", variable=rate_mode, value="fixed", command=toggle_rate_mode).pack(side=tk.LEFT, padx=15)

rate_vars = {}
rate_entries = {}
rmb_var = tk.StringVar(value="1")
rmb_var.trace_add("write", on_rmb_change)

for i, curr in enumerate(DEFAULT_RATES.keys()):
    row, col = (i // 3) + 1, (i % 3) * 2
    tk.Label(rate_label_frame, text=f"{curr}:", font=("Arial", 9)).grid(row=row, column=col, sticky=tk.W, pady=2)
    var = rmb_var if curr == "🇨🇳 RMB" else tk.StringVar(value=str(DEFAULT_RATES[curr]))
    rate_vars[curr] = var
    ent = tk.Entry(rate_label_frame, width=8, textvariable=var)
    ent.grid(row=row, column=col+1, padx=(2, 5), pady=2)
    rate_entries[curr] = ent
    if curr != "🇨🇳 RMB":
        ent.bind("<FocusOut>", lambda e, c=curr: update_base_rate(c))

# 核心输入区
tk.Label(main_frame, text="💰 商品成本 (人民币 RMB):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
entry_cost_rmb = tk.Entry(main_frame, font=("Arial", 14)); entry_cost_rmb.pack(fill=tk.X, pady=5); entry_cost_rmb.insert(0, "20")

tk.Label(main_frame, text="🚚 跨境运费:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10,0))
ship_row = tk.Frame(main_frame); ship_row.pack(fill=tk.X, pady=5)
entry_ship_val = tk.Entry(ship_row, font=("Arial", 14), width=15); entry_ship_val.pack(side=tk.LEFT, fill=tk.X, expand=True); entry_ship_val.insert(0, "1.95")
combo_ship_curr = ttk.Combobox(ship_row, values=list(DEFAULT_RATES.keys()), width=12, state="readonly", font=("Arial", 12))
combo_ship_curr.set("🇲🇾 MYR"); combo_ship_curr.pack(side=tk.RIGHT, padx=(10,0))

tk.Label(main_frame, text="💵 结果显示币种:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10,0))
combo_out_curr = ttk.Combobox(main_frame, values=list(DEFAULT_RATES.keys()), state="readonly", font=("Arial", 12))
combo_out_curr.set("🇲🇾 MYR"); combo_out_curr.pack(fill=tk.X, pady=5)

btn_calc = tk.Button(main_frame, text="开始定价计算 (Enter)", font=("Arial", 14, "bold"), bg="#00f2ea", fg="black", command=calculate_single, pady=10)
btn_calc.pack(fill=tk.X, pady=15); root.bind('<Return>', calculate_single)

text_result = tk.Text(main_frame, height=10, font=("Menlo", 12), state=tk.DISABLED, padx=12, pady=12)
text_result.pack(fill=tk.X)

if __name__ == "__main__":
    root.mainloop()
