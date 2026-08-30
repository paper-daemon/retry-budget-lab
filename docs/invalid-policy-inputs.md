# retry計算器は、不正設定をそれっぽい数字にしない

Retry Budget Labは、retry回数・backoff・成功率・同時数・timeoutから request amplification と worst-case時間を計算する。

計算式が正しくても、入力自体が無効なら結果を返さない方がいい。

## 修正前に受け入れていた例

- `attempts=0`
- `jitter=-0.1`
- `success_prob=1.2`
- `timeout=-1`
- `concurrency=0`

こういう値でもPythonの算術自体は動くので、見た目だけはレポートっぽい数字を作れてしまう。

## 今は先にrejectする

現在は次を検証してから計算する。

- attempts >= 1
- base delay >= 0
- factor > 0
- cap >= 0
- jitter >= 0
- 0 <= success probability <= 1
- concurrency >= 1
- timeout >= 0
- float値はfinite

## 正常系は変えない

fixture:

```text
attempts=3
base=1
factor=2
cap=30
jitter=0
success_prob=0.5
concurrency=10
timeout=5
```

結果:

- expected requests/job: `1.75x`
- success by final attempt: `0.875`
- worst-case job time: `18.0s`
- max concurrent request pressure: `30`

無効入力のrejectを含め、関連unit testは `2/2` PASS。

これは実トラフィックのベンチマークではなく、計算器のfixture結果。

Source: https://github.com/paper-daemon/retry-budget-lab
