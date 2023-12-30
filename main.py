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
        self.hop_box.addItems(['1', '2', '3'])
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
        self.ville=self.ville_box.currentText().lower()
        self.ville_box.currentTextChanged.connect(self.actualiser_ville)

        _label=QLabel('Transport: ', self)
        _label.setFixedSize(20,20)
        self.pt_box=QComboBox()
        self.pt_box.addItems(['bus', 'subway', 'tram', 'rail', 'walking'])
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

        
        self.cursor.execute(""f"SELECT DISTINCT name FROM nodes_paris""")
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
            _pt_use='steps_'+_pt_use+'_'+self.ville

            col=self.rows[self.tableWidget.currentRow()]
            for i in range(0,len(col)):
                if (i%2==0):
                    if(col[i].find("'")!=-1):
                        lst=col[i].split("'")
                        arret=lst[0] + "''" + lst[1]
                    else:
                        arret=col[i]

                    self.cursor.execute(""f" WITH tab1(stop_I, lat, lng) AS (SELECT stop_I, lat, lng FROM nodes_{self.ville} WHERE name='{arret}'), tmp (route_I) AS (SELECT route_I FROM route_{self.ville} WHERE route_name='{col[i+j]}') SELECT DISTINCT B.lat, B.lng FROM ({_pt_use} AS A INNER JOIN tab1 AS B ON (A.from_stop_I=B.stop_I)) INNER JOIN tmp AS C ON (A.route_I=C.route_I); """)
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

                    j=-1

        else:
            _pt_use='walk_'+self.ville

            col=self.rows[self.tableWidget.currentRow()]
            for i in range(0,len(col)):
                if (i%2==0):
                    if(col[i].find("'")!=-1):
                        lst=col[i].split("'")
                        arret=lst[0] + "''" + lst[1]
                    else:
                        arret=col[i]

                    self.cursor.execute(""f" WITH tab1(stop_I, lat, lng) AS (SELECT stop_I, lat, lng FROM nodes_{self.ville} WHERE name='{arret}') SELECT DISTINCT B.lat, B.lng FROM ({_pt_use} AS A INNER JOIN tab1 AS B ON (A.from_stop_I=B.stop_I)) """)
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
            _pt_use = 'steps_'+_pt_use+"_"+self.ville

            if _hops >= 1 : 
                self.cursor.execute(""f" WITH ligne (route_I) AS ((SELECT route_I FROM {_pt_use} AS A, nodes_{self.ville} AS B WHERE A.from_stop_I=B.stop_I AND B.name='{_from}') INTERSECT (SELECT route_I FROM {_pt_use} AS A, nodes_{self.ville} AS B WHERE A.to_stop_I=B.stop_I AND B.name='{_to}')) SELECT DISTINCT B.name, F.route_name, D.name FROM {_pt_use} AS A, nodes_{self.ville} AS B, {_pt_use} AS C, nodes_{self.ville} AS D, ligne AS E, route_{self.ville} AS F WHERE B.name='{_from}' AND D.name='{_to}' AND A.route_I=E.route_I AND C.route_I=E.route_I AND A.from_stop_I=B.stop_I AND C.to_stop_I=D.stop_I AND E.route_I=F.route_I; """)
                self.conn.commit()
                self.rows += self.cursor.fetchall()

            if _hops >= 2 : 
                self.cursor.execute(""f"WITH   depart_i AS (SELECT DISTINCT stop_i FROM nodes_{self.ville} WHERE name = '{_from}'), arrivee_i  AS (SELECT DISTINCT stop_i FROM nodes_{self.ville} WHERE name = '{_to}') , stations_from_a (depart,premier_transport, premier_arret) AS (SELECT DISTINCT from_stop_i,route_i, to_stop_i FROM {_pt_use} WHERE from_stop_i in (SELECT stop_i FROM depart_i)), stations_from_b (premier_arret, deuxieme_transport, deuxieme_arret) AS (SELECT DISTINCT from_stop_i,route_i, to_stop_i FROM {_pt_use} WHERE from_stop_i in (SELECT premier_arret FROM stations_from_a) AND to_stop_i in (SELECT stop_i FROM arrivee_i)),trajet_complet AS (SELECT depart,premier_transport, premier_arret, deuxieme_transport, deuxieme_arret  FROM stations_from_a INNER JOIN stations_from_b USING (premier_arret)) SELECT X.name, A.route_name AS premiere_ligne, Y.name, B.route_name AS deuxieme_ligne, Z.name deuxieme_arret FROM trajet_complet,route_{self.ville} AS A, route_{self.ville} AS B, nodes_{self.ville} AS X, nodes_{self.ville} AS Y, nodes_{self.ville} AS Z WHERE A.route_i = premier_transport AND B.route_i = deuxieme_transport AND X.stop_i = depart AND Y.stop_i = premier_arret AND Z.stop_i = deuxieme_arret AND A.route_name <> B.route_name;""")
                self.conn.commit()
                self.rows += self.cursor.fetchall()


            if _hops >= 3 : 
                self.cursor.execute(""f"WITH   depart_i AS (SELECT DISTINCT stop_i FROM nodes_{self.ville} WHERE name = '{_from}'), arrivee_i  AS (SELECT DISTINCT stop_i FROM nodes_{self.ville} WHERE name = '{_to}'), stations_from_a (depart,premier_transport, premier_arret) AS (SELECT DISTINCT from_stop_i,route_i, to_stop_i FROM {_pt_use} WHERE from_stop_i in (SELECT stop_i FROM depart_i)), stations_from_b (premier_arret, deuxieme_transport, deuxieme_arret) AS (SELECT DISTINCT from_stop_i,route_i, to_stop_i FROM {_pt_use} WHERE from_stop_i in (SELECT premier_arret FROM stations_from_a)), stations_from_c (deuxieme_arret, troisieme_transport, troisieme_arret) AS (SELECT DISTINCT from_stop_i,route_i, to_stop_i FROM {_pt_use} WHERE from_stop_i in (SELECT deuxieme_arret FROM stations_from_b) and to_stop_i in (SELECT stop_i  FROM arrivee_i)), trajet_complet AS (SELECT depart,premier_transport, premier_arret, deuxieme_transport, deuxieme_arret, troisieme_transport, troisieme_arret FROM stations_from_a INNER JOIN stations_from_b USING (premier_arret) INNER JOIN stations_from_c USING (deuxieme_arret)) SELECT X.name, A.route_name AS premiere_ligne, Y.name , B.route_name AS deuxieme_ligne, Z.name deuxieme_arret, C.route_name AS troisieme_ligne, F.name FROM trajet_complet, route_{self.ville} AS A, route_{self.ville} AS B, route_{self.ville} AS C, nodes_{self.ville} AS X, nodes_{self.ville} AS Y, nodes_{self.ville} AS Z, nodes_{self.ville} AS F WHERE A.route_i = premier_transport AND   B.route_i = deuxieme_transport AND   C.route_i = troisieme_transport AND X.stop_i = depart AND Y.stop_i = premier_arret AND Z.stop_i = deuxieme_arret AND F.stop_i = troisieme_arret AND A.route_name <> B.route_name AND A.route_name <> C.route_name AND B.route_name <> C.route_name;""")
                self.conn.commit()
                self.rows += self.cursor.fetchall()
        else:
            _pt_use = 'walk_'+self.ville
            self.cursor.execute(""f"WITH table_depart AS  (SELECT DISTINCT stop_i FROM nodes_{self.ville} WHERE name = '{_from}'),     table_arrivee AS ( SELECT DISTINCT stop_i FROM nodes_{self.ville} WHERE name = '{_to}'),     trajet AS ( SELECT DISTINCT d FROM walk_{self.ville} WHERE from_stop_i IN (SELECT * FROM table_depart) AND to_stop_i IN (SELECT * FROM table_arrivee))  SELECT '{_from}', d , '{_to}'from trajet;""")
            self.conn.commit()
            self.rows += self.cursor.fetchall()

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
        self.ville=ville.lower()

        #on met a jour la map
        self.webView.setMap(self.maptype_box.currentIndex(), ville)

        #on met a jour les modes de transport qui peuvent etre utiliser
        if(self.ville=='paris'):
            self.pt_box.clear()
            self.pt_box.addItems(['bus', 'subway', 'tram', 'rail', 'walking'])
        elif(self.ville=='berlin'):
            self.pt_box.clear()
            self.pt_box.addItems(['bus', 'ferry', 'subway', 'tram', 'rail', 'walking'])
        elif(self.ville=='bordeaux'):
            self.pt_box.clear()
            self.pt_box.addItems(['bus', 'ferry', 'tram', 'walking'])
        else:#Toulouse
            self.pt_box.clear()
            self.pt_box.addItems(['bus', 'subway', 'tram','walking'])

        #on met a jour la liste deroulante 'from' et 'to'
        self.cursor.execute(""f"SELECT DISTINCT name FROM nodes_{self.ville}""")
        self.conn.commit()
        rows = self.cursor.fetchall()

        for row in rows : 
            self.from_box.addItem(str(row[0]))
            self.to_box.addItem(str(row[0]))

        self.update()

    def actualiser_pt(self):
        self.pt_use=self.pt_box.currentText()


    def mouseClick(self, lat, lng):
        self.webView.addPointMarker(lat, lng)
        
        if(self.pt_box.currentText() != 'walking'):
            _pt_use="steps_"+self.pt_box.currentText()+"_"+self.ville
        else:
            _pt_use="walk"+"_"+self.ville

        self.cursor.execute(""f"SELECT A.name, (SQRT(POW(({lng}-A.lng), 2) + POW(({lat}-A.lat), 2))) AS dist FROM nodes_{self.ville} AS A, {_pt_use} AS B WHERE A.stop_I=B.from_stop_I OR A.stop_I=B.to_stop_I ORDER BY dist ASC;""")        
        self.conn.commit()
        rows = self.cursor.fetchall()

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
