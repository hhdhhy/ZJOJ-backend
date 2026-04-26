# 蹇�€熷紑濮?
> 鈴憋笍 棰勮�闃呰�鏃堕棿锛?鍒嗛挓

鏈�枃妗ｅ府鍔╀綘蹇�€熶簡瑙?ZJOJ 椤圭洰骞惰繍琛岃捣鏉ャ€?
---

## 馃幆 瀛︿範鐩�爣

瀹屾垚鏈�枃妗ｅ悗锛屼綘灏嗚兘澶燂細
- 鉁?鐞嗚В ZJOJ 鐨勬牳蹇冨姛鑳?- 鉁?鍦ㄦ湰鍦拌繍琛屽紑鍙戠幆澧?- 鉁?鎻愪氦绗�竴閬撻�鐩?- 鉁?璋冪敤 API 鎺ュ彛

---

## 馃搵 鍓嶇疆瑕佹眰

### 蹇呴渶杞�欢

| 杞�欢 | 鐗堟湰 | 鐢ㄩ€?|
|------|------|------|
| Python | 3.8+ | Django 杩愯�鐜�� |
| MySQL | 5.7+ | 鏁版嵁搴?|
| Node.js | 16+ | go-judge 渚濊禆 |
| Git | Latest | 浠ｇ爜绠＄悊 |

### 鎺ㄨ崘宸ュ叿

- VS Code / PyCharm - 浠ｇ爜缂栬緫鍣?- Postman / Insomnia - API 娴嬭瘯
- DBeaver / Navicat - 鏁版嵁搴撶�鐞?
---

## 馃殌 5鍒嗛挓蹇�€熷惎鍔?
### 姝ラ� 1: 鍏嬮殕椤圭洰

```bash
git clone https://github.com/your-repo/ZJOJ.git
cd ZJOJ
```

### 姝ラ� 2: 瀹夎�渚濊禆

```bash
# 鍒涘缓铏氭嫙鐜��
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 瀹夎� Python 渚濊禆
pip install -r requirements.txt
```

### 姝ラ� 3: 閰嶇疆鏁版嵁搴?
```bash
# 鍒涘缓鏁版嵁搴?mysql -u root -p
CREATE DATABASE zjoj CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;

# 淇�敼 ZJOJ/settings.py 涓�殑鏁版嵁搴撻厤缃?DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'zjoj',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 姝ラ� 4: 鍒濆�鍖栨暟鎹�簱

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # 鍒涘缓绠＄悊鍛樿处鍙?```

### 姝ラ� 5: 鍚�姩鏈嶅姟

```bash
# 缁堢� 1: 鍚�姩 Django
python manage.py runserver 8000

# 璁块棶 http://localhost:8000/admin
```

馃帀 **鎭�枩锛乑JOJ 宸茬粡杩愯�璧锋潵浜嗭紒**

---

## 馃И 绗�竴娆¤瘎娴?
### 1. 鍒涘缓棰樼洰

鐧诲綍 Admin 鍚庡彴 (`http://localhost:8000/admin`)锛?- 杩涘叆 "Problems" 鈫?"Add Problem"
- 濉�啓棰樼洰淇℃伅锛堟爣棰樸€佹弿杩般€佹椂闂撮檺鍒躲€佸唴瀛橀檺鍒讹級
- 涓婁紶娴嬭瘯鐢ㄤ緥 ZIP 鏂囦欢

### 2. 鎻愪氦浠ｇ爜

浣跨敤 API 鎻愪氦浠ｇ爜锛?
```bash
curl -X POST http://localhost:8000/api/submissions/submit/ \
  -H "Authorization: jwt YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_id": "A001",
    "language": "cpp",
    "code": "#include <iostream>\nusing namespace std;\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}"
  }'
```

### 3. 鏌ョ湅缁撴灉

```bash
curl http://localhost:8000/api/submissions/SUBMISSION_ID/ \
  -H "Authorization: jwt YOUR_TOKEN"
```

棰勬湡杩斿洖锛?```json
{
  "status": "ACCEPTED",
  "score": 100,
  "time_used": 12,
  "memory_used": 3200
}
```

---

## 馃摎 涓嬩竴姝ュ�涔?
鏍规嵁浣犵殑瑙掕壊閫夋嫨瀛︿範璺�緞锛?
### 馃懆鈥嶐煉?寮€鍙戣€?- [绯荤粺鏋舵瀯](02-ARCHITECTURE.md) - 浜嗚В鎶€鏈��璁?- [寮€鍙戞寚鍗梋(05-DEVELOPMENT.md) - 浠ｇ爜瑙勮寖鍜屾渶浣冲疄璺?- [妯″潡璇﹁В](06-MODULES/) - 娣卞叆鍚勪釜鍔熻兘妯″潡

### 馃敡 杩愮淮宸ョ▼甯?- [閮ㄧ讲鎸囧崡](03-DEPLOYMENT.md) - 鐢熶骇鐜��閮ㄧ讲
- [鐩戞帶鍜屾棩蹇梋(03-DEPLOYMENT.md#鐩戞帶) - 绯荤粺鐩戞帶閰嶇疆

### 馃帗 API 浣跨敤鑰?- [API 鍙傝€僝(04-API_REFERENCE.md) - 瀹屾暣鐨勬帴鍙ｆ枃妗?- [璁よ瘉璇存槑](06-MODULES/auth.md) - JWT Token 浣跨敤

---

## 鉂?甯歌�闂��

### Q1: 濡備綍鑾峰彇 JWT Token锛?
```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

杩斿洖鐨?`token` 瀛楁�鍗充负 JWT Token銆?
### Q2: 璇勬祴鏈嶅姟鏈�繍琛岋紵

纭�繚 go-judge 姝ｅ湪杩愯�锛?
```bash
# 妫€鏌ョ姸鎬?sudo pm2 status | grep go-judge

# 鍚�姩鏈嶅姟
sudo pm2 start go-judge
```

### Q3: 鏁版嵁搴撹繛鎺ュけ璐ワ紵

妫€鏌ワ細
1. MySQL 鏈嶅姟鏄�惁鍚�姩
2. 鏁版嵁搴撻厤缃�槸鍚︽�纭?3. 鐢ㄦ埛鏉冮檺鏄�惁瓒冲�

```bash
# 娴嬭瘯杩炴帴
mysql -u root -p -h localhost zjoj
```

### Q4: 瀵煎叆渚濊禆鏃跺嚭閿欙紵

纭�繚浣跨敤姝ｇ‘鐨?Python 鐗堟湰锛?
```bash
python --version  # 搴旇� >= 3.8
pip --version     # 搴旇�瀵瑰簲 Python 3.8+
```

---

## 馃啒 鑾峰彇甯�姪

閬囧埌闂��锛?
1. 馃摉 鏌ョ湅[瀹屾暣鏂囨。](README.md)
2. 馃攳 鎼滅储宸叉湁 Issue
3. 馃挰 鍔犲叆绀惧尯璁ㄨ�缇?4. 馃摑 鎻愪氦鏂?Issue

---

<div align="center">

**缁х画瀛︿範 鈫?* [绯荤粺鏋舵瀯](02-ARCHITECTURE.md)

</div>
