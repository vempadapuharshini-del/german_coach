import streamlit as st
from groq import Groq
import json
import os
from datetime import date

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
DATA_FILE = "german_data.json"
TODAY = str(date.today())

st.set_page_config(page_title="Mein Deutsch Coach", page_icon="🌸")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {
        "learned_words": [],
        "known_skipped_words": [],
        "daily_words": {},
        "notes": ""
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

data = load_data()

def ask_ai(prompt):
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )
    return response.choices[0].message.content

def get_new_word():
    learned = "\n".join([w["content"] for w in data["learned_words"]])
    skipped = "\n".join(data["known_skipped_words"])

    prompt = f"""
Give me ONE new German learning word.

Do NOT repeat these learned words:
{learned}

Do NOT give these already-known words:
{skipped}

Mix nouns, verbs, adjectives, and prepositions.

Return ONLY in this exact Markdown format.
Use blank lines between each field.

### 🌸 Word

**German:** der/die/das + word

**English:** English translation

**Type:** Noun / Verb / Adjective / Preposition

**Meaning:** simple meaning

**Pronunciation:** simple pronunciation

### 📌 Examples

**Nominativ:**  
German sentence  
English meaning

**Akkusativ:**  
German sentence  
English meaning

**Dativ:**  
German sentence  
English meaning

### 🧠 Simple Explanation

Explain in easy English in 2-3 lines.

Do not write everything in one paragraph.
Do not add extra text.
"""
    return ask_ai(prompt)

def generate_daily_quiz(today_words):
    words_text = "\n\n".join(today_words)

    prompt = f"""
Create a German quiz with 10 questions using ONLY these 5 words:

{words_text}

Make mixed questions:
- article question
- meaning question
- nominativ question
- akkusativ question
- dativ question
- fill in the blank
- correct the mistake

Rules:
- Use Markdown.
- Show ONLY the questions.
- Do NOT show answers.
- Do NOT include an answer key.
- Do NOT explain answers yet.
- Number the questions from 1 to 10.
- Keep it beginner friendly.

Format:

### 🧠 Daily Quiz

1. Question here
2. Question here
3. Question here
"""
    return ask_ai(prompt)

def generate_dictionary_quiz():
    total_words = len(data["learned_words"])

    if total_words <= 10:
        question_count = 10
    elif total_words <= 30:
        question_count = 20
    else:
        question_count = 30

    all_words = "\n\n".join([w["content"] for w in data["learned_words"]])

    prompt = f"""
Create a German revision quiz with {question_count} questions.

Use these learned words:

{all_words}

Make mixed questions:
- meaning
- article
- nominativ
- akkusativ
- dativ
- fill in the blank
- correct the mistake
- translation

Rules:
- Use Markdown.
- Show ONLY the questions.
- Do NOT show answers.
- Do NOT include an answer key.
- Do NOT explain answers yet.
- Number all questions clearly.
- Keep it beginner friendly.

Format:

### 🔁 Dictionary Revision Quiz

1. Question here
2. Question here
3. Question here
"""
    return ask_ai(prompt)

st.title("🌸 Mein Deutsch Coach")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["🏠 Today", "🧠 Daily Quiz", "📚 My Dictionary", "📝 Notes", "Categories", "🎮Games"]
)

if TODAY not in data["daily_words"]:
    data["daily_words"][TODAY] = []
    save_data(data)

if "current_word" not in st.session_state:
    st.session_state.current_word = ""

