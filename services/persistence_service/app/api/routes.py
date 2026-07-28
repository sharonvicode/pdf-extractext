from fastapi import APIRouter, HTTPException
from bson.errors import InvalidId

from app.schemas.document_schema import DocumentCreate, DocumentResponse
from app.repository.mongodb_repository import DocumentRepository

router = APIRouter(tags=["documents"])

repository = DocumentRepository()


@router.post("/documents", response_model=DocumentResponse, status_code=201)
def create_document(payload: DocumentCreate):
    document_id = repository.save(
        filename=payload.filename,
        content=payload.content,
        metadata=payload.metadata,
    )
    return DocumentResponse(document_id=document_id)


@router.get("/documents")
def list_documents():
    return repository.list_all()


@router.get("/documents/{document_id}")
def get_document(document_id: str):
    try:
        doc = repository.get_by_id(document_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de documento inválido")
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return doc


@router.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: str):
    try:
        deleted = repository.delete(document_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de documento inválido")
    if not deleted:
        raise HTTPException(status_code=404, detail="Documento no encontrado")


@router.get("/health")
def health_check():
    return {"status": "ok"}