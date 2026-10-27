"""Record actual MuJoCo stepping through EGL; no pose replay or synthetic motion."""
import os
os.environ.setdefault('MUJOCO_GL', 'egl')
os.environ.setdefault('MPLCONFIGDIR', '/workspace/.cache/group06-matplotlib')
from pathlib import Path
import argparse
import json
import subprocess
import mujoco
from PIL import Image, ImageDraw, ImageFont
from crawler_cleaning_controller import mission


def record(directory, speedup=8):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    width, height, fps = 960, 720, 25
    period = speedup / fps
    renderer = None
    encoder = None
    last_time = -period
    frames = 0
    font_path = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    font = ImageFont.truetype(str(font_path), 19) if font_path.exists() else ImageFont.load_default()
    first_frame = True
    log = (directory / 'ffmpeg.log').open('w')

    def capture(m, d, state, coverage_map):
        nonlocal renderer, encoder, last_time, frames, first_frame
        if d.time + 1e-9 < last_time + period:
            return
        last_time = float(d.time)
        coverage = coverage_map.summary()
        if renderer is None:
            m.vis.global_.offwidth = width
            m.vis.global_.offheight = height
            renderer = mujoco.Renderer(m, height=height, width=width)
            encoder = subprocess.Popen([
                'ffmpeg', '-hide_banner', '-loglevel', 'warning', '-n',
                '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{width}x{height}',
                '-r', str(fps), '-i', '-', '-an', '-c:v', 'libx264',
                '-preset', 'fast', '-crf', '22', '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart', str(directory / 'mujoco_demo.mp4')
            ], stdin=subprocess.PIPE, stderr=log)
        camera = mujoco.MjvCamera()
        mujoco.mjv_defaultCamera(camera)
        camera.lookat[:] = [0, 0, 1.2]
        camera.distance = 7.6
        camera.azimuth = 90
        camera.elevation = -65
        renderer.update_scene(d, camera=camera)
        picture = Image.fromarray(renderer.render())
        draw = ImageDraw.Draw(picture)
        draw.rectangle((0, 0, width, 100), fill=(15, 20, 30))
        draw.text((15, 8), f'Actual MuJoCo simulation | {speedup:g}x playback | sim t={d.time:.2f}s | {state}', font=font, fill='white')
        draw.text((15, 38), f'Whole-panel qualifying footprint: {coverage["qualified_contact_fraction"]:.1%}', font=font, fill='white')
        draw.text((15, 68), 'Rollers approximate tracks; ground-truth feedback; cleaning is an uncalibrated proxy', font=font, fill='white')
        if first_frame:
            picture.save(directory / 'preview.png')
            first_frame = False
        encoder.stdin.write(picture.tobytes())
        frames += 1

    try:
        result = mission(seed=0, duration=420, layout='expanded_safe_return',
                         output=directory / 'telemetry.csv.gz', on_sample=capture)
    finally:
        if renderer is not None:
            renderer.close()
        if encoder is not None:
            encoder.stdin.close()
            code = encoder.wait()
            if code:
                raise RuntimeError(f'ffmpeg failed ({code}); inspect {directory / "ffmpeg.log"}')
        log.close()
    if frames < 2:
        raise RuntimeError('No useful video frames captured')
    metadata = {'renderer': 'MuJoCo EGL', 'playback_speedup': speedup, 'fps': fps,
                'frames': frames, 'video_duration_s': frames/fps,
                'source': 'Fresh physical simulation, observed before each sampled mj_step; no state replay',
                'status': result['status'], 'simulation_duration_s': result['time_s'],
                'limitations': 'Not interactive viewer verification, not a team submission video, not calibrated cleaning or hardware evidence'}
    (directory / 'video_metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    return metadata


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(record(args.output_dir), indent=2))