with tab1:
    st.header("📚 Today's Tasks")

    st.checkbox("Learn 5 new German words")
    st.checkbox("Complete daily quiz")
    st.checkbox("Writing practice")
    st.checkbox("Speaking practice")
    st.checkbox("Take notes")

    today_words = data["daily_words"][TODAY]

    st.subheader(f"🌼 Today's accepted words: {len(today_words)}/5")

    if len(today_words) < 5:

        if not st.session_state.current_word:
            if st.button("✨ Start / Get New Word"):
                st.session_state.current_word = get_new_word()
                st.rerun()

        if st.session_state.current_word:
            formatted_word = st.session_state.current_word

            formatted_word = formatted_word.replace("**German:**", "\n\n**German:**")
            formatted_word = formatted_word.replace("**English:**", "\n\n**English:**")
            formatted_word = formatted_word.replace("**Type:**", "\n\n**Type:**")
            formatted_word = formatted_word.replace("**Meaning:**", "\n\n**Meaning:**")
            formatted_word = formatted_word.replace("**Pronunciation:**", "\n\n**Pronunciation:**")

            formatted_word = formatted_word.replace("### 📌 Examples", "\n\n### 📌 Examples")
            formatted_word = formatted_word.replace("**Nominativ:**", "\n\n**Nominativ:**")
            formatted_word = formatted_word.replace("**Akkusativ:**", "\n\n**Akkusativ:**")
            formatted_word = formatted_word.replace("**Dativ:**", "\n\n**Dativ:**")
            formatted_word = formatted_word.replace("### 🧠 Simple Explanation", "\n\n### 🧠 Simple Explanation")

            st.markdown(formatted_word)
            
            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Next - I want to learn this"):
                    today_words.append(st.session_state.current_word)

                    data["learned_words"].append({
                        "date": TODAY,
                        "content": st.session_state.current_word
                    })
                    save_data(data)

                    st.session_state.current_word = get_new_word()

                    
                    st.rerun()

            with col2:
                if st.button("🔄 I already knew this"):
                    data["known_skipped_words"].append(
                        st.session_state.current_word
                    )
                    save_data(data)

                    st.session_state.current_word = get_new_word()
                    
                    st.rerun()

    else:
        st.success("🎉 You completed today's 5 new words!")

        for i, word in enumerate(today_words, start=1):
            st.markdown(f"### Word {i}")
            st.markdown(word)

    st.header("✍️ Daily Writing")

    user_text = st.text_area(
        "Was hast du heute gemacht?",
        key="daily_writing"
    )

    if st.button("Correct my German"):
        correction_prompt = f"""
I am learning German.

Correct my German text simply.
Explain mistakes in easy English.

Give:
1. Correct version
2. Mistakes
3. Simple explanation
4. Two practice sentences

My text:
{user_text}
"""
        result = ask_ai(correction_prompt)
        st.markdown(result)

with tab2:
    st.header("🧠 Daily Quiz")

    today_words = data["daily_words"][TODAY]

    if len(today_words) < 5:
        st.warning("Complete today's 5 words first.")

    else:
        if "daily_quiz" not in st.session_state:
            st.session_state.daily_quiz = ""

        if st.button("📝 Generate Daily Quiz"):
            st.session_state.daily_quiz = generate_daily_quiz(today_words)

        if st.session_state.daily_quiz:

            st.markdown(st.session_state.daily_quiz)

            daily_answers = st.text_area(
                "Write your answers here:",
                key="daily_quiz_answers"
            )

            if st.button("Submit Daily Quiz"):

                check_prompt = f"""
Check my answers for this German quiz.

Quiz:
{st.session_state.daily_quiz}

My answers:
{daily_answers}

Give:
1. Score
2. Correct answers
3. Mistake explanation
4. What I should revise

Use easy English.
"""

                result = ask_ai(check_prompt)

                st.markdown(result)
