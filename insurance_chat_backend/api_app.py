from app import insurance_chat_api_app

app = insurance_chat_api_app()

if __name__ == '__main__':
    app.run(debug=False)