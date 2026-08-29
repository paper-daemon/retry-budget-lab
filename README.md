# Retry Budget Lab

リトライ設定が**何倍のリクエスト増幅になるか・最終成功率・最悪処理時間・同時負荷**を事前に見積もる無料OSSです。

```bash
python retry_budget_lab.py --attempts 5 --base-delay 1 --factor 2 --success-prob 0.65 --concurrency 20 --timeout 10
```

- exponential backoff / cap / jitter を反映
- 1ジョブあたりの期待リクエスト数を計算
- worst-case の処理時間と同時リクエスト圧を表示
- HTML + JSON レポート
- Python 3.10+ / 外部依存なし / MIT

「とりあえず5回retry」が本番で何倍になるか、入れる前に見るための道具。

OSS: https://github.com/paper-daemon/retry-budget-lab
作者サイト: https://paper-daemon.github.io/

## BOOTH
0円配布: https://amase-memo.booth.pm/items/8778559
