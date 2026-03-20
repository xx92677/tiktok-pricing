import tkinter as tk
from tkinter import messagebox, ttk
import math

# --- 默认汇率配置 (1 RMB 等于多少外币) ---
# 参考汇率，建议在 App 界面根据当天实时数据微调
DEFAULT_RATES = {
    "🇲🇾 MYR": 0.588,
    "🇺🇸 USD": 0.138,
    "🇪🇺 EUR": 0.127,
    "🇹🇼 TWD": 4.45,   # 新增：新台币
    "🇭🇰 HKD": 1.08,   # 新增：港币
    "🇻🇳 VND": 3450.0,
    "🇹🇭 THB": 4.85,
    "🇧🇷 BRL": 0.72,
    "🇲🇽 MXN": 2.35,
    "🇦🇷 ARS": 120.0,
    "🇯🇵 JPY": 20.5,
    "🇵🇭 PHP": 7.8,
    "🇮🇩 IDR": 2150.0,
    "🇨🇳 RMB": 1.0
}

# 财务常量 (基于马来站逻辑)
TARGET_PROFIT_RATE = 0.20
TARGET_DISCOUNT_RATE = 0.51
FIXED_FEES_MYR = 0.54
DEDUCTION_COEFFICIENT = 0.692

def core_calculation(cost_rmb, shipping_val, ship_curr, out_curr, current_rates):
    # 1. 统一折算运费为 MYR
    # 先转 RMB，再转 MYR
    ship_in_rmb = shipping_val / current_rates[ship_curr]
    ship_myr = ship_in_rmb * current_rates["🇲🇾 MYR"]
    
    # 2. 核心定价计算
    cost_myr = cost_rmb * current_rates["🇲🇾 MYR"]
    deal_price_myr = (cost_myr + ship_myr + FIXED_FEES_MYR) / DEDUCTION_COEFFICIENT
    
    # 3. 计算原价 (向上取整)
    original_price_myr = math.ceil(deal_price_myr / (1 - TARGET_DISCOUNT_RATE))
    
    # 4. 财务预览数据 (MYR)
    profit_myr = deal_price_myr * TARGET_PROFIT_RATE
    commission_myr = deal_price_myr * 0.0702
    
    # 5. 转换到目标显示货币
    to_out = lambda val_myr: (val_myr / current_rates["🇲🇾 MYR"]) * current_rates[out_curr]
    
    return (
        to_out(deal_price_myr), 
        to_out(original_price_myr), 
        to_out(commission_myr), 
        to_out(profit_myr)
    )

def calculate_single(event=None):
    try:
        # 获取用户输入的实时汇率
        user_rates = {}
        for curr, entry in rate_entries.items():
            user_rates[curr] = float(entry.get())
        
        cost_rmb = float(entry_cost_rmb.get())
        ship_val = float(entry_ship_val.get())
        ship_curr = combo_ship_curr.get()
        out_curr = combo_out_curr.get()
        
        d, o, c, p = core_calculation(cost_rmb, ship_val, ship_curr, out_curr, user_rates)
        
        # 提取币种名称
        curr_code = out_curr.split()[-1]
        
        text_result.config(state=tk.NORMAL)
        text_result.delete(1.0, tk.END)
        
        res = (
            f"--- 定价建议 ({curr_code}) ---\n"
            f"建议原价：{o:.2f}\n"
            f"后台折扣：{TARGET_DISCOUNT_RATE*100:.0f}%\n"
            f"成交价格：{d:.2f}\n"
            f"--------------------\n"
            f"--- 预估财务预览 ---\n"
            f"平台佣金: {c:.2f}\n"
            f"预计利润: {p:.2f}\n"
            f"\n* 汇率基准: 1 RMB = {user_rates[out_curr]} {curr_code}"
        )
        text_result.insert(tk.END, res)
        text_result.config(state=tk.DISABLED)
        
    except ValueError:
        messagebox.showerror("输入错误", "汇率、成本和运费框内只能输入数字！")

# --- UI 界面 ---
root = tk.Tk()
root.title("TikTok 全球定价助手 Pro - 14币种版")
root.geometry("520x820") # 适配多币种高度

main_frame = tk.Frame(root, padx=20, pady=15)
main_frame.pack(fill=tk.BOTH, expand=True)

# 1. 汇率设置区 (3列网格)
rate_label_frame = tk.LabelFrame(main_frame, text=" ⚙️ 实时汇率设置 (1 RMB = ?) ", padx=10, pady=10)
rate_label_frame.pack(fill=tk.X, pady=(0, 15))

rate_entries = {}
currencies = list(DEFAULT_RATES.keys())
for i, curr in enumerate(currencies):
    row = i // 3
    col = (i % 3) * 2
    tk.Label(rate_label_frame, text=f"{curr}:", font=("Arial", 9)).grid(row=row, column=col, sticky=tk.W, pady=2)
    ent = tk.Entry(rate_label_frame, width=7)
    ent.insert(0, str(DEFAULT_RATES[curr]))
    ent.grid(row=row, column=col+1, padx=(2, 5), pady=2)
    rate_entries[curr] = ent

# 2. 核心输入区
tk.Label(main_frame, text="💰 商品成本 (人民币 RMB):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
entry_cost_rmb = tk.Entry(main_frame, font=("Arial", 14))
entry_cost_rmb.pack(fill=tk.X, pady=(5, 12))
entry_cost_rmb.insert(0, "20")

tk.Label(main_frame, text="🚚 跨境运费 (输入数值并选择币种):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
ship_row = tk.Frame(main_frame)
ship_row.pack(fill=tk.X, pady=(5, 12))

entry_ship_val = tk.Entry(ship_row, font=("Arial", 14), width=15)
entry_ship_val.pack(side=tk.LEFT, fill=tk.X, expand=True)
entry_ship_val.insert(0, "1.95")

combo_ship_curr = ttk.Combobox(ship_row, values=currencies, width=12, state="readonly", font=("Arial", 12))
combo_ship_curr.set("🇲🇾 MYR")
combo_ship_curr.pack(side=tk.RIGHT, padx=(10, 0))

# 3. 输出设置
tk.Label(main_frame, text="💵 结果显示币种:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
combo_out_curr = ttk.Combobox(main_frame, values=currencies, state="readonly", font=("Arial", 12))
combo_out_curr.set("🇲🇾 MYR")
combo_out_curr.pack(fill=tk.X, pady=(5, 15))

# 4. 计算按钮
btn_calc = tk.Button(main_frame, text="开始定价计算 (Enter)", font=("Arial", 14, "bold"), 
                     bg="#00f2ea", fg="black", command=calculate_single, pady=10)
btn_calc.pack(fill=tk.X, pady=(0, 15))
root.bind('<Return>', calculate_single)

# 5. 结果显示
text_result = tk.Text(main_frame, height=10, font=("Menlo", 12), 
                      state=tk.DISABLED, padx=12, pady=12)
text_result.pack(fill=tk.X)

# 底部提示
tk.Label(main_frame, text="* 适配黑暗模式 | 右键.app可修改图标 | 汇率即改即用", font=("Arial", 8), fg="gray").pack(pady=5)

if __name__ == "__main__":
    root.mainloop()
