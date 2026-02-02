from flask import Flask, render_template, request
from recommendation_system import UniversityRecommendationSystem

app = Flask(__name__)
system = UniversityRecommendationSystem()

@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    if request.method == 'POST':
        user_scores = {
            'ქართული ენა და ლიტერატურა': int(request.form.get('georgian', 0)),
            'უცხოური ენა': int(request.form.get('foreign', 0)),
            'მათემატიკა': int(request.form.get('math', 0)),
            'ისტორია': int(request.form.get('history', 0)),
            'ბიოლოგია': int(request.form.get('biology', 0)),
            'გეოგრაფია': int(request.form.get('geography', 0)),
            'ფიზიკა': int(request.form.get('physics', 0)),
            'ქიმია': int(request.form.get('chemistry', 0)),
            'ზოგადი უნარები': int(request.form.get('general_skills', 0)),
            'ლიტერატურა': int(request.form.get('literature', 0)),
            'სამოქალაქო განათლება': int(request.form.get('civic_education', 0)),
            'სახვითი და გამოყენებითი ხელოვნება': int(request.form.get('art', 0)),
        }
        results = system.recommend(user_scores)

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
