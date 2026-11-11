from flask import Flask, render_template, request, abort, jsonify, redirect, url_for, flash, session   # 위 도구들에 더해, 다른 주소로 보내는 도구(redirect), 주소 만드는 도구(url_for), '한 번만 보이는 안내'를 남기는 도구(flash), '내 수첩'(session)도 가져와요
from data import load_classes, get_class, get_categories, filter_and_sort, get_stats   # data.py 의 함수들을 가져와요
import os                        # 컴퓨터의 환경 값(.env 에서 읽은 값 포함)을 읽는 도구를 가져와요
from pathlib import Path         # 파일 위치를 다루는 도구를 가져와요
from dotenv import load_dotenv   # .env 파일의 값을 환경 값으로 읽어 오는 도구를 가져와요
import db                        # db.py (후기를 SQLite 에 저장·조회하는 파일)를 가져와요

load_dotenv(Path(__file__).resolve().parent / ".env")   # app.py 옆의 .env 를 읽어요 (어느 폴더에서 실행해도 찾아요. .env 가 없으면 그냥 넘어가요)

app = Flask(__name__)            # 내 웹 서비스(앱) 하나를 만들어요
app.secret_key = os.environ.get("SECRET_KEY")   # 쿠키(안내 글, 찜 목록)에 '도장'을 찍는 비밀 열쇠예요. 코드가 아니라 .env 에서 가져와요
if not app.secret_key:           # 열쇠가 비어 있으면
    raise RuntimeError("SECRET_KEY 가 없어요. .env.example 을 .env 로 복사하고 SECRET_KEY 값을 채워 주세요.")   # 약한 기본값으로 몰래 돌지 않고, 이유를 알려 주며 멈춰요
db.init_db()                     # 서버가 켜질 때 reviews 표를 준비해요 (이미 있으면 그대로 둬요)
app.json.ensure_ascii = False    # JSON에서 한글이 \uXXXX 로 깨지지 않게, 한글 그대로 내보내요
app.json.sort_keys = False       # JSON 항목을 가나다순으로 섞지 않고, 내가 적은 순서대로 보여 줘요


def wished_ids():                # 내가 찜한 클래스 번호들을 꺼내는 도우미 함수예요
    return session.get("wishlist", [])   # 세션 수첩의 'wishlist' 칸을 읽어요 (한 번도 찜 안 했으면 빈 목록)


@app.context_processor           # 모든 화면에 아래 값을 자동으로 넘겨 줘요 (화면마다 따로 넘기지 않아도 돼요)
def inject_wish_count():         # 메뉴의 '찜 목록 (개수)' 에 쓸 값을 만들어요
    return {"wish_count": len(wished_ids())}   # 화면에서 {{ wish_count }} 로 쓸 수 있어요


@app.template_filter("won")      # 템플릿에서 {{ 값 | won }} 으로 쓸 수 있는 '원 표시 도구'를 등록해요
def won(value):                  # 숫자를 받아서
    return f"{value:,.0f}원"      # 25000 → 25,000원 처럼 콤마를 넣고 '원'을 붙여요


@app.route("/")                  # 누가 주소 / 로 들어오면 아래 함수를 실행해요
def home():                      # 홈 화면을 맡을 함수예요
    classes = load_classes()     # 클래스 목록을 읽어 와요
    return render_template(      # 홈 화면을 만들어서 돌려줘요
        "home.html",
        total=len(classes),                   # 전체 개수를 화면에 넘겨요
        categories=get_categories(classes),   # 카테고리 목록을 화면에 넘겨요
    )


@app.route("/classes")           # 누가 주소 /classes 로 들어오면 아래 함수를 실행해요
def class_list():                # 클래스 목록 화면을 맡을 함수예요
    category = request.args.get("category", "")   # 주소의 ?category= 값을 읽어요 (없으면 빈 글자)
    sort = request.args.get("sort", "")           # 주소의 ?sort= 값을 읽어요 (없으면 빈 글자)
    all_classes = load_classes()                  # 클래스 전체를 읽어 와요
    shown = filter_and_sort(all_classes, category, sort)   # 조건에 맞게 거르고 정렬해요
    return render_template(      # 목록 화면을 만들어서 돌려줘요
        "classes.html",
        classes=shown,                            # 보여 줄 클래스들
        categories=get_categories(all_classes),   # 상자에 채울 카테고리 목록
        category=category,                        # 지금 골라진 카테고리 (상자에 표시용)
        sort=sort,                                # 지금 골라진 정렬 (상자에 표시용)
    )


