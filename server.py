from flask import Flask, request, jsonify
import scrape

app = Flask(__name__)

# Global storage for received tokens
stored_tokens = []

def extract_addresses(data):
    """
    Extract pool address and token_mint_two address from transaction data.
    
    Args:
        data (dict): JSON data containing transaction information
        
    Returns:
        tuple: (pool_address, token_mint_two) or (None, None) if not found
    """
    try:
        # Check if data is a dictionary
        if not isinstance(data, dict):
            print("Error: Input data is not a dictionary")
            return None, None
        
        # Initialize variables
        pool_address = None
        token_mint_two = None
        
        # Check for actions list
        if 'actions' not in data or not isinstance(data['actions'], list):
            print("Error: 'actions' field missing or not a list")
            return None, None
        
        # Search for CREATE_POOL action
        for action in data['actions']:
            if action.get('type') == 'CREATE_POOL' and 'info' in action:
                info = action['info']
                
                # Extract pool address
                if 'liquidity_pool_address' in info:
                    pool_address = info['liquidity_pool_address']
                
                # Extract token_mint_two
                if 'token_mint_two' in info:
                    token_mint_two = info['token_mint_two']
                
                # Once we find the CREATE_POOL action, we can break out of the loop
                break
        
        # Verify both values were found
        if pool_address is None:
            print("Warning: 'liquidity_pool_address' not found in CREATE_POOL action")
        
        if token_mint_two is None:
            print("Warning: 'token_mint_two' not found in CREATE_POOL action")
            
        return pool_address, token_mint_two
        
    except Exception as e:
        print(f"Error extracting addresses: {str(e)}")
        return None, None

@app.route('/', methods=['POST', 'GET'])  # Add GET for testing
def handle_callback():
    print("=== Callback Hit ===")
    print("Method:", request.method)
    print("Headers:", dict(request.headers))
    print("Raw Body:", request.data)
    try:
        data = request.get_json(force=True, silent=True)
        pool_address, mint_address = extract_addresses(data)
        
        # Store the new token info if valid
        if pool_address and mint_address:
            timestamp = data.get('timestamp', '')
            token_info = {
                'timestamp': timestamp,
                'pool_address': pool_address,
                'mint_address': mint_address
            }
            
            # Add to the tokens list
            stored_tokens.append(token_info)
            print(f"New token stored: {token_info}")
            print(f"Total tokens waiting to be fetched: {len(stored_tokens)}")
        
    except Exception as e:
        print("JSON parsing failed:", str(e))
        data = None
    
    return jsonify({'status': 'received'}), 200

@app.route('/get_crypto_tokens', methods=['GET'])
def get_crypto_tokens():
    """Return all newly received tokens and clear the storage"""
    global stored_tokens
    
    # Get current tokens
    current_tokens = stored_tokens.copy()
    token_count = len(current_tokens)
    
    # Clear the tokens list for new ones
    stored_tokens = []
    
    print(f"Sent {token_count} tokens to client. Storage cleared.")
    
    # Return all tokens that were in storage
    return jsonify({
        'status': 'success',
        'count': token_count,
        'tokens': current_tokens
    })

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(debug=True)