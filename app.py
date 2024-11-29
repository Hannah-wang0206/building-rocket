from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import os
import tempfile
import replicate
import numpy as np
import matplotlib.pyplot as plt
import logging

# 配置日志记录
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# 指定模板目录和静态目录
template_dir = '/Users/rita/Desktop/ROCKET'
static_dir = '/Users/rita/Desktop/ROCKET/assets'

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
CORS(app)

# 设置secret key for session management
app.secret_key = 'your_secret_key_here'

# 初始化 Replicate 客户端
replicate_client = replicate.Client(api_token="r8_Mexxxxxx12345678")

# Constants for distances (in meters)
celestial_bodies = {
    "Moon": {"distance": 384400000},  # Distance from Earth (in meters)
    "Venus": {"distance": 108200000000},  # Distance from the Sun (in meters)
    "Mars": {"distance": 227940000000},  # Distance from the Sun (in meters)
    "Earth": {"distance": 149600000000},  # Distance from the Sun (in meters)
}

# Function to calculate and plot the orbit
def plot_orbit(target="Moon", angle=45, velocity=8000, fuel=500, output_dir="static/plots"):
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Get target data
        target_data = celestial_bodies[target]
        r_target = target_data["distance"]

        r_low_orbit = 7000000 * 1000  # Low Earth orbit radius in meters
        r_earth = celestial_bodies["Earth"]["distance"]  # Distance of Earth from the Sun
        a_transfer = (r_earth + r_target) / 2
        angle_rad = np.radians(angle)
        velocity_orbit = velocity * np.cos(angle_rad)
        a_transfer = a_transfer * (velocity_orbit / velocity) * (1 + fuel / 1000)
        e_transfer = 1 - (r_earth / a_transfer)

        # Create figure and axis for plotting
        fig, ax = plt.subplots(figsize=(8, 8))
        max_distance = max(celestial_bodies['Venus']['distance'], celestial_bodies['Mars']['distance'],
                           celestial_bodies['Earth']['distance'])
        ax.set_xlim(-max_distance * 1.5, max_distance * 1.5)
        ax.set_ylim(-max_distance * 1.5, max_distance * 1.5)

        # Plotting logic remains unchanged
        ax.plot(0, 0, "bo", label="Earth")
        ax.plot(r_low_orbit * np.cos(np.linspace(0, 2 * np.pi, 100)),
                r_low_orbit * np.sin(np.linspace(0, 2 * np.pi, 100)), 'k--', label="Low Earth Orbit")

        theta = np.linspace(0, 2 * np.pi, 100)
        x_transfer = a_transfer * np.cos(theta)
        y_transfer = a_transfer * np.sin(theta)
        ax.plot(x_transfer, y_transfer, 'r--', label="Transfer Orbit")

        if target == 'Moon':
            ax.plot(r_target, 0, "go", label="Moon")
            ax.plot(r_target * np.cos(np.linspace(0, 2 * np.pi, 100)),
                    r_target * np.sin(np.linspace(0, 2 * np.pi, 100)), 'g--', label="Moon Orbit")

        elif target == 'Venus' or target == 'Mars':
            sun_x = r_earth + 50000000000
            theta_planet = np.linspace(0, 2 * np.pi, 100)
            x_planet = r_target * np.cos(theta_planet) + sun_x
            y_planet = r_target * np.sin(theta_planet)
            ax.plot(x_planet, y_planet, 'm--', label=f"{target} Orbit")
            ax.plot(r_target + sun_x, 0, "yo", label=target)

        ax.set_aspect("equal", "box")
        ax.set_xlabel("X Position (m)")
        ax.set_ylabel("Y Position (m)")
        ax.set_title(f"Orbital Path to {target}")
        ax.legend()

        # Save the plot as a static image
        output_path = os.path.join(output_dir, f"{target}_orbit.png")
        plt.savefig(output_path)
        plt.close(fig)

        return output_path
    except Exception as e:
        logging.error(f"Error generating orbit: {str(e)}")
        return None

