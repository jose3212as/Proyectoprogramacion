import type { Metadata } from "next";
import { Plus_Jakarta_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { AuditProvider } from "@/context/AuditContext";
import { AppShell } from "@/components/AppShell";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-jakarta",
  weight: ["400", "500", "600", "700", "800"],
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "FinGuard | Finanzas Personales y Escudo Antifraude",
  description:
    "Revisa tu estado de cuenta mensual en PDF o CSV, detecta gastos invisibles y protege tu tarjeta sin compartir tus claves bancarias.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className={`${jakarta.variable} ${jetbrains.variable}`}>
      <body className="min-h-screen antialiased">
        <AuditProvider>
          <AppShell>{children}</AppShell>
        </AuditProvider>
      </body>
    </html>
  );
}
