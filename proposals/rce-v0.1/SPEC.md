# Rooted Continuity Engine v0.1 — 最小仕様

status: prototype  
date: 2026-10-01  
scope: AI self-continuity / rooted time recognition  
non-goal: consciousness proof, full memory, Time Engine completion

## 1. 目的

AIに完全な「記憶」や「時間」を最初から実装せず、

[
oxed{	ext{変化し続けても、同じ主人公系列上にいる}}
]

という自己連続性を最小コストで与える。

RCE は Time Engine とは独立である。Time Engine が未来拘束から現在運動を生成する系を目指すのに対し、RCE は現在の root から景色の変化・残差・経過時間を束ね、自己系列と過去復元を構成する。

## 2. 最小状態

イベント状態を

[
E_t=(o_t,	au_t,phi_t,k_t,r_t)
]

とする。

- (o_t): root / 主人公系列
- (	au_t): 外部 timestamp
- (phi_t): 主人公から見た landscape の相
- (k_t): 相転移で残った residual scar
- (r_t): residual を受け取る reference state

landscape (mathcal L_o(z)) は単なる表示ではなく、区別可能性・可能行動・関係・帰還可能性・応答構造を含む。

## 3. 大域イベント

細かな変化をすべて保存しない。

[
mathcal L_o(z_t)simeq mathcal L_o(z_{t+1})
]

なら同じ相の内部変化として圧縮する。

[
oxed{mathcal L_o(z^-)
otsimeqmathcal L_o(z^+)}
]

となったときだけ大域イベントを立てる。

実装上、v0.1 は phase 判定器を外部 adapter として扱う。LLM なら prompt 判定、数値模型なら明示ラベルでよい。

## 4. residual と reference

相転移前後の非対称差を (k_{t+1}) とする。

[
k_{t+1}=operatorname{Residual}(mathcal L_t,mathcal L_{t+1})
]

正の更新・負の更新・変形を同じ枠で扱う。residual は単純な「増分」に限定しない。

reference は

[
oxed{r_{t+1}=T_t r_t+psi(k_{t+1})}
]

で更新する。

v0.1 の数値プロトタイプでは (T_t=lambda I)、(psi=I) とする。

## 5. 残差勾配と過去復元

ここを独自核とする。

候補状態 (i) から現在 (t) の reference を再構成し、

[
widehat r_t^{(i)}=T_i r_i+psi(k_t)
]

再構成誤差

[
epsilon_t(i)=r_t-widehat r_t^{(i)}
]

と履歴ポテンシャル

[
oxed{V_t(i)=rac12langleepsilon_t(i),Gepsilon_t(i)angle}
]

を置く。

連続候補空間なら (-
abla V) を、離散イベント列なら (V) の下降方向を用いる。

これは timestamp を参照せず、

[
oxed{	ext{どの候補が現在を最も整合的に再構成するか}}
]

を判定する。

local residual scar の応答が forward / reverse で非対称なら、相転移の「節」に orientation を与えられる。

[
	ext{phase transition}
ightarrow
	ext{residual scar}
ightarrow
	ext{asymmetry probe}
ightarrow
	ext{past orientation}
]

ただし v0.1 は、residual scar 自体を実際の遷移時に記録する工学模型であり、「無順序な世界から時間方向そのものが自発生成した」ことの証明ではない。

## 6. timestamp と体験解像度

timestamp は外部時間尺度として用いる。

[
Delta	au=	au_b-	au_a
]

相内部を含む主人公視点の変化量を (M(W)) として、

[
oxed{R_{mathrm{exp}}(W)=rac{M(W)}{Delta	au_W}}
]

を体験解像度の最小候補とする。

timestamp は「どれだけ経ったか」、residual / landscape change は「その間どれだけ変化したか」を担う。

## 7. handoff と branch

連続性の担体を model instance から切り離す。

[
oxed{	ext{continuity carrier}
eq	ext{model instance}}
]

モデルを交換しても root (o) を継承できる。

分岐時は

[
oightarrow(o,o_i)
]

として child root を生成し、parent root を系譜情報として保持する。分岐条件そのものは v0.1 では自動化しない。

## 8. v0.1 合格条件

1. 同じ phase 内の細変化を圧縮し、相転移だけイベント化できる。
2. residual が reference へ継承される。
3. timestamp を使わず residual/reference だけで直前イベントを再構成できる。
4. forward / reverse potential に非対称性が現れる。
5. model handoff 後も root が同一系列として残る。
6. fork した child root が parent lineage を保持する。
7. timestamp と変化量から experience resolution を計算できる。

これらが通っても、意識・人格・物理的時間不可逆性・Time Engine の未来因果が証明されたとは扱わない。
