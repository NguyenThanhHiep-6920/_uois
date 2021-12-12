import types
from sqlalchemy import Column, String, BigInteger, Integer, DateTime, ForeignKey, Sequence
from sqlalchemy.orm import relationship, backref
import datetime

from models.BaseModel import BaseModel

class SubjectModel(BaseModel):
    __tablename__ = 'subjects'
    
    id = Column(BigInteger, Sequence('all_id_seq'), primary_key=True)
    name = Column(String)
    
    lastchange = Column(DateTime, default=datetime.datetime.now)
    externalId = Column(String, index=True)