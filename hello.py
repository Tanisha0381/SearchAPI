from flask import Flask, request, jsonify
import requests
from datetime import datetime

import json

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print("The file was not found")
        return None
    except json.JSONDecodeError:
        print("Failed to decode JSON")
        return None
        
app = Flask(__name__)

BASE_URL = "https://app.ylytic.com/ylytic/test"

def filter_comments(comments, filters):
    filtered_comments = comments

    # Filter by author name
    if 'search_author' in filters:
        filtered_comments = [comment for comment in filtered_comments if filters['search_author'].lower() in comment['author'].lower()]

    # Filter by date range
    if 'at_from' in filters and 'at_to' in filters:
        from_date = datetime.strptime(filters['at_from'], "%d-%m-%Y")
        to_date = datetime.strptime(filters['at_to'], "%d-%m-%Y")
        filtered_comments = [comment for comment in filtered_comments if from_date <= datetime.strptime(comment['at'], "%d-%m-%Y") <= to_date]

    # Filter by like and reply count range
    if 'like_from' in filters and 'like_to' in filters:
        filtered_comments = [comment for comment in filtered_comments if filters['like_from'] <= comment['like'] <= filters['like_to']]

    if 'reply_from' in filters and 'reply_to' in filters:
        filtered_comments = [comment for comment in filtered_comments if filters['reply_from'] <= comment['reply'] <= filters['reply_to']]

    # Filter by search text
    if 'search_text' in filters:
        filtered_comments = [comment for comment in filtered_comments if filters['search_text'].lower() in comment['text'].lower()]

    return filtered_comments

@app.route('/search', methods=['GET'])
def search_comments():
    try:
        response = requests.get(BASE_URL)
        comments = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

    filters = request.args.to_dict()
    filtered_comments = filter_comments(comments, filters)

    return jsonify({'comments': filtered_comments})

if __name__ == '__main__':
    app.run(debug=True)
