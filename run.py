from flask import Flask, request, jsonify
app = Flask(__name__)
import json
import database_class
from hashlib import md5

with open('configs/apis.json') as file:
    apis = json.load(file)
dbs = database_class.get_dbs_names()

@app.route('/api', methods=['POST'])
def database():
    if "api_key" not in request.headers:
        return jsonify({'error': 'no api key'}), 401
    else:
        api_key = request.headers['api_key']
        for api_keys in apis:
            if api_key not in api_keys:
                return jsonify({'error': 'invalid api key'}), 401
            else:
                permissions = api_keys[api_key]["permission"]

    data = request.get_json()
    if 'db' not in data or 'query' not in data:
        return jsonify({'error': 'Invalid request'}), 400
    if data['db'] not in dbs:
        return jsonify({'error': 'Database not found'}), 404
    db_name = data['db']
    query = data['query']
    type = data['type']

    # Updating Data
    if type == 'update':
        if "update" not in permissions:
            return jsonify({'error': 'permission denied'}), 403
        try:
            updated_record = data['update_query']
        except KeyError:
            return jsonify({'error': 'update_query not found'}), 400
        database = database_class.Database(db_name)
        if database:
            return jsonify(database.update_record_by_query(query, updated_record)), 200
        return jsonify({'error': 'Database not found'}), 404
    # Deleting Data
    elif type == 'delete':
        if "delete" not in permissions:
            return jsonify({'error': 'permission denied'}), 403
        database = database_class.Database(db_name)
        if database:
            return jsonify(database.delete_by(query)), 200
        return jsonify({'error': 'Database not found'}), 404
    # Creating Data
    elif type == 'create':
        if "create" not in permissions:
            return jsonify({'error': 'permission denied'}), 403
        database = database_class.Database(db_name)
        if database:
            return jsonify(database.create_record(query)), 200
        return jsonify({'error': 'Database not found'}), 404
    # Reading Data
    elif type == 'read':
        if "read" not in permissions:
            return jsonify({'error': 'permission denied'}), 403
        database = database_class.Database(db_name)
        if database:
            return jsonify(database.get_by(query)), 200
        return jsonify({'error': 'Database not found'}), 404
    # Matching Data
    elif type == 'match':
        if "read" not in permissions:
            return jsonify({'error': 'permission denied'}), 403
        database = database_class.Database(db_name)
        if database:
            key = list(query.keys())
            value = query[key[0]]
            data = database.get_by({key[0]:value})
            if isinstance(data, list):
                if key[1] in data[0]:
                    if data[0][key[1]] == query[key[1]]:
                        return {"message":"matched","data":data}
                    else:
                        return {"message":"not matched"}
                else:
                    return {"error":"key error"}
            elif isinstance(data, dict):
                if key[1] in data:
                    if data[key[1]] == query[key[1]]:
                        return {"message":"matched","data":data}
                    else:
                        return {"message":"not matched"}
                else:
                    return {"error":"key error"}
            
            else:
                return {"message":"not matched"}
            
        return jsonify({'error': 'Datbase not found'}), 404
    
    elif type == 'create_db':
        if "create" not in permissions:
            return jsonify({'error': 'permission denied'}), 403
        if "name" not in list(query.keys()):
            return {'error':'name not found'}
        return jsonify(database_class.create_db(query["name"])), 200
    
    # Invalid Request
    else:
        return jsonify({'error': 'Invalid request'}), 400    

@app.route("/users", methods=['POST'])
def user():
    data = request.get_json()
    if "api_key" not in request.headers:
        return jsonify({'error': 'no api key'}), 401
    else:
        api_key = request.headers['api_key']
        for api_keys in apis:
            if api_key not in api_keys:
                return jsonify({'error': 'invalid api key'}), 401
        permissions = api_keys[api_key]["permission"]
    if "create_user" not in permissions:
        return jsonify({'error': 'permission denied'}), 403
    if "name" not in data or "permission" not in data:
        return jsonify({'error': 'Invalid request'}), 400
    name = data["name"]
    for api_keys in apis:
        for key in api_keys:
            if api_keys[key]["name"] == name:
                return jsonify({'error': 'User already exists'}), 400
    permission = data["permission"]
    for perm in permission:
        if perm not in ["create","read","update","delete"]:
            return jsonify({'error': 'Invalid permission'}), 400
    apiKey = md5(str(data).encode()).hexdigest()
    apis[0].update({apiKey: {"name": name,"permission":permission}})
    with open('configs/apis.json', 'w') as file:
        json.dump(apis, file)
    return {"message":"User created","api_key":apiKey}

    

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Error'}), 500
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request'}), 400
@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden'}), 403
@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method Not Allowed'}), 405

if __name__ == '__main__':
    app.run(debug=False, port=2999)
