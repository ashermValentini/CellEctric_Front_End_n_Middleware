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
        QtGui.QFontDatabase.addApplicationFont(r"C:\Users\offic\CellEctric Biosciences\Sepsis Project - Documents\Development\4 Automation and Control Systems\11_GUI\BIO_TEAM_GUI\assets\fonts\static/Archivo-Regular.ttf")

        # Set up styles for labels
        title_style = "QLabel { color : #FFFFFF; font-family: Archivo; font-size: 20px; }"
        text_style = "QLabel { color : #FFFFFF; font-family: Archivo; font-size: 5px; }"
        header_style = "QLabel { color : #FFFFFF; font-family: Archivo; font-size: 50px; }"
        input_style = "QLabel { color : #FFFFFF; font-family: Archivo; font-size: 20px; }"

    # Dashboard
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 1920)
        MainWindow.setStyleSheet("background-color: #121212;")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.h_layout = QtWidgets.QHBoxLayout(self.centralwidget)

    # Sidebar
    
        #side bar frame
        self.frame_d_sidebar = QtWidgets.QFrame(self.centralwidget)
        self.frame_d_sidebar.setFixedWidth(int(MainWindow.height() * 0.05))
        self.frame_d_sidebar.setStyleSheet("background-color: #222222;")
        self.frame_d_sidebar.setObjectName("frame_d_sidebar")
        
        #side bar layout 
        self.h_layout.addWidget(self.frame_d_sidebar)
        self.h_layout.setContentsMargins(0, 0, 0, 0)

        # Add company logo to sidebar
        self.sidebar_logo = QtWidgets.QLabel(self.frame_d_sidebar)
        self.sidebar_logo.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        buffer = 10  # Amount of buffer space on each side
        self.sidebar_logo.setGeometry(buffer, 0, self.frame_d_sidebar.width() - 2 * buffer,
                                      int(MainWindow.height() * 0.2))

        logo_pixmap = QtGui.QPixmap(
            r'C:\Users\offic\CellEctric Biosciences\Sepsis Project - Documents\Development\4 Automation and Control Systems\11_GUI\BIO_TEAM_GUI\assets\images\logo_small_white.png')
        self.sidebar_logo.setPixmap(logo_pixmap.scaled(self.sidebar_logo.width(), self.sidebar_logo.height(),
                                                       QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        self.v_layout = QtWidgets.QVBoxLayout()
        self.h_layout.addLayout(self.v_layout)
        self.v_layout.setContentsMargins(0, 0, 0, 0)


    # Topbar
        self.frame_d_topbar = QtWidgets.QFrame(self.centralwidget)
        self.frame_d_topbar.setFixedHeight(int(MainWindow.height() * 0.05))
        self.frame_d_topbar.setStyleSheet("background-color: #222222;")
        self.frame_d_topbar.setObjectName("frame_d_topbar")

        # Add "Dashboard" label to top bar
        self.label = QtWidgets.QLabel(self.frame_d_topbar)
        self.label.setText("Dashboard")
        self.label.setStyleSheet(header_style)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        # Set up a layout for the frame_d_topbar
        topbar_layout = QtWidgets.QHBoxLayout(self.frame_d_topbar)
        topbar_layout.setContentsMargins(0, 0, 0, 0)  # Set layout margins to zero
        topbar_layout.addWidget(self.label)  # Add the label to the layout

        # Set the layout for frame_d_topbar
        self.frame_d_topbar.setLayout(topbar_layout)

        # Add the frame_d_topbar to the main layout (self.v_layout)
        self.v_layout.addWidget(self.frame_d_topbar)

    # Main content region
        self.main_content = QtWidgets.QVBoxLayout()
        self.v_layout.addLayout(self.main_content)

    # Application region of main content region
        self.application_region = QtWidgets.QHBoxLayout()
        self.main_content.addLayout(self.application_region)

    # Flowrate frame setups
        self.application_region_1_widget = QtWidgets.QWidget(self.centralwidget)
        self.application_region_1_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.application_region_1_layout = QtWidgets.QVBoxLayout(self.application_region_1_widget)

    # Frame sucroseFlowrate
        self.frame_sucrose = QtWidgets.QFrame(self.centralwidget)
        self.frame_sucrose.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.frame_sucrose.setObjectName("frame_d_sucroseFlowrate")

        label_sucrose = QtWidgets.QLabel(self.frame_sucrose)
        label_sucrose.setStyleSheet(title_style)
        label_sucrose.setText("Sucrose Flow Rate")
        label_sucrose.setAlignment(QtCore.Qt.AlignCenter)

        #frame to hold the progress bar 
        progress_bar_frame = QtWidgets.QFrame(self.frame_sucrose)
        progress_bar_frame.setObjectName("progress_bar_frame")

        self.progress_bar_sucrose = QRoundProgressBar()
        self.progress_bar_sucrose.setFixedSize(65, 65)
        self.progress_bar_sucrose.setRange(0, 10)  # Set the range to 0-10ml
        self.progress_bar_sucrose.setValue(0)  # Set the initial value to 0
        self.progress_bar_sucrose.setBarColor('#0796FF')

        
        # Create a layout for the progress bar frame
        progress_bar_layout = QtWidgets.QHBoxLayout(progress_bar_frame)
        progress_bar_layout.setAlignment(QtCore.Qt.AlignCenter)
        progress_bar_layout.addWidget(self.progress_bar_sucrose)

        # Create a QGroupBox for the line edit and label
        group_box_sucrose = QtWidgets.QGroupBox(self.frame_sucrose)
        group_box_sucrose.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
        group_box_sucrose.setAlignment(QtCore.Qt.AlignCenter)

        # Create a QHBoxLayout for the group box
        group_box_layout = QtWidgets.QHBoxLayout(group_box_sucrose)

        # Create the QLabel for the unit
        unit_label = QtWidgets.QLabel("ml/min")
        unit_label.setStyleSheet("color: white;")

        # Create the QLineEdit for the value
        self.line_edit_sucrose = QtWidgets.QLineEdit()
        self.line_edit_sucrose.setStyleSheet("QLineEdit { color: white; background-color: #222222; }")

        # Add the line edit and label to the group box layout
        group_box_layout.addWidget(self.line_edit_sucrose)
        group_box_layout.addWidget(unit_label)

        # Set the group box layout
        group_box_sucrose.setLayout(group_box_layout)

        
        layout_sucrose = QtWidgets.QVBoxLayout(self.frame_sucrose)
        layout_sucrose.setAlignment(QtCore.Qt.AlignCenter)
        layout_sucrose.addWidget(label_sucrose)
        layout_sucrose.addWidget(progress_bar_frame)
        layout_sucrose.addWidget(group_box_sucrose)

        self.frame_sucrose.setLayout(layout_sucrose)

    # Frame blood flow rate
        self.frame_blood = QtWidgets.QFrame(self.centralwidget)
        self.frame_blood.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.frame_blood.setObjectName("frame_d_bloodFlowrate")

        label_blood = QtWidgets.QLabel(self.frame_blood)
        label_blood.setStyleSheet(title_style)
        label_blood.setText("Blood Flow Rate")
        label_blood.setAlignment(QtCore.Qt.AlignCenter)

        # Frame to hold the progress bar
        #progress_bar_frame_blood = QtWidgets.QFrame(self.frame_blood)
        #progress_bar_frame_blood.setObjectName("progress_bar_frame_blood")

        #self.progress_bar_blood = QRoundProgressBar()
        #self.progress_bar_blood.setFixedSize(65, 65)
        #self.progress_bar_blood.setRange(0, 10)  # Set the range to 0-10ml
        #self.progress_bar_blood.setValue(0)  # Set the initial value to 0

        # Create a layout for the progress bar frame
        #progress_bar_layout_blood = QtWidgets.QHBoxLayout(progress_bar_frame_blood)
        #progress_bar_layout_blood.setAlignment(QtCore.Qt.AlignCenter)
        #progress_bar_layout_blood.addWidget(self.progress_bar_blood)

        # Create a QGroupBox for the line edit and label
        group_box_blood = QtWidgets.QGroupBox(self.frame_blood)
        group_box_blood.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
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

        layout_blood = QtWidgets.QVBoxLayout(self.frame_blood)
        layout_blood.setAlignment(QtCore.Qt.AlignCenter)
        layout_blood.addWidget(label_blood)
        #layout_blood.addWidget(progress_bar_frame_blood)
        layout_blood.addWidget(group_box_blood)

        self.frame_blood.setLayout(layout_blood)


    #Frame and label for "ethanolFlowrate"
        self.frame_ethanol = QtWidgets.QFrame(self.centralwidget)
        self.frame_ethanol.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.frame_ethanol.setObjectName("frame_d_ethanolFlowrate")
        

        label_ethanol = QtWidgets.QLabel(self.frame_ethanol)
        label_ethanol.setStyleSheet(title_style)
        label_ethanol.setText("Ethanol Flow Rate")
        label_ethanol.setAlignment(QtCore.Qt.AlignCenter)

        # Frame to hold the progress bar
        progress_bar_frame_ethanol = QtWidgets.QFrame(self.frame_ethanol)
        progress_bar_frame_ethanol.setObjectName("progress_bar_frame_ethanol")

        self.progress_bar_ethanol = QRoundProgressBar()
        self.progress_bar_ethanol.setFixedSize(65, 65)
        self.progress_bar_ethanol.setRange(0, 10)  # Set the range to 0-10ml
        self.progress_bar_ethanol.setValue(0)  # Set the initial value to 0
        self.progress_bar_ethanol.setBarColor('#0796FF')


        # Create a layout for the progress bar frame
        progress_bar_layout_ethanol = QtWidgets.QHBoxLayout(progress_bar_frame_ethanol)
        progress_bar_layout_ethanol.setAlignment(QtCore.Qt.AlignCenter)
        progress_bar_layout_ethanol.addWidget(self.progress_bar_ethanol)

        # Create a QGroupBox for the line edit and label
        group_box_ethanol = QtWidgets.QGroupBox(self.frame_ethanol)
        group_box_ethanol.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
        group_box_ethanol.setAlignment(QtCore.Qt.AlignCenter)

        # Create a QHBoxLayout for the group box
        group_box_layout_ethanol = QtWidgets.QHBoxLayout(group_box_ethanol)

        # Create the QLabel for the unit
        unit_label_ethanol = QtWidgets.QLabel("ml/min")
        unit_label_ethanol.setStyleSheet("color: white;")

        # Create the QLineEdit for the value
        self.line_edit_ethanol = QtWidgets.QLineEdit()
        self.line_edit_ethanol.setStyleSheet("QLineEdit { color: white; background-color: #222222; }")

        # Add the line edit and label to the group box layout
        group_box_layout_ethanol.addWidget(self.line_edit_ethanol)
        group_box_layout_ethanol.addWidget(unit_label_ethanol)

        # Set the group box layout
        group_box_ethanol.setLayout(group_box_layout_ethanol)

        layout_ethanol = QtWidgets.QVBoxLayout(self.frame_ethanol)
        layout_ethanol.setAlignment(QtCore.Qt.AlignCenter)
        layout_ethanol.addWidget(label_ethanol)
        layout_ethanol.addWidget(progress_bar_frame_ethanol)
        layout_ethanol.addWidget(group_box_ethanol)

        self.frame_ethanol.setLayout(layout_ethanol)
        
    #adding each of the frames to the application region 1 and then adding application region 1 to application region
        self.application_region_1_layout.addWidget(self.frame_sucrose)
        self.application_region_1_layout.addWidget(self.frame_ethanol)
        self.application_region_1_layout.addWidget(self.frame_blood)
        self.application_region.addWidget(self.application_region_1_widget)

    # Dilution and voltage signal frame setup
        self.application_region_2_widget = QtWidgets.QWidget(self.centralwidget)
        self.application_region_2_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.application_region_2_layout = QtWidgets.QVBoxLayout(self.application_region_2_widget)

    # Frame for dilution
        frame = QtWidgets.QFrame(self.centralwidget)
        frame.setStyleSheet("background-color: #222222; border-radius: 15px;")
        frame.setObjectName("frame_d_dilution")

        # Create a layout for the frame
        layout = QtWidgets.QVBoxLayout(frame)
        
        # Create the label and add it to the layout
        label = QtWidgets.QLabel()
        label.setStyleSheet(title_style)
        label.setText("Electronics")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)  # Add the label to the layout

        layout.addStretch(1)

        self.application_region_2_layout.addWidget(frame)
        
    # Frame for voltage signal
        frame = QtWidgets.QFrame(self.centralwidget)
        frame.setStyleSheet("background-color: #222222; border-radius: 15px;")
        frame.setObjectName("frame_d_voltageSignal")
                
        # Create a layout for the frame
        layout = QtWidgets.QVBoxLayout(frame)
        
        # Create the label and add it to the layout
        label = QtWidgets.QLabel()
        label.setStyleSheet(title_style)
        label.setText("Voltage")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)  # Add the label to the layout
        layout.addStretch(1)#
        
        self.application_region_2_layout.addWidget(frame)

        self.application_region.addWidget(self.application_region_2_widget)

    # Temperature and PSU enable button frame setup
        self.application_region_3_widget = QtWidgets.QWidget(self.centralwidget)
        self.application_region_3_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.application_region_3_layout = QtWidgets.QVBoxLayout(self.application_region_3_widget)

    # Frame for temperature
        temp_frame = QtWidgets.QFrame(self.centralwidget)
        temp_frame.setStyleSheet("background-color: #222222; border-radius: 15px; height: 20%;")
        temp_frame.setObjectName("frame_d_temperature")
        self.application_region_3_layout.addWidget(temp_frame)

        # Layout for temperature components
        temp_layout = QtWidgets.QVBoxLayout(temp_frame)

        # Spacer
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        # Title for temperature frame
        title_label = QtWidgets.QLabel("Electrode Temp")
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
            r'C:\Users\offic\CellEctric Biosciences\Sepsis Project - Documents\Development\4 Automation and Control Systems\11_GUI\BIO_TEAM_GUI\assets\images\boxplot_blue.png')
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

    # Frame for PSU button
        frame_d_psuButton = QtWidgets.QFrame(self.centralwidget)
        frame_d_psuButton.setStyleSheet("background-color: #222222; border-radius: 15px;")
        frame_d_psuButton.setObjectName("frame_d_psuButton")

        # Add a layout to this frame
        frame_d_psuButton_layout = QtWidgets.QVBoxLayout(frame_d_psuButton)

        self.application_region_3_layout.addWidget(frame_d_psuButton)

        # PSU button creation
        self.psu_button = QtWidgets.QPushButton("", frame_d_psuButton) # Set the text to empty since we are using an image
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(r'C:\Users\offic\CellEctric Biosciences\Sepsis Project - Documents\Development\4 Automation and Control Systems\11_GUI\BIO_TEAM_GUI\assets\images\lightning_symbol.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.psu_button.setIcon(icon)
        self.psu_button.setIconSize(QtCore.QSize(74, 74)) # Adjust size as needed
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

        # Center the button within the frame's layout
        frame_d_psuButton_layout.addWidget(self.psu_button, 0, QtCore.Qt.AlignCenter)
        
        self.application_region.addWidget(self.application_region_3_widget)

    # Plot region of the main content region
    
        # Plot region of the main content region
        self.plot_layout = QtWidgets.QVBoxLayout()
        self.plot_layout.setContentsMargins(10, 0, 10, 0)
        self.main_content.addLayout(self.plot_layout)
        
        # Create the Matplotlib canvas for voltage plot
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
        self.axes_voltage.xaxis.label.set_color('#5C5C5D')
        self.axes_voltage.yaxis.label.set_color('#5C5C5D')
        self.axes_voltage.tick_params(colors='#5C5C5D')
        
        # Set static labels
        self.axes_voltage.set_xlabel('Time (ms)', color='#FFFFFF')
        self.axes_voltage.set_ylabel('Temperature (°C)', color='#FFFFFF')
        self.axes_voltage.set_title('My Title', color='#FFFFFF')
        
        # Create the Matplotlib canvas for current plot
        self.canvas_current = FigureCanvas(Figure(figsize=(4, 2), dpi=100))
        self.canvas_current.setObjectName("canvas_current_plot")
        #self.plot_layout.addWidget(self.canvas_current)

        # Get the Axes object from the Figure for current plot
        self.axes_current = self.canvas_current.figure.add_subplot(111)
        self.axes_current.grid(True, color='white', linestyle='--')
        self.axes_current.set_facecolor('#222222')
        self.axes_current.spines['bottom'].set_color('#5C5C5D')
        self.axes_current.spines['top'].set_color('#5C5C5D')
        self.axes_current.spines['right'].set_color('#5C5C5D')
        self.axes_current.spines['left'].set_color('#5C5C5D')
        self.axes_current.xaxis.label.set_color('#5C5C5D')
        self.axes_current.yaxis.label.set_color('#5C5C5D')
        self.axes_current.tick_params(colors='#5C5C5D')
        # Set static labels
        self.axes_voltage.set_xlabel('Time (ms)', color='#5C5C5D')
        self.axes_voltage.set_ylabel('Temperature (°C)', color='#5C5C5D')

    #end layout 
    
    
        MainWindow.setCentralWidget(self.centralwidget)

        self.main_content.setStretchFactor(self.application_region, 50)
        self.main_content.setStretchFactor(self.plot_layout, 50)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

