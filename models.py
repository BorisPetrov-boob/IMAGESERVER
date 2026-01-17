from dataclasses import dataclass  
from datetime import datetime
from typing import Optional


@dataclass
class Image:
    id: Optional[int] = None
    filename: str = ''
    original_name: str = ''
    size: int = 0
    upload_time: Optional[datetime] = datetime.now()
    file_type: str = ''
    
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "original_name": self.original_name,
            "size": self.size,
            "upload_time": self.upload_time.isoformat() if self.upload_time else None,
            "file_type": self.file_type,
            "url": f"images/{self.filename}"
        }