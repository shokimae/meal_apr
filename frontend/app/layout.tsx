import "./globals.css";
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <main className="max-w-3xl mx-auto p-6">{children}</main>
      </body>
    </html>
  );
}
