from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QProgressBar, QDialog, QVBoxLayout, QLabel, QTextEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch
from matplotlib.transforms import Bbox


import resources_rc
import styling.application_style as application_style
import constants.defaults

from views.layout_temperature_frame import TemperatureFrame
from views.layout_signal_frame import SignalFrame
from views.layout_plotting_frame import PlottingFrame
from views.layout_connections_frame import ConnectionsFrame
from views.layout_sucrose_ethanol_frames import SucroseEthanolFrame
from views.layout_blood_frame import BloodFrame
from views.layout_fluidic_motors_frame import FluidicMotorsFrame
from views.layout_flask_motor_frame import FlaskMotorsFrame
from views.layout_workflow_subevent_frame import CustomExperimentFrame
from views.layout_popup_dialogues import SyringeSettingsPopupWindow

#===============================
# MAIN WINDOW LAYOUT CLASS
#===============================

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):

# region: main window setup
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

        # Initialize the SyringeSettingsPopupWindow but do not show it
        self.syringeSettingsPopup = SyringeSettingsPopupWindow(title="Syringe Diameter Settings", description="Select the standard diameter.")

        # Layout for the central widget
        self.central_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.central_layout.addWidget(self.stack)
        
        # Give all buttons the same padding in this layout 
        QtWidgets.QApplication.instance().setStyleSheet("""
            QPushButton {
                padding: 10px;
                }
         """)
