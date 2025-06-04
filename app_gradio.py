"""
Canadian Medical Product Short Name Generator - Gradio App
使用 Gradio 创建的交互式界面
"""

import gradio as gr
import pandas as pd
from pathlib import Path
from processor import CorrectedShortNameProcessor

# 全局变量存储处理器
processor = None

def load_dictionary(file_obj):
    """加载词典文件"""
    global processor
    
    if file_obj is None:
        return "请选择词典文件", None
    
    try:
        # 保存上传的文件
        file_path = file_obj.name
        
        # 创建处理器
        processor = CorrectedShortNameProcessor(file_path)
        
        # 显示词典信息
        dict_count = len(processor.dictionary.abbreviations)
        sample_items = list(processor.dictionary.abbreviations.items())[:10]
        
        df_sample = pd.DataFrame(sample_items, columns=['完整词汇', '缩写'])
        
        return f"✅ 词典加载成功！共 {dict_count} 个缩写", df_sample
        
    except Exception as e:
        return f"❌ 加载失败：{str(e)}", None

def process_description(full_description):
    """处理产品描述"""
    global processor
    
    if not full_description:
        return "请输入产品描述", "", None, []
    
    if processor is None:
        # 尝试使用默认词典
        default_path = str(Path(__file__).parent / "data" / "dictionary.xlsx")
        if Path(default_path).exists():
            processor = CorrectedShortNameProcessor(default_path)
        else:
            return "❌ 请先加载词典文件！", "", None, []
    
    # 处理输入
    result = processor.process_full_description(full_description)
    
    # 准备输出
    status = "✅ 生成成功" if result['success'] else "❌ 生成失败"
    short_name = result['short_name']
    char_info = f"字符数：{result['character_count']}/35"
    
    # 组件分解表格
    if result['components']:
        components_data = []
        for comp in result['components']:
            components_data.append([
                comp['position_number'],
                comp['position'],
                comp['value'],
                comp['original'],
                '是' if comp['mandatory'] else '否',
                ', '.join(comp['rules_applied'])
            ])
        
        df_components = pd.DataFrame(
            components_data,
            columns=['位置', '位置名称', '值', '原始值', '必填', '应用规则']
        )
    else:
        df_components = None
    
    # 消息列表
    messages = result['messages']
    
    return status, f"{short_name}\n\n{char_info}", df_components, messages

# 示例数据
examples = [
    ["Solution Dextrose 5% 500 milliliters Bottle Viaflex Non-Latex"],
    ["Halloween HERSHEY chocolate bar 500 kilograms"],
    ["Suture VICRYL 0 Taper CT1 J340H"],
    ["Tape Surgical 1.25cm x 9.14m"],
    ["Scissor Mayo 170mm Straight"],
    ["Glove Surgical Size 7.5 Sterile Latex-Free"],
    ["Catheter Foley 16 French 10ml Balloon Silicone"]
]

# 创建 Gradio 界面
with gr.Blocks(title="医疗产品短名称生成器", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🏥 加拿大医疗产品短名称生成器
    
    将医疗产品的完整描述自动转换为标准化的缩写描述（最大35个字符）
    """)
    
    with gr.Row():
        # 左侧：输入和控制
        with gr.Column(scale=1):
            gr.Markdown("## 📚 词典设置")
            
            dict_file = gr.File(
                label="上传词典文件", 
                file_types=[".xlsx", ".xls", ".csv"],
                type="file"
            )
            
            dict_load_btn = gr.Button("加载词典", variant="primary")
            dict_status = gr.Textbox(label="词典状态", interactive=False)
            dict_preview = gr.Dataframe(
                label="词典预览（前10个）",
                headers=["完整词汇", "缩写"],
                visible=True
            )
            
            gr.Markdown("## 📝 输入产品描述")
            
            input_text = gr.Textbox(
                label="完整产品描述",
                placeholder="输入英文的产品描述...",
                lines=3
            )
            
            process_btn = gr.Button("🔄 生成短名称", variant="primary")
            
            gr.Examples(
                examples=examples,
                inputs=input_text,
                label="示例输入"
            )
        
        # 右侧：输出结果
        with gr.Column(scale=1):
            gr.Markdown("## 📤 处理结果")
            
            status_output = gr.Textbox(label="处理状态", interactive=False)
            result_output = gr.Textbox(
                label="生成的短名称",
                interactive=False,
                lines=3
            )
            
            components_output = gr.Dataframe(
                label="组件分解",
                headers=["位置", "位置名称", "值", "原始值", "必填", "应用规则"]
            )
            
            messages_output = gr.JSON(label="处理消息")
    
    # 规则说明
    with gr.Accordion("📏 命名规则说明", open=False):
        gr.Markdown("""
        ### 五位置结构
        1. **产品类型** (必填，不缩写) - 如：Solution, Tape, Scissor
        2. **产品名称** (可选) - 如：Dextrose 5%, Surgical
        3. **主要变体** (可选) - 如：尺寸、品牌、左右
        4. **次要变体** (可选) - 如：颜色、材质特性
        5. **额外描述** (可选) - 如：包装类型
        
        ### 关键规则
        - 最大35个字符
        - 使用单数形式
        - 数字和单位之间无空格
        - 每个词只能使用一次
        - 位置1必须使用完整拼写
        """)
    
    # 事件绑定
    dict_load_btn.click(
        fn=load_dictionary,
        inputs=dict_file,
        outputs=[dict_status, dict_preview]
    )
    
    process_btn.click(
        fn=process_description,
        inputs=input_text,
        outputs=[status_output, result_output, components_output, messages_output]
    )

# 启动应用
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,  # 生成公共链接
        inbrowser=True  # 自动打开浏览器
    )
