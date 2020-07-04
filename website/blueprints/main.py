from flask import flash, redirect, Blueprint, render_template, request, abort, url_for
from website.extensions import limiter, db
from website.forms.main import QuestionForm, AnswerForm
from website.models import Question, Answer
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
    return render_template('main/about.html')


@main_bp.route('/question/new', methods=['GET', 'POST'])
@login_required
@limiter.limit("2 per second")
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

    return render_template('/main/question_new.html', form=form)


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
