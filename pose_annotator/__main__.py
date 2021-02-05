import os
import sys

from omegaconf import OmegaConf
from PySide2 import QtCore, QtWidgets, QtGui

from pose_annotator.gui.main import set_style, MainWindow


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app = set_style(app)
    
    default_path = os.path.join(os.path.dirname(__file__), 'gui', 'default_config.yaml')
    
    default = OmegaConf.load(default_path)
    cli = OmegaConf.from_cli()
    cfg = OmegaConf.merge(default, cli)
    OmegaConf.set_struct(cfg, True)

    window = MainWindow(cfg)
    window.resize(1024, 768)
    window.show()

    sys.exit(app.exec_())