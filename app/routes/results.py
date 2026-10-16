from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import ExamResult
from ..schemas import ExamResultCreate, ExamResultUpdate, ExamResultResponse

router = APIRouter(
    prefix='/results',
    tags=['Results']
)

@router.post('/', response_model=ExamResultResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: ExamResultCreate, db: Session = Depends(get_db)):
    db_item = ExamResult(**item.model_dump())
    db.add(db_item)
    try:
        db.commit()
        db.refresh(db_item)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_item

@router.get('/', response_model=list[ExamResultResponse])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(ExamResult).offset(skip).limit(limit).all()
    return items

@router.get('/{item_id}', response_model=ExamResultResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ExamResult).filter(ExamResult.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail='Item not found')
    return db_item

@router.put('/{item_id}', response_model=ExamResultResponse)
def update_item(item_id: int, item: ExamResultUpdate, db: Session = Depends(get_db)):
    db_item = db.query(ExamResult).filter(ExamResult.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail='Item not found')
    
    update_data = item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
        
    try:
        db.commit()
        db.refresh(db_item)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_item

@router.delete('/{item_id}')
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ExamResult).filter(ExamResult.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail='Item not found')
    db.delete(db_item)
    db.commit()
    return {'message': 'Item deleted successfully'}
