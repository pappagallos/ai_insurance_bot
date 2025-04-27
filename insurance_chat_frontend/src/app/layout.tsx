import type { Metadata } from "next";

import "./global.scss";

// Fonts
import localFont from "next/font/local";
const pretendard = localFont({
  src: "./fonts/PretendardVariable.woff2",
  display: "swap",
  weight: "45 920",
  variable: "--font-pretendard",
});

// Metadata
export const metadata: Metadata = {
  title: "Insurance Chat",
  description: "Insurance Chat",
};

// Root Layout
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="kr">
      <body className={`${pretendard.variable}`}>
        {children}
      </body>
    </html>
  );
}
