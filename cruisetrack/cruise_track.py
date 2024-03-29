# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CruiseTrackExport
                                 A QGIS plugin
 Export waypoints for cruise track.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-04-01
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Gianna Persichini and Markus Benninghoff
        email                : gimap@mail.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog  # added
from qgis.core import QgsProject  # added
import pickle
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .cruise_track_dialog import CruiseTrackExportDialog
import os.path
import numpy as np


class CruiseTrackExport:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CruiseTrackExport_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Cruise Track Export')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CruiseTrackExport', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/cruise_track/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Cruise Track Export'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&Cruise Track Export'), action)
            self.iface.removeToolBarIcon(action)

    def select_output_file(self):  # added

        filename, _filter = QFileDialog.getSaveFileName(self.dlg, "Select   output file ", "")
        if self.dlg.rt3_button.isChecked():
            filename = filename + '.rt3'
        elif self.dlg.rtz_button.isChecked():
            filename = filename + '.rtz'
        elif self.dlg.cvt_button.isChecked():
            filename = filename + '.cvt'
        else:
            filename = filename + '.cvt'

        self.dlg.le_outTrack.setText(filename)

    def run(self):
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start:
            self.first_start = False
            self.dlg = CruiseTrackExportDialog()
            self.dlg.tb_outTrack.clicked.connect(self.select_output_file)

        layers = QgsProject.instance().layerTreeRoot().children()  # Fetch the currently loaded layers
        self.dlg.cb_inVector.clear()  # Clear the contents of the comboBox from previous runs
        self.dlg.cb_inVector.addItems(
            [layer.name() for layer in layers])  # Populate the comboBox with names of all the loaded layers

        self.dlg.show()  # show the dialog
        result = self.dlg.exec_()  # Run the dialog event loop
        if result:  # PyQgis start

            is_individual_trackline = self.dlg.individualtrackline.isChecked()
            is_parallel_lines = self.dlg.parallel_lines.isChecked()
            is_mult_para_lines = self.dlg.mult_para_lines.isChecked()
            is_nonebt = self.dlg.noneBt.isChecked()
            is_normal_profile = self.dlg.normalProfiles.isChecked()
            flip_we = self.dlg.checkBox_flipWE.isChecked()
            flip_ns = self.dlg.checkBox_flipNS.isChecked()
            selected_layer_index = self.dlg.cb_inVector.currentIndex()
            only_process_2nds = self.dlg.every2nd.isChecked()
            is_littorina = self.dlg.Littorina.isChecked()

            export_to_rt3 = self.dlg.rt3_button.isChecked()
            export_to_rtz = self.dlg.rtz_button.isChecked()
            export_to_csv = self.dlg.cvt_button.isChecked()
            filename_out = self.dlg.le_outTrack.text()

            import os
            from qgis.core import QgsWkbTypes

            from cruisetrack.fileops.rt3_export import rt3_export

            from cruisetrack.fileops.rtz_export import rtz_export

            from cruisetrack.fileops.csv_export import csv_export

            # Identify selected layer by its index
            ly_tree_nd = layers[selected_layer_index]
            laye_r = ly_tree_nd.layer()  # Gives you the layer you have selected in the Layers Panel
            layer_provider = laye_r.dataProvider()

            # what input layer
            for fea_t in laye_r.getFeatures():
                geom = fea_t.geometry()

            if geom.type() == QgsWkbTypes.LineGeometry:
                from cruisetrack.process.workflow_lines import lines_workflow
                lon, lat = lines_workflow(layer_provider=layer_provider,
                                          laye_r=laye_r,
                                          is_individual_trackline=is_individual_trackline,
                                          is_parallel_lines=is_parallel_lines,
                                          is_mult_para_lines=is_mult_para_lines,
                                          is_nonebt=is_nonebt,
                                          is_normal_profile=is_normal_profile,
                                          flip_we=flip_we,
                                          only_process_2nds=only_process_2nds,
                                          is_littorina=is_littorina,
                                          flip_ns=flip_ns)

            elif geom.type() == QgsWkbTypes.PointGeometry:
                from cruisetrack.process.workflow_points import point_workflow
                lon, lat = point_workflow(laye_r=laye_r, flip_ns=flip_ns, flip_we=flip_we)


            # export text file for transas
            if export_to_rt3:
                rt3_export(lon, lat, filename=filename_out)  # RT3 file export
            elif export_to_rtz:
                rtz_export(lon, lat, filename=filename_out)  # RTZ file export
            elif export_to_csv:
                csv_export(lon, lat, filename=filename_out)  # CSV file export
            else:
                csv_export(lon, lat, filename=filename_out)
