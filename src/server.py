from flask import Flask, request, jsonify
import pyautogui
import threading
import json
import os
import uuid

app = Flask(__name__)
pyautogui.PAUSE = 0.1
CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default = {
            "brand": {
                "name": "AI快捷面板",
                "subtitle": "高效触发工作流 · 提升工作效率",
                "logo_img": "",
                "banner_img": ""
            },
            "sections": [
                {"id": "dev", "name": "研发区", "sort": 1},
                {"id": "ops", "name": "运营区", "sort": 2}
            ],
            "buttons": [
                {"id": "btn1", "icon": "", "text": "保存代码", "shortcut": "ctrl+s", "hint": "Ctrl+S", "sections": ["dev"]},
                {"id": "btn2", "icon": "", "text": "截图", "shortcut": "win+shift+s", "hint": "Win+Shift+S", "sections": ["dev", "ops"]}
            ]
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

@app.after_request
def cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp

@app.route('/api/config', methods=['GET'])
def api_config():
    cfg = load_config()
    cfg['sections'].sort(key=lambda x: x['sort'])
    return jsonify({"code":200,"data":cfg})

@app.route('/api/config/brand', methods=['PUT'])
def api_brand():
    cfg = load_config()
    data = request.get_json()
    # 确保图片Base64正确存储
    cfg['brand']['name'] = data.get('name', cfg['brand']['name'])
    cfg['brand']['subtitle'] = data.get('subtitle', cfg['brand']['subtitle'])
    cfg['brand']['logo_img'] = data.get('logo_img', cfg['brand']['logo_img'])
    cfg['brand']['banner_img'] = data.get('banner_img', cfg['brand']['banner_img'])
    save_config(cfg)
    return jsonify({"code":200,"msg":"保存成功"})

@app.route('/api/config/sections', methods=['GET'])
def api_sections():
    cfg = load_config()
    cfg['sections'].sort(key=lambda x:x['sort'])
    return jsonify({"code":200,"data":cfg['sections']})

@app.route('/api/config/sections', methods=['POST'])
def add_section():
    cfg = load_config()
    name = request.get_json().get('name')
    if not name:
        return jsonify({"code":400,"msg":"名称不能为空"})
    mid = str(uuid.uuid4())[:8]
    max_sort = max([s['sort'] for s in cfg['sections']], default=0)
    cfg['sections'].append({"id": mid, "name": name, "sort": max_sort+1})
    save_config(cfg)
    return jsonify({"code":200,"msg":"添加成功"})

@app.route('/api/config/sections/<sid>', methods=['PUT'])
def edit_section(sid):
    cfg = load_config()
    name = request.get_json().get('name')
    for s in cfg['sections']:
        if s['id'] == sid:
            s['name'] = name
            break
    save_config(cfg)
    return jsonify({"code":200,"msg":"修改成功"})

@app.route('/api/config/sections/<sid>', methods=['DELETE'])
def del_section(sid):
    cfg = load_config()
    cfg['sections'] = [s for s in cfg['sections'] if s['id'] != sid]
    for b in cfg['buttons']:
        if sid in b['sections']:
            b['sections'].remove(sid)
    cfg['sections'].sort(key=lambda x:x['sort'])
    for i, s in enumerate(cfg['sections']):
        s['sort'] = i+1
    save_config(cfg)
    return jsonify({"code":200,"msg":"删除成功"})

@app.route('/api/config/sections/sort', methods=['PUT'])
def sort_sections():
    cfg = load_config()
    arr = request.get_json()
    for item in arr:
        for s in cfg['sections']:
            if s['id'] == item.get('id'):
                s['sort'] = item.get('sort', 99)
    cfg['sections'].sort(key=lambda x:x['sort'])
    save_config(cfg)
    return jsonify({"code":200,"msg":"排序已保存"})

@app.route('/api/config/buttons', methods=['PUT'])
def save_buttons():
    cfg = load_config()
    cfg['buttons'] = request.get_json()
    save_config(cfg)
    return jsonify({"code":200,"msg":"按钮已保存"})

@app.route('/trigger', methods=['POST'])
def trigger():
    sc = request.get_json().get('shortcut', '').strip().lower()
    try:
        pyautogui.hotkey(*sc.split('+'))
        return jsonify({"code":200,"msg":f"已执行 {sc}"})
    except:
        return jsonify({"code":500,"msg":"执行失败"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)