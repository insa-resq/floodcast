from pydantic import BaseModel, ConfigDict

class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    mail: str
    ip: str
    #segments_ids: list[int]
    #departements: list[int]
