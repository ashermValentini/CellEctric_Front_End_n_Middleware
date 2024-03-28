from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressBar, QDialog, QVBoxLayout, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch
from matplotlib.transforms import Bbox
from roundprogressBar import QRoundProgressBar
from roundprogressBar import MainWindow
import resources_rc
import application_style

#===============================
# EXPERIMENT PAGE CLASSES
#===============================

class CustomExperimentFrame(QtWidgets.QFrame):
    def __init__(self, title, icon_paths):
        super().__init__()
        
        self.setStyleSheet("background-color: #222222; border-radius: 15px;")
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Label
        self.label = QtWidgets.QLabel(title)
        self.label.setStyleSheet("QLabel { color : #FFFFFF; font-family: Archivo; font-size: 25px;  }")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Action items layout
        self.button_layout = QtWidgets.QHBoxLayout()
        
        # Start/stop button
        self.start_stop_button = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icon_paths["start_stop"]), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.start_stop_button.setIcon(icon)
        self.start_stop_button.setIconSize(QtCore.QSize(30, 30))
        self.start_stop_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)

        
        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid white;
                border-radius: 3px;
                background-color: #222222;
                text-align: center;
                height: 50px;  /* Adjust as necessary */
            }

            QProgressBar::chunk {
                background-color: rgba(7, 150, 255, 0.7);
            }
            QProgressBar {
                color: white;  /* Color of the text */
                font-size: 15px;  /* Size of the text */
            }
            """
        )
            
        self.progress_bar.setValue(0)
        
        # Reset button
        self.reset_button = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icon_paths["reset"]), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.reset_button.setIcon(icon)
        self.reset_button.setIconSize(QtCore.QSize(30, 30))
        self.reset_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)

        
        # Add items to button layout
        self.button_layout.addWidget(self.start_stop_button)
        self.button_layout.addWidget(self.progress_bar)
        self.button_layout.addWidget(self.reset_button)
        
        # Add widgets to main layout
        layout.addWidget(self.label)
        layout.addSpacing(10)
        layout.addLayout(self.button_layout)

        self.setLayout(layout)

#===============================
# LIVE DATA POP UPS
#===============================


class PopupWindow(QDialog):
    def __init__(self, title="Default Title", description="Default Description"):
        super().__init__()
        self.title = title
        self.description = description
        self.initUI()

    def initUI(self):
        
        main_vertical_layout = QVBoxLayout()
        #================================================================================================================================================================
        # TITLE AND DESCRIPTION
        #================================================================================================================================================================
        # region :
        self.label_LDA_title = QLabel(self.title)
        self.label_LDA_title.setStyleSheet(application_style.title_style)
        
        self.label_LDA_instructions = QLabel(self.description)
        self.label_LDA_instructions.setStyleSheet(application_style.input_style)
        self.label_LDA_instructions.setFixedWidth(800)  
        self.label_LDA_instructions.setWordWrap(True)
        # endregion
        #================================================================================================================================================================
        # USER INFORMATION
        #================================================================================================================================================================
        # region: 
        layout_LDA_user_information = QtWidgets.QHBoxLayout()

        layout_LDA_folder_name = QtWidgets.QVBoxLayout()
        self.label_LDA_folder_name = QLabel("Folder: ")
        self.label_LDA_folder_name.setStyleSheet(application_style.input_style)
        self.line_edit_LDA_folder_name = QtWidgets.QLineEdit()
        self.line_edit_LDA_folder_name.setStyleSheet(application_style.line_edit_style)
        self.line_edit_LDA_folder_name.setText("Data")
        layout_LDA_folder_name.addWidget(self.label_LDA_folder_name)
        layout_LDA_folder_name.addWidget(self.line_edit_LDA_folder_name)

        layout_LDA_user_name = QtWidgets.QVBoxLayout()
        self.label_LDA_user_name = QLabel("Name: ")
        self.label_LDA_user_name.setStyleSheet(application_style.input_style)
        self.combobox_LDA_user_name = QtWidgets.QComboBox()
        self.combobox_LDA_user_name.setStyleSheet(application_style.combobox_button_style)
        self.combobox_LDA_user_name.addItems(["","Dora", "Julia", "Asher Valentini"]) 
        layout_LDA_user_name.addWidget(self.label_LDA_user_name) 
        layout_LDA_user_name.addWidget(self.combobox_LDA_user_name)

        layout_LDA_user_email = QtWidgets.QVBoxLayout()
        self.label_LDA_user_email = QLabel("Email")
        self.label_LDA_user_email.setStyleSheet(application_style.input_style)
        self.combobox_LDA_user_email = QtWidgets.QComboBox()
        self.combobox_LDA_user_email.setStyleSheet(application_style.combobox_button_style)
        self.combobox_LDA_user_email.addItems(["","email@email", "hotdoghotdoghotdiggidydog"])     
        layout_LDA_user_email.addWidget(self.label_LDA_user_email)
        layout_LDA_user_email.addWidget(self.combobox_LDA_user_email)

        layout_LDA_user_information.addLayout(layout_LDA_folder_name)
        layout_LDA_user_information.addStretch(1)
        layout_LDA_user_information.addLayout(layout_LDA_user_name)
        layout_LDA_user_information.addStretch(1)
        layout_LDA_user_information.addLayout(layout_LDA_user_email)
        layout_LDA_user_information.addStretch(1)
        
        #endregion
        #================================================================================================================================================================
        # EXPERIMENT INFORMATION
        #================================================================================================================================================================
        # region : 
        layout_LDA_experiment_information = QtWidgets.QHBoxLayout()

        layout_LDA_experiment_purpose = QtWidgets.QVBoxLayout()
        self.label_LDA_experiment_purpose = QLabel("Purpose: ")
        self.label_LDA_experiment_purpose.setStyleSheet(application_style.input_style)
        self.line_edit_LDA_experiment_purpose = QtWidgets.QLineEdit()
        self.line_edit_LDA_experiment_purpose.setStyleSheet(application_style.line_edit_style)
        layout_LDA_experiment_purpose.addWidget(self.label_LDA_experiment_purpose) 
        layout_LDA_experiment_purpose.addWidget(self.line_edit_LDA_experiment_purpose)

        layout_LDA_experiment_number = QtWidgets.QVBoxLayout()
        self.label_LDA_experiment_number = QLabel("ID")
        self.label_LDA_experiment_number.setStyleSheet(application_style.input_style)
        self.line_edit_LDA_experiment_number = QtWidgets.QLineEdit()
        self.line_edit_LDA_experiment_number.setStyleSheet(application_style.line_edit_style)
        layout_LDA_experiment_number.addWidget(self.label_LDA_experiment_number) 
        layout_LDA_experiment_number.addWidget(self.line_edit_LDA_experiment_number)

        layout_LDA_strain = QtWidgets.QVBoxLayout()
        self.label_LDA_strain = QLabel("Strain Name: ")
        self.label_LDA_strain.setStyleSheet(application_style.input_style)
        self.combobox_LDA_strain = QtWidgets.QComboBox()
        self.combobox_LDA_strain.setStyleSheet(application_style.combobox_button_style)
        self.combobox_LDA_strain.addItems(["","Pathogen x", "Pathogen y", "Pathogen z", "N/A"]) 
        layout_LDA_strain.addWidget(self.label_LDA_strain) 
        layout_LDA_strain.addWidget(self.combobox_LDA_strain)

        layout_LDA_fresh_sucrose = QtWidgets.QVBoxLayout()
        self.label_LDA_fresh_sucrose = QLabel("Fresh Sucrose: ")
        self.label_LDA_fresh_sucrose.setStyleSheet(application_style.input_style)
        self.combobox_LDA_fresh_sucrose = QtWidgets.QComboBox()
        self.combobox_LDA_fresh_sucrose.setStyleSheet(application_style.combobox_button_style)
        self.combobox_LDA_fresh_sucrose.addItems(["","Yes", "No", "N/A"]) 
        layout_LDA_fresh_sucrose.addWidget(self.label_LDA_fresh_sucrose) 
        layout_LDA_fresh_sucrose.addWidget(self.combobox_LDA_fresh_sucrose)
        
        layout_LDA_experiment_information.addLayout(layout_LDA_experiment_purpose)
        layout_LDA_experiment_information.addStretch(1)

        layout_LDA_experiment_information.addLayout(layout_LDA_experiment_number)
        layout_LDA_experiment_information.addStretch(1)

        layout_LDA_experiment_information.addLayout(layout_LDA_strain)
        layout_LDA_experiment_information.addStretch(1)

        layout_LDA_experiment_information.addLayout(layout_LDA_fresh_sucrose)
        layout_LDA_experiment_information.addStretch(1)

        
        #endregion
        #================================================================================================================================================================
        # VARIABLE OPTIONS 
        #================================================================================================================================================================
        # region : 
        self.label_LDA_variable_information= QLabel("Data to Track: ")
        self.label_LDA_variable_information.setStyleSheet(application_style.input_style)
        layout_variable_options = QtWidgets.QHBoxLayout()

        #region : temperature and pressure buttons
        layout_variable_options_c1 = QtWidgets.QVBoxLayout()
        self.label_LDA_temperature= QLabel("Temperature: ")
        self.label_LDA_temperature.setStyleSheet(application_style.input_style)
        self.label_LDA_pressure= QLabel("Pressure: ")
        self.label_LDA_pressure.setStyleSheet(application_style.input_style)
        layout_variable_options_c1.addWidget(self.label_LDA_temperature)
        layout_variable_options_c1.addWidget(self.label_LDA_pressure)

        layout_variable_options_c2 = QtWidgets.QVBoxLayout()

        self.button_LDA_temperature = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_LDA_temperature.setIcon(icon)
        self.button_LDA_temperature.setIconSize(QtCore.QSize(20, 20)) 
        self.reset_button_style(self.button_LDA_temperature)

        self.button_LDA_pressure = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_LDA_pressure.setIcon(icon)
        self.button_LDA_pressure.setIconSize(QtCore.QSize(20, 20)) 
        self.reset_button_style(self.button_LDA_pressure)
        layout_variable_options_c2.addWidget(self.button_LDA_temperature)
        layout_variable_options_c2.addWidget(self.button_LDA_pressure)

        #endregion 

        #region : voltage and current buttons
        layout_variable_options_c3 = QtWidgets.QVBoxLayout()
        self.label_LDA_current= QLabel("Current: ")
        self.label_LDA_current.setStyleSheet(application_style.input_style)
        self.label_LDA_voltage= QLabel("Voltage: ")
        self.label_LDA_voltage.setStyleSheet(application_style.input_style)
        layout_variable_options_c3.addWidget(self.label_LDA_current)
        layout_variable_options_c3.addWidget(self.label_LDA_voltage)

        layout_variable_options_c4 = QtWidgets.QVBoxLayout()

        self.button_LDA_current = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_LDA_current.setIcon(icon)
        self.button_LDA_current.setIconSize(QtCore.QSize(20, 20)) 
        self.reset_button_style(self.button_LDA_current)

        self.button_LDA_voltage = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_LDA_voltage.setIcon(icon)
        self.button_LDA_voltage.setIconSize(QtCore.QSize(20, 20)) 
        self.reset_button_style(self.button_LDA_voltage)

        layout_variable_options_c4.addWidget(self.button_LDA_current)
        layout_variable_options_c4.addWidget(self.button_LDA_voltage)

        #endregion

        #region : ethanol and sucrose buttons
        layout_variable_options_c5 = QtWidgets.QVBoxLayout()
        self.label_LDA_Ethanol_FR= QLabel("Ethanol Flowrate: ")
        self.label_LDA_Ethanol_FR.setStyleSheet(application_style.input_style)
        self.label_LDA_Sucrose_FR= QLabel("Sucrose Flowrate: ")
        self.label_LDA_Sucrose_FR.setStyleSheet(application_style.input_style)
        layout_variable_options_c5.addWidget(self.label_LDA_Ethanol_FR)
        layout_variable_options_c5.addWidget(self.label_LDA_Sucrose_FR)

        layout_variable_options_c6 = QtWidgets.QVBoxLayout()

        self.button_LDA_Sucrose = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_LDA_Sucrose.setIcon(icon)
        self.button_LDA_Sucrose.setIconSize(QtCore.QSize(20, 20)) 
        self.reset_button_style(self.button_LDA_Sucrose)

        self.button_LDA_Ethanol = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_LDA_Ethanol.setIcon(icon)
        self.button_LDA_Ethanol.setIconSize(QtCore.QSize(20, 20)) 
        self.reset_button_style(self.button_LDA_Ethanol)
        layout_variable_options_c6.addWidget(self.button_LDA_Ethanol)
        layout_variable_options_c6.addWidget(self.button_LDA_Sucrose)
        #endregion

        layout_variable_options.addLayout(layout_variable_options_c1)
        layout_variable_options.addLayout(layout_variable_options_c2)
        layout_variable_options.addStretch(1)
        layout_variable_options.addLayout(layout_variable_options_c3)
        layout_variable_options.addLayout(layout_variable_options_c4)
        layout_variable_options.addStretch(1)
        layout_variable_options.addLayout(layout_variable_options_c5)
        layout_variable_options.addLayout(layout_variable_options_c6)
        layout_variable_options.addStretch(1)
        #endregion
        #================================================================================================================================================================
        # APPLY AND GO LIVE BUTTONS
        #================================================================================================================================================================
        # region : 
        layout_LDA_apply_live = QtWidgets.QHBoxLayout()

        self.button_LDA_apply = QtWidgets.QPushButton("Apply")  # Set the text to empty since we are using an image
        self.reset_button_style(self.button_LDA_apply)

        self.button_LDA_go_live = QtWidgets.QPushButton("Go Live")  # Set the text to empty since we are using an image
        self.button_LDA_go_live.setEnabled(False)
        self.set_button_style(self.button_LDA_go_live, 23, False)


        layout_LDA_apply_live.addWidget(self.button_LDA_apply)
        layout_LDA_apply_live.addStretch(1)
        layout_LDA_apply_live.addWidget(self.button_LDA_go_live)
        layout_LDA_apply_live.addSpacing(10)
        
        main_vertical_layout.addWidget(self.label_LDA_title)
        main_vertical_layout.addWidget(self.label_LDA_instructions)
        main_vertical_layout.addSpacing(20) 
        main_vertical_layout.addLayout(layout_LDA_user_information)
        main_vertical_layout.addSpacing(20) 
        main_vertical_layout.addLayout(layout_LDA_experiment_information)
        main_vertical_layout.addSpacing(20)
        main_vertical_layout.addWidget(self.label_LDA_variable_information)
        main_vertical_layout.addSpacing(20) 
        main_vertical_layout.addLayout(layout_variable_options)
        main_vertical_layout.addSpacing(40) 
        main_vertical_layout.addLayout(layout_LDA_apply_live)
        # endregion

        self.setLayout(main_vertical_layout)
        self.setStyleSheet("background-color: #222222;")


    def reset_button_style(self, button, font_size=23):
        button.setStyleSheet(f"""
            QPushButton {{
                border: 2px solid white;
                border-radius: 10px;
                background-color: #222222;
                color: #FFFFFF;
                font-family: Archivo;
                font-size: {font_size}px;
            }}

            QPushButton:hover {{
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }}

            QPushButton:pressed {{
                background-color: #0796FF;
            }}
        """)

    def set_button_style(self, button, font_size=23, enabled=True):
        if enabled:
            button.setStyleSheet(f"""
                QPushButton {{
                    border: 2px solid white;
                    border-radius: 10px;
                    background-color: #222222;
                    color: #FFFFFF;
                    font-family: Archivo;
                    font-size: {font_size}px;
                }}

                QPushButton:hover {{
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }}

                QPushButton:pressed {{
                    background-color: #0796FF;
                }}
            """)
        else:
            button.setStyleSheet(f"""
                QPushButton {{
                    border: 2px solid #444444;
                    border-radius: 10px;
                    background-color: #333333;
                    color: #AAAAAA;
                    font-family: Archivo;
                    font-size: {font_size}px;
                }}
            """)

class EndPopupWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        input_style = "QLabel { color : #FFFFFF; font-family: Archivo; font-size: 23px;  }"
        main_vertical_layout = QtWidgets.QVBoxLayout()
        self.label_end_LDA_title = QLabel("Click Confirm to end this live data aquisiton session: ")
        self.label_end_LDA_title.setStyleSheet(input_style)

        layout_confirm_button = QtWidgets.QHBoxLayout()
        self.button_end_LDA = QtWidgets.QPushButton("Confirm")  # Set the text to empty since we are using an image
        self.button_end_LDA.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 5px;
                background-color: #222222;
                color: #FFFFFF;
                font-family: Archivo;
                font-size: 23px;
                padding: 7px;

            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)
        layout_confirm_button.addWidget(self.button_end_LDA)
        layout_confirm_button.addStretch(1)
        
        main_vertical_layout.addWidget(self.label_end_LDA_title)
        main_vertical_layout.addSpacing(20)
        main_vertical_layout.addLayout(layout_confirm_button)


        self.setLayout(main_vertical_layout)
        self.setStyleSheet("background-color: #222222;")

#===============================
# MAIN WINDOW LAYOUT CLASS
#===============================

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):

        # Set up the main window 
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 1920)
        MainWindow.setStyleSheet("background-color: #121212;")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Create a stacked widget object so that we can create multiple pages with mutliple layouts 
        self.stack = QtWidgets.QStackedWidget(self.centralwidget)
        self.dashboard = QtWidgets.QWidget()  #index 0 
        self.experiment = QtWidgets.QWidget() #index 1
        
        # Add pages to the stack
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.experiment)

        # Layout for the central widget
        self.central_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.central_layout.addWidget(self.stack)
        
        # Give all buttons the same padding in this layout 
        QtWidgets.QApplication.instance().setStyleSheet("""
            QPushButton {
                padding: 10px;
                }
         """)
    
#region : Dashboard Page Layout     
        self.h_layout = QtWidgets.QHBoxLayout(self.dashboard)
        self.h_layout.setContentsMargins(0, 0, 0, 0)   
        
    # region : Sidebar

        # Create sidebar frame 
        self.frame_d_sidebar = QtWidgets.QFrame()
        self.frame_d_sidebar.setContentsMargins(0, 0, 0, 0)
        self.frame_d_sidebar.setFixedWidth(int(MainWindow.height() * 0.07))
        self.frame_d_sidebar.setStyleSheet("background-color: #222222;")
        self.frame_d_sidebar.setObjectName("frame_d_sidebar")

        # Create layout for sidebar 
        self.side_bar_layout = QtWidgets.QVBoxLayout(self.frame_d_sidebar)

        # Attach sidebars layout to the side bar frame 
        self.frame_d_sidebar.setLayout(self.side_bar_layout)

        # Create company logo
        self.sidebar_logo = QtWidgets.QLabel()
        self.sidebar_logo.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        buffer = 10  
        self.sidebar_logo.setGeometry(buffer, buffer, self.frame_d_sidebar.width() - 3 * buffer, int(MainWindow.height() * 0.2))
        logo_pixmap = QtGui.QPixmap( ":/images/logo_small_white.png")
        self.sidebar_logo.setPixmap(logo_pixmap.scaled(self.sidebar_logo.width(), self.sidebar_logo.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        # Create the button to turn on the lights
        self.button_lights  = QtWidgets.QPushButton() 
        buffer = 10  
        self.button_lights .setGeometry(buffer, buffer, self.frame_d_sidebar.width() - 3 * buffer, int(MainWindow.height() * 0.2))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/lightbulb.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_lights .setIcon(icon)
        self.button_lights .setIconSize(QtCore.QSize(40, 40))  # Adjust size as needed
        self.button_lights .setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)
        
        # Create the button to home the motors
        self.button_motors_home  = QtWidgets.QPushButton() 
        buffer = 10  
        self.button_motors_home.setGeometry(buffer, buffer, self.frame_d_sidebar.width() - 3 * buffer, int(MainWindow.height() * 0.2))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/all_directions.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_motors_home.setIcon(icon)
        self.button_motors_home.setIconSize(QtCore.QSize(40, 40))  # Adjust size as needed
        self.button_motors_home.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)
        
        # Create the button for routing to the experiment page 
        self.button_experiment_route  = QtWidgets.QPushButton() 
        buffer = 10  
        self.button_experiment_route.setGeometry(buffer, buffer, self.frame_d_sidebar.width() - 3 * buffer, int(MainWindow.height() * 0.2))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/flasks_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_experiment_route.setIcon(icon)
        self.button_experiment_route.setIconSize(QtCore.QSize(40, 40))  # Adjust size as needed
        self.button_experiment_route.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)

        # Create the button for dashboard data recording  
        self.button_dashboard_data_recording  = QtWidgets.QPushButton() 
        buffer = 10  
        self.button_dashboard_data_recording.setGeometry(buffer, buffer, self.frame_d_sidebar.width() - 3 * buffer, int(MainWindow.height() * 0.2))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/record_button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_dashboard_data_recording.setIcon(icon)
        self.button_dashboard_data_recording.setIconSize(QtCore.QSize(40, 40))  # Adjust size as needed
        self.button_dashboard_data_recording.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)
        
        # Add widgets to the layout  
        self.side_bar_layout.addWidget(self.sidebar_logo)
        self.side_bar_layout.addSpacing(15)
        self.side_bar_layout.addWidget(self.button_lights)
        self.side_bar_layout.addWidget(self.button_motors_home)
        self.side_bar_layout.addWidget(self.button_experiment_route)
        self.side_bar_layout.addWidget(self.button_dashboard_data_recording)
        self.side_bar_layout.addStretch(1)
        


        # Add the entire sidebar as the left most widget on the dashboard page 
        self.h_layout.addWidget(self.frame_d_sidebar)
    #endregion

    # region: Topbar

        self.v_layout = QtWidgets.QVBoxLayout()
        self.h_layout.addLayout(self.v_layout)
        self.h_layout.setSpacing(0)
        self.v_layout.setSpacing(0)
        self.v_layout.setContentsMargins(0, 0, 0, 0)

        # Create the topbar frame 
        self.frame_d_topbar = QtWidgets.QFrame()
        self.frame_d_topbar.setContentsMargins(0, 0, 0, 0)
        self.frame_d_topbar.setFixedHeight(int(MainWindow.height() * 0.07))
        self.frame_d_topbar.setStyleSheet("background-color: #222222;")
        self.frame_d_topbar.setObjectName("frame_d_topbar")
        
        # Create layout for the frame_d_topbar
        topbar_layout = QtWidgets.QHBoxLayout(self.frame_d_topbar)
  
        # Attach the topbar's layout to the topbar frame 
        self.frame_d_topbar.setLayout(topbar_layout)

        # Create label for topbar
        self.label = QtWidgets.QLabel(self.frame_d_topbar)
        self.label.setText("DASHBOARD")
        self.label.setStyleSheet(application_style.main_window_header_style)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        # Add the lable to the topbar's layout 
        topbar_layout.addWidget(self.label)

        # Add the top bar frame to the v_layout 
        self.v_layout.addWidget(self.frame_d_topbar)
    #endregion
    
    # region : Main content
        self.main_content = QtWidgets.QVBoxLayout()
        self.main_content.setContentsMargins(0, 0, 0, 0)
        self.v_layout.addLayout(self.main_content)

# region: Applications
        self.application_region = QtWidgets.QHBoxLayout()
        self.main_content.addLayout(self.application_region)

    # region : LEFT FRAMES 
        self.application_region_1_widget = QtWidgets.QWidget()
        self.application_region_1_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.application_region_1_layout = QtWidgets.QVBoxLayout(self.application_region_1_widget)

        # region : Sucrose
        self.frame_sucrose = QtWidgets.QFrame()  # create sucrose frame
        self.frame_sucrose.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.frame_sucrose.setObjectName("frame_d_sucroseFlowrate")

        layout_sucrose = QtWidgets.QVBoxLayout(self.frame_sucrose)  # create layout for sucrose frame
        self.frame_sucrose.setLayout(layout_sucrose)  # set layout to sucrose frame
        layout_sucrose.setAlignment(QtCore.Qt.AlignCenter)

        # region: label
        label_sucrose = QtWidgets.QLabel(self.frame_sucrose)
        label_sucrose.setStyleSheet(application_style.main_window_title_style)
        label_sucrose.setText("SUCROSE")
        label_sucrose.setAlignment(QtCore.Qt.AlignCenter)
        layout_sucrose.addWidget(label_sucrose)  # add label to layout
        layout_sucrose.addSpacing(20)     # Add a fixed amount of vertical space  # Adjust the number for more or less space
        # endregion

        # region: progress bar and button
        progress_button_layout = QtWidgets.QHBoxLayout()  # create layout for progress bar and button

        self.progress_bar_sucrose = QRoundProgressBar()  # create progress bar
        self.progress_bar_sucrose.setFixedSize(175, 175)
        self.progress_bar_sucrose.setRange(0, 60)
        self.progress_bar_sucrose.setValue(0)
        self.progress_bar_sucrose.setBarColor('#0796FF')
        self.progress_bar_sucrose.setDecimals(2)
        self.progress_bar_sucrose.setDonutThicknessRatio(0.85)
        
        progress_button_layout.addSpacing(20)  # add fixed space of 20 pixels
        progress_button_layout.addWidget(self.progress_bar_sucrose)  # add progress bar to the layout
        progress_button_layout.addSpacing(5)  # add fixed space of 20 pixels

        self.button_sucrose = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/play_pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_sucrose.setIcon(icon)
        self.button_sucrose.setIconSize(QtCore.QSize(50, 50))  # Adjust size as needed
        self.button_sucrose.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)

        progress_button_layout.addWidget(self.button_sucrose)  # add button to the layout

        layout_sucrose.addLayout(progress_button_layout)  # add layout for progress bar and button to main layout
        # endregion
       
        # region : Inputs
        group_boxes_layout = QtWidgets.QHBoxLayout()  # create layout for both group boxes
        # region: Groupbox 1
        group_box_sucrose = QtWidgets.QGroupBox(self.frame_sucrose)  # create groupbox
        group_box_sucrose.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
        group_box_sucrose.setAlignment(QtCore.Qt.AlignCenter)
        group_box_layout = QtWidgets.QHBoxLayout(group_box_sucrose)  # create layout for groupbox
        group_box_sucrose.setLayout(group_box_layout)  # set layout to groupbox

        unit_label = QtWidgets.QLabel("ml/min")
        unit_label.setStyleSheet(application_style.main_window_input_style)

        self.line_edit_sucrose = QtWidgets.QLineEdit()
        self.line_edit_sucrose.setStyleSheet("QLineEdit { color: white; background-color: #222222; font-size: 25px; }")
        self.line_edit_sucrose.setText("3.00")

        group_box_layout.addWidget(self.line_edit_sucrose)
        group_box_layout.addWidget(unit_label)
        # endregion
        # region: Groupbox 2
        group_box_sucrose_2 = QtWidgets.QGroupBox(self.frame_sucrose)  # create second groupbox
        group_box_sucrose_2.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
        group_box_sucrose_2.setAlignment(QtCore.Qt.AlignCenter)
        group_box_layout_2 = QtWidgets.QHBoxLayout(group_box_sucrose_2)  # create layout for second groupbox
        group_box_sucrose_2.setLayout(group_box_layout_2)  # set layout to second groupbox

        unit_label_2 = QtWidgets.QLabel("ml")  # unit for time variable
        unit_label_2.setStyleSheet(application_style.main_window_input_style)

        self.line_edit_sucrose_2 = QtWidgets.QLineEdit()
        self.line_edit_sucrose_2.setStyleSheet("QLineEdit { color: white; background-color: #222222; font-size: 25px; }")
        self.line_edit_sucrose_2.setText("5")

        group_box_layout_2.addWidget(self.line_edit_sucrose_2)
        group_box_layout_2.addWidget(unit_label_2)
        # endregion
        group_boxes_layout.addWidget(group_box_sucrose)
        group_boxes_layout.addWidget(group_box_sucrose_2)
        layout_sucrose.addLayout(group_boxes_layout)  # add layout for group boxes to main layout
        #endregion

        # endregion
        
        # region : Blood
        self.frame_blood = QtWidgets.QFrame()  # create blood frame
        self.frame_blood.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.frame_blood.setObjectName("frame_d_bloodFlowrate")

        layout_blood = QtWidgets.QVBoxLayout(self.frame_blood)  # create layout for ethanol frame
        self.frame_blood.setLayout(layout_blood)  # set layout to blood frame
        layout_blood.setAlignment(QtCore.Qt.AlignCenter)

        # region: label
        label_blood = QtWidgets.QLabel(self.frame_blood)
        label_blood.setStyleSheet(application_style.main_window_title_style)
        label_blood.setText("BLOOD")
        label_blood.setAlignment(QtCore.Qt.AlignCenter)
        layout_blood.addWidget(label_blood)  # add label to layout
        layout_blood.addSpacing(20)     # Add a fixed amount of vertical space  # Adjust the number for more or less space
        # endregion

        # region: movement buttons
        progress_button_layout = QtWidgets.QHBoxLayout()  # create layout for progress bar and button

        self.button_blood_top = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/top_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_blood_top.setIcon(icon)
        self.button_blood_top.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.button_blood_top.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)

        self.button_blood_up = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/up_slow_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_blood_up.setIcon(icon)
        self.button_blood_up.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_blood_up, 30, False)

        self.button_blood_down = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/down_slow_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_blood_down.setIcon(icon)
        self.button_blood_down.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_blood_down, 30, False)

        self.button_blood_play_pause = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/play_pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_blood_play_pause.setIcon(icon)
        self.button_blood_play_pause.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_blood_play_pause, 30, False)

        progress_button_layout.addWidget(self.button_blood_top)  # add button to the layout
        progress_button_layout.addWidget(self.button_blood_up)
        progress_button_layout.addWidget(self.button_blood_down)
        progress_button_layout.addWidget(self.button_blood_play_pause)  # add button to the layout
        layout_blood.addLayout(progress_button_layout)  # add layout for progress bar and button to main layout
        # endregion
       
        # region : Inputs
        group_boxes_layout = QtWidgets.QHBoxLayout()  # create layout for both group boxes
        # region: Groupbox 1
        group_box_blood = QtWidgets.QGroupBox(self.frame_blood)  # create groupbox
        group_box_blood.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
        group_box_blood.setAlignment(QtCore.Qt.AlignCenter)
        group_box_layout= QtWidgets.QHBoxLayout(group_box_blood)  # create layout for groupbox
        group_box_blood.setLayout(group_box_layout)  # set layout to groupbox

        unit_label = QtWidgets.QLabel("ml/min")
        unit_label.setStyleSheet(application_style.main_window_input_style)

        self.line_edit_blood = QtWidgets.QLineEdit()
        self.line_edit_blood.setStyleSheet("QLineEdit { color: white; background-color: #222222; font-size: 25px; }")
        self.line_edit_blood.setText("0.25")
        group_box_layout.addWidget(self.line_edit_blood)
        group_box_layout.addWidget(unit_label)
        # endregion
        # region: Groupbox 2
        group_box_blood_2 = QtWidgets.QGroupBox(self.frame_blood)  # create second groupbox
        group_box_blood_2.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
        group_box_blood_2.setAlignment(QtCore.Qt.AlignCenter)
        group_box_layout_2 = QtWidgets.QHBoxLayout(group_box_blood_2)  # create layout for second groupbox
        group_box_blood_2.setLayout(group_box_layout_2)  # set layout to second groupbox

        unit_label_2 = QtWidgets.QLabel("ml")  # unit for time variable
        unit_label_2.setStyleSheet(application_style.main_window_input_style)

        self.line_edit_blood_2 = QtWidgets.QLineEdit()
        self.line_edit_blood_2.setStyleSheet("QLineEdit { color: white; background-color: #222222; font-size: 25px;}")
        self.line_edit_blood_2.setText("1")

        group_box_layout_2.addWidget(self.line_edit_blood_2)
        group_box_layout_2.addWidget(unit_label_2)
        # endregion
        group_boxes_layout.addWidget(group_box_blood)
        group_boxes_layout.addWidget(group_box_blood_2)
        layout_blood.addLayout(group_boxes_layout)  # add layout for group boxes to main layout
        #endregion
        #endregion
        
        # region : Ethanol
        self.frame_ethanol = QtWidgets.QFrame()  # create ethanol frame
        self.frame_ethanol.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.frame_ethanol.setObjectName("frame_d_ethanolFlowrate")

        layout_ethanol = QtWidgets.QVBoxLayout(self.frame_ethanol)  # create layout for ethanol frame
        self.frame_ethanol.setLayout(layout_ethanol)  # set layout to ethanol frame
        layout_ethanol.setAlignment(QtCore.Qt.AlignCenter)

        # region: label
        label_ethanol = QtWidgets.QLabel(self.frame_ethanol)
        label_ethanol.setStyleSheet(application_style.main_window_title_style)
        label_ethanol.setText("ETHANOL")
        label_ethanol.setAlignment(QtCore.Qt.AlignCenter)
        layout_ethanol.addWidget(label_ethanol)  # add label to layout
        layout_ethanol.addSpacing(20)     # Add a fixed amount of vertical space  # Adjust the number for more or less space
        # endregion

        # region: progress bar and button
        progress_button_layout = QtWidgets.QHBoxLayout()  # create layout for progress bar and button

        self.progress_bar_ethanol = QRoundProgressBar()  # create progress bar
        self.progress_bar_ethanol.setFixedSize(175, 175)
        self.progress_bar_ethanol.setRange(0, 60)
        self.progress_bar_ethanol.setValue(0)
        self.progress_bar_ethanol.setDecimals(2)
        self.progress_bar_ethanol.setDonutThicknessRatio(0.85)
        self.progress_bar_ethanol.setBarColor('#0796FF')
        
        progress_button_layout.addSpacing(20)  # add fixed space of 20 pixels
        progress_button_layout.addWidget(self.progress_bar_ethanol)  # add progress bar to the layout
        progress_button_layout.addSpacing(5)  # add fixed space of 20 pixels

        self.button_ethanol = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/play_pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_ethanol.setIcon(icon)
        self.button_ethanol.setIconSize(QtCore.QSize(50, 50))  # Adjust size as needed
        self.button_ethanol.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)

        progress_button_layout.addWidget(self.button_ethanol)  # add button to the layout

        layout_ethanol.addLayout(progress_button_layout)  # add layout for progress bar and button to main layout
        # endregion
       
        # region : Inputs
        group_boxes_layout = QtWidgets.QHBoxLayout()  # create layout for both group boxes
        # region: Groupbox 1
        group_box_ethanol = QtWidgets.QGroupBox(self.frame_ethanol)  # create groupbox
        group_box_ethanol.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
        group_box_ethanol.setAlignment(QtCore.Qt.AlignCenter)
        group_box_layout = QtWidgets.QHBoxLayout(group_box_ethanol)  # create layout for groupbox
        group_box_ethanol.setLayout(group_box_layout)  # set layout to groupbox

        unit_label = QtWidgets.QLabel("ml/min")
        unit_label.setStyleSheet(application_style.main_window_input_style)

        self.line_edit_ethanol = QtWidgets.QLineEdit()
        self.line_edit_ethanol.setStyleSheet("QLineEdit { color: white; background-color: #222222; font-size: 25px; }")
        self.line_edit_ethanol.setText("3.00")
        group_box_layout.addWidget(self.line_edit_ethanol)
        group_box_layout.addWidget(unit_label)
        # endregion
        # region: Groupbox 2
        group_box_ethanol_2 = QtWidgets.QGroupBox(self.frame_ethanol)  # create second groupbox
        group_box_ethanol_2.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
        group_box_ethanol_2.setAlignment(QtCore.Qt.AlignCenter)
        group_box_layout_2 = QtWidgets.QHBoxLayout(group_box_ethanol_2)  # create layout for second groupbox
        group_box_ethanol_2.setLayout(group_box_layout_2)  # set layout to second groupbox

        unit_label_2 = QtWidgets.QLabel("ml")  # unit for time variable
        unit_label_2.setStyleSheet(application_style.main_window_input_style)

        self.line_edit_ethanol_2 = QtWidgets.QLineEdit()
        self.line_edit_ethanol_2.setStyleSheet("QLineEdit { color: white; background-color: #222222; font-size: 25px;}")
        self.line_edit_ethanol_2.setText("5")

        group_box_layout_2.addWidget(self.line_edit_ethanol_2)
        group_box_layout_2.addWidget(unit_label_2)
        # endregion
        group_boxes_layout.addWidget(group_box_ethanol)
        group_boxes_layout.addWidget(group_box_ethanol_2)
        layout_ethanol.addLayout(group_boxes_layout)  # add layout for group boxes to main layout
        #endregion
        #endregion
        
        #adding each of the frames to the application region 1 and then adding application region 1 to application region
        self.application_region_1_layout.addWidget(self.frame_sucrose)
        self.application_region_1_layout.addWidget(self.frame_ethanol)
        self.application_region_1_layout.addWidget(self.frame_blood)
        self.application_region.addWidget(self.application_region_1_widget)
    #endregion
    
    # region : MIDDLE FRAMES  
        self.application_region_2_widget = QtWidgets.QWidget()
        self.application_region_2_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.application_region_2_layout = QtWidgets.QVBoxLayout(self.application_region_2_widget)

        # region : Frame for connections
        frame = QtWidgets.QFrame()
        frame.setStyleSheet("background-color: #222222; border-radius: 15px;")
        frame.setObjectName("frame_d_coms_status")

        # Create a layout for the frame
        layout = QtWidgets.QVBoxLayout(frame)

        # Create the label and add it to the layout
        label = QtWidgets.QLabel()
        label.setStyleSheet(application_style.main_window_title_style)
        label.setText("CONNECTIONS")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)  # Add the label to the layout

        # Add a spacer for some vertical space
        layout.addSpacing(75)
    
        # List of module names
        module_names = ["Pulse Generator", "PSU", "Temperature Sensor", "3PAC"]

        # Dictionary to hold the circles
        self.circles = {}

        for module in module_names:
            # Create a layout for the module name and circle
            module_layout = QtWidgets.QHBoxLayout()
            
            # Create the module label and add it to the layout
            module_label = QtWidgets.QLabel()
            module_label.setStyleSheet(application_style.main_window_text_style) 
            module_label.setText(module)
            module_label.setAlignment(QtCore.Qt.AlignLeft)
            module_layout.addWidget(module_label)
            
            # Add stretch to push the next widget to the right
            module_layout.addStretch(1)
            
            # Create the circle (using a radio button) and add it to the layout
            circle = QtWidgets.QRadioButton()
            circle.setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #222222; } QRadioButton { background-color: #222222; }")
            circle.setEnabled(False)  # Initially set as disabled so it appears as white
            module_layout.addWidget(circle)

            # Add the circle to the dictionary
            self.circles[module] = circle

            # Add the module layout to the main layout
            layout.addLayout(module_layout)

        layout.addSpacing(30) 

        self.application_region_2_layout.addWidget(frame)
        #endregion 
        
        # region : Frame for plot buttons
        plot_button_frame = QtWidgets.QFrame()
        plot_button_frame.setStyleSheet("background-color: #222222; border-radius: 15px;")
        plot_button_frame.setObjectName("frame_d_voltageSignal")
                
        # Create a layout for the frame
        layout = QtWidgets.QVBoxLayout(plot_button_frame)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        plot_button_frame.setLayout(layout)
        # Label
        label = QtWidgets.QLabel()
        label.setStyleSheet(application_style.main_window_title_style)
        label.setText("PLOTS")
        label.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(label)  
        layout.addSpacing(30)   
        
        # button creation
        self.temp_button = QtWidgets.QPushButton("Electrode Temperature")  # Set the text to empty since we are using an image
        self.temp_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 10px;
                background-color: #222222;
                color: #FFFFFF;
                font-family: Archivo;
                font-size: 30px;

            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)

        self.voltage_button = QtWidgets.QPushButton("Voltage Signal")  # Set the text to empty since we are using an image
        self.voltage_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 10px;
                background-color: #222222;
                color: #FFFFFF;
                font-family: Archivo;
                font-size: 30px;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)
        
        self.current_button = QtWidgets.QPushButton("Current Signal")  # Set the text to empty since we are using an image
        self.current_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 10px;
                background-color: #222222;
                color: #FFFFFF;
                font-family: Archivo;
                font-size: 30px;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)
        
        layout.addWidget(self.temp_button) 
        layout.addWidget(self.voltage_button) 
        layout.addWidget(self.current_button) 
      
        layout.addSpacing(0) 
        self.application_region_2_layout.addWidget(plot_button_frame)
        
        #endregion
        
        # region : Frame for fluidic motors
        self.frame_cartridge = QtWidgets.QFrame()  # create cartridge frame
        self.frame_cartridge.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.frame_cartridge.setObjectName("frame_d_cartridgeMotors")

        layout_cartridge = QtWidgets.QVBoxLayout(self.frame_cartridge)  # create layout for ethanol frame
        self.frame_cartridge.setLayout(layout_cartridge)  # set layout to cartridge frame
        layout_cartridge.setAlignment(QtCore.Qt.AlignCenter)

        # region: label
        label_cartridge = QtWidgets.QLabel(self.frame_cartridge)
        label_cartridge.setStyleSheet(application_style.main_window_title_style)
        label_cartridge.setText("FLUIDICS")
        label_cartridge.setAlignment(QtCore.Qt.AlignCenter)
        layout_cartridge.addWidget(label_cartridge)  # add label to layout
        layout_cartridge.addSpacing(20)     # Add a fixed amount of vertical space  # Adjust the number for more or less space
        # endregion

        # region: movement buttons
        progress_button_layout = QtWidgets.QHBoxLayout()  # create layout for progress bar and button

        self.button_cartridge_bottom = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/top_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_cartridge_bottom.setIcon(icon)
        self.button_cartridge_bottom.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_cartridge_bottom, 30, True)

        self.button_cartridge_up  = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/up_slow_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_cartridge_up.setIcon(icon)
        self.button_cartridge_up.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_cartridge_up, 30, False)

        self.button_cartridge_down = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/down_slow_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_cartridge_down.setIcon(icon)
        self.button_cartridge_down.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_cartridge_down, 30, False)

        progress_button_layout.addWidget(self.button_cartridge_bottom)  # add button to the layout
        progress_button_layout.addWidget(self.button_cartridge_up)
        progress_button_layout.addWidget(self.button_cartridge_down)
        layout_cartridge.addLayout(progress_button_layout)  # add layout for progress bar and button to main layout
        
        self.application_region_2_layout.addWidget(self.frame_cartridge)
        # endregion

        #endregion
        
        self.application_region.addWidget(self.application_region_2_widget)
    #endregion
    
    # region : RIGHT FRAMES 
        self.application_region_3_widget = QtWidgets.QWidget()
        self.application_region_3_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.application_region_3_layout = QtWidgets.QVBoxLayout(self.application_region_3_widget)

        # region: Frame for temperature
        temp_frame = QtWidgets.QFrame()
        temp_frame.setStyleSheet("background-color: #222222; border-radius: 15px; height: 20%;")
        temp_frame.setObjectName("frame_d_temperature")
        self.application_region_3_layout.addWidget(temp_frame)

        # Layout for temperature components
        temp_layout = QtWidgets.QVBoxLayout(temp_frame)

        # Title for temperature frame
        title_label = QtWidgets.QLabel("TEMPERATURE")
        title_label.setStyleSheet(application_style.main_window_title_style)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        temp_layout.addWidget(title_label)
        temp_layout.addSpacing(25)     # Add a fixed amount of vertical space  # Adjust the number for more or less space


        # Layout for image and stats
        temp_details_layout = QtWidgets.QHBoxLayout()
        temp_layout.addLayout(temp_details_layout)

        # Add labels for the temperature stats frame
        temp_stats_labels_layout = QtWidgets.QVBoxLayout()
        temp_details_layout.addLayout(temp_stats_labels_layout)

        self.max_temp_label = QtWidgets.QLabel("Max")
        self.max_temp_label.setStyleSheet(application_style.main_window_temperature_number_style)
        temp_stats_labels_layout.addWidget(self.max_temp_label, alignment=QtCore.Qt.AlignTop )

        self.min_temp_label = QtWidgets.QLabel("Current")
        self.min_temp_label.setStyleSheet(application_style.main_window_temperature_number_style)
        temp_stats_labels_layout.addWidget(self.min_temp_label, alignment=QtCore.Qt.AlignBottom)


        # Add temperature statistics next to labels
        temp_stats_layout = QtWidgets.QVBoxLayout()
        temp_details_layout.addLayout(temp_stats_layout)

        
        self.max_temp_data = QtWidgets.QLabel("-")
        self.max_temp_data.setStyleSheet(application_style.main_window_temperature_number_style)
        temp_stats_layout.addWidget(self.max_temp_data, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        self.current_temp_data = QtWidgets.QLabel("-")
        self.current_temp_data.setStyleSheet(application_style.main_window_temperature_number_style)
        temp_stats_layout.addWidget(self.current_temp_data, alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)

        #endregion
        
        # region: Frame for resevoir pressure reading/reseting 
        pressure_frame = QtWidgets.QFrame()
        pressure_frame.setStyleSheet("background-color: #222222; border-radius: 15px; height: 20%;")
        pressure_frame.setObjectName("frame_d_pressure")
        self.application_region_3_layout.addWidget(pressure_frame)

        # Layout for pressure frame components
        pressure_layout = QtWidgets.QVBoxLayout(pressure_frame)

        # Title for pressure frame
        title_label = QtWidgets.QLabel("PRESSURE")
        title_label.setStyleSheet(application_style.main_window_title_style)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        pressure_layout.addWidget(title_label)
        pressure_layout.addSpacing(15)     # Add a fixed amount of vertical space  # Adjust the number for more or less space

        #region : pressure check button and data
        pressure_details_layout = QtWidgets.QHBoxLayout()
        pressure_layout.addLayout(pressure_details_layout)

        # Add pressure check button
        self.pressure_check_button = QtWidgets.QPushButton("OPEN")  # create button
        #icon = QtGui.QIcon()
        #icon.addPixmap(QtGui.QPixmap(":/images/undo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        #self.pressure_check_button.setIcon(icon)
        #self.pressure_check_button.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        
        self.pressure_check_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 10px;
                background-color: #222222;
                color: #FFFFFF;
                font-family: Archivo;
                font-size: 25px;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)

        pressure_details_layout.addWidget(self.pressure_check_button, alignment=QtCore.Qt.AlignTop )

        #pressure_details_layout.addSpacing(110)     # Add a fixed amount of vertical space  # Adjust the number for more or less space

        pressure_details_layout.addStretch(1) 
        self.pressure_data = QtWidgets.QLabel("-    Bar")
        self.pressure_data.setStyleSheet(application_style.main_window_temperature_number_style)
        pressure_details_layout.addWidget(self.pressure_data, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        #endregion

        #region : pressure reset and progress bar

        # Layout for pressure reset button and progress bar
        pressure_reset_layout = QtWidgets.QHBoxLayout()
        pressure_layout.addLayout(pressure_reset_layout)
        
        # Add button to reset the pressure
        self.pressure_reset_button = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/increase.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pressure_reset_button.setIcon(icon)
        self.pressure_reset_button.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.pressure_reset_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)

        pressure_reset_layout.addWidget(self.pressure_reset_button, alignment=QtCore.Qt.AlignTop)


        # Add pressure reset progress bar
        self.pressure_progress_bar = QProgressBar()
        self.pressure_progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid white;
                border-radius: 3px;
                background-color: #222222;
                text-align: center;
                height: 40px;  /* Adjust as necessary */
            }

            QProgressBar::chunk {
                background-color: rgba(7, 150, 255, 0.7);
            }
            QProgressBar {
                color: white;  /* Color of the text */
                font-size: 15px;  /* Size of the text */
            }
            """
        )

        self.pressure_progress_bar.setValue(0)

        pressure_reset_layout.addWidget(self.pressure_progress_bar, alignment=QtCore.Qt.AlignTop)
        #endregion

        # endregion
        
        # region: Frame for voltage signal 
        frame_d_signal = QtWidgets.QFrame()
        frame_d_signal.setStyleSheet("background-color: #222222; border-radius: 15px;")
        frame_d_signal.setObjectName("frame_d_psuButton")
        self.application_region_3_layout.addWidget(frame_d_signal)

        # Create a layout for this frame
        frame_d_signal_layout = QtWidgets.QVBoxLayout(frame_d_signal)# Create a vertical layout for this frame

        # Create a label for this frame
        label = QtWidgets.QLabel("SIGNAL", frame_d_signal)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet(application_style.main_window_title_style)  # Set the color of the text as needed
        
        frame_d_signal_layout.addWidget(label)   #Place SIGNAL at the top of the frame
        frame_d_signal_layout.addSpacing(20)     # Add a fixed amount of vertical space  # Adjust the number for more or less space
            
        # Create a horizontal layout for group boxes and button
        inner_layout = QtWidgets.QHBoxLayout()     
        
        # Create a vertical layout for JUST the group boxes 
        group_boxes_layout = QtWidgets.QVBoxLayout()

        # region : Create a QGroupBox for the line edit and label for max voltage
        group_box_max_voltage = QtWidgets.QGroupBox(frame_d_signal)
        group_box_max_voltage.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
        group_box_max_voltage.setAlignment(QtCore.Qt.AlignCenter)

        # Create a QHBoxLayout for the first group box
        group_box_max_voltage_layout = QtWidgets.QHBoxLayout(group_box_max_voltage)

        # Create the QLabel for the unit
        unit_label = QtWidgets.QLabel("V")
        unit_label.setStyleSheet(application_style.main_window_voltage_style)

        # Create the QLabel for the higher pk-pk voltage
        MAX_label = QtWidgets.QLabel("Vp+ :")
        MAX_label.setStyleSheet(application_style.main_window_voltage_style)

        # Create the QLineEdit for the value
        self.line_edit_max_signal = QtWidgets.QLineEdit()
        self.line_edit_max_signal.setStyleSheet("QLineEdit { color: white; background-color: #222222; font-size: 20px; }")
        self.line_edit_max_signal.setText(" 75")

        # Add the line edit and label to the group box layout
        group_box_max_voltage_layout.addWidget(MAX_label)
        group_box_max_voltage_layout.addWidget(self.line_edit_max_signal)
        group_box_max_voltage_layout.addWidget(unit_label)

        group_box_max_voltage.setLayout(group_box_max_voltage_layout)
        #endregion
        
        # region : Create a QGroupBox for the line edit and label for min voltage
        group_box_min_voltage = QtWidgets.QGroupBox(frame_d_signal)
        group_box_min_voltage.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
        group_box_min_voltage.setAlignment(QtCore.Qt.AlignCenter)

        # Create a QHBoxLayout for the first group box
        group_box_min_voltage_layout = QtWidgets.QHBoxLayout(group_box_min_voltage)

        # Create the QLabel for the unit
        min_unit_label = QtWidgets.QLabel("V")
        min_unit_label.setStyleSheet(application_style.main_window_voltage_style)

        # Create the QLabel for the higher pk-pk voltage
        MIN_label = QtWidgets.QLabel("Vp- : ")
        MIN_label.setStyleSheet(application_style.main_window_voltage_style)

        # Create the QLineEdit for the value
        self.line_edit_min_signal = QtWidgets.QLineEdit()
        self.line_edit_min_signal.setStyleSheet("QLineEdit { color: white; background-color: #222222; font-size: 20px; }")
        self.line_edit_min_signal.setText("-75")

        # Add the line edit and label to the group box layout
        group_box_min_voltage_layout.addWidget(MIN_label)
        group_box_min_voltage_layout.addWidget(self.line_edit_min_signal)
        group_box_min_voltage_layout.addWidget(min_unit_label)

        group_box_min_voltage.setLayout(group_box_min_voltage_layout)
        #endregion

        group_boxes_layout.addWidget(group_box_max_voltage)# Add the group boxes to the vertical layout
        group_boxes_layout.addWidget(group_box_min_voltage)
        
        inner_layout.addLayout(group_boxes_layout)  # Add the vertical layout to the inner layout

        # PSU button creation
        self.psu_button = QtWidgets.QPushButton("", frame_d_signal)  # Set the text to empty since we are using an image
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/lightning_symbol.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.psu_button.setIcon(icon)
        self.psu_button.setIconSize(QtCore.QSize(64, 120))  # Adjust size as needed
        self.psu_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)
        inner_layout.addWidget(self.psu_button)# Add the button to the inner layout
        
        frame_d_signal_layout.addLayout(inner_layout)# Add the inner layout to the frame's layout
        # endregion

        # region : Frame for flask motors
        self.frame_flask = QtWidgets.QFrame()  # create flask frame
        self.frame_flask.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.frame_flask.setObjectName("frame_d_flaskMotors")

        layout_flask = QtWidgets.QVBoxLayout(self.frame_flask)  # create layout for ethanol frame
        self.frame_flask.setLayout(layout_flask)  # set layout to flask frame
        layout_flask.setAlignment(QtCore.Qt.AlignCenter)

        # region: label
        label_flask = QtWidgets.QLabel(self.frame_flask)
        label_flask.setStyleSheet(application_style.main_window_title_style)
        label_flask.setText("FLASKS")
        label_flask.setAlignment(QtCore.Qt.AlignCenter)
        layout_flask.addWidget(label_flask)  # add label to layout
        layout_flask.addSpacing(20)     # Add a fixed amount of vertical space  # Adjust the number for more or less space
        # endregion

        # region: flask up down buttons
        flask_up_down_button_layout = QtWidgets.QHBoxLayout()  # create layout for progress bar and button

        self.button_flask_bottom = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/bottom_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_flask_bottom.setIcon(icon)
        self.button_flask_bottom.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.button_flask_bottom.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)

        self.button_flask_up  = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/up_slow_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_flask_up.setIcon(icon)
        self.button_flask_up.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_flask_up, 30, False)

        self.button_flask_down = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/down_slow_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_flask_down.setIcon(icon)
        self.button_flask_down.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_flask_down, 30, False)

        flask_up_down_button_layout.addWidget(self.button_flask_bottom)  # add button to the layout
        flask_up_down_button_layout.addWidget(self.button_flask_up)
        flask_up_down_button_layout.addWidget(self.button_flask_down)

        layout_flask.addLayout(flask_up_down_button_layout)  # add layout for progress bar and button to main layout 
        # endregion
        
        # region: flask left right
        flask_left_right_button_layout = QtWidgets.QHBoxLayout()  # create layout for progress bar and button

        self.button_flask_rightmost = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/rightmost_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_flask_rightmost.setIcon(icon)
        self.button_flask_rightmost.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.button_flask_rightmost.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)

        self.button_flask_left  = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/left_slow_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_flask_left.setIcon(icon)
        self.button_flask_left.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_flask_left, 30, False)

        self.button_flask_right = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/right_slow_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_flask_right.setIcon(icon)
        self.button_flask_right.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_flask_right, 30, False)

        flask_left_right_button_layout.addWidget(self.button_flask_rightmost)  # add button to the layout
        flask_left_right_button_layout.addWidget(self.button_flask_left)
        flask_left_right_button_layout.addWidget(self.button_flask_right)

        layout_flask.addLayout(flask_left_right_button_layout)  # add layout for progress bar and button to main layout
        # endregion
        
        self.application_region_3_layout.addWidget(self.frame_flask)
        
        #endregion
        
        self.application_region.addWidget(self.application_region_3_widget)
    #endregion

