from flask import Flask, render_template, request, jsonify, send_file, url_for
import replicate
import os
import uuid
from datetime import datetime
import base64
from io import BytesIO
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/Users/zl/replicate_web/uploads'
app.config['GENERATED_FOLDER'] = '/Users/zl/replicate_web/static/images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

# 设置 API Token - 从环境变量读取
api_token = os.environ.get('REPLICATE_API_TOKEN')
if api_token:
    os.environ['REPLICATE_API_TOKEN'] = api_token
else:
    print("⚠️ 警告：未设置 REPLICATE_API_TOKEN 环境变量")
    print("请运行：export REPLICATE_API_TOKEN=your_token_here")

def save_image(image_data, filename_prefix="flux"):
    """保存图像并返回文件路径"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{filename_prefix}_{timestamp}_{unique_id}.png"
    filepath = os.path.join(app.config['GENERATED_FOLDER'], filename)
    
    if isinstance(image_data, list):
        with open(filepath, 'wb') as f:
            f.write(image_data[0].read())
    else:
        with open(filepath, 'wb') as f:
            f.write(image_data.read())
    
    return filename

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_image():
    """生成图像"""
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()
        model = data.get('model', 'google/imagen-4')  # 默认使用 Google Imagen 4
        
        if not prompt:
            return jsonify({'error': '请输入提示词'}), 400
        
        print(f"使用模型: {model}")
        print(f"提示词: {prompt}")
        
        # 生成图像
        image_output = replicate.run(model, input={"prompt": prompt})
        
        # 保存图像
        filename = save_image(image_output, "text2img")
        image_url = url_for('static', filename=f'images/{filename}')
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'filename': filename,
            'prompt': prompt,
            'model': model
        })
        
    except Exception as e:
        print(f"生成图像出错: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/img2img', methods=['POST'])
def image_to_image():
    """图生图"""
    try:
        prompt = request.form.get('prompt', '').strip()
        model = request.form.get('model', 'black-forest-labs/flux-kontext-pro')
        image_count = int(request.form.get('imageCount', 1))
        
        if not prompt:
            return jsonify({'error': '请输入提示词'}), 400
        
        print(f"图生图模型: {model}")
        print(f"提示词: {prompt}")
        print(f"图片数量: {image_count}")
        
        # 收集所有上传的图片
        uploaded_files = []
        for i in range(image_count):
            file_key = f'image{i}'
            if file_key not in request.files:
                return jsonify({'error': f'未找到图片 {i+1}'}), 400
            
            file = request.files[file_key]
            if file.filename == '':
                return jsonify({'error': f'图片 {i+1} 为空'}), 400
            
            # 保存临时文件
            upload_filename = f"{str(uuid.uuid4())}_{i}.png"
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], upload_filename)
            file.save(upload_path)
            uploaded_files.append(upload_path)
        
        try:
            # 构建输入参数
            input_params = {"prompt": prompt}
            
            # 根据图片数量决定如何传递图片
            if image_count == 1:
                # 单张图片
                with open(uploaded_files[0], "rb") as f:
                    input_params["image"] = f
                    image_output = replicate.run(model, input=input_params)
            else:
                # 多张图片 - 根据模型不同可能有不同的参数名
                # 尝试常见的多图片参数名
                try:
                    # 方法1：使用 images 数组
                    with open(uploaded_files[0], "rb") as f1:
                        input_params["image"] = f1
                        if image_count > 1 and len(uploaded_files) > 1:
                            with open(uploaded_files[1], "rb") as f2:
                                input_params["image2"] = f2
                                if image_count > 2 and len(uploaded_files) > 2:
                                    with open(uploaded_files[2], "rb") as f3:
                                        input_params["image3"] = f3
                        
                        image_output = replicate.run(model, input=input_params)
                except Exception as e:
                    # 方法2：如果上面失败，尝试只用第一张图片
                    print(f"多图片方式失败，使用单图片: {e}")
                    with open(uploaded_files[0], "rb") as f:
                        input_params = {"prompt": prompt, "image": f}
                        image_output = replicate.run(model, input=input_params)
            
            # 保存生成的图像
            filename = save_image(image_output, f"img2img_{image_count}imgs")
            image_url = url_for('static', filename=f'images/{filename}')
            
            return jsonify({
                'success': True,
                'image_url': image_url,
                'filename': filename,
                'prompt': prompt,
                'model': model,
                'input_images': image_count
            })
            
        finally:
            # 清理所有临时文件
            for temp_path in uploaded_files:
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception as e:
                    print(f"清理临时文件失败: {e}")
        
    except Exception as e:
        print(f"图生图出错: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/gallery')
def gallery():
    """图像画廊"""
    images = []
    image_dir = app.config['GENERATED_FOLDER']
    
    if os.path.exists(image_dir):
        for filename in sorted(os.listdir(image_dir), reverse=True):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                images.append({
                    'filename': filename,
                    'url': url_for('static', filename=f'images/{filename}'),
                    'created': datetime.fromtimestamp(
                        os.path.getctime(os.path.join(image_dir, filename))
                    ).strftime('%Y-%m-%d %H:%M:%S')
                })
    
    return jsonify({'images': images})

@app.route('/download/<filename>')
def download_image(filename):
    """下载图像"""
    try:
        filepath = os.path.join(app.config['GENERATED_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_image(filename):
    """删除图像"""
    try:
        filepath = os.path.join(app.config['GENERATED_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"已删除图像: {filename}")
            return jsonify({'success': True, 'message': '图像删除成功'})
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        print(f"删除图像失败: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 启动 Replicate Web 生成器...")
    print("📱 访问: http://localhost:8080")
    print("🎨 开始创作吧!")
    app.run(debug=True, host='0.0.0.0', port=8080)