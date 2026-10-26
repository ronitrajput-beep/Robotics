# Run on a MacBook

Use macOS Terminal. The same commands work with Intel and Apple Silicon Homebrew installations. Install Homebrew from https://brew.sh first if `brew` is not available.

## 1. Install Python and the video encoder

```sh
brew install python@3.12 ffmpeg
```

## 2. Download the compact project

The full repository contains gigabytes of raw experimental logs. The compact ZIP includes the code, models, required small test fixtures and finished videos.

```sh
mkdir -p ~/Robotics-Mac
cd ~/Robotics-Mac
curl -L 'https://github.com/ronitrajput-beep/Robotics/blob/feat/e052-waterless-rotary-bru/Group_06_Arush_Ronit_Harshvardhan/submission/Group06_Submission_Bundle.zip?raw=true' -o group06.zip
unzip -q group06.zip
cd Group_06_Arush_Ronit_Harshvardhan
```

Use a fresh destination if you already have edited local files; do not overwrite your own work when unzipping.

## 3. Create a local Python environment

```sh
"$(brew --prefix python@3.12)/bin/python3.12" -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-macos.txt
export MUJOCO_GL=cgl
python src/test_env.py
```

This environment belongs on your Mac. Cloud paths such as `/workspace/venvs/group06` do not exist locally. Mac packages resolve compatible wheels; the separately pinned `requirements.txt` records the exact Linux statistical-validation environment. Mac execution has not been hardware-tested here, and bitwise identical cross-platform results are not assumed.

## 4. Run the autonomous mission in a live window

```sh
MUJOCO_GL=cgl mjpython src/run_live.py
```

This launches the real camera/controller pipeline with rooftop scenery, visible dust, fixed brush, dock and tray in an interactive MuJoCo window. The robot waits at home for the actual RGB trigger (about four simulated seconds in the default combined scene), then moves. Mouse drag/scroll rotates/zooms. P pauses/resumes the mission; closing the window stops it. The native viewer's Space/Run controls do not govern this external controller, so use P. Terminal reports mission states and actual camera target counts. Raw RGB observations and telemetry are saved to a new timestamped `analytics/live_*` directory.

A complete nominal cycle is about ten simulated minutes. `mjpython src/run_live.py --speed 2` targets twice real-time without changing the physics timestep. The cinematic recording below retains its separate camera movements and RGB-feed sidebar; the live window has a freely controlled camera.

If the project was downloaded before the live launcher was added, close the old model-only window and install this small source-only update from the activated project directory:

```sh
cp -R src "src_before_live_$(date +%Y%m%d_%H%M%S)"
curl -fL 'https://github.com/ronitrajput-beep/Robotics/blob/feat/e052-waterless-rotary-bru/Group_06_Arush_Ronit_Harshvardhan/submission/Group06_Live_Viewer_Update.zip?raw=true' -o live_update.zip
unzip -o live_update.zip
MUJOCO_GL=cgl mjpython src/run_live.py
```

The update replaces four source files and leaves your documents, virtual environment, models and previous results intact. A backup of your existing source folder is made first.

## Record a fresh combined simulation as an MP4

```sh
GROUP06_RUN="analytics/mac_demo_$(date +%Y%m%d_%H%M%S)"
python src/vision_mission.py --scenario combined --cinematic --duration 1000 --output-dir "$GROUP06_RUN"
open "$GROUP06_RUN/cinematic_cleaning.mp4"
```

This runs fresh physics, camera detection, dust cleaning, solid-object pushing, return and dock service. It renders the rooftop scene, visible cameras, close-ups and actual camera feeds into an MP4. Wait for Python to finish before opening the movie. `1000` is a maximum simulated-time horizon in seconds, not the movie length or a wall-clock estimate. Rendering takes time depending on the Mac. Use a new output directory for every run; existing evidence is never overwritten.

The recording command creates an MP4. The live command above opens the integrated mission window. Both use the actual RGB trigger and controller. macOS passive viewer scripts use `mjpython`; the MP4 command uses ordinary `python`.

## Open the interactive robot-model window

From the group directory with `.venv` activated:

```sh
MUJOCO_GL=glfw python -m mujoco.viewer --mjcf=models/collection_cleaning_crawler.xml
```

Use ordinary `python` for this standalone viewer. `mjpython` is required for scripts using `viewer.launch_passive` on macOS; it is not the launcher for the standalone command above. Launching `mjpython -m mujoco.viewer` can import the viewer twice and start the managed window on the wrong thread, with an "already in sys.modules" warning followed by `RuntimeError: Caught an unknown exception!` during `_Simulate` construction. The inline GLFW setting applies only to this command and leaves the CGL recording setting intact.

Drag to rotate, scroll to zoom and press Space to pause/resume physics. This opens the model; it does not run the autonomous mission controller. The official mode distinctions and standalone command are documented at https://mujoco.readthedocs.io/en/stable/python.html#interactive-viewer.

## Watch the already finished videos immediately

```sh
open docs/validation/collection_demo_v6/cinematic_cleaning.mp4
open docs/validation/panel_camera_rig_v4/panel_camera_tour.mp4
```

The first is the full validated cleaning cycle; the second is the short camera-equipment tour.

## Later terminal sessions

```sh
cd ~/Robotics-Mac/Group_06_Arush_Ronit_Harshvardhan
source .venv/bin/activate
export MUJOCO_GL=cgl
```

Then run the fresh-simulation block again. Do not set `MUJOCO_GL=egl` on a Mac: EGL is the Linux headless backend.
