from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Загружаем базу (твой полный CSV)
df = pd.read_csv('programs_database.csv')

@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    if request.method == 'POST':
        # Получаем баллы и выбранный иностранный язык
        georgian = int(request.form.get('georgian', 0))
        foreign_lang = request.form.get('foreign_lang')
        foreign_score = int(request.form.get('foreign_score', 0)) if foreign_lang else 0
        
        # Остальные предметы (можно расширить)
        math = int(request.form.get('math', 0))
        history = int(request.form.get('history', 0))
        biology = int(request.form.get('biology', 0))
        
        # Простой расчёт (пока заглушка — позже добавим коэффициенты)
        for _, row in df.iterrows():
            total = georgian * 5 + foreign_score * 4 + math * 3 + history * 3 + biology * 3
            results.append({
                'program': row['program_name'],
                'qualification': row['qualification'],
                'uni_code': row['university_code'],
                'total': total,
                'chance': 'მაღალი' if total > 500 else 'საშუალო'  # Позже сделаем реальный
            })
        
        results = sorted(results, key=lambda x: x['total'], reverse=True)[:10]

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)