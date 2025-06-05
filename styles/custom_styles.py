def get_custom_css():
    return """
        <style>
            body { background-color: #fbfbfb; }
            section.main { background-color: #fbfbfb; }
            .custom-header {
                background-color: #000000;
                padding: 12px 24px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-family: 'Segoe UI', sans-serif;
                border-bottom: 1px solid #e0e0e0;
                margin-bottom: 20px;
            }
            .custom-header .logo-section {
                display: flex;
                align-items: center;
            }
            .custom-header .logo-section img {
                height: 24px;
                margin-right: 12px;
            }
            .custom-header .logo-text {
                font-size: 22px;
                font-weight: 600;
                color: #FFFFFF;
            }
            div.stButton > button:first-child {
                background-color: #6a0dad;
                color: white;
                border-radius: 8px;
                padding: 0.5em 1.5em;
                border: none;
                font-weight: 600;
            }
            div.stButton > button:first-child:hover {
                background-color: #5a059e;
                color: white;
            }
            .uploader-title {
                font-weight: 700;
                font-size: 20px;
                margin-bottom: 10px;
            }
        </style>
    """
