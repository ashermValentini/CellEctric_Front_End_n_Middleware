from PyQt5 import QtCore, QtGui, QtWidgets#
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch
from matplotlib.transforms import Bbox
from roundprogressBar import QRoundProgressBar
from roundprogressBar import MainWindow

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        # Load custom font
        QtGui.QFontDatabase.addApplicationFont(r"C:\Users\offic\CellEctric Biosciences\Sepsis Project - Documents\Development\4 Automation and Control Systems\11_GUI\BIO_Team_GUI\GUI_BioTeam\assets\fonts\static/Archivo-Regular.ttf")

        # Set up styles for labels
        title_style = "QLabel { color : #FFFFFF; font-family: Archivo; font-size: 20px; font-weight: bold; }"
        text_style = "QLabel { color : #FFFFFF; font-family: Archivo; font-size: 15px;  font-weight: bold; }"
        header_style = "QLabel { color : #FFFFFF; font-family: Archivo; font-size: 50px; font-weight: bold;  }"
        input_style = "QLabel { color : #FFFFFF; font-family: Archivo; font-size: 20px; font-weight: bold; }"
        
        # Set up the main window 
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 1920)
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
        self.frame_d_sidebar = QtWidgets.QFrame()
        self.frame_d_sidebar.setContentsMargins(0, 0, 0, 0)
        self.frame_d_sidebar.setFixedWidth(int(MainWindow.height() * 0.05))
        self.frame_d_sidebar.setStyleSheet("background-color: #222222;")
        self.frame_d_sidebar.setObjectName("frame_d_sidebar")
        
        self.h_layout.addWidget(self.frame_d_sidebar)
        

        # Add company logo to sidebar
        self.sidebar_logo = QtWidgets.QLabel(self.frame_d_sidebar)
        self.sidebar_logo.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        buffer = 10  # Amount of buffer space on each side
        self.sidebar_logo.setGeometry(buffer, buffer, self.frame_d_sidebar.width() - 2 * buffer,
                                      int(MainWindow.height() * 0.2))

        logo_pixmap = QtGui.QPixmap(
            r'C:\Users\offic\CellEctric Biosciences\Sepsis Project - Documents\Development\4 Automation and Control Systems\11_GUI\BIO_Team_GUI\GUI_BioTeam\assets\images\logo_small_white.png')
        self.sidebar_logo.setPixmap(logo_pixmap.scaled(self.sidebar_logo.width(), self.sidebar_logo.height(),
                                                       QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
    #endregion

    # region: Topbar
    
        self.v_layout = QtWidgets.QVBoxLayout()
        self.h_layout.addLayout(self.v_layout)
        self.h_layout.setSpacing(0)
        self.v_layout.setSpacing(0)
        self.v_layout.setContentsMargins(0, 0, 0, 0)

        
        self.frame_d_topbar = QtWidgets.QFrame()
        self.frame_d_topbar.setContentsMargins(0, 0, 0, 0)
        self.frame_d_topbar.setFixedHeight(int(MainWindow.height() * 0.05))
        self.frame_d_topbar.setStyleSheet("background-color: #222222;")
        self.frame_d_topbar.setObjectName("frame_d_topbar")
        
        self.v_layout.addWidget(self.frame_d_topbar)

        # Set up a layout for the frame_d_topbar
        topbar_layout = QtWidgets.QHBoxLayout(self.frame_d_topbar)
        topbar_layout.setContentsMargins(0, 0, 0, 0)
        self.frame_d_topbar.setLayout(topbar_layout)

        # Add label to top bar
        self.label = QtWidgets.QLabel(self.frame_d_topbar)
        self.label.setText("DASHBOARD")
        self.label.setStyleSheet(header_style)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        topbar_layout.addStretch(1)
        topbar_layout.addWidget(self.label)  # Add the label to the layout
        topbar_layout.addStretch(1)

        # Add experiment button to topbar 
        self.experiment_page_button = QtWidgets.QPushButton(self.frame_d_topbar)
        # load the image as an icon
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("C:/Users/offic/CellEctric Biosciences/Sepsis Project - Documents/Development/4 Automation and Control Systems/11_GUI/BIO_Team_GUI/GUI_BioTeam/assets/images/dark-on.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        # set the icon to the button
        self.experiment_page_button.setIcon(icon)
        # adjust the size of the button's icon to fit properly
        self.experiment_page_button.setIconSize(QtCore.QSize(74,74))  # adjust the size accordingly
        # if you don't want any text on the button, set an empty string as the button text
        self.experiment_page_button.setText('')
        # set the button's style (optional)
        self.experiment_page_button.setStyleSheet('QPushButton {background-color: #222222; border: none;}')  # make the button's background color match with topbar
        # add the button to the layout
        # set the button's style
        self.experiment_page_button.setStyleSheet("""
            QPushButton {
                padding: 0px;
                border: 2px solid white;
                border-radius: 10px;
                background-color: #222222;
                color: #FFFFFF;
                font-family: Archivo;
                font-size: 15px;
                

            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)

        
        topbar_layout.addWidget(self.experiment_page_button)

    #endregion
    
    # region : Main content
        self.main_content = QtWidgets.QVBoxLayout()
        self.main_content.setContentsMargins(0, 0, 0, 0)
        self.v_layout.addLayout(self.main_content)

# region: Applications
        self.application_region = QtWidgets.QHBoxLayout()
        self.main_content.addLayout(self.application_region)

    # region : SUCROSE, EHTANOL, BLOOD frame setups
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
        label_sucrose.setStyleSheet(title_style)
        label_sucrose.setText("SUCROSE")
        label_sucrose.setAlignment(QtCore.Qt.AlignCenter)
        layout_sucrose.addWidget(label_sucrose)  # add label to layout
        layout_sucrose.addSpacing(20)     # Add a fixed amount of vertical space  # Adjust the number for more or less space
        # endregion

        # region: progress bar and button
        progress_button_layout = QtWidgets.QHBoxLayout()  # create layout for progress bar and button

        self.progress_bar_sucrose = QRoundProgressBar()  # create progress bar
        self.progress_bar_sucrose.setFixedSize(65, 65)
        self.progress_bar_sucrose.setRange(0, 5)
        self.progress_bar_sucrose.setValue(0)
        self.progress_bar_sucrose.setBarColor('#0796FF')
        self.progress_bar_sucrose.setDecimals(2)
        
        progress_button_layout.addSpacing(20)  # add fixed space of 20 pixels
        progress_button_layout.addWidget(self.progress_bar_sucrose)  # add progress bar to the layout
        progress_button_layout.addSpacing(20)  # add fixed space of 20 pixels

        self.button_sucrose = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(r'C:\Users\offic\CellEctric Biosciences\Sepsis Project - Documents\Development\4 Automation and Control Systems\11_GUI\BIO_Team_GUI\GUI_BioTeam\assets\images\play_pause.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_sucrose.setIcon(icon)
        self.button_sucrose.setIconSize(QtCore.QSize(24, 24))  # Adjust size as needed
        self.button_sucrose.setStyleSheet("""
            QPushButton {
                border: 2px solid #8f8f91;
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
        unit_label.setStyleSheet("color: white;")

        self.line_edit_sucrose = QtWidgets.QLineEdit()
        self.line_edit_sucrose.setStyleSheet("QLineEdit { color: white; background-color: #222222; }")
        self.line_edit_sucrose.setText("2.50")

        group_box_layout.addWidget(self.line_edit_sucrose)
        group_box_layout.addWidget(unit_label)
        # endregion
        # region: Groupbox 2
        group_box_sucrose_2 = QtWidgets.QGroupBox(self.frame_sucrose)  # create second groupbox
        group_box_sucrose_2.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
        group_box_sucrose_2.setAlignment(QtCore.Qt.AlignCenter)
        group_box_layout_2 = QtWidgets.QHBoxLayout(group_box_sucrose_2)  # create layout for second groupbox
        group_box_sucrose_2.setLayout(group_box_layout_2)  # set layout to second groupbox

        unit_label_2 = QtWidgets.QLabel("s")  # unit for time variable
        unit_label_2.setStyleSheet("color: white;")

        self.line_edit_sucrose_2 = QtWidgets.QLineEdit()
        self.line_edit_sucrose_2.setStyleSheet("QLineEdit { color: white; background-color: #222222; }")
        self.line_edit_sucrose_2.setText("NF")

        group_box_layout_2.addWidget(self.line_edit_sucrose_2)
        group_box_layout_2.addWidget(unit_label_2)
        # endregion
        group_boxes_layout.addWidget(group_box_sucrose)
        group_boxes_layout.addWidget(group_box_sucrose_2)
        layout_sucrose.addLayout(group_boxes_layout)  # add layout for group boxes to main layout
        #endregion

        # endregion
        
        # region : Blood
        self.frame_blood = QtWidgets.QFrame()                                               # create blood frame 
        self.frame_blood.setStyleSheet("background-color: #222222; border-radius: 15px;")   
        self.frame_blood.setObjectName("frame_d_bloodFlowrate")
        
        layout_blood = QtWidgets.QVBoxLayout(self.frame_blood)                              # create layout for blood frame 
        self.frame_blood.setLayout(layout_blood)                                            # set layout to blood frame
        layout_blood.setAlignment(QtCore.Qt.AlignCenter)
        
        #region : label
        label_blood = QtWidgets.QLabel(self.frame_blood)
        label_blood.setStyleSheet(title_style)
        label_blood.setText("BLOOD")
        label_blood.setAlignment(QtCore.Qt.AlignCenter)
        #endregion
        
        #region : group box
        group_box_blood = QtWidgets.QGroupBox(self.frame_blood)
        group_box_blood.setStyleSheet("""
                                        QGroupBox {
                                            border: 2px solid white;
                                            border-radius: 10px;
                                            background-color: #222222;
                                        }
                                        QGroupBox:hover {
                                            background-color: rgba(255, 255, 255, 0.5);
                                        }
                                    """)
        group_box_blood.setAlignment(QtCore.Qt.AlignCenter)

        # Create a QHBoxLayout for the group box
        group_box_layout_blood = QtWidgets.QHBoxLayout(group_box_blood)

        # Create the QLabel for the unit
        unit_label_blood = QtWidgets.QLabel("ml/min")
        unit_label_blood.setStyleSheet("color: white;")

        # Create the QLineEdit for the value
        self.line_edit_blood = QtWidgets.QLineEdit()
        self.line_edit_blood.setStyleSheet("QLineEdit { color: white; background-color: #222222; }")

        # Add the line edit and label to the group box layout
        group_box_layout_blood.addWidget(self.line_edit_blood)
        group_box_layout_blood.addWidget(unit_label_blood)

        # Set the group box layout
        group_box_blood.setLayout(group_box_layout_blood)        
        #endregion 
        
        layout_blood.addWidget(label_blood)                                                 #add label to layout
        layout_blood.addWidget(group_box_blood)                                             #add group box to layout 
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
        label_ethanol.setStyleSheet(title_style)
        label_ethanol.setText("ETHANOL")
        label_ethanol.setAlignment(QtCore.Qt.AlignCenter)
        layout_ethanol.addWidget(label_ethanol)  # add label to layout
        layout_ethanol.addSpacing(20)     # Add a fixed amount of vertical space  # Adjust the number for more or less space
        # endregion

        # region: progress bar and button
        progress_button_layout = QtWidgets.QHBoxLayout()  # create layout for progress bar and button

        self.progress_bar_ethanol = QRoundProgressBar()  # create progress bar
        self.progress_bar_ethanol.setFixedSize(65, 65)
        self.progress_bar_ethanol.setRange(0, 10)
        self.progress_bar_ethanol.setValue(0)
        self.progress_bar_ethanol.setDecimals(2)
        self.progress_bar_ethanol.setBarColor('#0796FF')
        
        progress_button_layout.addSpacing(20)  # add fixed space of 20 pixels
        progress_button_layout.addWidget(self.progress_bar_ethanol)  # add progress bar to the layout
        progress_button_layout.addSpacing(20)  # add fixed space of 20 pixels

        self.button_ethanol = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(r'C:\Users\offic\CellEctric Biosciences\Sepsis Project - Documents\Development\4 Automation and Control Systems\11_GUI\BIO_Team_GUI\GUI_BioTeam\assets\images\play_pause.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_ethanol.setIcon(icon)
        self.button_ethanol.setIconSize(QtCore.QSize(24, 24))  # Adjust size as needed
        self.button_ethanol.setStyleSheet("""
            QPushButton {
                border: 2px solid #8f8f91;
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
        unit_label.setStyleSheet("color: white;")

        self.line_edit_ethanol = QtWidgets.QLineEdit()
        self.line_edit_ethanol.setStyleSheet("QLineEdit { color: white; background-color: #222222; }")
        self.line_edit_ethanol.setText("2.50")
        group_box_layout.addWidget(self.line_edit_ethanol)
        group_box_layout.addWidget(unit_label)
        # endregion
        # region: Groupbox 2
        group_box_ethanol_2 = QtWidgets.QGroupBox(self.frame_ethanol)  # create second groupbox
        group_box_ethanol_2.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
        group_box_ethanol_2.setAlignment(QtCore.Qt.AlignCenter)
        group_box_layout_2 = QtWidgets.QHBoxLayout(group_box_ethanol_2)  # create layout for second groupbox
        group_box_ethanol_2.setLayout(group_box_layout_2)  # set layout to second groupbox

        unit_label_2 = QtWidgets.QLabel("s")  # unit for time variable
        unit_label_2.setStyleSheet("color: white;")

        self.line_edit_ethanol_2 = QtWidgets.QLineEdit()
        self.line_edit_ethanol_2.setStyleSheet("QLineEdit { color: white; background-color: #222222; }")
        self.line_edit_ethanol_2.setText("NF")

        group_box_layout_2.addWidget(self.line_edit_ethanol_2)
        group_box_layout_2.addWidget(unit_label_2)
        # endregion
        group_boxes_layout.addWidget(group_box_ethanol)
        group_boxes_layout.addWidget(group_box_ethanol_2)
        layout_ethanol.addLayout(group_boxes_layout)  # add layout for group boxes to main layout
        #endregion

        # endregion
        
        #adding each of the frames to the application region 1 and then adding application region 1 to application region
        self.application_region_1_layout.addWidget(self.frame_sucrose)
        self.application_region_1_layout.addWidget(self.frame_ethanol)
        self.application_region_1_layout.addWidget(self.frame_blood)
        self.application_region.addWidget(self.application_region_1_widget)
    #endregion
    
    # region : CONNECTION and PLOT frame setup  
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
        title_style = "QLabel { color : #FFFFFF; font-family: Archivo; font-size: 20px; font-weight: bold; }"  # Add font-weight: bold; to make the text bold
        label.setStyleSheet(title_style)
        label.setText("CONNECTIONS")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)  # Add the label to the layout

        # Add a spacer for some vertical space
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)  # Adjust the second parameter for more or less space
        layout.addItem(spacer)

        # List of module names
        module_names = ["Pulse Generator", "PSU", "Temperature Sensor", "3PAC", "Pressure Sensor"]

        # Dictionary to hold the circles
        self.circles = {}

        for module in module_names:
            # Create a layout for the module name and circle
            module_layout = QtWidgets.QHBoxLayout()
            
            # Create the module label and add it to the layout
            module_label = QtWidgets.QLabel()
            module_label.setStyleSheet(text_style) 
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

        layout.addStretch(1)

        self.application_region_2_layout.addWidget(frame)
        #endregion 
        
        # region : Frame for plot buttons
        plot_button_frame = QtWidgets.QFrame()
        plot_button_frame.setStyleSheet("background-color: #222222; border-radius: 15px;")
        plot_button_frame.setObjectName("frame_d_voltageSignal")
                
        # Create a layout for the frame
        layout = QtWidgets.QVBoxLayout(plot_button_frame)
        
        # Label
        label = QtWidgets.QLabel()
        label.setStyleSheet(title_style)
        label.setText("PLOTS")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)  
        layout.addSpacing(20)    
        
        # button creation
        self.temp_button = QtWidgets.QPushButton("Electrode Temperature")  # Set the text to empty since we are using an image
        self.temp_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 10px;
                background-color: #222222;
                color: #FFFFFF;
                font-family: Archivo;
                font-size: 15px;

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
                font-size: 15px;
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
                font-size: 15px;
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
      
      
        self.application_region_2_layout.addWidget(plot_button_frame)
        
        #endregion
        
        self.application_region.addWidget(self.application_region_2_widget)
    #endregion
    
    # region : ELECTRODE TEMP and SIGNAL frames' setup
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

        # Spacer
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        # Title for temperature frame
        title_label = QtWidgets.QLabel("ELECTRODE TEMP.")
        title_label.setStyleSheet(title_style)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        temp_layout.addWidget(title_label)
        temp_layout.addItem(spacer)

        # Layout for image and stats
        temp_details_layout = QtWidgets.QHBoxLayout()
        temp_layout.addLayout(temp_details_layout)

        # Add image to temperature frame
        self.temp_image = QtWidgets.QLabel()
        self.temp_image.setAlignment(QtCore.Qt.AlignCenter)
        temp_image_pixmap = QtGui.QPixmap(
            r'C:\Users\offic\CellEctric Biosciences\Sepsis Project - Documents\Development\4 Automation and Control Systems\11_GUI\BIO_Team_GUI\GUI_BioTeam\assets\images\boxplot_blue.png')
        scaled_image = temp_image_pixmap.scaled(int(self.temp_image.width() * 0.30),
                                                int(self.temp_image.height() * 0.30),
                                                QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.temp_image.setPixmap(scaled_image)
        temp_details_layout.addWidget(self.temp_image)

        # Add temperature statistics next to image
        temp_stats_layout = QtWidgets.QVBoxLayout()
        temp_details_layout.addLayout(temp_stats_layout)

        # Example temperature statistics
        max_temp_label = QtWidgets.QLabel("35°")
        max_temp_label.setStyleSheet(input_style)
        temp_stats_layout.addWidget(max_temp_label, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        avg_temp_label = QtWidgets.QLabel("25°")
        avg_temp_label.setStyleSheet(input_style)
        temp_stats_layout.addWidget(avg_temp_label, alignment=QtCore.Qt.AlignCenter)

        min_temp_label = QtWidgets.QLabel("15°")
        min_temp_label.setStyleSheet(input_style)
        temp_stats_layout.addWidget(min_temp_label, alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)

        # Add vertical spacer for equal spacing
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        temp_layout.addItem(spacer)
        #endregion
        
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
        label.setStyleSheet(title_style)  # Set the color of the text as needed
        
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
        unit_label.setStyleSheet("color: white;")

        # Create the QLabel for the higher pk-pk voltage
        MAX_label = QtWidgets.QLabel("MAX :")
        MAX_label.setStyleSheet("color: white;")

        # Create the QLineEdit for the value
        self.line_edit_max_signal = QtWidgets.QLineEdit()
        self.line_edit_max_signal.setStyleSheet("QLineEdit { color: white; background-color: #222222; }")

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
        min_unit_label.setStyleSheet("color: white;")

        # Create the QLabel for the higher pk-pk voltage
        MIN_label = QtWidgets.QLabel("MIN : ")
        MIN_label.setStyleSheet("color: white;")

        # Create the QLineEdit for the value
        self.line_edit_min_signal = QtWidgets.QLineEdit()
        self.line_edit_min_signal.setStyleSheet("QLineEdit { color: white; background-color: #222222; }")

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
        icon.addPixmap(QtGui.QPixmap(r'C:\Users\offic\CellEctric Biosciences\Sepsis Project - Documents\Development\4 Automation and Control Systems\11_GUI\BIO_Team_GUI\GUI_BioTeam\assets\images\lightning_symbol.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.psu_button.setIcon(icon)
        self.psu_button.setIconSize(QtCore.QSize(64, 64))  # Adjust size as needed
        self.psu_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #8f8f91;
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
        self.axes_voltage.spines['bottom'].set_color('#5C5C5D')
        self.axes_voltage.spines['top'].set_color('#5C5C5D')
        self.axes_voltage.spines['right'].set_color('#5C5C5D')
        self.axes_voltage.spines['left'].set_color('#5C5C5D')
        self.axes_voltage.tick_params(colors='#FFFFFF')
        
        # Set static labels
        self.axes_voltage.set_xlabel('Time (ms)', color='#FFFFFF')
        self.axes_voltage.set_ylabel('Temperature (°C)', color='#FFFFFF')
        self.axes_voltage.set_title('My Title', color='#FFFFFF')
        

    #endregion
    
    # endregion : Main content 
        
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.main_content.setStretchFactor(self.application_region, 50)
        self.main_content.setStretchFactor(self.plot_layout, 50)    
#endregion

#region : Experiment Page Layout        
    # region : Sidebar

        self.h_layout = QtWidgets.QHBoxLayout(self.experiment)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
    
        self.frame_d_sidebar = QtWidgets.QFrame()
        self.frame_d_sidebar.setContentsMargins(0, 0, 0, 0)
        self.frame_d_sidebar.setFixedWidth(int(MainWindow.height() * 0.05))
        self.frame_d_sidebar.setStyleSheet("background-color: #222222;")
        self.frame_d_sidebar.setObjectName("frame_d_sidebar")
        
        self.h_layout.addWidget(self.frame_d_sidebar)
        

        # Add company logo to sidebar
        self.sidebar_logo = QtWidgets.QLabel(self.frame_d_sidebar)
        self.sidebar_logo.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        buffer = 10  # Amount of buffer space on each side
        self.sidebar_logo.setGeometry(buffer, buffer, self.frame_d_sidebar.width() - 2 * buffer,
                                      int(MainWindow.height() * 0.2))

        logo_pixmap = QtGui.QPixmap(
            r'C:\Users\offic\CellEctric Biosciences\Sepsis Project - Documents\Development\4 Automation and Control Systems\11_GUI\BIO_Team_GUI\GUI_BioTeam\assets\images\logo_small_white.png')
        self.sidebar_logo.setPixmap(logo_pixmap.scaled(self.sidebar_logo.width(), self.sidebar_logo.height(),
                                                       QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
    #endregion

    # region: Topbar
    
        self.v_layout = QtWidgets.QVBoxLayout()
        self.h_layout.addLayout(self.v_layout)
        self.h_layout.setSpacing(0)
        self.v_layout.setSpacing(0)
        self.v_layout.setContentsMargins(0, 0, 0, 0)

        
        self.frame_d_topbar = QtWidgets.QFrame()
        self.frame_d_topbar.setContentsMargins(0, 0, 0, 0)
        self.frame_d_topbar.setFixedHeight(int(MainWindow.height() * 0.05))
        self.frame_d_topbar.setStyleSheet("background-color: #222222;")
        self.frame_d_topbar.setObjectName("frame_d_topbar")
        
        self.v_layout.addWidget(self.frame_d_topbar)


        # Add "Dashboard" label to top bar
        self.label = QtWidgets.QLabel(self.frame_d_topbar)
        self.label.setText("EXPERIMENT")
        self.label.setStyleSheet(header_style)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        # Set up a layout for the frame_d_topbar
        topbar_layout = QtWidgets.QHBoxLayout(self.frame_d_topbar)
        topbar_layout.setContentsMargins(0, 0, 0, 0)
        self.frame_d_topbar.setLayout(topbar_layout)
        topbar_layout.addWidget(self.label)  # Add the label to the layout


    #endregion
    
    # region : Main content
        self.main_content = QtWidgets.QVBoxLayout()
        self.main_content.setContentsMargins(0, 0, 0, 0)
        self.v_layout.addLayout(self.main_content)
    #endregion
    
#endregion    
    
    
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