@app.route("/class/<int:class_id>", methods=["GET", "POST"])   # 숫자를 class_id 로 받아요. 보기(GET)와 후기 저장(POST)을 둘 다 받아요
def class_detail(class_id):      # 상세 화면을 맡을 함수예요
    found = get_class(class_id)  # 그 번호의 클래스를 찾아요 (없으면 None)
    if found is None:            # 못 찾았다면
        abort(404)               # 진짜 404 오류를 일으켜요 (아래 not_found 함수가 받아요)

    error = None                 # 틀린 점이 있으면 여기에 이유를 적어요 (없으면 None)
    form = {"nickname": "", "rating": "", "content": ""}   # 폼에 다시 채워 줄 값이에요 (처음엔 모두 빈칸)
    status = 200                 # 응답 상태 코드예요 (기본은 '잘 받았어요' 200)

    if request.method == "POST":                            # 후기 폼을 제출해서 들어왔다면
        form["nickname"] = request.form.get("nickname", "").strip()   # 닉네임 칸의 글자를 받고 앞뒤 공백을 지워요
        form["rating"] = request.form.get("rating", "")               # 별점 칸의 값을 받아요 (아직 글자 상태예요)
        form["content"] = request.form.get("content", "").strip()     # 후기 내용 칸의 글자를 받고 앞뒤 공백을 지워요

        try:                                                # 별점을 숫자로 바꿔 봐요
            stars = int(form["rating"])                     # "4" 같은 글자를 숫자 4로 바꿔요
        except ValueError:                                  # 숫자가 아니라서 바꾸지 못했다면
            stars = None                                    # '별점 없음'으로 해요

        if form["nickname"] == "":                          # 닉네임이 비어 있으면
            error = "닉네임을 입력해 주세요."
        elif len(form["nickname"]) > 20:                    # 닉네임이 20자보다 길면
            error = "닉네임은 20자까지 쓸 수 있어요."
        elif stars is None or not 1 <= stars <= 5:          # 별점이 없거나 1~5 사이가 아니면
            error = "별점은 1~5 중에서 골라 주세요."
        elif form["content"] == "":                         # 후기 내용이 비어 있으면
            error = "후기 내용을 입력해 주세요."
        elif len(form["content"]) > 500:                    # 후기 내용이 500자보다 길면
            error = "후기 내용은 500자까지 쓸 수 있어요."

        if error is None:                                   # 틀린 점이 하나도 없다면
            db.add_review(class_id, form["nickname"], stars, form["content"])   # 후기 한 개를 데이터베이스에 저장해요 (클래스 번호, 닉네임, 별점, 내용 순서)
            flash("후기가 저장됐어요")                       # '후기가 저장됐어요' 안내를 남겨요 (다음 화면에서 딱 한 번만 보여요)
            return redirect(url_for("class_detail", class_id=class_id))   # 같은 상세 화면으로 보내요 (302). 새로고침은 이 GET 화면을 다시 여는 것뿐이라 후기가 또 저장되지 않아요
        status = 400                                        # 틀린 점이 있었으면 상태 코드를 400(보낸 값이 틀렸어요)으로 해요

    mine = db.get_reviews(class_id)   # 데이터베이스에서 이 클래스의 후기를 최신 순으로 꺼내요
    return render_template(      # 상세 화면을 만들어서 돌려줘요
        "class.html",
        c=found,                 # 클래스 정보
        reviews=mine,            # 이 클래스의 후기 목록
        error=error,             # 틀린 이유 (없으면 None)
        form=form,               # 폼에 다시 채워 줄 값
        wished=class_id in wished_ids(),   # 이 클래스를 이미 찜했는지 (버튼 모양을 정해요)
    ), status                    # 위에서 정한 상태 코드(200 또는 400)와 함께 돌려줘요


@app.route("/class/<int:class_id>/wish", methods=["POST"])   # 찜 버튼이 보내는 주소예요. 값을 바꾸는 일이라 POST만 받아요 (GET 으로 열면 405)
def toggle_wish(class_id):       # 찜하기 / 찜 취소를 맡을 함수예요
    if get_class(class_id) is None:   # 없는 클래스 번호면
        abort(404)               # 404 오류를 일으켜요
    ids = list(wished_ids())     # 지금 찜 목록을 복사해서 꺼내요
    if class_id in ids:          # 이미 찜한 클래스라면
        ids.remove(class_id)     # 목록에서 빼요 (찜 취소)
        flash("찜을 취소했어요")  # 한 번만 보이는 안내를 남겨요
    else:                        # 아직 안 찜했다면
        ids.append(class_id)     # 목록에 더해요 (찜하기)
        flash("찜했어요")        # 한 번만 보이는 안내를 남겨요
    session["wishlist"] = ids    # 바뀐 목록을 세션 수첩에 다시 적어요 (이때 쿠키가 새로 구워져요)
    return redirect(url_for("class_detail", class_id=class_id))   # 상세 화면으로 돌려보내요 (302). 새로고침해도 찜이 또 바뀌지 않아요


