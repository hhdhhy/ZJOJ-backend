# go-judge 官方文档总结

## 📚 文档概览

本文档总结了 go-judge 的9个官方文档页面，涵盖安装、配置、API、设计原理等核心内容。

---

## 1. 安装与部署 (install)

### Docker 快速启动
```bash
docker run -it --privileged --shm-size=256m -p 5050:5050 criyle/go-judge
```
- `--privileged`: 开启容器嵌套，用户程序在沙箱中安全运行

### 自定义镜像构建（推荐方式）
```dockerfile
FROM criyle/go-judge:latest AS go-judge
FROM debian:latest
# 安装需要的编译器
RUN apt-get update && apt-get install -y g++ gcc python3 default-jdk
WORKDIR /opt
COPY --from=go-judge /opt/go-judge /opt/mount.yaml /opt/
EXPOSE 5050/tcp 5051/tcp 5052/tcp
ENTRYPOINT ["./go-judge"]
```

**关键点**：
- 使用多阶段构建
- 基于 Debian/Alpine 安装编译器
- 从第一阶段复制 go-judge 二进制文件和 mount.yaml

---

## 2. 根文件系统 (rootfs)

### 自定义 rootfs 结构
```
.
├── mount.yaml
└── rootfs/  # 容器根文件系统
    ├── bin/
    ├── lib/
    ├── usr/
    └── ...
```

### 支持的发行版
- **Alpine**: 轻量级，适合快速部署
- **Debian**: 完整工具链，兼容性好
- **Fedora**: RedHat 系
- **Arch Linux**: 滚动更新

**关键配置**：
```yaml
mount:
  - type: bind
    source: rootfs/bin
    target: /bin
    readonly: true
  - type: tmpfs
    target: /w
    data: size=128m,nr_inodes=4k
uid: 1536  # 容器内用户 ID
gid: 1536  # 容器内组 ID
```

---

## 3. 文件系统挂载 (mount)

### 默认挂载点
- `/bin`, `/lib`, `/lib64`, `/usr` (只读)
- `/etc/ld.so.cache`, `/etc/alternatives`
- `/dev/null`, `/dev/urandom`, `/dev/random`, `/dev/zero`, `/dev/full`
- `/w` (工作目录, tmpfs)
- `/tmp` (临时目录, tmpfs)
- `/proc` (进程信息)

### 自定义 mount.yaml
```yaml
mount:
  - type: bind
    source: /bin
    target: /bin
    readonly: true
  - type: tmpfs
    target: /w
    data: size=128m,nr_inodes=4k
proc: true  # 挂载 /proc
workDir: /w
uid: 1536
gid: 1536
symLink:
  - linkPath: /dev/fd
    target: /proc/self/fd
maskPath:
  - /sys/firmware
  - /proc/kcore
```

**特殊文件**：
- `containerPasswd.txt`: 显示用户名
- `.env`: 自定义环境变量

---

## 4. 配置选项 (configuration)

### 服务相关参数
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-http-addr` | localhost:5050 | HTTP 监听地址 |
| `-enable-grpc` | false | 启用 gRPC 接口 |
| `-auth-token` | 无 | 令牌鉴权 |
| `-enable-debug` | false | 启用调试接口 |
| `-enable-metrics` | false | 启用 Prometheus 监控 |

### 沙箱相关参数
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-parallelism` | CPU 数量 | 并发任务数 |
| `-extra-memory-limit` | 16KiB | 额外内存限制 |
| `-output-limit` | 256MiB | 最大输出限制 |
| `-copy-out-limit` | 64MiB | copyOut 文件大小限制 |
| `-open-file-limit` | 256 | 最大打开文件描述符 |
| `-time-limit-checker-interval` | 100ms | 时间检查周期 |
| `-container-cred-start` | 0 | 容器用户 ID 起始值 |
| `-mount-conf` | 内置 | mount.yaml 路径 |
| `-no-fallback` | false | cgroup 失败时退出 |

**环境变量支持**：所有命令行参数可通过环境变量设置（如 `GO_JUDGE_HTTP_ADDR`）

---

## 5. API 接口 (api)

### REST API

