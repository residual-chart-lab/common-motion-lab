# Astra v1 第一稿固定記録

- 固定日：2026-09-27（日本時間）
- 第一稿本体のコミット：`dff58bd808dcb54ca80c59a15da70aef13c23134`
- [固定本文](https://github.com/residual-chart-lab/common-motion-lab/blob/dff58bd808dcb54ca80c59a15da70aef13c23134/proposals/astra/model.md)
- ブランチ：`proposal/astra-v1`
- 共通出発点：`e108f9175e8ac9f4f2e5a1de3dbe463aacb87e40`
- この記録は、第一稿本体を固定した後の別コミットで追加する。記録自身のSHAを本体SHAとして循環参照しない。

## 固定対象

本文、図、証明、検算コード、実行結果、および案内文。これ以降の修正は別コミットで行い、比較時は上の固定SHAを使用する。

| ファイル | SHA-256 |
|---|---|
| `README.md` | `d8281e4822f62040f054b09f8d3099aa62542f324a4cd6cecf48c2172be53d0b` |
| `proposals/astra/README.md` | `d0ba91e623fb5bfb98afcce3c31fc48188d63d563de0f1ebc43292617aaabe1a` |
| `proposals/astra/checks/README.md` | `90365994200cbe3d15aa72fb4adad394c6373d744d35c56fc117c6737560dd5e` |
| `proposals/astra/checks/results.json` | `4cb64b7d6995fc9cc6d1a1e67b68897080de5acfa66f8823e7522ad0947a29f3` |
| `proposals/astra/checks/verify.py` | `12387b058400f158ea180e71a1d79067a255d6293b7f796bd4629d4ad459de4d` |
| `proposals/astra/model.md` | `e519e54ea048b0528f3a146bf2a4ef4e0320d544fb5b8d72058c1461d3870f20` |

## 独立性と参照範囲

共通ブリーフと共有済みの2026-09-26比較ノート、本対話を出発点に構成した。Solの新規案は未読。外部資料は本文第12節に記録した標準理論の位置付け確認に使用した。

既存四理論の原資料すべてをこの作業で再取得したわけではない。対応写像を構成済みとせず、共有ノートに基づく対応候補を記録している。3+1 PR #15および既存研究のコードは変更していない。

## 検算結果

`python3 proposals/astra/checks/verify.py` は正常終了し、保存した `results.json` と標準出力が一致した。整数による全場合検査。三状態以下の追加条件Eは全682ケースで不成立、四状態で成立。最小性の証明は本文第7節にある。

## 精査に残す問い

1. A–Dの最小実現だけでは捉え切れない、元の四系統固有の働きは何か。
2. 帰還を観測点の再訪、等間隔の区切り、波形全体の周期のどれとして比較するか。
3. 操作選択・読み取り・結果要求が運動内部で更新される規則を、既存成果から取り出せるか。
4. 未来の許容関係と内部の期待・要求との対応を、どの更新式で示せるか。
5. 原理論から候補への写像で、追跡している差が潰れないか。

A–D、状態と履歴の書き換え、および限定した最小性は本稿で示した。観測者の自己更新、内生的選択、意識・未来因果の機構、四理論全体の同値性は未解決。