@app.route("/wishlist")          # 누가 주소 /wishlist 로 들어오면 아래 함수를 실행해요
def wishlist():                  # 내 찜 목록 화면을 맡을 함수예요
    shown = [get_class(i) for i in wished_ids()]   # 찜한 번호마다 클래스를 찾아요
    shown = [c for c in shown if c is not None]    # 혹시 사라진 클래스(None)는 빼요
    return render_template("wishlist.html", classes=shown)   # 찜 목록 화면을 만들어서 돌려줘요


@app.route("/api/classes")       # 누가 주소 /api/classes 로 들어오면 아래 함수를 실행해요 (화면이 아니라 JSON을 줘요)
def api_classes():               # 클래스 전체 목록을 JSON으로 주는 함수예요
    category = request.args.get("category", "")   # 주소의 ?category= 값을 읽어요 (없으면 빈 글자)
    shown = filter_and_sort(load_classes(), category)   # 카테고리가 있으면 그것만 거르고, 없으면 전체예요
    return jsonify(              # 아래 내용을 JSON으로 바꿔서 돌려줘요 (빈칸 None 은 null 이 돼요)
        count=len(shown),                  # 몇 개인지
        category=category or None,         # 거른 카테고리 (안 걸렀으면 null)
        classes=shown,                     # 클래스 목록
    )


@app.route("/api/classes/<int:class_id>")   # /api/classes/ 뒤의 숫자를 class_id 로 받아요
def api_class(class_id):         # 클래스 하나를 JSON으로 주는 함수예요
    found = get_class(class_id)  # 그 번호의 클래스를 찾아요 (없으면 None)
    if found is None:            # 못 찾았다면
        return jsonify(error=f"{class_id}번 클래스를 찾을 수 없어요"), 404   # 에러 메시지를 JSON으로, 상태 코드는 진짜 404로 돌려줘요
    return jsonify(found)        # 찾았다면 그 클래스를 JSON으로 돌려줘요


@app.route("/api/stats")         # 누가 주소 /api/stats 로 들어오면 아래 함수를 실행해요
def api_stats():                 # 통계를 JSON으로 주는 함수예요
    return jsonify(get_stats(load_classes()))   # 클래스를 읽어서 통계를 계산하고, JSON으로 돌려줘요


@app.errorhandler(404)           # 404 오류가 날 때마다 아래 함수가 대신 응답을 만들어요
def not_found(error):            # 404 응답을 맡을 함수예요 (error 는 오류 정보)
    if request.path.startswith("/api/"):   # 주소가 /api/ 로 시작하면 (프로그램이 부른 거라서)
        return jsonify(error="찾는 주소가 없어요"), 404   # 화면 대신 JSON 에러를 404와 함께 돌려줘요
    return render_template("404.html"), 404   # 아니면 404 화면을 '상태 코드 404'와 함께 돌려줘요


@app.errorhandler(500)           # 서버 안에서 에러가 날 때마다 아래 함수가 대신 응답을 만들어요
def server_error(error):         # 500 응답을 맡을 함수예요
    if request.path.startswith("/api/"):   # 주소가 /api/ 로 시작하면 (프로그램이 부른 거라서)
        return jsonify(error="서버에 문제가 생겼어요"), 500   # 화면 대신 JSON 에러를 500과 함께 돌려줘요
    return render_template("500.html"), 500   # 아니면 친절한 500 화면을 '상태 코드 500'과 함께 돌려줘요


@app.route("/about")             # 누가 주소 /about 으로 들어오면 아래 함수를 실행해요
def about():                     # 소개 화면을 맡을 함수예요
    return render_template("about.html")  # templates/about.html 화면을 돌려줘요


@app.route("/hello/<name>")      # /hello/ 뒤에 오는 글자를 name 이라는 이름으로 받아요
def hello(name):                 # 받은 name 을 함수 안에서 쓸 수 있어요
    return render_template("hello.html", name=name)   # name 을 화면에 넘겨서 인사 화면을 돌려줘요


if __name__ == "__main__":       # 이 파일을 직접 실행했을 때만 아래 줄이 일해요
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")   # 서버를 켜요. .env 에 FLASK_DEBUG=1 이 있는 내 컴퓨터에서만 debug 가 켜져요 (켜지면 코드를 고칠 때 자동으로 다시 시작돼요)
