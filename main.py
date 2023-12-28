import folium, io, json, sys, math, random, os
import psycopg2
from folium.plugins import Draw, MousePosition, MeasureControl
from jinja2 import Template
from branca.element import Element
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets

villedf='Paris' #ville par defaut

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.resize(700, 700)
	
        main = QWidget()
        self.setCentralWidget(main)
        main.setLayout(QVBoxLayout())
        main.setFocusPolicy(Qt.StrongFocus)

        self.tableWidget = QTableWidget()
        self.tableWidget.doubleClicked.connect(self.table_Click)
        self.rows = []

        self.webView = myWebView()
		
        controls_panel = QHBoxLayout()
        mysplit = QSplitter(Qt.Vertical)
        mysplit.addWidget(self.tableWidget)
        mysplit.addWidget(self.webView)

        main.layout().addLayout(controls_panel)
        main.layout().addWidget(mysplit)

        _label = QLabel('From: ', self)
        _label.setFixedSize(20,10)
        self.from_box = QComboBox() 
        self.from_box.setEditable(True)
        self.from_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.from_box.setInsertPolicy(QComboBox.NoInsert)
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.from_box)

        _label = QLabel('To: ', self)
        _label.setFixedSize(20,10)
        self.to_box = QComboBox() 
        self.to_box.setEditable(True)
        self.to_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.to_box.setInsertPolicy(QComboBox.NoInsert)
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.to_box)

        _label = QLabel('Hops: ', self)
        _label.setFixedSize(20,20)
        self.hop_box = QComboBox() 
        self.hop_box.addItems( ['1', '2', '3'] )
        self.hop_box.setCurrentIndex( 0 )
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.hop_box)

        _label=QLabel('Ville: ', self)
        _label.setFixedSize(20,20)
        self.ville_box=QComboBox()
        self.ville_box.addItems(['Paris', 'Berlin', 'Toulouse', 'Bordeaux'])
        self.ville_box.setCurrentIndex(0)
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.ville_box)
        self.ville_box.currentTextChanged.connect(self.actualiser_ville)

        _label=QLabel('Transport: ', self)
        _label.setFixedSize(20,20)
        self.pt_box=QComboBox()
        self.pt_box.addItems( ['bus', 'subway', 'tram', 'rail', 'walking'] )
        self.pt_box.setCurrentIndex(0)
        self.pt_use=self.pt_box.currentText()
        self.pt_box.currentTextChanged.connect(self.actualiser_pt)
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.pt_box)

        self.go_button = QPushButton("Go!")
        self.go_button.clicked.connect(self.button_Go)
        controls_panel.addWidget(self.go_button)
           
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.button_Clear)
        controls_panel.addWidget(self.clear_button)

        self.maptype_box = QComboBox()
        self.maptype_box.addItems(self.webView.maptypes)
        self.maptype_box.currentIndexChanged.connect(self.webView.setMap)
        controls_panel.addWidget(self.maptype_box)
           
        self.connect_DB()

        self.startingpoint = True
                   
        self.show()        

    def connect_DB(self):
        self.conn = psycopg2.connect(database="BDD-db", user="Jibril", host="localhost", password="MG5scp15")
        self.cursor = self.conn.cursor()

        
        self.cursor.execute(""f"SELECT DISTINCT name FROM nodes""")
        self.conn.commit()
        rows = self.cursor.fetchall()

        for row in rows : 
            self.from_box.addItem(str(row[0]))
            self.to_box.addItem(str(row[0]))


    def table_Click(self):
        plat=0
        plng=0
        j=1
        _pt_use=self.pt_use
        if(_pt_use!='walking'):
            _pt_use='steps_'+_pt_use

            col=self.rows[self.tableWidget.currentRow()]
            for i in range(0,len(col)):
                if (i%2==0):
                    self.cursor.execute(""f" WITH tab1(stop_I, lat, lng) AS (SELECT stop_I, lat, lng FROM nodes WHERE name='{col[i]}'), tmp (route_I) AS (SELECT route_I FROM route WHERE route_name='{col[i+j]}') SELECT DISTINCT B.lat, B.lng FROM ({_pt_use} AS A INNER JOIN tab1 AS B ON (A.from_stop_I=B.stop_I)) INNER JOIN tmp AS C ON (A.route_I=C.route_I); """)
                    self.conn.commit()
                    coordonne=self.cursor.fetchall() 
                    #coordonne[0][0]=lat, coordonne[1][0]=lng c'est coordonne[i][j]
                    #car les requetes sont stockés sous la forme de matrice et si
                    #il y a plusieurs coordonne on prend celle qui est en coordonne[0]

                    if plat != 0:
                        self.webView.addSegment(plat, plng, coordonne[0][0], coordonne[0][1])
                    plat = coordonne[0][0]
                    plng = coordonne[0][1]

                    self.webView.addMarker(coordonne[0][0], coordonne[0][1])

                    if(j==-1):
                        j=1
                    else:
                        j=-1

            i+=1
        

    def button_Go(self):
        self.tableWidget.clearContents()

        _from = str(self.from_box.currentText())
        _to = str(self.to_box.currentText())
        _hops = int(self.hop_box.currentText())
        _pt_use = self.pt_use

        #verifie si _from ou _to contienent "'" 
        if(_from.find("'")!=-1):
            lst=_from.split("'")
            _from=lst[0] + "''" + lst[1]
        if(_to.find("'")!=-1):
            lst=_to.split("'")
            _to=lst[0] + "''" + lst[1]            

        self.rows = []

        if(_pt_use != 'walking'):
            _pt_use = 'steps_'+_pt_use

            if _hops >= 1 : 
                self.cursor.execute(""f" WITH ligne (route_I) AS ((SELECT route_I FROM {_pt_use} AS A, nodes WHERE A.from_stop_I=nodes.stop_I AND nodes.name='{_from}') INTERSECT (SELECT route_I FROM {_pt_use}, nodes WHERE {_pt_use}.to_stop_I=nodes.stop_I AND nodes.name='{_to}')) SELECT DISTINCT B.name, F.route_name, D.name FROM {_pt_use} AS A, nodes AS B, {_pt_use} AS C, nodes AS D, ligne AS E, route AS F WHERE B.name='{_from}' AND D.name='{_to}' AND A.route_I=E.route_I AND C.route_I=E.route_I AND A.from_stop_I=B.stop_I AND C.to_stop_I=D.stop_I AND E.route_I=F.route_I; """)
                self.conn.commit()
                self.rows += self.cursor.fetchall()

            #if _hops >= 2 : 
                #self.cursor.execute(""f" SELECT distinct A.geo_point_2d, A.nom_long, A.res_com, B.geo_point_2d, B.nom_long, C.res_com, D.geo_point_2d, D.nom_long FROM metros as A, metros as B, metros as C, metros as D WHERE A.nom_long = $${_from}$$ AND D.nom_long = $${_to}$$ AND A.res_com = B.res_com AND B.nom_long = C.nom_long AND C.res_com = D.res_com AND A.res_com <> C.res_com AND A.nom_long <> B.nom_long AND B.nom_long <> D.nom_long""")
                #self.conn.commit()
                #self.rows += self.cursor.fetchall()

            #if _hops >= 3 : 
                #self.cursor.execute(""f" SELECT distinct A.geo_point_2d, A.nom_long, A.res_com, B2.geo_point_2d, B2.nom_long, B2.res_com, C2.geo_point_2d, C2.nom_long, C2.res_com, D.geo_point_2d, D.nom_long FROM metros as A, metros as B1, metros as B2, metros as C1, metros as C2, metros as D WHERE A.nom_long = $${_from}$$ AND A.res_com = B1.res_com AND B1.nom_long = B2.nom_long AND B2.res_com = C1.res_com AND C1.nom_long = C2.nom_long AND C2.res_com = D.res_com AND D.nom_long = $${_to}$$ AND A.res_com <> B2.res_com AND B2.res_com <> C2.res_com AND A.res_com <> C2.res_com AND A.nom_long <> B1.nom_long AND B2.nom_long <> C1.nom_long AND C2.nom_long <> D.nom_long""")
                #self.conn.commit()
                #self.rows += self.cursor.fetchall()

        if len(self.rows) == 0 : 
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            return

        self.tableWidget.setRowCount(len(self.rows))
        self.tableWidget.setColumnCount(len(self.rows[-1]))

        i=0
        for row in self.rows : 
            j=0
            for col in row :
                self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(col)))
                j+=1
            i+=1

        header = self.tableWidget.horizontalHeader()
        i = 0
        while i < len(self.rows[-1]): 
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            i+=1
        
        self.update()	


    def button_Clear(self):
        self.webView.clearMap(self.maptype_box.currentIndex(), self.ville_box.currentText())
        self.startingpoint = True
        self.update()


    def actualiser_ville(self):
        ville=str(self.ville_box.currentText())
        self.webView.setMap(self.maptype_box.currentIndex(), ville)
        self.update()

    def actualiser_pt(self):
        self.pt_use=self.pt_box.currentText()


    def mouseClick(self, lat, lng):
        self.webView.addPointMarker(lat, lng)
        
        _pt_use="steps_"+self.pt_box.currentText()

        print(f"Clicked on: latitude {lat}, longitude {lng}")
        self.cursor.execute(""f"SELECT name, (SQRT(POW(ABS({lng}-nodes.lng), 2) + POW(ABS({lat}-nodes.lat), 2))) AS dist FROM nodes, {_pt_use} WHERE nodes.stop_I={_pt_use}.from_stop_I OR nodes.stop_I={_pt_use}.to_stop_I ORDER BY dist ASC;""")        
        self.conn.commit()
        rows = self.cursor.fetchall()
        print(rows[0][0])
        if self.startingpoint :
            self.from_box.setCurrentIndex(self.from_box.findText(rows[0][0], Qt.MatchFixedString))
            self.startingpoint=False
        else :
            self.to_box.setCurrentIndex(self.to_box.findText(rows[0][0], Qt.MatchFixedString))
            self.startingpoint = True



