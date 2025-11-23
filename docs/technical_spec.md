# 資金管理シミュレーション & 戦略評価ツール 技術仕様書

## 1. 概要

本ドキュメントは、「資金管理シミュレーション & 戦略評価ツール」の
技術構成・モジュール設計・データ構造・処理フローを定義する。

- 実装言語：Python 3 系
- UI フレームワーク：Streamlit（プロトタイプ）
- データ取得：yfinance
- データ形式：CSV（トレード履歴）、JSON（プリセット）

## 2. アーキテクチャ構成

### 2.1 レイヤ構造

1. データレイヤ
   - CSV 読み込み・検証
   - yfinance からの価格データ取得（必要な場合）
   - トレード履歴オブジェクトへのマッピング

2. ドメインレイヤ（コアロジック）
   - トレード・ポジション・ポートフォリオの内部表現
   - 資金管理エンジン（ポジションサイズ計算・残高更新）
   - 指標計算（勝率・期待値・R 期待値・DD・CAGR・破産確率など）
   - モンテカルロシミュレータ

3. アプリケーションレイヤ
   - シミュレーション条件の組み立て
   - 戦略タイプ別の前処理（イベント投資／ML 戦略）
   - 結果オブジェクトの作成

4. プレゼンテーションレイヤ（Streamlit）
   - 画面構成（タブ／ページ）
   - 入力フォーム・パラメータ設定 UI
   - グラフ・テーブル出力
   - プリセット保存・読み込み UI

## 3. 想定ディレクトリ構成

- app.py：Streamlit エントリポイント
- src/
  - config.py：共通設定値（デフォルトリスク上限など）
  - models/
    - trade.py：Trade／TradeResult モデル
    - portfolio.py：Portfolio／Position モデル（将来拡張）
  - data/
    - loader.py：CSV ローダー・バリデーション
    - yfinance_client.py：yfinance ラッパー（必要な場合）
  - risk/
    - sizing.py：ポジションサイズ計算（Fixed, Kelly, Lot）
    - metrics.py：勝率・期待値・R などの指標
    - ruin.py：バルサラ破産確率の簡易計算
  - simulation/
    - engine.py：資金管理＋残高更新のコア
    - monte_carlo.py：モンテカルロシミュレーション
  - presets/
    - manager.py：JSON プリセット読み書き
  - ui/
    - layout.py：Streamlit UI 構成
    - components.py：グラフや表の共通コンポーネント
- docs/
  - requirements.md：要件定義書
  - technical_spec.md：技術仕様書

## 4. データモデル

### 4.1 Trade（トレード）モデル

- trade_id：文字列
- strategy_id：文字列
- instrument：文字列（銘柄コード／シンボル）
- market：文字列（JP, US, FX など）
- entry_datetime：datetime
- exit_datetime：datetime
- side：LONG／SHORT
- entry_price：float
- exit_price：float
- stop_price：float（任意）
- quantity：float
- comment：文字列（任意）

### 4.2 TradeResult（トレード結果）モデル

- trade：Trade
- pnl：float（損益額）
- risk_amount：float（想定最大損失額）
- equity_before：float（トレード前残高）
- equity_after：float（トレード後残高）
- R：float（R 倍数 = pnl / risk_amount）
- f：float（リスク割合 = risk_amount / equity_before）
- portfolio_risk_sum：float（その時点の同時リスク合計％、v0 では簡略に扱う）

### 4.3 Portfolio モデル（将来拡張）

- equity：float（現在残高）
- max_portfolio_risk：float（最大リスク合計％、例 0.08）
- open_positions：ポジション辞書（v0 では必須ではない）

## 5. 資金管理ロジック

### 5.1 ポジションサイズ計算（sizing.py）

共通イメージ：

- 引数：
  - equity：現在残高
  - entry_price：エントリー価格
  - stop_price：ストップ価格（任意）
  - params：方式ごとのパラメータ（f, fixed_quantity など）
- 戻り値：
  - quantity：取引数量
  - risk_amount：想定最大損失額

#### 5.1.1 Fixed Fractional

- 入力：f（1 トレードリスク％）
- ロジック：
  - risk_amount = equity × f
  - per_unit_risk = abs(entry_price - stop_price)
  - quantity = floor(risk_amount / per_unit_risk)

#### 5.1.2 Fractional Kelly

