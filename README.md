# 🚀 LIN 信号配置生成工具 - 说明文档  
这是一个 Python 工具，用于从 Excel 信号定义自动生成符合 LIN 总线规范的 C 语言头文件 (`lin_cfg.h`)。该工具简化了汽车电子开发中的 LIN 总线配置流程，支持错误检查、自动信号处理和多种使用方式。  

## 核心功能  
| 功能 | 描述 |
|------|------|
| 📊 Excel 导入 | 从 Excel 文件读取信号定义 |
| 🔧 自动生成 | 创建符合规范的 LIN 配置头文件 |
| ⚙️ 信号处理 | 自动处理跨字节信号 |
| ✅ 数据验证 | 全面的输入数据校验 |
| 📝 错误报告 | 详细的错误和警告信息 |
| 🚀 多种使用方式 | 支持拖放、命令行和交互式操作 |

## 安装依赖
```bash
pip install pandas openpyxl
```

## 使用方式

### 方式一：拖放文件（推荐）
1. 将 Excel 文件拖放到脚本图标上
2. 自动生成 `lin_cfg.h`
3. 显示详细错误报告

### 方式二：命令行运行
```bash
python LIN_Signal_Autoconfiguration.py path/to/your/excel.xlsx
```

### 方式三：交互式选择
1. 双击运行脚本
2. 从对话框选择 Excel 文件
3. 自动生成配置文件

## 输入格式要求
Excel 文件必须包含以下列：

| 列名 | 描述 | 必填 | 示例 |
|------|------|------|------|
| **PID** | 协议标识符 | ✔️ | `0x01` |
| **PIDname** | 消息名称 | ✔️ | `DOOR_LOCK` |
| **SignalName** | 信号名称 | ✔️ | `LockStatus` |
| **StartBit** | 起始位 | ✔️ | `0` |
| **EndBit** | 结束位 | ➖ | `7` |
| **Length** | 信号长度 | ➖ | `8` |
| **DefaultValue** | 默认值 | ➖ | `1` |

## 输出文件 (lin_cfg.h)
生成的头文件包含以下关键部分：

### 信号表定义
```c
#define LIN_SIGNAL_TABLE(ENTRY) \
    ENTRY(ASCM_RL_01, 0x1)     \
    ENTRY(ASCS_SRL_01, 0x3)     \
    ENTRY(DIAG_REQ, 0x3C)       \
    ENTRY(DIAG_RSP, 0x3D)
```

### 信号ID枚举
```c
enum LIN_Signal_IDs
{
#define GEN_ID_ENUM(name, id) name = id,
    LIN_SIGNAL_TABLE(GEN_ID_ENUM)
#undef GEN_ID_ENUM
};
```

### 消息结构体
```c
typedef union // 0x1
{
    struct
    {
        /*byte0*/
        uint8_t L_IBCM_VehSt : 3; /* default: 0x0 */
        uint8_t L_ASCM_SRL_ReLeSeatMassgLvlReq : 3; /* default: 0x0 */
        uint8_t L_ASCM_SRL_SeatMassgReLeReq : 2;
        /*byte1*/
        uint8_t L_ASCM_SRL_ReLeSeatMassgModReq : 4; /* default: 0x0 */
        // ... 其他信号
    };
    uint8_t _buf[8];
} ASCM_RL_01_MSG_t; /* init_DefaultValue = {0xC0, 0x00, 0xBF, 0xC0, 0xFF, 0xFB, 0xFF, 0xFF} */
```

## 示例

### Excel 输入示例
```csv
PID,PIDname,SignalName,StartBit,EndBit,Length,DefaultValue
0x01,ASCM_RL_01,L_IBCM_VehSt,0,2,3,3
0x01,ASCM_RL_01,L_ASCM_SRL_SeatMassgReLeReq,3,,2,
0x03,ASCS_SRL_01,L_ASCS_SRL_ReLeSeatLenAdj,0,1,2,1
```

### 生成的头文件示例
```c
#ifndef _LIN_CFG__H
#define _LIN_CFG__H

#include "stdint.h"

/* LIN_Application_Define */

#define LIN_SIGNAL_TABLE(ENTRY) \
    ENTRY(ASCM_RL_01, 0x1)     \
    ENTRY(ASCS_SRL_01, 0x3)     \
    ENTRY(DIAG_REQ, 0x3C)       \
    ENTRY(DIAG_RSP, 0x3D)

enum LIN_Signal_IDs
{
#define GEN_ID_ENUM(name, id) name = id,
    LIN_SIGNAL_TABLE(GEN_ID_ENUM)
#undef GEN_ID_ENUM
};

// ... 其他部分 ...

#endif
```

## 完整脚本
```python
# 这里是完整的 Python 脚本代码
# 由于代码较长，已放在单独的 LIN_Signal_Autoconfiguration.py 文件中
# 用户可以从以下链接下载完整脚本：
# [下载脚本](https://github.com/ArchieNi/LIN_SIgnal_Autoconfiguration/releases)
```

## 错误报告
工具会生成详细的错误报告，包括：
- ❌ 缺少必要字段
- ❌ 位置信息不一致
- ⚠️ 默认值超出范围
- ℹ️ 信号处理警告

报告以可滚动窗口显示，方便用户查看所有问题。

## 注意事项
1. **LIN 总线特性**：
   - 未初始化信号位默认为 1（隐性电平）
   - 显性电平（0）覆盖隐性电平（1）

2. **特殊信号处理**：
   - 诊断信号自动添加到信号表
   - 不生成诊断信号的结构体定义

3. **跨字节信号**：
   - 自动拆分为多个8位段
   - 添加详细注释说明分段情况

## 许可证
本项目采用 MIT 许可证 - 详情见 [LICENSE](https://github.com/ArchieNi/LIN_SIgnal_Autoconfiguration/blob/main/LICENSE) 文件。

---

> **提示**：建议使用 Python 3.7 或更高版本以获得最佳兼容性。完整脚本和示例文件可从项目仓库获取。

**[⬇️ 下载完整脚本](https://github.com/ArchieNi/LIN_SIgnal_Autoconfiguration/releases)**  
**[⭐ 在 GitHub 上关注此项目](https://github.com/ArchieNi/LIN_Signal_Autoconfiguration)**
