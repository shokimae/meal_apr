
import Link from 'next/link';

export default function HomePage() {
  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 700 }}>Next.js + FastAPI + Firebase</h1>
      <p>Dockerで立ち上がる最小構成です。</p>
      <ul style={{ marginTop: 12 }}>
        <li><a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">FastAPI Docs</a></li>
        <li><Link href="/items">Items ページ</Link></li>
      </ul>
      <p style={{ marginTop: 12 }}>
        /api/* は Next.js の <code>rewrites</code> で <code>backend:8000</code> にプロキシされます。
      </p>
    </div>
  );
}
