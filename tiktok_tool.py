import tkinter as tk
from tkinter import messagebox
import math

# --- 核心财务配置 (锁定) ---
EXCHANGE_RATE_RMB_TO_MYR = 1 / 1.7  # 1:1.7 汇率下的 RMB 到 MYR 折算
EXCHANGE_RATE_MYR_TO_RMB = 1.7
TARGET_PROFIT_RATE = 0.20        # 20% 目标利润率
TARGET_DISCOUNT_RATE = 0.51      # 51% 目标折扣
FIXED_FEES_MYR = 0.54            # 平台固定费 (MYR)
# 计算系数：1 - 佣金(7.02%) - 服务费(3.78%) - 利润(20%)
DEDUCTION_COEFFICIENT = 0.692

# --- 核心计算逻辑 ---
def core_calculation(cost_rmb, shipping_myr):
    """
    定价公式：
    Deal_Price = (成本MYR + 运费MYR + 固定费) / (1 - 佣金% - 服务费% - 利润%)
    """
    # 成本折算
    cost_myr = cost_rmb * EXCHANGE_RATE_RMB_TO_MYR
    # 计算实际成交价
    deal_price = (cost_myr + shipping_myr + FIXED_FEES_MYR) / DEDUCTION_COEFFICIENT
    deal_price = round(deal_price, 2)
    # 反推原价 (向上取整，确保打完折后仍能覆盖成交价)
    original_price = math.ceil(deal_price / (1 - TARGET_DISCOUNT_RATE))
    # 财务数据
    commission_myr = round(deal_price * 0.0702, 2)
    profit_myr = round(deal_price * TARGET_PROFIT_RATE, 2)
    profit_rmb = round(profit_myr * EXCHANGE_RATE_MYR_TO_RMB, 2)
    
    return deal_price, original_price, commission_myr, profit_myr, profit_rmb

# --- 功能：触发计算 ---
def calculate_single(event=None): # 增加 event 参数以支持回车键
    try:
        cost_rmb = float(entry_cost_rmb.get())
        shipping_myr = float(entry_shipping_myr.get())
        
        d, o, c, p_m, p_r = core_calculation(cost_rmb, shipping_myr)
        
        text_result.config(state=tk.NORMAL) 
        text_result.delete(1.0, tk.END) 
        
        res = (
            f"--- 后台填写建议 ---\n"
            f"建议原价：RM {o:.2f} (向上取整)\n"
            f"后台折扣：{TARGET_DISCOUNT_RATE*100:.0f}%\n"
            f"实际成交：RM {d:.2f}\n"
            f"--------------------\n"
            f"--- 预估利润预览 ---\n"
            f"平台佣金: RM {c:.2f}\n"
            f"单件利润: RM {p_m:.2f}\n"
            f"折合人民币: ¥ {p_r:.2f}\n"
        )
        text_result.insert(tk.END, res)
        text_result.config(state=tk.DISABLED) 
        
    except ValueError:
        messagebox.showerror("输入错误", "请输入正确的数字（成本和运费）")

# --- 界面设置 ---
root = tk.Tk()
root.title("TikTok定价助手 (精简版)")
root.geometry("360x450")

# 主容器
main_frame = tk.Frame(root, padx=20, pady=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# 输入部分
tk.Label(main_frame, text="💰 成本 (RMB):", font=("Arial", 10)).pack(anchor=tk.W)
entry_cost_rmb = tk.Entry(main_frame, font=("Arial", 12))
entry_cost_rmb.pack(fill=tk.X, pady=(5, 15))
entry_cost_rmb.focus_set() # 自动聚焦

tk.Label(main_frame, text="🚚 跨境运费 (MYR):", font=("Arial", 10)).pack(anchor=tk.W)
entry_shipping_myr = tk.Entry(main_frame, font=("Arial", 12))
entry_shipping_myr.pack(fill=tk.X, pady=(5, 20))

# 计算按钮
btn_calc = tk.Button(main_frame, text="开始定价 (Enter)", font=("Arial", 12, "bold"), 
                     bg="#00f2ea", fg="black", command=calculate_single, pady=10)
btn_calc.pack(fill=tk.X, pady=(0, 20))

# 绑定回车键
root.bind('<Return>', calculate_single)

# 结果展示
text_result = tk.Text(main_frame, height=10, font=("Consolas", 10), 
                      state=tk.DISABLED, bg="#f4f4f4", padx=10, pady=10)
text_result.pack(fill=tk.X)

if __name__ == "__main__":
    root.mainloop()