class myWebView (QWebEngineView):
    def __init__(self):
        super().__init__()

        self.maptypes = ["OpenStreetMap"]
        self.setMap(0, villedf)


    def add_customjs(self, map_object):
        my_js = f"""{map_object.get_name()}.on("click",
                 function (e) {{
                    var data = `{{"coordinates": ${{JSON.stringify(e.latlng)}}}}`;
                    console.log(data)}}); """
        e = Element(my_js)
        html = map_object.get_root()
        html.script.get_root().render()
        html.script._children[e.get_name()] = e

        return map_object


    def handleClick(self, msg):
        data = json.loads(msg)
        lat = data['coordinates']['lat']
        lng = data['coordinates']['lng']


        window.mouseClick(lat, lng)


    def addSegment(self, lat1, lng1, lat2, lng2):
        js = Template(
        """
        L.polyline(
            [ [{{latitude1}}, {{longitude1}}], [{{latitude2}}, {{longitude2}}] ], {
                "color": "red",
                "opacity": 1.0,
                "weight": 4,
                "line_cap": "butt"
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude1=lat1, longitude1=lng1, latitude2=lat2, longitude2=lng2 )

        self.page().runJavaScript(js)


    def addMarker(self, lat, lng):
        js = Template(
        """
        L.marker([{{latitude}}, {{longitude}}] ).addTo({{map}});
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": "#3388ff",
                "popup": "hello",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": "#3388ff",
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2,
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude=lat, longitude=lng)
        self.page().runJavaScript(js)


    def addPointMarker(self, lat, lng):
        js = Template(
        """
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": 'green',
                "popup": "hello",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": 'green',
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2,
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude=lat, longitude=lng)
        self.page().runJavaScript(js)


    def setMap (self, i, ville):
        #[lat, lng]
        if(ville=='Paris'):
            self.mymap = folium.Map(location=[48.8619, 2.3519], tiles=self.maptypes[i], zoom_start=12, prefer_canvas=True)
        if(ville=='Berlin'):
            self.mymap = folium.Map(location=[52.520320, 13.413682], tiles=self.maptypes[i], zoom_start=12, prefer_canvas=True)
        if(ville=='Toulouse'):
            self.mymap = folium.Map(location=[43.605410, 1.443672], tiles=self.maptypes[i], zoom_start=12, prefer_canvas=True)
        if(ville=='Bordeaux'):
            self.mymap = folium.Map(location=[44.842027, -0.577090], tiles=self.maptypes[i], zoom_start=12, prefer_canvas=True)
        
        self.mymap = self.add_customjs(self.mymap)

        page = WebEnginePage(self)
        self.setPage(page)

        data = io.BytesIO()
        self.mymap.save(data, close_file=False)

        self.setHtml(data.getvalue().decode())

    def clearMap(self, index, ville):
        self.setMap(index, ville)
        self.update()



class WebEnginePage(QWebEnginePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        #print(msg)
        if 'coordinates' in msg:
            self.parent.handleClick(msg)


       
			
if __name__ == '__main__':
    sys.argv.append('--no-sandbox')
    app = QApplication(sys.argv) 
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
