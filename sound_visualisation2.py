#!/usr/bin/env python3
import numpy as np
import math
import argparse
import os
import subprocess
from pydub import AudioSegment
from PIL import Image, ImageDraw

def analyze_audio_fft(file_path, target_fps=30):
    """
    Analyze audio and extract FFT data.
    """
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_frame_rate(44100)
    
    # Get left channel
    if audio.channels == 2:
        left_channel = audio.split_to_mono()[0]
    else:
        left_channel = audio.set_channels(1)
    
    # Convert to numpy array
    left_data = np.frombuffer(left_channel.raw_data, dtype=np.int16).astype(np.float32) / 32768.0
    right_data = left_data.copy()
    
    frame_duration = 1.0 / target_fps
    samples_per_frame = int(44100 * frame_duration)
    n_frames = len(left_data) // samples_per_frame
    
    # FFT size
    fft_size = 1024
    n_freq_bands = 30
    
    left_fft_data = []
    right_fft_data = []
    
    for i in range(n_frames):
        start = i * samples_per_frame
        end = start + fft_size
        
        if end > len(left_data):
            left_frame = np.pad(left_data[start:], (0, end - len(left_data)), 'constant')
            right_frame = np.pad(right_data[start:], (0, end - len(right_data)), 'constant')
        else:
            left_frame = left_data[start:end]
            right_frame = right_data[start:end]
        
        # Perform FFT
        left_fft = np.fft.rfft(left_frame)
        right_fft = np.fft.rfft(right_frame)
        
        # Get magnitude
        left_magnitude = np.abs(left_fft)
        right_magnitude = np.abs(right_fft)
        
        # Create logarithmic frequency bands
        left_bands = []
        right_bands = []
        
        for band in range(n_freq_bands):
            freq_low = int(22 * (2 ** (band / 3.0)))
            freq_high = int(22 * (2 ** ((band + 1) / 3.0)))
            
            bin_low = int(freq_low * len(left_magnitude) / (44100 / 2))
            bin_high = int(freq_high * len(left_magnitude) / (44100 / 2))
            bin_low = max(0, min(bin_low, len(left_magnitude) - 1))
            bin_high = max(bin_low + 1, min(bin_high, len(left_magnitude)))
            
            left_avg = np.mean(left_magnitude[bin_low:bin_high])
            right_avg = np.mean(right_magnitude[bin_low:bin_high])
            
            left_bands.append(left_avg)
            right_bands.append(right_avg)
        
        left_fft_data.append(left_bands)
        right_fft_data.append(right_bands)
    
    return {
        'left_fft': np.array(left_fft_data),
        'right_fft': np.array(right_fft_data),
        'n_frames': n_frames,
        'n_bands': n_freq_bands
    }

def draw_frequency_waveform(draw, width, height, fft_data):
    """
    Draw a subtle circular waveform in the center showing frequency spectrum.
    """
    center_x = width // 2
    center_y = height // 2
    
    # Number of points around the circle
    n_points = len(fft_data)
    
    if n_points < 2:
        return
    
    # Base radius for the waveform circle
    base_radius = 30
    
    # Draw the circular waveform
    points = []
    for i in range(n_points):
        angle = (i / n_points) * 2 * math.pi
        # Add frequency amplitude to radius
        amplitude = fft_data[i] * 10  # Subtle amplitude
        radius = base_radius + amplitude
        
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))
    
    # Draw lines connecting the points to form the circular wave
    for i in range(len(points)):
        start = points[i]
        end = points[(i + 1) % len(points)]
        draw.line([start, end], fill=(100, 100, 100), width=1)

def draw_frame(draw, width, height, left_fft, right_fft, n_bands):
    """
    Original Processing visualization.
    """
    center_x, center_y = width // 2, height // 2
    
    # Draw the main frequency bars (original Processing style)
    total_rectangles = n_bands * 2
    
    for i in range(1, total_rectangles + 1):
        if i % 2 == 1:
            # Left channel - Red/Orange
            band_index = i // 2
            value = left_fft[band_index] if band_index < n_bands else 0
            color = (255, 50, 20)
            angle = i * 0.05
        else:
            # Right channel - Blue
            band_index = i // 2 - 1
            value = right_fft[band_index] if band_index < n_bands else 0
            color = (20, 100, 250)
            angle = -i * 0.05
        
        # Rectangle dimensions
        rect_x = value * 5
        rect_y = -5
        rect_width = value * 4
        rect_height = 10
        
        corners = [
            (rect_x, rect_y),
            (rect_x + rect_width, rect_y),
            (rect_x + rect_width, rect_y + rect_height),
            (rect_x, rect_y + rect_height)
        ]
        
        # Apply transforms: translate(50,0), rotate(angle), translate(center)
        rotated_corners = []
        for x, y in corners:
            tx = x + 50
            ty = y
            rx = tx * math.cos(angle) - ty * math.sin(angle)
            ry = tx * math.sin(angle) + ty * math.cos(angle)
            final_x = center_x + rx
            final_y = center_y + ry
            rotated_corners.append((final_x, final_y))
        
        draw.polygon(rotated_corners, fill=color)

