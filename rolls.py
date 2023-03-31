import sys
import datetime
from PySide6 import QtWidgets
from PySide6 import QtCore
import threading
import rollsfuncs

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.init_window()

    def init_window(self):
        self.setWindowTitle("i want a rolls")
        self.resize(800, 400)
        self.search_area = QtWidgets.QLineEdit()
        self.search_area.setPlaceholderText("Enter your search here...")
        self.search_button = QtWidgets.QPushButton("Search")

        search_layout = QtWidgets.QHBoxLayout()
        search_layout.addStretch()
        search_layout.addWidget(self.search_area)
        search_layout.addWidget(self.search_button)
        search_layout.addStretch()
        
        self.search_progress = QtWidgets.QLabel() #searching text that is displayed while search progress is executing
        progress_layout = QtWidgets.QHBoxLayout()
        progress_layout.addStretch()
        progress_layout.addWidget(self.search_progress)
        progress_layout.addStretch()
        progress_layout.addStretch()

        prologue_layout = QtWidgets.QVBoxLayout()
        prologue_layout.addStretch()
        prologue_layout.addLayout(search_layout)
        prologue_layout.addLayout(progress_layout)
        prologue_layout.addStretch()

        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        central.setLayout(prologue_layout)  
              
        self.search_button.clicked.connect(self.progress)
        
        self.show() 
        
    def progress(self):  #display the 'searching' message at the execution time of the search 
        startProgress = threading.Event() #start the thread
        threadEvent = threading.Event()       
        self.progressThread = Progress()
        self.progressThread.startTheProgress(startProgress, threadEvent)
        startProgress.set()
        self.search_progress.setText('searching...')  
        self.progressThread.finished.connect(self.search)     
              
    def search(self):
        car = self.search_area.text()
        self.results = rollsfuncs.car_search(car)
        self.search_area.clear()
        self.search_area.setPlaceholderText("Make another search...")
        self.search_button = QtWidgets.QPushButton("Search")
        time = "%s" % str(datetime.datetime.now())[:-10]
        self.time = QtWidgets.QLabel("time: " + time)
        location = 'Turkey' #set location, in case of future improvements
        self.location = QtWidgets.QLabel("location: " + location)
        
        search_layout = QtWidgets.QHBoxLayout()
        search_layout.addStretch()
        search_layout.addWidget(self.search_area)
        search_layout.addWidget(self.search_button)
        search_layout.addStretch()

        self.search_progress.setText('')
        progress_layout = QtWidgets.QHBoxLayout()
        progress_layout.addStretch()
        progress_layout.addWidget(self.search_progress)
        progress_layout.addStretch()
        progress_layout.addStretch()
        
        if type(self.results) is str: #in case of an exhibition of the error message
            self.last_results = QtWidgets.QLabel(self.results + '\n')
            
            final_layout = QtWidgets.QVBoxLayout()
            final_layout.addLayout(search_layout)
            final_layout.addLayout(progress_layout)
            final_layout.addWidget(self.last_results)
            final_layout.addWidget(self.time)
            final_layout.addWidget(self.location)
            final_layout.addStretch()
            
        else: #for the ordinary results
            result_text = self.results[0]
            dfs = rollsfuncs.result_table(self.results[1], self.results[2], self.results[3], self.results[4], self.results[5], self.results[6], self.results[7], self.results[8], self.results[9])
        
            self.last_results = QtWidgets.QLabel("results for " + "'" + car + "' " + result_text + '\n')        
            self.table = QtWidgets.QTableView()
            self.model = PandasModel(dfs) #display the dataframe in a proper way
            self.table.setModel(self.model)
            #equalize the cell sizes to each other
            hheader = self.table.horizontalHeader()
            hheader.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
            hheader.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
            hheader.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
            hheader.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
            vheader = self.table.verticalHeader()
            vheader.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
            vheader.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
            vheader.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)

            final_layout = QtWidgets.QVBoxLayout()
            final_layout.addLayout(search_layout)
            final_layout.addLayout(progress_layout)
            final_layout.addWidget(self.last_results)
            final_layout.addWidget(self.table)
            final_layout.addWidget(self.time)
            final_layout.addWidget(self.location)
            final_layout.addStretch()

        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        central.setLayout(final_layout)

        self.search_button.clicked.connect(self.progress)
           
class Progress(QtCore.QThread): #the thread
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.exit = False
        self.initSuccessEvent = None
        self.startProgress = None
        
    def stopThread(self):
        self.exit = True
        self.wait()

    def startTheProgress(self, startProgress, initSuccessEvent):
        self.initSuccessEvent = initSuccessEvent
        self.startProgress = startProgress
        self.start()

    def run(self):
        self.startProgress.wait()
        self.initSuccessEvent.set()  
        
class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        QtCore.QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)
        if role == QtCore.Qt.TextAlignmentRole:
            value = self._data.iloc[index.row(), index.column()]
            return QtCore.Qt.AlignVCenter + QtCore.Qt.AlignRight

    def headerData(self, section, orientation, role):
        #section is the index of the column/row
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == QtCore.Qt.Vertical:
                return str(self._data.index[section])

app = QtWidgets.QApplication(sys.argv)
window = Window()
sys.exit(app.exec())

#i want a rolls by lapin
#12.02.2023
