from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# In-memory data storage
voters = []
candidates = []
elections = []
votes = []

# Voter Registration
@app.route('/', methods=['GET', 'POST'])
def register_voter():
    if request.method == 'GET':
        return app.send_static_file('index.html')
    
    # Get voter data from the request body
    data = request.json
    print(f"Received data: {data}") 
    # Check if the data is valid
    if not data.get('id') or not data.get('name') or not data.get('age'):
        return jsonify({"error": "Missing details."}), 400

    # Check for duplicate voter ID
    if any(voter['id'] == data['id'] for voter in voters):
        return jsonify({"error": "Duplicate ID."}), 400

    # Check if the voter is at least 18 years old
    if int(data['age']) < 18:
        return jsonify({"error": "Voter must be at least 18 years old."}), 400

    # Register the voter
    voters.append(data)
    return jsonify({"message": "Voter registered successfully."}), 201


# Candidate Management
@app.route('/add-candidate', methods=['POST'])
def add_candidate():
    data = request.json
    if not data.get('id') or not data.get('name'):
        return jsonify({"error": "Missing candidate details."}), 400

    if any(candidate['id'] == data['id'] for candidate in candidates):
        return jsonify({"error": "Duplicate candidate ID."}), 400

    candidates.append(data)
    return jsonify({"message": "Candidate added successfully."}), 200

# Election Scheduling
@app.route('/create-election', methods=['POST'])
def create_election():
    data = request.json
    if not data.get('id') or not data.get('name') or not data.get('date'):
        return jsonify({"error": "Missing election details."}), 400

    if any(election['date'] == data['date'] for election in elections):
        return jsonify({"error": "Scheduling conflict on this date."}), 400

    elections.append(data)
    return jsonify({"message": "Election created successfully."}), 201

@app.route('/edit-election/<election_id>', methods=['PUT'])
def edit_election(election_id):
    data = request.json
    election = next((election for election in elections if election['id'] == election_id), None)

    if not election:
        return jsonify({"error": "Election not found."}), 404

    election.update(data)
    return jsonify({"message": "Election updated successfully."}), 200

@app.route('/delete-election/<election_id>', methods=['DELETE'])
def delete_election(election_id):
    global elections
    elections = [election for election in elections if election['id'] != election_id]
    return jsonify({"message": "Election deleted successfully."}), 200

# Vote Casting
@app.route('/cast-vote', methods=['POST'])
def cast_vote():
    data = request.json
    if not data.get('voter_id') or not data.get('election_id') or not data.get('candidate_id'):
        return jsonify({"error": "Missing vote details."}), 400

    if any(vote['voter_id'] == data['voter_id'] and vote['election_id'] == data['election_id'] for vote in votes):
        return jsonify({"error": "Voter has already cast a vote for this election."}), 400

    if not any(voter['id'] == data['voter_id'] for voter in voters):
        return jsonify({"error": "Unauthorized voter."}), 403

    if not any(candidate['id'] == data['candidate_id'] for candidate in candidates):
        return jsonify({"error": "Invalid candidate."}), 400

    votes.append(data)
    return jsonify({"message": "Vote cast successfully."}), 201
@app.route('/view-voters', methods=['GET'])
def view_voters():
    if not voters:
        return jsonify({"message": "No voters registered."}), 404
    return jsonify({"voters": voters}), 200
# Results and Analytics
@app.route('/results/<election_id>', methods=['GET'])
def results(election_id):
    election_votes = [vote for vote in votes if vote['election_id'] == election_id]
    if not election_votes:
        return jsonify({"error": "No votes found for this election."}), 404

    result = {}
    for vote in election_votes:
        candidate_id = vote['candidate_id']
        result[candidate_id] = result.get(candidate_id, 0) + 1

    winner = max(result, key=result.get)
    return jsonify({"results": result, "winner": winner}), 200

# Role-Based Access (Placeholder for future expansion)
# Example for admin-specific route
@app.route('/admin', methods=['GET'])
def admin_panel():
    # Admin functionality goes here
    return jsonify({"message": "Admin panel placeholder."}), 200

if __name__ == '__main__':
    app.run(debug=True)