from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd

# Load the pre-trained models and data
popular_df = pickle.load(open("./popular.pkl", "rb"))
pt = pickle.load(open("./pt.pkl", "rb"))
books = pickle.load(open("./books.pkl", "rb"))
similarity_scores = pickle.load(open("./similarity_scores.pkl", "rb"))

app = Flask(__name__)


@app.route("/")
def index():
    return render_template(
        "index.html",
        book_name=list(popular_df["Book-Title"].values),
        author=list(popular_df["Book-Author"].values),
        image=list(popular_df["Image-URL-M"].values),
        votes=list(popular_df["num_ratings"].values),
        rating=list(popular_df["avg_rating"].values),
    )


@app.route("/recommend")
def recommend_ui():
    return render_template("recommend.html")


@app.route("/recommend_books", methods=["POST"])
def recommend():
    user_input = request.form.get("user_input").lower().strip()
    print(f"User input: {user_input}")  # Debug print

    # Exact match search first
    exact_matches = pt.index[pt.index.str.lower() == user_input]
    print(f"Exact matches: {exact_matches}")  # Debug print

    if exact_matches.size > 0:
        matching_books = exact_matches
    else:
        # Fallback to partial match search
        partial_matches = pt.index[pt.index.str.lower().str.contains(user_input)]
        print(f"Partial matches: {partial_matches}")  # Debug print
        matching_books = partial_matches

    if matching_books.size == 0:
        print("Book not found")  # Debug print
        return render_template("recommend.html", data=[], invalid_input=True)

    index = np.where(pt.index == matching_books[0])[0][0]
    similar_items = sorted(
        list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True
    )[1:5]
    print(f"Similar items: {similar_items}")  # Debug print

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books["Book-Title"].str.lower() == pt.index[i[0]].lower()]
        item.extend(list(temp_df.drop_duplicates("Book-Title")["Book-Title"].values))
        item.extend(list(temp_df.drop_duplicates("Book-Title")["Book-Author"].values))
        item.extend(list(temp_df.drop_duplicates("Book-Title")["Image-URL-M"].values))

        data.append(item)

    print(f"Data: {data}")  # Debug print

    return render_template("recommend.html", data=data, invalid_input=False)


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
