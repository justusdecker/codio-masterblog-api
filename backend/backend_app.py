from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

def get_ids() -> list[int]:
    return [i['id'] for i in POSTS]

@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    if request.method == 'POST':
        title = request.form.get('title','')
        content = request.form.get('content','')
        if not title or not content:
            return "Bad Request", 400
        POSTS.append(
            {
                'id': max([i['id'] for i in POSTS]),
                'title': title,
                'content': content
                }
        )
        return "",201
    return jsonify(POSTS)
@app.route('/api/posts/<id>', methods=['DELETE'])
def delete_posts(id:str):
    if not id.isdecimal():
        return "Bad Request",400
    id = int(id)
    if id not in get_ids():
        return "Not Found",404 # <- 410 Gone?
    POSTS.pop(get_ids().index(id))
    return "OK",200
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
