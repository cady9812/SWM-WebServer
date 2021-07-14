from app import db

# class Question(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     subject = db.Column(db.String(200), nullable=False)
#     content = db.Column(db.Text(), nullable=False)
#     create_date = db.Column(db.DateTime(), nullable=False)

# class Answer(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     question_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete='CASCADE')) # CASCADE 삭제 연동 설정; 질문 삭제하면 딸린 답변도 삭제된다.
#     question = db.relationship('Question', backref=db.backref('answer_set'))
#     content = db.Column(db.Text(), nullable=False)
#     create_date = db.Column(db.DateTime(), nullable=False)

class Attack(db.Model):
    attackId = db.Column(db.Integer, primary_key=True)
    attackFileRoute = db.Column(db.Text(), nullable=False)
    program = db.Column(db.String(200), nullable=False)
    version = db.Column(db.String(20), nullable=False)
    port = db.Column(db.Integer, nullable=False)
