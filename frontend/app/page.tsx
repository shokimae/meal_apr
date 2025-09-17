export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50">
      <section className="mx-auto max-w-3xl px-6 py-12">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Meal Logger</h1>
        <p className="text-slate-600 mb-6">
          Next.js + FastAPI + Tailwind が動いています。上の <code>/items</code> ページでAPI疎通も確認できます。
        </p>
        <a href="/items" className="inline-flex items-center rounded-xl px-4 py-2 border border-slate-300 hover:bg-white bg-slate-100">
          Go to Items →
        </a>
      </section>
    </main>
  )
}