def create_visualization(fft_data, output_path, width=600, height=600, fps=30):
    """Create visualization by piping frames to FFmpeg."""
    n_frames = fft_data['n_frames']
    n_bands = fft_data['n_bands']
    
    command = [
        'ffmpeg', '-y', '-f', 'rawvideo',
        '-vcodec', 'rawvideo', '-s', f'{width}x{height}',
        '-pix_fmt', 'rgb24',
        '-r', str(fps), '-i', '-',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-crf', '23', '-preset', 'medium', output_path
    ]
    
    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        for frame_idx in range(n_frames):
            # Create black background
            img = Image.new('RGB', (width, height), (0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Get data for this frame
            left_fft = fft_data['left_fft'][frame_idx]
            right_fft = fft_data['right_fft'][frame_idx]
            
            # Draw the visualization
            draw_frame(draw, width, height, left_fft, right_fft, n_bands)
            
            # Write frame to FFmpeg
            proc.stdin.write(img.tobytes())
            
            if frame_idx % 30 == 0:
                print(f"Progress: {((frame_idx + 1) / n_frames * 100):.0f}%", flush=True)
    except BrokenPipeError:
        # FFmpeg crashed, get the error message
        stderr_output = proc.stderr.read().decode('utf-8')
        print(f"\nFFmpeg error:\n{stderr_output}")
        proc.wait()
        raise
    
    proc.stdin.close()
    stderr_output = proc.stderr.read().decode('utf-8')
    proc.wait()
    
    if proc.returncode != 0:
        print(f"\nFFmpeg failed with return code {proc.returncode}")
        print(f"Error output:\n{stderr_output}")
        raise RuntimeError("FFmpeg failed to create video")

def merge_audio_video(video_path, audio_path, output_path):
    """Merge the generated video with the original audio using FFmpeg."""
    temp_output_path = output_path.replace('.mp4', '_final.mp4')
    cmd = ['ffmpeg', '-y', '-i', video_path, '-i', audio_path, 
           '-c:v', 'copy', '-c:a', 'aac', '-shortest', temp_output_path]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        os.rename(temp_output_path, output_path)
        if os.path.exists(video_path):
            os.remove(video_path)
        return True
    except subprocess.CalledProcessError as e:
        print("Error during FFmpeg audio/video merge:")
        print("FFmpeg stderr:", e.stderr)
        if os.path.exists(temp_output_path):
            os.remove(temp_output_path)
        return False

def main():
    parser = argparse.ArgumentParser(description='Processing-style visualizer with frequency waveform.')
    parser.add_argument('input_file', help='Input audio file (e.g., mp3, wav)')
    parser.add_argument('--output', '-o', default='viz_with_wave.mp4', help='Output video file path')
    parser.add_argument('--fps', type=int, default=30, help='Frame rate for the output video')
    parser.add_argument('--width', type=int, default=600, help='Video width')
    parser.add_argument('--height', type=int, default=600, help='Video height')
    
    args = parser.parse_args()
    
    # Use a temporary path for the video-only file
    temp_video_path = args.output.replace('.mp4', '_temp_video.mp4')
    parent_directory = os.path.dirname(temp_video_path)
    if parent_directory:
        os.makedirs(parent_directory, exist_ok=True)
    
    print("Step 1: Analyzing audio with FFT...")
    fft_data = analyze_audio_fft(args.input_file, args.fps)
    
    print(f"Step 2: Generating {fft_data['n_frames']} video frames ({args.width}x{args.height} @ {args.fps}fps)...")
    create_visualization(fft_data, temp_video_path, width=args.width, height=args.height, fps=args.fps)
    
    print("Step 3: Merging audio and video...")
    success = merge_audio_video(temp_video_path, args.input_file, args.output)
    
    if success:
        print(f"\nSuccessfully created visualization: {args.output}")
    else:
        print("\nFailed to create the final video.")

if __name__ == "__main__":
    main()