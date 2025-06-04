"""
Canadian Medical Product Short Name Generator - Flask API
Azure部署版本
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
from pathlib import Path
from processor import CorrectedShortNameProcessor

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局处理器实例
processor = None

# 获取应用根目录
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DICTIONARY_PATH = BASE_DIR / "data" / "dictionary.xlsx"

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>医疗产品短名称生成器 API</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .input-group {
            margin: 20px 0;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
            display: none;
        }
        .success {
            color: #28a745;
        }
        .error {
            color: #dc3545;
        }
        .api-docs {
            margin-top: 40px;
            padding: 20px;
            background-color: #e9ecef;
            border-radius: 5px;
        }
        pre {
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏥 医疗产品短名称生成器 API</h1>
        
        <div class="input-group">
            <label for="description">产品完整描述：</label>
            <textarea id="description" rows="3" placeholder="例如：Solution Dextrose 5% 500 milliliters Bottle Viaflex Non-Latex"></textarea>
        </div>
        
        <button onclick="generateShortName()">生成短名称</button>
        
        <div id="result" class="result"></div>
        
        <div class="api-docs">
            <h2>API 文档</h2>
            
            <h3>1. 生成短名称</h3>
            <pre>
POST /api/generate
Content-Type: application/json

{
    "description": "Solution Dextrose 5% 500 milliliters Bottle Viaflex Non-Latex"
}
            </pre>
            
            <h3>2. 获取状态</h3>
            <pre>
GET /api/status
            </pre>
        </div>
    </div>
    
    <script>
        async function generateShortName() {
            const description = document.getElementById('description').value;
            const resultDiv = document.getElementById('result');
            
            if (!description) {
                alert('请输入产品描述');
                return;
            }
            
            resultDiv.style.display = 'none';
            resultDiv.innerHTML = '处理中...';
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        description: description
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = `
                        <h3 class="success">✅ 生成成功</h3>
                        <p><strong>短名称：</strong> ${data.short_name}</p>
                        <p><strong>字符数：</strong> ${data.character_count}/35</p>
                        <h4>组件分解：</h4>
                        <ul>
                            ${data.components.map(c => `
                                <li>位置 ${c.position_number} (${c.position}): 
                                    <strong>${c.value}</strong> ← ${c.original}
                                    ${c.mandatory ? ' (必填)' : ''}
                                </li>
                            `).join('')}
                        </ul>
                        ${data.messages.length > 0 ? `
                            <h4>消息：</h4>
                            <ul>
                                ${data.messages.map(m => `<li>${m}</li>`).join('')}
                            </ul>
                        ` : ''}
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <h3 class="error">❌ 生成失败</h3>
                        <p>${data.error || '未知错误'}</p>
                    `;
                }
                
                resultDiv.style.display = 'block';
                
            } catch (error) {
                resultDiv.innerHTML = `
                    <h3 class="error">❌ 请求失败</h3>
                    <p>${error.message}</p>
                `;
                resultDiv.style.display = 'block';
            }
        }
    </script>
</body>
</html>
"""

# 初始化：加载默认词典
def init_processor():
    """初始化处理器，加载默认词典"""
    global processor
    if DEFAULT_DICTIONARY_PATH.exists():
        try:
            processor = CorrectedShortNameProcessor(str(DEFAULT_DICTIONARY_PATH))
            print(f"✅ 成功加载词典：{DEFAULT_DICTIONARY_PATH}")
        except Exception as e:
            print(f"⚠️ 加载词典失败：{e}")
            processor = CorrectedShortNameProcessor()
    else:
        print(f"⚠️ 词典文件不存在：{DEFAULT_DICTIONARY_PATH}")
        processor = CorrectedShortNameProcessor()

@app.route('/')
def index():
    """显示简单的Web界面"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取API状态"""
    global processor
    
    return jsonify({
        'status': 'running',
        'dictionary_loaded': processor is not None,
        'dictionary_path': str(DEFAULT_DICTIONARY_PATH) if processor else None,
        'abbreviation_count': len(processor.dictionary.abbreviations) if processor else 0
    })

@app.route('/api/generate', methods=['POST'])
def generate_short_name():
    """生成短名称"""
    global processor
    
    data = request.get_json()
    description = data.get('description', '').strip()
    
    if not description:
        return jsonify({
            'success': False,
            'error': '请提供产品描述'
        }), 400
    
    # 如果还没有处理器，初始化一个
    if processor is None:
        init_processor()
    
    try:
        # 处理描述
        result = processor.process_full_description(description)
        
        return jsonify({
            'success': result['success'],
            'original': result['original'],
            'short_name': result['short_name'],
            'character_count': result['character_count'],
            'components': result['components'],
            'messages': result['messages']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/batch', methods=['POST'])
def batch_generate():
    """批量生成短名称"""
    global processor
    
    data = request.get_json()
    descriptions = data.get('descriptions', [])
    
    if not descriptions:
        return jsonify({
            'success': False,
            'error': '请提供产品描述列表'
        }), 400
    
    # 初始化处理器
    if processor is None:
        init_processor()
    
    results = []
    for desc in descriptions:
        try:
            result = processor.process_full_description(desc)
            results.append({
                'original': desc,
                'short_name': result['short_name'],
                'success': result['success'],
                'character_count': result['character_count']
            })
        except Exception as e:
            results.append({
                'original': desc,
                'short_name': '',
                'success': False,
                'error': str(e)
            })
    
    return jsonify({
        'success': True,
        'count': len(results),
        'results': results
    })

# 应用启动时初始化
with app.app_context():
    init_processor()

if __name__ == '__main__':
    # Azure App Service使用环境变量PORT
    port = int(os.environ.get('PORT', 5000))
    # 生产环境不使用debug模式
    app.run(host='0.0.0.0', port=port, debug=False)
