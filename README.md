# 医疗产品短名称生成器应用

这是一个将医疗产品完整描述转换为标准化缩写描述的应用程序，严格遵循加拿大医疗产品命名规则。

## 功能特点

- ✅ 自动生成符合规范的短名称（最大35字符）
- ✅ 支持自定义缩写词典（Excel/CSV格式）
- ✅ 严格的五位置结构规则
- ✅ 防止重复使用词汇
- ✅ 多种部署方式可选

## 快速开始

### 1. 安装依赖

```bash
# 进入项目目录
cd ~/Desktop/medical_shortname_app

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Mac/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 准备词典文件

确保你有一个词典文件（Excel或CSV格式）：
- 第一列：完整词汇
- 第二列：对应的缩写

示例：
```
Full Term    | Abbreviation
-------------|-------------
milliliter   | ML
kilogram     | KG
surgical     | SURG
```

## 运行应用

### 方案1：Streamlit 应用（推荐）

最简单易用的Web界面：

```bash
streamlit run app_streamlit.py
```

特点：
- 🎨 美观的用户界面
- 📊 实时显示处理结果
- 📜 处理历史记录
- 🔍 详细的组件分解

### 方案2：Gradio 应用

另一个优秀的Web界面选择：

```bash
python app_gradio.py
```

特点：
- 🚀 自动生成公共分享链接
- 📱 移动端友好
- 🎯 简洁直观的界面
- 📋 批量处理支持

### 方案3：Flask API

RESTful API 服务：

```bash
python app_flask.py
```

然后访问：
- Web界面：http://localhost:5000
- API文档：查看首页的API说明

API 端点：
- `POST /api/generate` - 生成单个短名称
- `POST /api/batch` - 批量生成
- `POST /api/load_dictionary` - 加载词典
- `GET /api/status` - 获取服务状态

## 使用示例

### Python 代码中使用

```python
from processor import CorrectedShortNameProcessor

# 创建处理器
processor = CorrectedShortNameProcessor('dictionary.xlsx')

# 处理描述
result = processor.process_full_description(
    "Solution Dextrose 5% 500 milliliters Bottle Viaflex Non-Latex"
)

print(f"短名称: {result['short_name']}")
print(f"字符数: {result['character_count']}/35")
```

### API 调用示例

```python
import requests

response = requests.post('http://localhost:5000/api/generate', 
    json={
        'description': 'Tape Surgical 1.25cm x 9.14m',
        'dictionary_path': '/path/to/dictionary.xlsx'
    }
)

data = response.json()
print(f"短名称: {data['short_name']}")
```

## 规则说明

### 五位置结构

1. **Position 1 - 产品类型（必填）**
   - 必须使用完整拼写，不能缩写
   - 例如：Solution, Tape, Scissor

2. **Position 2 - 产品名称（可选）**
   - 描述性词汇或百分比
   - 例如：Dextrose 5%, Surgical

3. **Position 3 - 主要变体（可选）**
   - 尺寸、品牌、左右标识
   - 例如：500ml, VICRYL, RT

4. **Position 4 - 次要变体（可选）**
   - 颜色、材质、特性
   - 例如：Sterile, Latex-Free

5. **Position 5 - 额外描述（可选）**
   - 包装类型或材料
   - 例如：Bottle, Plastic

### 关键规则

- 最大长度：35个字符
- 使用单数形式（除特定例外）
- 数字和单位之间无空格
- 每个词只能使用一次
- 优先使用公制单位

## 高级配置

### 自定义规则

编辑 `processor.py` 中的 `ShortNameRules` 类来自定义：
- 产品类型列表
- 品牌名称
- 单位转换
- 禁用字符

### 部署到生产环境

使用 Gunicorn 运行 Flask 应用：

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app_flask:app
```

使用 Docker：

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 常见问题

**Q: 词典文件格式要求？**
A: Excel (.xlsx, .xls) 或 CSV 文件，第一列为完整词汇，第二列为缩写。

**Q: 如何处理没有在词典中的词汇？**
A: 系统会保留原始形式或应用内置规则（如单位转换）。

**Q: 可以批量处理吗？**
A: 可以使用 Flask API 的批量端点，或在代码中循环调用。

## 许可证

本项目基于加拿大医疗产品描述标准化实施指南开发。

## 联系方式

如有问题或建议，请联系项目维护者。
