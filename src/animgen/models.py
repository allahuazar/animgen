from pydantic import BaseModel


class QuizItem(BaseModel):
    question: str
    answer: str


class Lesson(BaseModel):
    title: str
    subject: str
    grade: str
    summary: str
    key_points: list[str]
    formula: str
    quiz: list[QuizItem]
