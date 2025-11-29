from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "message": "Jumia Scraper API on Vercel",
            "status": "running",
            "note": "The Streamlit Dashboard cannot run on Vercel Serverless. Please deploy to Streamlit Cloud for the full experience.",
            "links": {
                "streamlit_cloud": "https://share.streamlit.io",
                "github_repo": "https://github.com/crab-xieyujin/playwright_jumia"
            }
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