with tab3:
    st.header("📚 My Dictionary")

    total = len(data["learned_words"])

    st.subheader(f"Total learned words: {total}")

    if total == 0:
        st.info("No learned words yet.")

    else:
        for item in data["learned_words"]:

            content = item["content"]

            lines = content.split("\n")

            german_word = "German Word"

            for line in lines:

                if "German:" in line:

                    german_word = line.replace(
                        "**German:**",
                        ""
                    ).strip()

            with st.expander(german_word):

                st.markdown(content)

    st.header("🔁 Quiz Me Until Now")

    if total < 5:

        st.warning("Learn at least 5 words first.")

    else:

        if "dictionary_quiz" not in st.session_state:
            st.session_state.dictionary_quiz = ""

        if st.button("Generate Dictionary Revision Quiz"):

            st.session_state.dictionary_quiz = (
                generate_dictionary_quiz()
            )

        if st.session_state.dictionary_quiz:

            st.markdown(
                st.session_state.dictionary_quiz
            )

            dictionary_answers = st.text_area(
                "Write your answers here:",
                key="dictionary_quiz_answers"
            )

            if st.button("Submit Dictionary Quiz"):

                check_prompt = f"""
Check my answers for this German revision quiz.

Quiz:
{st.session_state.dictionary_quiz}

My answers:
{dictionary_answers}

Give:
1. Score
2. Correct answers
3. Mistake explanation
4. Weak areas
5. Revision tips

Use easy English.
"""

                result = ask_ai(check_prompt)

                st.markdown(result)

with tab4:
    st.header("📝 My Notes")

    notes = st.text_area(
        "Write your notes here",
        value=data.get("notes", ""),
        key="notes_section",
        height=300
    )

    if st.button("Save Notes"):
        data["notes"] = notes
        save_data(data)
        st.success("Notes saved!")
with tab5:
    st.header("🏷️ Category Practice")

    category = st.selectbox(
        "Choose a category",
        [
            "Café",
            "School",
            "University",
            "Technology",
            "Supermarket",
            "Travel",
            "Doctor",
            "Job Interview",
            "Apartment/Home",
            "Transport"
        ]
    )

    if "category_result" not in st.session_state:
        st.session_state.category_result = ""

    if st.button("Generate Category Words"):
        category_prompt = f"""
Create German learning practice for this category: {category}

Give:
1. 10 useful German words
2. English meaning
3. Article for nouns
4. 5 simple example sentences
5. 5 small quiz questions

Use clean Markdown.
Keep it beginner friendly.
"""
        st.session_state.category_result = ask_ai(category_prompt)

    if st.session_state.category_result:
        st.markdown(st.session_state.category_result)
with tab6:
    st.header("🎮 German → English Game")

    if "game_word" not in st.session_state:
        st.session_state.game_word = ""

    if "game_answer" not in st.session_state:
        st.session_state.game_answer = ""

    if "game_score" not in st.session_state:
        st.session_state.game_score = 0

    st.subheader(f"🏆 Score: {st.session_state.game_score}")

    if st.button("🎲 Generate Game Word"):

        game_prompt = """
Give ONE beginner German word.

Format EXACTLY like this:

German Word: ...
Hint: ...
English Meaning: ...

Only one word.
"""

        result = ask_ai(game_prompt)

        st.session_state.game_word = result

        # Extract answer secretly
        answer = ""

        for line in result.split("\n"):
            if "English Meaning:" in line:
                answer = line.replace(
                    "English Meaning:",
                    ""
                ).strip()

        st.session_state.game_answer = answer

    if st.session_state.game_word:

        # Hide answer from UI
        visible_question = ""

        for line in st.session_state.game_word.split("\n"):
            if "English Meaning:" not in line:
                visible_question += line + "\n"

        st.markdown(visible_question)

        user_answer = st.text_input(
            "Type English meaning:",
            key="game_user_answer"
        )

        if st.button("✅ Submit Answer"):

            correct_answer = st.session_state.game_answer.lower().strip()

            user = user_answer.lower().strip()

            if user == correct_answer:

                st.success("Correct ✅")

                st.session_state.game_score += 1

            else:

                st.error("Wrong ❌")

                st.markdown(
                    f"""
### Correct Answer:
{st.session_state.game_answer}

### Explanation:
The German word means:
**{st.session_state.game_answer}**
"""
                )