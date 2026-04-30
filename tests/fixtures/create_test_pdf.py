"""
Script para generar PDFs de prueba para tests de integración.

Ejecutar: python tests/fixtures/create_test_pdf.py
"""

import os


def crear_pdf_simple(contenido: str, nombre_archivo: str = "test.pdf") -> bytes:
    """
    Crea un PDF simple con el contenido especificado usando reportlab.

    Args:
        contenido: Texto a incluir en el PDF
        nombre_archivo: Nombre del archivo a generar

    Returns:
        bytes: El contenido del PDF como bytes
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        import io

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Configurar fuente y posición
        c.setFont("Helvetica", 12)
        y = height - 50

        # Escribir el contenido línea por línea
        for linea in contenido.split("\n"):
            if y > 50:  # Margen inferior
                c.drawString(50, y, linea)
                y -= 14
            else:
                # Nueva página si no hay espacio
                c.showPage()
                c.setFont("Helvetica", 12)
                y = height - 50
                c.drawString(50, y, linea)
                y -= 14

        c.save()
        buffer.seek(0)
        return buffer.read()

    except ImportError:
        print("reportlab no está instalado. Instalando...")
        import subprocess

        subprocess.run(["pip", "install", "reportlab"], check=True)
        return crear_pdf_simple(contenido, nombre_archivo)


def guardar_pdf(contenido: str, nombre_archivo: str) -> str:
    """
    Crea y guarda un PDF de prueba en el directorio fixtures.

    Args:
        contenido: Texto a incluir en el PDF
        nombre_archivo: Nombre del archivo a generar

    Returns:
        str: Ruta al archivo generado
    """
    ruta = os.path.join(os.path.dirname(__file__), nombre_archivo)
    pdf_bytes = crear_pdf_simple(contenido, nombre_archivo)

    with open(ruta, "wb") as f:
        f.write(pdf_bytes)

    print(f"PDF generado: {ruta}")
    return ruta


if __name__ == "__main__":
    # Crear PDFs de prueba
    guardar_pdf(
        "Este es un documento de prueba para testing de extracción.", "test_valido.pdf"
    )
    guardar_pdf(
        "Documento número uno con contenido suficientemente largo para pasar la validación.",
        "test_documento_1.pdf",
    )
    guardar_pdf(
        "Documento número dos con contenido suficientemente largo para pasar la validación.",
        "test_documento_2.pdf",
    )
