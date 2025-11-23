# 資金管理シミュレーション & 戦略評価ツール

Streamlit で動作する資金管理シミュレーションのプロトタイプです。トレード履歴 CSV を読み込み、資金曲線・ドローダウン・各種指標を表示し、モンテカルロ試行や破産確率の簡易計算を行います。プリセットは JSON で保存できます。

## セットアップ

```bash
pip install -r requirements.txt
```

## 起動

```bash
streamlit run app.py
```

ブラウザが開かない場合は `http://localhost:8501` を開いてください。

## トレード履歴 CSV フォーマット

- 文字コード: UTF-8 (BOM なし)
- 区切り: カンマ
- 1 行目: ヘッダー
- 必須列:
  - `trade_id` (文字列)
  - `strategy_id` (文字列)
  - `instrument` (銘柄コード/シンボル)
  - `entry_datetime` (例: `2024-01-01 09:00:00`)
  - `exit_datetime` (例: `2024-01-05 15:00:00`)
  - `side` (`LONG` または `SHORT`)
  - `entry_price` (数値)
  - `exit_price` (数値)
- 任意列:
  - `market` (例: `JP`, `US`, `FX`)
  - `stop_price` (数値; 未指定時はリスク0扱い)
  - `quantity` (数値; 指定時はこのサイズを優先)
  - `comment`

### サンプル行

```csv
trade_id,strategy_id,instrument,market,entry_datetime,exit_datetime,side,entry_price,exit_price,stop_price,quantity,comment
T1,EVT,7203.T,JP,2024-01-01 09:00:00,2024-01-05 15:00:00,LONG,2000,2100,1900,,N営業日前エントリー
T2,ML,USDJPY=X,FX,2024-02-01 10:00:00,2024-02-02 10:00:00,SHORT,150.0,148.5,151.5,,
```

## 使い方の流れ

1) サイドバーで初期資金・資金管理方式（Fixed Fractional / Fractional Kelly / Fixed Lot）・最大同時リスク％を設定  
2) トレード履歴 CSV をアップロード（ない場合は「サンプルトレードを使う」をオン）  
3) 結果タブで資産曲線/ドローダウン/各種指標を確認  
4) モンテカルロタブで試行回数を指定し分布を表示  
5) 破産確率タブで勝率・損益比から簡易ロスオブルインを確認  
6) プリセット名を入力し保存/読み込み/削除で設定を管理

## 注意事項

- 手数料・スリッページ・税金は考慮していません（v0）。  
- `stop_price` 未指定の場合、リスクを 0 とみなし R 倍数は 0 になります。  
- `quantity` を指定した場合は CSV の数量を優先し、固定％リスクより多い/少ない可能性があります。  
- 最大同時リスク％は各トレード単体のリスク％で簡易的にスケーリングしています（ポジション重複は未考慮）。  
- プリセットは `presets_data/` 配下に JSON として保存されます。
