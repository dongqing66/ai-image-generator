from flask import Flask, render_template, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import replicate
import os
import uuid
from datetime import datetime
import base64
from io import BytesIO
import json
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 使用相对路径，不要硬编码
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['GENERATED_FOLDER'] = os.path.join(BASE_DIR, 'static', 'images')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# 确保目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

# 设置 API Token - 从环境变量读取
api_token = os.environ.get('REPLICATE_API_TOKEN')
if not api_token:
    logger.error("⚠️ 未设置 REPLICATE_API_TOKEN 环境变量")
    raise RuntimeError("必须设置 REPLICATE_API_TOKEN 环境变量。请运行：export REPLICATE_API_TOKEN=your_token_here")

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        model = data.get('model', 'google/nano-banana')  # 默认使用 Google Nano Banana

        if not prompt:
            return jsonify({'error': '请输入提示词'}), 400

        if len(prompt) > 1000:
            return jsonify({'error': '提示词太长，请控制在1000字符以内'}), 400

        logger.info(f"使用模型: {model}")
        logger.info(f"提示词: {prompt[:100]}...")  # 只记录前100个字符

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

    except replicate.exceptions.ReplicateError as e:
        logger.error(f"Replicate API错误: {e}")
        return jsonify({'error': 'API服务暂时不可用，请稍后重试'}), 503
    except Exception as e:
        logger.error(f"生成图像出错: {e}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@app.route('/img2img', methods=['POST'])
def image_to_image():
    """图生图"""
    try:
        prompt = request.form.get('prompt', '').strip()
        model = request.form.get('model', 'google/nano-banana')
        image_count = int(request.form.get('imageCount', 1))

        if not prompt:
            return jsonify({'error': '请输入提示词'}), 400

        if len(prompt) > 1000:
            return jsonify({'error': '提示词太长，请控制在1000字符以内'}), 400

        if image_count > 3:
            return jsonify({'error': '最多只能上传3张图片'}), 400

        logger.info(f"图生图模型: {model}")
        logger.info(f"提示词: {prompt[:100]}...")
        logger.info(f"图片数量: {image_count}")

        # 收集所有上传的图片
        uploaded_files = []
        for i in range(image_count):
            file_key = f'image{i}'
            if file_key not in request.files:
                return jsonify({'error': f'未找到图片 {i+1}'}), 400

            file = request.files[file_key]
            if file.filename == '':
                return jsonify({'error': f'图片 {i+1} 为空'}), 400

            # 验证文件类型
            if not allowed_file(file.filename):
                return jsonify({'error': f'图片 {i+1} 格式不支持，仅支持 PNG, JPG, JPEG, WEBP'}), 400

            # 保存临时文件（使用 secure_filename）
            safe_filename = secure_filename(file.filename)
            upload_filename = f"{str(uuid.uuid4())}_{i}_{safe_filename}"
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
                    logger.warning(f"清理临时文件失败: {e}")

    except ValueError as e:
        logger.error(f"参数错误: {e}")
        return jsonify({'error': '请求参数错误'}), 400
    except replicate.exceptions.ReplicateError as e:
        logger.error(f"Replicate API错误: {e}")
        return jsonify({'error': 'API服务暂时不可用，请稍后重试'}), 503
    except Exception as e:
        logger.error(f"图生图出错: {e}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

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
        # 安全性：清理文件名，防止路径遍历攻击
        filename = secure_filename(filename)
        filepath = os.path.join(app.config['GENERATED_FOLDER'], filename)

        # 确保文件在允许的目录内
        if not os.path.abspath(filepath).startswith(os.path.abspath(app.config['GENERATED_FOLDER'])):
            logger.warning(f"尝试访问非法路径: {filename}")
            return jsonify({'error': '非法文件路径'}), 403

        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        logger.error(f"下载文件出错: {e}")
        return jsonify({'error': '下载失败'}), 500

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_image(filename):
    """删除图像"""
    try:
        # 安全性：清理文件名，防止路径遍历攻击
        filename = secure_filename(filename)
        filepath = os.path.join(app.config['GENERATED_FOLDER'], filename)

        # 确保文件在允许的目录内
        if not os.path.abspath(filepath).startswith(os.path.abspath(app.config['GENERATED_FOLDER'])):
            logger.warning(f"尝试删除非法路径: {filename}")
            return jsonify({'error': '非法文件路径'}), 403

        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"已删除图像: {filename}")
            return jsonify({'success': True, 'message': '图像删除成功'})
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        logger.error(f"删除图像失败: {e}")
        return jsonify({'error': '删除失败'}), 500

if __name__ == '__main__':
    # 生产环境使用 gunicorn，本地开发使用 Flask
    port = int(os.environ.get('PORT', 8080))
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'

    logger.info("🚀 启动 Replicate Web 生成器...")
    logger.info(f"📱 访问: http://localhost:{port}")
    logger.info("🎨 开始创作吧!")

    app.run(debug=debug_mode, host='0.0.0.0', port=port)