～バックエンド～　概要　
このプロジェクトは、音声ファイルをアップロードして文字起こしと要約を行う FastAPI サーバーです。  
Whisper モデルを使用した高精度の日本語文字起こしと、OpenRouter API 経由での要約機能も利用可能です。  
更にコストを抑えるために AI は DeepSeek を採用しています。

主な機能
・音声ファイルのアップロード（.wav, .mp3, .m4a 等に対応）  
・Whisper モデルによる日本語文字起こし  
・OpenRouter API 経由での要約・重要ポイント抽出（API キー必須）  
・JSON 形式で文字起こし・要約・重要ポイントを返却  
・CORS 設定により、Next.js などのフロントエンドと直接連携可能  
・安全な一時ファイル保存と自動削除  
・エラー処理による安定稼働  

実装の特徴
・@app.get("/") や @app.post("/transcribe") によるルーティング  
・UploadFile, File でファイル受信  
・HTTPException による例外処理  
・CORSMiddleware でフロントエンドからのリクエストを許可  
・whisper.load_model("medium") でモデルロード  
・model.transcribe(tmp_path, language="ja") で文字起こし  
・tempfile.NamedTemporaryFile で一時ファイル生成  
・os.unlink(tmp_path) で文字起こし後に自動削除  
・requests.post で OpenRouter API 経由で DeepSeek モデルに要約リクエスト  
・JSON 形式で要約結果と重要ポイントを取得  
・try/except で JSON パースエラーに対応  
・dotenv.load_dotenv で .env から OPENROUTER_API_KEY を読み込み  
・アップロード、文字起こし、API リクエスト・レスポンスを詳細に出力  
・エラー内容もログ出力し、開発時に追跡可能
