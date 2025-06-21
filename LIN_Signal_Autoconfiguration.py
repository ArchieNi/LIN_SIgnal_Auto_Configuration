import pandas as pd
import sys
import os
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox
import math
import atexit

# 注册退出清理函数
@atexit.register
def cleanup():
    import os
    import signal
    os.kill(os.getpid(), signal.SIGTERM)

def generate_lin_cfg(input_excel, output_file):
    validation_errors = []  # 存储校验错误信息
    validation_warnings = []  # 存储校验警告信息
    
    try:
        # 读取Excel文件
        df = pd.read_excel(input_excel)
    except Exception as e:
        messagebox.showerror("错误", f"读取Excel文件失败: {e}")
        return False
    
    # 检查必要的列是否存在
    required_columns = ['PID', 'PIDname', 'SignalName']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        messagebox.showerror("错误", f"Excel文件中缺少必要的列: {', '.join(missing_cols)}")
        return False
    
    # 检查位置信息列
    position_columns = ['StartBit', 'EndBit', 'Length']
    has_position = any(col in df.columns for col in position_columns)
    if not has_position:
        messagebox.showerror("错误", "Excel文件中缺少位置信息列（StartBit, EndBit 或 length）")
        return False
    
    # 检查是否有默认值列
    has_default = 'DefaultValue' in df.columns
    
    # 处理数据
    signals = []
    for idx, row in df.iterrows():
        row_num = idx + 2  # Excel行号（从1开始，标题行是1，数据从2开始）
        pid = row['PID']
        pidname = row['PIDname']
        signalname = row['SignalName']
        
        # 获取位置信息
        start_bit = row.get('StartBit', None)
        end_bit = row.get('EndBit', None)
        sig_length = row.get('Length', None)
        default_val = row.get('DefaultValue', None) if has_default else None
        
        # 确保PID数据类型正确
        if isinstance(pid, str) and pid.startswith('0x'):
            try:
                pid = int(pid, 16)
            except:
                validation_errors.append(f"行 {row_num}: 无效的PID值: {pid}")
                continue
        else:
            try:
                pid = int(pid)
            except:
                validation_errors.append(f"行 {row_num}: 无效的PID值: {pid}")
                continue
        
        # 处理位置信息
        try:
            # 尝试解析起始位
            if pd.isna(start_bit):
                validation_errors.append(f"行 {row_num}: 缺少起始位(StartBit)")
                continue
            start_bit = int(start_bit)
            
            # 处理结束位和长度
            if not pd.isna(end_bit) and not pd.isna(sig_length):
                # 三者都有 - 进行校验
                end_bit = int(end_bit)
                sig_length = int(sig_length)
                
                # 计算期望长度
                expected_length = end_bit - start_bit + 1
                if sig_length != expected_length:
                    validation_errors.append(
                        f"行 {row_num}: 长度不一致 - 计算长度: {expected_length}, 指定长度: {sig_length} "
                        f"(起始位: {start_bit}, 结束位: {end_bit})"
                    )
                    continue
            elif not pd.isna(end_bit):
                # 有起始位和结束位
                end_bit = int(end_bit)
                sig_length = end_bit - start_bit + 1
            elif not pd.isna(sig_length):
                # 有起始位和长度
                sig_length = int(sig_length)
                end_bit = start_bit + sig_length - 1
            else:
                validation_errors.append(f"行 {row_num}: 缺少结束位(EndBit)或长度(length)")
                continue
            
            # 验证长度有效性
            if sig_length <= 0:
                validation_errors.append(f"行 {row_num}: 无效的长度: {sig_length} (必须大于0)")
                continue
                
            if end_bit < start_bit:
                validation_errors.append(f"行 {row_num}: 结束位({end_bit})小于起始位({start_bit})")
                continue
        except Exception as e:
            validation_errors.append(f"行 {row_num}: 无效的位置信息 - {str(e)}")
            continue
        
        # 处理默认值
        if has_default and not pd.isna(default_val):
            try:
                if isinstance(default_val, str):
                    if default_val.startswith('0x'):
                        default_val = int(default_val, 16)
                    else:
                        default_val = int(default_val)
                else:
                    default_val = int(default_val)
                
                # 验证默认值是否在范围内
                max_val = (1 << sig_length) - 1
                if default_val > max_val:
                    validation_warnings.append(
                        f"行 {row_num}: 默认值 {default_val} 超出范围 (最大允许值: {max_val} "
                        f"对于 {sig_length} 位信号)"
                    )
            except:
                default_val = None
                validation_warnings.append(f"行 {row_num}: 无法解析信号 '{signalname}' 的默认值: {row['DefaultValue']}")
        
        signals.append((pid, pidname, signalname, start_bit, end_bit, sig_length, default_val))
    
    if not signals and not validation_errors:
        validation_errors.append("没有找到有效的信号定义")
    
    # 按PID分组信号
    pid_groups = defaultdict(list)
    for sig in signals:
        pid_groups[sig[1]].append(sig)
    
    # 生成输出文件
    try:
        with open(output_file, 'w') as f:
            # 文件头
            f.write("#ifndef _LIN_CFG__H\n")
            f.write("#define _LIN_CFG__H\n\n")
            f.write("#include \"stdint.h\"\n\n")
            f.write("/*LIN_Application_Define*/\n\n")
            
            # LIN_SIGNAL_TABLE 宏 - 添加固定的诊断信号
            f.write("#define LIN_SIGNAL_TABLE(ENTRY) \\\n")
            unique_pids = {}
            for pid_name, sigs in pid_groups.items():
                pid_val = sigs[0][0]
                unique_pids[pid_name] = pid_val
                f.write(f"    ENTRY({pid_name}, {hex(pid_val)})     \\\n")
            
            # 添加固定的诊断信号
            f.write("    ENTRY(DIAG_REQ, 0x3C)       \\\n")
            f.write("    ENTRY(DIAG_RSP, 0x3D)\n\n")
            
            # 信号ID枚举
            f.write("enum LIN_Signal_IDs\n{\n")
            f.write("#define GEN_ID_ENUM(name, id) name = id,\n")
            f.write("    LIN_SIGNAL_TABLE(GEN_ID_ENUM)\n")
            f.write("#undef GEN_ID_ENUM\n")
            f.write("};\n\n")
            
            # 信号索引枚举
            f.write("enum LIN_Signal_Indexes\n{\n")
            f.write("#define GEN_IDX_ENUM(name, id) name##_IDX,\n")
            f.write("    LIN_SIGNAL_TABLE(GEN_IDX_ENUM)\n")
            f.write("        TABLE_SIZE,\n")
            f.write("#undef GEN_IDX_ENUM\n")
            f.write("};\n\n")
            
            # 为每个PID生成消息结构体（排除诊断信号）
            for pid_name, sigs in pid_groups.items():
                # 跳过诊断信号
                if pid_name in ["DIAG_REQ", "DIAG_RSP"]:
                    continue
                    
                pid_val = sigs[0][0]
                
                # 初始化默认值数组 - LIN总线隐性电平为1
                default_bytes = [0xFF] * 8  # 初始化为全1（隐性电平）
                if has_default:
                    # 计算每个字节的默认值
                    for sig in sigs:
                        _, _, sig_name, start, end, sig_length, default_val = sig
                        
                        if default_val is None or pd.isna(default_val):
                            # 没有默认值，保持为1（隐性电平）
                            continue
                            
                        # 计算信号在字节中的位置
                        for bit in range(start, end + 1):
                            byte_idx = bit // 8
                            bit_in_byte = bit % 8
                            
                            # 计算该位在默认值中的位置
                            bit_pos_in_sig = bit - start
                            bit_val = (default_val >> bit_pos_in_sig) & 0x01
                            
                            # 设置字节中的位
                            if bit_val:
                                # 设置位为1（隐性电平）
                                default_bytes[byte_idx] |= (1 << bit_in_byte)
                            else:
                                # 设置位为0（显性电平）
                                default_bytes[byte_idx] &= ~(1 << bit_in_byte)
                
                # 生成联合体定义开始
                f.write(f"typedef union // {hex(pid_val)}\n")
                f.write("{\n")
                f.write("    struct\n    {\n")
                
                # 按字节组织信号
                byte_signals = [[] for _ in range(8)]  # 8个字节
                for sig in sigs:
                    _, _, sig_name, start, end, sig_length, default_val = sig
                    
                    # 如果信号跨多个字节
                    if sig_length > 8:
                        # 将长信号拆分为多个8位段
                        current_bit = start
                        segment_index = 0
                        while current_bit <= end:
                            segment_end = min(current_bit + 7, end)  # 最多8位
                            segment_length = segment_end - current_bit + 1
                            
                            byte_idx = current_bit // 8
                            if byte_idx < 8:
                                # 添加分段信号
                                segment_name = sig_name
                                byte_signals[byte_idx].append((segment_name, current_bit % 8, segment_end % 8, default_val))
                            
                            current_bit = segment_end + 1
                            segment_index += 1
                    else:
                        # 单字节信号
                        byte_idx = start // 8
                        if byte_idx < 8:
                            start_in_byte = start % 8
                            end_in_byte = end % 8
                            byte_signals[byte_idx].append((sig_name, start_in_byte, end_in_byte, default_val))
                
                # 生成每个字节的位域
                for byte_idx in range(8):
                    f.write(f"        /*byte{byte_idx}*/\n")
                    sigs_in_byte = byte_signals[byte_idx]
                    
                    # 如果没有信号，整个字节都是保留位
                    if not sigs_in_byte:
                        f.write(f"        uint8_t _reserved_{byte_idx} : 8;\n")
                        continue
                    
                    # 按起始位排序信号（从最低位到最高位）
                    sigs_in_byte.sort(key=lambda x: x[1])
                    
                    # 自动填充保留位
                    bit_covered = [False] * 8
                    for sig_name, start, end, default_val in sigs_in_byte:
                        # 确保结束位不小于起始位
                        if end < start:
                            end = start
                        # 标记覆盖的位
                        for bit in range(start, min(end + 1, 8)):
                            bit_covered[bit] = True
                    
                    # 生成位域定义
                    current_pos = 0
                    segments = []
                    
                    # 收集所有段（信号和保留位）
                    for sig in sigs_in_byte:
                        sig_name, start, end, default_val = sig
                        # 添加前面的保留位
                        if start > current_pos:
                            segments.append(('reserved', current_pos, start - 1, None))
                        # 添加信号
                        segments.append((sig_name, start, min(end, 7), default_val))
                        current_pos = min(end + 1, 8)
                    
                    # 添加最后的保留位
                    if current_pos < 8:
                        segments.append(('reserved', current_pos, 7, None))
                    
                    # 生成位域定义
                    for segment in segments:
                        sig_type, start, end, default_val = segment
                        length = end - start + 1
                        
                        if length <= 0:
                            continue
                            
                        if sig_type == 'reserved':
                            f.write(f"        uint8_t _reserved_{byte_idx}_{start} : {length};\n")
                        else:
                            # 添加默认值注释（如果有）
                            default_comment = ""
                            if default_val is not None and not pd.isna(default_val):
                                # 计算该段信号的值
                                seg_value = 0
                                for bit in range(start, end + 1):
                                    bit_in_sig = bit - start
                                    bit_val = (default_val >> bit_in_sig) & 0x01
                                    seg_value |= (bit_val << (bit - start))
                                
                                # 转换为十六进制
                                hex_digits = math.ceil(length / 4)
                                hex_fmt = f"0x{{:0{hex_digits}X}}"
                                default_comment = f" /* default: {hex_fmt.format(seg_value)} */"
                            
                            f.write(f"        uint8_t {sig_type} : {length};{default_comment}\n")
                
                f.write("    };\n")
                f.write("    uint8_t _buf[8];\n")
                
                # 添加联合体初始化注释
                if has_default:
                    hex_bytes = [f"0x{b:02X}" for b in default_bytes]
                    f.write(f"}} {pid_name}_MSG_t; /* init_DefaultValue = {{{', '.join(hex_bytes)}}} */\n\n")
                else:
                    f.write(f"}} {pid_name}_MSG_t;\n\n")
            
            # 生成全局变量声明（排除诊断信号）
            f.write("/* Global message variables */\n")
            for pid_name in pid_groups.keys():
                # 跳过诊断信号
                if pid_name in ["DIAG_REQ", "DIAG_RSP"]:
                    continue
                    
                var_name = pid_name.lower() + '_msg_t'
                f.write(f"extern {pid_name}_MSG_t {var_name};\n")
            
            # 文件尾
            f.write("\n#endif\n")
        
        # 显示校验结果
        result_message = f"成功生成LIN配置文件: {output_file}\n\n"
        
        if validation_errors:
            result_message += "===== 错误 =====\n"
            result_message += "\n".join(validation_errors) + "\n\n"
            result_message += "部分信号可能未包含在生成文件中\n"
        
        if validation_warnings:
            result_message += "===== 警告 =====\n"
            result_message += "\n".join(validation_warnings) + "\n"
        
        if not validation_errors and not validation_warnings:
            result_message += "所有信号校验通过，无错误或警告"
        
        return result_message
    except Exception as e:
        messagebox.showerror("错误", f"生成文件失败: {e}")
        return False

