# Pose annotator
A simple GUI for clicking on keypoints for training pose estimation models. Currently only supports one set of 
points per frame. Please consider contributing for multiple instances per frame!

## Installation
* pip install pose-annotator

## Usage
Customize [default_config.yaml](pose_annotator/gui/default_config.yaml) then launch using
 `pose_annotator usr_cfg=path/to/custom/config.yaml` 
 
#### Hotkeys 
* `Ctrl+S` save
* `Right` next frame
* `Left` previous frame
* `Down` next keypoint
* `Space` next keypoint
* `Up` previous keypoint
* `Delete` delete keypoint

 

## Known issues
* Adding or deleting images from a directory with existing annotations
	* annotations are matched to image files by rank-order of the filename
* `ModuleNotFoundError: No module named 'skbuild'`
  * please `pip install --upgrade pip`

## TODO
* Make player resize image appropriately on startup
  * current behavior: changing frame resizes images to fit in view; does not expand size on image resize
* support removing keypoints
* support multiple animals / people per image
* add action queue + undo button