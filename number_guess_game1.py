import os
import random
import streamlit as st


# ---------- 成绩保存 ----------
def get_score_file(mode_key):
    return f"best_score_{mode_key}.txt"


def load_best_score(mode_key):
    score_file = get_score_file(mode_key)
    if os.path.exists(score_file):
        with open(score_file, "r", encoding="utf-8") as f:
            text = f.read().strip()
            if text.isdigit():
                return int(text)
    return None


def save_best_score(mode_key, score):
    score_file = get_score_file(mode_key)
    with open(score_file, "w", encoding="utf-8") as f:
        f.write(str(score))


# ---------- 游戏逻辑 ----------
def make_answer(digits):
    first = random.choice("123456789")
    pool = [x for x in "0123456789" if x != first]
    others = random.sample(pool, digits - 1)
    return first + "".join(others)


def judge(answer, guess):
    if len(guess) != len(answer):
        return None
    if not guess.isdigit():
        return None
    if len(set(guess)) != len(guess):
        return None

    nA = 0
    nB = 0

    for i in range(len(answer)):
        if guess[i] == answer[i]:
            nA += 1
        elif guess[i] in answer:
            nB += 1

    return nA, nB


def reset_game():
    mode_key = st.session_state.mode_key
    digits = MODES[mode_key]["digits"]

    st.session_state.answer = make_answer(digits)
    st.session_state.count = 0
    st.session_state.history = []
    st.session_state.cleared = False
    st.session_state.last_message = ""
    st.session_state.best_score = load_best_score(mode_key)


# ---------- 模式设置 ----------
MODES = {
    "easy": {"label": "簡単モード", "digits": 3, "emoji": "🐣"},
    "hard": {"label": "難しいモード", "digits": 4, "emoji": "🔥"},
    "expert": {"label": "専門家モード", "digits": 5, "emoji": "👑"},
}


# ---------- 页面设置 ----------
st.set_page_config(
    page_title="数字あてゲーム",
    page_icon="🎯",
    layout="centered"
)

# ---------- 样式 ----------
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(180deg, #fff9db 0%, #f8f9fa 100%);
    }

    .title-box {
        background: #fff3bf;
        border-radius: 18px;
        padding: 18px 20px;
        text-align: center;
        margin-bottom: 16px;
        border: 2px solid #ffe066;
    }

    .rule-box {
        background: white;
        border-radius: 16px;
        padding: 14px 16px;
        border: 1px solid #eee;
        margin-bottom: 12px;
    }

    .history-box {
        background: white;
        border-radius: 16px;
        padding: 14px 16px;
        border: 1px solid #eee;
        margin-top: 12px;
    }

    .history-row {
        font-size: 18px;
        padding: 8px 0;
        border-bottom: 1px dashed #eee;
    }

    .mode-box {
        background: white;
        border-radius: 16px;
        padding: 10px 14px;
        border: 1px solid #eee;
        margin-bottom: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- 初始化 ----------
if "mode_key" not in st.session_state:
    st.session_state.mode_key = "easy"

if "answer" not in st.session_state:
    reset_game()

# ---------- 标题 ----------
st.markdown(
    """
    <div class="title-box">
        <h1>🎯 数字あてゲーム</h1>
        <p>数字と位置をヒントにして、答えを当てよう！</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- 模式选择 ----------
st.markdown('<div class="mode-box">', unsafe_allow_html=True)

mode_key = st.radio(
    "モードを選んでね",
    options=list(MODES.keys()),
    format_func=lambda k: f"{MODES[k]['emoji']} {MODES[k]['label']}（{MODES[k]['digits']}桁）",
    horizontal=True,
    index=list(MODES.keys()).index(st.session_state.mode_key),
)

st.markdown('</div>', unsafe_allow_html=True)

if mode_key != st.session_state.mode_key:
    st.session_state.mode_key = mode_key
    reset_game()
    st.rerun()

current_mode = MODES[st.session_state.mode_key]
digits = current_mode["digits"]

# ---------- 最佳成绩 ----------
if st.session_state.best_score is not None:
    st.info(f"🏆 ベスト記録（{current_mode['label']}）：{st.session_state.best_score} 回")

# ---------- 规则 ----------
st.markdown(
    f"""
    <div class="rule-box">
        <b>{current_mode['emoji']} {current_mode['label']} のルール</b><br>
        ・{digits}桁の数字を入力します。<br>
        ・同じ数字は使えません。<br>
        ・先頭は 0 になりません。<br>
        ・A = 数字も位置もあっている<br>
        ・B = 数字はあっているけど位置がちがう
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- 输入区域 ----------
st.subheader("数字を入れてね")

guess = st.text_input(
    f"{digits}桁の数字を入力してください",
    value="",
    max_chars=digits,
    placeholder=f"例: {'12345'[:digits]}"
)

col1, col2 = st.columns(2)

guess_clicked = col1.button("✅ 判定する", use_container_width=True, disabled=st.session_state.cleared)
reset_clicked = col2.button("🔄 もう一回あそぶ", use_container_width=True)

# ---------- 重置 ----------
if reset_clicked:
    reset_game()
    st.rerun()

# ---------- 判定 ----------
if guess_clicked:
    result = judge(st.session_state.answer, guess)

    if result is None:
        st.session_state.last_message = f"{digits}桁の重複しない数字を入力してください。"
        st.error(st.session_state.last_message)
    else:
        st.session_state.count += 1
        nA, nB = result
        st.session_state.history.append((st.session_state.count, guess, nA, nB))

        if nA == digits:
            st.session_state.cleared = True
            score = st.session_state.count
            best = st.session_state.best_score

            if best is None or score < best:
                st.session_state.best_score = score
                save_best_score(st.session_state.mode_key, score)
                st.session_state.last_message = f"🏆 新記録！ {score} 回で当たりました！"
                st.success(st.session_state.last_message)
            else:
                st.session_state.last_message = f"🎉 おめでとう！ {score} 回で当たりました！"
                st.success(st.session_state.last_message)

            st.balloons()
        else:
            st.session_state.last_message = f"{nA}A {nB}B です。"
            st.info(st.session_state.last_message)

# ---------- 历史消息 ----------
if st.session_state.last_message and not guess_clicked:
    if st.session_state.cleared:
        st.success(st.session_state.last_message)
    else:
        st.info(st.session_state.last_message)

# ---------- 历史记录 ----------
st.markdown('<div class="history-box">', unsafe_allow_html=True)
st.subheader("📜 履歴")

if st.session_state.history:
    for turn, g, A, B in st.session_state.history:
        st.markdown(
            f"""
            <div class="history-row">
                {turn}回目: <b>{g}</b> → <b>{A}A {B}B</b>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.write("まだ入力がありません。")

st.markdown("</div>", unsafe_allow_html=True)

# ---------- 提示 ----------
st.caption("💡 ヒント: 0 は使えるけど、最初の数字には入りません。")

# ---------- 调试区 ----------
#with st.expander("開発用（必要なときだけ）"):
#    st.write("mode:", st.session_state.mode_key)
#    st.write("DEBUG answer:", st.session_state.answer)