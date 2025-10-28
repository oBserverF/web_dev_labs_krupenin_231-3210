import random
from functools import lru_cache
from flask import Flask, render_template, abort, request, make_response
from faker import Faker

fake = Faker()

app = Flask(__name__)
application = app

images_ids = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
              '2d2ab7df-cdbc-48a8-a936-35bba702def5',
              '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
              'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
              'cab5b7f2-774e-4884-a200-0c0180fa777f']

def generate_comments(replies=True):
    comments = []
    for _ in range(random.randint(1, 3)):
        comment = { 'author': fake.name(), 'text': fake.text() }
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments

def generate_post(i):
    return {
        'title': 'Заголовок поста',
        'text': fake.paragraph(nb_sentences=100),
        'author': fake.name(),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'image_id': f'{images_ids[i]}.jpg',
        'comments': generate_comments()
    }

@lru_cache
def posts_list():
    return sorted([generate_post(i) for i in range(5)], key=lambda p: p['date'], reverse=True)


def validate_phone_number(phone):

    alphabet = "0123456789()+-. "
    cleaned_number = "".join(c for c in phone if c.isdigit())
    
    if any(c not in alphabet for c in phone):
        return False, "Недопустимый ввод. В номере телефона встречаются недопустимые символы."
    
    if cleaned_number.startswith(('7', '8')):
        if len(cleaned_number) != 11:
            return False, "Недопустимый ввод. Неверное количество цифр."
    else:
        if len(cleaned_number) != 10:
            return False, "Недопустимый ввод. Неверное количество цифр."
    
    return True, format_phone_number(cleaned_number)

def format_phone_number(cleaned_number):
    formatted = f"8-{cleaned_number[-10:-7]}-{cleaned_number[-7:-4]}-{cleaned_number[-4:-2]}-{cleaned_number[-2:]}"
    return formatted

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/args')
def args():
    return render_template('args.html')

@app.route('/headers')
def headers():
    return render_template('headers.html')

@app.route('/cookies')
def cookies():
    resp = make_response(render_template('cookies.html'))
    if 'bestProgrammer' not in request.cookies:
        resp.set_cookie('bestProgrammer', "VladimirK")
    else:
        resp.delete_cookie('bestProgrammer')
    return resp

@app.route('/form', methods = ['GET', 'POST'])
def form():
    return render_template('form.html')

@app.route('/phone_form', methods = ['GET', 'POST'])
def phone_form():
    error = None
    formatted_number = None
    
    if request.method == 'POST':
        phone = request.form.get('phone', '')
        is_valid, result = validate_phone_number(phone)
        
        if is_valid:
            formatted_number = result
        else:
            error = result

    return render_template('phone_form.html', error=error, formatted_number=formatted_number)

@app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts=posts_list())

@app.route('/posts/<int:index>')
def post(index):
    posts = posts_list()

    if index < 0 or index >= len(posts):
        abort(404)

    p = posts[index]
    return render_template('post.html', title=p['title'], post=p)

@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')
