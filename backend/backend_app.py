from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

ALLOWED_KEYS = ['title', 'content']
ALLOWED_ORDERS = ['desc', 'asc']
def get_ids() -> list[int]:
    return [i['id'] for i in POSTS]
def search_in(key: str, phrase: str):
    return [i for i in POSTS if phrase.lower() in i[key].lower()]
def remove_duplicates(search_list):
    pass

@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    """
    Handles API requests for '/api/posts' to retrieve all posts or create a new post.

    GET Request:
        Retrieves a list of all existing posts.

        Returns:
            JSON: A list of dictionaries, where each dictionary represents a post
                  with 'id', 'title', and 'content' keys.
                  Example: `[{"id": 1, "title": "Post 1", "content": "Content 1"}]`

    POST Request:
        Creates a new post based on the provided JSON data in the request body.

        Request Body (JSON):
            - `title` (str): The title of the new post. (Required)
            - `content` (str): The content of the new post. (Required)

        Returns:
            JSON: On successful creation, returns the newly created post (including its new ID)
                  with a 201 Created status code.
                  Example: `{"id": 2, "title": "New Post", "content": "New Content"}`
            Tuple[str, int]: On error, returns an error message string and a 400 Bad Request
                             status code if:
                             - The request body is not valid JSON.
                             - The 'title' field is missing or empty.
                             - The 'content' field is missing or empty.
    """
    if request.method == 'POST':
        try:
            req = request.json
        except:
            return "Bad Request", 400
        
        title = req.get('title','')
        content = req.get('content','')

        if not title or not content:
            return "Bad Request", 400
        
        output = {
                'id': max([i['id'] for i in POSTS]),
                'title': title,
                'content': content
                }
        
        POSTS.append(
            output
        )
        
        return jsonify(output),201
    elif request.method == 'GET':
        try:
            args = query_parse(request.query_string.decode())
        except:
            args = False
        if not args:
            return jsonify(POSTS)
        else:
            direction = args.get('direction','desc')
            sort = args.get('sort','title')
            if sort not in ALLOWED_KEYS:
                sort = 'title'
            if direction not in ALLOWED_ORDERS:
                direction = 'desc'
                
            if sort == 'title':
                sorting_method = lambda x: x['title']
            elif sort == 'content':
                sorting_method = lambda x: x['content']
                
            sorting_direction = True if direction == 'desc' else False
            sorted_list = sorted(POSTS,reverse=sorting_direction,key=sorting_method)
            return jsonify(sorted_list)
        
@app.route('/api/posts/<id>/delete', methods=['DELETE'])
def delete_post(id:str):
    """
    Handles DELETE requests for '/api/posts/<id>/delete' to delete a specific post.

    Deletes a post identified by its ID.

    Args:
        id (str): The ID of the post to be deleted. This ID is expected to be a string
                  representation of an integer.

    Returns:
        JSON: On successful deletion, returns a JSON object with a success message
              and a 200 OK status code.
              Example: `{'message': 'Post with id <123> has been deleted successfully.'}`
        Tuple[str, int]: On error, returns an error message string and an appropriate
                         HTTP status code if:
                         - The 'id' provided in the URL is not a valid integer (400 Bad Request).
                         - The post with the specified 'id' does not exist (404 Not Found).
    """
    if not id.isdecimal():
        return "Bad Request",400
    id = int(id)
    if id not in get_ids():
        return "Not Found",404 # <- 410 Gone?
    POSTS.pop(get_ids().index(id))
    return jsonify({'message': f'Post with id <{id}> has been deleted successfully.'}), 200
  
@app.route('/api/posts/<id>', methods=['PUT'])
def update_post(id:str):
    if not id.isdecimal():
        return "Bad Request",400
    id = int(id)
    if id not in get_ids():
        return "Not Found",404 # <- 410 Gone?
    
    try:
        req = request.json
    except:
        return "Bad Request", 400
    
    title = req.get('title','')
    content = req.get('content','')
    

    blogpost = POSTS[get_ids().index(id)]
    
    if title:
        blogpost['title'] = title
    if content:
        blogpost['content'] = content
    
    return jsonify(blogpost), 200
  
def query_parse(q:str) -> dict[str,str]:
    return {i.split('=')[0]: i.split('=')[1] for i in q.split('&')}

@app.route('/api/posts/search', methods=['GET'])
def search_post():
    try:
        args = query_parse(request.query_string.decode())
    except:
        args = False
    if not args:
        return jsonify(POSTS)
    results = []
    seen = set()
    for key in args:
        if key not in ['title', 'content']:
            continue
        for i in search_in(key,args[key]):
            
            if i['id'] not in seen:
                seen.add(i['id'])
                results.append(i)

    return jsonify(results), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
