import pytest
from flask import Flask, jsonify
from app import app, voters, candidates, elections, votes  # Import the Flask app and data stores

@pytest.fixture
def client():
    # This fixture provides the test client for making HTTP requests
    with app.test_client() as client:
        yield client

# Unit Test: Voter Registration
def test_register_voter(client):
    # Test valid voter registration
    response = client.post('/', json={
        'id': 'voter1',
        'name': 'John Doe',
        'age': 30
    })
    assert response.status_code == 201
    assert b'Voter registered successfully' in response.data

    # Test missing details
    response = client.post('/', json={'id': 'voter2'})
    assert response.status_code == 400
    assert b'Missing details.' in response.data

    # Test duplicate voter ID
    client.post('/', json={'id': 'voter1', 'name': 'John Doe', 'age': 30})  # Re-register same voter
    response = client.post('/', json={'id': 'voter1', 'name': 'Jane Doe', 'age': 25})
    assert response.status_code == 400
    assert b'Duplicate ID.' in response.data

    # Test voter under 18
    response = client.post('/', json={'id': 'voter3', 'name': 'Alice', 'age': 17})
    assert response.status_code == 400
    assert b'Voter must be at least 18 years old.' in response.data

# Unit Test: Add Candidate
def test_add_candidate(client):
    # Test valid candidate addition
    response = client.post('/add-candidate', json={
        'id': 'candidate1',
        'name': 'Candidate A'
    })
    assert response.status_code == 200
    assert b'Candidate added successfully' in response.data

    # Test missing candidate details
    response = client.post('/add-candidate', json={'id': 'candidate2'})
    assert response.status_code == 400
    assert b'Missing candidate details.' in response.data

    # Test duplicate candidate ID
    client.post('/add-candidate', json={'id': 'candidate1', 'name': 'Candidate A'})  # Add same candidate again
    response = client.post('/add-candidate', json={'id': 'candidate1', 'name': 'Candidate A'})
    assert response.status_code == 400
    assert b'Duplicate candidate ID.' in response.data

# Unit Test: Create Election
def test_create_election(client):
    # Test valid election creation
    response = client.post('/create-election', json={
        'id': 'election1',
        'name': 'Election 2024',
        'date': '2024-12-29'
    })
    assert response.status_code == 201
    assert b'Election created successfully' in response.data

    # Test missing election details
    response = client.post('/create-election', json={'id': 'election2'})
    assert response.status_code == 400
    assert b'Missing election details.' in response.data

    # Test scheduling conflict
    client.post('/create-election', json={'id': 'election3', 'name': 'Election 2025', 'date': '2024-12-29'})
    response = client.post('/create-election', json={'id': 'election4', 'name': 'Election 2026', 'date': '2024-12-29'})
    assert response.status_code == 400
    assert b'Scheduling conflict on this date.' in response.data

# Unit Test: Cast Vote
def test_cast_vote(client):
    # Add voter and candidate first
    client.post('/', json={'id': 'voter1', 'name': 'John Doe', 'age': 30})
    client.post('/add-candidate', json={'id': 'candidate1', 'name': 'Candidate A'})
    client.post('/create-election', json={'id': 'election1', 'name': 'Election 2024', 'date': '2024-12-29'})

    # Test valid vote casting
    response = client.post('/cast-vote', json={
        'voter_id': 'voter1',
        'election_id': 'election1',
        'candidate_id': 'candidate1'
    })
    assert response.status_code == 201
    assert b'Vote cast successfully' in response.data

    # Test missing vote details
    response = client.post('/cast-vote', json={'voter_id': 'voter1'})
    assert response.status_code == 400
    assert b'Missing vote details.' in response.data

    # Test duplicate vote from same voter
    response = client.post('/cast-vote', json={
        'voter_id': 'voter1',
        'election_id': 'election1',
        'candidate_id': 'candidate1'
    })
    assert response.status_code == 400
    assert b'Voter has already cast a vote for this election.' in response.data

    # Test invalid candidate
    response = client.post('/cast-vote', json={
        'voter_id': 'voter1',
        'election_id': 'election1',
        'candidate_id': 'candidate2'
    })
    assert response.status_code == 400
    assert b'Invalid candidate.' in response.data

# Unit Test: View Election Results
def test_view_results(client):
    # Add voter, candidate, and election first
    client.post('/', json={'id': 'voter1', 'name': 'John Doe', 'age': 30})
    client.post('/add-candidate', json={'id': 'candidate1', 'name': 'Candidate A'})
    client.post('/create-election', json={'id': 'election1', 'name': 'Election 2024', 'date': '2024-12-29'})
    client.post('/cast-vote', json={
        'voter_id': 'voter1',
        'election_id': 'election1',
        'candidate_id': 'candidate1'
    })

    # Test valid results retrieval
    response = client.get('/results/election1')
    assert response.status_code == 200
    assert b'Candidate A' in response.data
    assert b'Winner' in response.data

    # Test results with no votes
    response = client.get('/results/election2')  # No votes cast for election2
    assert response.status_code == 404
    assert b'No votes found for this election.' in response.data
