# 寮€鍙戞寚鍗?
> 馃洜锔?ZJOJ 椤圭洰寮€鍙戣�鑼冨拰鏈€浣冲疄璺?
---

## 蹇�€熷紑濮?
### 鐜��瑕佹眰

- **Python**: 3.8+
- **Django**: 6.0+
- **MySQL**: 8.0+
- **Docker**: 20.10+锛堟帹鑽愶級

### 寮€鍙戠幆澧冩惌寤?
#### 鏂瑰紡涓€锛欴ocker锛堟帹鑽愶級

```bash
git clone git@github.com:hhdhhy/ZJOJ-backend.git
cd ZJOJ-backend
./deploy/setup_env.sh
docker compose up -d
```

#### 鏂瑰紡浜岋細鏈�湴寮€鍙?
```bash
# 1. 鍏嬮殕椤圭洰
git clone git@github.com:hhdhhy/ZJOJ-backend.git
cd ZJOJ-backend

# 2. 鍒涘缓铏氭嫙鐜��
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. 瀹夎�渚濊禆
pip install -r requirements.txt

# 4. 閰嶇疆鏁版嵁搴?# 缂栬緫 ZJOJ/settings.py 鎴栧垱寤?.env 鏂囦欢

# 5. 鏁版嵁杩佺Щ
python manage.py migrate

# 6. 鍒涘缓绠＄悊鍛?python manage.py createsuperuser

# 7. 鍚�姩鏈嶅姟
python manage.py runserver
```

---

## 浠ｇ爜瑙勮寖

### Python 浠ｇ爜椋庢牸

閬靛惊 PEP 8 瑙勮寖锛?
```python
# 鉁?濂界殑鍛藉悕
def get_user_profile(user_id: str) -> dict:
    """鑾峰彇鐢ㄦ埛璧勬枡"""
    pass

# 鉂?涓嶅ソ鐨勫懡鍚?def getUser(u):
    pass
```

**瑕佺偣**锛?- 浣跨敤 snake_case 鍛藉悕鍑芥暟鍜屽彉閲?- 浣跨敤 PascalCase 鍛藉悕绫?- 娣诲姞绫诲瀷娉ㄨВ
- 缂栧啓 docstring

### Django 鏈€浣冲疄璺?
#### 1. 妯″瀷璁捐�

```python
class Problem(models.Model):
    problem_id = models.CharField(primary_key=True, max_length=20)
    title = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'problem_problem'
        verbose_name = '棰樼洰'
        verbose_name_plural = '棰樼洰'
    
    def __str__(self):
        return f"{self.problem_id}: {self.title}"
```

#### 2. 瑙嗗浘璁捐�

浣跨敤 DRF 鐨?ViewSet锛?
```python
from rest_framework import viewsets, permissions

class ProblemViewSet(viewsets.ModelViewSet):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tag__name=tag)
        return queryset
```

#### 3. 搴忓垪鍖栧櫒

```python
from rest_framework import serializers

class ProblemSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='name',
        queryset=Tag.objects.all()
    )
    
    class Meta:
        model = Problem
        fields = ['problem_id', 'title', 'description', 'tags']
```

---

## 椤圭洰缁撴瀯

```
ZJOJ-backend/
鈹溾攢鈹€ apps/                  # 搴旂敤妯″潡
鈹?  鈹溾攢鈹€ ojauth/           # 鐢ㄦ埛璁よ瘉
鈹?  鈹溾攢鈹€ problem/          # 棰樼洰绠＄悊
鈹?  鈹溾攢鈹€ submission/       # 鎻愪氦璁板綍
鈹?  鈹斺攢鈹€ ai_assistant/     # AI鍔╂墜
鈹溾攢鈹€ ZJOJ/                 # 椤圭洰閰嶇疆
鈹?  鈹溾攢鈹€ settings.py       # 鍩虹�閰嶇疆
鈹?  鈹溾攢鈹€ urls.py           # URL璺�敱
鈹?  鈹斺攢鈹€ wsgi.py           # WSGI鍏ュ彛
鈹溾攢鈹€ deploy/               # 閮ㄧ讲鑴氭湰
鈹溾攢鈹€ docs/                 # 鏂囨。
鈹溾攢鈹€ manage.py             # Django绠＄悊鍛戒护
鈹斺攢鈹€ requirements.txt      # Python渚濊禆
```

---

## API 寮€鍙戣�鑼?
### RESTful 璁捐�

| 鏂规硶 | 璺�緞 | 璇存槑 |
|------|------|------|
| GET | /api/problems/ | 鑾峰彇棰樼洰鍒楄〃 |
| POST | /api/problems/ | 鍒涘缓棰樼洰 |
| GET | /api/problems/{id}/ | 鑾峰彇棰樼洰璇︽儏 |
| PUT | /api/problems/{id}/ | 鏇存柊棰樼洰 |
| DELETE | /api/problems/{id}/ | 鍒犻櫎棰樼洰 |