- 入力：p, E_R, 安全係数 c
- 事前計算：f* = (E_R × p) / (E_R - p + 1)
- f_safe = c × f*
- 実際のサイズ計算は Fixed Fractional と同様（f = f_safe）

#### 5.1.3 Fixed Lot / Fixed Notional

- 入力：fixed_quantity または fixed_notional
- ロジック：
  - quantity = fixed_quantity または fixed_notional / entry_price
  - risk_amount = per_unit_risk × quantity
  - f = risk_amount / equity を後段で計算し記録

### 5.2 口座全体のリスク上限

- max_portfolio_risk（例 0.08）を保持
- 新規トレード追加時に、既存の risk_amount 合計と比較
- 合計が上限を超える場合：
  - ロットを縮小する
  - または新規トレードをスキップ（オプション）

## 6. シミュレーションエンジン（engine.py）

### 6.1 基本フロー（非オーバーラップ簡易版）

1. trades をエントリー日時順にソート
2. equity = initial_equity として開始
3. 各 trade について：
   - position_sizer で quantity, risk_amount を計算
   - pnl = (exit_price - entry_price) × quantity × (LONG/SHORT で符号調整)
   - equity_before = equity
   - equity_after = equity_before + pnl
   - R, f を計算
   - TradeResult を生成しリストへ追加
   - equity = equity_after に更新
4. 最終的に TradeResult 一覧を返す

### 6.2 指標計算（metrics.py）

- 勝率：勝ちトレード数 / 全トレード数
- 平均損益（円）：pnl 合計 / トレード数
- 平均損益（％）：平均損益（円） / 初期資金
- R 期待値：R 合計 / トレード数
- 最大ドローダウン：資産の累積推移からピークとボトムを走査して算出
- CAGR： (final_equity / initial_equity)^(1/年数) - 1

## 7. モンテカルロシミュレーション（monte_carlo.py）

### 7.1 入力

- trades：トレードリスト
- n_sims：試行回数
- n_trades：各試行のトレード数（省略時は元データ件数）
- 資金管理設定：initial_equity, position_sizer, max_portfolio_risk など

### 7.2 概要フロー

1. ループ sim in range(n_sims)：
   - trades をランダムシャッフルまたはリサンプリング
   - engine を用いて資産曲線を生成
   - final_equity, CAGR, MaxDD 等を記録
2. 分布統計（平均・中央値・パーセンタイル）を集計し UI に渡す

## 8. 破産確率（ruin.py）

### 8.1 入力

- p：勝率
- 損益比：平均利益 / 平均損失
- f：1 トレードリスク％
- ruin_threshold：破産とみなす残高比（例：0.1）

### 8.2 実装方針

- v0 ではバルサラの近似式・テーブルに基づく簡易モデルとする。
- 将来、より精緻なモデル（マルコフ連鎖近似など）を検討。

## 9. プリセット管理（presets/manager.py）

- JSON ファイルとして保存：
  - initial_equity
  - risk_settings（mode, f or p/E_R/c など）
  - strategy 情報（event or ML, strategy_id など）
- プリセット一覧取得・保存・読み込み・削除の API を用意。

## 10. Streamlit UI 設計（ui/layout.py）

- サイドバー：
  - 戦略タイプ選択（イベント／ML）
  - CSV アップロード
  - プリセット読み込み
- メインエリア：
  - 設定タブ：
    - 初期資金、資金管理方式、f／p／E_R／c、最大リスク合計％などの入力
  - 結果タブ：
    - 資産曲線、DD 曲線、指標一覧テーブル
  - モンテカルロタブ（オプション）：
    - 試行回数入力、分布表示

## 11. ログ・エラーハンドリング

- CSV 読み込み：
  - 必須列欠落時はエラーメッセージ表示
  - 型変換失敗行はスキップか全体エラーとする（オプション）
- シミュレーション：
  - 0 除算は安全に 0 として扱い、必要に応じて警告をログ出力
- 例外：
  - Streamlit のエラーパネルでユーザーに分かるように表示する。

## 12. テスト方針（概要）

- 単体テスト（pytest）：
  - sizing, metrics, ruin, engine 各モジュール
- シナリオテスト：
  - 手作業で作成した小さなトレード系列で、期待通りの資産曲線になるか確認
- 回帰テスト：
  - ロジック変更後に既存テストケースと結果を比較し、大きな乖離がないかチェック
