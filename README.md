# LIN Signal Configuration Generation Tool
# LIN 信号配置生成工具
This is a Python script tool for generating LIN bus configuration header files (lin_cfg.h). It reads signal definitions from Excel files and automatically generates C-language header files compliant with LIN specifications.
这是一个用于生成LIN总线配置头文件（lin_cfg.h）的Python脚本工具。它可以从Excel文件中读取信号定义，自动生成符合LIN规范的C语言头文件。

✨ Features | 功能特性
📊 Read signal definitions from Excel files | 从Excel文件读取信号定义

🔧 Automatically generate LIN signal tables, signal IDs and index enums | 自动生成LIN信号表、信号ID和索引枚举

🧩 Generate message structs with bit fields for each PID | 为每个PID生成带位域定义的消息结构体

💡 Support default value settings | 支持默认值设置

Add default value comments in signal bit field definitions | 在信号位域定义行添加默认值注释

Add initialization values at the end of union definitions | 在联合体定义结尾添加整个消息的初始化值

⚙️ Automatically handle cross-byte signals (split into multiple 8-bit segments) | 自动处理跨字节信号（拆分为多个8位段）

✅ Comprehensive data validation | 全面的数据校验

Check for required fields | 检查必要字段是否存在

Verify position information consistency | 验证位置信息一致性

Check if default values are within valid ranges | 检查默认值是否在有效范围内

📝 Generate detailed error reports (with line numbers and problem descriptions) | 生成详细的错误报告（包含行号和问题描述）

🚀 Support multiple usage modes | 支持多种使用方式

Drag and drop Excel files onto the script icon | 拖放Excel文件到脚本图标上

Command line execution | 命令行运行

Interactive file selection | 交互式选择文件


📋 Input Format Requirements | 输入格式要求
The Excel file must contain the following columns:
Excel文件必须包含以下列：

Column Name	列名	Description	描述	Required	必填
PID	PID	Message Protocol Identifier (hex or decimal)	消息的协议标识符（十六进制或十进制）	Yes	是
PIDname	PIDname	Message name	消息名称	Yes	是
SignalName	SignalName	Signal name	信号名称	Yes	是
StartBit	StartBit	Signal start bit (0-based)	信号起始位（0起始）	Yes	是
EndBit	EndBit	Signal end bit (optional, mutually exclusive with Length)	信号结束位（可选，与长度二选一）	No	否
Length	Length	Signal length in bits (optional, mutually exclusive with EndBit)	信号长度（位）（可选，与结束位二选一）	No	否
DefaultValue	DefaultValue	Default signal value (decimal or hex, optional)	信号默认值（十进制或十六进制，可选）	No	否

Position Information Rules | 位置信息输入规则
You must provide one of the following combinations:
必须提供以下组合之一：

StartBit + EndBit

StartBit + Length

All three (consistency will be automatically verified)
三者都有（会自动校验一致性）

🖥 Usage | 使用方式
Method 1: Drag and Drop Excel File | 方式一：拖放Excel文件到脚本图标上
Drag and drop an Excel file onto the script file (.py or packaged .exe)
将Excel文件拖放到脚本文件（.py或打包后的.exe）上

The script automatically generates lin_cfg.h in the same directory as the Excel file
脚本会自动在Excel文件所在目录生成lin_cfg.h

A report window will display all errors and warnings upon completion
完成后会显示报告窗口，包含所有错误和警告信息

Method 2: Command Line Execution | 方式二：命令行运行
bash
python lin_cfg_generator.py path/to/your/excel.xlsx
Method 3: Interactive File Selection | 方式三：交互式选择文件
Double-click to run the script
双击运行脚本

Select an Excel file from the pop-up file dialog
在弹出的文件选择对话框中选择Excel文件

The script generates lin_cfg.h in the Excel file's directory
脚本会在Excel文件所在目录生成lin_cfg.h

A report window displays upon completion
完成后会显示报告窗口

📄 Output File (lin_cfg.h) | 输出文件
The generated header file contains:
生成的头文件包含：

LIN signal table definition (LIN_SIGNAL_TABLE) | LIN信号表定义

Signal ID enum (LIN_Signal_IDs) | 信号ID枚举

Signal index enum (LIN_Signal_Indexes) | 信号索引枚举

Message struct definitions (with bit fields) | 消息结构体定义（带位域）

Global variable declarations | 全局变量声明

Initialization value comments | 初始化值注释

⚠️ Error Reporting | 错误报告
If there are errors or warnings in the Excel file, a scrollable report window will display upon completion, containing:
如果Excel文件中存在错误或警告，生成完成后会显示可滚动的报告窗口，包含：

Errors: Issues that prevent signal processing (e.g., missing required fields, conflicting position information)
错误：阻止信号被处理的问题（如缺少必要字段、位置信息矛盾等）

Warnings: Issues that don't block processing but require attention (e.g., default values out of range)
警告：不影响处理但需要注意的问题（如默认值超出范围）

The script will attempt to generate a complete configuration file even if errors exist.
即使存在错误，脚本也会尽可能生成完整的配置文件。

📌 Notes | 注意事项
Ensure the Excel file is not open in another program
确保Excel文件未被其他程序打开

For cross-byte signals, the tool automatically splits them and adds comments explaining each segment
对于跨字节信号，工具会自动拆分，并在每个分段信号后添加注释说明

LIN bus characteristics:
LIN总线特性：

Uninitialized signal bits default to 1 (recessive level)
未初始化的信号位默认为1（隐性电平）

Dominant level (0) overrides recessive level (1)
显性电平（0）会覆盖隐性电平（1）

Diagnostic signals (DIAG_REQ and DIAG_RSP) are automatically added to the signal table but not included in struct definitions
诊断信号（DIAG_REQ 和 DIAG_RSP）会自动添加到信号表中，但不会生成结构体定义

📊 Example Excel File | 示例Excel文件

PID,   PIDname,     SignalName,                    StartBit,  EndBit,  length,  default_value
0x01,  ASCM_RL_01,  L_IBCM_VehSt,                  0,          2,        3,        3
0x01,  ASCM_RL_01,  L_ASCM_SRL_SeatMassgReLeReq     ,          3,        2,        
0x03,  ASCS_SRL_01, L_ASCS_SRL_ReLeSeatLenAdj,     0,          1,        2,        1
0x20,  DOOR_LOCK,   LockStatus,                   16,         16,        1,        1
