[Unit]
Description=Telegram Bot
After=network.target

[Service]
User=test_user
Group=test_user
WorkingDirectory=/home/test_user/PythonAdvancedJuly/
Environment="PYTHONPATH=/home/test_user/PythonAdvancedJuly/"
ExecStart=/home/test_user/PythonAdvancedJuly/.venv/bin/python /home/test_user/PythonAdvancedJuly/chat_roulette.py

[Install]
WantedBy=multi-user.target