def select_excel_file():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    file_path = filedialog.askopenfilename(
        title="选择Excel文件",
        filetypes=[("Excel文件", "*.xlsx;*.xls")]
    )
    return file_path

def main():
    # 如果有命令行参数，使用第一个参数作为Excel文件路径
    if len(sys.argv) > 1:
        input_excel = sys.argv[1]
        # 检查文件是否存在
        if not os.path.isfile(input_excel):
            messagebox.showerror("错误", f"文件不存在: {input_excel}")
            return
    else:
        input_excel = select_excel_file()
    
    if not input_excel:
        return
    
    # 确定输出文件路径
    output_dir = os.path.dirname(input_excel)
    output_file = os.path.join(output_dir, "lin_cfg.h")
    
    # 生成配置文件
    result = generate_lin_cfg(input_excel, output_file)
    
    # 显示完成消息
    if isinstance(result, str):
        # 创建可滚动的文本窗口显示结果
        root = tk.Tk()
        root.title("LIN配置文件生成结果")
        
        text_frame = tk.Frame(root)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, width=80, height=20)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.insert(tk.END, result)
        text_widget.config(state=tk.DISABLED)  # 设置为只读
        
        # 添加关闭按钮
        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 修复：确保窗口完全关闭
        close_button = tk.Button(button_frame, text="关闭", 
                                command=lambda: [root.destroy(), root.quit()])
        close_button.pack(side=tk.RIGHT)
        
        # 绑定窗口关闭事件
        root.protocol("WM_DELETE_WINDOW", lambda: [root.destroy(), root.quit()])
        
        root.mainloop()
    elif result is False:
        messagebox.showerror("错误", "生成LIN配置文件失败")
    else:
        messagebox.showinfo("完成", f"LIN配置文件已生成:\n{output_file}")

if __name__ == "__main__":
    # 确保只运行一次
    if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
        # 在调试模式下运行
        main()
    else:
        # 在正常模式下运行
        try:
            main()
        except Exception as e:
            messagebox.showerror("致命错误", f"程序崩溃: {str(e)}")
            sys.exit(1)