
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body className="min-h-screen antialiased">
        <main className="p-6 max-w-3xl mx-auto">
          {children}
        </main>
      </body>
    </html>
  );
}
