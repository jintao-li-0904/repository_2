"""
Canadian Medical Product Short Name Generator - Streamlit App
简易应用程序版本
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入核心处理器（需要将原始代码保存为processor.py）
try:
    from processor import CorrectedShortNameProcessor, print_result
except ImportError:
    st.error("请确保 processor.py 文件在同一目录下")
    st.stop()

# 设置页面配置
st.set_page_config(
    page_title="医疗产品短名称生成器",
    page_icon="🏥",
    layout="wide"
)

# 初始化session state
if 'processor' not in st.session_state:
    st.session_state.processor = None
if 'history' not in st.session_state:
    st.session_state.history = []

# 标题和说明
st.title("🏥 加拿大医疗产品短名称生成器")
st.markdown("""
### 功能说明
- 将医疗产品的完整描述自动转换为标准化的缩写描述
- 严格遵循加拿大医疗产品命名规则
- 最大长度限制：35个字符
- 支持自定义缩写词典
""")

# 侧边栏 - 词典管理
with st.sidebar:
    st.header("📚 词典设置")
    
    # 上传词典文件
    uploaded_file = st.file_uploader(
        "上传缩写词典文件",
        type=['xlsx', 'xls', 'csv'],
        help="Excel或CSV文件，第一列为完整词汇，第二列为缩写"
    )
    
    if uploaded_file is not None:
        # 保存上传的文件
        save_path = f"temp_{uploaded_file.name}"
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 加载词典
        try:
            st.session_state.processor = CorrectedShortNameProcessor(save_path)
            st.success(f"✅ 词典加载成功！共{len(st.session_state.processor.dictionary.abbreviations)}个缩写")
            
            # 显示部分词典内容
            with st.expander("查看词典示例"):
                dict_items = list(st.session_state.processor.dictionary.abbreviations.items())[:10]
                df_dict = pd.DataFrame(dict_items, columns=['完整词汇', '缩写'])
                st.dataframe(df_dict)
        except Exception as e:
            st.error(f"❌ 词典加载失败：{str(e)}")
    else:
        # 使用默认词典路径
        default_dict_path = str(Path(__file__).parent / "data" / "dictionary.xlsx")
        if Path(default_dict_path).exists():
            if st.button("使用默认词典"):
                try:
                    st.session_state.processor = CorrectedShortNameProcessor(default_dict_path)
                    st.success("✅ 默认词典加载成功！")
                except Exception as e:
                    st.error(f"❌ 默认词典加载失败：{str(e)}")
        else:
            st.info("请上传词典文件或确保默认词典存在")
    
    st.divider()
    
    # 规则说明
    st.header("📏 命名规则")
    st.markdown("""
    **五位置结构：**
    1. **产品类型** (必填，不缩写)
    2. **产品名称** (可选)
    3. **主要变体** (可选)
    4. **次要变体** (可选)
    5. **额外描述** (可选)
    
    **关键规则：**
    - 最大35个字符
    - 单数形式
    - 数字和单位之间无空格
    - 每个词只能使用一次
    """)

# 主界面
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 输入")
    
    # 输入框
    full_description = st.text_area(
        "输入完整的产品描述",
        height=100,
        placeholder="例如：Solution Dextrose 5% 500 milliliters Bottle Viaflex Non-Latex",
        help="输入英文的完整产品描述"
    )
    
    # 处理按钮
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    with col_btn1:
        process_btn = st.button("🔄 生成短名称", type="primary", use_container_width=True)
    with col_btn2:
        clear_btn = st.button("🗑️ 清除", use_container_width=True)
    
    # 示例输入
    st.subheader("💡 示例输入")
    examples = [
        "Solution Dextrose 5% 500 milliliters Bottle Viaflex Non-Latex",
        "Halloween HERSHEY chocolate bar 500 kilograms",
        "Suture VICRYL 0 Taper CT1 J340H",
        "Tape Surgical 1.25cm x 9.14m",
        "Scissor Mayo 170mm Straight"
    ]
    
    for i, example in enumerate(examples):
        if st.button(f"示例 {i+1}: {example[:40]}...", key=f"example_{i}"):
            st.session_state.example_text = example
            st.rerun()
    
    # 如果选择了示例，更新输入框
    if 'example_text' in st.session_state:
        full_description = st.session_state.example_text
        del st.session_state.example_text

with col2:
    st.header("📤 输出")
    
    # 处理输入
    if process_btn and full_description:
        if st.session_state.processor is None:
            st.error("❌ 请先加载词典！")
        else:
            with st.spinner("处理中..."):
                result = st.session_state.processor.process_full_description(full_description)
                
                # 添加到历史记录
                st.session_state.history.append({
                    'input': full_description,
                    'output': result['short_name'],
                    'success': result['success']
                })
                
                # 显示结果
                if result['success']:
                    st.success(f"✅ **生成成功**")
                    st.markdown(f"### 短名称：`{result['short_name']}`")
                    st.markdown(f"**字符数：** {result['character_count']}/35")
                else:
                    st.error("❌ **生成失败**")
                    st.markdown(f"### 短名称：`{result['short_name']}`")
                
                # 组件分解
                with st.expander("🔍 详细分解", expanded=True):
                    if result['components']:
                        df_components = pd.DataFrame([
                            {
                                '位置': comp['position_number'],
                                '位置名称': comp['position'],
                                '值': comp['value'],
                                '原始值': comp['original'],
                                '必填': '是' if comp['mandatory'] else '否',
                                '应用规则': ', '.join(comp['rules_applied'])
                            }
                            for comp in result['components']
                        ])
                        st.dataframe(df_components, use_container_width=True)
                
                # 消息
                if result['messages']:
                    with st.expander("💬 处理消息"):
                        for msg in result['messages']:
                            if 'Error' in msg:
                                st.error(msg)
                            elif 'Warning' in msg:
                                st.warning(msg)
                            else:
                                st.info(msg)
    
    # 清除按钮
    if clear_btn:
        st.rerun()

# 历史记录
st.divider()
st.header("📜 处理历史")

if st.session_state.history:
    # 创建历史记录表格
    df_history = pd.DataFrame(st.session_state.history)
    df_history['状态'] = df_history['success'].map({True: '✅ 成功', False: '❌ 失败'})
    df_history = df_history[['input', 'output', '状态']].rename(columns={
        'input': '输入',
        'output': '输出'
    })
    
    st.dataframe(df_history, use_container_width=True)
    
    # 清除历史按钮
    if st.button("🗑️ 清除历史"):
        st.session_state.history = []
        st.rerun()
else:
    st.info("暂无处理历史")

# 页脚
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>加拿大医疗产品短名称生成器 v1.0</p>
    <p>基于加拿大医疗产品描述标准化实施指南</p>
</div>
""", unsafe_allow_html=True)
