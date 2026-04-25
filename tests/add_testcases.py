"""
为题目 A001 创建测试用例
"""
import zipfile
import os
import requests

BASE_URL = "http://101.35.233.33:8000"

def login(username, password):
    """登录获取 Token"""
    response = requests.post(f"{BASE_URL}/api/login/", json={
        'username': username,
        'password': password
    })
    
    if response.status_code == 200:
        data = response.json()
        return data['token']
    else:
        print(f"❌ 登录失败: {response.status_code}")
        print(response.json())
        return None


def create_testcases_zip():
    """创建测试用例 ZIP 文件"""
    print("📦 创建测试用例 ZIP 文件...")
    
    # 创建临时目录
    temp_dir = 'temp_testcases'
    testdata_dir = os.path.join(temp_dir, 'testdata')
    os.makedirs(testdata_dir, exist_ok=True)
    
    # 创建测试用例
    test_cases = [
        (1, "1 2\n", "3\n"),
        (2, "10 20\n", "30\n"),
        (3, "0 0\n", "0\n"),
        (4, "100 200\n", "300\n"),
        (5, "999 1\n", "1000\n"),
    ]
    
    for case_id, input_data, output_data in test_cases:
        # 写入输入文件
        with open(os.path.join(testdata_dir, f"{case_id}.in"), 'w', encoding='utf-8') as f:
            f.write(input_data)
        
        # 写入输出文件
        with open(os.path.join(testdata_dir, f"{case_id}.out"), 'w', encoding='utf-8') as f:
            f.write(output_data)
        
        print(f"   ✓ 测试点 #{case_id}: {input_data.strip()} -> {output_data.strip()}")
    
    # 压缩成 ZIP
    zip_path = 'testcases_A001.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ ZIP 文件创建成功: {zip_path}")
    
    # 清理临时目录
    import shutil
    shutil.rmtree(temp_dir)
    
    return zip_path


def upload_testcases(token, problem_id, zip_path):
    """上传测试用例"""
    headers = {'Authorization': f'jwt {token}'}
    
    print(f"\n📤 上传测试用例到题目 {problem_id}...")
    
    with open(zip_path, 'rb') as f:
        files = {'file': (zip_path, f, 'application/zip')}
        response = requests.post(
            f"{BASE_URL}/api/problems/{problem_id}/testcases/upload/",
            headers=headers,
            files=files
        )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 上传成功!")
        print(f"   测试用例数量: {data.get('data', {}).get('test_cases_count', 'N/A')}")
        return True
    else:
        print(f"❌ 上传失败: {response.status_code}")
        print(response.json())
        return False


def verify_testcases(token, problem_id):
    """验证测试用例是否上传成功"""
    headers = {'Authorization': f'jwt {token}'}
    
    print(f"\n🔍 验证测试用例...")
    response = requests.get(
        f"{BASE_URL}/api/problems/{problem_id}/testcases/",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        # 兼容两种响应格式
        if 'data' in data:
            # 自定义格式: {code, message, data}
            test_data = data['data']
            count = test_data.get('test_case_count', 0)
            print(f"✅ 共有 {count} 个测试用例")
            
            if test_data.get('test_cases'):
                for tc in test_data['test_cases']:
                    print(f"   - 测试点 #{tc['id']}: {tc['input']} / {tc['output']}")
            
            return count > 0
        else:
            # 分页格式: {count, results}
            count = data.get('count', 0)
            print(f"✅ 共有 {count} 个测试用例")
            
            if data.get('results'):
                for tc in data['results']:
                    print(f"   - 测试点 #{tc['id']}: {tc['input_file']} / {tc['output_file']}")
            
            return count > 0
    else:
        print(f"❌ 获取失败: {response.status_code}")
        print(response.json())
        return False


def main():
    print("=" * 60)
    print("📝 为题目 A001 添加测试用例")
    print("=" * 60)
    
    # 1. 登录
    print("\n[步骤 1] 登录...")
    token = login('admin', 'Admin@123456')
    if not token:
        return
    
    print(f"✅ 登录成功")
    
    # 2. 创建测试用例 ZIP
    print("\n[步骤 2] 创建测试用例...")
    zip_path = create_testcases_zip()
    
    # 3. 上传测试用例
    print("\n[步骤 3] 上传测试用例...")
    success = upload_testcases(token, 'A001', zip_path)
    
    if success:
        # 4. 验证
        print("\n[步骤 4] 验证上传结果...")
        verify_testcases(token, 'A001')
        
        print("\n" + "=" * 60)
        print("✅ 测试用例添加完成！现在可以提交代码进行测试了")
        print("=" * 60)
    else:
        print("\n❌ 上传失败")
    
    # 清理 ZIP 文件
    if os.path.exists(zip_path):
        os.remove(zip_path)
        print(f"\n🗑️  已清理临时文件: {zip_path}")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ 出错: {str(e)}")
        import traceback
        traceback.print_exc()
