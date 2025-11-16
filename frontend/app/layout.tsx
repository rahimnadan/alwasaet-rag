import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Alwasaet RAG - Professional Document Q&A",
  description: "Professional RAG application for document question answering",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
