# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Chat, Conversation
from forms import LoginForm, SignupForm, ChatForm
import uuid
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask_migrate import Migrate
import markdown
from bleach import clean
from markupsafe import Markup
from sqlalchemy import text  # Import the text object

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///chat.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-pro-exp-02-05')


# Markdown 필터 정의
@app.template_filter('markdown')
def render_markdown(text):
    allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'code', 'pre', 'h1', 'h2', 'h3',
                    'h4', 'h5', 'h6', 'blockquote', 'hr']
    allowed_attributes = {'*': ['class', 'id', 'style'], 'a': ['href', 'title', 'rel']}
    html = markdown.markdown(text, extensions=['extra', 'nl2br', 'codehilite'])
    cleaned_html = clean(html, tags=allowed_tags, attributes=allowed_attributes, strip=True)
    return Markup(cleaned_html)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def generate_guest_id():
    return str(uuid.uuid4())


def get_or_create_conversation(user_id=None, guest_id=None):
    """
    Gets the current conversation or creates a new one if none exists.
    """
    if user_id:
        conversation = Conversation.query.filter_by(user_id=user_id).order_by(
            Conversation.created_at.desc()).first()
    else:
        conversation = Conversation.query.filter_by(guest_id=guest_id).order_by(
            Conversation.created_at.desc()).first()

    if not conversation:
        conversation = Conversation(user_id=user_id, guest_id=guest_id)
        db.session.add(conversation)
        db.session.commit()
    return conversation


def get_conversations(user_id=None, guest_id=None):
    """
    Fetches all conversations for a user or guest.
    """
    if user_id:
        return Conversation.query.filter_by(user_id=user_id).order_by(
            Conversation.created_at.desc()).all()
    else:
        return Conversation.query.filter_by(guest_id=guest_id).order_by(
            Conversation.created_at.desc()).all()


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if form.agree.data:
            hashed_password = generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('회원가입이 완료되었습니다. 로그인해주세요.')
            return redirect(url_for('login'))
        else:
            flash('약관에 동의해야 합니다.')
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('아이디 또는 비밀번호가 잘못되었습니다.')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ChatForm()
    show_terms_popup = False
    scroll_to_bottom = False
    guest_id = None
    conversations =# Initialize conversations here
    chat_history =
    current_conversation_id = request.args.get('conversation_id')

    if current_user.is_authenticated:
        conversations = Conversation.query.filter_by(
            user_id=current_user.id).order_by(Conversation.created_at.desc()).all()
    else:
        guest_id = request.cookies.get('guest_id')
        if not guest_id:
            guest_id = generate_guest_id()
            show_terms_popup = True
        conversations = Conversation.query.filter_by(
            guest_id=guest_id).order_by(Conversation.created_at.desc()).all()

    # 새 채팅 시작 (POST 요청이면서 새 채팅 버튼이 눌린 경우)
    if request.method == 'POST' and request.form.get('new_chat'):
        if current_user.is_authenticated:
            new_conversation = Conversation(user_id=current_user.id)
        else:
            new_conversation = Conversation(guest_id=guest_id)
        db.session.add(new_conversation)
        db.session.commit()
        return redirect(url_for('index', conversation_id=new_conversation.id))  # 새 대화 ID로 리다이렉트

    # 선택된 대화 로드
    if current_conversation_id:
        if current_user.is_authenticated:
            current_conversation = Conversation.query.filter_by(
                id=current_conversation_id, user_id=current_user.id).first()
        else:
            current_conversation = Conversation.query.filter_by(
                id=current_conversation_id, guest_id=guest_id).first()

        if not current_conversation:  # 현재 대화가 없으면(삭제되었거나)
            flash("선택한 대화가 존재하지 않습니다.")
            return redirect(url_for('index'))

        chat_history = Chat.query.filter_by(
            conversation_id=current_conversation.id).order_by(Chat.timestamp.asc()).all()
    else:
        # Ensure conversations is assigned even if current_conversation_id is not present
        if current_user.is_authenticated:
            conversations = Conversation.query.filter_by(user_id=current_user.id).order_by(
                Conversation.created_at.desc()).all()
        else:
            guest_id = request.cookies.get('guest_id')
            if guest_id:
                conversations = Conversation.query.filter_by(guest_id=guest_id).order_by(
                    Conversation.created_at.desc()).all()
            else:
                conversations =# Or handle this case as needed

    # 대화가 없을 경우 새 대화 생성 (최초 접속 시 또는 대화 목록이 없을 때)
    if not conversations:
        if current_user.is_authenticated:
            new_conversation = Conversation(user_id=current_user.id)
        else:
            new_conversation = Conversation(guest_id=guest_id)

        db.session.add(new_conversation)
        db.session.commit()
        return redirect(url_for('index', conversation_id=new_conversation.id))

    # 폼 제출 처리 (메시지 전송)
    if form.validate_on_submit() and current_conversation_id:  # current_conversation_id 필수
        if current_user.is_authenticated or request.form.get('terms_agreed') == 'true':
            user_message = form.message.data
            form.message.data = ""

            # 대화 기록 가져오기 및 Gemini API 호출
            history =
            for chat in chat_history:
                history.append({'role': 'user', 'parts': [chat.message]})
                history.append({'role': 'model', 'parts': [chat.response]})

            history.append({'role': 'user', 'parts': [user_message]})

            try:
                chat_session = model.start_chat(history=history)
                response = chat_session.send_message(user_message)
                gemini_response = response.text

            except Exception as e:
                gemini_response = f"Error: {str(e)}"

            # Chat 객체 생성 및 저장
            if current_user.is_authenticated:
                chat_entry = Chat(conversation_id=current_conversation_id,
                                  user_id=current_user.id,
                                  message=user_message, response=gemini_response)
            else:
                chat_entry = Chat(conversation_id=current_conversation_id,
                                  guest_id=guest_id,
                                  message=user_message, response=gemini_response)

            db.session.add(chat_entry)
            db.session.commit()
            scroll_to_bottom = True  # DB에 저장 후

        elif not current_user.is_authenticated:  # 비회원 + 약관 미동의
            flash('채팅을 시작하려면 약관에 동의해야 합니다.')
            show_terms_popup = True

    # 템플릿 렌더링 및 응답
    response = make_response(render_template('index.html', form=form,
                                             conversations=conversations,
                                             chat_history=chat_history,
                                             show_terms_popup=show_terms_popup,
                                             scroll_to_bottom=scroll_to_bottom,
                                             current_conversation_id=current_conversation_id))

    if not current_user.is_authenticated:
        if not request.cookies.get('guest_id'):
            response.set_cookie('guest_id', guest_id)
        if request.method == 'POST' and request.form.get('terms_agreed') == 'true':
            response.set_cookie('terms_agreed', 'true', max_age=365 * 24 * 60 * 60)

    return response


