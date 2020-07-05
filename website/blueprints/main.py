from flask import flash, redirect, Blueprint, render_template, request, abort, url_for
from website.extensions import limiter, db
from website.forms.main import QuestionForm, AnswerForm, CommentForm
from website.models import Question, Answer, Comment
from website.models import UserCommon as User
from flask_login import current_user, login_required
from website.decorators import confirm_required, permission_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@limiter.limit("2 per second")
def index():

    questions = Question.query.order_by(Question.timestamp.desc()).all()

    return render_template('main/index.html', questions=questions)


@main_bp.route('/about')
@limiter.limit("2 per minute")
#@limiter.limit("2 per second" , key_func=lambda: current_user.username)
def about():
    url = url_for('auth.check', token='1234', _external=True)
    flash("the auth.check: " + url)
    return render_template('main/about.html')


@main_bp.route('/question/new', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def question_new():
    form = QuestionForm()
    if form.validate_on_submit():
        question = form.question.data

        author = current_user._get_current_object()
        q = Question(question=question, author=author)
        db.session.add(q)
        db.session.commit()
        flash("Done creating new question...")
        return redirect(url_for('main.question_detail', question_id=q.id))

    return render_template('/main/question.html', form=form)


@main_bp.route('/question/edit/<int:question_id>', methods=['GET','POST'])
@login_required
@limiter.limit("10 per minute")
def question_edit(question_id):
    question = Question.query.filter_by(id=question_id).first()
    if not question or current_user != question.author:
        flash("question not found or your are not the author...")
        return redirect(url_for('main.question_detail', question_id=question_id))

    else:
        form = QuestionForm()
        if form.validate_on_submit():
            question.question = form.question.data
            db.session.commit()
            flash("done chaning the question...")
            return redirect(url_for('main.question_detail', question_id=question_id))

        form.question.data = question.question
    return render_template('main/question.html', form=form)

@main_bp.route('/question/delete/<int:question_id>', methods=['POST'])
@login_required
@limiter.limit("10 per minute")
def question_delete(question_id):
    question = Question.query.filter_by(id=question_id).first()
    if not question or current_user != question.author:
        flash("question not found or you are not the author...")
        return redirect(url_for('main.question_detail', question_id=question_id))
    else:
        db.session.delete(question)
        db.session.commit()

    return redirect(url_for('main.index'))


@main_bp.route('/question/detail/<int:question_id>')
@limiter.limit("5 per second")
def question_detail(question_id):
    q = Question.query.get_or_404(question_id)
    if q is None:
        flash("page not found...")
        return redirect(url_for('main.index'))

    #ans = Answer.query.filter_by(question_id=question_id).order_by(Answer.timestamp.desc()).all()
    ans = Answer.query.filter_by(question_id=question_id).all()

    return render_template('main/question_detail.html', question=q, answers=ans)


@main_bp.route('/answer/new/<int:question_id>', methods=['GET', 'POST'])
@login_required
@limiter.limit("5 per minute")
def answer_new(question_id):
    answered = Answer.query.filter_by(author=current_user, question_id=question_id).first()

    if answered:
        flash("already answered the question, please reply to your original answer...")
        return redirect(url_for('main.question_detail', question_id=question_id))

    form = AnswerForm()
    if form.validate_on_submit():
        answer = form.answer.data
        a = Answer(answer=answer, author=current_user, question_id=question_id)

        db.session.add(a)
        db.session.commit()
        flash("done answering the question...")
        return redirect(url_for('main.question_detail', question_id=question_id)+"#answer")

    #return redirect(url_for('main/answer_new', form=form))
    return render_template('main/answer_new.html', form=form)

#FIXME: need to figure out how to change the 'last_edit_timestamp' everytime we edit it
@main_bp.route('/answer/edit/<int:question_id>/<int:answer_id>', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def answer_edit( question_id, answer_id):
    ans = Answer.query.filter_by(author=current_user, id=answer_id).first()
    if not ans or current_user != ans.author:
        flash("failed to append to answer, answer not found, or the answer doesn't belong to you...")
        return redirect(url_for('main.question_detail', question_id=question_id)+'#answer')

    form = AnswerForm()
    if form.validate_on_submit():
        ans.answer = form.answer.data
        db.session.commit()
        flash("Done editing your answer...")
        return redirect(url_for('main.question_detail', question_id=question_id)+"#answer")

    form.answer.data = ans.answer
    return render_template('/main/answer_edit.html', form=form)

@main_bp.route('/answer/delete/<int:question_id>/<int:answer_id>', methods=['POST'])
@login_required
@limiter.limit("2 per minute")
def answer_delete(question_id, answer_id):
    ans = Answer.query.filter_by(id=answer_id, author=current_user).first()
    #check permission or if the answer even belong to current user
    if not ans or current_user != ans.author:
        flash("delete answer failed: answer not found or it doesn't belong to you...")

    else:

        db.session.delete(ans)
        db.session.commit()
        flash("deleted your question...", "warning")
    return redirect(url_for('main.question_detail', question_id=question_id)+"#answer")



"""
@main_bp.route('/answer/reply/<int:question_id>/<int:answer_id>', methods=['GET', 'POST'])
@login_required
@limiter.limit("5 per minute")
def answer_reply(answer_id, question_id):
    ans = Answer.query.get_or_404(answer_id)
    form = AnswerForm()
    if form.validate_on_submit():
        reply= form.answer.data
        answer_reply = Answer(answer=reply, author=current_user, replied_id=answer_id)
        db.session.add(answer_reply)
        db.session.commit()
        flash("reply success...")
        return redirect(url_for('main.question_detail', question_id=question_id))

    return render_template('/main/answer_reply.html', form=form)
    
"""


@main_bp.route('/comment/new/<int:question_id>/<int:answer_id>', methods=['GET', 'POST'])
@login_required
@limiter.limit("30 per minute")
def comment_new(question_id, answer_id):

    ans = Answer.query.filter_by(id=answer_id).first()
    if not ans:
        flash("answer not found...")
        return redirect(url_for('main.question_detail', question_id=question_id)+"#answer")

    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(comment=form.comment.data, author=current_user, answer_id=answer_id)
        db.session.add(comment)
        db.session.commit()
        flash("done commenting...")
        return redirect(url_for('main.question_detail', question_id=question_id)+"#answer")

    return render_template('main/comment.html', form=form)

@main_bp.route('/comment/delete/<int:question_id>/<int:comment_id>', methods=['POST'])
@login_required
@limiter.limit("2 per minute")
def comment_delete(question_id, comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment or current_user != comment.author:
        flash("comment delete failed, comment not found, or the comment doesn't belong to you...")
        return redirect(url_for('main.question_detail', question_id=question_id)+"#answer")

    else:
        db.session.delete(comment)
        db.session.commit()
        flash("delete your comment...")

    return redirect(url_for('main.question_detail', question_id=question_id)+"#answer")





@main_bp.route("/search", methods=['POST'])
def search():

    """
    keyword = request.form.get('keyword', "NONE")
    if keyword:
        flash("get keyword: " + keyword)
    else:
        flash("empty...", "warning")
    """
    flash("NOT IMPLEMENTED YET...", "warning")

    return redirect(url_for('main.index'))


@main_bp.route('/test/permission/visit')
@permission_required('VISIT')
def test_permission_visit():
    flash("you have the permission: VISIT")
    return redirect(url_for('main.index'))


@main_bp.route('/test/permission/confirm')
@confirm_required
def test_permission_confirm():
    flash("you are confirmed")
    return redirect(url_for('main.index'))


@main_bp.route('/test/permission/moderate')
@permission_required('MODERATE')
def test_permission_moderate():
    flash("you have the permission: moderate")
    return redirect(url_for('main.index'))
