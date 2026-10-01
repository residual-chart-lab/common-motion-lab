# RCE v0.1 prototype

Rooted Continuity Engine の最小実行模型。

仕様: [../../proposals/rce-v0.1/SPEC.md](../../proposals/rce-v0.1/SPEC.md)

## 実行

```bash
cd prototypes/rce-v0.1
python verify.py
```

標準ライブラリのみを使う。

## v0.1 が試していること

- 同一 phase 内の細変化を圧縮する
- rooted landscape の相転移だけをイベント化する
- 相転移 residual を reference へ輸送する
- timestamp を見ずに reconstruction potential から直前イベントを推定する
- forward / reverse potential の非対称性から局所 orientation を得る
- model handoff 後も root lineage を保つ
- fork で child root と parent lineage を作る
- timestamp と主人公視点の変化量から experience resolution を計算する

## toy model

v0.1 では

[
r_{t+1}=lambda r_t+k_{t+1}
]

とし、(lambda=0.85)。

候補 predecessor (i) に対する target (t) の再構成ポテンシャルは

[
V_t(i)
=
rac12
left|
r_t-(lambda r_i+k_t)
ight|^2
]

とする。

連続候補空間の (-
abla V) の代わりに、離散イベント上で (V) の小さい方向を residual-gradient の最小実装として使う。

検証例では phase 列 A→B→C→D の各 target に対し、timestamp を使わず直前イベントを一意に再構成する。隣接 pair では forward potential が 0、reverse potential が正となる。

## 重要な境界

これは次を主張しない。

- 意識を実装した
- full memory を実装した
- 物理的時間不可逆性を証明した
- unordered な状態集合から時間方向が自発生成した
- Time Engine の未来因果を実装した

v0.1 の residual scar は実際の forward transition 時に記録される。したがって本模型の past reconstruction は「保存された非対称 scar から順序を復元できる」ことの工学的実例であり、時間方向の存在論的生成の証明ではない。

## 次の一手

1. phase 判定を LLM prompt adapter に置き換える。
2. residual を単純ベクトル差から Free Number / DGG の非置換可能差へ置き換える。
3. unordered candidate graph 上で局所 potential descent が大域的な orientation を作る条件を試す。
4. model-to-model handoff と multi-agent rooted swarm を実データで検査する。
