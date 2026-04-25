```c++
#include <bits/stdc++.h>
using namespace std;

int main() {
    int a, b;
    cin >> a >> b;

    // 方法1：临时变量法
    int c;
    c = a;
    a = b;
    b = c;

    // 方法2：加减法交换
    a = a + b;
    b = a - b;
    a = a - b;

    // 方法3：swap
    swap(a, b);


    return 0;
}
```

```c++
#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, num;
    cin >> n;          // 数字个数
    int maxVal = INT_MIN;        // 擂主

    for (int i = 1; i <= n; i++) {
        cin >> num;
        if (num > maxVal) {
            maxVal = num;   // 更新擂主
        }
    }
    cout << "最大�? " << maxVal << endl;

    return 0;
}
```