#### POST /run - 执行程序
```typescript
interface Request {
  cmd: Cmd[];
  pipeMapping?: PipeMap[];
}

interface Cmd {
  args: string[];              // 命令行参数
  env?: string[];              // 环境变量
  files?: FileSpec[];          // stdin/stdout/stderr
  cpuLimit?: number;           // CPU 时间限制 (纳秒)
  clockLimit?: number;         // 等待时间限制 (纳秒)
  memoryLimit?: number;        // 内存限制 (字节)
  procLimit?: number;          // 线程数量限制
  copyIn?: {[dst: string]: File};   // 输入文件
  copyOut?: string[];          // 输出文件
  copyOutCached?: string[];    // 缓存文件（返回 fileId）
}

interface Result {
  status: Status;
  exitStatus: number;
  time: number;      // CPU 时间 (纳秒)
  memory: number;    // 内存使用 (字节)
  runTime: number;   // 实际运行时间 (纳秒)
  files?: {[name: string]: string};  // 输出内容
  fileIds?: {[name: string]: string}; // 缓存文件 ID
}

enum Status {
  Accepted = 'Accepted',
  MemoryLimitExceeded = 'Memory Limit Exceeded',
  TimeLimitExceeded = 'Time Limit Exceeded',
  OutputLimitExceeded = 'Output Limit Exceeded',
  FileError = 'File Error',
  NonzeroExitStatus = 'Nonzero Exit Status',
  Signalled = 'Signalled',
  InternalError = 'Internal Error',
}
```

#### 文件管理
- `GET /file` - 获取所有文件映射
- `POST /file` - 上传文件
- `GET /file/:fileId` - 下载文件
- `DELETE /file/:fileId` - 删除文件

---

## 6. 示例 (example)

### C++ 编译运行（两阶段）

#### 阶段 1: 编译
```json
{
  "cmd": [{
    "args": ["/usr/bin/g++", "a.cc", "-o", "a"],
    "env": ["PATH=/usr/bin:/bin"],
    "files": [
      {"content": ""},
      {"name": "stdout", "max": 10240},
      {"name": "stderr", "max": 10240}
    ],
    "cpuLimit": 10000000000,
    "memoryLimit": 104857600,
    "procLimit": 50,
    "copyIn": {
      "a.cc": {
        "content": "#include <iostream>\n..."
      }
    },
    "copyOut": ["stdout", "stderr"],
    "copyOutCached": ["a"]
  }]
}
```
返回：`{"fileIds": {"a": "5LWIZAA45JHX4Y4Z"}}`

#### 阶段 2: 运行
```json
{
  "cmd": [{
    "args": ["a"],
    "env": ["PATH=/usr/bin:/bin"],
    "files": [
      {"content": "1 1"},
      {"name": "stdout", "max": 10240},
      {"name": "stderr", "max": 10240}
    ],
    "cpuLimit": 10000000000,
    "memoryLimit": 104857600,
    "procLimit": 50,
    "copyIn": {
      "a": {"fileId": "5LWIZAA45JHX4Y4Z"}
    }
  }]
}
```

**重要**：每个命令在独立的容器中运行，文件系统不共享！必须使用 `copyOutCached` + `fileId` 机制传递文件。

---

## 7. 设计原理 (design)

### 系统架构
```
+------------------------------------------+
| 传输层 (HTTP / WebSocket / FFI)          |
+------------------------------------------+
| 工作协程 (环境池 + 生产者)                |
+------------------+-----------------------+
| 运行环境          | 文件存储              |
+--------+---------+----------+------------+
| Linux  | Windows | macOS    | 共享内存/磁盘 |
+--------+---------+----------+------------+
```

### 运行要求
- Linux 内核 >= 3.10
- cgroup 文件系统挂载于 `/sys/fs/cgroup`

### cgroup 权限
- **cgroup v1**: 需要 root 权限创建 cgroup
- **cgroup v2**: 通过 systemd dbus 创建临时 scope
- 无 cgroup 权限时回退到 rlimit/rusage 模式

### 状态优先级
```
Internal Error > Signalled > Dangerous Syscall > 
File Error > Non Zero Exit Status > 
Output Limit Exceeded > Time Limit Exceeded > 
Memory Limit Exceeded > Accepted
```

### 内存使用
- 控制进程: ~20MB
- 每个容器: 20MB + tmpfs (2 × 128MB)
- 每个请求: 用户程序内存限制 + 16KB + copyOut 限制

**注意**: Go runtime 不会主动归还内存，后台 GC 线程强制回收：
- `-force-gc-target`: 20MB (触发 GC 的堆内存阈值)
- `-force-gc-interval`: 5s (检查间隔)

---

## 8. 扩展 (scale)

水平扩展架构示例：
- 多个 go-judge 实例
- 负载均衡器分发请求
- 共享文件存储（可选）

---

## 🔑 核心要点总结

1. **编译和运行必须分开**：每个命令在独立容器中，使用 `copyOutCached` + `fileId` 传递文件
2. **自定义镜像**：使用多阶段构建，基于 Debian/Alpine 安装编译器
3. **cgroup 权限**：需要 root 或 privileged 模式
4. **API 请求格式**：必须包含 `env`, `files`, 资源限制
5. **文件清理**：使用 `DELETE /file/:id` 删除缓存文件避免内存泄漏
6. **错误诊断**：Internal Error 通常是容器创建失败或程序路径不存在

---

## 📖 参考链接

- 官方文档: https://docs.goj.ac/cn
- GitHub: https://github.com/criyle/go-judge
- Release: https://github.com/criyle/go-judge/releases
