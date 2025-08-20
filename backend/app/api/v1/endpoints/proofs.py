"""
Enhanced Proof Submission API endpoints for FocusForge
Provides comprehensive proof submission with file uploads and AI validation
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.services.proof_service import ProofService
from app.models.schemas import EnhancedTaskCompletion, ProofSubmission, ProofType
from app.models.api_schemas import validate_user_id
from app.core.database import get_database
from app.core.auth import get_current_user_from_token

router = APIRouter()

# ===== ENHANCED PROOF SUBMISSION =====

@router.post("/submit")
async def submit_enhanced_proof(
    task_id: str = Form(..., description="Task ID"),
    user_id: str = Depends(get_current_user_from_token),
    completion_note: Optional[str] = Form(None, description="Completion notes"),
    completion_confidence: int = Form(5, ge=1, le=10, description="Completion confidence (1-10)"),
    time_spent_minutes: Optional[int] = Form(None, description="Time spent in minutes"),
    challenges_faced: Optional[str] = Form(None, description="Challenges faced (JSON array)"),
    lessons_learned: Optional[str] = Form(None, description="Lessons learned"),
    proof_texts: Optional[str] = Form(None, description="Text proofs (JSON array)"),
    proof_links: Optional[str] = Form(None, description="Link proofs (JSON array)"),
    files: List[UploadFile] = File(default=[], description="File attachments"),
    db=Depends(get_database)
):
    """Submit enhanced proof with multiple evidence types"""
    try:
        user_id = validate_user_id(user_id)
        proof_service = ProofService(db)
        await proof_service.initialize()
        
        # Parse JSON fields
        challenges_list = json.loads(challenges_faced) if challenges_faced else []
        text_proofs = json.loads(proof_texts) if proof_texts else []
        link_proofs = json.loads(proof_links) if proof_links else []
        
        # Build proof submissions list
        proofs = []
        
        # Add text proofs
        for text_proof in text_proofs:
            proofs.append(ProofSubmission(
                proof_type=ProofType.TEXT,
                content=text_proof.get("content", ""),
                description=text_proof.get("description", "Text proof")
            ))
        
        # Add link proofs
        for link_proof in link_proofs:
            proofs.append(ProofSubmission(
                proof_type=ProofType.LINK,
                content=link_proof.get("url", ""),
                description=link_proof.get("description", "Link proof")
            ))
        
        # Process file uploads
        uploaded_files = []
        for file in files:
            if file.filename:
                file_content = await file.read()
                uploaded_files.append({
                    "filename": file.filename,
                    "content": file_content,
                    "content_type": file.content_type
                })
        
        # Create enhanced completion data
        completion_data = EnhancedTaskCompletion(
            task_id=task_id,
            completion_note=completion_note,
            proofs=proofs,
            completion_confidence=completion_confidence,
            time_spent_minutes=time_spent_minutes,
            challenges_faced=challenges_list,
            lessons_learned=lessons_learned
        )
        
        # Submit proof
        result = await proof_service.submit_enhanced_proof(
            user_id, completion_data, uploaded_files
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Proof submission failed"))
        
        return {
            **result,
            "submission_summary": {
                "text_proofs": len(text_proofs),
                "link_proofs": len(link_proofs),
                "file_uploads": len(uploaded_files),
                "total_evidence_pieces": len(proofs) + len(uploaded_files),
                "confidence_level": completion_confidence,
                "time_invested": f"{time_spent_minutes} minutes" if time_spent_minutes else "Not specified"
            },
            "tips_for_next_time": [
                "Include screenshots or photos of your work for stronger evidence",
                "Detailed descriptions help with validation scoring",
                "Multiple types of proof provide better validation",
                "Be specific about what you accomplished"
            ]
        }
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in form data: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proof submission failed: {str(e)}")

@router.post("/submit-simple")
async def submit_simple_proof(
    task_id: str = Query(..., description="Task ID"),
    user_id: str = Depends(get_current_user_from_token),
    proof_text: str = Form(..., description="Text proof of completion"),
    completion_confidence: int = Form(5, ge=1, le=10, description="Completion confidence"),
    time_spent_minutes: Optional[int] = Form(None, description="Time spent"),
    db=Depends(get_database)
):
    """Submit simple text-based proof (backwards compatibility)"""
    try:
        user_id = validate_user_id(user_id)
        proof_service = ProofService(db)
        await proof_service.initialize()
        
        # Create simple completion data
        completion_data = EnhancedTaskCompletion(
            task_id=task_id,
            proofs=[ProofSubmission(
                proof_type=ProofType.TEXT,
                content=proof_text,
                description="Task completion proof"
            )],
            completion_confidence=completion_confidence,
            time_spent_minutes=time_spent_minutes
        )
        
        result = await proof_service.submit_enhanced_proof(user_id, completion_data)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Proof submission failed"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simple proof submission failed: {str(e)}")

# ===== PROOF MANAGEMENT =====

@router.get("/history")
async def get_proof_history(
    user_id: str = Depends(get_current_user_from_token),
    limit: int = Query(20, ge=1, le=100, description="Number of proofs to return"),
    task_id: Optional[str] = Query(None, description="Filter by task ID"),
    db=Depends(get_database)
):
    """Get user's proof submission history"""
    try:
        user_id = validate_user_id(user_id)
        proof_service = ProofService(db)
        await proof_service.initialize()
        
        history = await proof_service.get_user_proof_history(user_id, limit, task_id)
        
        # Format for response
        formatted_history = []
        for proof in history:
            formatted_history.append({
                "proof_id": proof["_id"],
                "task_id": proof["task_id"],
                "submitted_at": proof["submitted_at"].isoformat(),
                "validation_score": proof.get("validation_result", {}).get("overall_score", 0),
                "validation_status": proof.get("validation_result", {}).get("validation_status", "unknown"),
                "proof_count": len(proof.get("proofs", [])),
                "file_count": len(proof.get("processed_files", [])),
                "completion_confidence": proof.get("completion_confidence", 5),
                "time_spent_minutes": proof.get("time_spent_minutes"),
                "status": proof.get("status", "submitted"),
                "completion_note": proof.get("completion_note", "")[:100] + "..." if len(proof.get("completion_note", "")) > 100 else proof.get("completion_note", "")
            })
        
        return {
            "success": True,
            "user_id": user_id,
            "total_returned": len(formatted_history),
            "history": formatted_history,
            "filters": {
                "limit": limit,
                "task_id": task_id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get proof history: {str(e)}")

@router.get("/{proof_id}")
async def get_proof_details(
    proof_id: str,
    user_id: str = Depends(get_current_user_from_token),
    db=Depends(get_database)
):
    """Get detailed information about a specific proof submission"""
    try:
        user_id = validate_user_id(user_id)
        proof_service = ProofService(db)
        await proof_service.initialize()
        
        proof = await proof_service.collection.find_one({
            "_id": proof_id,
            "user_id": user_id
        })
        
        if not proof:
            raise HTTPException(status_code=404, detail="Proof not found")
        
        # Format response
        return {
            "success": True,
            "proof": {
                "proof_id": proof["_id"],
                "task_id": proof["task_id"],
                "block_id": proof.get("block_id"),
                "submitted_at": proof["submitted_at"].isoformat(),
                "completion_note": proof.get("completion_note", ""),
                "completion_confidence": proof.get("completion_confidence", 5),
                "time_spent_minutes": proof.get("time_spent_minutes"),
                "challenges_faced": proof.get("challenges_faced", []),
                "lessons_learned": proof.get("lessons_learned", ""),
                "status": proof.get("status", "submitted"),
                "proofs": proof.get("proofs", []),
                "processed_files": proof.get("processed_files", []),
                "validation_result": proof.get("validation_result", {}),
                "file_urls": [
                    proof_service.file_service.get_file_url(f["relative_path"])
                    for f in proof.get("processed_files", [])
                ]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get proof details: {str(e)}")

# ===== FILE MANAGEMENT =====

@router.get("/files/{file_path:path}")
async def get_uploaded_file(
    file_path: str,
    user_id: str = Depends(get_current_user_from_token)
):
    """Retrieve an uploaded proof file"""
    try:
        user_id = validate_user_id(user_id)
        proof_service = ProofService()
        
        # Security check: ensure file belongs to user
        # This is a simplified check - in production, you'd want more robust security
        if not file_path.startswith(user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        full_path = proof_service.file_service.upload_dir / file_path
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(full_path),
            filename=full_path.name,
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve file: {str(e)}")

@router.delete("/files/{file_path:path}")
async def delete_uploaded_file(
    file_path: str,
    user_id: str = Depends(get_current_user_from_token),
    db=Depends(get_database)
):
    """Delete an uploaded proof file"""
    try:
        user_id = validate_user_id(user_id)
        proof_service = ProofService(db)
        await proof_service.initialize()
        
        # Security check
        if not file_path.startswith(user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if file is referenced in any proof submissions
        file_usage = await proof_service.collection.find_one({
            "user_id": user_id,
            "processed_files.relative_path": file_path
        })
        
        if file_usage:
            # Update proof record to mark file as deleted
            await proof_service.collection.update_one(
                {"_id": file_usage["_id"]},
                {"$set": {"processed_files.$[elem].deleted_at": datetime.now()}},
                array_filters=[{"elem.relative_path": file_path}]
            )
        
        # Delete the actual file
        success = await proof_service.file_service.delete_file(file_path)
        
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "success": True,
            "message": "File deleted successfully",
            "file_path": file_path
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

# ===== ANALYTICS & INSIGHTS =====

@router.get("/analytics/overview")
async def get_proof_analytics(
    user_id: str = Depends(get_current_user_from_token),
    days_back: int = Query(30, ge=1, le=365, description="Days to analyze"),
    db=Depends(get_database)
):
    """Get comprehensive proof submission analytics"""
    try:
        user_id = validate_user_id(user_id)
        proof_service = ProofService(db)
        await proof_service.initialize()
        
        analytics = await proof_service.get_proof_analytics(user_id, days_back)
        
        if not analytics["success"]:
            raise HTTPException(status_code=500, detail=analytics.get("error", "Analytics failed"))
        
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.get("/analytics/validation-trends")
async def get_validation_trends(
    user_id: str = Depends(get_current_user_from_token),
    days_back: int = Query(30, ge=1, le=365, description="Days to analyze"),
    db=Depends(get_database)
):
    """Get validation score trends over time"""
    try:
        user_id = validate_user_id(user_id)
        proof_service = ProofService(db)
        await proof_service.initialize()
        
        # Get proof history
        start_date = datetime.now() - timedelta(days=days_back)
        cursor = proof_service.collection.find({
            "user_id": user_id,
            "submitted_at": {"$gte": start_date}
        }).sort("submitted_at", 1)
        
        trends = []
        total_score = 0
        count = 0
        
        async for proof in cursor:
            validation_result = proof.get("validation_result", {})
            score = validation_result.get("overall_score", 0)
            
            trends.append({
                "date": proof["submitted_at"].date().isoformat(),
                "score": score,
                "status": validation_result.get("validation_status", "unknown"),
                "proof_count": len(proof.get("proofs", []))
            })
            
            total_score += score
            count += 1
        
        avg_score = total_score / count if count > 0 else 0
        
        return {
            "success": True,
            "user_id": user_id,
            "period_days": days_back,
            "average_score": round(avg_score, 2),
            "total_submissions": count,
            "trends": trends,
            "insights": [
                f"Your average validation score is {round(avg_score, 1)}/10",
                "Consistency in proof quality is key to building good habits",
                "Higher quality evidence typically results in better scores",
                "Track your improvement over time to stay motivated"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get validation trends: {str(e)}")

# ===== PROOF TEMPLATES & GUIDANCE =====

@router.get("/templates")
async def get_proof_templates():
    """Get proof submission templates and best practices"""
    return {
        "templates": {
            "coding_task": {
                "name": "Coding/Development Task",
                "suggested_proofs": [
                    {
                        "type": "file",
                        "description": "Upload source code files",
                        "examples": ["main.py", "app.js", "README.md"]
                    },
                    {
                        "type": "image",
                        "description": "Screenshots of running application",
                        "examples": ["terminal output", "UI screenshots", "test results"]
                    },
                    {
                        "type": "link",
                        "description": "Links to deployed app or repository",
                        "examples": ["GitHub repo", "live demo", "documentation"]
                    },
                    {
                        "type": "text",
                        "description": "Description of implementation approach",
                        "examples": ["technical details", "challenges solved", "features implemented"]
                    }
                ]
            },
            "learning_task": {
                "name": "Learning/Study Task",
                "suggested_proofs": [
                    {
                        "type": "text",
                        "description": "Summary of what you learned",
                        "examples": ["key concepts", "insights gained", "questions answered"]
                    },
                    {
                        "type": "image",
                        "description": "Photos of notes or study materials",
                        "examples": ["handwritten notes", "mind maps", "study guides"]
                    },
                    {
                        "type": "file",
                        "description": "Study materials created",
                        "examples": ["PDF notes", "flashcards", "practice problems"]
                    }
                ]
            },
            "creative_task": {
                "name": "Creative Task",
                "suggested_proofs": [
                    {
                        "type": "image",
                        "description": "Photos of your creative work",
                        "examples": ["artwork", "designs", "prototypes"]
                    },
                    {
                        "type": "file",
                        "description": "Digital creative files",
                        "examples": ["PSD files", "videos", "audio files"]
                    },
                    {
                        "type": "text",
                        "description": "Creative process description",
                        "examples": ["inspiration sources", "techniques used", "design decisions"]
                    }
                ]
            },
            "physical_task": {
                "name": "Physical/Exercise Task",
                "suggested_proofs": [
                    {
                        "type": "image",
                        "description": "Photos of activity",
                        "examples": ["workout selfie", "equipment used", "location"]
                    },
                    {
                        "type": "text",
                        "description": "Activity details",
                        "examples": ["duration", "intensity", "achievements"]
                    },
                    {
                        "type": "link",
                        "description": "Fitness app data",
                        "examples": ["Strava activity", "fitness tracker", "app screenshots"]
                    }
                ]
            }
        },
        "best_practices": [
            "Be specific and detailed in your descriptions",
            "Include visual evidence whenever possible",
            "Upload actual work products (files, documents)",
            "Explain challenges you overcame",
            "Share what you learned from the experience",
            "Use multiple types of proof for stronger validation",
            "Be honest about your completion confidence level"
        ],
        "scoring_factors": [
            "Specificity and detail in descriptions",
            "Quality and relevance of visual evidence",
            "Inclusion of actual work products",
            "Demonstration of learning and growth",
            "Honest self-assessment",
            "Multiple proof types strengthen validation"
        ]
    }
