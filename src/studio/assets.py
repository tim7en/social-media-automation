from typing import Dict, Any, List, Optional
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
import hashlib

class AssetManager:
    """Manage content assets (images, videos, audio files)"""
    
    def __init__(self, assets_dir: str = "assets"):
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.images_dir = self.assets_dir / "images"
        self.videos_dir = self.assets_dir / "videos"
        self.audio_dir = self.assets_dir / "audio"
        self.thumbnails_dir = self.assets_dir / "thumbnails"
        
        for dir_path in [self.images_dir, self.videos_dir, self.audio_dir, self.thumbnails_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.assets_registry = {}
        
    def upload_asset(self, file_path: str, asset_type: str, metadata: Dict[str, Any] = None) -> str:
        """Upload and register an asset"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate asset ID
        asset_id = str(uuid.uuid4())
        
        # Determine file extension
        file_extension = Path(file_path).suffix
        
        # Determine destination directory
        if asset_type == "image":
            dest_dir = self.images_dir
        elif asset_type == "video":
            dest_dir = self.videos_dir
        elif asset_type == "audio":
            dest_dir = self.audio_dir
        else:
            dest_dir = self.assets_dir
        
        # Copy file to assets directory
        dest_path = dest_dir / f"{asset_id}{file_extension}"
        shutil.copy2(file_path, dest_path)
        
        # Calculate file hash for deduplication
        file_hash = self._calculate_file_hash(dest_path)
        
        # Register asset
        asset_info = {
            "id": asset_id,
            "type": asset_type,
            "filename": Path(file_path).name,
            "path": str(dest_path),
            "size": os.path.getsize(dest_path),
            "hash": file_hash,
            "uploaded_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        # Add type-specific metadata
        if asset_type == "image":
            asset_info.update(self._get_image_metadata(dest_path))
        elif asset_type == "video":
            asset_info.update(self._get_video_metadata(dest_path))
        elif asset_type == "audio":
            asset_info.update(self._get_audio_metadata(dest_path))
        
        self.assets_registry[asset_id] = asset_info
        
        return asset_id
    
    def get_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Get asset information"""
        return self.assets_registry.get(asset_id)
    
    def list_assets(self, asset_type: str = None, tags: List[str] = None) -> List[Dict[str, Any]]:
        """List assets with optional filtering"""
        assets = list(self.assets_registry.values())
        
        if asset_type:
            assets = [a for a in assets if a["type"] == asset_type]
        
        if tags:
            assets = [a for a in assets if any(tag in a.get("metadata", {}).get("tags", []) for tag in tags)]
        
        return assets
    
    def delete_asset(self, asset_id: str) -> bool:
        """Delete an asset"""
        if asset_id not in self.assets_registry:
            return False
        
        asset = self.assets_registry[asset_id]
        
        # Delete file
        try:
            os.unlink(asset["path"])
        except FileNotFoundError:
            pass  # File already deleted
        
        # Delete thumbnail if exists
        thumbnail_path = self.thumbnails_dir / f"{asset_id}_thumb.jpg"
        if thumbnail_path.exists():
            os.unlink(thumbnail_path)
        
        # Remove from registry
        del self.assets_registry[asset_id]
        
        return True
    
    def update_asset_metadata(self, asset_id: str, metadata: Dict[str, Any]) -> bool:
        """Update asset metadata"""
        if asset_id not in self.assets_registry:
            return False
        
        self.assets_registry[asset_id]["metadata"].update(metadata)
        self.assets_registry[asset_id]["updated_at"] = datetime.utcnow().isoformat()
        
        return True
    
    def create_thumbnail(self, asset_id: str, size: tuple = (300, 300)) -> Optional[str]:
        """Create thumbnail for an asset"""
        asset = self.get_asset(asset_id)
        if not asset:
            return None
        
        thumbnail_path = self.thumbnails_dir / f"{asset_id}_thumb.jpg"
        
        try:
            if asset["type"] == "image":
                return self._create_image_thumbnail(asset["path"], thumbnail_path, size)
            elif asset["type"] == "video":
                return self._create_video_thumbnail(asset["path"], thumbnail_path, size)
            else:
                return None
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return None
    
    def find_similar_assets(self, asset_id: str, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Find assets similar to the given asset"""
        target_asset = self.get_asset(asset_id)
        if not target_asset:
            return []
        
        similar_assets = []
        target_hash = target_asset["hash"]
        
        for aid, asset in self.assets_registry.items():
            if aid == asset_id:
                continue
            
            # Simple hash comparison for exact duplicates
            if asset["hash"] == target_hash:
                similar_assets.append({**asset, "similarity": 1.0})
            
            # For images, could implement perceptual hashing
            # For videos, could compare frame hashes
            # For now, just filename similarity
            elif asset["type"] == target_asset["type"]:
                filename_similarity = self._calculate_filename_similarity(
                    target_asset["filename"], asset["filename"]
                )
                if filename_similarity >= threshold:
                    similar_assets.append({**asset, "similarity": filename_similarity})
        
        return sorted(similar_assets, key=lambda x: x["similarity"], reverse=True)
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        total_size = 0
        type_stats = {}
        
        for asset in self.assets_registry.values():
            asset_type = asset["type"]
            asset_size = asset["size"]
            
            total_size += asset_size
            
            if asset_type not in type_stats:
                type_stats[asset_type] = {"count": 0, "size": 0}
            
            type_stats[asset_type]["count"] += 1
            type_stats[asset_type]["size"] += asset_size
        
        return {
            "total_assets": len(self.assets_registry),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "by_type": type_stats,
            "storage_path": str(self.assets_dir)
        }
    
    def cleanup_orphaned_files(self) -> List[str]:
        """Remove files not in registry"""
        orphaned_files = []
        
        for root, dirs, files in os.walk(self.assets_dir):
            for file in files:
                file_path = Path(root) / file
                
                # Check if file is registered
                is_registered = any(
                    asset["path"] == str(file_path) 
                    for asset in self.assets_registry.values()
                )
                
                if not is_registered and not file.startswith('.'):
                    orphaned_files.append(str(file_path))
                    try:
                        os.unlink(file_path)
                    except Exception as e:
                        print(f"Error deleting orphaned file {file_path}: {e}")
        
        return orphaned_files
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _get_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract image metadata"""
        try:
            from PIL import Image
            
            with Image.open(file_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode
                }
        except Exception:
            return {}
    
    def _get_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract video metadata"""
        # Mock implementation - in production would use ffprobe
        return {
            "duration": 0,
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "format": "mp4"
        }
    
    def _get_audio_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract audio metadata"""
        # Mock implementation - in production would use audio libraries
        return {
            "duration": 0,
            "sample_rate": 44100,
            "channels": 2,
            "format": "mp3"
        }
    
    def _create_image_thumbnail(self, source_path: str, thumb_path: Path, size: tuple) -> str:
        """Create image thumbnail"""
        try:
            from PIL import Image
            
            with Image.open(source_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(thumb_path, "JPEG")
            
            return str(thumb_path)
        except Exception:
            return None
    
    def _create_video_thumbnail(self, source_path: str, thumb_path: Path, size: tuple) -> str:
        """Create video thumbnail"""
        # Mock implementation - in production would use ffmpeg
        try:
            from PIL import Image
            
            # Create a placeholder thumbnail
            img = Image.new('RGB', size, color='gray')
            img.save(thumb_path, "JPEG")
            
            return str(thumb_path)
        except Exception:
            return None
    
    def _calculate_filename_similarity(self, filename1: str, filename2: str) -> float:
        """Calculate similarity between filenames"""
        # Simple Jaccard similarity based on character sets
        set1 = set(filename1.lower())
        set2 = set(filename2.lower())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0