@app.route('/delete_conversation/<int:conversation_id>', methods=['POST'])
@login_required
def delete_conversation(conversation_id):
    if current_user.is_authenticated:
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user.id).first()
    else:
        guest_id = request.cookies.get('guest_id')
        conversation = Conversation.query.filter_by(id=conversation_id, guest_id=guest_id).first()

    if conversation:
        db.session.delete(conversation)
        db.session.commit()
        flash("대화가 삭제되었습니다.")
    else:
        flash("대화를 찾을 수 없습니다.")
    return redirect(url_for('index'))  # 삭제 후에는 대화목록으로 redirect


@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('관리자 권한이 없습니다.')
        return redirect(url_for('index'))

    users = User.query.all()
    guest_chats = db.session.query(Chat.guest_id).filter(Chat.user_id == None).group_by(
        Chat.guest_id).all()

    return render_template('admin.html', users=users, guest_chats=guest_chats)


@app.route('/admin/user/<int:user_id>')
@login_required
def admin_user_detail(user_id):
    if not current_user.is_admin:
        return "Unauthorized", 403
    user = User.query.get_or_404(user_id)
    chats = Chat.query.filter_by(user_id=user.id).order_by(Chat.timestamp.asc()).all()
    return render_template('admin_user_detail.html', user=user, chats=chats)


@app.route('/admin/guest/<guest_id>')
@login_required
def admin_guest_detail(guest_id):
    if not current_user.is_admin:
        return "Unauthorized", 403
    guest_chats = Chat.query.filter_by(guest_id=guest_id).order_by(Chat.timestamp.asc()).all()
    return render_template('admin_guest_detail.html', guest_id=guest_id, chats=guest_chats)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)