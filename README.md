# MultiResolutionCameras
This is a minimal Blender add-on written to easily customize resolutions and render your cameras.

After installation, it appears here: `View3D > Sidebar [N] > Render Resolutions`

<img width="315" alt="Screenshot 2023-03-28 at 02 35 47" src="https://user-images.githubusercontent.com/326334/228104087-8b21a2e2-7abe-4366-97d7-7498eb12ed11.png">

## Quick Overview

For each camera row you will find:

1. Checkbox to create a subset of customized cameras.
2. The name of the camera.
3. The wrench is filled when the camera has a custom resolution. Click it to restore default scene resolution.
4. The Render Still button will render the camera to Blender Render window in the current slot.

Below the list you can click to edit or slide to adjust the resolution of the highlighted camera.

There is also two buttons:

* **Selected**: Renders only the currently selected cameras.
* **Renders All**: Yep, you guessed it, renders all cameras in the scene.

Using this button will render in the custom resolution is one is set, othewise default resolution will be used.

Please note that changing the scene resolution will **not** automatically update the cameras with default resolution.

Thanks for checking out my first add-on for Blender. I hope you find it useful!

All the best!\
Johan

# The Future

I have tried multiple approaches to adding a mesh to the selected camera that shows the resolution of the camera, if it has been customized, but so far—all my attempts have been to no avail. The mest just doesn't show up in the 3D Viewport.

If you can help, please get in touch!
