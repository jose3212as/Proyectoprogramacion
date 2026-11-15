import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FinGuard | Asistente de Finanzas Personales y Escudo Antifraude",
  description:
    "Auditoría inteligente y privada de estados de cuenta bancarios (PDF/CSV) mediante Programación Funcional, SWI-Prolog y Ciencia de Datos.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