# 星球的参数限制（发射角度、发射速度和燃料量）
planet_parameters = {
    'Moon': {
        'launch_angle': {'min': 0, 'max': 90},
        'launch_speed': {'min': 5000, 'max': 12000},
        'fuel_amount': {'min': 200, 'max': 900}
    },
    'Venus': {
        'launch_angle': {'min': 0, 'max': 90},
        'launch_speed': {'min': 10000, 'max': 30000},
        'fuel_amount': {'min': 300, 'max': 1000}
    },
    'Mars': {
        'launch_angle': {'min': 0, 'max': 90},
        'launch_speed': {'min': 10000, 'max': 30000},
        'fuel_amount': {'min': 300, 'max': 1000}
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/page2', methods=['GET', 'POST'])
def page2():
    if request.method == 'POST':
        # 获取上传的图像文件和用户提供的描述文本
        uploaded_image = request.files.get('image')
        prompt = request.form.get('prompt')

        if not uploaded_image:
            return jsonify({'success': False, 'message': 'No image uploaded'}), 400
        if not prompt:
            return jsonify({'success': False, 'message': 'No prompt provided'}), 400

        try:
            # 保存上传的图像到临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            uploaded_image.save(temp_file)
            temp_file_path = temp_file.name

            # 使用 Replicate API 生成图像
            with open(temp_file_path, "rb") as image_file:
                input_data = {
                    "image": image_file,
                    "prompt": prompt
                }
                output = replicate_client.run(
                    "jagilley/controlnet-scribble:435061a1b5a4c1e26740464bf786efdfa9cb3a3ac488595a2de23e143fdb0117",
                    input=input_data,
                )

            # 假设 Replicate 返回的是图像的 URL
            generated_image_url = output[0]  # 获取生成的图像 URL

            # 存储生成的图像 URL 到 session 中
            session['generated_image_url'] = generated_image_url

            # 重定向到 page4
            return redirect(url_for('page4'))

        except Exception as e:
            logging.error(f"Error processing image upload: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500

    return render_template('page2.html')

@app.route('/page3')
def page3():
    return render_template('page3.html')

@app.route('/page4')
def page4():
    # 从 session 中获取生成的图像 URL
    generated_image_url = session.get('generated_image_url', '')
    return render_template('page4.html', generated_image_url=generated_image_url)

@app.route('/page5')
def page5():
    return render_template('page5.html')

@app.route('/page6')
def page6():
    planet = request.args.get('planet')
    launch_angle = float(request.args.get('launch_angle', 0))
    launch_speed = float(request.args.get('launch_speed', 0))
    fuel_amount = float(request.args.get('fuel_amount', 0))
    launch_date = request.args.get('launch_date')
    project_name = request.args.get('project_name')

    # 获取星球对应的限制参数
    if planet and launch_angle and launch_speed and fuel_amount:
        planet_params = planet_parameters.get(planet)
        
        if planet_params:
            # 判断每个参数是否在合法范围内
            valid_angle = planet_params['launch_angle']['min'] <= launch_angle <= planet_params['launch_angle']['max']
            valid_speed = planet_params['launch_speed']['min'] <= launch_speed <= planet_params['launch_speed']['max']
            valid_fuel = planet_params['fuel_amount']['min'] <= fuel_amount <= planet_params['fuel_amount']['max']
            
            # 判断所有条件是否都满足
            if valid_angle and valid_speed and valid_fuel:
                launch_params_are_valid = True
            else:
                launch_params_are_valid = False
        else:
            launch_params_are_valid = False
    else:
        launch_params_are_valid = False
    
    # 返回 page6.html 页面，并传递星球和参数有效性
    return render_template('page6.html', 
                           planet=planet, 
                           launch_angle=launch_angle, 
                           launch_speed=launch_speed,
                           fuel_amount=fuel_amount,
                           launch_date=launch_date,
                           project_name=project_name,
                           launch_params_are_valid=launch_params_are_valid)

@app.route('/page7')
def page7():
    launch_date = request.args.get('launch_date')
    return render_template('page7.html', launch_date=launch_date)

@app.route('/page8')
def page8():
    return render_template('page8.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    # 获取上传的图像文件和用户提供的描述文本
    uploaded_image = request.files.get('image')
    prompt = request.form.get('prompt')

    if not uploaded_image:
        return jsonify({'success': False, 'message': 'No image uploaded'}), 400
    if not prompt:
        return jsonify({'success': False, 'message': 'No prompt provided'}), 400

    try:
        # 保存上传的图像到临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        uploaded_image.save(temp_file)
        temp_file_path = temp_file.name

        # 使用 Replicate API 生成图像
        with open(temp_file_path, "rb") as image_file:
            input_data = {
                "image": image_file,
                "prompt": prompt
            }
            output = replicate_client.run(
                "jagilley/controlnet-scribble:435061a1b5a4c1e26740464bf786efdfa9cb3a3ac488595a2de23e143fdb0117",
                input=input_data,
            )

        # 假设 Replicate 返回的是图像的 URL
        generated_image_url = output[0]  # 获取生成的图像 URL

        # 返回生成的图像 URL 给前端
        return jsonify({'success': True, 'image_url': generated_image_url})

    except Exception as e:
        logging.error(f"Error uploading image: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/generate_orbit', methods=['POST'])
def generate_orbit():
    try:
        data = request.json
        target = data.get('target')
        angle = data.get('angle', 45)
        velocity = data.get('velocity', 8000)
        fuel = data.get('fuel', 500)

        if not target:
            return jsonify({'success': False, 'message': 'Target not specified'}), 400

        plot_path = plot_orbit(target=target, angle=angle, velocity=velocity, fuel=fuel)
        if plot_path:
            return jsonify({'success': True, 'plot_url': url_for('static', filename=os.path.relpath(plot_path, 'static'))})
        else:
            return jsonify({'success': False, 'message': 'Failed to generate orbit plot'}), 500
    except Exception as e:
        logging.error(f"Error in generate_orbit: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)


