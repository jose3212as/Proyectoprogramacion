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
    "Auditoría inteligente y privada de estados de cuenta bancarios en PDF y CSV mediante Programación Funcional, SWI-Prolog y Ciencia de Datos.",
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
