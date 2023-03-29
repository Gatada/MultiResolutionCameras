# Multi-Resolution Cameras for Blender
This is a Blender add-on written to easily customize render resolutions, and render your cameras. With the add-on you can:

* Set a custom render resolution for the cameras in the scene, without impacting the scene rendering resolution/aspect.
* Easily render a still for a camera with the custom resolution.

But what makes the add-on cool is that you can preview the render right there in the viewport, as a frame is added to the camera which updates in real-time while you adjust the size and ratio of the render.

It is a single file add-on. After installation, it appears here: `View3D > Sidebar [N] > Render Resolutions`


![Feature Overview](https://user-images.githubusercontent.com/326334/228676238-09964662-3a0f-4cdf-ab00-4d49347428d7.png)


![Custom Camera Resolution](https://user-images.githubusercontent.com/326334/228645249-619cb3b0-3934-496a-b817-aeb84345221b.png)


## Installation

To install this add-on please follow these steps:

1. Download.
1. Open Blender Preferences (CMD+comma on MacOS).
1. Go to the **Add-ons** tab and click `Install`.
1. Browse to the downloaded python script and select it.
1. Enable the script, it is called: `3D View: Multi-Resolution Cameras`.


## Quick Overview

The add-on panel presents a scrollable list, two integer fields with undo buttons, and two render buttons.

For each camera row you will find:

1. Checkbox to create a subset of cameras.
2. The name of the camera.
3. The wrench is filled when the camera has a custom resolution. Click it to restore default scene resolution.
4. The Render Still button will render the camera to `Blender Render` window in the current slot.
5. The Scene Camera: click it to make the camera the Scene Camera, allowing you to adjust the rendered image dimensions in real-time. This is the killer feature. Very happy I managed to add this exactly as I wanted it to work.

Below the list you can click to edit or slide to adjust the resolution of the highlighted camera.

There is also two buttons:

* **Selected**: Renders only the current subset of selected cameras.
* **Renders All**: Yep, you guessed it, this button renders all cameras in the scene.

Using this button will render in the custom resolution is one is set, othewise default resolution will be used.

Please note that changing the scene resolution will **not** automatically update the cameras with default resolution. Tap the wrench of the cameras that you want to update after a scene resolution change.

## How It Works

The plugin appends a property group (a data struct) to your file for each camera. The property group contains the name of the camera, index; X and Y dimensions, as well as the state of the checkbox. In other words, your file size will not be notably affected by the additional data.

When you save the file, the data is retained—even if you uninstall the add-on. The data becomes part of the file. So you can share the file with others, and as long as they have the add-on installed, they will be able to render the different camera sizes.

Thanks for checking out my first add-on for Blender. It took an entire week to make, and it turned into everything I wanted it to be. I'm very happy about it.

I hope you find it useful!

All the best!\
Johan

# The Future

I have tried multiple approaches to adding a mesh to the selected camera that shows the resolution of the camera, if it has been customized, but so far—all my attempts have been to no avail. The mest just doesn't show up in the 3D Viewport.

If you can help, please get in touch!
