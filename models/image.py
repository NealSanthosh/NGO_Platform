from bson.objectid import ObjectId
from extensions import mongo
from datetime import datetime
import base64

class Image:
    def __init__(self, filename, content_type, data, uploader_id, **kwargs):
        self.filename = filename
        self.content_type = content_type
        self.data = data  # base64 encoded data
        self.uploader_id = ObjectId(uploader_id)
        self.created_at = datetime.utcnow()
        self.alt_text = kwargs.get('alt_text', '')
        self.category = kwargs.get('category', 'general')  # profile, banner, campaign, organisation
    
    def save(self):
        image_data = {
            'filename': self.filename,
            'content_type': self.content_type,
            'data': self.data,
            'uploader_id': self.uploader_id,
            'created_at': self.created_at,
            'alt_text': self.alt_text,
            'category': self.category
        }
        result = mongo.db.images.insert_one(image_data)
        self._id = result.inserted_id
        return self
    
    @staticmethod
    def get_by_id(image_id):
        try:
            image_data = mongo.db.images.find_one({'_id': ObjectId(image_id)})
            if image_data:
                image = Image.__new__(Image)
                image.__dict__.update(image_data)
                return image
        except:
            pass
        return None
    
    @staticmethod
    def create_from_file(file, uploader_id, **kwargs):
        if file and file.filename:
            file_data = file.read()
            encoded_data = base64.b64encode(file_data).decode('utf-8')
            
            image = Image(
                filename=file.filename,
                content_type=file.content_type,
                data=encoded_data,
                uploader_id=uploader_id,
                **kwargs
            )
            return image.save()
        return None
    
    def get_data_url(self):
        return f"data:{self.content_type};base64,{self.data}"
