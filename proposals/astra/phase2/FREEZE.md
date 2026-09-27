# Astra Phase 2 独立第二稿・固定記録

- 固定日：2026-09-27（日本時間）
- 本体の固定コミット：`47e99f0eef1e8d612e9b422b23f0855357037805`
- [固定本文](https://github.com/residual-chart-lab/common-motion-lab/blob/47e99f0eef1e8d612e9b422b23f0855357037805/proposals/astra/phase2/model.md)
- ブランチ：`proposal/astra-phase2`
- 共通ブリーフ：`318962b59fc4cf97aec5931fc8a6ce531a3f78bc`
- この固定記録は、本体を固定した後の別コミットで追加する。

## 固定内容

| ファイル | SHA-256 |
|---|---|
| `README.md` | `1467a59eaf7e4fe9c0aee852dd8bffb2312ccfe8bfd01c458b362e1eabba71e6` |
| `proposals/astra/README.md` | `9834cf250afdd4a2e6eda042d26b1c14f13fc873114c58e3406b5407f54748f7` |
| `proposals/astra/phase2/README.md` | `8fdc998bc96a77bdaa8adb21f1c09cf1700d1768d0fc7b7b622c49df4f868579` |
| `proposals/astra/phase2/checks/README.md` | `2d032e1b26dcfd8dedd663cd3a87c76d1fd38962d42eb0ea9e6ff03703f34178` |
| `proposals/astra/phase2/checks/results.json` | `f845fdcab591e1832a1b169e8ce45276a931ab1d39a90413ec16422097367bb9` |
| `proposals/astra/phase2/checks/verify.py` | `f7e43107d1cf54398a0c21276d76e83d44385eb6c33f8657c286d2fe4fa32f41` |
| `proposals/astra/phase2/model.md` | `3bdbe354fed38a7fe72a4d6e4795f86c0c4508622920ed820562e20cafeb5ba8` |

## 独立性

共通Phase 2ブリーフと第一稿比較までを共有した上で構成した。SolのPhase 2新規案は読んでいない。この稿の固定後の比較・改訂は差分として残す。

旧Astra第一稿、Sol第一稿、共通ブリーフ、比較稿および3+1 PR #15は変更していない。

## 確認したこと

- 固定自律則の六状態模型でE–Hが成立する。
- C0の位置差を同じ状態対として追い、参照だけの差へ移した後、運動と参照更新へ戻せる。
- 履歴の偶奇を現在の一ビットに保持し、次の選択へ使う。
- この模型はR1。表示三個と過去の実行操作二個、または表示四個で全状態を復元できる。
- 有限自律系の同じ則による後続識別には一様な上限がある。任意probeを許すR2とは区別する。
- 全六状態、異なる全30状態対、全過去窓、結合の削減を整数で検査した。保存結果と再実行結果は一致した。

## 未解決・限定

六状態の最小性は、位置三状態と参照二状態を独立直積因子とするクラスのみ。全般の最小性は未証明。

結果拘束の内部表現・期待・未来因果の作用機構、元の四理論からの対応写像、意味付け・意識の成立条件は未構成。外部停止／再開を追加したR2例を、自律六状態系の性質と混同しない。

比較では、参照更新を作る内部の検知と、それを選択へ返す結合が原理論のどこに対応するかを優先する。
