"""
Enhanced Proof Submission Service for FocusForge
Handles rich proof submission with file uploads, links, and AI validation
"""

import os
import asyncio
import logging
import hashlib
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path
import aiofiles
from PIL import Image
import uuid

from app.core.database import get_database
from app.models.schemas import ProofSubmission, EnhancedTaskCompletion, ProofType
from app.services.llm_service import LLMService
from app.core.config import settings

logger = logging.getLogger(__name__)

class FileUploadService:
    """Service for handling file uploads and storage"""
    
    def __init__(self):
        self.upload_dir = Path(getattr(settings, 'UPLOAD_DIR', './uploads'))
        self.max_file_size = getattr(settings, 'MAX_FILE_SIZE_MB', 10) * 1024 * 1024  # 10MB default
        self.allowed_extensions = {
            'image': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'},
            'video': {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'},
            'document': {'.pdf', '.doc', '.docx', '.txt', '.md', '.rtf'},
            'archive': {'.zip', '.rar', '.7z', '.tar', '.gz'}
        }
        self._ensure_upload_dirs()
    
    def _ensure_upload_dirs(self):
        """Ensure upload directories exist"""
        self.upload_dir.mkdir(exist_ok=True)
        (self.upload_dir / 'images').mkdir(exist_ok=True)
        (self.upload_dir / 'videos').mkdir(exist_ok=True)
        (self.upload_dir / 'documents').mkdir(exist_ok=True)
        (self.upload_dir / 'archives').mkdir(exist_ok=True)
        (self.upload_dir / 'thumbnails').mkdir(exist_ok=True)
    
    def _get_file_category(self, file_extension: str) -> str:
        """Determine file category based on extension"""
        file_extension = file_extension.lower()
        for category, extensions in self.allowed_extensions.items():
            if file_extension in extensions:
                return category
        return 'other'
    
    def _generate_secure_filename(self, original_filename: str, user_id: str) -> str:
        """Generate a secure, unique filename"""
        file_extension = Path(original_filename).suffix.lower()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        secure_name = f"{user_id}_{timestamp}_{unique_id}{file_extension}"
        return secure_name
    
    async def save_uploaded_file(self, file_content: bytes, filename: str, user_id: str) -> Dict[str, Any]:
        """Save uploaded file and return file info"""
        try:
            # Check file size
            if len(file_content) > self.max_file_size:
                return {
                    "success": False,
                    "error": f"File size exceeds {self.max_file_size // (1024*1024)}MB limit"
                }
            
            # Get file info
            file_extension = Path(filename).suffix.lower()
            category = self._get_file_category(file_extension)
            
            if category == 'other':
                return {
                    "success": False,
                    "error": f"File type {file_extension} not allowed"
                }
            
            # Generate secure filename
            secure_filename = self._generate_secure_filename(filename, user_id)
            
            # Determine storage path
            if category == 'image':
                storage_path = self.upload_dir / 'images' / secure_filename
            elif category == 'video':
                storage_path = self.upload_dir / 'videos' / secure_filename
            elif category == 'document':
                storage_path = self.upload_dir / 'documents' / secure_filename
            else:
                storage_path = self.upload_dir / 'archives' / secure_filename
            
            # Save file
            async with aiofiles.open(storage_path, 'wb') as f:
                await f.write(file_content)
            
            # Generate thumbnail for images
            thumbnail_path = None
            if category == 'image':
                thumbnail_path = await self._generate_thumbnail(storage_path, secure_filename)
            
            # Calculate file hash for integrity
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            file_info = {
                "success": True,
                "filename": secure_filename,
                "original_filename": filename,
                "file_path": str(storage_path),
                "relative_path": str(storage_path.relative_to(self.upload_dir)),
                "category": category,
                "size_bytes": len(file_content),
                "size_mb": round(len(file_content) / (1024*1024), 2),
                "file_hash": file_hash,
                "thumbnail_path": thumbnail_path,
                "uploaded_at": datetime.now().isoformat(),
                "file_extension": file_extension
            }
            
            logger.info(f"File uploaded successfully: {secure_filename} for user {user_id}")
            return file_info
            
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_thumbnail(self, image_path: Path, secure_filename: str) -> Optional[str]:
        """Generate thumbnail for image files"""
        try:
            thumbnail_filename = f"thumb_{secure_filename}"
            thumbnail_path = self.upload_dir / 'thumbnails' / thumbnail_filename
            
            # Use PIL to create thumbnail
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                img.save(thumbnail_path, 'JPEG', quality=85)
            
            return str(thumbnail_path.relative_to(self.upload_dir))
        except Exception as e:
            logger.warning(f"Failed to generate thumbnail: {e}")
            return None
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file and its thumbnail"""
        try:
            full_path = self.upload_dir / file_path
            if full_path.exists():
                full_path.unlink()
                
                # Delete thumbnail if it exists
                if 'images/' in file_path:
                    thumbnail_name = f"thumb_{full_path.name}"
                    thumbnail_path = self.upload_dir / 'thumbnails' / thumbnail_name
                    if thumbnail_path.exists():
                        thumbnail_path.unlink()
                
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    def get_file_url(self, file_path: str) -> str:
        """Get URL for accessing uploaded file"""
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
        return f"{base_url}/files/{file_path}"

class ProofValidationService:
    """Enhanced proof validation with AI analysis"""
    
    def __init__(self):
        self.llm_service = LLMService()
    
    async def validate_proof_submission(self, task_description: str, proofs: List[ProofSubmission], completion_criteria: str = "") -> Dict[str, Any]:
        """Validate proof submission using AI analysis"""
        try:
            validation_results = []
            overall_score = 0
            total_weight = 0
            
            for i, proof in enumerate(proofs):
                # Weight different proof types
                proof_weight = self._get_proof_weight(proof.proof_type)
                total_weight += proof_weight
                
                # Validate individual proof
                proof_result = await self._validate_single_proof(
                    task_description, proof, completion_criteria, i + 1
                )
                
                validation_results.append(proof_result)
                overall_score += proof_result["score"] * proof_weight
            
            # Calculate overall validation score
            final_score = overall_score / total_weight if total_weight > 0 else 0
            
            # Determine validation status
            validation_status = self._determine_validation_status(final_score, validation_results)
            
            # Generate comprehensive feedback
            feedback = await self._generate_comprehensive_feedback(
                task_description, validation_results, final_score, validation_status
            )
            
            return {
                "success": True,
                "overall_score": round(final_score, 2),
                "validation_status": validation_status,
                "individual_proofs": validation_results,
                "comprehensive_feedback": feedback,
                "recommendations": self._generate_recommendations(validation_results, final_score),
                "validated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Proof validation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "overall_score": 0,
                "validation_status": "error"
            }
    
    def _get_proof_weight(self, proof_type: ProofType) -> float:
        """Get weight for different proof types"""
        weights = {
            ProofType.TEXT: 0.3,
            ProofType.IMAGE: 0.8,
            ProofType.FILE: 0.9,
            ProofType.LINK: 0.6,
            ProofType.VIDEO: 1.0
        }
        return weights.get(proof_type, 0.5)
    
    async def _validate_single_proof(self, task_description: str, proof: ProofSubmission, completion_criteria: str, proof_number: int) -> Dict[str, Any]:
        """Validate a single proof submission"""
        try:
            # Prepare validation prompt based on proof type
            if proof.proof_type == ProofType.TEXT:
                validation_prompt = f"""
Task: {task_description}
Completion Criteria: {completion_criteria}
Proof Type: Text Description
Proof Content: {proof.content}

Evaluate this text proof for task completion. Consider:
1. Does the description demonstrate clear completion?
2. Are specific details provided?
3. Does it address the completion criteria?
4. Is there evidence of actual work done?

Provide a score from 1-10 and detailed feedback.
"""
            elif proof.proof_type == ProofType.LINK:
                validation_prompt = f"""
Task: {task_description}
Completion Criteria: {completion_criteria}
Proof Type: Link/URL
Proof Content: {proof.content}
Description: {proof.description or 'No description provided'}

Evaluate this link proof for task completion. Consider:
1. Is the URL relevant to the task?
2. Does the link demonstrate work completion?
3. Is it a credible/verifiable source?
4. Does it align with completion criteria?

Note: Cannot directly access the link, so evaluate based on URL structure and description.
Provide a score from 1-10 and detailed feedback.
"""
            elif proof.proof_type in [ProofType.IMAGE, ProofType.FILE, ProofType.VIDEO]:
                validation_prompt = f"""
Task: {task_description}
Completion Criteria: {completion_criteria}
Proof Type: {proof.proof_type.value.title()}
File Description: {proof.description or 'No description provided'}
File Metadata: {proof.metadata or {}}

Evaluate this file proof for task completion. Consider:
1. Does the file type match expected deliverables?
2. Is the description detailed and specific?
3. Does metadata suggest genuine work?
4. Does it align with completion criteria?

Note: Evaluating based on description and metadata.
Provide a score from 1-10 and detailed feedback.
"""
            else:
                validation_prompt = f"""
Task: {task_description}
Completion Criteria: {completion_criteria}
Proof Content: {proof.content}

Evaluate this proof for task completion.
Provide a score from 1-10 and detailed feedback.
"""
            
            # Get AI validation
            validation_result = await self.llm_service.validate_task_proof(
                task_description, validation_prompt, completion_criteria
            )
            
            # Extract score and feedback
            score = validation_result.get("score", 5)
            feedback = validation_result.get("feedback", "Standard validation completed")
            
            return {
                "proof_number": proof_number,
                "proof_type": proof.proof_type.value,
                "score": score,
                "feedback": feedback,
                "content_preview": proof.content[:200] + "..." if len(proof.content) > 200 else proof.content,
                "description": proof.description,
                "validation_details": validation_result
            }
        except Exception as e:
            logger.error(f"Single proof validation failed: {e}")
            return {
                "proof_number": proof_number,
                "proof_type": proof.proof_type.value,
                "score": 3,
                "feedback": f"Validation error: {str(e)}",
                "content_preview": proof.content[:200] if len(proof.content) > 200 else proof.content,
                "error": str(e)
            }
    
    def _determine_validation_status(self, final_score: float, validation_results: List[Dict]) -> str:
        """Determine overall validation status"""
        if final_score >= 8.0:
            return "excellent"
        elif final_score >= 6.5:
            return "good"
        elif final_score >= 5.0:
            return "acceptable"
        elif final_score >= 3.0:
            return "needs_improvement"
        else:
            return "insufficient"
    
    async def _generate_comprehensive_feedback(self, task_description: str, validation_results: List[Dict], final_score: float, status: str) -> str:
        """Generate comprehensive feedback using AI"""
        try:
            feedback_prompt = f"""
Task: {task_description}
Overall Validation Score: {final_score}/10
Status: {status}

Individual Proof Results:
{chr(10).join([f"Proof {r['proof_number']} ({r['proof_type']}): {r['score']}/10 - {r['feedback']}" for r in validation_results])}

Generate comprehensive, constructive feedback that:
1. Summarizes the overall submission quality
2. Highlights strengths in the proof submission
3. Identifies areas for improvement
4. Provides specific suggestions for better proof submission
5. Encourages continued progress

Make it motivational and specific to the evidence provided.
"""
            
            # Use LLM to generate feedback
            feedback_result = await self.llm_service.get_motivational_message(
                {"task": task_description}, "neutral", [], feedback_prompt
            )
            
            return feedback_result if isinstance(feedback_result, str) else "Good effort on your task completion proof!"
        except Exception as e:
            logger.error(f"Failed to generate comprehensive feedback: {e}")
            return f"Task completion evaluated with score {final_score}/10. Keep up the good work!"
    
    def _generate_recommendations(self, validation_results: List[Dict], final_score: float) -> List[str]:
        """Generate recommendations for improving proof submission"""
        recommendations = []
        
        # Analyze proof types used
        proof_types_used = set(r["proof_type"] for r in validation_results)
        low_scoring_proofs = [r for r in validation_results if r["score"] < 6]
        
        if final_score < 6:
            recommendations.append("Consider providing more detailed evidence of completion")
        
        if "image" not in proof_types_used and "video" not in proof_types_used:
            recommendations.append("Visual evidence (screenshots, photos, videos) can strengthen your proof")
        
        if "file" not in proof_types_used:
            recommendations.append("Include actual deliverables or work files when possible")
        
        if len(validation_results) == 1:
            recommendations.append("Multiple types of proof provide stronger validation")
        
        if low_scoring_proofs:
            recommendations.append("Add more specific details about what you accomplished")
        
        if final_score >= 8:
            recommendations.append("Excellent proof submission! This is a great example to follow")
        
        return recommendations

class ProofService:
    """Main proof submission service"""
    
    def __init__(self, db=None):
        self.db = db
        self.collection = None
        self.file_service = FileUploadService()
        self.validation_service = ProofValidationService()
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the proof service"""
        if self.is_initialized:
            return
        
        if not self.db:
            self.db = await get_database()
        
        self.collection = self.db.task_proofs
        self.is_initialized = True
        logger.info("Proof service initialized")
    
    async def submit_enhanced_proof(self, user_id: str, completion_data: EnhancedTaskCompletion, files: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Submit enhanced proof with files and validation"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Process file uploads if provided
            processed_files = []
            if files:
                for file_data in files:
                    file_result = await self.file_service.save_uploaded_file(
                        file_data["content"], file_data["filename"], user_id
                    )
                    if file_result["success"]:
                        processed_files.append(file_result)
                        
                        # Add file proof to completion data
                        file_proof = ProofSubmission(
                            proof_type=ProofType.FILE if file_result["category"] != "image" else ProofType.IMAGE,
                            content=file_result["relative_path"],
                            description=f"Uploaded file: {file_result['original_filename']}",
                            metadata=file_result
                        )
                        completion_data.proofs.append(file_proof)
            
            # Get task information for validation
            task = await self.db.tasks.find_one({"_id": completion_data.task_id})
            if not task:
                return {"success": False, "error": "Task not found"}
            
            # Validate proof submission
            validation_result = await self.validation_service.validate_proof_submission(
                task_description=f"{task['title']}: {task.get('description', '')}",
                proofs=completion_data.proofs,
                completion_criteria=task.get("completion_criteria", "")
            )
            
            # Create proof submission record
            proof_record = {
                "user_id": user_id,
                "task_id": completion_data.task_id,
                "block_id": completion_data.block_id,
                "completion_note": completion_data.completion_note,
                "proofs": [proof.dict() for proof in completion_data.proofs],
                "completion_confidence": completion_data.completion_confidence,
                "time_spent_minutes": completion_data.time_spent_minutes,
                "challenges_faced": completion_data.challenges_faced,
                "lessons_learned": completion_data.lessons_learned,
                "validation_result": validation_result,
                "processed_files": processed_files,
                "submitted_at": datetime.now(),
                "status": "validated" if validation_result["validation_status"] in ["excellent", "good"] else "needs_review"
            }
            
            result = await self.collection.insert_one(proof_record)
            proof_record["_id"] = str(result.inserted_id)
            
            # Update task completion status based on validation
            await self._update_task_completion_status(completion_data, validation_result)
            
            return {
                "success": True,
                "proof_id": proof_record["_id"],
                "validation": validation_result,
                "processed_files": processed_files,
                "status": proof_record["status"],
                "message": self._generate_completion_message(validation_result),
                "next_steps": self._generate_next_steps(validation_result)
            }
        except Exception as e:
            logger.error(f"Enhanced proof submission failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _update_task_completion_status(self, completion_data: EnhancedTaskCompletion, validation_result: Dict[str, Any]):
        """Update task/block completion status based on validation"""
        try:
            validation_score = validation_result.get("overall_score", 0)
            
            if completion_data.block_id:
                # Update task block
                update_data = {
                    "proof_submitted": True,
                    "proof_score": validation_score,
                    "completion_confidence": completion_data.completion_confidence,
                    "validated_at": datetime.now()
                }
                
                if validation_score >= 6.5:
                    update_data["status"] = "completed"
                    update_data["completed_at"] = datetime.now()
                else:
                    update_data["status"] = "needs_review"
                
                await self.db.task_blocks.update_one(
                    {"_id": completion_data.block_id},
                    {"$set": update_data}
                )
            else:
                # Update main task
                update_data = {
                    "proof_submitted": True,
                    "proof_score": validation_score,
                    "completion_confidence": completion_data.completion_confidence,
                    "validated_at": datetime.now()
                }
                
                if validation_score >= 6.5:
                    update_data["status"] = "completed"
                    update_data["completed_at"] = datetime.now()
                else:
                    update_data["status"] = "needs_review"
                
                await self.db.tasks.update_one(
                    {"_id": completion_data.task_id},
                    {"$set": update_data}
                )
        except Exception as e:
            logger.error(f"Failed to update task completion status: {e}")
    
    def _generate_completion_message(self, validation_result: Dict[str, Any]) -> str:
        """Generate appropriate completion message"""
        status = validation_result.get("validation_status", "acceptable")
        score = validation_result.get("overall_score", 5)
        
        if status == "excellent":
            return f"🎉 Excellent work! Your proof scored {score}/10. Task completion validated successfully!"
        elif status == "good":
            return f"✅ Great job! Your proof scored {score}/10. Well done on completing this task!"
        elif status == "acceptable":
            return f"👍 Good effort! Your proof scored {score}/10. Task completion recorded."
        elif status == "needs_improvement":
            return f"📝 Thanks for submitting! Your proof scored {score}/10. Consider adding more detail next time."
        else:
            return f"📋 Proof submitted with score {score}/10. Please review the feedback for improvements."
    
    def _generate_next_steps(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate next steps based on validation result"""
        status = validation_result.get("validation_status", "acceptable")
        
        if status in ["excellent", "good"]:
            return [
                "🎯 Move on to your next task or take a well-deserved break",
                "💫 You're building great momentum - keep it up!",
                "📈 Your proof submission skills are improving",
                "🌟 Consider sharing your approach with others"
            ]
        elif status == "acceptable":
            return [
                "✅ Task completion recorded - good work!",
                "📚 Review the feedback to improve future submissions",
                "🎯 Ready for your next challenge",
                "💪 Keep building on this progress"
            ]
        else:
            return [
                "📝 Review the detailed feedback provided",
                "🔄 Consider resubmitting with additional evidence",
                "💡 Try including visual proof (screenshots, photos)",
                "📞 Reach out if you need help with proof submission"
            ]
    
    async def get_user_proof_history(self, user_id: str, limit: int = 20, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user's proof submission history"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            query = {"user_id": user_id}
            if task_id:
                query["task_id"] = task_id
            
            cursor = self.collection.find(query).sort("submitted_at", -1).limit(limit)
            proofs = []
            
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                proofs.append(doc)
            
            return proofs
        except Exception as e:
            logger.error(f"Failed to get proof history: {e}")
            return []
    
    async def get_proof_analytics(self, user_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Get analytics on proof submission patterns"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Get proofs from specified period
            start_date = datetime.now() - timedelta(days=days_back)
            
            cursor = self.collection.find({
                "user_id": user_id,
                "submitted_at": {"$gte": start_date}
            })
            
            proofs = []
            async for doc in cursor:
                proofs.append(doc)
            
            # Calculate analytics
            total_proofs = len(proofs)
            avg_score = sum(p.get("validation_result", {}).get("overall_score", 0) for p in proofs) / max(total_proofs, 1)
            
            proof_types = {}
            validation_statuses = {}
            monthly_trend = {}
            
            for proof in proofs:
                # Proof types
                for proof_item in proof.get("proofs", []):
                    proof_type = proof_item.get("proof_type", "unknown")
                    proof_types[proof_type] = proof_types.get(proof_type, 0) + 1
                
                # Validation statuses
                status = proof.get("validation_result", {}).get("validation_status", "unknown")
                validation_statuses[status] = validation_statuses.get(status, 0) + 1
                
                # Monthly trend
                month_key = proof["submitted_at"].strftime("%Y-%m")
                monthly_trend[month_key] = monthly_trend.get(month_key, 0) + 1
            
            return {
                "success": True,
                "period_days": days_back,
                "summary": {
                    "total_proofs_submitted": total_proofs,
                    "average_validation_score": round(avg_score, 2),
                    "proof_types_used": len(proof_types),
                    "most_used_proof_type": max(proof_types.items(), key=lambda x: x[1])[0] if proof_types else None
                },
                "proof_type_breakdown": proof_types,
                "validation_status_breakdown": validation_statuses,
                "monthly_trend": monthly_trend,
                "recommendations": [
                    f"Your average validation score is {round(avg_score, 1)}/10",
                    "Try using multiple proof types for stronger validation" if len(proof_types) <= 2 else "Great variety in proof types!",
                    "Visual evidence (images/videos) typically score higher" if "image" not in proof_types and "video" not in proof_types else "Good use of visual evidence!"
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get proof analytics: {e}")
            return {"success": False, "error": str(e)}

# Global proof service instance
proof_service = ProofService()
