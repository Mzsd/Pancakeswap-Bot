# Only style sheet data
# To save space in main gui.py file

message_box_styleSheet = \
""" QPushButton {
    background-color: rgb(100, 100, 100);
    color: rgb(250, 250, 250);
    border-style: outset;
    border: 2px solid;
    border-color: rgb(70, 70, 70);
    border-radius: 4px;
}

QPushButton:hover {
background-color: rgb(130, 130, 130);
}

QPushButton:pressed {
    background-color: rgb(85, 85, 85);
}

QPushButton:default {
    background-color: rgb(100, 100, 100);
}"""

start_bot_styleSheet = \
"""QPushButton {
    background-color: rgb(0, 170, 0);
	color: rgb(250, 250, 250);
	border-style: outset;
	border: 2px solid;
	border-color: rgb(70, 70, 70);
	border-radius: 4px;
}

QPushButton:hover {
    background-color: rgb(0, 185, 0);
}

QPushButton:pressed {
	background-color: rgb(0, 145, 0);
}

QPushButton:default {
    background-color: rgb(0, 170, 0);
}"""

stop_bot_styleSheet = \
"""QPushButton {
    background-color: rgb(170, 0, 0);
	color: rgb(250, 250, 250);
	border: 2px solid;
	border-color: rgb(70, 70, 70);
	border-radius: 4px;
}

QPushButton:hover {
    background-color: rgb(195, 0, 0);
}

QPushButton:pressed {
	background-color: rgb(145, 0, 0);
}

QPushButton:default {
    background-color: rgb(170, 0, 0);
}"""