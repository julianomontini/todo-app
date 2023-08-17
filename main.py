from flask import request, jsonify
from sqlalchemy import text
from encryption import bcrypt
import logging
from app import app
from model import User, ToDo
from database import db
from jwt_token import jwt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({'status': 'healthy', 'message': 'Application is running and database connection is successful.'}), 200
    except Exception as e:
        error_message = 'Application is running but database connection failed.'
        logging.error(error_message, exc_info=True)  # Log the error along with exception details

        return jsonify({'status': 'unhealthy', 'message': error_message, 'error': str(e)}), 500



@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    existing_user = db.session.query(User).filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = db.session.query(User).filter_by(username=username).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=username, additional_claims={'iss': 'montech.tech', 'id': user.id})
    return jsonify({'access_token': access_token}), 200

@app.route('/todos', methods=['POST'])
@jwt_required()  # Requires a valid JWT token
def create_todo():
    data = request.json
    title = data.get('title')
    user_id = get_jwt_identity()  # Get the user's id from the JWT token claim

    if not title:
        return jsonify({'message': 'Title is required'}), 400

    new_todo = ToDo(title=title, user_id=user_id)
    db.session.add(new_todo)
    db.session.commit()

    return jsonify({'message': 'ToDo created successfully'}), 201

@app.route('/todos/<int:todo_id>', methods=['PUT'])
@jwt_required()  # Requires a valid JWT token
def update_todo(todo_id):
    data = request.json
    user_id = get_jwt_identity()  # Get the user's id from the JWT token claim

    todo = db.session.query(ToDo).filter_by(id=todo_id, user_id=user_id).first()
    if not todo:
        return jsonify({'message': 'ToDo not found or you are not the owner'}), 404

    # Update fields if provided in the request
    if 'title' in data:
        todo.title = data['title']
    if 'description' in data:
        todo.description = data['description']
    if 'due_date' in data:
        todo.due_date = data['due_date']
    if 'status' in data:
        todo.status = data['status']

    db.session.commit()

    return jsonify({'message': 'ToDo updated successfully'}), 200

@app.route('/todos', methods=['GET'])
@jwt_required()  # Requires a valid JWT token
def list_todos():
    user_id = get_jwt_identity()  # Get the user's id from the JWT token claim
    status = request.args.get('status')

    todos_query = db.session.query(ToDo).filter_by(user_id=user_id)
    if status:
        todos_query = todos_query.filter_by(status=status)

    todos = todos_query.all()

    todos_list = []
    for todo in todos:
        todos_list.append({
            'id': todo.id,
            'title': todo.title,
            'description': todo.description,
            'due_date': todo.due_date,
            'status': todo.status,
            'last_updated': todo.last_updated
        })

    return jsonify(todos_list), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0")
    
