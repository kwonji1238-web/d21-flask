import sqlite3                               # SQLite(파일 하나짜리 작은 데이터베이스)를 다루는 도구를 가져와요
from contextlib import closing                # 다 쓰면 연결을 자동으로 닫아 주는 도구를 가져와요
from pathlib import Path                      # 파일 위치를 다루는 도구를 가져와요

DB_PATH = Path(__file__).resolve().parent / "reviews.db"   # 데이터베이스 파일 위치예요 (db.py 와 같은 폴더의 reviews.db)


def connect():                                # 데이터베이스와 연결하는 함수예요
    conn = sqlite3.connect(DB_PATH)           # reviews.db 파일에 연결해요 (파일이 없으면 새로 만들어요)
    conn.row_factory = sqlite3.Row            # 꺼낸 줄을 r["nickname"] 처럼 칸 이름으로 읽을 수 있게 해요
    return conn                               # 연결을 돌려줘요


def init_db():                                # reviews 표를 만드는 함수예요
    with closing(connect()) as conn, conn:    # 연결해서 쓰고, 끝나면 저장(commit)하고 연결을 닫아요
        conn.execute(                         # 아래 SQL 문장을 실행해요
            """
            CREATE TABLE IF NOT EXISTS reviews (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id   INTEGER NOT NULL,
                nickname   TEXT    NOT NULL,
                rating     INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                content    TEXT    NOT NULL,
                created_at TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """                               # 표가 없을 때만 만들어요. id 는 자동 번호, rating 은 1~5만 허용, created_at 은 안 넣으면 지금 시각이에요
        )


def add_review(class_id, nickname, rating, content):   # 후기 한 개를 저장하는 함수예요
    with closing(connect()) as conn, conn:    # 연결해서 쓰고, 끝나면 저장(commit)하고 연결을 닫아요
        conn.execute(                         # 아래 SQL 문장을 실행해요
            "INSERT INTO reviews (class_id, nickname, rating, content) VALUES (?, ?, ?, ?)",   # 사용자 값 자리는 모두 ? 로 비워 둬요
            (class_id, nickname, rating, content),   # ? 자리에 순서대로 들어갈 값이에요 (글자로 이어 붙이지 않아서 안전해요)
        )


def get_reviews(class_id):                    # 그 클래스의 후기를 최신 순으로 꺼내는 함수예요
    with closing(connect()) as conn:          # 연결해서 쓰고, 끝나면 연결을 닫아요
        rows = conn.execute(                  # 아래 SQL 문장을 실행해요
            "SELECT id, class_id, nickname, rating, content, created_at "
            "FROM reviews WHERE class_id = ? ORDER BY id DESC",   # 이 클래스 후기만, id 가 큰 것(최신)부터 가져와요. class_id 자리는 ? 예요
            (class_id,),                      # ? 자리에 들어갈 값이에요 (값이 하나여도 끝에 쉼표를 붙여요)
        ).fetchall()                          # 결과를 전부 받아요
    return [dict(row) for row in rows]        # 한 줄씩 사전(dict)으로 바꿔서 목록으로 돌려줘요
