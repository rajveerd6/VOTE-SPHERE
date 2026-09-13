# app.py
from flask import Flask, request, jsonify, send_from_directory
import os
import database as db

app = Flask(__name__, static_folder=None)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')


# ---------- Admin Auth ----------
@app.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    data = request.get_json() or {}
    if data.get('password') == db.get_setting('admin_password'):
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid admin password"}), 401


# ---------- Candidates ----------
@app.route('/api/candidates', methods=['GET'])
def api_get_candidates():
    return jsonify(db.get_all_candidates())


@app.route('/api/candidates', methods=['POST'])
def api_add_candidate():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({"success": False, "error": "Name required"}), 400
    result = db.add_candidate(name)
    if result is True:
        return jsonify({"success": True})
    return jsonify({"success": False, "error": result}), 400


@app.route('/api/candidates/<int:cid>', methods=['DELETE'])
def api_remove_candidate(cid):
    db.remove_candidate(cid)
    return jsonify({"success": True})


# ---------- Voters ----------
@app.route('/api/voters', methods=['GET'])
def api_get_voters():
    return jsonify(db.get_all_voters())


@app.route('/api/voters', methods=['POST'])
def api_add_voter():
    data = request.get_json() or {}
    roll = (data.get('roll') or '').strip()
    name = (data.get('name') or '').strip()
    gender = data.get('gender', '')

    if not roll or not name or gender not in ('Girl', 'Boy'):
        return jsonify({"success": False, "error": "All fields required"}), 400

    result = db.add_voter(roll, name, gender)
    if result is True:
        return jsonify({"success": True})
    return jsonify({"success": False, "error": result}), 400


@app.route('/api/voters/<roll>', methods=['DELETE'])
def api_remove_voter(roll):
    db.remove_voter(roll)
    return jsonify({"success": True})


# ---------- Verify & Vote ----------
@app.route('/api/voter/verify', methods=['POST'])
def api_verify_voter():
    data = request.get_json() or {}
    roll = (data.get('roll') or '').strip()
    if not roll:
        return jsonify({"success": False, "error": "Roll required"}), 400

    voter = db.get_voter_by_roll(roll)
    if not voter:
        return jsonify({"success": False, "error": "invalid_roll"}), 404

    if db.has_voted(roll):
        return jsonify({"success": False, "error": "already_voted"}), 409

    return jsonify({"success": True, "voter": voter})


@app.route('/api/vote', methods=['POST'])
def api_cast_vote():
    data = request.get_json() or {}
    roll = (data.get('roll') or '').strip()
    candidate_id = data.get('candidate_id')

    if not roll or not candidate_id:
        return jsonify({"success": False, "error": "Missing fields"}), 400

    voter = db.get_voter_by_roll(roll)
    if not voter:
        return jsonify({"success": False, "error": "invalid_roll"}), 404

    if db.has_voted(roll):
        return jsonify({"success": False, "error": "already_voted"}), 409

    result = db.cast_vote(roll, candidate_id, voter['gender'])
    if result is True:
        return jsonify({"success": True})
    return jsonify({"success": False, "error": result}), 400


# ---------- Results (public, no identities) ----------
@app.route('/api/results', methods=['POST'])
def api_results():
    data = request.get_json() or {}
    if data.get('password') != db.get_setting('result_password'):
        return jsonify({"success": False, "error": "Wrong password"}), 401
    return jsonify({"success": True, "results": db.get_results()})


# ---------- Audit (who voted whom — admin only) ----------
@app.route('/api/audit', methods=['POST'])
def api_audit():
    data = request.get_json() or {}
    if data.get('password') != db.get_setting('admin_password'):
        return jsonify({"success": False, "error": "Wrong password"}), 401
    return jsonify({"success": True, "audit": db.get_all_votes()})


# ---------- Admin Actions ----------
@app.route('/api/admin/password', methods=['POST'])
def api_update_password():
    """Update the shared admin/result password."""
    data = request.get_json() or {}
    if data.get('admin_password') != db.get_setting('admin_password'):
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    new_pwd = (data.get('new_password') or '').strip()
    if not new_pwd:
        return jsonify({"success": False, "error": "New password required"}), 400
    db.set_setting('admin_password', new_pwd)
    db.set_setting('result_password', new_pwd)
    return jsonify({"success": True})


@app.route('/api/admin/reset-votes', methods=['POST'])
def api_reset_votes():
    data = request.get_json() or {}
    if data.get('admin_password') != db.get_setting('admin_password'):
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    db.reset_votes()
    return jsonify({"success": True})


@app.route('/api/admin/reset-all', methods=['POST'])
def api_reset_all():
    data = request.get_json() or {}
    if data.get('admin_password') != db.get_setting('admin_password'):
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    db.reset_everything()
    return jsonify({"success": True})


if __name__ == '__main__':
    db.init_db()
    app.run(debug=True, port=5000)