#endregion
 
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
        self.reset_button_style(self.button_lights, border_radius=6)

        # Create the button to home the motors
        self.button_motors_home  = QtWidgets.QPushButton() 
        buffer = 10  
        self.button_motors_home.setGeometry(buffer, buffer, self.frame_d_sidebar.width() - 3 * buffer, int(MainWindow.height() * 0.2))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/all_directions.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_motors_home.setIcon(icon)
        self.button_motors_home.setIconSize(QtCore.QSize(40, 40))  # Adjust size as needed
        self.reset_button_style(self.button_motors_home, border_radius=6)
        
        # Create the button for routing to the experiment page 
        self.button_experiment_route  = QtWidgets.QPushButton() 
        buffer = 10  
        self.button_experiment_route.setGeometry(buffer, buffer, self.frame_d_sidebar.width() - 3 * buffer, int(MainWindow.height() * 0.2))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/flasks_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_experiment_route.setIcon(icon)
        self.button_experiment_route.setIconSize(QtCore.QSize(40, 40))  # Adjust size as needed
        self.reset_button_style(self.button_experiment_route, border_radius=6)

        # Create the button for dashboard data recording  
        self.button_dashboard_data_recording  = QtWidgets.QPushButton() 
        buffer = 10  
        self.button_dashboard_data_recording.setGeometry(buffer, buffer, self.frame_d_sidebar.width() - 3 * buffer, int(MainWindow.height() * 0.2))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/record_button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_dashboard_data_recording.setIcon(icon)
        self.button_dashboard_data_recording.setIconSize(QtCore.QSize(40, 40))  # Adjust size as needed
        self.reset_button_style(self.button_dashboard_data_recording, border_radius=6)

        
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
        self.sucrose_frame = SucroseEthanolFrame('SUCROSE', constants.defaults.sucrose_default, 50)
        self.application_region_1_layout.addWidget(self.sucrose_frame)
        #endregion
                
        # region : Ethanol        
        self.ethanol_frame = SucroseEthanolFrame('ETHANOL', 5, 50)
        self.application_region_1_layout.addWidget(self.ethanol_frame)
        # endregion
        
        #region : Blood 
        self.blood_frame = BloodFrame()
        self.application_region_1_layout.addWidget(self.blood_frame)
        #endregion

        self.application_region.addWidget(self.application_region_1_widget)    
    
    #endregion : LEFT FRAMES

    # region : MIDDLE FRAMES  
        self.application_region_2_widget = QtWidgets.QWidget()
        self.application_region_2_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.application_region_2_layout = QtWidgets.QVBoxLayout(self.application_region_2_widget)

        # region : Frame for connections
        self.connections_frame = ConnectionsFrame()
        self.application_region_2_layout.addWidget(self.connections_frame)
        #endregion 
        
        # region : Frame for plot buttons
        self.plotting_frame = PlottingFrame()
        self.application_region_2_layout.addWidget(self.plotting_frame) 
        #endregion
        
        # region : Frame for fluidic motors
        self.fluidic_motors_frame = FluidicMotorsFrame()
        self.application_region_2_layout.addWidget(self.fluidic_motors_frame)
        # endregion
        
        self.application_region.addWidget(self.application_region_2_widget)
    #endregion
    
    # region : RIGHT FRAMES 
        self.application_region_3_widget = QtWidgets.QWidget()
        self.application_region_3_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.application_region_3_layout = QtWidgets.QVBoxLayout(self.application_region_3_widget)

        # region: Frame for temperature
        self.temperature_frame = TemperatureFrame()
        self.application_region_3_layout.addWidget(self.temperature_frame)
        #endregion
        
        # region: (not in use atm) Frame for resevoir pressure reading/reseting 
        pressure_frame = QtWidgets.QFrame()
        pressure_frame.setStyleSheet("background-color: #222222; border-radius: 15px; height: 20%;")
        pressure_frame.setObjectName("frame_d_pressure")
        #for now this frame is not needed but we might need it in the future so just dont display it
        #self.application_region_3_layout.addWidget(pressure_frame)

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
        self.signal_frame = SignalFrame()
        self.application_region_3_layout.addWidget(self.signal_frame)
        # endregion

        # region : Frame for flask motors
        self.flask_motors_frame = FlaskMotorsFrame()
        self.application_region_3_layout.addWidget(self.flask_motors_frame)
        # endregion
        #endregion
        
        self.application_region.addWidget(self.application_region_3_widget)

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
    
        MainWindow.setCentralWidget(self.centralwidget)
        self.main_content.setStretchFactor(self.application_region, 50)
        self.main_content.setStretchFactor(self.plot_layout, 50)    
    # endregion : Main content 

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
        self.reset_button_style(self.experiment_page_button_lights, border_radius=6)

        # Create the button for routing to the experiment page 
        self.button_dashboard_route  = QtWidgets.QPushButton() 
        buffer = 10  
        self.button_dashboard_route.setGeometry(buffer, buffer, self.frame_e_sidebar.width() - 3 * buffer, int(MainWindow.height() * 0.2))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/icon_dashboard_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_dashboard_route.setIcon(icon)
        self.button_dashboard_route.setIconSize(QtCore.QSize(40, 40))  # Adjust size as needed
        self.reset_button_style(self.button_dashboard_route, border_radius=6)
        
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
        if hasattr(self, 'username') and self.username == "0201":     
            self.application_combobox.addItems(["Mouse Blood", "Human Blood"])  # Add more emails as needed
        else:    
            self.application_combobox.addItems(["POCII", "Ethanol to Sucrose Flush", "CG2 QC", "Autotune", "Demonstration"])  # Add more emails as needed
   
        #endregion

        # region: add choice lockin button 
        self.user_info_lockin_button = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.user_info_lockin_button.setIcon(icon)
        self.user_info_lockin_button.setIconSize(QtCore.QSize(20, 20))  # Adjust size as needed
        self.reset_button_style(self.user_info_lockin_button, border_radius=6)
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

        self.safe_disconnect_frame = CustomExperimentFrame("Safe Disconnect", {
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
        # region : create mouse blood frames
        # endregion : mouse blood frames 
    #endregion  
        # region : experiment activity logger 
        self.frame_activity_logger = QtWidgets.QFrame()
        self.frame_activity_logger.setMinimumHeight(600)  # Sets the minimum height of the frame
        self.frame_activity_logger.setStyleSheet("background-color: #222222; border-radius: 15px;")
        layout_activity_logger = QtWidgets.QHBoxLayout(self.frame_activity_logger)
        self.frame_activity_logger.setLayout(layout_activity_logger)

        v_layout_activity_logger = QtWidgets.QVBoxLayout()
        layout_activity_logger.addLayout(v_layout_activity_logger)

        # Create Title for activiy logger 
        self.label_activity_logger = QLabel("Workflow Logger")
        self.label_activity_logger.setStyleSheet(application_style.main_window_title_style)
        # Create a QTextEdit for logging
        self.WF_activity_log = QTextEdit()
        self.WF_activity_log.setReadOnly(True) 

        v_layout_activity_logger.addWidget(self.label_activity_logger)
        v_layout_activity_logger.addWidget(self.WF_activity_log)
        #endregion

        # region : Add the user info frame to the maincontent layout
        self.experiment_page_main_content.addWidget(self.frame_user_info)
        self.experiment_page_main_content.addSpacing(20)
        #endregion 

        # region : Add white line seperator 
        self.experiment_page_main_content.addWidget(self.line)
        self.experiment_page_main_content.addSpacing(20)
        #endregion

        # region : Add the POCII frames to the main content layout
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
        #endregion

        # region : Add the demo frames to the experiment pages main content layout 
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

        # region : Add WF acitivity logger to experiment page main content layout
        self.experiment_page_main_content.addSpacing(20)
        self.experiment_page_main_content.addWidget(self.frame_activity_logger, alignment=QtCore.Qt.AlignTop)
        self.frame_activity_logger.hide()
        #endregion 
    #endregion
    
#endregion    

    def set_button_style(self, button, font_size=30, border_radius = 10):
        button.setStyleSheet(f"""
            QPushButton {{
                border: 2px solid white;
                border-radius: {border_radius}px;
                background-color: #0796FF;
                color: #FFFFFF;
                font-family: Archivo;
                font-size: {font_size}px;
            }}

            QPushButton:hover {{
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }}
        """)

    def reset_button_style(self, button, font_size=30, border_radius = 10):
        button.setStyleSheet(f"""
            QPushButton {{
                border: 2px solid white;
                border-radius: {border_radius}px;
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

