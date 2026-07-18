import os
import uuid
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from datetime import date

from app.database import get_db
from app.models import User, RoleEnum
from app.models.certificate import Certificate, CertificateCategoryEnum
from app.models.student import StudentProfile
from app.dependencies.auth import get_current_active_user, RoleChecker
from app.schemas import StandardResponse

require_student = RoleChecker([RoleEnum.student])
require_faculty_or_hod = RoleChecker([RoleEnum.faculty, RoleEnum.hod])

router = APIRouter(prefix="/api/certificates", tags=["Certificates"])

UPLOAD_DIR = "uploads/certificates"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=StandardResponse)
async def upload_certificate(
    title: str = Form(...),
    event_name: str = Form(...),
    category: CertificateCategoryEnum = Form(...),
    issuing_body: str = Form(...),
    date_achieved: date = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
):

    # Get student profile
    result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == current_user.id))
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

    # Validate file type
    allowed_types = {"application/pdf", "image/jpeg", "image/png"}
    if file.content_type not in allowed_types:
        return StandardResponse(success=False, data=None, error="Only PDF, JPEG, or PNG files are allowed.")

    # Save file
    ext = os.path.splitext(file.filename or "file")[1] or ".pdf"
    file_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    contents = await file.read()
    file_size_kb = len(contents) // 1024

    with open(file_path, "wb") as f:
        f.write(contents)

    cert = Certificate(
        student_id=student.id,
        title=title,
        event_name=event_name,
        category=category,
        issuing_body=issuing_body,
        date_achieved=date_achieved,
        file_path=file_path,
        file_size_kb=file_size_kb,
    )
    db.add(cert)
    await db.commit()
    await db.refresh(cert)

    return StandardResponse(success=True, data={"id": str(cert.id), "title": cert.title, "status": cert.verification_status.value})


@router.get("/me", response_model=StandardResponse)
async def get_my_certificates(
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == current_user.id))
    student = result.scalars().first()
    if not student:
        return StandardResponse(success=True, data={"certificates": []})

    cert_result = await db.execute(
        select(Certificate).where(Certificate.student_id == student.id).order_by(Certificate.uploaded_at.desc())
    )
    certs = cert_result.scalars().all()

    return StandardResponse(success=True, data={
        "certificates": [
            {
                "id": str(c.id),
                "title": c.title,
                "event_name": c.event_name,
                "category": c.category.value,
                "issuing_body": c.issuing_body,
                "date_achieved": str(c.date_achieved),
                "file_size_kb": c.file_size_kb,
                "verification_status": c.verification_status.value,
                "uploaded_at": c.uploaded_at.isoformat(),
            }
            for c in certs
        ]
    })


@router.delete("/{cert_id}", response_model=StandardResponse)
async def delete_certificate(
    cert_id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == current_user.id))
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

    cert_result = await db.execute(
        select(Certificate).where(Certificate.id == uuid.UUID(cert_id), Certificate.student_id == student.id)
    )
    cert = cert_result.scalars().first()
    if not cert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found.")

    # Only allow deleting pending certificates
    if cert.verification_status.value != "pending":
        return StandardResponse(success=False, data=None, error="Only pending certificates can be deleted.")

    # Remove file from disk
    if os.path.exists(cert.file_path):
        os.remove(cert.file_path)

    await db.delete(cert)
    await db.commit()

    return StandardResponse(success=True, data={"message": "Certificate deleted."})