# endregion: Applications   
  
# region : Plots
    
        # Plot region of the main content region
        self.plot_layout = QtWidgets.QVBoxLayout()
        self.plot_layout.setContentsMargins(10, 0, 10, 0)
        self.main_content.addLayout(self.plot_layout)
        
        # Create the Matplotlib canvas for the voltage plots
        self.canvas_voltage = FigureCanvas(Figure(figsize=(5, 4), dpi=100, facecolor='#222222'))
        self.canvas_voltage.setObjectName("canvas_voltage_plot")
        self.plot_layout.addWidget(self.canvas_voltage)
        
        fig = self.canvas_voltage.figure
        fig.subplots_adjust(bottom=0.15, top=0.85)


        # Get the Axes object from the Figure for voltage plot
        self.axes_voltage = self.canvas_voltage.figure.add_subplot(111)
        self.axes_voltage.grid(True, color='black', linestyle='--')
        self.axes_voltage.set_facecolor('#222222')
        self.axes_voltage.spines['bottom'].set_color('#FFFFFF')
        self.axes_voltage.spines['top'].set_color('#FFFFFF')
        self.axes_voltage.spines['right'].set_color('#FFFFFF')
        self.axes_voltage.spines['left'].set_color('#FFFFFF')
        self.axes_voltage.tick_params(colors='#FFFFFF')

        # Increase the font size of the x-axis and y-axis labels
        self.axes_voltage.tick_params(axis='x', labelsize=14)  # You can adjust the font size (e.g., 12)
        self.axes_voltage.tick_params(axis='y', labelsize=14)  # You can adjust the font size (e.g., 12)
        # Move the y-axis ticks and labels to the right
        self.axes_voltage.yaxis.tick_right()
        # Adjust the position of the x-axis label
        self.axes_voltage.xaxis.set_label_coords(0.5, -0.1)  # Move the x-axis label downwards

        # Adjust the position of the y-axis label to the left
        self.axes_voltage.yaxis.set_label_coords(-0.05, 0.5)  # Move the y-axis label to the left

        # Set static labels
        self.axes_voltage.set_xlabel('Time (ms)', color='#FFFFFF', fontsize=15)
        self.axes_voltage.set_ylabel('Temperature (°C)', color='#FFFFFF',  fontsize=15)
        self.axes_voltage.set_title('Electrode Temperature', color='#FFFFFF', fontsize=20, fontweight='bold', y=1.05)
        

    #endregion
    
    # endregion : Main content 
        MainWindow.setCentralWidget(self.centralwidget)
        self.main_content.setStretchFactor(self.application_region, 50)
        self.main_content.setStretchFactor(self.plot_layout, 50)    
