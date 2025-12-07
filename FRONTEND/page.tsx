'use client';

import { useState } from 'react';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const onSelectFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;

    if (f.type.startsWith('audio/') || f.name.endsWith('.m4a')) {
      setFile(f);
      setResult(null);
    } else {
      alert('音声ファイルを選択してください。');
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (!f) return;

    if (f.type.startsWith('audio/') || f.name.endsWith('.m4a')) {
      setFile(f);
      setResult(null);
    } else {
      alert('音声ファイルを選択してください。');
    }
  };

  const onUpload = async () => {
    if (!file) return;

    setLoading(true);

    try {
      const form = new FormData();
      form.append('file', file);

      const res = await fetch('http://localhost:8000/transcribe', {
        method: 'POST',
        body: form,
      });

      const data = await res.json();
      if (data.success) {
        setResult(data);
      } else {
        alert(data.detail || 'エラーが発生しました');
      }
    } catch (err) {
      console.error(err);
      alert('サーバーへ接続できませんでした。');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">

        <h1 className="text-4xl font-bold text-center mb-4">
          音声文字起こし & 要約
        </h1>
        <p className="text-center text-gray-400 mb-10">
          音声をアップロードして自動で処理します
        </p>

        {!result && (
          <div
            onDrop={onDrop}
            onDragOver={(e) => e.preventDefault()}
            className="border-2 border-dashed border-gray-600 rounded-xl p-10 text-center bg-gray-800/40 mb-8"
          >
            {!file ? (
              <>
                <p className="text-xl mb-4">ここにファイルをドロップ</p>
                <label className="inline-block px-6 py-3 bg-gray-700 rounded-xl cursor-pointer hover:bg-gray-600">
                  <span>ファイルを選択</span>
                  <input
                    type="file"
                    accept="audio/*,.m4a"
                    onChange={onSelectFile}
                    className="hidden"
                  />
                </label>
              </>
            ) : (
              <>
                <p className="text-2xl mb-2 text-green-400">選択済み</p>
                <p className="mb-6">{file.name}</p>
                <div className="flex justify-center gap-4">
                  <button
                    onClick={() => setFile(null)}
                    className="px-5 py-3 bg-gray-700 rounded-xl hover:bg-gray-600"
                    disabled={loading}
                  >
                    別のファイル
                  </button>
                  <button
                    onClick={onUpload}
                    disabled={loading}
                    className="px-7 py-3 bg-blue-600 rounded-xl hover:bg-blue-500 disabled:opacity-50"
                  >
                    {loading ? '処理中...' : '開始'}
                  </button>
                </div>
              </>
            )}
          </div>
        )}

        {loading && (
          <div className="text-center py-10">
            <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p>処理しています…</p>
          </div>
        )}

        {result && !loading && (
          <div className="space-y-6">
            <section className="bg-gray-800 p-6 rounded-xl">
              <h2 className="text-xl font-bold mb-2">ファイル情報</h2>
              <p>名前: {result.filename}</p>
              <p className="text-gray-400">文字数: {result.transcription?.length || 0}</p>
            </section>

            <section className="bg-gray-800 p-6 rounded-xl">
              <h2 className="text-xl font-bold mb-2">文字起こし</h2>
              <div className="bg-gray-900 p-4 rounded-lg max-h-96 overflow-y-auto">
                <p className="whitespace-pre-wrap text-lg">{result.transcription}</p>
              </div>
            </section>

            {result.summary && (
              <section className="bg-gray-800 p-6 rounded-xl">
                <h2 className="text-xl font-bold mb-2">要約</h2>
                <p className="text-lg leading-relaxed">{result.summary}</p>
              </section>
            )}

            {result.key_points?.length > 0 && (
              <section className="bg-gray-800 p-6 rounded-xl">
                <h2 className="text-xl font-bold mb-2">重要ポイント</h2>
                <ul className="space-y-2">
                  {result.key_points.map((pt: string, i: number) => (
                    <li key={i} className="flex gap-2">
                      <span className="font-bold">{i + 1}.</span>
                      <span>{pt}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            <div className="text-center">
              <button
                onClick={() => {
                  setFile(null);
                  setResult(null);
                }}
                className="px-7 py-3 bg-blue-600 rounded-xl hover:bg-blue-500"
              >
                もう一度処理する
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}