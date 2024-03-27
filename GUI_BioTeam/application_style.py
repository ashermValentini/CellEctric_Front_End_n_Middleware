
medium_temperature_number_style = "QLabel { color : #FF940A; font-family: Archivo; font-size: 30px;  }"
high_temperature_number_style = "QLabel { color : #FF0000; font-family: Archivo; font-size: 30px;  }"

title_style = "QLabel { color : #FFFFFF; font-family: Archivo; font-size: 40px; font-weight: bold; }"
subtitle_style = "QLabel { color : #FFFFFF; font-family: Archivo; font-size: 30px;  }"
input_style = "QLabel { color : #FFFFFF; font-family: Archivo; font-size: 23px;  }"
combobox_button_style = """
QComboBox, QPushButton {
    color: #FFFFFF;
    background-color: rgba(255, 255, 255, 0.1);
    font-family: Archivo;
    font-size: 20px;   /* adjust this as needed */
    border: 2px solid rgba(255, 255, 255, 0.7);
    border-radius: 5px;
    padding: 5px 15px;
}
QComboBox::drop-down, QPushButton {
    border: none;
}
QComboBox:hover, QPushButton:hover {
    background-color: rgba(7, 150, 255, 0.7);  
}
QComboBox QAbstractItemView {
color: #FFFFFF;
background-color: rgba(255, 255, 255, 0.1);
font-family: Archivo;
font-size: 20px;   /* adjust this as needed */
border: 2px solid rgba(255, 255, 255, 0.7);
border-radius: 5px;
selection-background-color: rgba(7, 150, 255, 0.5);  
}
"""   
line_edit_style = """
    QLineEdit {
        border: 2px solid white;
        border-radius: 5px;
        color: white;
        background-color: rgba(255, 255, 255, 0.1);
        font-size: 20px;
        padding: 7px;
    }
"""