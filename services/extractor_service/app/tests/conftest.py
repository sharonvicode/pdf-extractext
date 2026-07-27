from pathlib import Path

import pytest
from fpdf import FPDF


@pytest.fixture
def pdf_valido(tmp_path: Path) -> Path:
    path = tmp_path / "test.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(text="Contenido de prueba para extraccion")
    pdf.output(str(path))
    return path


@pytest.fixture
def pdf_vacio(tmp_path: Path) -> Path:
    path = tmp_path / "vacio.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.output(str(path))
    return path