#endregion

#region : Experiment Page Layout    
 
        self.experiment_page_h_layout = QtWidgets.QHBoxLayout(self.experiment)
        self.experiment_page_h_layout.setContentsMargins(0, 0, 0, 0)    
    
    # region : Sidebar

        self.frame_e_sidebar = QtWidgets.QFrame()
        self.frame_e_sidebar.setContentsMargins(0, 0, 0, 0)
        self.frame_e_sidebar.setFixedWidth(int(MainWindow.height() * 0.07))
        self.frame_e_sidebar.setStyleSheet("background-color: #222222;")
        self.frame_e_sidebar.setObjectName("frame_d_sidebar")
        
        # Create layout for sidebar 
        self.experiment_page_side_bar_layout = QtWidgets.QVBoxLayout(self.frame_e_sidebar)
        
        # Attach sidebars layout to the side bar frame 
        self.frame_e_sidebar.setLayout(self.experiment_page_side_bar_layout)

        # Create company logo
        self.experiment_page_sidebar_logo = QtWidgets.QLabel()
        self.experiment_page_sidebar_logo.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        buffer = 10  
        self.experiment_page_sidebar_logo.setGeometry(buffer, buffer, self.frame_e_sidebar.width() - 3 * buffer, int(MainWindow.height() * 0.2))
        experiment_page_logo_pixmap = QtGui.QPixmap( ":/images/logo_small_white.png")
        self.experiment_page_sidebar_logo.setPixmap(experiment_page_logo_pixmap.scaled(self.experiment_page_sidebar_logo.width(), self.experiment_page_sidebar_logo.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        
        # Create the button to turn on the lights
        self.experiment_page_button_lights  = QtWidgets.QPushButton() 
        buffer = 10  
        self.experiment_page_button_lights  .setGeometry(buffer, buffer, self.frame_e_sidebar.width() - 3 * buffer, int(MainWindow.height() * 0.2))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/lightbulb.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.experiment_page_button_lights  .setIcon(icon)
        self.experiment_page_button_lights  .setIconSize(QtCore.QSize(40, 40))  # Adjust size as needed
        self.experiment_page_button_lights  .setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)

        # Create the button for routing to the experiment page 
        self.button_dashboard_route  = QtWidgets.QPushButton() 
        buffer = 10  
        self.button_dashboard_route.setGeometry(buffer, buffer, self.frame_e_sidebar.width() - 3 * buffer, int(MainWindow.height() * 0.2))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/icon_dashboard_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_dashboard_route.setIcon(icon)
        self.button_dashboard_route.setIconSize(QtCore.QSize(40, 40))  # Adjust size as needed
        self.button_dashboard_route.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)
        
        # Add widgets to the layout  
        self.experiment_page_side_bar_layout.addWidget(self.experiment_page_sidebar_logo)
        self.experiment_page_side_bar_layout.addSpacing(15)
        self.experiment_page_side_bar_layout.addWidget(self.experiment_page_button_lights)
        self.experiment_page_side_bar_layout.addWidget(self.button_dashboard_route)
        self.experiment_page_side_bar_layout.addStretch(1)

        # Add the entire sidebar as the left most widget on the experimentn page 
        self.experiment_page_h_layout.addWidget(self.frame_e_sidebar)

    #endregion
        
        self.experiment_page_v_layout = QtWidgets.QVBoxLayout()
        self.experiment_page_h_layout.addLayout(self.experiment_page_v_layout)
        self.experiment_page_h_layout.setSpacing(0)
        self.experiment_page_v_layout.setSpacing(0)
        self.experiment_page_v_layout.setContentsMargins(0, 0, 0, 0)

    # region: Topbar
    
        self.frame_e_topbar = QtWidgets.QFrame()
        self.frame_e_topbar.setContentsMargins(0, 0, 0, 0)
        self.frame_e_topbar.setFixedHeight(int(MainWindow.height() * 0.07))
        self.frame_e_topbar.setStyleSheet("background-color: #222222;")
        self.frame_e_topbar.setObjectName("frame_d_topbar")
        
        # Create layout for the frame_d_topbar
        experiment_page_topbar_layout = QtWidgets.QHBoxLayout(self.frame_e_topbar)

        # Attach the topbar's layout to the topbar frame 
        self.frame_e_topbar.setLayout(experiment_page_topbar_layout)

        # Add "experiment" label to top bar
        self.experiment_page_label = QtWidgets.QLabel(self.frame_e_topbar)
        self.experiment_page_label.setText("EXPERIMENT")
        self.experiment_page_label.setStyleSheet(application_style.main_window_header_style)
        self.experiment_page_label.setAlignment(QtCore.Qt.AlignCenter)

        # Add the lable to the topbar's layout 
        experiment_page_topbar_layout.addWidget(self.experiment_page_label)

        # Add the top bar frame to the v_layout 
        self.experiment_page_v_layout.addWidget(self.frame_e_topbar)


    #endregion
    
    # region : Main content
        self.experiment_page_main_content = QtWidgets.QVBoxLayout()
        self.experiment_page_main_content.setContentsMargins(20, 20, 0, 0)
        self.experiment_page_main_content.setAlignment(QtCore.Qt.AlignTop)

        self.experiment_page_v_layout.addLayout(self.experiment_page_main_content)

    # region : data saving 
        self.frame_user_info= QtWidgets.QFrame()
        self.frame_user_info.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.frame_user_info.setObjectName("frame_e_user_info")

        layout_user_info = QtWidgets.QHBoxLayout(self.frame_user_info)
        self.frame_user_info.setLayout(layout_user_info)

        # region: add label for which application
        label_application = QtWidgets.QLabel(self.frame_user_info)
        label_application.setStyleSheet(application_style.main_window_input_style)
        label_application.setText("Application: ")
        #endregion

        # region: add combobox to select which application to use
        self.application_combobox = QtWidgets.QComboBox()
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
        
        self.application_combobox.setStyleSheet(combobox_button_style)
        self.application_combobox.addItems(["POCII", "Ethanol to Sucrose Flush", "CG2 QC", "Autotune", "Demonstration"])  # Add more emails as needed
        #endregion

        # region: add choice lockin button 
        self.user_info_lockin_button = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.user_info_lockin_button.setIcon(icon)
        self.user_info_lockin_button.setIconSize(QtCore.QSize(20, 20))  # Adjust size as needed
        self.user_info_lockin_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)
        #endregion

        layout_user_info.addWidget(label_application)
        layout_user_info.addWidget(self.application_combobox)
        layout_user_info.addWidget(self.user_info_lockin_button)
        layout_user_info.addStretch(1)

    # endregion
    # region : line separator 
        self.line = QtWidgets.QFrame()
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setStyleSheet("background-color: white;")
    #endregion
    # region : experiment steps (not shown only created)
        
        # region : create the POCII frames
        self.frame_POCII_system_sterilaty = CustomExperimentFrame("System Sterilaty Control", {
            "start_stop": ":/images/play_pause.png",
            "reset": ":/images/undo.png"
        })

        self.frame_POCII_decontaminate_cartridge = CustomExperimentFrame("Cartridge Decontamination", {
            "start_stop": ":/images/play_pause.png",
            "reset": ":/images/undo.png"
        })

        self.high_voltage_frame = CustomExperimentFrame("High Voltage", {
            "start_stop": ":/images/play_pause.png",
            "reset": ":/images/undo.png"
        })

        self.flush_out_frame = CustomExperimentFrame("Flush Out", {
            "start_stop": ":/images/play_pause.png",
            "reset": ":/images/undo.png"
        })

        self.zero_volt_frame = CustomExperimentFrame("Zero Voltage", {
            "start_stop": ":/images/play_pause.png",
            "reset": ":/images/undo.png"
        })

        self.safe_disconnect_frame = CustomExperimentFrame("Flush Out", {
            "start_stop": ":/images/play_pause.png",
            "reset": ":/images/undo.png"
        })

        self.save_experiment_data_frame = CustomExperimentFrame("Save Your Data", {
            "start_stop": ":/images/send.png",
            "reset": ":/images/trash.png"
        })
        #endregion 
        
        # region : create the Demo frames

        self.frame_DEMO_close_fluidic_circuit = CustomExperimentFrame("Close Fluidic Circuit", {
            "start_stop": ":/images/play_pause.png",
            "reset": ":/images/undo.png"
        })



        self.frame_DEMO_connect_waste_flask = CustomExperimentFrame("Waste Flask Connection", {
            "start_stop": ":/images/play_pause.png",
            "reset": ":/images/undo.png"
        })


        self.frame_DEMO_ethanol_flush = CustomExperimentFrame("Ethanol Flush", {
            "start_stop": ":/images/play_pause.png",
            "reset": ":/images/undo.png"
        })



        self.frame_DEMO_connect_to_harvest_flask = CustomExperimentFrame("Harvest Flask Connection", {
            "start_stop": ":/images/play_pause.png",
            "reset": ":/images/undo.png"
        })



        self.frame_DEMO_blood_sucrose_mix = CustomExperimentFrame("Blood and Sucrose Delivery", {
            "start_stop": ":/images/play_pause.png",
            "reset": ":/images/undo.png"
        })



        self.frame_DEMO_sample_retrieval = CustomExperimentFrame("Retrieve Sample", {
            "start_stop": ":/images/play_pause.png",
            "reset": ":/images/undo.png"
        })



        self.save_experiment_data_frame = CustomExperimentFrame("Save Your Data", {
            "start_stop": ":/images/send.png",
            "reset": ":/images/trash.png"
        })


        #endregion 

    #endregion

        #Add the user info frame to the maincontent layout
        self.experiment_page_main_content.addWidget(self.frame_user_info, alignment=QtCore.Qt.AlignTop)
        self.experiment_page_main_content.addSpacing(20)
        self.experiment_page_main_content.addWidget(self.line)
        self.experiment_page_main_content.addSpacing(20)

        #Add the POCII frames to the main content layout
        self.experiment_page_main_content.addWidget(self.frame_POCII_system_sterilaty)
        self.spacing_placeholder1 = QtWidgets.QWidget()
        self.spacing_placeholder1.setFixedHeight(5)
        self.experiment_page_main_content.addWidget(self.spacing_placeholder1)
        self.experiment_page_main_content.addWidget(self.frame_POCII_decontaminate_cartridge)
        self.spacing_placeholder2 = QtWidgets.QWidget()
        self.spacing_placeholder2.setFixedHeight(5)
        self.experiment_page_main_content.addWidget(self.spacing_placeholder2)
        self.experiment_page_main_content.addWidget(self.high_voltage_frame)
        self.spacing_placeholder3 = QtWidgets.QWidget()
        self.spacing_placeholder3.setFixedHeight(5)
        self.experiment_page_main_content.addWidget(self.spacing_placeholder3)
        self.experiment_page_main_content.addWidget(self.flush_out_frame)
        self.spacing_placeholder4 = QtWidgets.QWidget()
        self.spacing_placeholder4.setFixedHeight(5)
        self.experiment_page_main_content.addWidget(self.spacing_placeholder4)
        self.experiment_page_main_content.addWidget(self.zero_volt_frame)
        self.spacing_placeholder5 = QtWidgets.QWidget()
        self.spacing_placeholder5.setFixedHeight(5)
        self.experiment_page_main_content.addWidget(self.spacing_placeholder5)
        self.experiment_page_main_content.addWidget(self.safe_disconnect_frame)
        self.spacing_placeholder6 = QtWidgets.QWidget()
        self.spacing_placeholder6.setFixedHeight(5)
        self.experiment_page_main_content.addWidget(self.spacing_placeholder6)
        self.experiment_page_main_content.addWidget(self.save_experiment_data_frame)

        # Start the page as blank by hiding any widgets
        self.frame_POCII_system_sterilaty.hide()
        self.frame_POCII_decontaminate_cartridge.hide()
        self.high_voltage_frame.hide()
        self.flush_out_frame.hide()
        self.zero_volt_frame.hide()
        self.safe_disconnect_frame.hide()
        self.save_experiment_data_frame.hide()

        self.spacing_placeholder1.hide()
        self.spacing_placeholder2.hide()
        self.spacing_placeholder3.hide()
        self.spacing_placeholder4.hide()
        self.spacing_placeholder5.hide()
        self.spacing_placeholder6.hide()

        #Add the demo frames to the experiment pages main content layout 
        self.experiment_page_main_content.addWidget(self.frame_DEMO_close_fluidic_circuit)
        self.spacing_placeholder7 = QtWidgets.QWidget()
        self.spacing_placeholder7.setFixedHeight(5)
        self.experiment_page_main_content.addWidget(self.spacing_placeholder7)
        self.experiment_page_main_content.addWidget(self.frame_DEMO_connect_waste_flask)
        self.spacing_placeholder8 = QtWidgets.QWidget()
        self.spacing_placeholder8.setFixedHeight(5)
        self.experiment_page_main_content.addWidget(self.spacing_placeholder8)
        self.experiment_page_main_content.addWidget(self.frame_DEMO_ethanol_flush)
        self.spacing_placeholder9 = QtWidgets.QWidget()
        self.spacing_placeholder9.setFixedHeight(5)
        self.experiment_page_main_content.addWidget(self.spacing_placeholder9)
        self.experiment_page_main_content.addWidget(self.frame_DEMO_connect_to_harvest_flask)
        self.spacing_placeholder10 = QtWidgets.QWidget()
        self.spacing_placeholder10.setFixedHeight(5)
        self.experiment_page_main_content.addWidget(self.spacing_placeholder10)
        self.experiment_page_main_content.addWidget(self.frame_DEMO_blood_sucrose_mix)
        self.spacing_placeholder11 = QtWidgets.QWidget()
        self.spacing_placeholder11.setFixedHeight(5)
        self.experiment_page_main_content.addWidget(self.spacing_placeholder11)
        self.experiment_page_main_content.addWidget(self.frame_DEMO_sample_retrieval)
        self.spacing_placeholder12 = QtWidgets.QWidget()
        self.spacing_placeholder12.setFixedHeight(5)
        self.experiment_page_main_content.addWidget(self.spacing_placeholder12)
        self.experiment_page_main_content.addWidget(self.save_experiment_data_frame)

        # start the page blank by hiding any widgets
        self.frame_DEMO_close_fluidic_circuit.hide()
        self.frame_DEMO_connect_waste_flask.hide()
        self.frame_DEMO_ethanol_flush.hide()
        self.frame_DEMO_connect_to_harvest_flask.hide()
        self.frame_DEMO_blood_sucrose_mix.hide()
        self.frame_DEMO_sample_retrieval.hide()
        self.save_experiment_data_frame.hide()

        self.spacing_placeholder7.hide()
        self.spacing_placeholder8.hide()
        self.spacing_placeholder9.hide()
        self.spacing_placeholder10.hide()
        self.spacing_placeholder11.hide()
        self.spacing_placeholder12.hide()

    #endregion
    
#endregion    
     
    def set_button_style(self, button, font_size=30, enabled=True):
        if enabled:
            button.setStyleSheet(f"""
                QPushButton {{
                    border: 2px solid white;
                    border-radius: 10px;
                    background-color: #222222;
                    color: #FFFFFF;
                    font-family: Archivo;
                    font-size: {font_size}px;
                }}

                QPushButton:hover {{
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }}

                QPushButton:pressed {{
                    background-color: #0796FF;
                }}
            """)
        else:
            button.setStyleSheet(f"""
                QPushButton {{
                    border: 2px solid #444444;
                    border-radius: 10px;
                    background-color: #333333;
                    color: #AAAAAA;
                    font-family: Archivo;
                    font-size: {font_size}px;
                }}
            """)
