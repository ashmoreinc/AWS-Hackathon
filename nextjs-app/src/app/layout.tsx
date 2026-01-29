import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AWS Hackathon - Next.js with AWS Integration",
  description: "Next.js application with AWS DynamoDB and S3 integration",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
