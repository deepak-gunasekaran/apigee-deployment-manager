#!/usr/bin/env python3
"""
Apigee Deployment Web Application
Provides a web interface for managing Apigee API proxies, shared flows, target servers, and KVMs
"""

import os
import json
import zipfile
import tempfile
import requests
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'apigee-deployment-secret-key-2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Static credentials (in production, use environment variables or secure storage)
USERS = {
    'apigee_admin': generate_password_hash('ApigeeAdmin2024!')
}

# Apigee API base URLs
APIGEE_BASE_URL = "https://apigee.googleapis.com/v1"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_auth_headers():
    """Get authorization headers using stored GCP token"""
    token = session.get('gcp_token')
    if not token:
        return None
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in USERS and check_password_hash(USERS[username], password):
            session['logged_in'] = True
            session['username'] = username
            flash('Successfully logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Successfully logged out!', 'success')
    return redirect(url_for('login'))

@app.route('/auth', methods=['GET', 'POST'])
@login_required
def auth():
    if request.method == 'POST':
        token = request.form['gcp_token'].strip()
        print(f"[DEBUG] Received token for validation: {token[:50]}...")
        if token:
            # Validate token by making a test API call
            headers = {'Authorization': f'Bearer {token}'}
            try:
                response = requests.get(f'{APIGEE_BASE_URL}/organizations', headers=headers, timeout=10)
                print(f"[DEBUG] Token validation response: {response.status_code}")
                if response.status_code == 200:
                    session['gcp_token'] = token
                    session.permanent = True
                    print(f"[DEBUG] Token stored in session. Session ID: {session.get('_id', 'N/A')}")
                    flash('GCP token validated and stored successfully!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash(f'Invalid GCP token. API returned: {response.status_code}', 'error')
            except Exception as e:
                print(f"[DEBUG] Token validation error: {str(e)}")
                flash(f'Error validating token: {str(e)}', 'error')
        else:
            flash('Please provide a GCP token', 'error')
    
    return render_template('auth.html')

@app.route('/api/organizations')
@login_required
def get_organizations():
    """Get list of Apigee organizations"""
    print(f"[DEBUG] Session contents: {dict(session)}")
    headers = get_auth_headers()
    print(f"[DEBUG] Auth headers: {headers}")
    
    if not headers:
        print("[DEBUG] No auth headers found, using fallback organizations")
        # Fallback to hardcoded organizations if no token
        return jsonify({
            'organizations': [
                'irx-apm1081130-slvr-01q6',
                'irx-apm1082662-slvr-013l', 
                'irx-apm1082662-gld-01c5',
                'test-org-1',
                'test-org-2'
            ]
        })
    
    try:
        print(f"[DEBUG] Making API call to {APIGEE_BASE_URL}/organizations")
        response = requests.get(f'{APIGEE_BASE_URL}/organizations', headers=headers, timeout=10)
        print(f"[DEBUG] API Response Status: {response.status_code}")
        print(f"[DEBUG] API Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[DEBUG] Raw API Response received")
            
            # FORCE: Always extract and return only organization names as strings
            organizations = []
            
            # Handle Apigee API response format: {"organizations": [{"organization": "name", ...}, ...]}
            if isinstance(data, dict) and 'organizations' in data:
                for org_obj in data['organizations']:
                    if isinstance(org_obj, dict) and 'organization' in org_obj:
                        organizations.append(str(org_obj['organization']))
            
            print(f"[DEBUG] Extracted {len(organizations)} organization names")
            
            # NEVER return raw API response - always return parsed strings
            return jsonify({'organizations': organizations})
        else:
            print(f"[DEBUG] API Error: {response.status_code} - {response.text}")
            # Fallback to hardcoded list on API error
            return jsonify({
                'organizations': [
                    'irx-apm1081130-slvr-01q6',
                    'irx-apm1082662-slvr-013l', 
                    'irx-apm1082662-gld-01c5',
                    'test-org-1',
                    'test-org-2'
                ]
            })
            
    except Exception as e:
        print(f"[DEBUG] Exception occurred: {str(e)}")
        # Fallback to hardcoded list on exception
        return jsonify({
            'organizations': [
                'irx-apm1081130-slvr-01q6',
                'irx-apm1082662-slvr-013l', 
                'irx-apm1082662-gld-01c5',
                'test-org-1',
                'test-org-2'
            ]
        })

@app.route('/api/organizations/<org>/environments')
@login_required
def get_environments(org):
    """Get environments for a specific organization"""
    headers = get_auth_headers()
    if not headers:
        return jsonify({'error': 'No GCP token provided'}), 401
    
    try:
        response = requests.get(f'{APIGEE_BASE_URL}/organizations/{org}/environments', headers=headers, timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': f'API error: {response.status_code}'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizations/<org>/apis')
@login_required
def get_api_proxies(org):
    """Get API proxies for a specific organization"""
    headers = get_auth_headers()
    if not headers:
        return jsonify({'error': 'No GCP token provided'}), 401
    
    try:
        response = requests.get(f'{APIGEE_BASE_URL}/organizations/{org}/apis', headers=headers, timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': f'API error: {response.status_code}'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizations/<org>/sharedflows')
@login_required
def get_shared_flows(org):
    """Get shared flows for a specific organization"""
    headers = get_auth_headers()
    if not headers:
        return jsonify({'error': 'No GCP token provided'}), 401
    
    try:
        response = requests.get(f'{APIGEE_BASE_URL}/organizations/{org}/sharedflows', headers=headers, timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': f'API error: {response.status_code}'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizations/<org>/environments/<env>/sharedflows/deployments')
@login_required
def get_deployed_shared_flows(org, env):
    """Get deployed shared flows for a specific organization and environment"""
    headers = get_auth_headers()
    if not headers:
        return jsonify({'error': 'No GCP token provided'}), 401
    
    try:
        response = requests.get(f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/sharedflows', headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"[DEBUG] Deployed shared flows for {org}/{env}: {json.dumps(data, indent=2)}")
            return jsonify(data)
        else:
            print(f"[DEBUG] Deployed shared flows API error: {response.status_code} - {response.text}")
            return jsonify({'error': f'API error: {response.status_code}'}), response.status_code
    except Exception as e:
        print(f"[DEBUG] Deployed shared flows exception: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizations/<org>/environments/<env>/targetservers')
@login_required
def get_target_servers(org, env):
    """Get target servers for a specific environment"""
    headers = get_auth_headers()
    if not headers:
        return jsonify({'error': 'No GCP token provided'}), 401
    
    try:
        response = requests.get(f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/targetservers', headers=headers, timeout=10)
        print(f"[DEBUG] Target servers API response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[DEBUG] Target servers raw data: {json.dumps(data, indent=2)}")
            
            # Parse target servers response - Apigee returns array of target server names
            target_servers = []
            if isinstance(data, list):
                # If it's a list of names, fetch details for each
                for ts_name in data:
                    ts_response = requests.get(f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/targetservers/{ts_name}', headers=headers, timeout=10)
                    if ts_response.status_code == 200:
                        ts_data = ts_response.json()
                        target_servers.append(ts_data)
                        print(f"[DEBUG] Target server {ts_name} details: {json.dumps(ts_data, indent=2)}")
            elif isinstance(data, dict) and 'targetServers' in data:
                target_servers = data['targetServers']
            else:
                target_servers = data if isinstance(data, list) else []
            
            print(f"[DEBUG] Returning {len(target_servers)} target servers")
            return jsonify(target_servers)
        else:
            print(f"[DEBUG] Target servers API error: {response.status_code} - {response.text}")
            return jsonify({'error': f'API error: {response.status_code}'}), response.status_code
    except Exception as e:
        print(f"[DEBUG] Target servers exception: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizations/<org>/environments/<env>/keyvaluemaps')
@login_required
def get_kvms(org, env):
    """Get KVMs for a specific environment"""
    headers = get_auth_headers()
    if not headers:
        return jsonify({'error': 'No GCP token provided'}), 401
    
    try:
        response = requests.get(f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/keyvaluemaps', headers=headers, timeout=10)
        print(f"[DEBUG] KVMs API response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"[DEBUG] KVMs data: {json.dumps(data, indent=2)}")
            return jsonify(data)
        else:
            print(f"[DEBUG] KVMs API error: {response.status_code} - {response.text}")
            return jsonify({'error': f'API error: {response.status_code}', 'details': response.text}), response.status_code
    except Exception as e:
        print(f"[DEBUG] KVMs exception: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizations/<org>/environments/<env>/keyvaluemaps', methods=['POST'])
@login_required
def create_kvm(org, env):
    """Create a new KVM in a specific environment"""
    headers = get_auth_headers()
    if not headers:
        return jsonify({'error': 'No GCP token provided'}), 401
    
    try:
        data = request.json
        print(f"[DEBUG] Creating KVM in {org}/{env}: {json.dumps(data, indent=2)}")
        
        url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/keyvaluemaps'
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"[DEBUG] KVM creation response: {response.status_code}")
        if response.status_code in [200, 201]:
            return jsonify({'success': True, 'data': response.json()})
        else:
            print(f"[DEBUG] KVM creation error: {response.status_code} - {response.text}")
            return jsonify({'error': f'API error: {response.status_code}', 'details': response.text}), response.status_code
    except Exception as e:
        print(f"[DEBUG] KVM creation exception: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizations/<org>/environments/<env>/keyvaluemaps/<kvm>', methods=['DELETE'])
@login_required
def delete_kvm(org, env, kvm):
    """Delete a KVM from a specific environment"""
    headers = get_auth_headers()
    if not headers:
        return jsonify({'error': 'No GCP token provided'}), 401
    
    try:
        url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/keyvaluemaps/{kvm}'
        response = requests.delete(url, headers=headers, timeout=30)
        
        print(f"[DEBUG] KVM deletion response: {response.status_code}")
        if response.status_code in [200, 204]:
            return jsonify({'success': True, 'message': 'KVM deleted successfully'})
        else:
            print(f"[DEBUG] KVM deletion error: {response.status_code} - {response.text}")
            return jsonify({'error': f'API error: {response.status_code}', 'details': response.text}), response.status_code
    except Exception as e:
        print(f"[DEBUG] KVM deletion exception: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizations/<org>/environments/<env>/keyvaluemaps/<kvm>/entries', methods=['GET', 'POST', 'PUT'])
@login_required
def manage_kvm_entries(org, env, kvm):
    """Get, create, or update KVM entries"""
    headers = get_auth_headers()
    if not headers:
        return jsonify({'error': 'No GCP token provided'}), 401
    
    try:
        url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/keyvaluemaps/{kvm}/entries'
        
        if request.method == 'GET':
            # Get KVM entries
            response = requests.get(url, headers=headers, timeout=10)
            print(f"[DEBUG] KVM entries API response: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"[DEBUG] KVM entries data: {json.dumps(data, indent=2)}")
                return jsonify(data)
            else:
                print(f"[DEBUG] KVM entries API error: {response.status_code} - {response.text}")
                return jsonify({'error': f'API error: {response.status_code}', 'details': response.text}), response.status_code
        else:
            # Create or update KVM entries
            data = request.json
            if request.method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
                print(f"[DEBUG] KVM entry creation response: {response.status_code}")
            else:
                response = requests.put(url, headers=headers, json=data, timeout=30)
                print(f"[DEBUG] KVM entry update response: {response.status_code}")
            
            if response.status_code in [200, 201]:
                return jsonify({'success': True, 'data': response.json()})
            else:
                print(f"[DEBUG] KVM entry {request.method} error: {response.status_code} - {response.text}")
                return jsonify({'error': f'API error: {response.status_code}', 'details': response.text}), response.status_code
                
    except Exception as e:
        print(f"[DEBUG] KVM entries exception: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizations/<org>/environments/<env>/keyvaluemaps/<kvm>/entries/<key>', methods=['PUT', 'DELETE'])
@login_required
def manage_kvm_entry(org, env, kvm, key):
    """Update or delete a specific KVM entry"""
    headers = get_auth_headers()
    if not headers:
        return jsonify({'error': 'No GCP token provided'}), 401
    
    try:
        url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/keyvaluemaps/{kvm}/entries/{key}'
        
        if request.method == 'PUT':
            # Update KVM entry
            data = request.json
            response = requests.put(url, headers=headers, json=data, timeout=30)
            print(f"[DEBUG] KVM entry update response: {response.status_code}")
        else:
            # Delete KVM entry
            response = requests.delete(url, headers=headers, timeout=30)
            print(f"[DEBUG] KVM entry delete response: {response.status_code}")
        
        if response.status_code in [200, 201, 204]:
            return jsonify({'success': True, 'message': f'KVM entry {request.method.lower()}d successfully'})
        else:
            print(f"[DEBUG] KVM entry {request.method} error: {response.status_code} - {response.text}")
            return jsonify({'error': f'API error: {response.status_code}', 'details': response.text}), response.status_code
    except Exception as e:
        print(f"[DEBUG] KVM entry {request.method} exception: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/deploy', methods=['GET', 'POST'])
@login_required
def deploy():
    if request.method == 'POST':
        deployment_type = request.form.get('deployment_type')
        org = request.form.get('organization')
        env = request.form.get('environment')
        
        if deployment_type == 'api_proxy':
            return handle_api_proxy_deployment(org, env)
        elif deployment_type == 'shared_flow':
            return handle_shared_flow_deployment(org, env)
    
    return render_template('deploy.html')

def handle_api_proxy_deployment(org, env):
    """Handle API proxy deployment"""
    headers = get_auth_headers()
    if not headers:
        flash('No GCP token provided', 'error')
        return redirect(url_for('deploy'))
    
    # Check if it's a file upload (new or existing with new code)
    file = None
    proxy_name = None
    
    if 'proxy_file' in request.files and request.files['proxy_file'].filename:
        # New proxy deployment
        file = request.files['proxy_file']
        proxy_name = request.form.get('proxy_name') or file.filename.replace('.zip', '')
    elif 'existing_proxy_file' in request.files and request.files['existing_proxy_file'].filename:
        # Existing proxy with new code upload
        file = request.files['existing_proxy_file']
        proxy_name = request.form.get('existing_proxy')  # Get proxy name from dropdown
        if not proxy_name:
            flash('Please select an existing proxy when uploading new code', 'error')
            return redirect(url_for('deploy'))
    
    if file and file.filename.endswith('.zip'):
        # Handle file upload (both new and existing proxy with new code)
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Import the proxy
            with open(filepath, 'rb') as f:
                files = {'file': f}
                import_url = f'{APIGEE_BASE_URL}/organizations/{org}/apis?action=import&name={proxy_name}'
                response = requests.post(import_url, headers={'Authorization': headers['Authorization']}, files=files, timeout=30)
            
            if response.status_code in [200, 201]:
                revision = response.json().get('revision', '1')
                
                # Deploy the proxy with override flag
                deploy_url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/apis/{proxy_name}/revisions/{revision}/deployments?override=true'
                deploy_response = requests.post(deploy_url, headers=headers, timeout=30)
                
                if deploy_response.status_code in [200, 201]:
                    flash(f'API proxy {proxy_name} deployed successfully to {env}!', 'success')
                else:
                    flash(f'Import successful but deployment failed: {deploy_response.text}', 'error')
            else:
                flash(f'Import failed: {response.text}', 'error')
            
            # Clean up uploaded file
            os.remove(filepath)
            
        except Exception as e:
            flash(f'Deployment error: {str(e)}', 'error')
            if os.path.exists(filepath):
                os.remove(filepath)
    elif file:
        flash('Please upload a valid ZIP file', 'error')
    else:
        # Existing proxy deployment
        proxy_name = request.form.get('existing_proxy')
        revision = request.form.get('revision', '1')
        
        print(f"[DEBUG] Existing proxy deployment - proxy_name: {proxy_name}, revision: {revision}")
        print(f"[DEBUG] All form data: {dict(request.form)}")
        
        if proxy_name:
            try:
                deploy_url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/apis/{proxy_name}/revisions/{revision}/deployments?override=true'
                response = requests.post(deploy_url, headers=headers, timeout=30)
                
                if response.status_code in [200, 201]:
                    flash(f'API proxy {proxy_name} revision {revision} deployed successfully to {env}!', 'success')
                else:
                    flash(f'Deployment failed: {response.text}', 'error')
            except Exception as e:
                flash(f'Deployment error: {str(e)}', 'error')
        else:
            flash('Please select a proxy to deploy', 'error')
    
    return redirect(url_for('deploy'))

def handle_shared_flow_deployment(org, env):
    """Handle shared flow deployment"""
    headers = get_auth_headers()
    if not headers:
        flash('No GCP token provided', 'error')
        return redirect(url_for('deploy'))
    
    # Check if it's a file upload (new or existing with new code)
    file = None
    sharedflow_name = None
    
    if 'sharedflow_file' in request.files and request.files['sharedflow_file'].filename:
        # New shared flow deployment
        file = request.files['sharedflow_file']
        sharedflow_name = request.form.get('sharedflow_name') or file.filename.replace('.zip', '')
    elif 'existing_sharedflow_file' in request.files and request.files['existing_sharedflow_file'].filename:
        # Existing shared flow with new code upload
        file = request.files['existing_sharedflow_file']
        sharedflow_name = request.form.get('existing_sharedflow')  # Get shared flow name from dropdown
        if not sharedflow_name:
            flash('Please select an existing shared flow when uploading new code', 'error')
            return redirect(url_for('deploy'))
    
    if file and file.filename.endswith('.zip'):
        # Handle file upload (both new and existing shared flow with new code)
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Import the shared flow
            with open(filepath, 'rb') as f:
                files = {'file': f}
                import_url = f'{APIGEE_BASE_URL}/organizations/{org}/sharedflows?action=import&name={sharedflow_name}'
                response = requests.post(import_url, headers={'Authorization': headers['Authorization']}, files=files, timeout=30)
            
            if response.status_code in [200, 201]:
                revision = response.json().get('revision', '1')
                
                # Deploy the shared flow with override flag
                deploy_url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/sharedflows/{sharedflow_name}/revisions/{revision}/deployments?override=true'
                deploy_response = requests.post(deploy_url, headers=headers, timeout=30)
                
                if deploy_response.status_code in [200, 201]:
                    flash(f'Shared flow {sharedflow_name} deployed successfully to {env}!', 'success')
                else:
                    flash(f'Import successful but deployment failed: {deploy_response.text}', 'error')
            else:
                flash(f'Import failed: {response.text}', 'error')
            
            # Clean up uploaded file
            os.remove(filepath)
            
        except Exception as e:
            flash(f'Deployment error: {str(e)}', 'error')
            if os.path.exists(filepath):
                os.remove(filepath)
    elif file:
        flash('Please upload a valid ZIP file', 'error')
    else:
        # Existing shared flow deployment
        sharedflow_name = request.form.get('existing_sharedflow')
        revision = request.form.get('sf_revision', '1')
        
        print(f"[DEBUG] Existing shared flow deployment - sharedflow_name: {sharedflow_name}, revision: {revision}")
        print(f"[DEBUG] All form data: {dict(request.form)}")
        
        if sharedflow_name:
            try:
                deploy_url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/sharedflows/{sharedflow_name}/revisions/{revision}/deployments?override=true'
                response = requests.post(deploy_url, headers=headers, timeout=30)
                
                if response.status_code in [200, 201]:
                    flash(f'Shared flow {sharedflow_name} revision {revision} deployed successfully to {env}!', 'success')
                else:
                    flash(f'Deployment failed: {response.text}', 'error')
            except Exception as e:
                flash(f'Deployment error: {str(e)}', 'error')
        else:
            flash('Please select a shared flow to deploy', 'error')
    
    return redirect(url_for('deploy'))


@app.route('/test')
@login_required
def test_page():
    """Test page for debugging organization dropdown"""
    return send_from_directory('.', 'test_org_dropdown.html')

@app.route('/manage')
@login_required
def manage():
    return render_template('manage.html')

@app.route('/api/organizations/<org>/environments/<env>/targetservers', methods=['POST'])
@login_required
def create_target_server(org, env):
    """Create a new target server"""
    headers = get_auth_headers()
    if not headers:
        return jsonify({'error': 'No GCP token provided'}), 401
    
    try:
        data = request.json
        print(f"[DEBUG] Creating target server in {org}/{env}: {json.dumps(data, indent=2)}")
        
        url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/targetservers'
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"[DEBUG] Target server creation response: {response.status_code}")
        if response.status_code in [200, 201]:
            return jsonify({'success': True, 'data': response.json()})
        else:
            print(f"[DEBUG] Target server creation error: {response.status_code} - {response.text}")
            return jsonify({'error': f'API error: {response.status_code}', 'details': response.text}), response.status_code
    except Exception as e:
        print(f"[DEBUG] Target server creation exception: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizations/<org>/targetservers/multi', methods=['POST', 'PUT', 'DELETE'])
@login_required
def manage_target_server_multi_env(org):
    """Create, update, or delete target server across multiple environments"""
    headers = get_auth_headers()
    if not headers:
        return jsonify({'error': 'No GCP token provided'}), 401
    
    try:
        data = request.json
        environments = data.get('environments', [])
        server_name = data.get('name')
        
        if not environments:
            return jsonify({'error': 'No environments specified'}), 400
        
        results = []
        errors = []
        
        for env in environments:
            try:
                # Create a clean payload without the 'environments' field for Apigee API
                clean_data = {k: v for k, v in data.items() if k != 'environments'}
                print(f"[DEBUG] Clean data for {env}: {json.dumps(clean_data, indent=2)}")
                
                if request.method == 'POST':
                    # Create target server
                    url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/targetservers'
                    response = requests.post(url, headers=headers, json=clean_data, timeout=30)
                elif request.method == 'PUT':
                    # Update target server
                    url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/targetservers/{server_name}'
                    response = requests.put(url, headers=headers, json=clean_data, timeout=30)
                else:
                    # Delete target server
                    url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/targetservers/{server_name}'
                    response = requests.delete(url, headers=headers, timeout=30)
                
                if response.status_code in [200, 201, 204]:
                    results.append({
                        'environment': env,
                        'success': True,
                        'status': response.status_code
                    })
                elif response.status_code == 409:
                    # Handle conflict (already exists) as a special case
                    error_details = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'message': response.text}
                    message = error_details.get('error', {}).get('message', 'Target server already exists')
                    
                    if request.method == 'POST':
                        # For creation, 409 is an error but with helpful message
                        errors.append({
                            'environment': env,
                            'error': f'Already exists: {message}',
                            'details': response.text,
                            'status': 409
                        })
                    else:
                        # For update/delete, 409 might be expected, treat as warning
                        results.append({
                            'environment': env,
                            'success': True,
                            'status': response.status_code,
                            'warning': f'Target server already exists: {message}'
                        })
                else:
                    errors.append({
                        'environment': env,
                        'error': f'API error: {response.status_code}',
                        'details': response.text,
                        'status': response.status_code
                    })
                    
            except Exception as e:
                errors.append({
                    'environment': env,
                    'error': str(e)
                })
        
        return jsonify({
            'results': results,
            'errors': errors,
            'success_count': len(results),
            'error_count': len(errors)
        })
        
    except Exception as e:
        print(f"[DEBUG] Multi-env target server operation exception: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizations/<org>/environments/<env>/targetservers/<server>', methods=['PUT', 'DELETE'])
@login_required
def manage_target_server(org, env, server):
    """Update or delete target server configuration"""
    headers = get_auth_headers()
    if not headers:
        return jsonify({'error': 'No GCP token provided'}), 401
    
    try:
        url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/targetservers/{server}'
        
        if request.method == 'PUT':
            data = request.json
            response = requests.put(url, headers=headers, json=data, timeout=30)
            print(f"[DEBUG] Target server update response: {response.status_code}")
        else:
            response = requests.delete(url, headers=headers, timeout=30)
            print(f"[DEBUG] Target server delete response: {response.status_code}")
        
        if response.status_code in [200, 201, 204]:
            return jsonify({'success': True, 'message': f'Target server {request.method.lower()}d successfully'})
        else:
            print(f"[DEBUG] Target server {request.method} error: {response.status_code} - {response.text}")
            return jsonify({'error': f'API error: {response.status_code}', 'details': response.text}), response.status_code
    except Exception as e:
        print(f"[DEBUG] Target server {request.method} exception: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizations/<org>/keyvaluemaps/multi', methods=['POST', 'PUT', 'DELETE'])
@login_required
def manage_kvm_multi_env(org):
    """Create, update, or delete KVM across multiple environments"""
    headers = get_auth_headers()
    if not headers:
        return jsonify({'error': 'No GCP token provided'}), 401
    
    try:
        data = request.json
        environments = data.get('environments', [])
        kvm_name = data.get('name')
        
        if not environments:
            return jsonify({'error': 'No environments specified'}), 400
        
        results = []
        errors = []
        
        for env in environments:
            try:
                # Create a clean payload without the 'environments' field for Apigee API
                clean_data = {k: v for k, v in data.items() if k != 'environments'}
                print(f"[DEBUG] Clean KVM data for {env}: {json.dumps(clean_data, indent=2)}")
                
                if request.method == 'POST':
                    # Create KVM
                    url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/keyvaluemaps'
                    response = requests.post(url, headers=headers, json=clean_data, timeout=30)
                elif request.method == 'PUT':
                    # Update KVM (note: KVMs themselves don't typically get updated, but we can handle it)
                    url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/keyvaluemaps/{kvm_name}'
                    response = requests.put(url, headers=headers, json=clean_data, timeout=30)
                else:
                    # Delete KVM (with optional entry deletion first)
                    if clean_data.get('deleteEntriesFirst') and clean_data.get('entryKeys'):
                        # First delete specified entries
                        entry_deletion_errors = []
                        for entry_key in clean_data['entryKeys']:
                            try:
                                entry_url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/keyvaluemaps/{kvm_name}/entries/{entry_key}'
                                entry_response = requests.delete(entry_url, headers=headers, timeout=30)
                                if entry_response.status_code not in [200, 204, 404]:  # 404 is OK if entry doesn't exist
                                    entry_deletion_errors.append(f"Entry '{entry_key}': {entry_response.status_code}")
                            except Exception as e:
                                entry_deletion_errors.append(f"Entry '{entry_key}': {str(e)}")
                        
                        # Log entry deletion results
                        if entry_deletion_errors:
                            print(f"[DEBUG] Entry deletion errors in {env}: {entry_deletion_errors}")
                    
                    # Now delete the KVM itself
                    url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/keyvaluemaps/{kvm_name}'
                    response = requests.delete(url, headers=headers, timeout=30)
                
                if response.status_code in [200, 201, 204]:
                    results.append({
                        'environment': env,
                        'success': True,
                        'status': response.status_code
                    })
                elif response.status_code == 409:
                    # Handle conflict (already exists) as a special case
                    error_details = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'message': response.text}
                    message = error_details.get('error', {}).get('message', 'KVM already exists')
                    
                    if request.method == 'POST':
                        # For creation, 409 is an error but with helpful message
                        errors.append({
                            'environment': env,
                            'error': f'Already exists: {message}',
                            'details': response.text,
                            'status': 409
                        })
                    else:
                        # For update/delete, 409 might be expected, treat as warning
                        results.append({
                            'environment': env,
                            'success': True,
                            'status': response.status_code,
                            'warning': f'KVM already exists: {message}'
                        })
                else:
                    errors.append({
                        'environment': env,
                        'error': f'API error: {response.status_code}',
                        'details': response.text,
                        'status': response.status_code
                    })
                    
            except Exception as e:
                errors.append({
                    'environment': env,
                    'error': str(e)
                })
        
        return jsonify({
            'results': results,
            'errors': errors,
            'success_count': len(results),
            'error_count': len(errors)
        })
        
    except Exception as e:
        print(f"[DEBUG] Multi-env KVM operation exception: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizations/<org>/keyvaluemaps/<kvm>/entries/multi', methods=['POST', 'PUT', 'DELETE'])
@login_required
def manage_kvm_entries_multi_env(org, kvm):
    """Create, update, or delete KVM entries across multiple environments"""
    headers = get_auth_headers()
    if not headers:
        return jsonify({'error': 'No GCP token provided'}), 401
    
    try:
        data = request.json
        environments = data.get('environments', [])
        entry_key = data.get('name') or data.get('key')
        
        if not environments:
            return jsonify({'error': 'No environments specified'}), 400
        
        results = []
        errors = []
        
        for env in environments:
            try:
                # Create a clean payload without the 'environments' field for Apigee API
                clean_data = {k: v for k, v in data.items() if k != 'environments'}
                print(f"[DEBUG] Clean KVM entry data for {env}: {json.dumps(clean_data, indent=2)}")
                
                if request.method == 'POST':
                    # Create KVM entry
                    url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/keyvaluemaps/{kvm}/entries'
                    response = requests.post(url, headers=headers, json=clean_data, timeout=30)
                elif request.method == 'PUT':
                    # Update KVM entry
                    url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/keyvaluemaps/{kvm}/entries/{entry_key}'
                    response = requests.put(url, headers=headers, json=clean_data, timeout=30)
                else:
                    # Delete KVM entry
                    url = f'{APIGEE_BASE_URL}/organizations/{org}/environments/{env}/keyvaluemaps/{kvm}/entries/{entry_key}'
                    response = requests.delete(url, headers=headers, timeout=30)
                
                if response.status_code in [200, 201, 204]:
                    results.append({
                        'environment': env,
                        'success': True,
                        'status': response.status_code
                    })
                elif response.status_code == 409:
                    # Handle conflict (already exists) as a special case
                    error_details = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'message': response.text}
                    message = error_details.get('error', {}).get('message', 'KVM entry already exists')
                    
                    if request.method == 'POST':
                        # For creation, 409 is an error but with helpful message
                        errors.append({
                            'environment': env,
                            'error': f'Already exists: {message}',
                            'details': response.text,
                            'status': 409
                        })
                    else:
                        # For update/delete, 409 might be expected, treat as warning
                        results.append({
                            'environment': env,
                            'success': True,
                            'status': response.status_code,
                            'warning': f'KVM entry already exists: {message}'
                        })
                else:
                    errors.append({
                        'environment': env,
                        'error': f'API error: {response.status_code}',
                        'details': response.text,
                        'status': response.status_code
                    })
                    
            except Exception as e:
                errors.append({
                    'environment': env,
                    'error': str(e)
                })
        
        return jsonify({
            'results': results,
            'errors': errors,
            'success_count': len(results),
            'error_count': len(errors)
        })
        
    except Exception as e:
        print(f"[DEBUG] Multi-env KVM entries operation exception: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