### 鍝嶅簲鏍煎紡

**鎴愬姛鍝嶅簲**锛?```json
{
  "count": 100,
  "next": "http://api.example.com/problems/?page=2",
  "previous": null,
  "results": [...]
}
```

**閿欒�鍝嶅簲**锛?```json
{
  "error": "楠岃瘉澶辫触",
  "details": {
    "title": ["姝ゅ瓧娈靛繀濉?]
  }
}
```

### 鏉冮檺鎺у埗

```python
from rest_framework.permissions import IsAuthenticated

class SubmissionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # 闇€瑕佺櫥褰?```

#### 瑙掕壊鏉冮檺鎺у埗

```python
from Middleware.PermissionCheck import coach_required, student_required

class ClassView(APIView):
    @coach_required  # 浠呮暀缁冨彲璁块棶
    def post(self, request):
        pass
```

璇﹁�锛歔鏉冮檺绯荤粺鏂囨。](06-MODULES/permission-system.md)

鍏�紑鎺ュ彛闇€鏄惧紡璞佸厤锛?
```python
from rest_framework.permissions import AllowAny

class LoginView(APIView):
    permission_classes = [AllowAny]  # 鏃犻渶鐧诲綍
```

---

## 娴嬭瘯

### 鍗曞厓娴嬭瘯

```python
from django.test import TestCase
from apps.problem.models import Problem

class ProblemTestCase(TestCase):
    def setUp(self):
        Problem.objects.create(
            problem_id='P1001',
            title='Test Problem',
            time_limit=1000,
            memory_limit=256
        )
    
    def test_problem_creation(self):
        problem = Problem.objects.get(problem_id='P1001')
        self.assertEqual(problem.title, 'Test Problem')
```

杩愯�娴嬭瘯锛?```bash
python manage.py test
```

---

## Git 宸ヤ綔娴?
### 鍒嗘敮绛栫暐

- `main` - 涓诲垎鏀�紙鐢熶骇鐜��锛?- `develop` - 寮€鍙戝垎鏀?- `feature/*` - 鍔熻兘鍒嗘敮
- `hotfix/*` - 绱ф€ヤ慨澶?
### 鎻愪氦瑙勮寖

```bash
# 鏍煎紡锛?type>: <subject>

# 绀轰緥
git commit -m "feat: add problem search feature"
git commit -m "fix: resolve login timeout issue"
git commit -m "docs: update API documentation"
```

**Type 绫诲瀷**锛?- `feat`: 鏂板姛鑳?- `fix`: 淇��bug
- `docs`: 鏂囨。鏇存柊
- `style`: 浠ｇ爜鏍煎紡
- `refactor`: 閲嶆瀯
- `test`: 娴嬭瘯鐩稿叧
- `chore`: 鏋勫缓/宸ュ叿閾?
---

## 璋冭瘯鎶€宸?
### Django Debug Toolbar

瀹夎�锛?```bash
pip install django-debug-toolbar
```

閰嶇疆 `settings.py`锛?```python
INSTALLED_APPS = [
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']
```

### 鏃ュ織閰嶇疆

```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

---

## 鎬ц兘浼樺寲

### 鏁版嵁搴撴煡璇�紭鍖?
```python
# 鉂?N+1 鏌ヨ�闂��
problems = Problem.objects.all()
for p in problems:
    print(p.creator.username)  # 姣忔�寰�幆閮芥煡璇㈡暟鎹�簱

# 鉁?浣跨敤 select_related
problems = Problem.objects.select_related('creator').all()
for p in problems:
    print(p.creator.username)  # 鍙�煡璇�竴娆?```

### 缂撳瓨

```python
from django.core.cache import cache

def get_problem_list():
    cache_key = 'problem_list'
    data = cache.get(cache_key)
    if not data:
        data = list(Problem.objects.all())
        cache.set(cache_key, data, 300)  # 缂撳瓨5鍒嗛挓
    return data
```

---

## 甯歌�闂��

### 1. 鏁版嵁搴撹繛鎺ュけ璐?
```bash
# 妫€鏌?MySQL 鏄�惁杩愯�
sudo systemctl status mysql

# 娴嬭瘯杩炴帴
mysql -u root -p
```

### 2. 杩佺Щ鍐茬獊

```bash
# 閲嶇疆杩佺Щ
python manage.py migrate --fake zero
python manage.py makemigrations
python manage.py migrate
```

### 3. 闈欐€佹枃浠?404

```bash
python manage.py collectstatic
```

---

## 鐩稿叧鏂囨。

- [API 鍙傝€僝(04-API_REFERENCE.md)
- [鏁版嵁搴撹�璁�(07-DATABASE.md)
- [閮ㄧ讲鎸囧崡](03-DEPLOYMENT.md)
